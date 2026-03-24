"""SettingsDialog — Ollama-Key-Validierungs-Sink (reines UI-Mirroring)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from app.gui.domains.settings.settings_dialog import _OllamaApiKeyValidationSink
from app.ui_contracts.workspaces.settings_modal_ollama import OllamaCloudApiKeyValidationResult


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_sink_applies_valid_result(qapp: QApplication) -> None:
    label = QLabel()
    btn = QPushButton()
    btn.setEnabled(False)
    sink = _OllamaApiKeyValidationSink(label, btn)
    sink.apply_ollama_cloud_api_key_validation(
        OllamaCloudApiKeyValidationResult(kind="valid", message="✓ ok"),
    )
    assert "✓" in label.text()
    assert btn.isEnabled()
