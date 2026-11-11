import os
import streamlit as st
import time
import pandas as pd
import requests
import sys
sys.path.append(os.environ["DOMINO_WORKING_DIR"])
from exercises.b_DataEngineering.data_engineering import add_derived_features

# --- Environment variables for model endpoints ---
xgboost_endpoint = os.environ.get('xgboost_endpoint',None)
xgboost_auth = os.environ.get('xgboost_auth',None)

adaboost_endpoint = os.environ.get('adaboost_endpoint',None)
adaboost_auth = os.environ.get('adaboost_auth',None)

gaussiannb_endpoint = os.environ.get('gaussiannb_endpoint',None)
gaussiannb_auth = os.environ.get('gaussiannb_auth',None)

model_dict = {
    'XG Boost': {
        'endpoint': xgboost_endpoint,
        'auth': xgboost_auth,
    },
    'ADA Boost': {
        'endpoint': adaboost_endpoint,
        'auth': adaboost_auth,
    },
    'GaussianNB': {
        'endpoint': gaussiannb_endpoint,
        'auth': gaussiannb_auth,
    }
}


def create_transaction_data(amount, hour, tx_type, card_present, age, tenure,
                            txn_24h, avg_30d, merchant_risk, device_trust,
                            ip_reputation, dist_from_home, latitude, longitude,
                            device_type, merchant_cat, channel):
    """Create a single-row DataFrame with transaction data and derived features."""
    current_time = time.time()
    raw_data = {
        'Time': current_time,
        'Amount': amount,
        'Age': age,
        'Tenure': tenure,
        'MerchantRisk': merchant_risk,
        'DeviceTrust': device_trust,
        'Txn24h': txn_24h,
        'Avg30d': avg_30d,
        'IPReputation': ip_reputation,
        'Latitude': latitude,
        'Longitude': longitude,
        'DistFromHome': dist_from_home,
        'Hour': hour,
        'TxType': tx_type,
        'DeviceType': device_type,
        'MerchantCat': merchant_cat,
        'Channel': channel,
        'CardPresent': card_present
    }
    df = pd.DataFrame([raw_data])
    df_with_features = add_derived_features(df)
    return df_with_features


