import streamlit as st

import ui
from compare_page import show_compare_page
from explore_page import show_explore_page
from predict_page import show_predict_page

st.set_page_config(page_title="Developer Salary Predictor", page_icon="🚀", layout="wide")
ui.inject_css()

page = st.navigation(
    [
        st.Page(show_predict_page, title="Predict", icon="🔮", url_path="predict", default=True),
        st.Page(show_compare_page, title="Compare", icon="⚖️", url_path="compare"),
        st.Page(show_explore_page, title="Explore", icon="🌍", url_path="explore"),
    ],
    position="top",
)
page.run()
st.caption("Estimates are based on the 2020 Stack Overflow Developer Survey.")
