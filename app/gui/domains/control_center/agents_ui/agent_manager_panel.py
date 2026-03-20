"""
AgentManagerPanel – HR-Verwaltungsoberfläche für Agenten.

Kombiniert Agentenliste, Profilansicht und Aktionen.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, Signal

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_service import get_agent_service, AgentService
from app.agents.agent_registry import get_agent_registry
from app.agents.seed_agents import ensure_seed_agents
from app.gui.domains.control_center.agents_ui.agent_list_panel import AgentListPanel
from app.gui.domains.control_center.agents_ui.agent_profile_panel import AgentProfilePanel


class AgentManagerPanel(QWidget):
    """
    Vollständige Agenten-HR-Verwaltung.
    Liste links, Profil rechts, Aktionen oben.
    """

    agent_selected_for_chat = Signal(object)  # AgentProfile für Chat-Integration

    def __init__(
        self,
        agent_service: AgentService | None = None,
        theme: str = "dark",
        model_ids: list[str] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._service = agent_service or get_agent_service()
        self._registry = get_agent_registry()
        self.theme = theme
        self._model_ids = model_ids or []
        self.init_ui()
        self._ensure_seed()
        self._refresh_list()

    def init_ui(self):
        self.setObjectName("agentManagerPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Aktionsleiste
        actions_layout = QHBoxLayout()
        self.new_btn = QPushButton("Neu")
        self.new_btn.setObjectName("agentNewBtn")
        self.new_btn.clicked.connect(self._on_new)
        self.duplicate_btn = QPushButton("Duplizieren")
        self.duplicate_btn.setObjectName("agentDuplicateBtn")
        self.duplicate_btn.clicked.connect(self._on_duplicate)
        self.activate_btn = QPushButton("Aktivieren")
        self.activate_btn.clicked.connect(self._on_activate)
        self.deactivate_btn = QPushButton("Deaktivieren")
        self.deactivate_btn.clicked.connect(self._on_deactivate)
        self.delete_btn = QPushButton("Löschen")
        self.delete_btn.setObjectName("agentDeleteBtn")
        self.delete_btn.clicked.connect(self._on_delete)
        self.use_in_chat_btn = QPushButton("Im Chat verwenden")
        self.use_in_chat_btn.setObjectName("agentUseInChatBtn")
        self.use_in_chat_btn.clicked.connect(self._on_use_in_chat)
        actions_layout.addWidget(self.new_btn)
        actions_layout.addWidget(self.duplicate_btn)
        actions_layout.addWidget(self.activate_btn)
        actions_layout.addWidget(self.deactivate_btn)
        actions_layout.addWidget(self.delete_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.use_in_chat_btn)
        layout.addLayout(actions_layout)

        # Splitter: Liste | Profil
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.list_panel = AgentListPanel(theme=self.theme)
        self.list_panel.agent_selected.connect(self._on_agent_selected)
        splitter.addWidget(self.list_panel)

        self.profile_panel = AgentProfilePanel(theme=self.theme)
        self.profile_panel.save_requested.connect(self._on_save)
        self.profile_panel.set_model_options(self._model_ids)
        splitter.addWidget(self.profile_panel)
        splitter.setSizes([250, 400])
        layout.addWidget(splitter)

    def _ensure_seed(self):
        """Stellt sicher, dass Standard-Agenten existieren."""
        ensure_seed_agents()

    def _refresh_list(self):
        """Aktualisiert die Agentenliste."""
        agents = self._service.list_all()
        self.list_panel.set_agents(agents)
        self._registry.refresh()

    def set_model_ids(self, model_ids: list[str]):
        """Setzt die verfügbaren Modell-IDs für die Modell-Combo."""
        self._model_ids = model_ids
        self.profile_panel.set_model_options(model_ids)

    def _on_agent_selected(self, profile: AgentProfile):
        """Agent wurde in der Liste ausgewählt."""
        self.list_panel.set_current_agent(profile)
        self.profile_panel.load_profile(profile)
        self._update_action_states(profile)

    def _update_action_states(self, profile: AgentProfile | None):
        """Aktualisiert die Sichtbarkeit der Aktionsbuttons."""
        has_selection = profile is not None
        self.duplicate_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.use_in_chat_btn.setEnabled(has_selection and profile.is_active)
        self.activate_btn.setEnabled(has_selection and profile.status != AgentStatus.ACTIVE.value)
        self.deactivate_btn.setEnabled(has_selection and profile.status == AgentStatus.ACTIVE.value)

    def _on_new(self):
        """Neuen Agenten anlegen."""
        profile = AgentProfile(
            name="Neuer Agent",
            display_name="Neuer Agent",
            slug="",
            status=AgentStatus.INACTIVE.value,
        )
        agent_id, err = self._service.create(profile)
        if err:
            QMessageBox.warning(self, "Fehler", err)
            return
        self._registry.refresh()
        self._refresh_list()
        created = self._service.get(agent_id)
        if created:
            self.list_panel.set_agents(self._service.list_all())
            self.profile_panel.load_profile(created)
            self.profile_panel._edit_mode = True
            self.profile_panel.form.setVisible(True)
            self.profile_panel.readonly_frame.setVisible(False)
            self.profile_panel.edit_btn.setVisible(False)
            self.profile_panel.save_btn.setVisible(True)
            self.profile_panel.cancel_btn.setVisible(True)
            self._update_action_states(created)

    def _on_duplicate(self):
        """Agent duplizieren."""
        profile = self.list_panel.get_selected()
        if not profile or not profile.id:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst einen Agenten auswählen.")
            return
        new_id, err = self._service.duplicate(profile.id)
        if err:
            QMessageBox.warning(self, "Fehler", err)
            return
        self._registry.refresh()
        self._refresh_list()
        created = self._service.get(new_id)
        if created:
            self.profile_panel.load_profile(created)
            self._update_action_states(created)

    def _on_activate(self):
        """Agent aktivieren."""
        profile = self.list_panel.get_selected()
        if not profile or not profile.id:
            return
        ok, err = self._service.activate(profile.id)
        if err:
            QMessageBox.warning(self, "Fehler", err)
            return
        self._registry.refresh()
        self._refresh_list()
        updated = self._service.get(profile.id)
        self.profile_panel.load_profile(updated)
        self._update_action_states(updated)

    def _on_deactivate(self):
        """Agent deaktivieren."""
        profile = self.list_panel.get_selected()
        if not profile or not profile.id:
            return
        ok, err = self._service.deactivate(profile.id)
        if err:
            QMessageBox.warning(self, "Fehler", err)
            return
        self._registry.refresh()
        self._refresh_list()
        updated = self._service.get(profile.id)
        self.profile_panel.load_profile(updated)
        self._update_action_states(updated)

    def _on_delete(self):
        """Agent löschen."""
        profile = self.list_panel.get_selected()
        if not profile or not profile.id:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst einen Agenten auswählen.")
            return
        reply = QMessageBox.question(
            self,
            "Agent löschen",
            f"Agent '{profile.effective_display_name}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        ok, err = self._service.delete(profile.id)
        if err:
            QMessageBox.warning(self, "Fehler", err)
            return
        self._registry.unregister(profile.id)
        self._refresh_list()
        self.profile_panel.load_profile(None)
        self._update_action_states(None)

    def _on_save(self, profile: AgentProfile):
        """Profil speichern."""
        ok, err = self._service.update(profile)
        if err:
            QMessageBox.warning(self, "Fehler", err)
            return
        self._registry.register_profile(profile)
        self._refresh_list()
        self.profile_panel.load_profile(profile)
        self._update_action_states(profile)

    def _on_use_in_chat(self):
        """Agent für Chat auswählen."""
        profile = self.list_panel.get_selected()
        if profile and profile.is_active:
            self.agent_selected_for_chat.emit(profile)


class AgentManagerDialog(QDialog):
    """Dialog mit AgentManagerPanel für Toolbar/Menü-Öffnung."""

    agent_selected_for_chat = Signal(object)

    def __init__(self, theme: str = "dark", model_ids: list[str] | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agenten verwalten (HR)")
        self.setMinimumSize(800, 500)
        layout = QVBoxLayout(self)
        self.panel = AgentManagerPanel(theme=theme, model_ids=model_ids)
        self.panel.agent_selected_for_chat.connect(self._on_agent_selected)
        layout.addWidget(self.panel)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)

    def _on_agent_selected(self, profile):
        self.agent_selected_for_chat.emit(profile)
        self.accept()
