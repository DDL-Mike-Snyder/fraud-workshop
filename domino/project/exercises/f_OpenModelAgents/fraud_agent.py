"""Agent 2: score transactions with the fine-tuned fraud LLM.

fraud_score = P(label=1) from the model's next-token log-probabilities, so it is a real
probability-like score (not generated text). Each scored batch is traced.
"""
import json, math, os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from openai import OpenAI
from domino.agents.tracing import add_tracing, init_tracing

from exercises.f_OpenModelAgents.common import FRAUD_URL, FRAUD_SERVED_NAME, transaction_prompt

init_tracing(autolog_frameworks=["openai"])


def _client():
    return OpenAI(base_url=FRAUD_URL, api_key=os.environ.get("VLLM_API_KEY", "EMPTY"))


def score_one(client, row) -> float:
    r = client.completions.create(model=FRAUD_SERVED_NAME, prompt=transaction_prompt(row),
                                  max_tokens=1, temperature=0, logprobs=10)
    top = r.choices[0].logprobs.top_logprobs[0]
    p1 = sum(math.exp(v) for k, v in top.items() if k.strip() == "1")
    p0 = sum(math.exp(v) for k, v in top.items() if k.strip() == "0")
    return p1 / (p1 + p0) if (p1 + p0) > 0 else float("nan")


def evaluator(span):
    o = span.outputs
    return {"n_scored": o.get("n", 0), "flag_rate": o.get("flag_rate", 0.0)} if isinstance(o, dict) else {}


@add_tracing(name="fraud_scoring_agent", evaluator=evaluator)
def score_transactions(df: pd.DataFrame, threshold: float = 0.5) -> dict:
    client = _client()
    with ThreadPoolExecutor(8) as ex:
        scores = list(ex.map(lambda i: score_one(client, df.iloc[i]), range(len(df))))
    out = df.copy(); out["fraud_score"] = [round(s, 4) for s in scores]
    out["flagged"] = (out["fraud_score"] >= threshold).astype(int)
    return {"scored": out, "n": len(out), "flag_rate": float(out["flagged"].mean())}
