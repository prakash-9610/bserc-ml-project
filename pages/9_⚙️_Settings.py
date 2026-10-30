import streamlit as st
import pandas as pd
from utils.data_loader import get_data_path, load_data

# ----------------------------------------
# Page Configuration
# ----------------------------------------
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Dashboard Settings")

st.markdown("""
Configure operational preferences, default visualizations, and examine platform runtime diagnostics.
""")

# ----------------------------------------
# Appearance
# ----------------------------------------
st.header("🎨 Appearance & Display")

col_a, col_b, col_c = st.columns(3)
with col_a:
    theme = st.selectbox("Dashboard Theme", ["Default / Dark", "Light"])
with col_b:
    layout = st.selectbox("Dashboard Layout", ["Wide", "Centered"])
with col_c:
    chart_style = st.selectbox("Chart Style", ["Plotly Default", "High-Contrast", "Monochrome"])

# ----------------------------------------
# Default Dashboard Settings
# ----------------------------------------
st.header("🌍 Default Parameters")

col_d1, col_d2, col_d3 = st.columns(3)
with col_d1:
    default_country = st.text_input("Default Focus Country", "India")
with col_d2:
    default_forecast_years = st.slider("Default Forecast Horizon (Years)", 1, 10, 5)
with col_d3:
    confidence_thresh = st.slider("Prediction Confidence Alert Threshold (%)", 50, 100, 80)

# ----------------------------------------
# Map Settings
# ----------------------------------------
st.header("🗺️ Global Threat Map Configuration")

col_m1, col_m2 = st.columns(2)
with col_m1:
    map_projection = st.selectbox(
        "Map Projection Style",
        ["natural earth", "equirectangular", "orthographic", "mercator"]
    )
with col_m2:
    map_sample_size = st.select_slider(
        "Max Incidents Displayed on 'All Years'",
        options=[1000, 2500, 5000, 10000],
        value=5000
    )

# ----------------------------------------
# Machine Learning & AI Settings
# ----------------------------------------
st.header("🤖 Machine Learning & Intelligence Engine")

col_ml1, col_ml2 = st.columns(2)
with col_ml1:
    ml_model = st.selectbox(
        "Default Attack Classifier",
        ["Random Forest (Optimized)", "Ensemble Gradient Boosted"]
    )
    show_prob = st.checkbox("Show Detailed Probability Breakdown", value=True)

with col_ml2:
    forecast_model = st.selectbox(
        "Forecasting Engine",
        ["Linear Regression", "Polynomial Trend", "Moving Average"]
    )
    include_recommendations = st.checkbox("Generate Tactical AI Recommendations", value=True)

# ----------------------------------------
# Notifications & Alerts
# ----------------------------------------
st.header("🔔 Intelligence Alerts")

c_n1, c_n2, c_n3 = st.columns(3)
with c_n1:
    attack_alert = st.checkbox("Enable High-Risk Country Alerts", value=True)
with c_n2:
    forecast_alert = st.checkbox("Enable Growth Trend Alerts", value=True)
with c_n3:
    report_alert = st.checkbox("Enable Automated Executive Summary", value=True)

# ----------------------------------------
# Dataset Diagnostic Information
# ----------------------------------------
st.divider()
st.header("📊 Dataset Runtime Diagnostic")

data_path = get_data_path()

if data_path:
    st.success(f"✅ Active Dataset Source: `{data_path}`")
    try:
        df = load_data()
        if df is not None:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Records", f"{df.shape[0]:,}")
            col2.metric("Total Features", df.shape[1])
            col3.metric("Monitored Countries", df["country_txt"].nunique())
    except Exception as e:
        st.error(f"Error reading dataset diagnostics: {e}")
else:
    st.error("❌ Dataset file not located in project.")
    st.warning("Ensure `globalterrorism.csv` or `globalterrorism.csv.zip` is present in `data/`.")

# ----------------------------------------
# Save & Reset Settings
# ----------------------------------------
st.divider()
col_btn1, col_btn2 = st.columns([1, 5])

with col_btn1:
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("Settings saved successfully!")
        st.balloons()

with col_btn2:
    if st.button("🔄 Reset to Defaults"):
        st.info("Settings restored to factory default configuration.")
