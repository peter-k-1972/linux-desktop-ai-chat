"""Slice 1: Global Overlay — Controller, Status, Host, Shortcuts."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QWidget

from app.global_overlay import detach_global_overlay_host
from app.global_overlay.gui_launch_watchdog import (
    reset_watchdog_for_tests,
    get_gui_launch_watchdog_state,
    note_failed_gui_launch,
    note_successful_gui_launch,
    on_app_session_start,
)
from app.global_overlay.overlay_controller import OverlayController
from app.global_overlay.overlay_host import (
    GlobalOverlayHost,
    install_global_overlay_host,
    shortcut_sequences,
)
from app.global_overlay.overlay_models import OverlaySurfaceKind
from app.global_overlay.overlay_status import collect_overlay_status
from app.core.startup_contract import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML


@pytest.fixture(autouse=True)
def _reset_watchdog():
    reset_watchdog_for_tests()
    yield
    reset_watchdog_for_tests()


@pytest.fixture(autouse=True)
def _detach_overlay_host(qapplication):
    yield
    detach_global_overlay_host(qapplication)
    QApplication.processEvents()


def test_overlay_controller_initially_closed():
    c = OverlayController()
    assert c.normal_visible is False
    assert c.emergency_visible is False


def test_overlay_controller_toggle_normal_opens_closes():
    c = OverlayController()
    assert c.toggle_normal_overlay() == OverlaySurfaceKind.NORMAL
    assert c.normal_visible is True
    assert c.toggle_normal_overlay() is None
    assert c.normal_visible is False


def test_overlay_controller_toggle_emergency_opens_closes():
    c = OverlayController()
    assert c.toggle_emergency_overlay() == OverlaySurfaceKind.EMERGENCY
    assert c.emergency_visible is True
    assert c.toggle_emergency_overlay() is None
    assert c.emergency_visible is False


def test_overlay_controller_mutual_exclusion():
    c = OverlayController()
    c.toggle_normal_overlay()
    assert c.normal_visible is True
    c.toggle_emergency_overlay()
    assert c.normal_visible is False
    assert c.emergency_visible is True
    c.toggle_normal_overlay()
    assert c.emergency_visible is False
    assert c.normal_visible is True


def test_overlay_controller_close_all():
    c = OverlayController()
    c.toggle_emergency_overlay()
    c.close_overlay()
    assert c.normal_visible is False
    assert c.emergency_visible is False


def test_shortcut_sequences_match_product_hotkeys():
    n, e = shortcut_sequences()
    assert n == "Alt+Z"
    assert e == "Alt+Shift+Z"


def test_collect_overlay_status_default_widget(qapplication):
    s = collect_overlay_status(GUI_ID_DEFAULT_WIDGET)
    assert s.active_gui_id == GUI_ID_DEFAULT_WIDGET
    assert s.gui_type == "pyside6"
    assert s.app_release_version
    assert s.bridge_interface_version
    assert s.default_fallback_gui_id == GUI_ID_DEFAULT_WIDGET


def test_collect_overlay_status_library_qml(qapplication):
    s = collect_overlay_status(GUI_ID_LIBRARY_QML)
    assert s.active_gui_id == GUI_ID_LIBRARY_QML
    assert s.gui_type == "qt_quick"


def test_watchdog_session_and_counters():
    on_app_session_start()
    st = get_gui_launch_watchdog_state()
    assert st.successful_launch_count == 0
    assert st.consecutive_gui_launch_failures == 0
    note_successful_gui_launch()
    assert st.successful_launch_count == 1
    note_failed_gui_launch()
    assert st.consecutive_gui_launch_failures == 1


def test_global_overlay_host_toggle_and_close(qapplication):
    win = QWidget()
    win.show()
    host = install_global_overlay_host(
        qapplication,
        active_gui_id=GUI_ID_DEFAULT_WIDGET,
        primary_window=win,
    )
    assert isinstance(host, GlobalOverlayHost)
    host.close_all_overlays()
    assert host.controller.normal_visible is False

    host._on_toggle_normal()
    assert host.controller.normal_visible is True
    assert host._normal_dialog is not None
    assert host._normal_dialog.isVisible()

    host._on_toggle_normal()
    assert host.controller.normal_visible is False
    assert not host._normal_dialog.isVisible()

    host._on_toggle_emergency()
    assert host.controller.emergency_visible is True
    host._on_toggle_normal()
    assert host.controller.emergency_visible is False
    assert host.controller.normal_visible is True

    host.close_all_overlays()


def test_global_overlay_host_idempotent_install(qapplication):
    w = QWidget()
    h1 = install_global_overlay_host(
        qapplication, active_gui_id=GUI_ID_DEFAULT_WIDGET, primary_window=w
    )
    h2 = install_global_overlay_host(
        qapplication, active_gui_id=GUI_ID_LIBRARY_QML, primary_window=w
    )
    assert h1 is h2
    assert h2.active_gui_id == GUI_ID_LIBRARY_QML


def test_smoke_overlay_constructible(qapplication):
    """Minimal smoke: Host erzeugen, öffnen, schließen ohne Exception."""
    win = QWidget()
    win.show()
    QApplication.processEvents()
    host = install_global_overlay_host(
        qapplication, active_gui_id=GUI_ID_DEFAULT_WIDGET, primary_window=win
    )
    host._on_toggle_normal()
    QApplication.processEvents()
    host.close_all_overlays()
    QApplication.processEvents()
