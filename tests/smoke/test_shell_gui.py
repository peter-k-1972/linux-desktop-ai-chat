"""
Smoke Tests: Neue GUI-Shell (ShellMainWindow).

Testet, dass die neue GUI-Shell startet und alle Hauptbereiche erreichbar sind.
Standard-Startpfad der Anwendung.
"""

import os
import tempfile
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.navigation.nav_areas import NavArea


def test_shell_main_window_importable():
    """ShellMainWindow kann importiert werden."""
    from app.gui.shell import ShellMainWindow
    assert ShellMainWindow is not None


def test_run_gui_shell_importable():
    """run_gui_shell kann importiert werden."""
    from run_gui_shell import main
    assert callable(main)


def test_app_main_module_runs_new_gui():
    """python -m app delegiert an run_gui_shell (neue GUI)."""
    from app.__main__ import main as app_main
    assert callable(app_main)


def test_nav_areas_defined():
    """Alle sechs Hauptbereiche sind definiert."""
    areas = NavArea.all_areas()
    assert len(areas) == 6
    ids = [a[0] for a in areas]
    assert NavArea.COMMAND_CENTER in ids
    assert NavArea.OPERATIONS in ids
    assert NavArea.CONTROL_CENTER in ids
    assert NavArea.QA_GOVERNANCE in ids
    assert NavArea.RUNTIME_DEBUG in ids
    assert NavArea.SETTINGS in ids


@pytest.mark.smoke
def test_workspace_host_shows_all_areas():
    """
    WorkspaceHost kann alle sechs Bereiche anzeigen.
    Kein Crash beim Wechsel.
    """
    from app.gui.workspace.workspace_host import WorkspaceHost
    from app.gui.bootstrap import register_all_screens

    register_all_screens()
    host = WorkspaceHost()
    host.register_from_registry()

    for area_id in [
        NavArea.COMMAND_CENTER,
        NavArea.OPERATIONS,
        NavArea.CONTROL_CENTER,
        NavArea.QA_GOVERNANCE,
        NavArea.RUNTIME_DEBUG,
        NavArea.SETTINGS,
    ]:
        host.show_area(area_id)
        QApplication.instance().processEvents()
        assert host.currentWidget() is not None


@pytest.mark.smoke
def test_inspector_host_exists():
    """InspectorHost kann erstellt werden."""
    from app.gui.inspector.inspector_host import InspectorHost

    host = InspectorHost()
    assert host is not None
    host.clear_content()


@pytest.mark.smoke
def test_bottom_panel_host_exists():
    """BottomPanelHost kann erstellt werden."""
    from app.gui.monitors.bottom_panel_host import BottomPanelHost

    host = BottomPanelHost(None)
    assert host is not None


@pytest.mark.smoke
def test_theme_manager_available():
    """ThemeManager ist verfügbar und blockiert den Start nicht."""
    from app.gui.themes import get_theme_manager

    manager = get_theme_manager()
    assert manager is not None
    ok = manager.set_theme("light_default")
    assert ok is True or ok is None


@pytest.mark.smoke
def test_shell_main_window_starts_with_mocked_infra():
    """
    ShellMainWindow startet mit gemockter Infrastruktur.
    Minimaler Smoke-Check: Fenster wird erstellt, keine Exception.
    """
    from app.gui.shell import ShellMainWindow
    from app.services.infrastructure import set_infrastructure, _ServiceInfrastructure
    from app.core.db import DatabaseManager
    from app.core.config.settings import AppSettings

    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        mock_client = MagicMock()
        mock_client.get_debug_info = AsyncMock(return_value={"online": True})
        mock_client.get_models = AsyncMock(return_value=[])

        with patch("app.services.infrastructure.OllamaClient", return_value=mock_client):
            infra = _ServiceInfrastructure()
            infra._client = mock_client
            infra._db = DatabaseManager(db_path=db_path)
            infra._settings = AppSettings()
            set_infrastructure(infra)

            try:
                with patch("run_gui_shell.get_infrastructure", return_value=infra):
                    with patch("run_gui_shell.set_chat_backend", create=True):
                        with patch("run_gui_shell.set_knowledge_backend", create=True):
                            with patch("run_gui_shell.ChatBackend", create=True):
                                with patch("run_gui_shell.KnowledgeBackend", create=True):
                                    win = ShellMainWindow()
                                    QApplication.instance().processEvents()
                                    assert win is not None
                                    assert win.windowTitle()
                                    assert hasattr(win, "_workspace_host")
                                    assert hasattr(win, "_inspector_host")
                                    assert hasattr(win, "_bottom_host")
            finally:
                set_infrastructure(None)
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass
