"""End-to-end check of both agents against the running vLLM servers (also creates traces).
    python exercises/f_OpenModelAgents/smoke_test.py"""
import os, sys
sys.path.append(os.environ.get("DOMINO_WORKING_DIR", os.getcwd()))
from sklearn.metrics import roc_auc_score
from exercises.f_OpenModelAgents import generator_agent, fraud_agent
from exercises.f_OpenModelAgents.common import COLUMNS

r = generator_agent.chat([{"role": "user", "content":
    "Make 40 transactions, 30% fraud, late-night online electronics purchases far from the cardholder's home."}])
print("E2E reply:", r["reply"])
df = r["transactions"]
assert df is not None, "generator did not produce transactions"
print("E2E generated:", len(df), "rows,", int(df.is_fraud_intent.sum()), "intended fraud; spec:", r["spec"])
out = fraud_agent.score_transactions(df[["txn_id"] + COLUMNS + ["is_fraud_intent"]], 0.5)["scored"]
print("E2E scored:", len(out), "flagged:", int(out.flagged.sum()),
      "roc_auc_vs_intent:", round(roc_auc_score(out.is_fraud_intent, out.fraud_score), 3))
print("E2E sample:\n", out.sort_values("fraud_score", ascending=False).head(5)[["txn_id", "Amount", "Hour", "fraud_score", "is_fraud_intent"]].to_string())
