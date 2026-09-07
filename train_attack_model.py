import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ---------------------------------------------------
# Create models folder
# ---------------------------------------------------

os.makedirs("models", exist_ok=True)

# ---------------------------------------------------
# Load Dataset
# ---------------------------------------------------

print("Loading GTD Dataset...")

df = pd.read_csv(
    "data/globalterrorism.csv",
    encoding="latin1",
    low_memory=False
)

print("Original Shape:", df.shape)

# ---------------------------------------------------
# Select Features
# ---------------------------------------------------

features = [
    "country_txt",
    "region_txt",
    "weaptype1_txt",
    "targtype1_txt",
    "gname",
    "success",
    "suicide",
    "nkill",
    "nwound"
]

target = "attacktype1_txt"

df = df[features + [target]]

# ---------------------------------------------------
# Handle Missing Values
# ---------------------------------------------------

df["nkill"] = df["nkill"].fillna(0)
df["nwound"] = df["nwound"].fillna(0)

df = df.dropna()

print("After Cleaning:", df.shape)

# ---------------------------------------------------
# Encode Categorical Features
# ---------------------------------------------------

encoders = {}

categorical_features = [
    "country_txt",
    "region_txt",
    "weaptype1_txt",
    "targtype1_txt",
    "gname"
]

for col in categorical_features:
    encoder = LabelEncoder()
    df[col] = encoder.fit_transform(df[col])
    encoders[col] = encoder

# ---------------------------------------------------
# Encode Target
# ---------------------------------------------------

target_encoder = LabelEncoder()
df[target] = target_encoder.fit_transform(df[target])

# ---------------------------------------------------
# Features and Labels
# ---------------------------------------------------

X = df[features]
y = df[target]

# ---------------------------------------------------
# Train/Test Split
# ---------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# ---------------------------------------------------
# Train Random Forest
# ---------------------------------------------------

print("\nTraining Model...")

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ---------------------------------------------------
# Prediction
# ---------------------------------------------------

pred = model.predict(X_test)

# ---------------------------------------------------
# Evaluation
# ---------------------------------------------------

accuracy = accuracy_score(y_test, pred)

print("\n" + "=" * 50)
print("Accuracy")
print("=" * 50)
print(f"{accuracy:.4f}")

print("\n" + "=" * 50)
print("Classification Report")
print("=" * 50)
print(classification_report(y_test, pred))

print("=" * 50)
print("Confusion Matrix")
print("=" * 50)
print(confusion_matrix(y_test, pred))

# ---------------------------------------------------
# Save Model
# ---------------------------------------------------

joblib.dump(model, "models/attack_prediction_model.pkl")
joblib.dump(target_encoder, "models/target_encoder.pkl")
joblib.dump(encoders, "models/feature_encoders.pkl")

print("\n" + "=" * 50)
print("Model Saved Successfully")
print("=" * 50)