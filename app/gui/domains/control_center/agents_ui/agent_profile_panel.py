"""
AgentProfilePanel – Detailansicht und Bearbeitung eines Agentenprofils.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QMessageBox,
    QFrame,
    QScrollArea,
    QTabWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.agents.agent_profile import AgentProfile
from app.agents.departments import department_from_str, get_department_display_name
from app.gui.domains.control_center.agents_ui.agent_avatar_widget import AgentAvatarWidget
from app.gui.domains.control_center.agents_ui.agent_form_widgets import AgentProfileForm
from app.gui.domains.control_center.agents_ui.agent_performance_tab import AgentPerformanceTab


class AgentProfilePanel(QWidget):
    """Profil-Detail und Bearbeitungsbereich."""

    save_requested = Signal(object)  # AgentProfile
    agent_changed = Signal(object)  # AgentProfile (für Chat-Integration)

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self._current_profile: AgentProfile | None = None
        self._edit_mode = False
        self.init_ui()

    def init_ui(self):
        self.setObjectName("agentProfilePanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Kopf: Avatar + Name
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 12)

        self.avatar_widget = AgentAvatarWidget(theme=self.theme, size=64)
        self.avatar_widget.avatar_changed.connect(self._on_avatar_changed)
        header_layout.addWidget(self.avatar_widget)

        title_layout = QVBoxLayout()
        self.name_label = QLabel("Kein Agent ausgewählt")
        self.name_label.setObjectName("profileNameLabel")
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.DemiBold)
        self.name_label.setFont(font)
        self.dept_label = QLabel("")
        self.dept_label.setStyleSheet("color: #64748b; font-size: 12px;")
        title_layout.addWidget(self.name_label)
        title_layout.addWidget(self.dept_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addWidget(header)

        # Aktionen
        actions_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Bearbeiten")
        self.edit_btn.setObjectName("profileEditBtn")
        self.edit_btn.clicked.connect(self._toggle_edit)
        self.save_btn = QPushButton("Speichern")
        self.save_btn.setObjectName("profileSaveBtn")
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setVisible(False)
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self._toggle_edit)
        self.cancel_btn.setVisible(False)
        actions_layout.addWidget(self.edit_btn)
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.cancel_btn)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Tabs: Profil | Performance
        self.tab_widget = QTabWidget()
        profile_tab = QWidget()
        profile_tab_layout = QVBoxLayout(profile_tab)
        profile_tab_layout.setContentsMargins(0, 0, 0, 0)

        # Formular (Bearbeitung)
        self.form = AgentProfileForm(theme=self.theme)
        self.form.setVisible(False)
        profile_tab_layout.addWidget(self.form)

        # Leseansicht (nur Anzeige)
        self.readonly_frame = QFrame()
        self.readonly_frame.setObjectName("profileReadonlyFrame")
        readonly_layout = QVBoxLayout(self.readonly_frame)
        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #94a3b8;")
        readonly_layout.addWidget(self.desc_label)
        self.prompt_preview = QLabel("")
        self.prompt_preview.setWordWrap(True)
        self.prompt_preview.setMaximumHeight(60)
        self.prompt_preview.setStyleSheet("color: #64748b; font-size: 11px;")
        readonly_layout.addWidget(QLabel("System-Prompt:"))
        readonly_layout.addWidget(self.prompt_preview)
        readonly_layout.addStretch()
        profile_tab_layout.addWidget(self.readonly_frame)

        self.tab_widget.addTab(profile_tab, "Profil")
        self.performance_tab = AgentPerformanceTab(theme=self.theme)
        self.tab_widget.addTab(self.performance_tab, "Performance")
        layout.addWidget(self.tab_widget)

    def set_model_options(self, model_ids: list[str]):
        """Befüllt die Modell-Combo im Formular."""
        self.form.set_model_options(model_ids)

    def load_profile(self, profile: AgentProfile | None):
        """Lädt ein Profil in die Ansicht."""
        self._current_profile = profile
        self._edit_mode = False
        self.edit_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.form.setVisible(False)
        self.readonly_frame.setVisible(True)

        if not profile:
            self.name_label.setText("Kein Agent ausgewählt")
            self.dept_label.setText("")
            self.desc_label.setText("")
            self.prompt_preview.setText("")
            self.avatar_widget.set_avatar_path(None)
            self.performance_tab.load_profile(None)
            return

        self.name_label.setText(profile.effective_display_name)
        dept = department_from_str(profile.department)
        self.dept_label.setText(get_department_display_name(dept) if dept else (profile.department or "-"))
        self.desc_label.setText(profile.short_description or profile.long_description or "-")
        prompt = profile.system_prompt or ""
        self.prompt_preview.setText(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        self.avatar_widget.set_avatar_path(profile.avatar_path)
        self.form.load_profile(profile)
        self.performance_tab.load_profile(profile)

    def _toggle_edit(self):
        """Wechselt zwischen Lese- und Bearbeitungsmodus."""
        self._edit_mode = not self._edit_mode
        self.form.setVisible(self._edit_mode)
        self.readonly_frame.setVisible(not self._edit_mode)
        self.edit_btn.setVisible(not self._edit_mode)
        self.save_btn.setVisible(self._edit_mode)
        self.cancel_btn.setVisible(self._edit_mode)
        if self._edit_mode and self._current_profile:
            self.form.load_profile(self._current_profile)

    def _on_save(self):
        """Speichert das Profil."""
        if not self._current_profile:
            return
        profile = self.form.to_profile(self._current_profile)
        self.save_requested.emit(profile)

    def _on_avatar_changed(self, path: str):
        """Avatar wurde geändert."""
        if self._current_profile:
            self._current_profile.avatar_path = path if path else None

    def refresh_theme(self, theme: str):
        self.theme = theme
        self.avatar_widget.refresh_theme(theme)
        self.performance_tab.theme = theme
