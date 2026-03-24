"""
AdvancedSettingsPanel – Debug, experimentelle Optionen für Settings-Kategorie.

Hauptpfad: Presenter → SettingsOperationsPort → Adapter.
Legacy: ``ServiceSettingsAdapter`` für Lese-/Schreibpfad (kein ``get_infrastructure`` im Widget).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
)

from app.gui.domains.settings.settings_advanced_sink import SettingsAdvancedSink
from app.ui_application.presenters.settings_advanced_presenter import SettingsAdvancedPresenter
from app.ui_contracts.workspaces.settings_advanced import (
    AdvancedSettingsWritePatch,
    LoadAdvancedSettingsCommand,
    SetChatContextModeCommand,
    SetContextDebugEnabledCommand,
    SetDebugPanelEnabledCommand,
)

if TYPE_CHECKING:
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class AdvancedSettingsPanel(QFrame):
    """Panel für Advanced-Einstellungen: Debug-Panel, experimentell."""

    def __init__(self, parent=None, *, settings_port: SettingsOperationsPort | None = None):
        self._settings_port = settings_port
        self._sink: SettingsAdvancedSink | None = None
        self._presenter: SettingsAdvancedPresenter | None = None
        super().__init__(parent)
        self.setObjectName("advancedSettingsPanel")
        self._setup_ui()
        self._connect_signals()
        if settings_port is not None:
            self._sink = SettingsAdvancedSink(
                self.debug_panel_check,
                self.context_debug_check,
                self.context_mode_combo,
                self._error_label,
            )
            self._presenter = SettingsAdvancedPresenter(self._sink, settings_port)
            self._presenter.handle_command(LoadAdvancedSettingsCommand())
        else:
            self._load_from_settings_legacy()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        title = QLabel("Advanced")
        title.setObjectName("settingsPanelTitle")
        layout.addWidget(title)

        desc = QLabel(
            "Entwickler- und Debug-Optionen. Änderungen werden automatisch gespeichert."
        )
        desc.setObjectName("settingsPanelDescription")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        form = QFormLayout()
        form.setSpacing(12)

        self.debug_panel_check = QCheckBox("Agent Debug Tab aktiv")
        self.debug_panel_check.setToolTip(
            "Debug-Tab im Side-Panel (nach Modelle und Prompts) anzeigen. "
            "Ermöglicht Einblick in Agenten-Aktivität, Tasks und Modellnutzung."
        )
        form.addRow("", self.debug_panel_check)

        self.context_debug_check = QCheckBox("Kontext-Inspection aktiv")
        self.context_debug_check.setToolTip(
            "Kontext-Inspection (Inspect Last Context, CLI, Request-Capture, Explainability-Logs) aktivieren. "
            "Nur für Entwickler und QA."
        )
        form.addRow("", self.context_debug_check)

        self.context_mode_combo = QComboBox()
        self.context_mode_combo.addItems(["neutral", "semantic", "off"])
        self.context_mode_combo.setToolTip(
            "Kontext-Injektion im Chat: neutral (nüchtern), semantic (angereichert), off (keine Injektion). "
            "Für manuelle Variantentests und Evaluierung."
        )
        form.addRow("Chat-Kontext-Modus:", self.context_mode_combo)

        layout.addLayout(form)

        self._error_label = QLabel("")
        self._error_label.setObjectName("advancedSettingsError")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        layout.addStretch()

    def _use_port_path(self) -> bool:
        return self._settings_port is not None and self._presenter is not None

    def _connect_signals(self) -> None:
        self.debug_panel_check.stateChanged.connect(self._on_debug_panel_changed)
        self.context_debug_check.stateChanged.connect(self._on_context_debug_changed)
        self.context_mode_combo.currentTextChanged.connect(self._on_context_mode_changed)

    @staticmethod
    def _legacy_adapter():
        from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter

        return ServiceSettingsAdapter()

    def _load_from_settings_legacy(self) -> None:
        try:
            from app.gui.domains.settings.settings_advanced_sink import SettingsAdvancedSink

            state = self._legacy_adapter().load_advanced_settings_state()
            sink = SettingsAdvancedSink(
                self.debug_panel_check,
                self.context_debug_check,
                self.context_mode_combo,
                self._error_label,
            )
            sink.apply_full_state(state)
        except Exception:
            pass

    def _on_debug_panel_changed(self, _state: int) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetDebugPanelEnabledCommand(self.debug_panel_check.isChecked()))
            return
        try:
            self._legacy_adapter().persist_advanced_settings(
                AdvancedSettingsWritePatch(debug_panel_enabled=self.debug_panel_check.isChecked())
            )
        except Exception:
            pass

    def _on_context_debug_changed(self, _state: int) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetContextDebugEnabledCommand(self.context_debug_check.isChecked()))
            return
        try:
            self._legacy_adapter().persist_advanced_settings(
                AdvancedSettingsWritePatch(context_debug_enabled=self.context_debug_check.isChecked())
            )
        except Exception:
            pass

    def _on_context_mode_changed(self, value: str) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            if value:
                self._presenter.handle_command(SetChatContextModeCommand(value))
            return
        try:
            if value in ("off", "neutral", "semantic"):
                self._legacy_adapter().persist_advanced_settings(
                    AdvancedSettingsWritePatch(chat_context_mode=value)
                )
        except Exception:
            pass
