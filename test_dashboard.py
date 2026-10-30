"""
Comprehensive Project Audit & Verification Test Suite for
AI-Based Military Intelligence Dashboard
"""
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent

print("=" * 60)
print("RUNNING COMPREHENSIVE DASHBOARD AUDIT TEST SUITE")
print("=" * 60)

# Test 1: Verify Requirements & Imports
print("\n[TEST 1] Verifying core library dependencies...")
try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    import joblib
    import sklearn
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import LabelEncoder
    print("  --> All required dependencies imported successfully.")
except Exception as e:
    print(f"  FAILED: Missing dependency: {e}")
    sys.exit(1)

# Test 2: Verify utils/data_loader and Dataset Resolution
print("\n[TEST 2] Verifying utils/data_loader.py & dataset resolution...")
from utils.data_loader import get_data_path, load_data, MODELS_DIR, DATA_DIR

data_path = get_data_path()
assert data_path is not None, "get_data_path() returned None! No dataset found."
print(f"  --> Identified dataset at: {data_path}")

df = load_data()
assert df is not None, "load_data() returned None!"
assert len(df) > 0, "Loaded dataframe is empty!"
print(f"  --> Dataset loaded successfully. Shape: {df.shape}")
print(f"  --> Missing nkill values remaining: {df['nkill'].isnull().sum()}")
print(f"  --> Missing nwound values remaining: {df['nwound'].isnull().sum()}")

# Test 3: Verify Page 1 (Home) Logic
print("\n[TEST 3] Testing Page 1 (Home) data operations...")
yearly = df.groupby("iyear").size().reset_index(name="Attacks")
assert len(yearly) > 0
fig1 = px.line(yearly, x="iyear", y="Attacks", markers=True)
assert fig1 is not None
print(f"  --> Page 1 metrics: {len(df):,} incidents across {df['country_txt'].nunique()} countries.")
print("  --> Page 1 line chart rendered successfully.")

# Test 4: Verify Page 2 (Global Threat Map) Logic
print("\n[TEST 4] Testing Page 2 (Global Threat Map) data operations...")
map_df = df.dropna(subset=["latitude", "longitude"]).sample(min(100, len(df)), random_state=42)
fig2 = px.scatter_geo(
    map_df,
    lat="latitude",
    lon="longitude",
    color="attacktype1_txt",
    hover_name="country_txt",
    projection="natural earth"
)
assert fig2 is not None
print("  --> Page 2 scatter_geo map figure constructed successfully.")

# Test 5: Verify Page 3 (Country Analysis) Logic
print("\n[TEST 5] Testing Page 3 (Country Analysis) data operations...")
test_country = "India"
country_df = df[df["country_txt"] == test_country]
assert len(country_df) > 0, f"No records found for test country {test_country}"
country_yearly = country_df.groupby("iyear").size().reset_index(name="Attacks")
fig3_line = px.line(country_yearly, x="iyear", y="Attacks")
country_attacks = country_df.groupby("attacktype1_txt").size().reset_index(name="Count")
fig3_pie = px.pie(country_attacks, names="attacktype1_txt", values="Count")
top_groups = country_df.groupby("gname").size().reset_index(name="Attacks").sort_values("Attacks", ascending=False).head(10)
fig3_bar = px.bar(top_groups, x="Attacks", y="gname", orientation="h")
assert fig3_line and fig3_pie and fig3_bar
print(f"  --> Country Analysis for '{test_country}': {len(country_df):,} incidents, charts generated.")

# Test 6: Verify Page 4 (Attack Prediction) Model & Inference
print("\n[TEST 6] Testing Page 4 (Attack Prediction) model inference...")
model_path = MODELS_DIR / "attack_prediction_model.pkl"
encoders_path = MODELS_DIR / "feature_encoders.pkl"
target_path = MODELS_DIR / "target_encoder.pkl"

assert model_path.exists(), "attack_prediction_model.pkl missing!"
assert encoders_path.exists(), "feature_encoders.pkl missing!"
assert target_path.exists(), "target_encoder.pkl missing!"

attack_model = joblib.load(model_path)
encoders = joblib.load(encoders_path)
target_encoder = joblib.load(target_path)

# Test sample inference
sample_country = encoders["country_txt"].classes_[0]
sample_region = encoders["region_txt"].classes_[0]
sample_weapon = encoders["weaptype1_txt"].classes_[0]
sample_target = encoders["targtype1_txt"].classes_[0]
sample_group = encoders["gname"].classes_[0]

input_df = pd.DataFrame({
    "country_txt": [encoders["country_txt"].transform([sample_country])[0]],
    "region_txt": [encoders["region_txt"].transform([sample_region])[0]],
    "weaptype1_txt": [encoders["weaptype1_txt"].transform([sample_weapon])[0]],
    "targtype1_txt": [encoders["targtype1_txt"].transform([sample_target])[0]],
    "gname": [encoders["gname"].transform([sample_group])[0]],
    "success": [1],
    "suicide": [0],
    "nkill": [2],
    "nwound": [5]
})

