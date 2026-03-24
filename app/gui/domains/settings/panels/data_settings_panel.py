"""
DataSettingsPanel – RAG, Prompt-Speicherung für Settings-Kategorie.

Hauptpfad: Presenter → SettingsOperationsPort → Adapter.
Legacy: keine Port-Injektion — Lese-/Schreibpfad über ``ServiceSettingsAdapter`` (kein ``get_infrastructure`` im Widget).

QFileDialog bleibt GUI-seitig; Persistenz nur über Port im Hauptpfad.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.gui.domains.settings.settings_data_sink import SettingsDataSink
from app.ui_application.presenters.settings_data_presenter import SettingsDataPresenter
from app.ui_contracts.workspaces.settings_data import (
    DataSettingsWritePatch,
    LoadDataSettingsCommand,
    SetPromptConfirmDeleteCommand,
    SetPromptDirectoryCommand,
    SetPromptStorageTypeCommand,
    SetRagEnabledCommand,
    SetRagSpaceCommand,
    SetRagTopKCommand,
    SetSelfImprovingEnabledCommand,
)

if TYPE_CHECKING:
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class DataSettingsPanel(QFrame):
    """Panel für Data-Einstellungen: RAG, Prompt-Speicherung."""

    def __init__(self, parent=None, *, settings_port: SettingsOperationsPort | None = None):
        self._settings_port = settings_port
        self._sink: SettingsDataSink | None = None
        self._presenter: SettingsDataPresenter | None = None
        super().__init__(parent)
        self.setObjectName("dataSettingsPanel")
        self._setup_ui()
        self._connect_signals()
        if settings_port is not None:
            self._sink = SettingsDataSink(
                self.rag_enabled_check,
                self.rag_space_combo,
                self.rag_top_k_spin,
                self.self_improving_check,
                self.prompt_storage_combo,
                self.prompt_directory_edit,
                self.prompt_confirm_delete_check,
                self._error_label,
            )
            self._presenter = SettingsDataPresenter(self._sink, settings_port)
            self._presenter.handle_command(LoadDataSettingsCommand())
        else:
            self._load_from_settings_legacy()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        title = QLabel("Data")
        title.setObjectName("settingsPanelTitle")
        layout.addWidget(title)

        desc = QLabel(
            "RAG-Konfiguration, Prompt-Speicherung. Änderungen werden automatisch gespeichert."
        )
        desc.setObjectName("settingsPanelDescription")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        form = QFormLayout()
        form.setSpacing(12)

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
        self.rag_top_k_spin.setToolTip("Anzahl der Chunks pro Abfrage")
        form.addRow("RAG Top-K:", self.rag_top_k_spin)

        self.self_improving_check = QCheckBox("Self-Improving Knowledge aktiv")
        self.self_improving_check.setToolTip(
            "Wissen aus LLM-Antworten extrahieren und automatisch in den Knowledge Store aufnehmen"
        )
        form.addRow("", self.self_improving_check)

        form.addRow(QLabel(""))  # Spacer

        self.prompt_storage_combo = QComboBox()
        self.prompt_storage_combo.addItems(["Datenbank", "Verzeichnis"])
        self.prompt_storage_combo.setToolTip("Datenbank: SQLite. Verzeichnis: JSON-Dateien.")
        form.addRow("Prompt-Speicherart:", self.prompt_storage_combo)

        dir_row = QHBoxLayout()
        self.prompt_directory_edit = QLineEdit()
        self.prompt_directory_edit.setPlaceholderText("Pfad zum Prompt-Verzeichnis")
        dir_row.addWidget(self.prompt_directory_edit)
        self.prompt_dir_btn = QPushButton("…")
        self.prompt_dir_btn.setFixedWidth(36)
        self.prompt_dir_btn.setToolTip("Ordner auswählen")
        dir_row.addWidget(self.prompt_dir_btn)
        form.addRow("Prompt-Verzeichnis:", dir_row)

        self.prompt_confirm_delete_check = QCheckBox("Vor Löschen bestätigen")
        self.prompt_confirm_delete_check.setToolTip("Bestätigungsdialog vor dem Löschen eines Prompts")
        form.addRow("", self.prompt_confirm_delete_check)

        layout.addLayout(form)

        self._error_label = QLabel("")
        self._error_label.setObjectName("dataSettingsError")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        layout.addStretch()

    def _use_port_path(self) -> bool:
        return self._settings_port is not None and self._presenter is not None

    def _connect_signals(self) -> None:
        self.rag_enabled_check.stateChanged.connect(self._on_rag_changed)
        self.rag_space_combo.currentTextChanged.connect(self._on_rag_space_changed)
        self.rag_top_k_spin.valueChanged.connect(self._on_rag_top_k_changed)
        self.self_improving_check.stateChanged.connect(self._on_self_improving_changed)
        self.prompt_storage_combo.currentIndexChanged.connect(self._on_prompt_storage_changed)
        self.prompt_directory_edit.editingFinished.connect(self._on_prompt_dir_changed)
        self.prompt_dir_btn.clicked.connect(self._on_browse_prompt_directory)
        self.prompt_confirm_delete_check.stateChanged.connect(self._on_confirm_delete_changed)

    @staticmethod
    def _legacy_adapter():
        from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter

        return ServiceSettingsAdapter()

    def _load_from_settings_legacy(self) -> None:
        try:
            from app.gui.domains.settings.settings_data_sink import SettingsDataSink

            state = self._legacy_adapter().load_data_settings_state()
            sink = SettingsDataSink(
                self.rag_enabled_check,
                self.rag_space_combo,
                self.rag_top_k_spin,
                self.self_improving_check,
                self.prompt_storage_combo,
                self.prompt_directory_edit,
                self.prompt_confirm_delete_check,
                self._error_label,
            )
            sink.apply_full_state(state)
        except Exception:
            pass

    def _storage_from_combo_index(self, index: int) -> Literal["database", "directory"]:
        return "directory" if index == 1 else "database"

    def _on_rag_changed(self, _state: int) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetRagEnabledCommand(self.rag_enabled_check.isChecked()))
            return
        try:
            self._legacy_adapter().persist_data_settings(
                DataSettingsWritePatch(rag_enabled=self.rag_enabled_check.isChecked())
            )
        except Exception:
            pass

    def _on_rag_space_changed(self, v: str) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            if v:
                self._presenter.handle_command(SetRagSpaceCommand(v))
            return
        if v:
            try:
                self._legacy_adapter().persist_data_settings(DataSettingsWritePatch(rag_space=v))
            except Exception:
                pass

    def _on_rag_top_k_changed(self, v: int) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetRagTopKCommand(v))
            return
        try:
            self._legacy_adapter().persist_data_settings(DataSettingsWritePatch(rag_top_k=v))
        except Exception:
            pass

    def _on_self_improving_changed(self, _state: int) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetSelfImprovingEnabledCommand(self.self_improving_check.isChecked()))
            return
        try:
            self._legacy_adapter().persist_data_settings(
                DataSettingsWritePatch(self_improving_enabled=self.self_improving_check.isChecked())
            )
        except Exception:
            pass

    def _on_prompt_storage_changed(self, index: int) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetPromptStorageTypeCommand(self._storage_from_combo_index(index)))
            return
        try:
            self._legacy_adapter().persist_data_settings(
                DataSettingsWritePatch(
                    prompt_storage_type=self._storage_from_combo_index(index),
                )
            )
        except Exception:
            pass

    def _on_prompt_dir_changed(self) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetPromptDirectoryCommand(self.prompt_directory_edit.text()))
            return
        try:
            self._legacy_adapter().persist_data_settings(
                DataSettingsWritePatch(
                    prompt_directory=(self.prompt_directory_edit.text() or "").strip(),
                    prompt_directory_set=True,
                )
            )
        except Exception:
            pass

    def _on_browse_prompt_directory(self) -> None:
        if self._use_port_path():
            current = self.prompt_directory_edit.text().strip()
            path = QFileDialog.getExistingDirectory(
                self,
                "Prompt-Verzeichnis wählen",
                current or ".",
            )
            if path:
                assert self._presenter is not None
                self._presenter.handle_command(SetPromptDirectoryCommand(path))
            return
        current = self.prompt_directory_edit.text().strip()
        path = QFileDialog.getExistingDirectory(
            self,
            "Prompt-Verzeichnis wählen",
            current or ".",
        )
        if path:
            self.prompt_directory_edit.setText(path)
            try:
                self._legacy_adapter().persist_data_settings(
                    DataSettingsWritePatch(prompt_directory=path, prompt_directory_set=True)
                )
            except Exception:
                pass

    def _on_confirm_delete_changed(self, _state: int) -> None:
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SetPromptConfirmDeleteCommand(self.prompt_confirm_delete_check.isChecked()))
            return
        try:
            self._legacy_adapter().persist_data_settings(
                DataSettingsWritePatch(prompt_confirm_delete=self.prompt_confirm_delete_check.isChecked())
            )
        except Exception:
            pass
