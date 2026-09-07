import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression

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
Forecast the future number of terrorist attacks using historical GTD data.
""")

# ----------------------------------------------------
# Load Dataset
# ----------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/globalterrorism.csv",
        encoding="latin1",
        low_memory=False
    )
    return df

df = load_data()

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
    "Forecast Years",
    1,
    10,
    5
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
    st.warning("Not enough historical data for forecasting.")
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
last_year = yearly["iyear"].max()

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
        name="Historical"
    )
)

fig.add_trace(
    go.Scatter(
        x=forecast["Year"],
        y=forecast["Forecasted Attacks"],
        mode="lines+markers",
        name="Forecast"
    )
)

fig.update_layout(
    title=f"Attack Forecast for {country}",
    xaxis_title="Year",
    yaxis_title="Number of Attacks",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# Forecast Table
# ----------------------------------------------------
st.subheader("Forecast Results")

st.dataframe(
    forecast,
    use_container_width=True
)

# ----------------------------------------------------
# Growth Analysis
# ----------------------------------------------------
historical_last = yearly.iloc[-1]["Attacks"]
forecast_last = forecast.iloc[-1]["Forecasted Attacks"]

growth = (
    (forecast_last - historical_last)
    / max(historical_last, 1)
) * 100

st.subheader("Growth Analysis")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Current Attacks",
    int(historical_last)
)

col2.metric(
    f"Forecast ({forecast_years} Years)",
    int(forecast_last)
)

col3.metric(
    "Growth %",
    f"{growth:.2f}%"
)

# ----------------------------------------------------
# Risk Assessment
# ----------------------------------------------------
st.subheader("Risk Assessment")

if growth < 0:
    st.success("🟢 Threat Trend: Decreasing")
elif growth < 15:
    st.warning("🟡 Threat Trend: Stable")
else:
    st.error("🔴 Threat Trend: Increasing")

# ----------------------------------------------------
# Download Forecast
# ----------------------------------------------------
csv = forecast.to_csv(index=False)

st.download_button(
    label="📥 Download Forecast CSV",
    data=csv,
    file_name=f"{country}_forecast.csv",
    mime="text/csv"
)