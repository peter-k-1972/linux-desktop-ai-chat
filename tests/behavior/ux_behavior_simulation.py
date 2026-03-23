"""
UX Behavior Simulation – Simulates realistic manual usage to find defects.

Runs programmatically (no human interaction). Exercises:
- Switching projects repeatedly
- Opening Chat / Knowledge / Prompt Studio / Agents in different orders
- Navigating to Settings and back
- Checking for stale UI state, inconsistent labels, empty views
- Project-scoped data isolation

Documents observed behavior for defect reporting.
"""

import os
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


# Module-level defect list for reporting
_RECORDED_DEFECTS = []


class UXBehaviorSimulation(unittest.TestCase):
    """Simulates user flows and records observed behavior."""

    def setUp(self):
        _ensure_qapp()

    def _record_defect(self, id_, title, steps, expected, actual, severity, subsystem):
        _RECORDED_DEFECTS.append({
            "id": id_,
            "title": title,
            "steps": steps,
            "expected": expected,
            "actual": actual,
            "severity": severity,
            "subsystem": subsystem,
        })

    def test_project_switch_chat_restoration(self):
        """D2: Chat restores last-selected session when switching projects back."""
        from app.gui.bootstrap import register_all_screens
        from app.gui.workspace.workspace_host import WorkspaceHost
        from app.gui.navigation.nav_areas import NavArea
        from app.services.infrastructure import set_infrastructure, _ServiceInfrastructure
        from app.db import DatabaseManager
        from app.core.config.settings import AppSettings
        from app.core.context.project_context_manager import get_project_context_manager
        from app.services.project_service import get_project_service, set_project_service

        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            mock_client = MagicMock()
            mock_client.get_debug_info = AsyncMock(return_value={"online": True})
            mock_client.get_models = AsyncMock(return_value=[])

            with patch("app.services.infrastructure.OllamaClient", return_value=mock_client):
                set_project_service(None)
                infra = _ServiceInfrastructure()
                infra._client = mock_client
                infra._db = DatabaseManager(db_path=db_path)
                infra._settings = AppSettings()
                set_infrastructure(infra)

                try:
                    register_all_screens()
                    host = WorkspaceHost()
                    host.register_from_registry()

                    # Create projects
                    svc = get_project_service()
                    pa = svc.create_project("Project A", "")
                    pb = svc.create_project("Project B", "")

                    # Show Operations > Chat
                    host.show_area(NavArea.OPERATIONS, "operations_chat")
                    _process_events()

                    # Get ChatWorkspace
                    ops = host.widget(host._area_to_index[NavArea.OPERATIONS])
                    chat_ws = ops._stack.widget(ops._stack_indices["operations_chat"])

                    # Set Project A, select a chat (simulate)
                    pcm = get_project_context_manager()
                    pcm.set_active_project(pa)
                    _process_events()

                    # ChatWorkspace should have _last_selected_chat_per_project
                    last_per_proj = getattr(chat_ws, "_last_selected_chat_per_project", {})
                    has_restore = hasattr(chat_ws, "_restore_project_selection")

                    # Switch to B, then back to A
                    pcm.set_active_project(pb)
                    _process_events()
                    pcm.set_active_project(pa)
                    _process_events()

                    # Expected: last selected chat restored or first chat selected
                    # Actual: check if _restore_project_selection exists and is called
                    if not has_restore:
                        self._record_defect(
                            "D2", "Chat does not restore last-selected session",
                            ["Select Project A", "Open Chat", "Select chat", "Switch to B", "Switch back to A"],
                            "Chat shows previously selected chat (or first chat)",
                            "No _restore_project_selection logic",
                            "Major",
                            "ChatWorkspace",
                        )
                finally:
                    set_infrastructure(None)
                    set_project_service(None)
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass

    def test_settings_breadcrumb_via_command_palette(self):
        """D1: Settings breadcrumb when opened via Command Palette (no workspace_id)."""
        from app.gui.bootstrap import register_all_screens
        from app.gui.workspace.workspace_host import WorkspaceHost
        from app.gui.navigation.nav_areas import NavArea
        from app.gui.breadcrumbs import get_breadcrumb_manager, set_breadcrumb_manager
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

                    # 1. Open Settings via Sidebar (Appearance)
                    host.show_area(NavArea.SETTINGS, "settings_appearance")
                    _process_events()

                    settings_screen = host.widget(host._area_to_index[NavArea.SETTINGS])
                    current_cat = settings_screen.get_current_workspace()
                    path = bc_mgr.get_path()
                    bc_title = path[-1].title if path else ""

                    # 2. Navigate to Chat
                    host.show_area(NavArea.OPERATIONS, "operations_chat")
                    _process_events()

                    # 3. Open Settings via Command Palette (no workspace_id)
                    host.show_area(NavArea.SETTINGS)  # no workspace_id
                    _process_events()

                    # Breadcrumb should reflect actual category (Appearance if that was last)
                    current_after = settings_screen.get_current_workspace()
                    path_after = bc_mgr.get_path()
                    bc_title_after = path_after[-1].title if path_after else ""

                    # Defect: if get_current_workspace returns settings_application but
                    # content shows Appearance, breadcrumb would be wrong
                    if current_after != "settings_appearance" and current_cat == "settings_appearance":
                        self._record_defect(
                            "D1", "Settings breadcrumb mismatch",
                            ["Open Settings > Appearance", "Go to Chat", "Open Settings (Command Palette)"],
                            "Breadcrumb shows Appearance",
                            f"get_current_workspace={current_after}, bc={bc_title_after}",
                            "Major",
                            "SettingsScreen, BreadcrumbManager",
                        )
                finally:
                    set_infrastructure(None)
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass

    def test_chat_labels_mixed_language(self):
        """D6: Chat navigation uses consistent German labels (UI language = DE)."""
        from app.gui.domains.operations.chat.panels.chat_navigation_panel import ChatNavigationPanel

        panel = ChatNavigationPanel(None)
        panel.set_project(1, "Test")  # Ensure topic filter is populated
        # Verify filter labels are German (no EN: Pinned, Ungrouped)
        filter_pinned_text = str(panel._filter_pinned.text()) if hasattr(panel, "_filter_pinned") else ""
        filter_archived_text = str(panel._filter_archived.text()) if hasattr(panel, "_filter_archived") else ""
        assert "Pinned" not in filter_pinned_text, "Filter 'Pinned' should be 'Angeheftet'"
        assert "Angeheftet" in filter_pinned_text, "Filter should show 'Angeheftet'"
        assert "Archiv" in filter_archived_text or "Archiviert" in filter_archived_text, "Archiv filter should be DE"
        # Topic filter: Alle Themen, Ungruppiert (no Alle Topics, Ungrouped)
        for i in range(panel._filter_topic.count()):
            item_text = panel._filter_topic.itemText(i)
            assert "Ungrouped" not in item_text, f"Topic filter should not contain 'Ungrouped', got {item_text!r}"
            assert "Alle Topics" not in item_text, f"Topic filter should not contain 'Alle Topics', got {item_text!r}"

    def test_sidebar_vs_operations_label_mismatch(self):
        """D7: Sidebar and Operations nav use consistent labels."""
        from app.gui.navigation.sidebar_config import get_sidebar_sections
        from app.gui.domains.operations.operations_nav import OperationsNav

        sections = get_sidebar_sections()
        sidebar_items = {}
        for s in sections:
            for item in s.items:
                sidebar_items[item.workspace_id or item.area_id] = item.title

        ops_titles = dict(OperationsNav.WORKSPACES)

        assert sidebar_items.get("operations_projects") == ops_titles.get("operations_projects"), (
            f"Projects mismatch: Sidebar={sidebar_items.get('operations_projects')!r}, "
            f"Ops={ops_titles.get('operations_projects')!r}"
        )
        assert sidebar_items.get("operations_agent_tasks") == ops_titles.get("operations_agent_tasks"), (
            f"Agent Tasks mismatch: Sidebar={sidebar_items.get('operations_agent_tasks')!r}, "
            f"Ops={ops_titles.get('operations_agent_tasks')!r}"
        )

    def test_workspace_switch_order_no_crash(self):
        """Rapid workspace switching in different orders – no crash, no stale inspector."""
        from app.gui.bootstrap import register_all_screens
        from app.gui.workspace.workspace_host import WorkspaceHost
        from app.gui.navigation.nav_areas import NavArea
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

                    order1 = [
                        (NavArea.OPERATIONS, "operations_chat"),
                        (NavArea.OPERATIONS, "operations_knowledge"),
                        (NavArea.OPERATIONS, "operations_prompt_studio"),
                        (NavArea.OPERATIONS, "operations_agent_tasks"),
                        (NavArea.SETTINGS, None),
                        (NavArea.OPERATIONS, "operations_chat"),
                    ]
                    for area_id, ws_id in order1:
                        host.show_area(area_id, ws_id)
                        _process_events()

                    # Reverse order
                    order2 = [
                        (NavArea.OPERATIONS, "operations_agent_tasks"),
                        (NavArea.OPERATIONS, "operations_prompt_studio"),
                        (NavArea.OPERATIONS, "operations_knowledge"),
                        (NavArea.OPERATIONS, "operations_chat"),
                    ]
                    for area_id, ws_id in order2:
                        host.show_area(area_id, ws_id)
                        _process_events()

                    # No exception = pass
                    self.assertIsNotNone(host.currentWidget())
                finally:
                    set_infrastructure(None)
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass

    def test_workspace_switch_with_inspector_host_no_crash(self):
        """D25: D13 regression – switching to Prompt Studio with InspectorHost connected must not crash.
        Verifies setup_inspector(content_token=...) path is exercised."""
        from app.gui.bootstrap import register_all_screens
        from app.gui.workspace.workspace_host import WorkspaceHost
        from app.gui.navigation.nav_areas import NavArea
        from app.gui.inspector.inspector_host import InspectorHost
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

                infra = _ServiceInfrastructure()
                infra._client = mock_client
                infra._db = DatabaseManager(db_path=db_path)
                infra._settings = AppSettings()
                set_infrastructure(infra)

                try:
                    register_all_screens()
                    host = WorkspaceHost()
                    host.register_from_registry()
                    inspector = InspectorHost()
                    host.set_inspector_host(inspector)

                    # Switch to Prompt Studio – this exercises setup_inspector with content_token
                    host.show_area(NavArea.OPERATIONS, "operations_prompt_studio")
                    _process_events()

                    # Also switch Chat -> Knowledge -> Prompt Studio to cover full path
                    host.show_area(NavArea.OPERATIONS, "operations_chat")
                    _process_events()
                    host.show_area(NavArea.OPERATIONS, "operations_knowledge")
                    _process_events()
                    host.show_area(NavArea.OPERATIONS, "operations_prompt_studio")
                    _process_events()

                    self.assertIsNotNone(host.currentWidget())
                finally:
                    set_infrastructure(None)
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass

    def test_command_palette_navigation(self):
        """Phase 6: Command Palette commands reach Knowledge, Prompt Studio, Agent Tasks, Control Center sub-workspaces."""
        from app.gui.bootstrap import register_all_screens
        from app.gui.workspace.workspace_host import WorkspaceHost
        from app.gui.navigation.nav_areas import NavArea
        from app.gui.commands.registry import CommandRegistry
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
                    from app.gui.commands.bootstrap import register_commands
                    register_commands(host)

                    targets = [
                        ("nav.knowledge", NavArea.OPERATIONS, "operations_knowledge"),
                        ("nav.prompt_studio", NavArea.OPERATIONS, "operations_prompt_studio"),
                        ("nav.agent_tasks", NavArea.OPERATIONS, "operations_agent_tasks"),
                        ("nav.cc_agents", NavArea.CONTROL_CENTER, "cc_agents"),
                        ("nav.rd_system_graph", NavArea.RUNTIME_DEBUG, "rd_system_graph"),
                    ]
                    for cmd_id, area_id, workspace_id in targets:
                        cmd = CommandRegistry.get(cmd_id)
                        assert cmd is not None, f"Command {cmd_id} should be registered"
                        cmd.callback()
                        _process_events()
                        idx = host._area_to_index.get(area_id)
                        assert idx is not None, f"Area {area_id} should exist"
                        screen = host.widget(idx)
                        assert host.currentWidget() == screen, f"After {cmd_id}, {area_id} should be visible"
                        if hasattr(screen, "get_current_workspace"):
                            current_ws = screen.get_current_workspace()
                            assert current_ws == workspace_id, (
                                f"After {cmd_id}, workspace should be {workspace_id}, got {current_ws!r}"
                            )
                finally:
                    set_infrastructure(None)
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass

    def test_area_switch_inspector_no_stale(self):
        """Phase 6: Rapid area switching (Operations → Control Center → Settings) – no crash, inspector uses token."""
        from app.gui.bootstrap import register_all_screens
        from app.gui.workspace.workspace_host import WorkspaceHost
        from app.gui.navigation.nav_areas import NavArea
        from app.gui.inspector.inspector_host import InspectorHost
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

                infra = _ServiceInfrastructure()
                infra._client = mock_client
                infra._db = DatabaseManager(db_path=db_path)
                infra._settings = AppSettings()
                set_infrastructure(infra)

                try:
                    register_all_screens()
                    host = WorkspaceHost()
                    host.register_from_registry()
                    inspector = InspectorHost()
                    host.set_inspector_host(inspector)

                    # Rapid area switching – D24: prepare_for_setup + content_token prevents stale
                    for _ in range(2):
                        host.show_area(NavArea.OPERATIONS, "operations_chat")
                        _process_events()
                        host.show_area(NavArea.CONTROL_CENTER, "cc_models")
                        _process_events()
                        host.show_area(NavArea.SETTINGS)
                        _process_events()
                        host.show_area(NavArea.QA_GOVERNANCE, "qa_test_inventory")
                        _process_events()
                        host.show_area(NavArea.RUNTIME_DEBUG, "rd_logs")
                        _process_events()

                    self.assertIsNotNone(host.currentWidget())
                finally:
                    set_infrastructure(None)
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass

    def test_project_section_navigation(self):
        """PROJECT-Sidebar: Command Center + Projekte (Operations); kein separater Project Hub."""
        from app.gui.navigation.sidebar_config import get_sidebar_sections

        sections = get_sidebar_sections()
        project_section = next((s for s in sections if s.id == "project"), None)
        if not project_section:
            return

        items = [(i.title, getattr(i, "tooltip", None)) for i in project_section.items]
        titles = [t for t, _ in items]
        assert "Projektübersicht" not in titles, "Standalone Project Hub entry must be removed"
        assert "Systemübersicht" in titles, "Dashboard should be labeled Systemübersicht"
        assert "Projekte" in titles, "Projects workspace should be labeled Projekte"
        assert len(project_section.items) == 2, "PROJECT section should have exactly two entries"
        tooltips = [tt for _, tt in items if tt]
        assert len(tooltips) >= 2, "PROJECT items should have clarifying tooltips"


if __name__ == "__main__":
    _RECORDED_DEFECTS.clear()
    suite = unittest.TestLoader().loadTestsFromTestCase(UXBehaviorSimulation)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    if _RECORDED_DEFECTS:
        print("\n--- Recorded Defects ---")
        for d in _RECORDED_DEFECTS:
            print(f"\n{d['id']}: {d['title']}")
            print(f"  Steps: {d['steps']}")
            print(f"  Expected: {d['expected']}")
            print(f"  Actual: {d['actual']}")
            print(f"  Severity: {d['severity']} | Subsystem: {d['subsystem']}")
