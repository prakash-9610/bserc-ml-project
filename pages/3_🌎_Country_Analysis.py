import streamlit as st
import plotly.express as px
from utils.data_loader import load_data

st.set_page_config(
    page_title="Country Analysis",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 Country Analysis")

df = load_data()
if df is None:
    st.stop()

# -----------------------------
# Sidebar
# -----------------------------
countries = sorted(df["country_txt"].dropna().unique())

country = st.sidebar.selectbox(
    "Select Country",
    countries
)

country_df = df[df["country_txt"] == country]

if len(country_df) == 0:
    st.warning(f"No incident records found for {country}.")
    st.stop()

st.header(f"Intelligence Report: {country}")

# -----------------------------
# KPIs
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Incidents",
    f"{len(country_df):,}"
)

c2.metric(
    "Fatalities",
    f"{int(country_df['nkill'].fillna(0).sum()):,}"
)

c3.metric(
    "Injured",
    f"{int(country_df['nwound'].fillna(0).sum()):,}"
)

c4.metric(
    "Active Groups",
    country_df["gname"].nunique()
)

st.divider()

# -----------------------------
# Attacks Over Time & Attack Types
# -----------------------------
left, right = st.columns(2)

with left:
    yearly = (
        country_df
        .groupby("iyear")
        .size()
        .reset_index(name="Attacks")
    )

    fig = px.line(
        yearly,
        x="iyear",
        y="Attacks",
        markers=True,
        title=f"Attacks Over Years in {country}",
        labels={"iyear": "Year", "Attacks": "Number of Attacks"}
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    attack = (
        country_df
        .groupby("attacktype1_txt")
        .size()
        .reset_index(name="Count")
    )

    fig = px.pie(
        attack,
        names="attacktype1_txt",
        values="Count",
        title="Attack Types Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------
# Organizations & Weapons
# -----------------------------
left, right = st.columns(2)

with left:
    groups = (
        country_df
        .groupby("gname")
        .size()
        .reset_index(name="Attacks")
        .sort_values("Attacks", ascending=False)
        .head(10)
    )

    fig = px.bar(
        groups,
        x="Attacks",
        y="gname",
        orientation="h",
        title="Top 10 Active Terrorist Organizations",
        labels={"gname": "Organization", "Attacks": "Incident Count"}
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with right:
    weapon = (
        country_df
        .groupby("weaptype1_txt")
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
    )

    fig = px.bar(
        weapon,
        x="weaptype1_txt",
        y="Count",
        title="Weapon Types Utilized",
        labels={"weaptype1_txt": "Weapon Type", "Count": "Incident Count"}
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------
# Incident Map
# -----------------------------
st.subheader("Incident Locations")

map_df = country_df.dropna(subset=["latitude", "longitude"])

if len(map_df) == 0:
    st.info(f"No geographic coordinate records available for incidents in {country}.")
else:
    fig = px.scatter_geo(
        map_df,
        lat="latitude",
        lon="longitude",
        hover_name="city",
        hover_data={
            "country_txt": True,
            "iyear": True,
            "attacktype1_txt": True,
            "gname": True,
            "nkill": True,
            "latitude": False,
            "longitude": False
        },
        color="attacktype1_txt",
        projection="natural earth",
        title=f"Incident Map: {country}",
        height=600
    )
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------
# Incident Table
# -----------------------------
st.subheader("Incident Details")

candidate_cols = [
    "iyear",
    "city",
    "attacktype1_txt",
    "targtype1_txt",
    "weaptype1_txt",
    "gname",
    "nkill",
    "nwound"
]
cols = [c for c in candidate_cols if c in country_df.columns]

st.dataframe(
    country_df[cols],
    use_container_width=True
)

# -----------------------------
# Download
# -----------------------------
csv = country_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Country Data (CSV)",
    csv,
    file_name=f"{country}_threat_data.csv",
    mime="text/csv"
)
