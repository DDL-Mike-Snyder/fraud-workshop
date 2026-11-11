"""Agent 1: chat with an open LLM to specify a batch of simulated transactions.

The LLM (Granite-3.3-8B-Instruct) turns your request into a call to the `generate_transactions`
tool; the tool draws realistic rows with a seeded simulator. Every turn is traced.
"""
import json, os
import numpy as np, pandas as pd
from openai import OpenAI
from domino.agents.tracing import add_tracing, init_tracing

from exercises.f_OpenModelAgents.common import (GENERATOR_URL, GENERATOR_SERVED_NAME, TX_TYPES,
                                                DEVICE_TYPES, MERCHANT_CATS, CHANNELS)

init_tracing(autolog_frameworks=["openai"])

SCENARIOS = {
    "mixed": "Everyday legitimate activity plus a blend of fraud patterns.",
    "account_takeover": "Untrusted new device, bad IP, far from home, big jump over the 30-day average, often at night.",
    "card_not_present": "Online/web purchases in electronics or travel with high merchant risk and no card present.",
    "atm_skimming": "ATM withdrawals at odd hours, far from home, several in 24h.",
    "velocity_burst": "Many small transactions in 24h on a risky merchant/IP.",
}

SYSTEM_PROMPT = (
    "You help a fraud analyst build a batch of simulated card transactions. When the user asks "
    "for transactions, you MUST call the generate_transactions tool; never write code or show "
    "the call as text. Choose sensible values for anything unstated. Ask a short clarifying "
    "question only if the request has no usable detail. After the tool returns, summarise in "
    "2-3 sentences what was generated (count, fraud share, scenario). Do not list the rows; "
    "the user sees them in a table."
)

TOOLS = [{
    "type": "function",
    "function": {
        "name": "generate_transactions",
        "description": "Simulate a series of realistic card transactions.",
        "parameters": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "description": "Number of transactions (1-500)."},
                "fraud_rate": {"type": "number", "description": "Fraction that are fraudulent, 0-1."},
                "scenario": {"type": "string", "enum": list(SCENARIOS), "description": "; ".join(f"{k}: {v}" for k, v in SCENARIOS.items())},
                "amount_min": {"type": "number"}, "amount_max": {"type": "number"},
                "merchant_categories": {"type": "array", "items": {"type": "string", "enum": MERCHANT_CATS}},
                "channels": {"type": "array", "items": {"type": "string", "enum": CHANNELS}},
                "seed": {"type": "integer"},
            },
            "required": ["n"],
        },
    },
}]


