import streamlit as st
import plotly.express as px
from utils.data_loader import load_data

st.set_page_config(
    page_title="Global Threat Map",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Global Threat Map")

df = load_data()
if df is None:
    st.stop()

st.sidebar.header("Filters")

year = st.sidebar.selectbox(
    "Year",
    ["All"] + sorted(df["iyear"].unique().tolist())
)

filtered_df = df
if year != "All":
    filtered_df = filtered_df[filtered_df["iyear"] == year]

filtered_df = filtered_df.dropna(subset=["latitude", "longitude"])

# Sampling when "All" is selected prevents browser/WebGL tab crash with 180k points
if year == "All" and len(filtered_df) > 5000:
    st.caption("ℹ️ Displaying a representative sample of 5,000 incidents for smooth rendering. Select a specific year in the sidebar to inspect all incidents for that year.")
    map_df = filtered_df.sample(5000, random_state=42)
else:
    map_df = filtered_df

if len(map_df) == 0:
    st.warning("No geographic coordinates found for the selected filter.")
else:
    fig = px.scatter_geo(
        map_df,
        lat="latitude",
        lon="longitude",
        color="attacktype1_txt",
        hover_name="country_txt",
        hover_data=["city", "gname", "nkill"],
        projection="natural earth",
        title=f"Geographical Distribution of Incidents ({'All Years' if year == 'All' else year})"
    )

    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=650)
    st.plotly_chart(fig, use_container_width=True)

st.info("👈 Change filters from the sidebar.")
