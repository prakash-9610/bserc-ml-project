from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd
import joblib
from utils.data_loader import MODELS_DIR

st.set_page_config(
    page_title="Threat Level Prediction",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 AI Threat Level Prediction System")

st.markdown("""
Predict the operational severity level (**LOW**, **MEDIUM**, or **HIGH**) of a security threat scenario
using a pre-trained Random Forest classification model.
""")

# -------------------------------
# Load Model & Encoders
# -------------------------------
@st.cache_resource(show_spinner="Loading threat level model...")
def load_threat_models():
    model_path = MODELS_DIR / "threat_level_model.pkl"
    encoders_path = MODELS_DIR / "threat_encoders.pkl"
    target_path = MODELS_DIR / "threat_target_encoder.pkl"

    if not model_path.exists() or not encoders_path.exists() or not target_path.exists():
        return None, None, None

    try:
        model = joblib.load(model_path)
        encoders = joblib.load(encoders_path)
        target_encoder = joblib.load(target_path)
        return model, encoders, target_encoder
    except Exception as e:
        st.error(f"Error loading threat model files: {e}")
        return None, None, None

model, encoders, target_encoder = load_threat_models()

if model is None or encoders is None or target_encoder is None:
    st.warning("⚠️ **Threat Level Prediction Model Not Found!**")
    st.info(
        """
        The threat classification model `models/threat_level_model.pkl` is not yet available.

        **To train and generate the model:**
        Run the training script in your terminal:
        ```bash
        python train_threat_model.py
        ```
        This trains the model in ~10 seconds and saves the model artifact (`~1.4 MB`).
        """
    )
    st.stop()

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.header("Input Parameters")

country = st.sidebar.selectbox("Country", sorted(encoders["country_txt"].classes_))
region = st.sidebar.selectbox("Region", sorted(encoders["region_txt"].classes_))
attack = st.sidebar.selectbox("Attack Type", sorted(encoders["attacktype1_txt"].classes_))
weapon = st.sidebar.selectbox("Weapon Type", sorted(encoders["weaptype1_txt"].classes_))
target = st.sidebar.selectbox("Target Type", sorted(encoders["targtype1_txt"].classes_))

nkill = st.sidebar.number_input("Number Killed", min_value=0, max_value=10000, value=0, step=1)
nwound = st.sidebar.number_input("Number Wounded", min_value=0, max_value=10000, value=0, step=1)

# -------------------------------
# Prediction Button & Output
# -------------------------------
predict_clicked = st.sidebar.button("🚨 Predict Threat Level", use_container_width=True)

if predict_clicked:
    try:
        country_enc = encoders["country_txt"].transform([country])[0]
        region_enc = encoders["region_txt"].transform([region])[0]
        attack_enc = encoders["attacktype1_txt"].transform([attack])[0]
        weapon_enc = encoders["weaptype1_txt"].transform([weapon])[0]
        target_enc = encoders["targtype1_txt"].transform([target])[0]

        input_df = pd.DataFrame({
            "country_txt": [country_enc],
            "region_txt": [region_enc],
            "attacktype1_txt": [attack_enc],
            "weaptype1_txt": [weapon_enc],
            "targtype1_txt": [target_enc],
            "nkill": [nkill],
            "nwound": [nwound]
        })

        prediction = model.predict(input_df)
        probability = model.predict_proba(input_df)

        result = target_encoder.inverse_transform(prediction)[0]
        confidence = np.max(probability) * 100

        st.subheader("🔍 Prediction Result")

        col1, col2 = st.columns([1, 1])

        with col1:
            if result == "LOW":
                st.success(f"### 🟢 Operational Threat Level: **{result}**")
                st.info("Scenario classified as standard risk profile with limited casualty impact.")
            elif result == "MEDIUM":
                st.warning(f"### 🟡 Operational Threat Level: **{result}**")
                st.info("Scenario classified as elevated risk profile requiring tactical deployment.")
            else:
                st.error(f"### 🔴 Operational Threat Level: **{result}**")
                st.info("Critical severity threat profile with substantial casualty risk. Immediate response required.")

            st.metric("Model Confidence Score", f"{confidence:.2f}%")

        with col2:
            st.write("### Probability Distribution")
            prob_df = pd.DataFrame({
                "Threat Level": target_encoder.classes_,
                "Probability": probability[0]
            })
            st.bar_chart(prob_df, x="Threat Level", y="Probability")

    except Exception as e:
        st.error(f"Error computing threat prediction: {e}")
else:
    st.info("👈 Configure tactical parameters in the sidebar and click **🚨 Predict Threat Level**.")
