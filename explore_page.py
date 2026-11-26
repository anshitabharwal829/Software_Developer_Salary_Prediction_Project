from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import ui

DATA_PATH = Path(__file__).parent / "survey_results_public.csv"
EDUCATION_LEVELS = ["Less than a Bachelors", "Bachelors degree", "Masters degree", "Post grad"]


def shorten_categories(categories, cutoff):
    return {name: name if count >= cutoff else "Other" for name, count in categories.items()}


def clean_experience(x):
    if x == "More than 50 years":
        return 50
    if x == "Less than 1 year":
        return 0.5
    return float(x)


def clean_education(x):
    if "Bachelor’s degree" in x:
        return "Bachelors degree"
    if "Master’s degree" in x:
        return "Masters degree"
    if "Professional degree" in x or "Other doctoral" in x:
        return "Post grad"
    return "Less than a Bachelors"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, usecols=["Country", "EdLevel", "YearsCodePro", "Employment", "ConvertedComp"])
    df = df.rename(columns={"ConvertedComp": "Salary"}).dropna()

    df = df[df["Employment"] == "Employed full-time"].drop(columns="Employment")

    df["Country"] = df["Country"].map(shorten_categories(df["Country"].value_counts(), 400))
    df = df[df["Salary"].between(10000, 250000) & (df["Country"] != "Other")]

    df["YearsCodePro"] = df["YearsCodePro"].apply(clean_experience)
    df["EdLevel"] = df["EdLevel"].apply(clean_education)
    return df


def show_explore_page():
    ui.hero("The developer salary atlas", "Full-time developers from the 2020 Stack Overflow Developer Survey.")

    if not DATA_PATH.exists():
        st.warning(
            "Survey data not found. Download the 2020 Stack Overflow Developer Survey from "
            "https://survey.stackoverflow.co/ and place `survey_results_public.csv` next to `app.py`.",
            icon="📂",
        )
        return

    df = load_data()
    if df.empty:
        st.warning("No rows left after filtering. Check that this is the 2020 survey file.")
        return

    selected = st.multiselect("Filter by country", sorted(df["Country"].unique()), placeholder="All countries",
                              format_func=lambda c: f"{ui.flag(c)}  {c}")
    if selected:
        df = df[df["Country"].isin(selected)]

    stats = df.groupby("Country")["Salary"].agg(Median="median", Responses="count").sort_values("Median")
    stats = stats.reset_index()
    top = stats.iloc[-1]
    ui.cards([
        ("Responses", f"{len(df):,}"),
        ("Median salary", f"${df['Salary'].median():,.0f}"),
        ("Countries", str(len(stats))),
        ("Highest median", f"{ui.flag(top['Country'])} ${top['Median']:,.0f}"),
    ])

    world, ranking, by_experience, by_education = st.tabs(
        ["🗺️ World map", "🏆 Ranking", "📈 Experience", "🎓 Education"])

    with world:
        mapped = stats.assign(Code=stats["Country"].map(lambda c: ui.COUNTRIES.get(c, ("", ""))[1]))
        fig = px.choropleth(mapped, locations="Code", color="Median", hover_name="Country",
                            hover_data={"Code": False, "Median": ":$,.0f", "Responses": ":,"},
                            color_continuous_scale=["#184f95", "#3987e5", "#cde2fb"],
                            title="Median salary around the world", labels={"Median": "Median salary"})
        fig.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False, showland=True,
                        landcolor="#262a45", showcountries=True, countrycolor="#0e1020",
                        projection_type="natural earth", center={"lon": 0, "lat": 0},
                        projection_rotation={"lon": 0}, lataxis_range=[-58, 85])
        ui.chart(fig, height=520, coloraxis_colorbar={"tickprefix": "$", "tickformat": "~s"})

    with ranking:
        fig = px.bar(stats, x="Median", y="Country", orientation="h", text="Median", title="Median salary by country",
                     hover_data=["Responses"], labels={"Median": "Median salary"})
        fig.update_traces(marker_color=ui.BLUE, texttemplate="$%{text:,.0f}", textposition="outside",
                          cliponaxis=False)
        fig.update_xaxes(visible=False, range=[0, stats["Median"].max() * 1.15])
        ui.chart(fig, height=max(300, 36 * len(stats) + 100), bargap=0.3, barcornerradius=4)
        with st.expander("View as table"):
            st.dataframe(stats.iloc[::-1], hide_index=True,
                         column_config={"Median": st.column_config.NumberColumn("Median salary", format="$%.0f")})

    with by_experience:
        trend = df.groupby("YearsCodePro")["Salary"].median().reset_index()
        fig = px.area(trend, x="YearsCodePro", y="Salary", title="Median salary by years of experience",
                      labels={"YearsCodePro": "Years of experience", "Salary": "Median salary"})
        fig.update_traces(line={"color": ui.BLUE, "width": 2}, fillcolor="rgba(57,135,229,.18)")
        fig.update_yaxes(tickprefix="$", tickformat="~s", rangemode="tozero")
        ui.chart(fig)

    with by_education:
        fig = px.box(df, x="EdLevel", y="Salary", title="Salary distribution by education level",
                     category_orders={"EdLevel": EDUCATION_LEVELS}, labels={"EdLevel": "Education level"})
        fig.update_traces(marker_color=ui.BLUE)
        fig.update_yaxes(tickprefix="$", tickformat="~s")
        ui.chart(fig)
