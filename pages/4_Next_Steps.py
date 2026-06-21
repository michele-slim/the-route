"""
Next Steps page — The Route

Takes the intake profile + Snapshot and produces a prioritized action list,
bucketed This week / This month / This year / Beyond.

v0.1 — May 10, 2026.
"""

import json

import streamlit as st

from lib.claude_client import stream_message, OPUS
from lib.prompts import VOICE_PROMPT, NEXT_STEPS_INSTRUCTIONS
from lib.profile import save_next_steps, clear_next_steps, hydrate_session_state, save_note
from lib.export import build_export_text

st.set_page_config(page_title="Next Steps — The Route", layout="centered")
hydrate_session_state()


# ─────────────────────────────────────────────
# Guards: profile + snapshot must exist
# ─────────────────────────────────────────────
profile = st.session_state.get("profile")
snapshot = st.session_state.get("snapshot")

if not profile:
    st.title("We need to hear about your kid first.")
    st.write("The Next Steps build on the intake. Without it there's nothing to prioritize.")
    st.page_link("pages/1_Intake.py", label="Go to the intake →")
    st.stop()

if not snapshot:
    st.title("Read the Snapshot first.")
    st.write(
        "Next Steps build on what the Snapshot already laid out. "
        "Open the Snapshot, then come back."
    )
    st.page_link("pages/3_Snapshot.py", label="Go to the Snapshot →")
    st.stop()


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _their_name(p: dict) -> str:
    return (p.get("their_name") or "your kid").strip() or "your kid"


def _profile_for_model(p: dict) -> str:
    cleaned = {}
    for k, v in p.items():
        if v in (None, "", "—", []):
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        cleaned[k] = v
    return json.dumps(cleaned, indent=2, default=str)


def _build_user_message(p: dict, snap: str) -> str:
    return (
        "Here is the parent's intake and the Snapshot you already wrote for them. "
        "Write the Next Steps page now, following the structure in your instructions.\n\n"
        f"## Intake\n```json\n{_profile_for_model(p)}\n```\n\n"
        f"## Snapshot\n{snap}"
    )


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
their = _their_name(profile)
st.title(f"What to do, in what order.")
st.caption(
    f"Prioritized for {their}. This is the page to come back to. "
    "Each item: why it matters, what to do, where to start, what to watch out for."
)
st.write("---")


# ─────────────────────────────────────────────
# Generate (cache in session_state, regen on demand)
# ─────────────────────────────────────────────
def _generate():
    system = VOICE_PROMPT + "\n\n---\n\n" + NEXT_STEPS_INSTRUCTIONS
    user = _build_user_message(profile, snapshot)
    placeholder = st.empty()
    chunks: list[str] = []
    for piece in stream_message(system=system, user=user, model=OPUS, max_tokens=4500):
        chunks.append(piece)
        placeholder.markdown("".join(chunks))
    return "".join(chunks)


next_steps = st.session_state.get("next_steps")

if next_steps:
    st.markdown(next_steps)
else:
    with st.spinner("Pulling together what comes next…"):
        try:
            next_steps = _generate()
            st.session_state["next_steps"] = next_steps
            save_next_steps(next_steps)
        except Exception as e:
            st.error(
                "Something broke trying to generate Next Steps. "
                "Check that the Anthropic API key is set in `.streamlit/secrets.toml`."
            )
            st.exception(e)
            st.stop()


# ─────────────────────────────────────────────
# Actions — "this isn't quite right" fix loop (mirrors the Snapshot).
# One line of correction saves a note and regenerates this page so the
# fix sticks. No raw "Regenerate" — corrections should teach the tool.
# ─────────────────────────────────────────────
st.write("---")

with st.expander("Something on this page isn't right →"):
    fix = st.text_input(
        "Tell us what's off, in a line:",
        key="next_steps_fix",
    )
    if st.button("Fix it"):
        if fix.strip():
            save_note(f"Correction from the parent after reading Next Steps: {fix.strip()}")
            st.session_state.pop("next_steps", None)
            clear_next_steps()
            st.rerun()

st.button("Open Chat →", disabled=True, help="Coming next build.")


# ─────────────────────────────────────────────
# Testing aid: download everything to email back to Michele.
# Bundles the intake answers + this Snapshot + these Next Steps.
# ─────────────────────────────────────────────
st.write("---")
st.subheader("Testing The Route?")
st.write(
    "Download your full session — your answers plus what The Route showed you — "
    "and email it to **mkunken@gmail.com**. Nothing is sent automatically; "
    "you choose what to share."
)
_their = (profile.get("their_name") or "kid").lower().replace(" ", "-")
st.download_button(
    "Download my responses (to send to Michele)",
    data=build_export_text(profile, snapshot or "", next_steps or ""),
    file_name=f"the-route-session-{_their}.txt",
    mime="text/plain",
)
