"""The Agent tab: chat -> generated transactions -> fraud scoring."""
import pandas as pd
import streamlit as st

from exercises.f_OpenModelAgents import generator_agent, fraud_agent
from exercises.f_OpenModelAgents.common import COLUMNS


def render():
    ss = st.session_state
    ss.setdefault("agent_msgs", []); ss.setdefault("agent_txns", None); ss.setdefault("agent_scored", None)

    st.title("🤖 Fraud Agents")
    st.write("Tell the **generator agent** what transactions you want, then have the **fraud agent** score them. "
             "Both are open models running on this app's GPU; every call is traced in Domino.")
    left, right = st.columns([2, 3], gap="large")

    with left:
        st.subheader("1. Generator agent")
        st.caption("Example: *Make 80 transactions, 25% fraud, mostly late-night online electronics purchases far from the cardholder's home.*")
        box = st.container(height=420)
        for m in ss.agent_msgs:
            box.chat_message(m["role"]).write(m["content"])
        if prompt := st.chat_input("Describe the transactions you want"):
            ss.agent_msgs.append({"role": "user", "content": prompt})
            with st.spinner("Generator agent is working..."):
                try:
                    res = generator_agent.chat(ss.agent_msgs)
                except Exception as e:
                    res = {"reply": f"Could not reach the generator model ({e}). Is the GPU app running?", "transactions": None}
            ss.agent_msgs.append({"role": "assistant", "content": res["reply"]})
            if res.get("transactions") is not None:
                ss.agent_txns, ss.agent_scored = res["transactions"], None
            st.rerun()
        if st.button("Clear conversation"):
            ss.agent_msgs, ss.agent_txns, ss.agent_scored = [], None, None
            st.rerun()

    with right:
        st.subheader("2. Fraud-scoring agent")
        if ss.agent_txns is None:
            st.info("Generate some transactions first."); return
        df = ss.agent_txns
        thr = st.slider("Flag as fraud at or above", 0.05, 0.95, 0.5, 0.05)
        if st.button("🔍 Score with fraud agent", type="primary"):
            with st.spinner(f"Scoring {len(df)} transactions..."):
                try:
                    ss.agent_scored = fraud_agent.score_transactions(df[["txn_id"] + COLUMNS + ["is_fraud_intent"]], thr)["scored"]
                except Exception as e:
                    st.error(f"Could not reach the fraud model ({e}). Has the fine-tuning Job finished?")
        shown = ss.agent_scored
        if shown is None:
            st.dataframe(df, use_container_width=True, height=380); return
        shown = shown.assign(flagged=(shown.fraud_score >= thr).astype(int))
        c1, c2, c3 = st.columns(3)
        c1.metric("Scored", len(shown)); c2.metric("Flagged", int(shown.flagged.sum()))
        tp = int(((shown.flagged == 1) & (shown.is_fraud_intent == 1)).sum()); n1 = int(shown.is_fraud_intent.sum())
        c3.metric("Caught of intended fraud", f"{tp}/{n1}")
        st.caption("`is_fraud_intent` is what the generator meant to create, not ground truth about the real world.")
        cfg = {"fraud_score": st.column_config.ProgressColumn("fraud_score", min_value=0, max_value=1, format="%.2f")}
        ranked = shown.sort_values("fraud_score", ascending=False)
        flagged = ranked[ranked.flagged == 1]
        st.subheader(f"🚨 Transactions marked fraudulent ({len(flagged)})")
        if flagged.empty:
            st.success(f"No transactions scored at or above {thr:.2f}. Try lowering the threshold.")
        else:
            st.dataframe(flagged, use_container_width=True, height=min(380, 40 + 35 * len(flagged)), column_config=cfg)
        with st.expander(f"All scored transactions ({len(ranked)})"):
            st.dataframe(ranked, use_container_width=True, height=380, column_config=cfg)
