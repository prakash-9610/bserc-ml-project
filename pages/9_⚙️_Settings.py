import streamlit as st
import pandas as pd

# ----------------------------------------
# Page Configuration
# ----------------------------------------

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Dashboard Settings")

st.markdown(
    """
Configure your AI-Based Military Intelligence Dashboard.
"""
)

# ----------------------------------------
# Appearance
# ----------------------------------------

st.header("🎨 Appearance")

theme = st.selectbox(
    "Dashboard Theme",
    [
        "Light",
        "Dark"
    ]
)

layout = st.selectbox(
    "Dashboard Layout",
    [
        "Wide",
        "Centered"
    ]
)

chart_style = st.selectbox(
    "Chart Style",
    [
        "Plotly",
        "Bar",
        "Line",
        "Pie"
    ]
)

# ----------------------------------------
# Default Dashboard Settings
# ----------------------------------------

st.header("🌍 Default Dashboard")

country = st.text_input(
    "Default Country",
    "India"
)

forecast_years = st.slider(
    "Default Forecast Years",
    1,
    10,
    5
)

confidence = st.slider(
    "Minimum Prediction Confidence (%)",
    50,
    100,
    80
)

# ----------------------------------------
# Map Settings
# ----------------------------------------

st.header("🗺️ Global Threat Map")

map_style = st.selectbox(
    "Map Style",
    [
        "OpenStreetMap",
        "Carto Positron",
        "Carto Dark"
    ]
)

show_cluster = st.checkbox(
    "Enable Marker Clustering",
    value=True
)

show_heatmap = st.checkbox(
    "Enable Heatmap",
    value=False
)

# ----------------------------------------
# Forecasting Settings
# ----------------------------------------

st.header("📈 Forecasting")

forecast_model = st.selectbox(
    "Forecasting Algorithm",
    [
        "Linear Regression",
        "ARIMA",
        "Prophet"
    ]
)

# ----------------------------------------
# Machine Learning Settings
# ----------------------------------------

st.header("🤖 Machine Learning")

ml_model = st.selectbox(
    "Prediction Model",
    [
        "Random Forest",
        "Decision Tree",
        "Gradient Boosting"
    ]
)

probability = st.checkbox(
    "Show Prediction Probability",
    value=True
)

feature_importance = st.checkbox(
    "Show Feature Importance",
    value=True
)

# ----------------------------------------
# Report Settings
# ----------------------------------------

st.header("📄 AI Intelligence Report")

report_type = st.selectbox(
    "Default Report Format",
    [
        "PDF",
        "Word",
        "Text"
    ]
)

include_charts = st.checkbox(
    "Include Charts in Report",
    value=True
)

include_tables = st.checkbox(
    "Include Data Tables",
    value=True
)

# ----------------------------------------
# Notifications
# ----------------------------------------

st.header("🔔 Notifications")

attack_alert = st.checkbox(
    "Enable Attack Alerts",
    value=True
)

forecast_alert = st.checkbox(
    "Enable Forecast Alerts",
    value=True
)

report_alert = st.checkbox(
    "Enable Report Notifications",
    value=False
)

# ----------------------------------------
# Dataset Information
# ----------------------------------------

st.header("📊 Dataset Information")

try:

    df = pd.read_csv(
        "data/globalterrorism.csv",
        encoding="latin1",
        low_memory=False
    )

    st.success("Dataset Loaded Successfully")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Rows",
        df.shape[0]
    )

    col2.metric(
        "Columns",
        df.shape[1]
    )

    col3.metric(
        "Countries",
        df["country_txt"].nunique()
    )

except:

    st.error("Dataset not found.")

# ----------------------------------------
# Save Settings
# ----------------------------------------

st.divider()

if st.button("💾 Save Settings"):

    st.success("Settings saved successfully!")

    st.balloons()

# ----------------------------------------
# Reset Settings
# ----------------------------------------

if st.button("🔄 Reset Settings"):

    st.warning("Settings reset to default values.")