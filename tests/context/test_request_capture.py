"""
QA coverage for request capture safety.

No UI integration. No persistence. Tests capture behavior in isolation.
"""

import pytest

from app.context.devtools.request_capture import (
    ALLOWED_KEYS,
    FORBIDDEN_KEYS,
    MAX_MESSAGE_CHARS,
    capture,
    clear_capture,
    get_last_request,
)


@pytest.fixture(autouse=True)
def clear_before_after():
    """Ensure clean state before and after each test."""
    clear_capture()
    yield
    clear_capture()


@pytest.fixture(autouse=True)
def enable_context_debug(monkeypatch):
    """Enable context debug for capture tests (tooling tests verify disabled separately)."""
    monkeypatch.setenv("CONTEXT_DEBUG_ENABLED", "1")


def test_request_stored_after_execution():
    """Request is stored after capture() and retrievable via get_last_request()."""
    messages = [{"role": "user", "content": "Hello"}]
    capture(
        chat_id=1,
        messages=messages,
        project_id=42,
        request_context_hint="low_context_query",
        context_policy="architecture",
    )

    last = get_last_request()
    assert last is not None
    assert last["chat_id"] == 1
    assert last["project_id"] == 42
    assert last["message"] == "Hello"
    assert last["request_context_hint"] == "low_context_query"
    assert last["context_policy"] == "architecture"


def test_message_truncated_deterministically():
    """Message longer than MAX_MESSAGE_CHARS is truncated to exactly MAX_MESSAGE_CHARS."""
    long_message = "x" * (MAX_MESSAGE_CHARS + 100)
    messages = [{"role": "user", "content": long_message}]

    capture(chat_id=1, messages=messages)

    last = get_last_request()
    assert last is not None
    assert len(last["message"]) == MAX_MESSAGE_CHARS
    assert last["message"] == "x" * MAX_MESSAGE_CHARS


def test_no_context_payload_stored():
    """Captured dict contains only request input; no context payload keys."""
    messages = [{"role": "user", "content": "test"}]
    capture(chat_id=1, messages=messages)

    last = get_last_request()
    assert last is not None
    allowed_keys = {"chat_id", "project_id", "message", "request_context_hint", "context_policy"}
    assert set(last.keys()) == allowed_keys
    assert "context_payload" not in last
    assert "resolved_context" not in last
    assert "fragment" not in last


def test_no_provider_output_stored():
    """Captured dict has no provider output keys."""
    messages = [{"role": "user", "content": "test"}]
    capture(chat_id=1, messages=messages)

    last = get_last_request()
    assert last is not None
    assert "response" not in last
    assert "chunk" not in last
    assert "provider_output" not in last
    assert "stream" not in last


def test_get_last_request_returns_none_if_no_request_executed():
    """get_last_request() returns None when no capture has run."""
    clear_capture()
    assert get_last_request() is None


def test_captured_data_contains_no_forbidden_fields():
    """Captured data must not contain any forbidden keys; zero sensitive leakage."""
    messages = [{"role": "user", "content": "test"}]
    capture(chat_id=1, messages=messages, project_id=42)

    last = get_last_request()
    assert last is not None
    captured_keys = set(last.keys())
    forbidden_in_result = captured_keys & FORBIDDEN_KEYS
    assert not forbidden_in_result, (
        f"Captured data must not contain forbidden keys: {forbidden_in_result}. "
        "Blocked: context payload, resolved context, provider responses."
    )
    assert captured_keys <= ALLOWED_KEYS, (
        f"Captured data contains unexpected keys: {captured_keys - ALLOWED_KEYS}"
    )


def test_message_truncation_enforced_max_500():
    """Message is always <= MAX_MESSAGE_CHARS (500); no leakage via long content."""
    long_message = "sensitive" * 100  # 900 chars
    messages = [{"role": "user", "content": long_message}]
    capture(chat_id=1, messages=messages)

    last = get_last_request()
    assert last is not None
    assert len(last["message"]) <= MAX_MESSAGE_CHARS
    assert last["message"] == ("sensitive" * 100)[:MAX_MESSAGE_CHARS]
