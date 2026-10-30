from pathlib import Path
import streamlit as st
import joblib
import pandas as pd
from utils.data_loader import MODELS_DIR

st.set_page_config(
    page_title="Attack Prediction",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Attack Type Prediction")

st.markdown("""
Predict the likely terrorist attack classification based on operational and environmental tactical indicators.
Enter incident details below and click **Predict Attack Type**.
""")

# -------------------------
# Load Machine Learning Model & Encoders
# -------------------------
@st.cache_resource(show_spinner="Loading attack prediction model...")
def load_attack_models():
    model_path = MODELS_DIR / "attack_prediction_model.pkl"
    encoders_path = MODELS_DIR / "feature_encoders.pkl"
    target_path = MODELS_DIR / "target_encoder.pkl"

    if not model_path.exists() or not encoders_path.exists() or not target_path.exists():
        return None, None, None

    try:
        model = joblib.load(model_path)
        encoders = joblib.load(encoders_path)
        target_encoder = joblib.load(target_path)
        return model, encoders, target_encoder
    except Exception as e:
        st.error(f"Error loading model files: {e}")
        return None, None, None

model, encoders, target_encoder = load_attack_models()

if model is None or encoders is None or target_encoder is None:
    st.warning("⚠️ **Trained Attack Prediction Model Not Found!**")
    st.info(
        """
        The model file `models/attack_prediction_model.pkl` or its encoders are not yet built or available.

        **To train and generate the model:**
        Open your terminal in the project directory and run:
        ```bash
        python train_attack_model.py
        ```
        This will train an optimized Random Forest classifier and save the necessary encoders.
        """
    )
    st.stop()

# -------------------------
# Create Input Form
# -------------------------
with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        country = st.selectbox(
            "🌍 Country",
            sorted(encoders["country_txt"].classes_)
        )

        region = st.selectbox(
            "🌎 Region",
            sorted(encoders["region_txt"].classes_)
        )

        weapon = st.selectbox(
            "🔫 Weapon Type",
            sorted(encoders["weaptype1_txt"].classes_)
        )

        target = st.selectbox(
            "🎯 Target Type",
            sorted(encoders["targtype1_txt"].classes_)
        )

    with col2:
        group = st.selectbox(
            "👥 Terrorist Group",
            sorted(encoders["gname"].classes_)
        )

        success = st.selectbox(
            "✅ Attack Successful?",
            [1, 0],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        suicide = st.selectbox(
            "💣 Suicide Attack?",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        nkill = st.number_input(
            "☠ Number of Fatalities",
            min_value=0,
            max_value=10000,
            value=0,
            step=1
        )

        nwound = st.number_input(
            "🏥 Number of Injured",
            min_value=0,
            max_value=10000,
            value=0,
            step=1
        )

    submitted = st.form_submit_button("🚀 Predict Attack Type")

if submitted:
    try:
        c_enc = encoders["country_txt"].transform([country])[0]
        r_enc = encoders["region_txt"].transform([region])[0]
        w_enc = encoders["weaptype1_txt"].transform([weapon])[0]
        t_enc = encoders["targtype1_txt"].transform([target])[0]
        g_enc = encoders["gname"].transform([group])[0]

        input_df = pd.DataFrame({
            "country_txt": [c_enc],
            "region_txt": [r_enc],
            "weaptype1_txt": [w_enc],
            "targtype1_txt": [t_enc],
            "gname": [g_enc],
            "success": [success],
            "suicide": [suicide],
            "nkill": [nkill],
            "nwound": [nwound]
        })

        prediction = model.predict(input_df)
        attack_type = target_encoder.inverse_transform(prediction)[0]

        probabilities = model.predict_proba(input_df)
        confidence = probabilities.max() * 100

        st.divider()
        st.subheader("🎯 Prediction Result")
        st.success(f"**Predicted Attack Type:** {attack_type}")

        m1, m2 = st.columns(2)
        m1.metric("Prediction Confidence", f"{confidence:.2f}%")
        m2.metric("Target Assessment", f"{target}")

        # Show distribution across classes
        with st.expander("📊 Probability Breakdown by Attack Type"):
            prob_df = pd.DataFrame({
                "Attack Type": target_encoder.classes_,
                "Probability (%)": [round(p * 100, 2) for p in probabilities[0]]
            }).sort_values("Probability (%)", ascending=False)
            st.dataframe(prob_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Prediction failed: {e}")
else:
    st.info("👈 Enter the scenario parameters above and click **Predict Attack Type** to evaluate.")
