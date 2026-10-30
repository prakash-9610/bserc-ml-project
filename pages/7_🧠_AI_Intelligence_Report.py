import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data

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
Synthesize operational intelligence summaries, risk indicators, and tactical recommendations from the Global Terrorism Database.
""")

df = load_data()
if df is None:
    st.stop()

# -------------------------------------------------
# Sidebar Filters
# -------------------------------------------------
st.sidebar.header("Report Filters")

years = sorted(df["iyear"].unique())

selected_year = st.sidebar.selectbox(
    "Select Year",
    ["All"] + list(years)
)

filtered_df = df
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["iyear"] == selected_year]

if len(filtered_df) == 0:
    st.warning("No incident data matches the selected filter.")
    st.stop()

# -------------------------------------------------
# Key Statistics
# -------------------------------------------------
total_incidents = len(filtered_df)
total_killed = int(filtered_df["nkill"].fillna(0).sum())
total_wounded = int(filtered_df["nwound"].fillna(0).sum())
countries_count = filtered_df["country_txt"].nunique()
groups_count = filtered_df["gname"].nunique()

top_countries = filtered_df["country_txt"].value_counts().head(10)
top_groups = filtered_df["gname"].value_counts().head(10)
attack_types = filtered_df["attacktype1_txt"].value_counts()
weapon_types = filtered_df["weaptype1_txt"].value_counts()

avg_killed = filtered_df["nkill"].fillna(0).mean()

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
col1.metric("Incidents", f"{total_incidents:,}")
col2.metric("Fatalities", f"{total_killed:,}")
col3.metric("Injuries", f"{total_wounded:,}")
col4.metric("Assessed Threat Level", threat)

# -------------------------------------------------
# Executive Summary
# -------------------------------------------------
st.subheader("Executive Intelligence Brief")

top_country_str = top_countries.index[0] if len(top_countries) > 0 else "N/A"
top_group_str = top_groups.index[0] if len(top_groups) > 0 else "N/A"
top_attack_str = attack_types.index[0] if len(attack_types) > 0 else "N/A"
top_weapon_str = weapon_types.index[0] if len(weapon_types) > 0 else "N/A"

period_label = f"the year {selected_year}" if selected_year != "All" else "the complete GTD recorded period"

summary = f"""
**Operational Overview:**
During {period_label}, a total of **{total_incidents:,}** security incidents were cataloged across **{countries_count}** nations, resulting in **{total_killed:,}** fatalities and **{total_wounded:,}** non-fatal injuries.

- **Threat Classification:** Evaluated at **{threat}** severity.
- **Primary Geopolitical Focus:** Highest incident concentration documented in **{top_country_str}**.
- **Most Active Organization:** **{top_group_str}**.
- **Predominant Attack Modality:** **{top_attack_str}**.
- **Predominant Weapon Category:** **{top_weapon_str}**.
"""

st.info(summary)

# -------------------------------------------------
# Analytics Charts
# -------------------------------------------------
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("Top 10 High-Risk Countries")
    fig = px.bar(
        top_countries,
        x=top_countries.values,
        y=top_countries.index,
        orientation="h",
        labels={"x": "Total Incidents", "y": "Country"},
        title="Incident Volume by Country"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with c_right:
    st.subheader("Most Active Identified Groups")
    fig2 = px.bar(
        top_groups,
        x=top_groups.values,
        y=top_groups.index,
        orientation="h",
        labels={"x": "Incidents Attributed", "y": "Organization"},
        title="Incidents by Group / Organization"
    )
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# Tactical Recommendations
# -------------------------------------------------
st.subheader("Tactical Directives & Action Items")

recommendation = f"""
1. **Targeted Border & Surveillance Hardening:** Allocate priority defense surveillance assets toward primary friction zones in **{top_country_str}**.
2. **Network Counter-Operations:** Coordinate multilateral intelligence initiatives targeting command and logistics nodes of **{top_group_str}**.
3. **Critical Infrastructure Protection:** Harden regional key infrastructure frequently exposed to **{top_attack_str}** tactics.
4. **Counter-Explosive & Weapons Interdiction:** Intensify border and transit sweeps focused on mitigating trafficking of **{top_weapon_str}**.
5. **Predictive Intelligence Updates:** Refresh machine-learning risk scoring cycles continuously as new field observations are logged.
"""

st.success(recommendation)

# -------------------------------------------------
# Download Report
# -------------------------------------------------
report = f"""==================================================
AI MILITARY INTELLIGENCE EXECUTIVE REPORT
Target Period: {selected_year}
==================================================

KEY OPERATIONAL METRICS:
- Total Incidents: {total_incidents:,}
- Cumulative Fatalities: {total_killed:,}
- Cumulative Injuries: {total_wounded:,}
- Countries Affected: {countries_count}
- Assessed Threat Level: {threat}

PRIMARY THREAT INDICATORS:
- Highest Impact Country: {top_country_str}
- Leading Active Organization: {top_group_str}
- Prevalent Attack Type: {top_attack_str}
- Prevalent Weapon Category: {top_weapon_str}

TACTICAL DIRECTIVES:
{recommendation}
==================================================
Report generated automatically by AI-Based Military Intelligence Dashboard.
"""

st.download_button(
    "📄 Download Full Intelligence Report (TXT)",
    report,
    file_name=f"Intelligence_Report_{selected_year}.txt",
    mime="text/plain"
)
