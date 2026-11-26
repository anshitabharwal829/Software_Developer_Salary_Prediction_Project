"""Loading and querying the trained salary model."""
import pickle
from pathlib import Path

import pandas as pd
import streamlit as st

MODEL_PATH = Path(__file__).parent / "saved_steps.pkl"
EDUCATION_LEVELS = ["Less than a Bachelors", "Bachelors degree", "Masters degree", "Post grad"]
MAX_EXPERIENCE = 50


@st.cache_resource
def load_model():
    with open(MODEL_PATH, "rb") as file:
        return pickle.load(file)


def countries():
    # Options come from the encoder, so they always match what the model knows.
    return list(load_model()["le_country"].classes_)


def predict(country_list, education_list, years):
    """Predicted salary for each (country, education, years) row."""
    data = load_model()
    X = pd.DataFrame(
        {
            "Country": data["le_country"].transform(country_list),
            "EdLevel": data["le_education"].transform(education_list),
            "YearsCodePro": [float(y) for y in years],
        }
    )
    return data["model"].predict(X)


def career_curve(country, education):
    """Estimate for every whole year of experience; the list index is the year."""
    n = MAX_EXPERIENCE + 1
    return predict([country] * n, [education] * n, range(n))
