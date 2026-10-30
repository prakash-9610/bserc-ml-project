import streamlit as st
import plotly.express as px
from utils.data_loader import load_data

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Home")

df = load_data()
if df is None:
    st.stop()

st.subheader("Dashboard Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Incidents", f"{len(df):,}")
c2.metric("Fatalities", f"{int(df['nkill'].fillna(0).sum()):,}")
c3.metric("Injured", f"{int(df['nwound'].fillna(0).sum()):,}")
c4.metric("Countries", df["country_txt"].nunique())

st.divider()

st.subheader("Attacks Over Years")

yearly = (
    df.groupby("iyear")
      .size()
      .reset_index(name="Attacks")
)

fig = px.line(
    yearly,
    x="iyear",
    y="Attacks",
    markers=True,
    labels={"iyear": "Year", "Attacks": "Number of Incidents"},
    title="Global Terrorist Incidents Trend (1970 - Present)"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.success("👉 Click **Global Threat Map** from the left sidebar to explore incidents geographically.")
