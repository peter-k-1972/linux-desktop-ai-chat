"""
DockingConfig – Einziger Ort für QDockWidget-Konfiguration.

Erstellt Docks für Navigation, Inspector, Bottom Panel.
"""

from PySide6.QtWidgets import QMainWindow, QDockWidget
from PySide6.QtCore import Qt

from app.gui.shell.layout_constants import (
    NAV_SIDEBAR_WIDTH,
    INSPECTOR_WIDTH,
    BOTTOM_PANEL_HEIGHT,
)
from app.gui.navigation import NavigationSidebar
from app.gui.inspector import InspectorHost
from app.gui.monitors import BottomPanelHost


def setup_docks(main_window: QMainWindow) -> dict:
    """
    Richtet alle Docks ein. Gibt Referenzen zurück.

    Returns:
        dict mit Keys: nav_dock, nav_sidebar, inspector_dock, inspector_host,
        bottom_dock, bottom_host
    """
    result = {}

    # Navigation Sidebar (links)
    nav_sidebar = NavigationSidebar(main_window)
    nav_dock = QDockWidget("Navigation", main_window)
    nav_dock.setObjectName("navDock")
    nav_dock.setWidget(nav_sidebar)
    nav_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
    nav_dock.setFeatures(
        QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable
    )
    main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, nav_dock)
    nav_dock.setMinimumWidth(NAV_SIDEBAR_WIDTH)
    result["nav_dock"] = nav_dock
    result["nav_sidebar"] = nav_sidebar

    # Inspector (rechts)
    inspector_host = InspectorHost(main_window)
    inspector_dock = QDockWidget("Inspektor", main_window)
    inspector_dock.setObjectName("inspectorDock")
    inspector_dock.setWidget(inspector_host)
    inspector_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
    inspector_dock.setFeatures(
        QDockWidget.DockWidgetFeature.DockWidgetMovable
        | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        | QDockWidget.DockWidgetFeature.DockWidgetClosable
    )
    main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, inspector_dock)
    inspector_dock.setMinimumWidth(INSPECTOR_WIDTH)
    result["inspector_dock"] = inspector_dock
    result["inspector_host"] = inspector_host

    # Bottom Panel
    bottom_host = BottomPanelHost(main_window)
    bottom_dock = QDockWidget("Monitor", main_window)
    bottom_dock.setObjectName("bottomDock")
    bottom_dock.setWidget(bottom_host)
    bottom_dock.setAllowedAreas(Qt.DockWidgetArea.TopDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)
    bottom_dock.setFeatures(
        QDockWidget.DockWidgetFeature.DockWidgetMovable
        | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        | QDockWidget.DockWidgetFeature.DockWidgetClosable
    )
    main_window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)
    bottom_dock.setMinimumHeight(BOTTOM_PANEL_HEIGHT)
    result["bottom_dock"] = bottom_dock
    result["bottom_host"] = bottom_host

    return result
