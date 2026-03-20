"""
SettingsDialog – Modal-Dialog für Einstellungen (Legacy MainWindow).

Kanonisch unter app.gui.domains.settings.
GUI nutzt ModelService und ProviderService; keine direkten Provider-Imports.
"""

import asyncio
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
    QDoubleSpinBox, QSpinBox, QLabel, QPushButton, QFormLayout, QCheckBox,
    QLineEdit, QFileDialog, QGroupBox, QScrollArea, QWidget,
)
from PySide6.QtCore import Qt

from app.core.config.settings import AppSettings


class SettingsDialog(QDialog):
    def __init__(
        self,
        settings: AppSettings,
        orchestrator=None,
        parent=None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.orchestrator = orchestrator
        self.setWindowTitle("Einstellungen")
        self.setMinimumWidth(420)
        self.setMinimumHeight(400)
        self.init_ui()
        self.load_settings_to_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        form = QFormLayout()
        form.setSpacing(14)

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
        key_row = QHBoxLayout()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("API-Key von ollama.com/settings/keys")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setMinimumWidth(280)
        key_row.addWidget(self.api_key_edit)
        self.api_key_from_env_btn = QPushButton("Aus .env")
        self.api_key_from_env_btn.setToolTip("Key aus .env laden (OLLAMA_API_KEY)")
        self.api_key_from_env_btn.clicked.connect(self._on_load_key_from_env)
        key_row.addWidget(self.api_key_from_env_btn)
        api_key_layout.addRow("API-Key:", key_row)

        status_row = QHBoxLayout()
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
        self.prompt_storage_combo = QComboBox()
        self.prompt_storage_combo.addItems(["Datenbank", "Verzeichnis"])
        self.prompt_storage_combo.setToolTip("Datenbank: SQLite. Verzeichnis: JSON-Dateien in einem Ordner.")
        prompt_layout.addRow("Speicherart:", self.prompt_storage_combo)

        dir_row = QHBoxLayout()
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
        btn_layout.setContentsMargins(24, 0, 24, 0)
        btn_layout.setSpacing(12)
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
        from app.services.provider_service import get_provider_service
        key = get_provider_service().get_ollama_api_key_from_env()
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
        asyncio.create_task(self._check_api_key_async(key))

    async def _check_api_key_async(self, key: str):
        try:
            from app.services.provider_service import get_provider_service
            ok = await get_provider_service().validate_cloud_api_key(key)
            if ok:
                self.api_key_status_label.setText("✓ Key gültig")
                self.api_key_status_label.setStyleSheet("color: green; font-size: 11px;")
            else:
                self.api_key_status_label.setText("✗ Key ungültig oder abgelaufen (401)")
                self.api_key_status_label.setStyleSheet("color: #c44; font-size: 11px;")
        except Exception as e:
            msg = str(e).strip()[:60]
            self.api_key_status_label.setText(f"✗ Fehler: {msg}")
            self.api_key_status_label.setStyleSheet("color: #c44; font-size: 11px;")
        finally:
            self.api_key_check_btn.setEnabled(True)

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

        # Modelle asynchron laden
        asyncio.create_task(self.update_models())

    async def update_models(self):
        from app.services.model_service import get_model_service
        result = await get_model_service().get_models_full()
        models = result.data if result.success and result.data else []
        self.model_combo.clear()
        for m in models:
            mid = m.get("name", m.get("model", "?"))
            self.model_combo.addItem(mid, mid)
        # Cloud-Modelle hinzufügen, falls API-Key vorhanden
        try:
            from app.services.provider_service import get_provider_service
            if get_provider_service().get_ollama_api_key_from_env():
                from app.core.models.registry import get_registry
                for entry in get_registry().list_cloud():
                    self.model_combo.addItem(f"{entry.id} (Cloud)", entry.id)
        except Exception:
            pass
        # Aktuelles Modell auswählen
        current = self.settings.model
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i, Qt.ItemDataRole.UserRole) == current:
                self.model_combo.setCurrentIndex(i)
                break
            if self.model_combo.itemText(i) == current:
                self.model_combo.setCurrentIndex(i)
                break

    def save_and_close(self):
        model_id = self.model_combo.currentData(Qt.ItemDataRole.UserRole)
        self.settings.model = model_id if model_id else self.model_combo.currentText()
        self.settings.temperature = self.temp_spin.value()
        self.settings.max_tokens = self.tokens_spin.value()
        self.settings.theme = self.theme_combo.currentText()
        self.settings.think_mode = self.think_mode_combo.currentText()
        self.settings.auto_routing = self.auto_routing_check.isChecked()
        self.settings.cloud_escalation = self.cloud_escalation_check.isChecked()
        self.settings.cloud_via_local = self.cloud_via_local_check.isChecked()
        self.settings.overkill_mode = self.overkill_check.isChecked()
        self.settings.rag_enabled = self.rag_enabled_check.isChecked()
        self.settings.rag_space = self.rag_space_combo.currentText()
        self.settings.rag_top_k = self.rag_top_k_spin.value()
        self.settings.self_improving_enabled = self.self_improving_check.isChecked()
        self.settings.debug_panel_enabled = self.debug_panel_check.isChecked()
        self.settings.prompt_storage_type = "directory" if self.prompt_storage_combo.currentIndex() == 1 else "database"
        self.settings.prompt_directory = self.prompt_directory_edit.text().strip()
        self.settings.prompt_confirm_delete = self.prompt_confirm_delete_check.isChecked()
        self.settings.ollama_api_key = (self.api_key_edit.text() or "").strip()
        self.settings.save()

        if self.orchestrator and hasattr(self.orchestrator, "_cloud"):
            key = (self.settings.ollama_api_key or "").strip() or None
            self.orchestrator._cloud.set_api_key(key)

        self.accept()
