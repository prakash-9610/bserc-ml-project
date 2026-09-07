import pandas as pd
import streamlit as st

@st.cache_resource
def load_data():
    df = pd.read_csv(
        "data/globalterrorism.csv",
        encoding="latin1",
        low_memory=False
    )

    # Fill missing values
    df["nkill"] = df["nkill"].fillna(0)
    df["nwound"] = df["nwound"].fillna(0)

    return df