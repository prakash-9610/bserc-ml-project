from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"


def get_data_path():
    """Locate the GTD dataset in order of preference."""
    candidates = [
        DATA_DIR / "globalterrorism.csv",
        DATA_DIR / "globalterrorism.csv.zip",
        DATA_DIR / "globalterrorism.csv.gz",
        PROJECT_ROOT / "globalterrorism.csv",
        PROJECT_ROOT / "globalterrorism.csv.zip",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


@st.cache_data(show_spinner="Loading military intelligence dataset...")
def load_data():
    """
    Load and cache the Global Terrorism Database (GTD).
    Handles missing file scenarios gracefully with user-facing guidance.
    """
    data_path = get_data_path()

    if data_path is None:
        st.error("🚨 **Dataset File Not Found!**")
        st.warning(
            "The Global Terrorism Database could not be found at `data/globalterrorism.csv` or `data/globalterrorism.csv.zip`."
        )
        st.info(
            """
            ### 🛠️ How to Resolve:
            1. **For Streamlit Community Cloud:**
               - GitHub enforces a strict **100 MB per-file limit**.
               - The raw `globalterrorism.csv` is ~162 MB and was gitignored.
               - Commit the compressed archive `data/globalterrorism.csv.zip` (~27.5 MB) to your GitHub repo.
            2. **For Local Development:**
               - Place `globalterrorism.csv` inside the `data/` directory.
            3. **Download Dataset:**
               - Download the official Global Terrorism Database from [Kaggle GTD Dataset](https://www.kaggle.com/datasets/START-UMD/gtd).
            """
        )
        st.stop()
        return None

    try:
        df = pd.read_csv(
            data_path,
            encoding="latin1",
            low_memory=False
        )

        # Fill common missing numerical values
        if "nkill" in df.columns:
            df["nkill"] = df["nkill"].fillna(0)
        if "nwound" in df.columns:
            df["nwound"] = df["nwound"].fillna(0)

        return df
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        st.stop()
        return None