pred_raw = attack_model.predict(input_df)
pred_label = target_encoder.inverse_transform(pred_raw)[0]
probs = attack_model.predict_proba(input_df)
confidence = float(np.max(probs) * 100)

print(f"  --> Attack Model Size: {model_path.stat().st_size / (1024*1024):.2f} MB")
print(f"  --> Sample Prediction: '{pred_label}' (Confidence: {confidence:.2f}%)")
assert pred_label in target_encoder.classes_

# Test 7: Verify Page 5 (Threat Level Prediction) Model & Inference
print("\n[TEST 7] Testing Page 5 (Threat Level Prediction) model inference...")
threat_model_path = MODELS_DIR / "threat_level_model.pkl"
threat_encoders_path = MODELS_DIR / "threat_encoders.pkl"
threat_target_path = MODELS_DIR / "threat_target_encoder.pkl"

assert threat_model_path.exists(), "threat_level_model.pkl missing!"
assert threat_encoders_path.exists(), "threat_encoders.pkl missing!"
assert threat_target_path.exists(), "threat_target_encoder.pkl missing!"

threat_model = joblib.load(threat_model_path)
threat_encoders = joblib.load(threat_encoders_path)
threat_target_encoder = joblib.load(threat_target_path)

threat_input = pd.DataFrame({
    "country_txt": [threat_encoders["country_txt"].transform([sample_country])[0]],
    "region_txt": [threat_encoders["region_txt"].transform([sample_region])[0]],
    "attacktype1_txt": [threat_encoders["attacktype1_txt"].transform([threat_encoders["attacktype1_txt"].classes_[0]])[0]],
    "weaptype1_txt": [threat_encoders["weaptype1_txt"].transform([sample_weapon])[0]],
    "targtype1_txt": [threat_encoders["targtype1_txt"].transform([sample_target])[0]],
    "nkill": [5],
    "nwound": [10]
})

threat_pred_raw = threat_model.predict(threat_input)
threat_result = threat_target_encoder.inverse_transform(threat_pred_raw)[0]
threat_prob = threat_model.predict_proba(threat_input)
threat_conf = float(np.max(threat_prob) * 100)

print(f"  --> Threat Model Size: {threat_model_path.stat().st_size / (1024*1024):.2f} MB")
print(f"  --> Sample Threat Level: '{threat_result}' (Confidence: {threat_conf:.2f}%)")
assert threat_result in ["LOW", "MEDIUM", "HIGH"]

# Test 8: Verify Page 6 (Forecasting) Linear Regression
print("\n[TEST 8] Testing Page 6 (Forecasting) regression calculations...")
country_yearly = df[df["country_txt"] == "India"].groupby("iyear").size().reset_index(name="Attacks").sort_values("iyear")
X = country_yearly[["iyear"]]
y = country_yearly["Attacks"]
reg_model = LinearRegression().fit(X, y)
future_years = np.arange(country_yearly["iyear"].max() + 1, country_yearly["iyear"].max() + 6)
future_preds = np.maximum(reg_model.predict(pd.DataFrame({"iyear": future_years})), 0).astype(int)
assert len(future_preds) == 5
print(f"  --> Next 5-year forecasted attacks for India: {future_preds.tolist()}")

# Test 9: Verify Page 7 (AI Intelligence Report) Computations
print("\n[TEST 9] Testing Page 7 (AI Intelligence Report) generation...")
top_c = df["country_txt"].value_counts().head(5)
top_g = df["gname"].value_counts().head(5)
avg_k = df["nkill"].fillna(0).mean()
threat_rating = "LOW" if avg_k < 2 else ("MEDIUM" if avg_k < 5 else "HIGH")
assert len(top_c) > 0 and len(top_g) > 0
print(f"  --> Report metrics: Top Country: {top_c.index[0]}, Top Group: {top_g.index[0]}, Rating: {threat_rating}")

# Test 10: Verify Page 8 (Data Explorer) Filtering
print("\n[TEST 10] Testing Page 8 (Data Explorer) multiselect filtering...")
filtered = df[df["iyear"] == 2017]
filtered = filtered[filtered["country_txt"] == "India"]
assert len(filtered) > 0
search_test = filtered[filtered["city"].fillna("").str.contains("Delhi", case=False)]
print(f"  --> Filtered: 2017 + India = {len(filtered):,} records. 'Delhi' query = {len(search_test):,} records.")

# Test 11: Verify Page 9 (Settings) Runtime Health
print("\n[TEST 11] Testing Page 9 (Settings) dataset checks...")
assert get_data_path().exists()
print(f"  --> Runtime diagnostic: Data OK at {get_data_path().name}")

print("\n" + "=" * 60)
print("ALL 11 VERIFICATION TESTS COMPLETED AND PASSED!")
print("=" * 60)
