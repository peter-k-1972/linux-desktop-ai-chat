"""
AIModelsSettingsPanel – Modell, Temperatur, Tokens, Think-Mode für Settings-Kategorie.

Bindet an AppSettings über get_infrastructure().settings.
Asynchrones Laden der Modellliste über ModelService.
"""

import asyncio
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QFormLayout,
    QCheckBox,
)
from PySide6.QtCore import Qt, QTimer


class AIModelsSettingsPanel(QFrame):
    """Kompaktes Panel für AI/Models-Einstellungen in Settings → AI Models."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("aiModelsSettingsPanel")
        self._setup_ui()
        self._connect_signals()
        self._load_from_settings()
        QTimer.singleShot(0, self._defer_load_models)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        title = QLabel("AI / Models")
        title.setObjectName("settingsPanelTitle")
        layout.addWidget(title)

        desc = QLabel(
            "Standardmodell, Temperatur und Token-Limits. Änderungen werden automatisch gespeichert."
        )
        desc.setObjectName("settingsPanelDescription")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        form = QFormLayout()
        form.setSpacing(12)

        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(220)
        self.model_combo.setToolTip("Standardmodell für Chat und Completion")
        form.addRow("Standardmodell:", self.model_combo)

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setToolTip("Kreativität (0 = deterministisch, 1+ = kreativer)")
        form.addRow("Temperatur:", self.temp_spin)

        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(0, 32768)
        self.tokens_spin.setToolTip(
            "Max. Tokens pro Antwort. Bei Thinking-Modellen zählen Thinking-Tokens mit."
        )
        form.addRow("Max Tokens:", self.tokens_spin)

        self.think_mode_combo = QComboBox()
        self.think_mode_combo.addItems(["auto", "off", "low", "medium", "high"])
        self.think_mode_combo.setToolTip("Thinking-Modus für kompatible Modelle")
        form.addRow("Thinking-Modus:", self.think_mode_combo)

        self.stream_check = QCheckBox("Streaming aktiv")
        self.stream_check.setToolTip(
            "Antworten während der Generierung anzeigen. Deaktivieren bei Darstellungsproblemen."
        )
        form.addRow("", self.stream_check)

        layout.addLayout(form)
        layout.addStretch()

    def _connect_signals(self) -> None:
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        self.temp_spin.valueChanged.connect(self._on_temp_changed)
        self.tokens_spin.valueChanged.connect(self._on_tokens_changed)
        self.think_mode_combo.currentTextChanged.connect(self._on_think_mode_changed)
        self.stream_check.stateChanged.connect(self._on_stream_changed)

    def _get_settings(self):
        from app.services.infrastructure import get_infrastructure
        return get_infrastructure().settings

    def _load_from_settings(self) -> None:
        try:
            s = self._get_settings()
            self.temp_spin.setValue(getattr(s, "temperature", 0.7))
            self.tokens_spin.setValue(getattr(s, "max_tokens", 4096))
            idx = self.think_mode_combo.findText(getattr(s, "think_mode", "auto"))
            if idx >= 0:
                self.think_mode_combo.setCurrentIndex(idx)
            self.stream_check.setChecked(getattr(s, "chat_streaming_enabled", True))
        except Exception:
            pass

    def _defer_load_models(self) -> None:
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._load_models())
        except RuntimeError:
            QTimer.singleShot(100, self._defer_load_models)

    async def _load_models(self) -> None:
        try:
            from app.services.model_service import get_model_service
            result = await get_model_service().get_models_full()
            models = result.data if result.success and result.data else []
            self.model_combo.blockSignals(True)
            self.model_combo.clear()
            for m in models:
                mid = m.get("name", m.get("model", "?"))
                self.model_combo.addItem(mid, mid)
            self.model_combo.blockSignals(False)
            self._sync_model_from_settings()
        except Exception:
            self.model_combo.blockSignals(False)
            self.model_combo.clear()
            self.model_combo.addItem("(Keine Modelle – Ollama starten?)", "")

    def _sync_model_from_settings(self) -> None:
        try:
            s = self._get_settings()
            current = getattr(s, "model", "")
            for i in range(self.model_combo.count()):
                if self.model_combo.itemData(i, Qt.ItemDataRole.UserRole) == current:
                    self.model_combo.setCurrentIndex(i)
                    return
                if self.model_combo.itemText(i) == current:
                    self.model_combo.setCurrentIndex(i)
                    return
        except Exception:
            pass

    def _on_model_changed(self) -> None:
        model_id = self.model_combo.currentData(Qt.ItemDataRole.UserRole)
        if model_id:
            try:
                s = self._get_settings()
                s.model = model_id
                s.save()
            except Exception:
                pass

    def _on_temp_changed(self, v: float) -> None:
        try:
            s = self._get_settings()
            s.temperature = v
            s.save()
        except Exception:
            pass

    def _on_tokens_changed(self, v: int) -> None:
        try:
            s = self._get_settings()
            s.max_tokens = v
            s.save()
        except Exception:
            pass

    def _on_think_mode_changed(self, v: str) -> None:
        if v:
            try:
                s = self._get_settings()
                s.think_mode = v
                s.save()
            except Exception:
                pass

    def _on_stream_changed(self, _) -> None:
        try:
            s = self._get_settings()
            s.chat_streaming_enabled = self.stream_check.isChecked()
            s.save()
        except Exception:
            pass
