"""Fraud Detection System: two tabs in one Streamlit app.

  Trad ML Model  the original XGBoost-endpoint scorer (trad_ml_tab.py)
  Agent          chat with a transaction-generator agent, then score the result
                 with a fraud-tuned open model (exercises/f_OpenModelAgents)

app.sh still just runs this file.
"""
import os
import sys

import streamlit as st

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "/mnt/code"))

st.set_page_config(page_title="Fraud Detection System", page_icon="🔒", layout="wide")

tab_ml, tab_agent = st.tabs(["Trad ML Model", "Agent"])

with tab_ml:
    from exercises.d_HostingAndExecution import trad_ml_tab
    trad_ml_tab.render()

with tab_agent:
    try:
        from exercises.f_OpenModelAgents import agent_tab
    except Exception as e:  # missing packages must not break the Trad ML tab
        st.error(f"The Agent tab could not load: {e}")
        st.info("It needs the Fraud-Detection-LLM environment. See step 9 of the workshop guide.")
    else:
        agent_tab.render()
