from pathlib import Path
import pandas as pd
import numpy as np
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
# Project Paths
# ---------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"


def train_attack_model():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading GTD Dataset for Attack Model...")
    data_file = DATA_DIR / "globalterrorism.csv"
    if not data_file.exists():
        data_file = DATA_DIR / "globalterrorism.csv.zip"

    if not data_file.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_DIR / 'globalterrorism.csv'} or {DATA_DIR / 'globalterrorism.csv.zip'}. "
            "Please place globalterrorism.csv in the data/ folder."
        )

    print(f"Reading dataset from: {data_file}")
    df = pd.read_csv(
        data_file,
        encoding="latin1",
        low_memory=False
    )

    print("Original Shape:", df.shape)

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

    df["nkill"] = df["nkill"].fillna(0)
    df["nwound"] = df["nwound"].fillna(0)
    df = df.dropna()

    print("After Cleaning:", df.shape)

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

    target_encoder = LabelEncoder()
    df[target] = target_encoder.fit_transform(df[target])

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print("\nTraining Model (Random Forest)...")
    model = RandomForestClassifier(
        n_estimators=60,
        max_depth=20,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, pred)

    print("\n" + "=" * 50)
    print(f"Test Accuracy: {accuracy:.4f}")
    print("=" * 50)
    print("Classification Report:")
    print(classification_report(y_test, pred))

    model_save_path = MODELS_DIR / "attack_prediction_model.pkl"
    target_encoder_path = MODELS_DIR / "target_encoder.pkl"
    feature_encoders_path = MODELS_DIR / "feature_encoders.pkl"

    joblib.dump(model, model_save_path, compress=3)
    joblib.dump(target_encoder, target_encoder_path)
    joblib.dump(encoders, feature_encoders_path)

    file_size_mb = model_save_path.stat().st_size / (1024 * 1024)
    print("\n" + "=" * 50)
    print(f"Model Saved Successfully to: {model_save_path}")
    print(f"Compressed File Size: {file_size_mb:.2f} MB (GitHub-ready < 100 MB)")
    print("=" * 50)


if __name__ == "__main__":
    train_attack_model()
