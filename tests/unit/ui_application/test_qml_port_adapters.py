"""Smoke: QML-Ports delegieren an die erwarteten Service-Fassaden (mit Monkeypatch)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.prompts.prompt_models import Prompt
from app.ui_application.adapters.service_qml_prompt_shelf_adapter import ServiceQmlPromptShelfAdapter


def test_prompt_shelf_adapter_delegates_list(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_svc = MagicMock()
    mock_svc.list_all.return_value = []

    def fake_get():
        return mock_svc

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", fake_get)
    ad = ServiceQmlPromptShelfAdapter()
    assert ad.list_prompts("x") == []
    mock_svc.list_all.assert_called_once_with(filter_text="x")


def test_prompt_shelf_adapter_delegates_get(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_svc = MagicMock()
    p = Prompt.empty()
    mock_svc.get.return_value = p

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: mock_svc)
    ad = ServiceQmlPromptShelfAdapter()
    assert ad.get_prompt(3) is p
    mock_svc.get.assert_called_once_with(3)
