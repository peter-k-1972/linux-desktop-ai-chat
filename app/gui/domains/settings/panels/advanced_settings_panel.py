"""
AdvancedSettingsPanel – Debug, experimentelle Optionen für Settings-Kategorie.

Bindet an AppSettings über get_infrastructure().settings.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QFormLayout,
    QLabel,
    QCheckBox,
    QVBoxLayout,
)


class AdvancedSettingsPanel(QFrame):
    """Panel für Advanced-Einstellungen: Debug-Panel, experimentell."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("advancedSettingsPanel")
        self._setup_ui()
        self._connect_signals()
        self._load_from_settings()

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
        layout.addStretch()

    def _connect_signals(self) -> None:
        self.debug_panel_check.stateChanged.connect(self._on_debug_panel_changed)
        self.context_debug_check.stateChanged.connect(self._on_context_debug_changed)
        self.context_mode_combo.currentTextChanged.connect(self._on_context_mode_changed)

    def _get_settings(self):
        from app.services.infrastructure import get_infrastructure
        return get_infrastructure().settings

    def _load_from_settings(self) -> None:
        try:
            s = self._get_settings()
            self.debug_panel_check.setChecked(getattr(s, "debug_panel_enabled", True))
            self.context_debug_check.setChecked(getattr(s, "context_debug_enabled", False))
            mode = getattr(s, "chat_context_mode", "semantic")
            idx = self.context_mode_combo.findText(mode)
            if idx >= 0:
                self.context_mode_combo.setCurrentIndex(idx)
            else:
                self.context_mode_combo.setCurrentText("semantic")
        except Exception:
            pass

    def _on_debug_panel_changed(self) -> None:
        try:
            s = self._get_settings()
            s.debug_panel_enabled = self.debug_panel_check.isChecked()
            s.save()
        except Exception:
            pass

    def _on_context_debug_changed(self) -> None:
        try:
            s = self._get_settings()
            s.context_debug_enabled = self.context_debug_check.isChecked()
            s.save()
        except Exception:
            pass

    def _on_context_mode_changed(self, value: str) -> None:
        try:
            s = self._get_settings()
            if value in ("off", "neutral", "semantic"):
                s.chat_context_mode = value
                s.save()
        except Exception:
            pass
