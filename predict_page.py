import pickle
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import ui
from explore_page import DATA_PATH, EDUCATION_LEVELS, load_data

MODEL_PATH = Path(__file__).parent / "saved_steps.pkl"
MAX_EXPERIENCE = 50


@st.cache_resource
def load_model():
    with open(MODEL_PATH, "rb") as file:
        return pickle.load(file)


def predict(data, countries, educations, years):
    """Predicted salary for each (country, education, years) row."""
    X = pd.DataFrame(
        {
            "Country": data["le_country"].transform(countries),
            "EdLevel": data["le_education"].transform(educations),
            "YearsCodePro": [float(y) for y in years],
        }
    )
    return data["model"].predict(X)


def show_predict_page():
    data = load_model()
    # Options come from the encoders, so they always match what the model knows.
    countries = list(data["le_country"].classes_)

    ui.hero("What is your code worth?", "Move the controls and watch your estimated salary update live.")
    inputs, result = st.columns([2, 3], gap="large")

    with inputs, st.container(border=True):
        st.subheader("Your profile")
        country = st.selectbox("Country", countries, index=countries.index("United States"),
                               format_func=lambda c: f"{ui.flag(c)}  {c}")
        education = st.select_slider("Education level", EDUCATION_LEVELS, value="Bachelors degree")
        experience = st.slider("Years of experience", 0, MAX_EXPERIENCE, 3)

    salary = predict(data, [country], [education], [experience])[0]

    with result:
        st.html(
            f'<div class="result"><div class="sub">{ui.flag(country)} Estimated yearly salary in {escape(country)}</div>'
            f'<div class="amount">${salary:,.0f}</div>'
            f'<div class="sub">about ${salary / 12:,.0f} per month, before tax</div></div>'
        )
        items = []
        if DATA_PATH.exists():
            df = load_data()
            peers = df.loc[df["Country"] == country, "Salary"]
            if len(peers):
                items.append((f"Above this share of {country} responses", f"{(peers < salary).mean():.0%}"))
                items.append((f"Median in {country}", f"${peers.median():,.0f}"))
        later = predict(data, [country], [education], [min(experience + 5, MAX_EXPERIENCE)])[0]
        items.append(("Estimate with 5 more years", f"${later:,.0f}"))
        ui.cards(items)

    growth, abroad = st.tabs(["📈 Your career path", "✈️ Same you, other countries"])

    with growth:
        years = list(range(MAX_EXPERIENCE + 1))
        curve = pd.DataFrame({"Years": years})
        curve["Salary"] = predict(data, [country] * len(years), [education] * len(years), years)
        fig = px.area(curve, x="Years", y="Salary", title="Model estimate by years of experience",
                      labels={"Years": "Years of experience", "Salary": "Estimated salary"})
        fig.update_traces(line={"color": ui.BLUE, "width": 2}, fillcolor="rgba(57,135,229,.18)",
                          hovertemplate="%{x} years: $%{y:,.0f}<extra></extra>")
        fig.add_scatter(x=[experience], y=[salary], mode="markers+text", text=["You"], textposition="top center",
                        marker={"color": ui.HIGHLIGHT, "size": 14, "line": {"color": "white", "width": 2}},
                        hoverinfo="skip", showlegend=False)
        fig.update_yaxes(tickprefix="$", tickformat="~s", rangemode="tozero")
        ui.chart(fig)
        st.caption("Jumps in the line come from the model, which is a decision tree.")

    with abroad:
        n = len(countries)
        world = pd.DataFrame({"Country": countries})
        world["Salary"] = predict(data, countries, [education] * n, [experience] * n)
        world = world.sort_values("Salary")
        fig = px.bar(world, x="Salary", y="Country", orientation="h", text="Salary",
                     title="Your profile around the world (your country in orange)",
                     labels={"Salary": "Estimated salary"})
        fig.update_traces(marker_color=[ui.HIGHLIGHT if c == country else ui.BLUE for c in world["Country"]],
                          texttemplate="$%{text:,.0f}", textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}: $%{x:,.0f}<extra></extra>")
        fig.update_xaxes(visible=False, range=[0, world["Salary"].max() * 1.15])
        ui.chart(fig, height=560, bargap=0.3, barcornerradius=4)
