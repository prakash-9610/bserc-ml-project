import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from utils.data_loader import load_data

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="Forecasting",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Terrorism Attack Forecasting")

st.markdown("""
Forecast future terrorist attack occurrences using historical trend extrapolation from the Global Terrorism Database.
""")

df = load_data()
if df is None:
    st.stop()

# ----------------------------------------------------
# Sidebar Filters
# ----------------------------------------------------
st.sidebar.header("Forecast Settings")

countries = sorted(df["country_txt"].dropna().unique())

country = st.sidebar.selectbox(
    "Select Country",
    countries
)

forecast_years = st.sidebar.slider(
    "Forecast Horizon (Years)",
    min_value=1,
    max_value=10,
    value=5
)

# ----------------------------------------------------
# Prepare Data
# ----------------------------------------------------
country_df = df[df["country_txt"] == country]

yearly = (
    country_df
    .groupby("iyear")
    .size()
    .reset_index(name="Attacks")
)

yearly = yearly.sort_values("iyear")

# ----------------------------------------------------
# Check data availability
# ----------------------------------------------------
if len(yearly) < 5:
    st.warning(f"⚠️ Insufficient historical data for **{country}** to construct a reliable forecast (minimum 5 recorded years required).")
    st.stop()

# ----------------------------------------------------
# Train Linear Regression Model
# ----------------------------------------------------
X = yearly[["iyear"]]
y = yearly["Attacks"]

model = LinearRegression()
model.fit(X, y)

# ----------------------------------------------------
# Future Prediction
# ----------------------------------------------------
last_year = int(yearly["iyear"].max())

future_years = np.arange(
    last_year + 1,
    last_year + forecast_years + 1
)

future_df = pd.DataFrame({
    "iyear": future_years
})

predictions = model.predict(future_df)
predictions = np.maximum(predictions, 0)

forecast = pd.DataFrame({
    "Year": future_years,
    "Forecasted Attacks": predictions.astype(int)
})

# ----------------------------------------------------
# Historical + Forecast Plot
# ----------------------------------------------------
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=yearly["iyear"],
        y=yearly["Attacks"],
        mode="lines+markers",
        name="Historical Observed",
        line=dict(color="#1f77b4", width=2)
    )
)

fig.add_trace(
    go.Scatter(
        x=forecast["Year"],
        y=forecast["Forecasted Attacks"],
        mode="lines+markers",
        name="Linear Forecast",
        line=dict(color="#ff7f0e", width=2, dash="dash")
    )
)

fig.update_layout(
    title=f"Incident Trajectory & Forecast for {country}",
    xaxis_title="Year",
    yaxis_title="Number of Incidents",
    height=550,
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# Forecast Table & Analytics
# ----------------------------------------------------
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📋 Forecast Projections")
    st.dataframe(
        forecast,
        use_container_width=True,
        hide_index=True
    )

with right_col:
    st.subheader("📊 Growth Analysis")

    historical_last = yearly.iloc[-1]["Attacks"]
    forecast_last = forecast.iloc[-1]["Forecasted Attacks"]

    growth = (
        (forecast_last - historical_last)
        / max(historical_last, 1)
    ) * 100

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Latest Actual",
        int(historical_last)
    )

    col2.metric(
        f"Forecast (+{forecast_years} yrs)",
        int(forecast_last)
    )

    col3.metric(
        "Projected Trend",
        f"{growth:+.1f}%"
    )

    st.subheader("Risk Trend Assessment")
    if growth < 0:
        st.success("🟢 **Threat Trend: Decreasing** — Incident velocity is declining based on historical trajectory.")
    elif growth < 15:
        st.warning("🟡 **Threat Trend: Stable** — Incident volume projected to remain approximately steady.")
    else:
        st.error("🔴 **Threat Trend: Increasing** — Elevated operational threat projection. Preemptive counter-measures advised.")

# ----------------------------------------------------
# Download Forecast
# ----------------------------------------------------
csv = forecast.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Forecast CSV",
    data=csv,
    file_name=f"{country}_forecast_{forecast_years}yr.csv",
    mime="text/csv"
)
