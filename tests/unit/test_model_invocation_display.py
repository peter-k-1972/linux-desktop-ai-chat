"""Tests für model_invocation_display (ohne Qt)."""

import pytest

from app.services.model_chat_runtime import (
    ERROR_KIND_CONFIG_ERROR,
    ERROR_KIND_POLICY_BLOCK,
    ERROR_KIND_PROVIDER_ERROR,
)
from app.services.model_invocation_display import (
    build_chat_invocation_view,
    error_kind_from_chunk,
    merge_model_invocation_payload,
)

pytestmark = pytest.mark.model_usage_gate


def test_merge_invocation_updates():
    acc = None
    acc = merge_model_invocation_payload(acc, {"model_invocation": {"a": 1}})
    acc = merge_model_invocation_payload(acc, {"model_invocation": {"b": 2, "a": 2}})
    assert acc == {"a": 2, "b": 2}


def test_error_kind_from_chunk():
    assert error_kind_from_chunk({"error_kind": "x"}) == "x"
    assert error_kind_from_chunk({}) is None


def test_build_view_policy_block():
    v = build_chat_invocation_view(
        {"outcome": "policy_block", "preflight_message": "total: limit"},
        last_error_text="Anfrage blockiert",
        last_error_kind=ERROR_KIND_POLICY_BLOCK,
        completion_status_db="error",
        model_name="m",
    )
    assert v["style_hint"] == "block"
    assert "Limit" in v["title"] or "block" in v["title"].lower()


def test_build_view_warn():
    v = build_chat_invocation_view(
        {"preflight_decision": "allow_with_warning", "preflight_message": "80%"},
        last_error_text=None,
        last_error_kind=None,
        completion_status_db="complete",
        model_name="m",
    )
    assert v["style_hint"] == "warn"


def test_build_view_provider_error():
    v = build_chat_invocation_view(
        None,
        last_error_text="boom",
        last_error_kind=ERROR_KIND_PROVIDER_ERROR,
        completion_status_db="error",
        model_name="m",
    )
    assert v["style_hint"] == "error"


def test_build_view_config():
    v = build_chat_invocation_view(
        {"outcome": "config_error"},
        last_error_text="key",
        last_error_kind=ERROR_KIND_CONFIG_ERROR,
        completion_status_db="error",
        model_name="m",
    )
    assert v["style_hint"] == "error"
    assert "Konfiguration" in v["title"]
