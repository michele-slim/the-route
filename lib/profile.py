"""
Profile persistence for The Route.

V1: single local profile saved to data/profiles/current.json. Snapshot and
Next Steps cached alongside it so they survive a browser refresh.

Multi-user persistence comes later.
"""

import json
import os
from pathlib import Path
from typing import Optional

import streamlit as st

_DATA_DIR = Path(__file__).parent.parent / "data" / "profiles"
_PROFILE_PATH = _DATA_DIR / "current.json"


def _ephemeral() -> bool:
    """Private by default: nothing is written to shared server storage, so each
    visitor's session is fully isolated (st.session_state is already per-visitor)
    and no one can ever see another family's answers. This is the safe default
    for the shared demo link.

    Opt OUT only for single-user local dev where you want answers to survive a
    browser refresh, by setting PERSIST_PROFILES=1 in the environment or secrets."""
    if os.environ.get("PERSIST_PROFILES"):
        return False
    try:
        if st.secrets.get("PERSIST_PROFILES", False):
            return False
    except Exception:
        pass
    return True


def _ensure_dir() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def _persist(payload: dict) -> None:
    if _ephemeral():
        return
    _ensure_dir()
    _PROFILE_PATH.write_text(json.dumps(payload, indent=2, default=str))


def save_profile(profile: dict) -> None:
    _ensure_dir()
    payload = _read_payload()
    payload["profile"] = profile
    # New profile invalidates downstream cached generations and the
    # parent's confirmation — they must re-review what changed.
    payload.pop("snapshot", None)
    payload.pop("next_steps", None)
    payload.pop("confirmed", None)
    _persist(payload)


def set_confirmed() -> None:
    """Parent confirmed the 'Did we get this right?' playback."""
    _ensure_dir()
    payload = _read_payload()
    payload["confirmed"] = True
    _persist(payload)


def save_note(note: str) -> None:
    """Append a parent note from the review screen onto the profile.

    The note rides with the profile so every downstream generation sees it.
    Invalidates cached generations but not the review itself.
    """
    _ensure_dir()
    payload = _read_payload()
    profile = payload.get("profile") or {}
    existing = profile.get("parent_note", "")
    profile["parent_note"] = (existing + "\n\n" + note).strip() if existing else note
    payload["profile"] = profile
    payload.pop("snapshot", None)
    payload.pop("next_steps", None)
    _persist(payload)
    st.session_state["profile"] = profile


def save_snapshot(snapshot: str) -> None:
    _ensure_dir()
    payload = _read_payload()
    payload["snapshot"] = snapshot
    payload.pop("next_steps", None)  # Next Steps depend on snapshot
    _persist(payload)


def save_next_steps(next_steps: str) -> None:
    _ensure_dir()
    payload = _read_payload()
    payload["next_steps"] = next_steps
    _persist(payload)


def clear() -> None:
    if _PROFILE_PATH.exists():
        _PROFILE_PATH.unlink()


def clear_snapshot() -> None:
    payload = _read_payload()
    payload.pop("snapshot", None)
    payload.pop("next_steps", None)
    _ensure_dir()
    _persist(payload)


def clear_next_steps() -> None:
    payload = _read_payload()
    payload.pop("next_steps", None)
    _ensure_dir()
    _persist(payload)


def _read_payload() -> dict:
    if _ephemeral() or not _PROFILE_PATH.exists():
        return {}
    try:
        return json.loads(_PROFILE_PATH.read_text())
    except json.JSONDecodeError:
        return {}


def hydrate_session_state() -> None:
    """Pull profile / snapshot / next_steps from disk into session_state if missing.

    Call this at the top of every page so a browser refresh doesn't blow
    away the user's work.
    """
    payload = _read_payload()
    for key in ("profile", "snapshot", "next_steps", "confirmed"):
        if key not in st.session_state and key in payload:
            st.session_state[key] = payload[key]


def load_profile() -> Optional[dict]:
    return _read_payload().get("profile")
