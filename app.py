from pathlib import Path
import streamlit as st
from utils.data_loader import get_data_path, MODELS_DIR

st.set_page_config(
    page_title="AI Military Intelligence Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ AI-Based Military Intelligence Dashboard")

st.markdown("""
### Welcome
This dashboard provides operational military intelligence and threat analysis using the
**Global Terrorism Database (GTD)** and machine-learning predictive models.

👈 **Select a page from the sidebar to begin.**
""")

# System Health & Deployment Readiness
data_path = get_data_path()
attack_model_exists = (MODELS_DIR / "attack_prediction_model.pkl").exists()
threat_model_exists = (MODELS_DIR / "threat_level_model.pkl").exists()

c1, c2, c3 = st.columns(3)
with c1:
    if data_path:
        st.success(f"✅ **Dataset:** Online (`{data_path.name}`)")
    else:
        st.error("❌ **Dataset:** Missing (`data/globalterrorism.csv`)")

with c2:
    if attack_model_exists:
        st.success("✅ **Attack Model:** Online")
    else:
        st.warning("⚠️ **Attack Model:** Needs Training (`train_attack_model.py`)")

with c3:
    if threat_model_exists:
        st.success("✅ **Threat Level Model:** Online")
    else:
        st.warning("⚠️ **Threat Model:** Needs Training (`train_threat_model.py`)")

st.info("""
### Available Modules
- 🏠 **Home:** Overall dashboard metrics and annual attack trends.
- 🌍 **Global Threat Map:** Interactive geospatial visualization of global incidents.
- 🌎 **Country Analysis:** Country-level intelligence reports, weapons, and top groups.
- 🤖 **Attack Prediction:** ML-driven prediction of attack method with confidence scoring.
- 🚨 **Threat Level Prediction:** Operational risk classification (LOW / MEDIUM / HIGH).
- 📈 **Forecasting:** Linear regression attack frequency trend projection.
- 🧠 **AI Intelligence Report:** Automated tactical summary and defense recommendations.
- 📊 **Data Explorer:** Multi-filter query engine, raw data inspector, and CSV export.
- ⚙️ **Settings:** Platform configuration, default preferences, and system diagnostic info.
""")
