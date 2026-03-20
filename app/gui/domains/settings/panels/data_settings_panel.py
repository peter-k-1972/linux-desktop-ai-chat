"""
DataSettingsPanel – RAG, Prompt-Speicherung für Settings-Kategorie.

Bindet an AppSettings über get_infrastructure().settings.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QFileDialog,
)
from PySide6.QtCore import Qt


class DataSettingsPanel(QFrame):
    """Panel für Data-Einstellungen: RAG, Prompt-Speicherung."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dataSettingsPanel")
        self._setup_ui()
        self._connect_signals()
        self._load_from_settings()

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
        layout.addStretch()

    def _connect_signals(self) -> None:
        self.rag_enabled_check.stateChanged.connect(self._on_rag_changed)
        self.rag_space_combo.currentTextChanged.connect(self._on_rag_space_changed)
        self.rag_top_k_spin.valueChanged.connect(self._on_rag_top_k_changed)
        self.self_improving_check.stateChanged.connect(self._on_self_improving_changed)
        self.prompt_storage_combo.currentIndexChanged.connect(self._on_prompt_storage_changed)
        self.prompt_directory_edit.editingFinished.connect(self._on_prompt_dir_changed)
        self.prompt_dir_btn.clicked.connect(self._on_browse_prompt_directory)
        self.prompt_confirm_delete_check.stateChanged.connect(self._on_confirm_delete_changed)

    def _get_settings(self):
        from app.services.infrastructure import get_infrastructure
        return get_infrastructure().settings

    def _load_from_settings(self) -> None:
        try:
            s = self._get_settings()
            self.rag_enabled_check.setChecked(getattr(s, "rag_enabled", False))
            self.rag_space_combo.setCurrentText(getattr(s, "rag_space", "default"))
            self.rag_top_k_spin.setValue(getattr(s, "rag_top_k", 5))
            self.self_improving_check.setChecked(getattr(s, "self_improving_enabled", False))
            storage = getattr(s, "prompt_storage_type", "database")
            self.prompt_storage_combo.setCurrentIndex(1 if storage == "directory" else 0)
            self.prompt_directory_edit.setText(getattr(s, "prompt_directory", "") or "")
            self.prompt_confirm_delete_check.setChecked(getattr(s, "prompt_confirm_delete", True))
        except Exception:
            pass

    def _on_rag_changed(self) -> None:
        try:
            s = self._get_settings()
            s.rag_enabled = self.rag_enabled_check.isChecked()
            s.save()
        except Exception:
            pass

    def _on_rag_space_changed(self, v: str) -> None:
        if v:
            try:
                s = self._get_settings()
                s.rag_space = v
                s.save()
            except Exception:
                pass

    def _on_rag_top_k_changed(self, v: int) -> None:
        try:
            s = self._get_settings()
            s.rag_top_k = v
            s.save()
        except Exception:
            pass

    def _on_self_improving_changed(self) -> None:
        try:
            s = self._get_settings()
            s.self_improving_enabled = self.self_improving_check.isChecked()
            s.save()
        except Exception:
            pass

    def _on_prompt_storage_changed(self) -> None:
        try:
            s = self._get_settings()
            s.prompt_storage_type = "directory" if self.prompt_storage_combo.currentIndex() == 1 else "database"
            s.save()
        except Exception:
            pass

    def _on_prompt_dir_changed(self) -> None:
        try:
            s = self._get_settings()
            s.prompt_directory = (self.prompt_directory_edit.text() or "").strip()
            s.save()
        except Exception:
            pass

    def _on_browse_prompt_directory(self) -> None:
        current = self.prompt_directory_edit.text().strip()
        path = QFileDialog.getExistingDirectory(
            self,
            "Prompt-Verzeichnis wählen",
            current or ".",
        )
        if path:
            self.prompt_directory_edit.setText(path)
            try:
                s = self._get_settings()
                s.prompt_directory = path
                s.save()
            except Exception:
                pass

    def _on_confirm_delete_changed(self) -> None:
        try:
            s = self._get_settings()
            s.prompt_confirm_delete = self.prompt_confirm_delete_check.isChecked()
            s.save()
        except Exception:
            pass
