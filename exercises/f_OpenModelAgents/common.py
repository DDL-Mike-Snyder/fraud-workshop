"""Shared settings and helpers for the two open-model agents."""
import os

# --- Models (Hugging Face ids) -------------------------------------------------
GENERATOR_MODEL = os.environ.get("GENERATOR_MODEL", "ibm-granite/granite-3.3-8b-instruct")
FRAUD_BASE_MODEL = os.environ.get("FRAUD_BASE_MODEL", "ibm-granite/granite-3.3-2b-instruct")

# --- Where the vLLM servers listen (both started by serve_llms.sh) ------------
GENERATOR_URL = os.environ.get("GENERATOR_URL", "http://localhost:8000/v1")
FRAUD_URL = os.environ.get("FRAUD_URL", "http://localhost:8001/v1")
FRAUD_SERVED_NAME = "fraud-llm"
GENERATOR_SERVED_NAME = "txn-generator"

# --- Transaction schema (the raw columns of raw_cc_transactions.csv.gz) -------
NUMERIC = ["Amount", "Age", "Tenure", "MerchantRisk", "DeviceTrust", "Txn24h", "Avg30d",
           "IPReputation", "Latitude", "Longitude", "DistFromHome", "Hour", "CardPresent"]
CATEGORICAL = ["TxType", "DeviceType", "MerchantCat", "Channel"]
COLUMNS = NUMERIC + CATEGORICAL
TX_TYPES = ["purchase", "withdrawal", "transfer", "payment"]
DEVICE_TYPES = ["mobile", "web", "desktop", "POS", "ATM"]
MERCHANT_CATS = ["grocery", "electronics", "clothing", "entertainment", "travel",
                 "restaurant", "gas", "utilities"]
CHANNELS = ["online", "in-store", "contactless", "chip"]

PROMPT_HEAD = "Classify this card transaction as fraud (1) or legitimate (0).\n"


def transaction_prompt(row) -> str:
    """Turn one transaction (dict or Series) into the text the fraud model sees.
    Training and serving must use this exact function."""
    def f(k):
        v = row[k]
        if k in CATEGORICAL:
            return str(v) if v == v and v is not None else "unknown"
        return f"{float(v):.2f}" if k not in ("Hour", "CardPresent", "Tenure", "Txn24h", "Age") \
            else f"{float(v):.0f}"
    fields = "\n".join(f"{k}: {f(k)}" for k in COLUMNS)
    return f"{PROMPT_HEAD}{fields}\nlabel="
