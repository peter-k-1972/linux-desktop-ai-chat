"""Kanonische Heimat von strip_embedded_think_blocks; Shim in provider_chunk_forensics."""

from __future__ import annotations

from app.chat.final_message_cleaning import strip_embedded_think_blocks as strip_canonical
from app.chat.provider_chunk_forensics import strip_embedded_think_blocks as strip_shim


def test_strip_embedded_think_blocks_shim_is_canonical() -> None:
    assert strip_shim is strip_canonical


def test_strip_embedded_think_blocks_removes_think_element_wrappers() -> None:
    # Wie test_chat_response_pipeline: Tags ohne Literale im Quelltext zusammensetzen.
    ot = "".join(("<", "think", ">"))
    ct = "".join(("<", "/think", ">"))
    blob = f"pre {ot}hidden{ct} post"
    out = strip_canonical(blob)
    assert "hidden" not in out
    assert out == "pre  post"


def test_strip_embedded_think_blocks_removes_reasoning_tags() -> None:
    s = "a <reasoning>x</reasoning> b"
    assert strip_canonical(s) == "a  b"
