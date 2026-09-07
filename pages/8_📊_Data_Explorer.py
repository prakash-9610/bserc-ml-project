import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------------
# Page Configuration
# --------------------------------------------------------

st.set_page_config(
    page_title="Data Explorer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Global Terrorism Data Explorer")

st.markdown("Explore, filter, visualize and download the GTD dataset.")

# --------------------------------------------------------
# Load Dataset
# --------------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/globalterrorism.csv",
        encoding="latin1",
        low_memory=False
    )
    return df

df = load_data()

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

filtered_df = df.copy()

if selected_year:
    filtered_df = filtered_df[
        filtered_df["iyear"].isin(selected_year)
    ]

if selected_country:
    filtered_df = filtered_df[
        filtered_df["country_txt"].isin(selected_country)
    ]

if selected_region:
    filtered_df = filtered_df[
        filtered_df["region_txt"].isin(selected_region)
    ]

if selected_attack:
    filtered_df = filtered_df[
        filtered_df["attacktype1_txt"].isin(selected_attack)
    ]

if selected_weapon:
    filtered_df = filtered_df[
        filtered_df["weaptype1_txt"].isin(selected_weapon)
    ]

if selected_group:
    filtered_df = filtered_df[
        filtered_df["gname"].isin(selected_group)
    ]

# --------------------------------------------------------
# Search Box
# --------------------------------------------------------

search = st.text_input(
    "🔍 Search by City or Country"
)

if search:

    filtered_df = filtered_df[
        filtered_df["city"].fillna("").str.contains(
            search,
            case=False
        )
        |
        filtered_df["country_txt"].fillna("").str.contains(
            search,
            case=False
        )
    ]

# --------------------------------------------------------
# KPIs
# --------------------------------------------------------

st.subheader("Dataset Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Incidents",
    len(filtered_df)
)

c2.metric(
    "Countries",
    filtered_df["country_txt"].nunique()
)

c3.metric(
    "Fatalities",
    int(filtered_df["nkill"].fillna(0).sum())
)

c4.metric(
    "Injuries",
    int(filtered_df["nwound"].fillna(0).sum())
)

# --------------------------------------------------------
# Dataset Preview
# --------------------------------------------------------

st.subheader("Filtered Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500
)

# --------------------------------------------------------
# Download CSV
# --------------------------------------------------------

csv = filtered_df.to_csv(index=False)

st.download_button(
    "📥 Download Filtered Data",
    csv,
    file_name="Filtered_GTD_Data.csv",
    mime="text/csv"
)

# --------------------------------------------------------
# Charts
# --------------------------------------------------------

st.subheader("Visual Analytics")

tab1, tab2, tab3 = st.tabs([
    "Country",
    "Attack Type",
    "Weapon Type"
])

# ---------------- Country ----------------

with tab1:

    country_chart = (
        filtered_df["country_txt"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    country_chart.columns = [
        "Country",
        "Incidents"
    ]

    fig = px.bar(
        country_chart,
        x="Country",
        y="Incidents",
        color="Incidents",
        title="Top 10 Countries"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------- Attack ----------------

with tab2:

    attack_chart = (
        filtered_df["attacktype1_txt"]
        .value_counts()
        .reset_index()
    )

    attack_chart.columns = [
        "Attack Type",
        "Count"
    ]

    fig = px.pie(
        attack_chart,
        names="Attack Type",
        values="Count",
        title="Attack Type Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------- Weapon ----------------

with tab3:

    weapon_chart = (
        filtered_df["weaptype1_txt"]
        .value_counts()
        .reset_index()
    )

    weapon_chart.columns = [
        "Weapon",
        "Count"
    ]

    fig = px.bar(
        weapon_chart,
        x="Weapon",
        y="Count",
        color="Count",
        title="Weapon Type Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------------
# Missing Values
# --------------------------------------------------------

st.subheader("Missing Values")

missing = (
    filtered_df.isnull()
    .sum()
    .sort_values(ascending=False)
)

missing = missing.reset_index()

missing.columns = [
    "Column",
    "Missing Values"
]

st.dataframe(
    missing,
    use_container_width=True
)

# --------------------------------------------------------
# Dataset Information
# --------------------------------------------------------

st.subheader("Dataset Information")

st.write("Rows :", filtered_df.shape[0])

st.write("Columns :", filtered_df.shape[1])

st.write("Memory Usage (MB):",
         round(filtered_df.memory_usage(deep=True).sum()/1024**2,2))

st.write("Column Names")

st.write(filtered_df.columns.tolist())