def render():
    """Render the traditional ML (XGBoost endpoint) tab."""
    st.title("🔒 Fraud Detection System")
    st.write("Simulate a transaction and analyze fraud risk using machine learning models.")

    # Input fields
    col1, col2, col3 = st.columns(3)

    with col1:
        amount = st.number_input("Transaction Amount", min_value=1, max_value=10000, value=100)
        age = st.slider("Customer Age", 18, 100, 30)
        tenure = st.slider("Customer Tenure (years)", 0, 40, 5)
        txn_24h = st.slider("Transactions in last 24h", 0, 50, 2)
        avg_30d = st.number_input("Average Transaction (30d)", min_value=1, max_value=5000, value=200)

    with col2:
        merchant_risk = st.slider("Merchant Risk Score", -3.0, 3.0, 0.0)
        device_trust = st.slider("Device Trust Score", -3.0, 3.0, 0.0)
        ip_reputation = st.slider("IP Reputation Score", -3.0, 3.0, 0.0)
        dist_from_home = st.slider("Distance from Home (km)", 0.0, 5000.0, 10.0)
        latitude = st.number_input("Latitude", -90.0, 90.0, 37.7749)
        longitude = st.number_input("Longitude", -180.0, 180.0, -122.4194)

    with col3:
        hour = st.slider("Transaction Hour", 0, 23, 14)
        tx_type = st.selectbox("Transaction Type", ["purchase", "withdrawal", "transfer", "payment"])
        device_type = st.selectbox("Device Type", ["mobile", "web", "desktop", "POS", "ATM"])
        merchant_cat = st.selectbox("Merchant Category",
                                    ["grocery", "electronics", "clothing", "entertainment", "travel", "restaurant", "gas", "utilities"])
        channel = st.selectbox("Channel", ["online", "in-store", "contactless", "chip"])
        card_present = st.selectbox("Card Present", [0, 1])
        selected_model = st.selectbox("Model", ["XG Boost", "ADA Boost", "GaussianNB"],index=0)

    st.markdown("---")

    # Prediction button and results
    predict_button = st.button("🔍 Predict Fraud Risk", type="primary")

    if predict_button:
        with st.spinner("Analyzing transaction... 🔍"):
            time.sleep(2)  # Simulate latency

            # Build transaction dataframe + features
            transaction_df = create_transaction_data(
                amount=amount,
                hour=hour,
                tx_type=tx_type,
                card_present=card_present,
                age=age,
                tenure=tenure,
                txn_24h=txn_24h,
                avg_30d=avg_30d,
                merchant_risk=merchant_risk,
                device_trust=device_trust,
                ip_reputation=ip_reputation,
                dist_from_home=dist_from_home,
                latitude=latitude,
                longitude=longitude,
                device_type=device_type,
                merchant_cat=merchant_cat,
                channel=channel
            )

            # JSON payload for classifier
            transaction_json = {
                "data": {
                    # --- Numeric features ---
                    "num__Time": float(transaction_df['Time'].iloc[0]),
                    "num__Amount": float(transaction_df['Amount'].iloc[0]),
                    "num__Age": float(transaction_df['Age'].iloc[0]),
                    "num__Tenure": float(transaction_df['Tenure'].iloc[0]),
                    "num__MerchantRisk": float(transaction_df['MerchantRisk'].iloc[0]),
                    "num__DeviceTrust": float(transaction_df['DeviceTrust'].iloc[0]),
                    "num__Txn24h": float(transaction_df['Txn24h'].iloc[0]),
                    "num__Avg30d": float(transaction_df['Avg30d'].iloc[0]),
                    "num__IPReputation": float(transaction_df['IPReputation'].iloc[0]),
                    "num__Latitude": float(transaction_df['Latitude'].iloc[0]),
                    "num__Longitude": float(transaction_df['Longitude'].iloc[0]),
                    "num__DistFromHome": float(transaction_df['DistFromHome'].iloc[0]),
                    "num__Hour": float(transaction_df['Hour'].iloc[0]),
                    "num__CardPresent": float(transaction_df['CardPresent'].iloc[0]),
                    "num__amount_vs_avg30d_ratio": float(transaction_df['amount_vs_avg30d_ratio'].iloc[0]),
                    "num__risk_score": float(transaction_df['risk_score'].iloc[0]),
                    "num__trust_score": float(transaction_df['trust_score'].iloc[0]),
        
                    # --- One-hot categorical features ---
                    # Transaction type
                    "cat__TxType_payment": 1.0 if tx_type == "payment" else 0.0,
                    "cat__TxType_purchase": 1.0 if tx_type == "purchase" else 0.0,
                    "cat__TxType_transfer": 1.0 if tx_type == "transfer" else 0.0,
                    "cat__TxType_withdrawal": 1.0 if tx_type == "withdrawal" else 0.0,
        
                    # Device type
                    "cat__DeviceType_ATM": 1.0 if device_type == "ATM" else 0.0,
                    "cat__DeviceType_POS": 1.0 if device_type == "POS" else 0.0,
                    "cat__DeviceType_desktop": 1.0 if device_type == "desktop" else 0.0,
                    "cat__DeviceType_mobile": 1.0 if device_type == "mobile" else 0.0,
                    "cat__DeviceType_web": 1.0 if device_type == "web" else 0.0,
        
                    # Merchant category
                    "cat__MerchantCat_clothing": 1.0 if merchant_cat == "clothing" else 0.0,
                    "cat__MerchantCat_electronics": 1.0 if merchant_cat == "electronics" else 0.0,
                    "cat__MerchantCat_entertainment": 1.0 if merchant_cat == "entertainment" else 0.0,
                    "cat__MerchantCat_gas": 1.0 if merchant_cat == "gas" else 0.0,
                    "cat__MerchantCat_grocery": 1.0 if merchant_cat == "grocery" else 0.0,
                    "cat__MerchantCat_restaurant": 1.0 if merchant_cat == "restaurant" else 0.0,
                    "cat__MerchantCat_travel": 1.0 if merchant_cat == "travel" else 0.0,
                    "cat__MerchantCat_utilities": 1.0 if merchant_cat == "utilities" else 0.0,
        
                    # Channel
                    "cat__Channel_chip": 1.0 if channel == "chip" else 0.0,
                    "cat__Channel_contactless": 1.0 if channel == "contactless" else 0.0,
                    "cat__Channel_in-store": 1.0 if channel == "in-store" else 0.0,
                    "cat__Channel_online": 1.0 if channel == "online" else 0.0,
        
                    # Generation (from add_derived_features)
                    "cat__generation_Baby Boomer": 1.0 if transaction_df['generation'].iloc[0] == "Baby Boomer" else 0.0,
                    "cat__generation_Generation X": 1.0 if transaction_df['generation'].iloc[0] == "Generation X" else 0.0,
                    "cat__generation_Generation Z": 1.0 if transaction_df['generation'].iloc[0] == "Generation Z" else 0.0,
                    "cat__generation_Millennial": 1.0 if transaction_df['generation'].iloc[0] == "Millennial" else 0.0
                }
            }


            fraud_prediction = None
            try:
                selected_endpoint = model_dict[selected_model]['endpoint']
                selected_auth = model_dict[selected_model]['auth']

                classifier_response = requests.post(
                    selected_endpoint,
                    auth=(selected_auth, selected_auth),
                    json=transaction_json
                )

                if classifier_response.status_code == 200:
                    classifier_resp = classifier_response.json()
                    fraud_prediction = classifier_resp['result']

                    # ✅ FIX: Always coerce fraud_prediction into a float
                    if isinstance(fraud_prediction, list) and len(fraud_prediction) > 0:
                        fraud_prediction = float(fraud_prediction[0])
                    elif isinstance(fraud_prediction, (int, float)):
                        fraud_prediction = float(fraud_prediction)
                    else:
                        fraud_prediction = None

                    print("fraud_prediction =", fraud_prediction)
                else:
                    st.error(f"Classifier API Error: {classifier_response.status_code}")
                    print(f"Classifier error: {classifier_response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Classifier Connection Error: {str(e)}")

            # Fallback heuristic if classifier fails
            final_risk_score = (
                fraud_prediction
                if fraud_prediction is not None
                else sum([
                    amount > 500,
                    merchant_risk > 1.0,
                    device_trust < -1.0,
                    ip_reputation < -1.0,
                    dist_from_home > 2.0,
                    hour in [0, 1, 2, 3, 4, 5, 23]
                ]) / 6
            )

            # ✅ No more list-vs-float error
            is_fraud = float(final_risk_score) > 0.4

            # --- Display results ---
            st.subheader("Prediction Results")
            col_a, col_b = st.columns(2)

            with col_a:
                st.metric("Fraud Probability", f"{final_risk_score:.2f}")
            with col_b:
                st.metric("Prediction", "🚨 FRAUD" if is_fraud else "✅ Legitimate")
