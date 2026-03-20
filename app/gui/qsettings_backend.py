"""
QSettingsBackendAdapter – Qt-Implementierung von SettingsBackend (core).

Implementiert app.core.config.settings_backend.SettingsBackend.
Wird vom GUI-Bootstrap (run_gui_shell, run_legacy_gui) an init_infrastructure übergeben.
"""

from typing import Any

from PySide6.QtCore import QSettings


class QSettingsBackendAdapter:
    """Adapter: QSettings als SettingsBackend."""

    def __init__(self, org: str = "OllamaChat", app: str = "LinuxDesktopChat") -> None:
        self._qsettings = QSettings(org, app)

    def value(self, key: str, default: Any = None) -> Any:
        return self._qsettings.value(key, default)

    def setValue(self, key: str, value: Any) -> None:
        self._qsettings.setValue(key, value)


def create_qsettings_backend() -> "QSettingsBackendAdapter":
    """Erstellt QSettings-Backend für Produktion."""
    return QSettingsBackendAdapter()
