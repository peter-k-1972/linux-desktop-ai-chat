"""
UX Regression Tests – Verhindern von UX Regressionen.

Basierend auf UX_DEFECTS_BEHAVIOR_TEST.md. Fokussierte Tests für:
- Chat Navigation Language Consistency (D6)
- Sidebar Label Consistency (D7)
- Inspector Workspace Sync (D9)
- Settings Breadcrumb Correctness (D1)
- Project Context Isolation (V1)
"""

import os
import pytest
import tempfile
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer


def _ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


def _process_events():
    app = QApplication.instance()
    if app:
        app.processEvents()
        QTimer.singleShot(50, lambda: None)
        app.processEvents()


@pytest.mark.regression
class UXRegressionTests(unittest.TestCase):
    """Fokussierte Regressionstests für UX-Verhalten."""

    def setUp(self):
        _ensure_qapp()

    def test_chat_navigation_language_consistency(self):
        """1. Chat Navigation Language Consistency (D6).
        Verhindert Rückfall zu gemischten EN/DE Labels."""
        from app.gui.domains.operations.chat.panels.chat_navigation_panel import ChatNavigationPanel

        panel = ChatNavigationPanel(None)
        panel.set_project(1, "Test")

        # Filter-Labels: Angeheftet, Archiv (kein Pinned)
        assert "Pinned" not in str(panel._filter_pinned.text())
        assert "Angeheftet" in str(panel._filter_pinned.text())
        assert "Archiv" in str(panel._filter_archived.text()) or "Archiviert" in str(
            panel._filter_archived.text()
        )

        # Topic-Filter: Alle Themen, Ungruppiert (kein Alle Topics, Ungrouped)
        for i in range(panel._filter_topic.count()):
            item_text = panel._filter_topic.itemText(i)
            assert "Ungrouped" not in item_text
            assert "Alle Topics" not in item_text

        # Recent-Filter: Alle, 7 Tage, 30 Tage
        assert "Alle" in [panel._filter_recent.itemText(j) for j in range(panel._filter_recent.count())]

    def test_sidebar_label_consistency(self):
        """2. Sidebar Label Consistency (D7).
        Sidebar und Operations Nav müssen dieselben Labels für dieselben Workspaces nutzen."""
        from app.gui.navigation.sidebar_config import get_sidebar_sections
        from app.gui.domains.operations.operations_nav import OperationsNav

        sections = get_sidebar_sections()
        sidebar_by_key = {
            item.workspace_id or item.area_id: item.title
            for s in sections
            for item in s.items
        }
        ops_titles = dict(OperationsNav.WORKSPACES)

        for ws_id in ("operations_projects", "operations_agent_tasks"):
            sidebar_title = sidebar_by_key.get(ws_id)
            ops_title = ops_titles.get(ws_id)
            assert sidebar_title == ops_title, (
                f"Sidebar/Operations mismatch for {ws_id}: "
                f"Sidebar={sidebar_title!r}, Ops={ops_title!r}"
            )

        # PROJECT-Sektion: Command Center + Projekte (kein separater Project Hub mehr)
        project_section = next((s for s in sections if s.id == "project"), None)
        assert project_section is not None
        titles = [i.title for i in project_section.items]
        assert "Projektübersicht" not in titles
        assert "Systemübersicht" in titles
        assert "Projekte" in titles
        assert len(project_section.items) == 2
        tooltips = [i.tooltip for i in project_section.items if getattr(i, "tooltip", None)]
        assert len(tooltips) >= 2

    def test_inspector_workspace_sync(self):
        """3. Inspector Workspace Sync (D9).
        InspectorHost muss prepare_for_setup und content_token-Guard haben.
        OperationsScreen muss clear vor setup aufrufen."""
        from app.gui.inspector.inspector_host import InspectorHost
        from app.gui.domains.operations.operations_screen import OperationsScreen

        # InspectorHost: prepare_for_setup existiert
        host = InspectorHost(None)
        assert hasattr(host, "prepare_for_setup")
        assert callable(host.prepare_for_setup)

        # prepare_for_setup liefert Token und cleared
        token = host.prepare_for_setup()
        assert isinstance(token, int)
        assert token > 0
        assert host._stack.currentIndex() == 0  # Default-Content sichtbar

        # set_content mit falschem Token wird verworfen
        from PySide6.QtWidgets import QLabel
        stale_widget = QLabel("Stale")
        host.set_content(stale_widget, content_token=token - 1)
        assert host._stack.count() == 1  # Kein neuer Content

        # OperationsScreen._on_workspace_changed ruft prepare_for_setup vor setup_inspector
        import inspect
        source = inspect.getsource(OperationsScreen._on_workspace_changed)
        assert "prepare_for_setup" in source
        assert "content_token" in source

    def test_settings_breadcrumb_correctness(self):
        """4. Settings Breadcrumb Correctness (D1).
        Breadcrumb muss die tatsächlich sichtbare Settings-Kategorie anzeigen."""
        from app.gui.bootstrap import register_all_screens
        from app.gui.workspace.workspace_host import WorkspaceHost
        from app.gui.navigation.nav_areas import NavArea
        from app.gui.breadcrumbs import set_breadcrumb_manager
        from app.gui.breadcrumbs.manager import BreadcrumbManager
        from app.services.infrastructure import set_infrastructure, _ServiceInfrastructure
        from app.db import DatabaseManager
        from app.core.config.settings import AppSettings

        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            with patch("app.services.infrastructure.OllamaClient") as mock_cls:
                mock_client = MagicMock()
                mock_client.get_debug_info = AsyncMock(return_value={"online": True})
                mock_client.get_models = AsyncMock(return_value=[])
                mock_cls.return_value = mock_client

                infra = _ServiceInfrastructure()
                infra._client = mock_client
                infra._db = DatabaseManager(db_path=db_path)
                infra._settings = AppSettings()
                set_infrastructure(infra)

                try:
                    register_all_screens()
                    host = WorkspaceHost()
                    host.register_from_registry()

                    bc_mgr = BreadcrumbManager()
                    set_breadcrumb_manager(bc_mgr)

                    # Settings → Appearance öffnen
                    host.show_area(NavArea.SETTINGS, "settings_appearance")
                    _process_events()

                    settings_screen = host.widget(host._area_to_index[NavArea.SETTINGS])
                    current = settings_screen.get_current_workspace()

                    assert current == "settings_appearance", (
                        f"get_current_workspace should return settings_appearance, got {current!r}"
                    )

                    # Zu Chat wechseln, dann Settings ohne workspace_id (Command Palette)
                    host.show_area(NavArea.OPERATIONS, "operations_chat")
                    _process_events()
                    host.show_area(NavArea.SETTINGS)
                    _process_events()

                    current_after = settings_screen.get_current_workspace()
                    assert current_after == "settings_appearance", (
                        f"Breadcrumb/category should stay Appearance after Command Palette open, "
                        f"got {current_after!r}"
                    )
                finally:
                    set_infrastructure(None)
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass

    def test_project_context_isolation(self):
        """5. Project Context Isolation (V1).
        Projektbezogene Workspaces müssen project_context_changed abonnieren."""
        from app.gui.domains.operations.chat.chat_workspace import ChatWorkspace
        from app.gui.domains.operations.knowledge.knowledge_workspace import KnowledgeWorkspace
        from app.gui.domains.operations.prompt_studio.prompt_studio_workspace import (
            PromptStudioWorkspace,
        )
        from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import (
            AgentTasksWorkspace,
        )

        # Diese Workspaces zeigen projektbezogene Daten und müssen auf Projektwechsel reagieren
        project_scoped_workspaces = [
            ChatWorkspace,
            KnowledgeWorkspace,
            PromptStudioWorkspace,
            AgentTasksWorkspace,
        ]

        for ws_class in project_scoped_workspaces:
            assert hasattr(ws_class, "_on_project_context_changed"), (
                f"{ws_class.__name__} must have _on_project_context_changed for project isolation"
            )

        # ChatWorkspace: D2 – Restore last selection when switching projects back
        chat_ws = ChatWorkspace(None)
        assert hasattr(chat_ws, "_restore_project_selection")
        assert hasattr(chat_ws, "_last_selected_chat_per_project")
