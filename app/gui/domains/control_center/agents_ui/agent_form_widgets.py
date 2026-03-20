"""
Agent Form Widgets – Formularfelder für Agentenprofile.

Capabilities-Editor, Tags, Listenfelder.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QComboBox,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFormLayout,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from typing import List, Optional

from app.agents.agent_profile import AgentProfile
from app.agents.departments import all_departments, Department, get_department_display_name
from app.core.models.roles import all_roles, get_role_display_name, ModelRole


class AgentCapabilitiesEditor(QWidget):
    """Editor für Capabilities (kommagetrennt oder Liste)."""

    capabilities_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.input = QLineEdit()
        self.input.setPlaceholderText(
            "z.B. research, code, debug, documentation (kommagetrennt)"
        )
        self.input.textChanged.connect(self._emit_changed)
        layout.addWidget(self.input)

    def _emit_changed(self):
        text = self.input.text().strip()
        caps = [c.strip() for c in text.split(",") if c.strip()]
        self.capabilities_changed.emit(caps)

    def set_capabilities(self, caps: List[str]):
        self.input.blockSignals(True)
        self.input.setText(", ".join(caps) if caps else "")
        self.input.blockSignals(False)

    def get_capabilities(self) -> List[str]:
        text = self.input.text().strip()
        return [c.strip() for c in text.split(",") if c.strip()]


class AgentProfileForm(QWidget):
    """Vollständiges Formular für Agentenprofile."""

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)

        # Basisdaten
        base_frame = QFrame()
        base_frame.setObjectName("profileBaseFrame")
        base_form = QFormLayout(base_frame)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Interner Name (eindeutig)")
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setPlaceholderText("Anzeigename")
        self.slug_edit = QLineEdit()
        self.slug_edit.setPlaceholderText("Slug (URL-freundlich)")
        base_form.addRow("Name:", self.name_edit)
        base_form.addRow("Anzeigename:", self.display_name_edit)
        base_form.addRow("Slug:", self.slug_edit)
        self.department_combo = QComboBox()
        for d in all_departments():
            self.department_combo.addItem(get_department_display_name(d), d.value)
        self.department_combo.setCurrentIndex(0)
        base_form.addRow("Abteilung:", self.department_combo)
        self.role_edit = QLineEdit()
        self.role_edit.setPlaceholderText("z.B. Researcher, Developer")
        base_form.addRow("Rolle:", self.role_edit)
        form_layout.addWidget(base_frame)

        # Beschreibung
        form_layout.addWidget(QLabel("Kurzbeschreibung:"))
        self.short_desc_edit = QLineEdit()
        self.short_desc_edit.setPlaceholderText("Einzeiler")
        form_layout.addWidget(self.short_desc_edit)
        form_layout.addWidget(QLabel("Ausführliche Beschreibung:"))
        self.long_desc_edit = QPlainTextEdit()
        self.long_desc_edit.setMaximumHeight(80)
        self.long_desc_edit.setPlaceholderText("Optionale ausführliche Beschreibung")
        form_layout.addWidget(self.long_desc_edit)

        # Status
        form_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("Aktiv", "active")
        self.status_combo.addItem("Inaktiv", "inactive")
        self.status_combo.addItem("Archiviert", "archived")
        form_layout.addWidget(self.status_combo)

        # Modellzuweisung
        form_layout.addWidget(QLabel("Modell:"))
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setPlaceholderText("Modell-ID oder leer für Auto")
        form_layout.addWidget(self.model_combo)
        form_layout.addWidget(QLabel("Modellrolle:"))
        self.model_role_combo = QComboBox()
        for r in all_roles():
            self.model_role_combo.addItem(get_role_display_name(r), r.value)
        self.model_role_combo.setCurrentIndex(1)  # DEFAULT
        form_layout.addWidget(self.model_role_combo)

        # System-Prompt
        form_layout.addWidget(QLabel("System-Prompt:"))
        self.system_prompt_edit = QPlainTextEdit()
        self.system_prompt_edit.setMaximumHeight(120)
        self.system_prompt_edit.setPlaceholderText("System-Prompt für den Agenten")
        form_layout.addWidget(self.system_prompt_edit)

        # Capabilities
        form_layout.addWidget(QLabel("Capabilities:"))
        self.capabilities_editor = AgentCapabilitiesEditor()
        form_layout.addWidget(self.capabilities_editor)

        # Tools
        form_layout.addWidget(QLabel("Tools (kommagetrennt):"))
        self.tools_edit = QLineEdit()
        self.tools_edit.setPlaceholderText("z.B. rag, web_search, comfyui")
        form_layout.addWidget(self.tools_edit)

        # Knowledge Spaces
        form_layout.addWidget(QLabel("Knowledge Spaces:"))
        self.knowledge_edit = QLineEdit()
        self.knowledge_edit.setPlaceholderText("z.B. default, code, documentation")
        form_layout.addWidget(self.knowledge_edit)

        # Tags
        form_layout.addWidget(QLabel("Tags (kommagetrennt):"))
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("z.B. research, default")
        form_layout.addWidget(self.tags_edit)

        form_layout.addStretch()
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)

    def set_model_options(self, model_ids: List[str]):
        """Befüllt die Modell-Combo mit verfügbaren Modellen."""
        self.model_combo.clear()
        self.model_combo.addItem("(Auto)", "")
        for mid in sorted(model_ids):
            self.model_combo.addItem(mid, mid)

    def load_profile(self, profile: Optional[AgentProfile]):
        """Lädt ein Profil in das Formular."""
        if not profile:
            self.name_edit.clear()
            self.display_name_edit.clear()
            self.slug_edit.clear()
            self.short_desc_edit.clear()
            self.long_desc_edit.clear()
            self.role_edit.clear()
            self.status_combo.setCurrentIndex(0)
            self.model_combo.setCurrentIndex(0)
            self.model_role_combo.setCurrentIndex(1)
            self.system_prompt_edit.clear()
            self.capabilities_editor.set_capabilities([])
            self.tools_edit.setText("")
            self.knowledge_edit.setText("")
            self.tags_edit.setText("")
            return
        self.name_edit.setText(profile.name or "")
        self.display_name_edit.setText(profile.display_name or "")
        self.slug_edit.setText(profile.slug or "")
        self.short_desc_edit.setText(profile.short_description or "")
        self.long_desc_edit.setPlainText(profile.long_description or "")
        self.role_edit.setText(profile.role or "")
        idx = self.status_combo.findData(profile.status)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)
        idx = self.model_combo.findData(profile.assigned_model or "")
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        else:
            self.model_combo.setCurrentText(profile.assigned_model or "")
        idx = self.model_role_combo.findData(profile.assigned_model_role or "")
        if idx >= 0:
            self.model_role_combo.setCurrentIndex(idx)
        else:
            self.model_role_combo.setCurrentIndex(1)
        self.system_prompt_edit.setPlainText(profile.system_prompt or "")
        self.capabilities_editor.set_capabilities(profile.capabilities)
        self.tools_edit.setText(", ".join(profile.tools) if profile.tools else "")
        self.knowledge_edit.setText(", ".join(profile.knowledge_spaces) if profile.knowledge_spaces else "")
        self.tags_edit.setText(", ".join(profile.tags) if profile.tags else "")
        idx = self.department_combo.findData(profile.department)
        if idx >= 0:
            self.department_combo.setCurrentIndex(idx)

    def to_profile(self, profile: Optional[AgentProfile] = None) -> AgentProfile:
        """Erstellt ein Profil aus den Formulardaten."""
        p = profile or AgentProfile()
        p.name = self.name_edit.text().strip()
        p.display_name = self.display_name_edit.text().strip() or p.name
        p.slug = self.slug_edit.text().strip() or AgentProfile._slugify(p.name)
        p.short_description = self.short_desc_edit.text().strip()
        p.long_description = self.long_desc_edit.toPlainText().strip()
        p.department = self.department_combo.currentData() or "general"
        p.role = self.role_edit.text().strip()
        p.status = self.status_combo.currentData() or "active"
        p.assigned_model = self.model_combo.currentData() or None
        if not p.assigned_model and self.model_combo.currentText():
            p.assigned_model = self.model_combo.currentText().strip() or None
        p.assigned_model_role = self.model_role_combo.currentData() or None
        p.system_prompt = self.system_prompt_edit.toPlainText().strip()
        p.capabilities = self.capabilities_editor.get_capabilities()
        tools_txt = self.tools_edit.text().strip()
        p.tools = [t.strip() for t in tools_txt.split(",") if t.strip()]
        ks_txt = self.knowledge_edit.text().strip()
        p.knowledge_spaces = [k.strip() for k in ks_txt.split(",") if k.strip()]
        tags_txt = self.tags_edit.text().strip()
        p.tags = [t.strip() for t in tags_txt.split(",") if t.strip()]
        return p
