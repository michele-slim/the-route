"""
The Route — caregiver navigator for parents of young people with IDD
navigating the transition to adulthood.

This is the landing page. Run with:
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
st.subheader("A guide for parents and caregivers of young people with disabilities navigating the transition to adulthood.")

st.write("")
st.write(
    "The years from 16 to 26 pile on fast: benefits to apply for, legal decisions to make, "
    "services to line up, and deadlines no one warns you about. The Route helps you find your "
    "way through. Tell us about your kid, and we'll show you where things stand right now and "
    "what to do next, in plain language and in the right order."
)
st.caption("This is an early version we're testing. We're glad you're here.")

st.write("")
st.page_link("pages/1_Intake.py", label="Start →")

# Setup check (only surfaces if the key is missing — testers won't see it once set).
_key = ""
try:
    _key = st.secrets.get("ANTHROPIC_API_KEY", "")
except Exception:
    _key = ""
if not _key or _key == "PASTE_YOUR_KEY_HERE":
    st.write("---")
    st.warning(
        "Setup note (for Michele): no Anthropic API key detected. Open "
        "`.streamlit/secrets.toml` and paste the key. The intake and review screens "
        "work without it; the Snapshot and Next Steps need it to generate."
    )
