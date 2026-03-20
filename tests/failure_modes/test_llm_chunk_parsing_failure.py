"""
Failure Injection: Malformed LLM Streaming-Chunks.

Simuliert: Unerwartete Chunk-Formen von Provider/Ollama.
Verhindert: LLM stream schema drift / malformed chunk input → Crash.
"""

from typing import Any

import pytest

from app.gui.legacy import _extract_chunk_parts


def _assert_safe_return(content: str, thinking: str, error: Any) -> None:
    """Erwartete defensive Rückgabe: immer (str, str, Optional[str])."""
    assert isinstance(content, str)
    assert isinstance(thinking, str)
    assert error is None or isinstance(error, str)


@pytest.mark.failure_mode
def test_extract_chunk_parts_message_is_string():
    """message als String statt Dict → kein Crash, leere Rückgabe."""
    chunk = {"message": "invalid"}
    content, thinking, error = _extract_chunk_parts(chunk)
    _assert_safe_return(content, thinking, error)
    assert content == ""
    assert thinking == ""
    assert error is None


@pytest.mark.failure_mode
def test_extract_chunk_parts_message_is_list():
    """message als Liste statt Dict → kein Crash, leere Rückgabe."""
    chunk = {"message": ["a", "b"]}
    content, thinking, error = _extract_chunk_parts(chunk)
    _assert_safe_return(content, thinking, error)
    assert content == ""
    assert thinking == ""
    assert error is None


@pytest.mark.failure_mode
def test_extract_chunk_parts_chunk_is_none():
    """Chunk ist None → kein Crash."""
    content, thinking, error = _extract_chunk_parts(None)
    _assert_safe_return(content, thinking, error)
    assert content == ""
    assert thinking == ""
    assert error is None


@pytest.mark.failure_mode
def test_extract_chunk_parts_chunk_is_string():
    """Chunk ist String statt Dict → kein Crash."""
    content, thinking, error = _extract_chunk_parts("not a dict")
    _assert_safe_return(content, thinking, error)
    assert content == ""
    assert thinking == ""
    assert error is None


@pytest.mark.failure_mode
def test_extract_chunk_parts_chunk_is_list():
    """Chunk ist Liste statt Dict → kein Crash."""
    content, thinking, error = _extract_chunk_parts([1, 2, 3])
    _assert_safe_return(content, thinking, error)
    assert content == ""
    assert thinking == ""
    assert error is None


@pytest.mark.failure_mode
def test_extract_chunk_parts_content_missing_in_message():
    """message ohne content → content leer, kein Crash."""
    chunk = {"message": {"thinking": "x"}}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == "x"
    assert error is None


@pytest.mark.failure_mode
def test_extract_chunk_parts_thinking_missing_in_message():
    """message ohne thinking → thinking leer, kein Crash."""
    chunk = {"message": {"content": "Hello"}}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == "Hello"
    assert thinking == ""
    assert error is None


@pytest.mark.failure_mode
def test_extract_chunk_parts_error_takes_precedence_over_message():
    """Chunk mit error und message → error hat Vorrang."""
    chunk = {"error": "fail", "message": {"content": "x", "thinking": "y"}}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == ""
    assert error == "fail"


@pytest.mark.failure_mode
def test_extract_chunk_parts_empty_dict():
    """Leeres Chunk-Dict → leere Rückgabe."""
    content, thinking, error = _extract_chunk_parts({})
    _assert_safe_return(content, thinking, error)
    assert content == ""
    assert thinking == ""
    assert error is None
