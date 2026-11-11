import os
import sys

import streamlit as st

sys.path.append(os.environ["DOMINO_WORKING_DIR"])

# Importing agent also calls init_tracing(), which routes traces to this agent's own
# experiment when running as a published Agent. Don't call mlflow.set_experiment() here.
from exercises.e_AgentAddOn.agent import (
    SAMPLE_TRANSACTIONS,
    investigate_transaction,
)

st.set_page_config(page_title="Fraud Investigation Agent", page_icon="🕵️", layout="centered")

st.title("🕵️ Fraud Investigation Agent")
st.write(
    "Optional add-on: an agent investigates a transaction the fraud model already "
    "flagged, calling two mock lookup tools before giving a recommendation. Every "
    "click here produces a real, inspectable trace in Domino."
)

try:
    import anthropic  # noqa: F401
except ImportError:
    st.error(
        "The `anthropic` package isn't installed in this compute environment. "
        "Add `RUN pip install --no-cache-dir anthropic` to the environment "
        "definition and rebuild it — the rest of the workshop doesn't need it."
    )
    st.stop()

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.error(
        "ANTHROPIC_API_KEY is not set. Add it as a project or app environment "
        "variable in Domino before using this page — never hardcode it in code."
    )
    st.stop()

labels = [txn["label"] for txn in SAMPLE_TRANSACTIONS]
choice = st.selectbox("Pick a flagged transaction to investigate", labels)
transaction = next(txn for txn in SAMPLE_TRANSACTIONS if txn["label"] == choice)

with st.expander("Transaction details"):
    st.json({k: v for k, v in transaction.items() if k != "label"})

if st.button("🔍 Investigate", type="primary"):
    with st.spinner("Agent is investigating — calling tools and reasoning over the result..."):
        result = investigate_transaction(transaction)

    st.subheader("Investigation summary")
    st.write(result["summary"])

    recommendation = "UNKNOWN"
    for level in ("ESCALATE", "MONITOR", "CLEAR"):
        if level in result["summary"].upper():
            recommendation = level
            break
    badge = {"ESCALATE": "🚨", "MONITOR": "🟡", "CLEAR": "✅"}.get(recommendation, "❔")
    st.metric("Recommendation", f"{badge} {recommendation}")

    st.caption(f"Model: {result['model']} · Tools used: {result['tools_used']}")
    st.info("View the full trace in Domino: **Apps & Agents → this agent → Traces tab.**")
