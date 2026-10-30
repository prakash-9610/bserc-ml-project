import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data

# --------------------------------------------------------
# Page Configuration
# --------------------------------------------------------
st.set_page_config(
    page_title="Data Explorer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Global Terrorism Data Explorer")

st.markdown("Query, filter, inspect, and export intelligence records from the GTD database.")

df = load_data()
if df is None:
    st.stop()

# --------------------------------------------------------
# Sidebar Filters
# --------------------------------------------------------
st.sidebar.header("Filter Dataset")

# Year
years = sorted(df["iyear"].dropna().unique())
selected_year = st.sidebar.multiselect(
    "Select Year",
    years,
    default=[]
)

# Country
countries = sorted(df["country_txt"].dropna().unique())
selected_country = st.sidebar.multiselect(
    "Select Country",
    countries,
    default=[]
)

# Region
regions = sorted(df["region_txt"].dropna().unique())
selected_region = st.sidebar.multiselect(
    "Select Region",
    regions,
    default=[]
)

# Attack Type
attack_types = sorted(df["attacktype1_txt"].dropna().unique())
selected_attack = st.sidebar.multiselect(
    "Attack Type",
    attack_types,
    default=[]
)

# Weapon Type
weapons = sorted(df["weaptype1_txt"].dropna().unique())
selected_weapon = st.sidebar.multiselect(
    "Weapon Type",
    weapons,
    default=[]
)

# Terrorist Group
groups = sorted(df["gname"].dropna().unique())
selected_group = st.sidebar.multiselect(
    "Terrorist Group",
    groups,
    default=[]
)

# --------------------------------------------------------
# Apply Filters
# --------------------------------------------------------
filtered_df = df

if selected_year:
    filtered_df = filtered_df[filtered_df["iyear"].isin(selected_year)]

if selected_country:
    filtered_df = filtered_df[filtered_df["country_txt"].isin(selected_country)]

if selected_region:
    filtered_df = filtered_df[filtered_df["region_txt"].isin(selected_region)]

if selected_attack:
    filtered_df = filtered_df[filtered_df["attacktype1_txt"].isin(selected_attack)]

if selected_weapon:
    filtered_df = filtered_df[filtered_df["weaptype1_txt"].isin(selected_weapon)]

if selected_group:
    filtered_df = filtered_df[filtered_df["gname"].isin(selected_group)]

# --------------------------------------------------------
# Search Box
# --------------------------------------------------------
search = st.text_input("🔍 Quick Search by City or Country Name")

if search:
    city_match = filtered_df["city"].fillna("").astype(str).str.contains(search, case=False)
    country_match = filtered_df["country_txt"].fillna("").astype(str).str.contains(search, case=False)
    filtered_df = filtered_df[city_match | country_match]

# --------------------------------------------------------
# KPIs
# --------------------------------------------------------
st.subheader("Dataset Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Incidents", f"{len(filtered_df):,}")
c2.metric("Countries", filtered_df["country_txt"].nunique())
c3.metric("Fatalities", f"{int(filtered_df['nkill'].fillna(0).sum()):,}")
c4.metric("Injuries", f"{int(filtered_df['nwound'].fillna(0).sum()):,}")

# --------------------------------------------------------
# Dataset Preview & Export
# --------------------------------------------------------
st.subheader("Filtered Records")

if len(filtered_df) == 0:
    st.info("No records match the active filter criteria.")
else:
    # Selected key columns first for clean readable preview
    key_cols = [
        "eventid", "iyear", "imonth", "iday", "country_txt", "region_txt",
        "city", "attacktype1_txt", "targtype1_txt", "targsubtype1_txt",
        "gname", "weaptype1_txt", "nkill", "nwound", "summary"
    ]
    display_cols = [c for c in key_cols if c in filtered_df.columns]
    remaining_cols = [c for c in filtered_df.columns if c not in display_cols]
    final_cols = display_cols + remaining_cols

    st.dataframe(
        filtered_df[final_cols].head(1000),
        use_container_width=True,
        height=400
    )
    if len(filtered_df) > 1000:
        st.caption(f"Showing first 1,000 of {len(filtered_df):,} matching rows in table preview.")

    # CSV Download (limiting to 20,000 rows if huge to keep browser responsive)
    export_df = filtered_df.head(20000)
    csv = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=f"📥 Download Filtered Data (CSV{f' - first {len(export_df):,} rows' if len(filtered_df) > len(export_df) else ''})",
        data=csv,
        file_name="Filtered_GTD_Data.csv",
        mime="text/csv"
    )

# --------------------------------------------------------
# Visual Analytics
# --------------------------------------------------------
st.divider()
st.subheader("Visual Analytics")

if len(filtered_df) > 0:
    tab1, tab2, tab3 = st.tabs([
        "Top Countries",
        "Attack Types",
        "Weapon Types"
    ])

    with tab1:
        country_chart = (
            filtered_df["country_txt"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        country_chart.columns = ["Country", "Incidents"]

        fig = px.bar(
            country_chart,
            x="Country",
            y="Incidents",
            color="Incidents",
            title="Top 10 Countries by Incident Count"
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        attack_chart = (
            filtered_df["attacktype1_txt"]
            .value_counts()
            .reset_index()
        )
        attack_chart.columns = ["Attack Type", "Count"]

        fig = px.pie(
            attack_chart,
            names="Attack Type",
            values="Count",
            title="Attack Type Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        weapon_chart = (
            filtered_df["weaptype1_txt"]
            .value_counts()
            .reset_index()
        )
        weapon_chart.columns = ["Weapon", "Count"]

        fig = px.bar(
            weapon_chart,
            x="Weapon",
            y="Count",
            color="Count",
            title="Weapon Type Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Visual analytics unavailable: No data matching filters.")

# --------------------------------------------------------
# Dataset Diagnostics
# --------------------------------------------------------
with st.expander("ℹ️ Dataset Information & Memory Footprint"):
    mem_mb = round(filtered_df.memory_usage(deep=True).sum() / (1024 ** 2), 2)
    st.write(f"- **Matching Rows:** {filtered_df.shape[0]:,}")
    st.write(f"- **Total Columns:** {filtered_df.shape[1]}")
    st.write(f"- **In-Memory Size:** ~{mem_mb} MB")

    missing = (
        filtered_df.isnull()
        .sum()
        .loc[lambda x: x > 0]
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )
    missing.columns = ["Column", "Missing Count"]
    if not missing.empty:
        st.write("Top Columns with Missing Values:")
        st.dataframe(missing, use_container_width=True, hide_index=True)
