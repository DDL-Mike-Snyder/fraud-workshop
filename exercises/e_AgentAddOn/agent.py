"""
Optional agent add-on: investigates a transaction the fraud model flagged, using
two mock tools and Claude. Traced with Domino's GenAI tracing SDK.

Requires ANTHROPIC_API_KEY in the environment - never hardcode it here.
"""

import json
import os
from pathlib import Path

import mlflow
from domino.agents.tracing import add_tracing, init_tracing
from domino.agents.logging import DominoRun

# When running as a published Agent (Domino sets DOMINO_AGENT_IS_PROD and DOMINO_APP_ID),
# this activates the agent's own experiment so traces surface under Apps & Agents.
# Outside an agent it just enables Anthropic autologging. Do not call
# mlflow.set_experiment() after this in the agent path - that overrides the routing.
init_tracing(autolog_frameworks=["anthropic"])

MODEL = os.environ.get("FRAUD_AGENT_MODEL", "claude-sonnet-5")
CONFIG_PATH = str(Path(__file__).parent / "config.yaml")

SYSTEM_PROMPT = (
    "You are a fraud investigations assistant helping a card issuer's review team. "
    "You will be given one transaction that a machine-learning model already flagged "
    "as suspicious. Use your tools to pull additional context on the merchant and the "
    "originating IP before you conclude anything - never guess at facts your tools can "
    "look up. Then respond with a short plain-language summary (2-4 sentences) and end "
    "with exactly one recommendation on its own line: 'Recommendation: ESCALATE', "
    "'Recommendation: MONITOR', or 'Recommendation: CLEAR'."
)

TOOLS = [
    {
        "name": "check_merchant_risk_history",
        "description": (
            "Look up recent dispute/chargeback history for a merchant category, given "
            "the risk score the transaction was tagged with."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "merchant_category": {"type": "string"},
                "merchant_risk_score": {"type": "number"},
            },
            "required": ["merchant_category", "merchant_risk_score"],
        },
    },
    {
        "name": "check_ip_reputation",
        "description": (
            "Look up reputation flags for the originating IP address and check whether "
            "the transaction's distance from the cardholder's home address is unusual."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ip_reputation_score": {"type": "number"},
                "distance_from_home_km": {"type": "number"},
            },
            "required": ["ip_reputation_score", "distance_from_home_km"],
        },
    },
]

# Same feature shape as exercises/d_HostingAndExecution/app.py's create_transaction_data.
SAMPLE_TRANSACTIONS = [
    {
        "label": "Late-night electronics purchase, far from home",
        "Amount": 842.50,
        "Age": 34,
        "MerchantCat": "electronics",
        "MerchantRisk": 1.8,
        "DeviceTrust": -1.2,
        "IPReputation": -1.6,
        "DistFromHome": 1240.0,
        "Txn24h": 6,
        "Avg30d": 95.0,
        "Hour": 3,
        "TxType": "purchase",
        "DeviceType": "web",
        "Channel": "online",
    },
    {
        "label": "Routine grocery purchase, familiar pattern",
        "Amount": 42.10,
        "Age": 51,
        "MerchantCat": "grocery",
        "MerchantRisk": 0.1,
        "DeviceTrust": 0.9,
        "IPReputation": 0.4,
        "DistFromHome": 3.0,
        "Txn24h": 1,
        "Avg30d": 55.0,
        "Hour": 17,
        "TxType": "purchase",
        "DeviceType": "POS",
        "Channel": "chip",
    },
]


def check_merchant_risk_history(merchant_category: str, merchant_risk_score: float) -> dict:
    """Mock lookup - deterministic, no external system."""
    if merchant_risk_score >= 1.5:
        tier, note = "high", (
            f"'{merchant_category}' merchants at this risk tier have an elevated "
            "chargeback rate over the last 90 days in our mock risk ledger."
        )
    elif merchant_risk_score >= 0.5:
        tier, note = "moderate", (
            f"'{merchant_category}' merchants at this risk tier show a moderately "
            "above-average dispute rate."
        )
    else:
        tier, note = "low", f"'{merchant_category}' merchants at this risk tier have a clean dispute history."
    return {"merchant_category": merchant_category, "risk_tier": tier, "note": note}


def check_ip_reputation(ip_reputation_score: float, distance_from_home_km: float) -> dict:
    """Mock lookup - deterministic, no external system."""
    flags = []
    if ip_reputation_score < -1.0:
        flags.append("IP has appeared on a known-bad-actor watchlist in our mock reputation feed")
    if distance_from_home_km > 500:
        flags.append(f"transaction originated {distance_from_home_km:.0f} km from the cardholder's home address")
    if not flags:
        flags.append("no reputation or geolocation flags")
    return {"flags": flags}


def _run_tool(name: str, tool_input: dict) -> dict:
    if name == "check_merchant_risk_history":
        return check_merchant_risk_history(**tool_input)
    if name == "check_ip_reputation":
        return check_ip_reputation(**tool_input)
    raise ValueError(f"Unknown tool: {name}")


def investigation_evaluator(span):
    """Takes the mlflow Span for the wrapped call, returns metrics to attach to it."""
    output = span.outputs
    summary = output.get("summary", "") if isinstance(output, dict) else ""
    tools_used = output.get("tools_used", 0) if isinstance(output, dict) else 0
    return {
        "response_length": len(summary),
        "tools_used": tools_used,
        "used_both_tools": 1.0 if tools_used >= 2 else 0.0,
    }


@add_tracing(name="fraud_investigation_agent", evaluator=investigation_evaluator)
def investigate_transaction(transaction: dict) -> dict:
    # Imported here, not at module scope, so app.py can still start and show a clear
    # message if the environment doesn't carry the anthropic package.
    import anthropic

    client = anthropic.Anthropic()

    txn_for_prompt = {k: v for k, v in transaction.items() if k != "label"}
    user_prompt = (
        "A fraud model just flagged this transaction for review:\n"
        f"{json.dumps(txn_for_prompt, indent=2)}\n\n"
        "Investigate it using your tools, then give your summary and recommendation."
    )
    messages = [{"role": "user", "content": user_prompt}]

    tools_used = 0
    response = None
    for _ in range(4):  # hard cap so a misbehaving loop can't run away
        response = client.messages.create(
            model=MODEL,
            max_tokens=800,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tools_used += 1
                result = _run_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    summary_text = "".join(block.text for block in response.content if block.type == "text")
    return {"summary": summary_text, "tools_used": tools_used, "model": MODEL}


if __name__ == "__main__":
    aggregated_metrics = [
        ("response_length", "mean"),
        ("tools_used", "mean"),
        ("used_both_tools", "mean"),
    ]

    # Terminal/dev mode only: group the sample investigations into one evaluation run
    # under a named experiment. The published agent path does not do this - it relies on
    # init_tracing() above to route traces to the agent's own experiment.
    mlflow.set_experiment("fraud-investigation-agent")
    with DominoRun(
        agent_config_path=CONFIG_PATH,
        custom_summary_metrics=aggregated_metrics,
    ) as run:
        for txn in SAMPLE_TRANSACTIONS:
            print(f"\n=== Investigating: {txn['label']} ===")
            result = investigate_transaction(txn)
            print(result["summary"])
            print(f"(tools used: {result['tools_used']}, model: {result['model']})")

        print(f"\nDomino run ID: {run.info.run_id}")
        print("Dev run - view under Experiments -> 'fraud-investigation-agent'.")
