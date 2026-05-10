"""
The Route — caregiver navigator for parents of young people with IDD
navigating the transition to adulthood.

This is the entry point. Run with:
    streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="The Route",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("The Route")
st.subheader("A guide for parents and caregivers of young people with IDD navigating the transition to adulthood.")

st.write("")
st.write(
    "This is a placeholder home page. The real intake, snapshot, "
    "next steps, and chat pages will live in the `pages/` folder."
)

st.write("---")

# Smoke test: confirm the Anthropic API key is loading correctly
# Remove or hide this block once we're past initial setup
if "ANTHROPIC_API_KEY" in st.secrets and st.secrets["ANTHROPIC_API_KEY"] != "PASTE_YOUR_KEY_HERE":
    st.success("API key loaded. Ready to wire up Claude.")
else:
    st.warning(
        "No API key detected. Open `.streamlit/secrets.toml` and paste your "
        "Anthropic API key between the quotes."
    )
