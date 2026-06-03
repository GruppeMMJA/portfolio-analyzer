"""
Portfolio Eingabe — merged into main Dashboard.
This file redirects to app.py.
"""
import streamlit as st

st.set_page_config(page_title="Portfolio Analyzer", layout="wide", initial_sidebar_state="collapsed")

# Redirect to Dashboard (which now contains portfolio input)
try:
    st.switch_page("app.py")
except Exception:
    st.info("Portfolio-Eingabe ist jetzt im Dashboard integriert.")
    st.markdown("[Zum Dashboard](/)", unsafe_allow_html=True)
