import streamlit as st
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Threat Level Prediction",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 AI Threat Level Prediction System")

# -------------------------------
# Load Dataset
# -------------------------------
df = pd.read_csv(
    "data/globalterrorism.csv",
    encoding="latin1",
    low_memory=False
)

df = df[[
    "country_txt",
    "region_txt",
    "attacktype1_txt",
    "weaptype1_txt",
    "targtype1_txt",
    "nkill",
    "nwound"
]]

df = df.dropna()

# -------------------------------
# Create Threat Level
# -------------------------------
df["impact"] = df["nkill"] + df["nwound"]

def classify_threat(x):
    if x <= 2:
        return "LOW"
    elif x <= 10:
        return "MEDIUM"
    else:
        return "HIGH"

df["threat_level"] = df["impact"].apply(classify_threat)

# -------------------------------
# Encode Categorical Data
# -------------------------------
encoders = {}

for col in [
    "country_txt",
    "region_txt",
    "attacktype1_txt",
    "weaptype1_txt",
    "targtype1_txt"
]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# Encode target
target_encoder = LabelEncoder()
df["threat_level"] = target_encoder.fit_transform(df["threat_level"])

# -------------------------------
# Train Model
# -------------------------------

X = df.drop(columns=["threat_level", "impact"])
y = df["threat_level"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.header("Input Parameters")

country = st.sidebar.selectbox("Country", df["country_txt"].unique())
region = st.sidebar.selectbox("Region", df["region_txt"].unique())
attack = st.sidebar.selectbox("Attack Type", df["attacktype1_txt"].unique())
weapon = st.sidebar.selectbox("Weapon Type", df["weaptype1_txt"].unique())
target = st.sidebar.selectbox("Target Type", df["targtype1_txt"].unique())

nkill = st.sidebar.number_input("Number Killed", 0, 1000, 0)
nwound = st.sidebar.number_input("Number Wounded", 0, 1000, 0)

# -------------------------------
# Prediction Button
# -------------------------------
if st.button("🚨 Predict Threat Level"):

    # Encode inputs
    input_data = np.array([[
        country,
        region,
        attack,
        weapon,
        target,
        nkill,
        nwound
    ]])

    prediction = model.predict(input_data)
    probability = model.predict_proba(input_data)

    result = target_encoder.inverse_transform(prediction)[0]
    confidence = np.max(probability) * 100

    # -------------------------------
    # Output
    # -------------------------------
    st.subheader("🔍 Prediction Result")

    if result == "LOW":
        st.success(f"🟢 Threat Level: {result}")
    elif result == "MEDIUM":
        st.warning(f"🟡 Threat Level: {result}")
    else:
        st.error(f"🔴 Threat Level: {result}")

    st.metric("Confidence Score", f"{confidence:.2f}%")

    st.write("### Probability Distribution")
    st.bar_chart(probability[0])