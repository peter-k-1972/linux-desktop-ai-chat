"""Settings modal Ollama — Contracts (POST-CORRECTION Slice 2)."""

from __future__ import annotations

from dataclasses import asdict

from app.ui_contracts.workspaces.settings_modal_ollama import (
    OllamaCloudApiKeyValidationResult,
    OllamaCloudApiKeyValidateRequested,
)


def test_validate_requested_asdict() -> None:
    r = OllamaCloudApiKeyValidateRequested(api_key="k")
    assert asdict(r)["api_key"] == "k"


def test_validation_result_asdict() -> None:
    r = OllamaCloudApiKeyValidationResult(kind="invalid", message="m")
    d = asdict(r)
    assert d["kind"] == "invalid"
    assert d["message"] == "m"
