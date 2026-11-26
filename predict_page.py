from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

import ui
from explore_page import DATA_PATH, load_data
from model import EDUCATION_LEVELS, MAX_EXPERIENCE, career_curve, countries, predict

DEFAULT_PROFILE = ("United States", "Bachelors degree", 3)


def starting_profile(options):
    """Last used profile, else the one in the page link, else the default."""
    if "profile" in st.session_state:
        return st.session_state["profile"]
    country, education, years = DEFAULT_PROFILE
    query = st.query_params
    if query.get("country") in options:
        country = query["country"]
    if query.get("education") in EDUCATION_LEVELS:
        education = query["education"]
    raw = query.get("years", "")
    if raw.isdecimal() and int(raw) <= MAX_EXPERIENCE:
        years = int(raw)
    return country, education, years


def show_predict_page():
    options = countries()

    ui.hero("What is your code worth?", "Move the controls and watch your estimated salary update live.")
    inputs, result = st.columns([2, 3], gap="large")

    # Read the starting values once; changing a widget's default would reset it.
    if "predict_default" not in st.session_state or "predict_country" not in st.session_state:
        st.session_state["predict_default"] = starting_profile(options)

    with inputs, st.container(border=True):
        st.subheader("Your profile")
        country, education, experience = ui.profile_inputs(
            "predict", options, EDUCATION_LEVELS, MAX_EXPERIENCE, st.session_state["predict_default"])
        save = st.button("💾 Save this estimate", type="primary", width="stretch")
        st.caption("The address bar updates with your profile, so you can copy it to share.")

    st.session_state["profile"] = (country, education, experience)
    st.query_params.update(country=country, education=education, years=str(experience))

    curve = career_curve(country, education)
    salary = curve[experience]
    saved = st.session_state.setdefault("saved", [])
    if save:
        row = {"Country": country, "Education": education, "Years": experience, "Yearly salary (USD)": round(salary)}
        if row in saved:
            st.toast("Already saved.")
        else:
            saved.append(row)
            st.toast("Estimate saved.", icon="✅")

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
        later = curve[min(experience + 5, MAX_EXPERIENCE)]
        items.append(("Estimate with 5 more years", f"${later:,.0f}"))
        ui.cards(items)

    growth, goal, study, abroad, history = st.tabs(
        ["📈 Career path", "🎯 Salary goal", "🎓 Education", "✈️ Other countries", f"💾 Saved ({len(saved)})"])

    with growth:
        frame = pd.DataFrame({"Years": range(MAX_EXPERIENCE + 1), "Salary": curve})
        fig = px.area(frame, x="Years", y="Salary", title="Model estimate by years of experience",
                      labels={"Years": "Years of experience", "Salary": "Estimated salary"})
        fig.update_traces(line={"color": ui.BLUE, "width": 2}, fillcolor="rgba(57,135,229,.18)",
                          hovertemplate="%{x} years: $%{y:,.0f}<extra></extra>")
        fig.add_scatter(x=[experience], y=[salary], mode="markers+text", text=["You"], textposition="top center",
                        marker={"color": ui.HIGHLIGHT, "size": 14, "line": {"color": "white", "width": 2}},
                        hoverinfo="skip", showlegend=False)
        fig.update_yaxes(tickprefix="$", tickformat="~s", rangemode="tozero")
        ui.chart(fig)
        st.caption("Jumps in the line come from the model, which is a decision tree.")

    with goal:
        target = st.number_input("Target yearly salary (USD)", 10_000, 500_000,
                                 min(500_000, max(10_000, int(round(salary * 1.25, -3)))), step=5_000)
        reached = next((y for y in range(experience, MAX_EXPERIENCE + 1) if curve[y] >= target), None)
        if salary >= target:
            st.success("Your current estimate already meets this target.", icon="🎉")
        elif reached is None:
            st.warning(f"The model never reaches ${target:,.0f} for this country and education level. "
                       f"The highest later estimate is ${max(curve[experience:]):,.0f}.", icon="🧗")
        else:
            st.info(f"The estimate first reaches ${target:,.0f} at **{reached} years** of experience, "
                    f"{reached - experience} more than you have now.", icon="🎯")
        st.progress(float(min(salary / target, 1.0)), text=f"{salary / target:.0%} of your target")

    with study:
        n = len(EDUCATION_LEVELS)
        frame = pd.DataFrame({"Education": EDUCATION_LEVELS})
        frame["Salary"] = predict([country] * n, EDUCATION_LEVELS, [experience] * n)
        fig = px.bar(frame, x="Education", y="Salary", text="Salary",
                     title="Same country and experience, different education (yours in orange)")
        fig.update_traces(marker_color=[ui.HIGHLIGHT if e == education else ui.BLUE for e in EDUCATION_LEVELS],
                          texttemplate="$%{text:,.0f}", textposition="outside", cliponaxis=False,
                          hovertemplate="%{x}: $%{y:,.0f}<extra></extra>")
        fig.update_yaxes(visible=False, range=[0, frame["Salary"].max() * 1.15])
        ui.chart(fig, bargap=0.4, barcornerradius=4)

    with abroad:
        n = len(options)
        world = pd.DataFrame({"Country": options})
        world["Salary"] = predict(options, [education] * n, [experience] * n)
        world = world.sort_values("Salary")
        fig = px.bar(world, x="Salary", y="Country", orientation="h", text="Salary",
                     title="Your profile around the world (your country in orange)")
        fig.update_traces(marker_color=[ui.HIGHLIGHT if c == country else ui.BLUE for c in world["Country"]],
                          texttemplate="$%{text:,.0f}", textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}: $%{x:,.0f}<extra></extra>")
        fig.update_xaxes(visible=False, range=[0, world["Salary"].max() * 1.15])
        ui.chart(fig, height=560, bargap=0.3, barcornerradius=4)

    with history:
        if not saved:
            st.info("Nothing saved yet. Press **Save this estimate** to build a shortlist.")
        else:
            table = pd.DataFrame(saved)
            st.dataframe(table, hide_index=True)
            download, clear = st.columns(2)
            download.download_button("⬇️ Download CSV", table.to_csv(index=False), "salary_estimates.csv",
                                     "text/csv", width="stretch")
            clear.button("🗑️ Clear list", on_click=saved.clear, width="stretch")
            st.caption("Saved estimates last until you reload or close the page.")