def generate_transactions(n=50, fraud_rate=0.2, scenario="mixed", amount_min=None, amount_max=None,
                          merchant_categories=None, channels=None, seed=None) -> pd.DataFrame:
    """Seeded simulator. `is_fraud_intent` is what the simulator meant, not a model output."""
    rng = np.random.default_rng(seed)
    n = int(np.clip(n, 1, 500)); fraud_rate = float(np.clip(fraud_rate, 0, 1))
    scenario = scenario if scenario in SCENARIOS else "mixed"
    cats = [c for c in (merchant_categories or MERCHANT_CATS) if c in MERCHANT_CATS] or MERCHANT_CATS
    chans = [c for c in (channels or CHANNELS) if c in CHANNELS] or CHANNELS
    fraud = np.zeros(n, bool); fraud[rng.choice(n, int(round(n * fraud_rate)), replace=False)] = True  # exact share

    avg30 = rng.normal(0, 1, n)
    amount = np.exp(rng.normal(3.9, 0.9, n))                       # median ~$50
    age = np.clip(rng.normal(40, 12, n), 18, 76).round()
    d = {"Amount": amount, "Age": age, "Tenure": rng.integers(0, 30, n).astype(float),
         "MerchantRisk": rng.normal(0, 1, n), "DeviceTrust": rng.normal(0, 1, n),
         "Txn24h": rng.poisson(1.5, n).astype(float), "Avg30d": avg30,
         "IPReputation": rng.normal(0, 1, n), "Latitude": rng.uniform(25, 50, n),
         "Longitude": rng.uniform(-125, -67, n), "DistFromHome": rng.normal(0, 1, n),
         "Hour": rng.choice(24, n, p=_hour_p()).astype(float), "CardPresent": (rng.random(n) < 0.8).astype(float),
         "TxType": rng.choice(TX_TYPES, n, p=[.6, .1, .1, .2]), "DeviceType": rng.choice(DEVICE_TYPES, n),
         "MerchantCat": rng.choice(cats, n), "Channel": rng.choice(chans, n)}
    df = pd.DataFrame(d)
    # Avg30d in the source data is a standardized score; keep the model-facing column the same way.
    k = int(fraud.sum())
    if k:
        f = df.index[fraud]
        sc = scenario if scenario != "mixed" else rng.choice([s for s in SCENARIOS if s != "mixed"], k)
        sc = np.array([sc] * k) if isinstance(sc, str) else sc
        def shift(mask, col, delta, sd=0.4):
            idx = f[mask]; df.loc[idx, col] = df.loc[idx, col] + delta + rng.normal(0, sd, len(idx))
        df.loc[f, "Amount"] *= rng.uniform(2, 6, k)
        m = sc == "account_takeover"
        shift(m, "DeviceTrust", -2.0); shift(m, "IPReputation", -2.0); shift(m, "DistFromHome", 2.5)
        df.loc[f[m], "Hour"] = rng.choice([0, 1, 2, 3, 4, 23], m.sum()); df.loc[f[m], "Channel"] = "online"
        m = sc == "card_not_present"
        shift(m, "MerchantRisk", 2.0); df.loc[f[m], "CardPresent"] = 0.0
        df.loc[f[m], "Channel"] = "online"; df.loc[f[m], "DeviceType"] = rng.choice(["web", "mobile"], m.sum())
        df.loc[f[m], "MerchantCat"] = rng.choice([c for c in ["electronics", "travel"] if c in cats] or cats, m.sum())
        m = sc == "atm_skimming"
        df.loc[f[m], "DeviceType"] = "ATM"; df.loc[f[m], "TxType"] = "withdrawal"; df.loc[f[m], "Channel"] = "chip"
        shift(m, "DistFromHome", 2.0); df.loc[f[m], "Txn24h"] += rng.integers(3, 8, m.sum())
        df.loc[f[m], "Hour"] = rng.choice([1, 2, 3, 4, 22, 23], m.sum())
        m = sc == "velocity_burst"
        df.loc[f[m], "Txn24h"] = rng.integers(8, 30, m.sum()); df.loc[f[m], "Amount"] = amount[f[m]] * rng.uniform(.3, 1.2, m.sum())
        shift(m, "MerchantRisk", 1.5); shift(m, "IPReputation", -1.5)
    if amount_min is not None: df["Amount"] = df["Amount"].clip(lower=float(amount_min))
    if amount_max is not None: df["Amount"] = df["Amount"].clip(upper=float(amount_max))
    df["Amount"] = df["Amount"].round(2); df["Avg30d"] = (df["Avg30d"] * 1).round(3)
    for c in ["MerchantRisk", "DeviceTrust", "IPReputation", "DistFromHome"]: df[c] = df[c].round(3)
    df[["Latitude", "Longitude"]] = df[["Latitude", "Longitude"]].round(4)
    df.insert(0, "txn_id", [f"T{i + 1:04d}" for i in range(n)])
    df["is_fraud_intent"] = fraud.astype(int)
    return df


def _hour_p():
    w = np.array([1, 1, 1, 1, 1, 2, 3, 5, 6, 6, 6, 6, 7, 6, 6, 6, 6, 7, 7, 6, 5, 4, 3, 2], float)
    return w / w.sum()


def _looks_like_code(text) -> bool:
    t = text or ""
    return "```" in t or "generate_transactions" in t or "fraud_rate" in t


@add_tracing(name="transaction_generator_agent")
def chat(messages: list) -> dict:
    """messages: [{role, content}, ...] incl. prior turns. Returns {reply, transactions|None, spec|None}."""
    client = OpenAI(base_url=GENERATOR_URL, api_key=os.environ.get("VLLM_API_KEY", "EMPTY"))
    convo = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    frame, spec = None, None
    for _ in range(3):
        r = client.chat.completions.create(model=GENERATOR_SERVED_NAME, messages=convo, tools=TOOLS,
                                           temperature=0.2, max_tokens=600)
        msg = r.choices[0].message
        if not msg.tool_calls and frame is None and _looks_like_code(msg.content):
            # Smaller open models sometimes write the call as code instead of calling the tool.
            # Retry once with the tool call forced; the arguments still come from the model.
            r = client.chat.completions.create(
                model=GENERATOR_SERVED_NAME, messages=convo, tools=TOOLS, temperature=0.2, max_tokens=600,
                tool_choice={"type": "function", "function": {"name": "generate_transactions"}})
            msg = r.choices[0].message
        if not msg.tool_calls:
            return {"reply": msg.content or "", "transactions": frame, "spec": spec}
        convo.append({"role": "assistant", "content": msg.content or "",
                      "tool_calls": [t.model_dump() for t in msg.tool_calls]})
        for t in msg.tool_calls:
            try:
                spec = json.loads(t.function.arguments)
                frame = generate_transactions(**spec)
                res = {"generated": len(frame), "fraud_share": round(float(frame.is_fraud_intent.mean()), 3),
                       "scenario": spec.get("scenario", "mixed")}
            except Exception as e:                       # let the model see and repair bad arguments
                res = {"error": str(e)}
            convo.append({"role": "tool", "tool_call_id": t.id, "content": json.dumps(res)})
    return {"reply": "I could not complete that request. Try rephrasing it.", "transactions": frame, "spec": spec}
