import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------

st.set_page_config(
    page_title="AI Intelligence Report",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI Intelligence Report")

st.markdown("""
Generate an AI-assisted intelligence summary from the
Global Terrorism Database (GTD).
""")

# -------------------------------------------------
# Load Dataset
# -------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
        "data/globalterrorism.csv",
        encoding="latin1",
        low_memory=False
    )

    return df


df = load_data()

# -------------------------------------------------
# Sidebar Filters
# -------------------------------------------------

st.sidebar.header("Report Filters")

years = sorted(df["iyear"].unique())

selected_year = st.sidebar.selectbox(
    "Select Year",
    ["All"] + list(years)
)

if selected_year != "All":
    df = df[df["iyear"] == selected_year]

# -------------------------------------------------
# Key Statistics
# -------------------------------------------------

total_incidents = len(df)

total_killed = int(df["nkill"].fillna(0).sum())

total_wounded = int(df["nwound"].fillna(0).sum())

countries = df["country_txt"].nunique()

groups = df["gname"].nunique()

# -------------------------------------------------
# Top Countries
# -------------------------------------------------

top_countries = (
    df["country_txt"]
    .value_counts()
    .head(10)
)

# -------------------------------------------------
# Top Terrorist Groups
# -------------------------------------------------

top_groups = (
    df["gname"]
    .value_counts()
    .head(10)
)

# -------------------------------------------------
# Attack Types
# -------------------------------------------------

attack_types = (
    df["attacktype1_txt"]
    .value_counts()
)

# -------------------------------------------------
# Weapon Types
# -------------------------------------------------

weapon_types = (
    df["weaptype1_txt"]
    .value_counts()
)

# -------------------------------------------------
# Threat Level
# -------------------------------------------------

avg_killed = df["nkill"].fillna(0).mean()

if avg_killed < 2:
    threat = "LOW 🟢"

elif avg_killed < 5:
    threat = "MEDIUM 🟡"

else:
    threat = "HIGH 🔴"

# -------------------------------------------------
# Dashboard Metrics
# -------------------------------------------------

st.subheader("Key Intelligence Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Incidents",
    f"{total_incidents:,}"
)

col2.metric(
    "Fatalities",
    f"{total_killed:,}"
)

col3.metric(
    "Injuries",
    f"{total_wounded:,}"
)

col4.metric(
    "Threat Level",
    threat
)

# -------------------------------------------------
# Executive Summary
# -------------------------------------------------

st.subheader("Executive Summary")

summary = f"""

During the selected period, {total_incidents:,} terrorist incidents
were recorded across {countries} countries.

The attacks resulted in {total_killed:,} fatalities and
{total_wounded:,} injuries.

The overall threat level is assessed as {threat}.

The most affected country is
{top_countries.index[0]}.

The most active terrorist organization is
{top_groups.index[0]}.

The most common attack type is
{attack_types.index[0]}.

The most frequently used weapon is
{weapon_types.index[0]}.

"""

st.info(summary)

# -------------------------------------------------
# Top Countries
# -------------------------------------------------

st.subheader("Top 10 High-Risk Countries")

fig = px.bar(
    top_countries,
    x=top_countries.values,
    y=top_countries.index,
    orientation="h",
    labels={
        "x":"Incidents",
        "y":"Country"
    }
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# Terrorist Groups
# -------------------------------------------------

st.subheader("Most Active Terrorist Groups")

fig2 = px.bar(
    top_groups,
    x=top_groups.values,
    y=top_groups.index,
    orientation="h",
    labels={
        "x":"Attacks",
        "y":"Group"
    }
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# AI Intelligence Assessment
# -------------------------------------------------

st.subheader("AI Intelligence Assessment")

recommendation = f"""

1. Increase surveillance in {top_countries.index[0]}.

2. Closely monitor activities associated with
{top_groups.index[0]}.

3. Strengthen protection of infrastructure that
is frequently targeted.

4. Enhance intelligence sharing among agencies.

5. Increase monitoring of explosive-based attacks.

6. Continue trend analysis using predictive
machine learning models.

"""

st.success(recommendation)

# -------------------------------------------------
# Download Report
# -------------------------------------------------

report = f"""

==============================

AI INTELLIGENCE REPORT

==============================

Total Incidents : {total_incidents}

Fatalities : {total_killed}

Injuries : {total_wounded}

Threat Level : {threat}

Top Country : {top_countries.index[0]}

Top Group : {top_groups.index[0]}

Most Common Attack :
{attack_types.index[0]}

Most Common Weapon :
{weapon_types.index[0]}

Recommendations

{recommendation}

"""

st.download_button(
    "📄 Download Intelligence Report",
    report,
    file_name="AI_Intelligence_Report.txt"
)