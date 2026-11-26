import streamlit as st

import ui
from explore_page import show_explore_page
from predict_page import show_predict_page

st.set_page_config(page_title="Developer Salary Predictor", page_icon="🚀", layout="wide")
ui.inject_css()

PAGES = {"🔮 Predict": show_predict_page, "🌍 Explore": show_explore_page}

with st.sidebar:
    st.title("🚀 DevSalary")
    page = st.radio("Navigate", list(PAGES))
    st.divider()
    st.caption("Estimates are based on the 2020 Stack Overflow Developer Survey.")

PAGES[page]()
