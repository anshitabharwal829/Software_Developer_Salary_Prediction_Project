import pandas as pd
import plotly.express as px
import streamlit as st

import ui
from model import EDUCATION_LEVELS, MAX_EXPERIENCE, career_curve, countries


def show_compare_page():
    options = countries()
    ui.hero("Compare two paths", "Put two profiles side by side: a move abroad, more study, or more experience.")

    defaults = {"A": ("United States", "Bachelors degree", 3), "B": ("India", "Masters degree", 3)}
    profiles = {}
    for column, name in zip(st.columns(2, gap="large"), defaults):
        with column, st.container(border=True):
            st.subheader(f"Profile {name}")
            country, education, years = ui.profile_inputs(
                f"compare_{name}", options, EDUCATION_LEVELS, MAX_EXPERIENCE, defaults[name])
            curve = career_curve(country, education)
            profiles[name] = (curve, curve[years], years)

    a, b = profiles["A"][1], profiles["B"][1]
    ui.cards([
        ("Profile A, yearly", f"${a:,.0f}"),
        ("Profile B, yearly", f"${b:,.0f}"),
        ("B compared with A", f"{'+' if b >= a else '-'}${abs(b - a):,.0f} ({(b - a) / a:+.0%})"),
    ])

    frame = pd.concat(
        pd.DataFrame({"Years": range(MAX_EXPERIENCE + 1), "Salary": curve, "Profile": f"Profile {name}"})
        for name, (curve, _, _) in profiles.items())
    fig = px.line(frame, x="Years", y="Salary", color="Profile", title="Career paths",
                  color_discrete_map={"Profile A": ui.BLUE, "Profile B": ui.HIGHLIGHT},
                  labels={"Years": "Years of experience", "Salary": "Estimated salary"})
    fig.update_traces(line_width=2, hovertemplate="$%{y:,.0f}")
    fig.update_yaxes(tickprefix="$", tickformat="~s", rangemode="tozero")
    ui.chart(fig, hovermode="x unified")
    st.caption("Estimates are in US dollars and are not adjusted for cost of living or tax.")
