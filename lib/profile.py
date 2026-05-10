"""
Profile persistence for The Route.

V1: single local profile saved to data/profiles/current.json. Snapshot and
Next Steps cached alongside it so they survive a browser refresh.

Multi-user persistence comes later.
"""

import json
from pathlib import Path
from typing import Optional

import streamlit as st

_DATA_DIR = Path(__file__).parent.parent / "data" / "profiles"
_PROFILE_PATH = _DATA_DIR / "current.json"


def _ensure_dir() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_profile(profile: dict) -> None:
    _ensure_dir()
    payload = _read_payload()
    payload["profile"] = profile
    # New profile invalidates downstream cached generations
    payload.pop("snapshot", None)
    payload.pop("next_steps", None)
    _PROFILE_PATH.write_text(json.dumps(payload, indent=2, default=str))


def save_snapshot(snapshot: str) -> None:
    _ensure_dir()
    payload = _read_payload()
    payload["snapshot"] = snapshot
    payload.pop("next_steps", None)  # Next Steps depend on snapshot
    _PROFILE_PATH.write_text(json.dumps(payload, indent=2, default=str))


def save_next_steps(next_steps: str) -> None:
    _ensure_dir()
    payload = _read_payload()
    payload["next_steps"] = next_steps
    _PROFILE_PATH.write_text(json.dumps(payload, indent=2, default=str))


def clear() -> None:
    if _PROFILE_PATH.exists():
        _PROFILE_PATH.unlink()


def clear_snapshot() -> None:
    payload = _read_payload()
    payload.pop("snapshot", None)
    payload.pop("next_steps", None)
    _ensure_dir()
    _PROFILE_PATH.write_text(json.dumps(payload, indent=2, default=str))


def clear_next_steps() -> None:
    payload = _read_payload()
    payload.pop("next_steps", None)
    _ensure_dir()
    _PROFILE_PATH.write_text(json.dumps(payload, indent=2, default=str))


def _read_payload() -> dict:
    if not _PROFILE_PATH.exists():
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
    for key in ("profile", "snapshot", "next_steps"):
        if key not in st.session_state and key in payload:
            st.session_state[key] = payload[key]


def load_profile() -> Optional[dict]:
    return _read_payload().get("profile")
