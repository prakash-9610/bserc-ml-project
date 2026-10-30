from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# ---------------------------------------------------
# Project Paths
# ---------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"


def train_threat_model():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading GTD Dataset for Threat Level Model...")
    data_file = DATA_DIR / "globalterrorism.csv"
    if not data_file.exists():
        data_file = DATA_DIR / "globalterrorism.csv.zip"

    if not data_file.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_DIR / 'globalterrorism.csv'} or {DATA_DIR / 'globalterrorism.csv.zip'}."
        )

    print(f"Reading dataset from: {data_file}")
    df = pd.read_csv(
        data_file,
        encoding="latin1",
        low_memory=False
    )

    cols = [
        "country_txt",
        "region_txt",
        "attacktype1_txt",
        "weaptype1_txt",
        "targtype1_txt",
        "nkill",
        "nwound"
    ]

    df = df[cols].copy()
    df["nkill"] = df["nkill"].fillna(0)
    df["nwound"] = df["nwound"].fillna(0)
    df = df.dropna()

    print("Cleaned records:", len(df))

    df["impact"] = df["nkill"] + df["nwound"]

    def classify_threat(impact_val):
        if impact_val <= 2:
            return "LOW"
        elif impact_val <= 10:
            return "MEDIUM"
        else:
            return "HIGH"

    df["threat_level"] = df["impact"].apply(classify_threat)

    encoders = {}
    categorical_cols = [
        "country_txt",
        "region_txt",
        "attacktype1_txt",
        "weaptype1_txt",
        "targtype1_txt"
    ]

    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    target_encoder = LabelEncoder()
    df["threat_level"] = target_encoder.fit_transform(df["threat_level"])

    X = df.drop(columns=["threat_level", "impact"])
    y = df["threat_level"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    print("Training Threat Level Classifier...")
    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)

    print("\n" + "=" * 50)
    print(f"Threat Level Model Accuracy: {acc:.4f}")
    print("=" * 50)
    print(classification_report(y_test, pred, target_names=target_encoder.classes_))

    model_path = MODELS_DIR / "threat_level_model.pkl"
    encoders_path = MODELS_DIR / "threat_encoders.pkl"
    target_path = MODELS_DIR / "threat_target_encoder.pkl"

    joblib.dump(model, model_path, compress=3)
    joblib.dump(encoders, encoders_path)
    joblib.dump(target_encoder, target_path)

    file_size_mb = model_path.stat().st_size / (1024 * 1024)
    print(f"Saved Threat Level Model to: {model_path} ({file_size_mb:.2f} MB)")


if __name__ == "__main__":
    train_threat_model()
