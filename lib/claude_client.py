"""
Thin wrapper around the Anthropic SDK for The Route.

Centralizes model choice, key handling, and streaming so pages don't repeat it.
"""

import streamlit as st
from anthropic import Anthropic

OPUS = "claude-opus-4-7"
SONNET = "claude-sonnet-4-6"


def _client() -> Anthropic:
    return Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def stream_message(
    system: str,
    user: str,
    model: str = OPUS,
    max_tokens: int = 2000,
):
    """Yield text chunks as they stream from the model."""
    with _client().messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=[
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user}],
    ) as stream:
        for text in stream.text_stream:
            yield text
