"""Shared look and feel."""
from html import escape

import streamlit as st

BLUE = "#3987e5"
HIGHLIGHT = "#d95926"

# Country name -> (flag, ISO-3 code used by the world map)
COUNTRIES = {
    "Australia": ("🇦🇺", "AUS"), "Brazil": ("🇧🇷", "BRA"), "Canada": ("🇨🇦", "CAN"),
    "France": ("🇫🇷", "FRA"), "Germany": ("🇩🇪", "DEU"), "India": ("🇮🇳", "IND"),
    "Italy": ("🇮🇹", "ITA"), "Netherlands": ("🇳🇱", "NLD"), "Poland": ("🇵🇱", "POL"),
    "Russian Federation": ("🇷🇺", "RUS"), "Spain": ("🇪🇸", "ESP"), "Sweden": ("🇸🇪", "SWE"),
    "United Kingdom": ("🇬🇧", "GBR"), "United States": ("🇺🇸", "USA"),
}

CSS = """
<style>
.stApp {
    background:
        radial-gradient(900px 500px at 85% -10%, rgba(124,108,240,.28), transparent 60%),
        radial-gradient(700px 500px at 0% 100%, rgba(20,184,166,.16), transparent 60%),
        #0e1020;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 4.5rem; }
.hero {
    padding: 2.2rem 2.4rem; border-radius: 1.4rem; margin-bottom: 1.2rem; color: #fff;
    background: linear-gradient(120deg, #4f3fd1, #8b3fc4 45%, #0f8f8a);
    background-size: 200% 200%; animation: drift 12s ease infinite;
    box-shadow: 0 18px 45px rgba(79,63,209,.35);
}
.hero h1 { margin: 0; padding: 0; font-size: 2.4rem; color: #fff; }
.hero p { margin: .5rem 0 0; opacity: .9; font-size: 1.05rem; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .9rem; margin-bottom: 1rem; }
.card {
    padding: 1.1rem 1.3rem; border-radius: 1.1rem; background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.11); transition: transform .2s, border-color .2s;
}
.card:hover { transform: translateY(-4px); border-color: #7c6cf0; }
.card small { display: block; color: #b4b8da; }
.card b { display: block; font-size: 1.75rem; line-height: 1.5; }
.result {
    text-align: center; padding: 1.8rem 1rem; border-radius: 1.4rem; margin-bottom: 1rem;
    background: linear-gradient(160deg, rgba(124,108,240,.28), rgba(20,184,166,.18));
    border: 1px solid rgba(255,255,255,.16); animation: rise .6s ease;
}
.result .amount {
    font-size: 4rem; font-weight: 800; line-height: 1.15;
    background: linear-gradient(90deg, #a99cff, #5eead4); -webkit-background-clip: text;
    background-clip: text; color: transparent;
}
.result .sub { color: #c5c8e8; }
[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255,255,255,.035); }
@keyframes drift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@media (prefers-reduced-motion: reduce) { .hero, .result { animation: none; } }
</style>
"""


def inject_css():
    st.html(CSS)


def hero(title, subtitle):
    st.html(f'<div class="hero"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>')


def cards(items):
    """items: list of (label, value) pairs."""
    body = "".join(f'<div class="card"><small>{escape(k)}</small><b>{escape(v)}</b></div>' for k, v in items)
    st.html(f'<div class="cards">{body}</div>')


def flag(country):
    return COUNTRIES.get(country, ("🌍", ""))[0]


def chart(fig, **layout):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin={"l": 10, "r": 10, "t": 50, "b": 10}, **layout)
    st.plotly_chart(fig, config={"displayModeBar": False})


def profile_inputs(key, countries, education_levels, max_experience, default):
    """Country, education and experience controls. Returns the three values."""
    country = st.selectbox("Country", countries, index=countries.index(default[0]),
                           format_func=lambda c: f"{flag(c)}  {c}", key=f"{key}_country")
    education = st.select_slider("Education level", education_levels, value=default[1], key=f"{key}_education")
    experience = st.slider("Years of experience", 0, max_experience, default[2], key=f"{key}_experience")
    return country, education, experience
