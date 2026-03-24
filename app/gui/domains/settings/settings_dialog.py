"""
SettingsDialog – Modal-Dialog für Einstellungen (Legacy MainWindow).

Kanonisch unter app.gui.domains.settings.
Provider- und Katalog-Zugriff über injizierbare Ports/Adapter (Standard: Service-Adapter).
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, QTimer

from app.core.config.settings import AppSettings
from app.gui.shared.layout_constants import (
    WIDGET_SPACING,
    apply_dialog_button_bar_layout,
    apply_dialog_scroll_content_layout,
    apply_form_layout_policy,
)
from app.gui.domains.settings.settings_ai_model_catalog_sink import SettingsAiModelCatalogSink
from app.gui.theme.design_metrics import (
    DIALOG_FOOTER_TOP_GAP_PX,
    WIDE_LINE_EDIT_MIN_WIDTH_PX,
)
from app.ui_application.presenters.settings_legacy_modal_presenter import SettingsLegacyModalPresenter
from app.ui_contracts.workspaces.settings_modal_ollama import OllamaCloudApiKeyValidationResult

if TYPE_CHECKING:
    from app.ui_application.ports.ai_model_catalog_port import AiModelCatalogPort
    from app.ui_application.ports.ollama_provider_settings_port import OllamaProviderSettingsPort
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class _OllamaApiKeyValidationSink:
    """Sink: Prüfergebnis → Status-Label + Button (POST-CORRECTION: keine Port-Aufrufe im Widget)."""

    _STYLES = {
        "valid": "color: green; font-size: 11px;",
        "invalid": "color: #c44; font-size: 11px;",
        "error": "color: #c44; font-size: 11px;",
    }

    def __init__(self, status_label: QLabel, check_button: QPushButton) -> None:
        self._status_label = status_label
        self._check_button = check_button

    def apply_ollama_cloud_api_key_validation(self, result: OllamaCloudApiKeyValidationResult) -> None:
        self._status_label.setText(result.message)
        self._status_label.setStyleSheet(self._STYLES.get(result.kind, self._STYLES["error"]))
        self._check_button.setEnabled(True)


class SettingsDialog(QDialog):
    def __init__(
        self,
        settings: AppSettings,
        orchestrator=None,
        parent=None,
        *,
        ollama_provider_port: OllamaProviderSettingsPort | None = None,
        catalog_port: AiModelCatalogPort | None = None,
        settings_operations_port: SettingsOperationsPort | None = None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.orchestrator = orchestrator
        if ollama_provider_port is None:
            from app.ui_application.adapters.service_ollama_provider_settings_adapter import (
                ServiceOllamaProviderSettingsAdapter,
            )

            ollama_provider_port = ServiceOllamaProviderSettingsAdapter()
        if catalog_port is None:
            from app.ui_application.adapters.service_ai_model_catalog_adapter import (
                ServiceAiModelCatalogAdapter,
            )

            catalog_port = ServiceAiModelCatalogAdapter()
        if settings_operations_port is None:
            from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter

            settings_operations_port = ServiceSettingsAdapter()
        self._ollama_provider_port = ollama_provider_port
        self._catalog_port = catalog_port
        self._settings_operations_port = settings_operations_port
        self.setWindowTitle("Einstellungen")
        self.setMinimumWidth(420)
        self.setMinimumHeight(400)
        self.init_ui()
        self._legacy_modal_presenter = SettingsLegacyModalPresenter(
            settings_operations_port,
            catalog_port,
            SettingsAiModelCatalogSink(self.model_combo),
            ollama_provider_port,
        )
        self.load_settings_to_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, DIALOG_FOOTER_TOP_GAP_PX)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("settingsDialogContent")
        layout = QVBoxLayout(content)
        apply_dialog_scroll_content_layout(layout)
        form = QFormLayout()
        apply_form_layout_policy(form)

        self.model_combo = QComboBox()
        form.addRow("Modell:", self.model_combo)

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 1.0)
        self.temp_spin.setSingleStep(0.1)
        form.addRow("Temperatur:", self.temp_spin)

        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(0, 32768)
        self.tokens_spin.setToolTip(
            "Max. Tokens pro Antwort. Bei Thinking-Modellen (z.B. GPT-OSS) zählen "
            "Thinking-Tokens mit – höhere Werte (4096+) empfehlenswert."
        )
        form.addRow("Max Tokens:", self.tokens_spin)

        # Thinking-Mode für Modelle (steuert das 'think'-Flag im Ollama-Payload)
        self.think_mode_combo = QComboBox()
        self.think_mode_combo.addItems(["auto", "off", "low", "medium", "high"])
        form.addRow("Thinking-Modus:", self.think_mode_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        form.addRow("UI Theme:", self.theme_combo)

        # Modell-Router
        self.auto_routing_check = QCheckBox("Automatische Modellauswahl")
        self.auto_routing_check.setToolTip("Modell nach Prompt-Inhalt wählen (Code, Denken, etc.)")
        form.addRow("", self.auto_routing_check)

        self.cloud_escalation_check = QCheckBox("Cloud-Eskalation erlauben")
        self.cloud_escalation_check.setToolTip("Overkill/Cloud-Modelle nutzen (API-Key in Einstellungen oder .env)")
        form.addRow("", self.cloud_escalation_check)

        self.cloud_via_local_check = QCheckBox("Cloud über lokales Ollama (ollama signin)")
        self.cloud_via_local_check.setToolTip(
            "Alternative zum API-Key: Cloud-Modelle über localhost.\n"
            "Voraussetzung: 1) ollama signin  2) ollama pull <modell>:cloud (z.B. ollama pull glm-5:cloud)"
        )
        form.addRow("", self.cloud_via_local_check)

        self.overkill_check = QCheckBox("Overkill-Modus (Standard)")
        self.overkill_check.setToolTip("Standardmäßig stärkstes Modell verwenden")
        form.addRow("", self.overkill_check)

        # RAG
        self.rag_enabled_check = QCheckBox("RAG aktiv (Retrieval Augmented Generation)")
        self.rag_enabled_check.setToolTip(
            "Kontext aus indexierten Dokumenten nutzen. "
            "Dokumente mit: python scripts/index_rag.py --space <name> <pfad>"
        )
        form.addRow("", self.rag_enabled_check)
        self.rag_space_combo = QComboBox()
        self.rag_space_combo.addItems(["default", "documentation", "code", "notes", "projects"])
        self.rag_space_combo.setToolTip("Knowledge Space für die Suche")
        form.addRow("RAG Space:", self.rag_space_combo)
        self.rag_top_k_spin = QSpinBox()
        self.rag_top_k_spin.setRange(1, 20)
        self.rag_top_k_spin.setValue(5)
        self.rag_top_k_spin.setToolTip("Anzahl der Chunks pro Abfrage")
        form.addRow("RAG Top-K:", self.rag_top_k_spin)
        self.self_improving_check = QCheckBox("Self-Improving Knowledge aktiv")
        self.self_improving_check.setToolTip(
            "Wissen aus LLM-Antworten extrahieren und automatisch in den Knowledge Store aufnehmen"
        )
        form.addRow("", self.self_improving_check)

        self.debug_panel_check = QCheckBox("Agent Debug Tab aktiv")
        self.debug_panel_check.setToolTip(
            "Debug-Tab im Side-Panel (nach Modelle und Prompts) anzeigen. Ermöglicht Einblick in Agenten-Aktivität, Tasks und Modellnutzung."
        )
        form.addRow("", self.debug_panel_check)

        layout.addLayout(form)

        # Ollama Cloud API-Key
        api_key_group = QGroupBox("Ollama Cloud API-Key")
        api_key_group.setToolTip(
            "Für direkten Zugriff auf ollama.com. Alternative: „Cloud über lokales Ollama“ aktivieren "
            "und „ollama signin“ im Terminal ausführen – dann kein API-Key nötig."
        )
        api_key_layout = QFormLayout()
        apply_form_layout_policy(api_key_layout)
        key_row = QHBoxLayout()
        key_row.setSpacing(WIDGET_SPACING)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("API-Key von ollama.com/settings/keys")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setMinimumWidth(WIDE_LINE_EDIT_MIN_WIDTH_PX)
        key_row.addWidget(self.api_key_edit)
        self.api_key_from_env_btn = QPushButton("Aus .env")
        self.api_key_from_env_btn.setToolTip("Key aus .env laden (OLLAMA_API_KEY)")
        self.api_key_from_env_btn.clicked.connect(self._on_load_key_from_env)
        key_row.addWidget(self.api_key_from_env_btn)
        api_key_layout.addRow("API-Key:", key_row)

        status_row = QHBoxLayout()
        status_row.setSpacing(WIDGET_SPACING)
        self.api_key_status_label = QLabel("—")
        self.api_key_status_label.setStyleSheet("color: gray; font-size: 11px;")
        status_row.addWidget(self.api_key_status_label)
        status_row.addStretch()
        self.api_key_check_btn = QPushButton("Status prüfen")
        self.api_key_check_btn.setToolTip("Prüft, ob der API-Key gültig ist")
        self.api_key_check_btn.clicked.connect(self._on_check_api_key_status)
        status_row.addWidget(self.api_key_check_btn)
        api_key_layout.addRow("", status_row)
        api_key_group.setLayout(api_key_layout)
        layout.addWidget(api_key_group)

        # Prompt-Speicherung
        prompt_group = QGroupBox("Prompt-Speicherung")
        prompt_layout = QFormLayout()
        apply_form_layout_policy(prompt_layout)
        self.prompt_storage_combo = QComboBox()
        self.prompt_storage_combo.addItems(["Datenbank", "Verzeichnis"])
        self.prompt_storage_combo.setToolTip("Datenbank: SQLite. Verzeichnis: JSON-Dateien in einem Ordner.")
        prompt_layout.addRow("Speicherart:", self.prompt_storage_combo)

        dir_row = QHBoxLayout()
        dir_row.setSpacing(WIDGET_SPACING)
        self.prompt_directory_edit = QLineEdit()
        self.prompt_directory_edit.setPlaceholderText("Pfad zum Prompt-Verzeichnis")
        dir_row.addWidget(self.prompt_directory_edit)
        self.prompt_dir_btn = QPushButton("…")
        self.prompt_dir_btn.setFixedWidth(36)
        self.prompt_dir_btn.setToolTip("Ordner auswählen")
        self.prompt_dir_btn.clicked.connect(self._on_browse_prompt_directory)
        dir_row.addWidget(self.prompt_dir_btn)
        prompt_layout.addRow("Prompt-Verzeichnis:", dir_row)

        self.prompt_confirm_delete_check = QCheckBox("Vor Löschen bestätigen")
        self.prompt_confirm_delete_check.setToolTip("Bestätigungsdialog vor dem Löschen eines Prompts")
        prompt_layout.addRow("", self.prompt_confirm_delete_check)
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        apply_dialog_button_bar_layout(btn_layout)
        self.save_btn = QPushButton("Speichern")
        self.save_btn.setObjectName("settingsSaveBtn")
        self.save_btn.clicked.connect(self.save_and_close)
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)

    def _on_load_key_from_env(self):
        key = self._ollama_provider_port.get_ollama_api_key_from_env()
        if key:
            self.api_key_edit.setText(key)
            self._update_api_key_status_label(key)
        else:
            self.api_key_status_label.setText("Kein Key in .env")

    def _update_api_key_status_label(self, key: str):
        if not key:
            self.api_key_status_label.setText("Kein Key gesetzt")
        else:
            self.api_key_status_label.setText("Key gesetzt")

    def _on_check_api_key_status(self):
        key = self.api_key_edit.text().strip()
        if not key:
            self.api_key_status_label.setText("Bitte Key eingeben")
            return
        self.api_key_check_btn.setEnabled(False)
        self.api_key_status_label.setText("Prüfe…")

        async def _run_validate() -> None:
            sink = _OllamaApiKeyValidationSink(self.api_key_status_label, self.api_key_check_btn)
            await self._legacy_modal_presenter.validate_ollama_cloud_api_key(key, validation_sink=sink)

        def _defer_check() -> None:
            try:
                asyncio.get_running_loop()
                asyncio.create_task(_run_validate())
            except RuntimeError:
                QTimer.singleShot(100, _defer_check)

        _defer_check()

    def _on_browse_prompt_directory(self):
        current = self.prompt_directory_edit.text().strip()
        path = QFileDialog.getExistingDirectory(
            self,
            "Prompt-Verzeichnis wählen",
            current or ".",
        )
        if path:
            self.prompt_directory_edit.setText(path)

    def load_settings_to_ui(self):
        self.temp_spin.setValue(self.settings.temperature)
        self.tokens_spin.setValue(self.settings.max_tokens)
        index = self.theme_combo.findText(self.settings.theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        self.auto_routing_check.setChecked(getattr(self.settings, "auto_routing", True))
        self.cloud_escalation_check.setChecked(getattr(self.settings, "cloud_escalation", False))
        self.cloud_via_local_check.setChecked(getattr(self.settings, "cloud_via_local", False))
        self.overkill_check.setChecked(getattr(self.settings, "overkill_mode", False))
        self.rag_enabled_check.setChecked(getattr(self.settings, "rag_enabled", False))
        self.rag_space_combo.setCurrentText(getattr(self.settings, "rag_space", "default"))
        self.rag_top_k_spin.setValue(getattr(self.settings, "rag_top_k", 5))
        self.self_improving_check.setChecked(getattr(self.settings, "self_improving_enabled", False))
        self.debug_panel_check.setChecked(getattr(self.settings, "debug_panel_enabled", True))

        # Prompt-Speicherung
        storage = getattr(self.settings, "prompt_storage_type", "database")
        self.prompt_storage_combo.setCurrentIndex(1 if storage == "directory" else 0)
        self.prompt_directory_edit.setText(getattr(self.settings, "prompt_directory", "") or "")
        self.prompt_confirm_delete_check.setChecked(getattr(self.settings, "prompt_confirm_delete", True))

        # API-Key (maskiert im Passwortfeld)
        api_key = getattr(self.settings, "ollama_api_key", "") or ""
        self.api_key_edit.setText(api_key)
        self._update_api_key_status_label(api_key)
        self.api_key_status_label.setStyleSheet("color: gray; font-size: 11px;")

        # Thinking-Mode setzen
        think_index = self.think_mode_combo.findText(self.settings.think_mode)
        if think_index < 0:
            think_index = self.think_mode_combo.findText("auto")
        if think_index >= 0:
            self.think_mode_combo.setCurrentIndex(think_index)

        # Modelle asynchron laden (Loop wie bei AIModelsSettingsPanel erst nach App-Start)
        QTimer.singleShot(0, self._defer_update_models)

    def _defer_update_models(self) -> None:
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self.update_models())
        except RuntimeError:
            QTimer.singleShot(100, self._defer_update_models)

    async def update_models(self):
        await self._legacy_modal_presenter.refresh_model_catalog(self.settings.model)

    def save_and_close(self):
        uid = self.model_combo.currentData(Qt.ItemDataRole.UserRole)
        model_resolved = uid if uid else self.model_combo.currentText()
        model_id_str = str(model_resolved) if model_resolved is not None else ""
        self._legacy_modal_presenter.persist_from_ui(
            self.settings,
            model_id_str=model_id_str,
            temperature=self.temp_spin.value(),
            max_tokens=self.tokens_spin.value(),
            legacy_theme_text=self.theme_combo.currentText(),
            think_mode=self.think_mode_combo.currentText(),
            auto_routing=self.auto_routing_check.isChecked(),
            cloud_escalation=self.cloud_escalation_check.isChecked(),
            cloud_via_local=self.cloud_via_local_check.isChecked(),
            overkill_mode=self.overkill_check.isChecked(),
            rag_enabled=self.rag_enabled_check.isChecked(),
            rag_space=self.rag_space_combo.currentText(),
            rag_top_k=self.rag_top_k_spin.value(),
            self_improving_enabled=self.self_improving_check.isChecked(),
            debug_panel_enabled=self.debug_panel_check.isChecked(),
            prompt_storage_is_directory=self.prompt_storage_combo.currentIndex() == 1,
            prompt_directory=self.prompt_directory_edit.text().strip(),
            prompt_confirm_delete=self.prompt_confirm_delete_check.isChecked(),
            ollama_api_key=(self.api_key_edit.text() or "").strip(),
        )

        if self.orchestrator and hasattr(self.orchestrator, "_cloud"):
            key = (self.settings.ollama_api_key or "").strip() or None
            self.orchestrator._cloud.set_api_key(key)

        self.accept()
