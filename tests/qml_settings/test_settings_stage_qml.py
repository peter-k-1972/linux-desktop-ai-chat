"""QQmlComponent smoke: SettingsStage + settingsStudio."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend


class _SettingsLedgerPortStub:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def get_settings(self) -> AppSettings:
        return self._settings

    def reload_settings(self) -> None:
        self._settings.load()


@pytest.fixture
def qml_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "qml"
    assert root.is_dir()
    return root


def test_settings_stage_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.settings.settings_viewmodel import SettingsViewModel

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    backend = InMemoryBackend()
    vm = SettingsViewModel(port=_SettingsLedgerPortStub(AppSettings(backend)))
    eng.rootContext().setContextProperty("settingsStudio", vm)
    path = qml_root / "domains" / "settings" / "SettingsStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()


def test_settings_viewmodel_update_and_save_roundtrip(qapplication) -> None:
    from python_bridge.settings.settings_viewmodel import SettingsViewModel

    backend = InMemoryBackend()
    settings = AppSettings(backend)
    vm = SettingsViewModel(port=_SettingsLedgerPortStub(settings))
    assert not vm.dirty
    vm.updateSetting("temperature", "0.5")
    assert vm.dirty
    vm.saveSettings()
    assert not vm.dirty
    s = AppSettings(backend)
    assert s.temperature == 0.5
