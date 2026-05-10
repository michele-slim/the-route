"""
Snapshot page — The Route

The aha moment of the product. Takes the intake profile and renders a
personalized one-screen read of where this family is right now.

v0.1 — May 10, 2026.
"""

import json

import streamlit as st

from lib.claude_client import stream_message, OPUS
from lib.prompts import VOICE_PROMPT, SNAPSHOT_INSTRUCTIONS
from lib.profile import save_snapshot, clear_snapshot, hydrate_session_state

st.set_page_config(page_title="Snapshot — The Route", layout="centered")
hydrate_session_state()


# ─────────────────────────────────────────────
# Guard: profile must exist
# ─────────────────────────────────────────────
profile = st.session_state.get("profile")

if not profile:
    st.title("We need to hear about your young person first.")
    st.write(
        "The snapshot reads your intake and tells you where you are right now. "
        "Without the intake there's nothing to read."
    )
    st.page_link("pages/1_Intake.py", label="Go to the intake →")
    st.stop()


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _their_name(p: dict) -> str:
    return (p.get("their_name") or "your young person").strip() or "your young person"


def _profile_for_model(p: dict) -> str:
    """Trim and shape the profile for the model. Drop noisy 'Other' fallbacks
    when the user didn't fill them in."""
    cleaned = {}
    for k, v in p.items():
        if v in (None, "", "—", []):
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        cleaned[k] = v
    return json.dumps(cleaned, indent=2, default=str)


def _build_user_message(p: dict) -> str:
    return (
        "Here is the parent's intake. Write the Snapshot for them, following "
        "the section structure and tone in your instructions.\n\n"
        f"```json\n{_profile_for_model(p)}\n```"
    )


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
their = _their_name(profile)
st.title(f"Where you and {their} are right now.")
st.caption(
    "Read this once. It will not be the last word — the next page is what to do "
    "about it."
)
st.write("---")


# ─────────────────────────────────────────────
# Generate (cache in session_state, regen on demand)
# ─────────────────────────────────────────────
def _generate():
    system = VOICE_PROMPT + "\n\n---\n\n" + SNAPSHOT_INSTRUCTIONS
    user = _build_user_message(profile)
    placeholder = st.empty()
    chunks: list[str] = []
    for piece in stream_message(system=system, user=user, model=OPUS, max_tokens=2200):
        chunks.append(piece)
        placeholder.markdown("".join(chunks))
    return "".join(chunks)


snapshot = st.session_state.get("snapshot")

if snapshot:
    st.markdown(snapshot)
else:
    with st.spinner("Reading your intake…"):
        try:
            snapshot = _generate()
            st.session_state["snapshot"] = snapshot
            save_snapshot(snapshot)
        except Exception as e:
            st.error(
                "Something broke trying to generate the snapshot. "
                "Check that the Anthropic API key is set in `.streamlit/secrets.toml`."
            )
            st.exception(e)
            st.stop()


# ─────────────────────────────────────────────
# Actions
# ─────────────────────────────────────────────
st.write("---")
col_a, col_b = st.columns(2)

with col_a:
    if st.button("Regenerate"):
        st.session_state.pop("snapshot", None)
        st.session_state.pop("next_steps", None)
        clear_snapshot()
        st.rerun()

with col_b:
    st.page_link("pages/3_Next_Steps.py", label="Continue to Next Steps →")
