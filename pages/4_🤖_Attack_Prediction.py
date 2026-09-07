import streamlit as st
import joblib
import pandas as pd

model = joblib.load(
    "models/attack_prediction_model.pkl"
)
encoders = joblib.load(
    "models/feature_encoders.pkl"
)
target_encoder = joblib.load(
    "models/target_encoder.pkl"
)


st.set_page_config(
    page_title="Attack Prediction",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Attack Type Prediction")

st.markdown("""
Enter the incident details below and click **Predict Attack Type**.
""")

# -------------------------
# Load Dataset
# -------------------------

df = pd.read_csv(
    "data/globalterrorism.csv",
    encoding="latin1",
    low_memory=False
)

# -------------------------
# Remove Missing Values
# -------------------------

df = df.dropna(subset=[
    "country_txt",
    "region_txt",
    "weaptype1_txt",
    "targtype1_txt",
    "gname"
])

# -------------------------
# Create Input Form
# -------------------------

with st.form("prediction_form"):

    col1, col2 = st.columns(2)

    with col1:

        country = st.selectbox(
            "🌍 Country",
            sorted(df["country_txt"].unique())
        )

        region = st.selectbox(
            "🌎 Region",
            sorted(df["region_txt"].unique())
        )

        weapon = st.selectbox(
            "🔫 Weapon Type",
            sorted(df["weaptype1_txt"].unique())
        )

        target = st.selectbox(
            "🎯 Target Type",
            sorted(df["targtype1_txt"].unique())
        )

    with col2:

        group = st.selectbox(
            "👥 Terrorist Group",
            sorted(df["gname"].unique())
        )

        success = st.selectbox(
            "✅ Attack Successful?",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        suicide = st.selectbox(
            "💣 Suicide Attack?",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        nkill = st.number_input(
            "☠ Number of Fatalities",
            min_value=0,
            value=0,
            step=1
        )

        nwound = st.number_input(
            "🏥 Number of Injured",
            min_value=0,
            value=0,
            step=1
        )

    submitted = st.form_submit_button("🚀 Predict Attack Type")
    if submitted:
        st.success("Prediction request received.")

country = encoders["country_txt"].transform([country])[0]
region = encoders["region_txt"].transform([region])[0]
weapon = encoders["weaptype1_txt"].transform([weapon])[0]
target = encoders["targtype1_txt"].transform([target])[0]
group = encoders["gname"].transform([group])[0]

input_df = pd.DataFrame({
    "country_txt": [country],
    "region_txt": [region],
    "weaptype1_txt": [weapon],
    "targtype1_txt": [target],
    "gname": [group],
    "success": [success],
    "suicide": [suicide],
    "nkill": [nkill],
    "nwound": [nwound]
})
prediction = model.predict(input_df)
attack_type = target_encoder.inverse_transform(prediction)[0]
st.success(f"Predicted Attack Type: {attack_type}")
probabilities = model.predict_proba(input_df)
confidence = probabilities.max() * 100

st.metric(
    "Prediction Confidence",
    f"{confidence:.2f}%"
)

