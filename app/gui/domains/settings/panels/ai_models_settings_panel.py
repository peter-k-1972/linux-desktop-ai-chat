"""
AIModelsSettingsPanel – Modell, Temperatur, Tokens, Think-Mode für Settings-Kategorie.

Hauptpfad (Slice 4): skalare Felder → Presenter → SettingsOperationsPort → Adapter.
Hauptpfad (Slice 4b): Modell-Combo → CatalogPresenter → AiModelCatalogPort → Catalog-Adapter
(mit ``UiCoroutineScheduler`` für asyncio/QTimer am GUI-Rand).

Legacy: ohne ``settings_port`` / ``catalog_port``: ``ServiceSettingsAdapter`` + ``ServiceAiModelCatalogAdapter`` (kein ``get_infrastructure`` / kein direkter Catalog-Service im Widget).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QFormLayout,
    QCheckBox,
)
from PySide6.QtCore import Qt, QTimer

from app.gui.domains.settings.settings_ai_model_catalog_sink import SettingsAiModelCatalogSink
from app.gui.domains.settings.settings_ai_models_sink import SettingsAiModelsSink
from app.ui_application.presenters.settings_ai_model_catalog_presenter import (
    SettingsAiModelCatalogPresenter,
)
from app.ui_application.presenters.settings_ai_models_presenter import SettingsAiModelsPresenter
from app.ui_contracts.workspaces.settings_ai_models import AiModelsScalarWritePatch
from app.ui_contracts.workspaces.settings_ai_model_catalog import (
    LoadAiModelCatalogCommand,
    PersistAiModelSelectionCommand,
)
from app.ui_contracts.workspaces.settings_ai_models import (
    LoadAiModelsScalarSettingsCommand,
    SetAiModelsChatStreamingEnabledCommand,
    SetAiModelsMaxTokensCommand,
    SetAiModelsTemperatureCommand,
    SetAiModelsThinkModeCommand,
)

if TYPE_CHECKING:
    from app.ui_application.ports.ai_model_catalog_port import AiModelCatalogPort
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort

logger = logging.getLogger(__name__)


class AIModelsSettingsPanel(QFrame):
    """Panel für AI/Models-Einstellungen in Settings → AI Models."""

    def __init__(
        self,
        parent=None,
        *,
        settings_port: SettingsOperationsPort | None = None,
        catalog_port: AiModelCatalogPort | None = None,
    ):
        self._settings_port = settings_port
        self._catalog_port = catalog_port
        self._sink: SettingsAiModelsSink | None = None
        self._presenter: SettingsAiModelsPresenter | None = None
        self._catalog_sink: SettingsAiModelCatalogSink | None = None
        self._catalog_presenter: SettingsAiModelCatalogPresenter | None = None
        super().__init__(parent)
        self.setObjectName("aiModelsSettingsPanel")
        self._setup_ui()
        self._connect_signals()
        if settings_port is not None:
            self._sink = SettingsAiModelsSink(
                self.temp_spin,
                self.tokens_spin,
                self.think_mode_combo,
                self.stream_check,
                self._error_label,
            )
            self._presenter = SettingsAiModelsPresenter(self._sink, settings_port)
            self._presenter.handle_command(LoadAiModelsScalarSettingsCommand())
        else:
            self._load_scalar_from_settings_legacy()
        if self._settings_port is not None and self._catalog_port is not None:
            self._catalog_sink = SettingsAiModelCatalogSink(self.model_combo)
            self._catalog_presenter = SettingsAiModelCatalogPresenter(
                self._catalog_sink,
                self._catalog_port,
                self,
            )
        QTimer.singleShot(0, self._defer_load_models)

    def schedule(self, coroutine_factory: Callable[[], Awaitable[None]]) -> None:
        """:class:`UiCoroutineScheduler` — Coroutine im laufenden Loop starten oder später erneut."""
        async def _wrap() -> None:
            await coroutine_factory()

        try:
            asyncio.get_running_loop()
            asyncio.create_task(_wrap())
        except RuntimeError:
            QTimer.singleShot(100, lambda: self.schedule(coroutine_factory))

    def _use_port_path(self) -> bool:
        return self._settings_port is not None and self._presenter is not None

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

        self._error_label = QLabel("")
        self._error_label.setObjectName("aiModelsSettingsError")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        layout.addStretch()

    def _connect_signals(self) -> None:
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        self.temp_spin.valueChanged.connect(self._on_temp_changed)
        self.tokens_spin.valueChanged.connect(self._on_tokens_changed)
        self.think_mode_combo.currentTextChanged.connect(self._on_think_mode_changed)
        self.stream_check.stateChanged.connect(self._on_stream_changed)

    @staticmethod
    def _legacy_settings_adapter():
        from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter

        return ServiceSettingsAdapter()

    def _load_scalar_from_settings_legacy(self) -> None:
        try:
            state = self._legacy_settings_adapter().load_ai_models_scalar_state()
            sink = SettingsAiModelsSink(
                self.temp_spin,
                self.tokens_spin,
                self.think_mode_combo,
                self.stream_check,
                self._error_label,
            )
            sink.apply_full_state(state)
        except Exception:
            pass

    def _defer_load_models(self) -> None:
        if self._catalog_presenter is not None:
            self._catalog_presenter.handle_command(LoadAiModelCatalogCommand())
            return
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._load_models_legacy())
        except RuntimeError:
            QTimer.singleShot(100, self._defer_load_models)

    async def _load_models_legacy(self) -> None:
        try:
            from app.ui_application.adapters.service_ai_model_catalog_adapter import (
                ServiceAiModelCatalogAdapter,
            )

            from app.gui.domains.settings.settings_ai_model_catalog_sink import SettingsAiModelCatalogSink

            adapter = ServiceAiModelCatalogAdapter()
            outcome = await adapter.load_chat_selectable_catalog_for_settings()
            catalog_state = SettingsAiModelCatalogPresenter._outcome_to_state(outcome)
            SettingsAiModelCatalogSink(self.model_combo).apply_full_catalog_state(catalog_state)
        except Exception as e:
            logger.warning("Modellkatalog laden fehlgeschlagen: %s", e, exc_info=True)
            self.model_combo.blockSignals(True)
            try:
                self.model_combo.clear()
                hint = "(Keine Modelle – Ollama starten?)"
                if "no such table" in str(e).lower():
                    hint = "(Datenbank-Schema fehlt – Migration ausführen)"
                self.model_combo.addItem(hint, "")
            finally:
                self.model_combo.blockSignals(False)

    def _on_model_changed(self) -> None:
        from app.gui.common.model_catalog_combo import combo_current_selection_id

        model_id = combo_current_selection_id(self.model_combo)
        if not model_id:
            model_id = self.model_combo.currentData(Qt.ItemDataRole.UserRole)
        if not model_id:
            return
        if self._catalog_presenter is not None:
            self._catalog_presenter.handle_command(PersistAiModelSelectionCommand(str(model_id)))
            return
        try:
            from app.ui_application.adapters.service_ai_model_catalog_adapter import (
                ServiceAiModelCatalogAdapter,
            )

            ServiceAiModelCatalogAdapter().persist_default_chat_model_id(str(model_id))
        except Exception:
            pass

    def _on_temp_changed(self, v: float) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetAiModelsTemperatureCommand(v))
            return
        try:
            self._legacy_settings_adapter().persist_ai_models_scalar(AiModelsScalarWritePatch(temperature=v))
        except Exception:
            pass

    def _on_tokens_changed(self, v: int) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetAiModelsMaxTokensCommand(v))
            return
        try:
            self._legacy_settings_adapter().persist_ai_models_scalar(AiModelsScalarWritePatch(max_tokens=v))
        except Exception:
            pass

    def _on_think_mode_changed(self, v: str) -> None:
        if v:
            if self._use_port_path():
                assert self._presenter is not None
                self._presenter.handle_command(SetAiModelsThinkModeCommand(v))
                return
            try:
                self._legacy_settings_adapter().persist_ai_models_scalar(
                    AiModelsScalarWritePatch(think_mode=v)
                )
            except Exception:
                pass

    def _on_stream_changed(self, _) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(
                SetAiModelsChatStreamingEnabledCommand(self.stream_check.isChecked()),
            )
            return
        try:
            self._legacy_settings_adapter().persist_ai_models_scalar(
                AiModelsScalarWritePatch(chat_streaming_enabled=self.stream_check.isChecked())
            )
        except Exception:
            pass
