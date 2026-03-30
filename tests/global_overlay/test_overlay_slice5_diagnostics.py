"""Slice 5: Overlay diagnostics, capabilities summary, focus / Escape, smoke."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget

from app.global_overlay.overlay_diagnostics import (
    collect_overlay_diagnostics,
    format_diagnostics_rich_html,
)
from app.global_overlay.overlay_dialogs import EmergencyOverlayDialog, StandardOverlayDialog
from app.global_overlay import detach_global_overlay_host
from app.global_overlay.overlay_host import GlobalOverlayHost, install_global_overlay_host
from app.core.startup_contract import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML
@pytest.fixture(autouse=True)
def _detach_overlay_host(qapplication):
    yield
    detach_global_overlay_host(qapplication)
    QApplication.processEvents()


def test_diagnostics_default_widget_versions_and_safe_mode(qapplication):
    d = collect_overlay_diagnostics(GUI_ID_DEFAULT_WIDGET)
    assert d.active_gui_id == GUI_ID_DEFAULT_WIDGET
    assert d.app_release_version
    assert d.backend_bundle_version
    assert d.contracts_version
    assert d.bridge_version
    assert d.fallback_gui_id == GUI_ID_DEFAULT_WIDGET
    assert d.safe_mode_next_launch in ("yes", "no", "unavailable")
    assert "widget gui" in d.manifest_short_status.lower()
    assert d.release_status == "unavailable"
    html = format_diagnostics_rich_html(d)
    assert "Alt+Z" in html and "Esc" in html


def test_diagnostics_qml_manifest_release_when_present(qapplication):
    d = collect_overlay_diagnostics(GUI_ID_LIBRARY_QML)
    assert d.active_gui_id == GUI_ID_LIBRARY_QML
    assert d.release_status != ""  # manifest field or unavailable
    assert "theme_manifest" in d.manifest_short_status.lower() or "issue" in d.manifest_short_status.lower()


def test_diagnostics_unavailable_gui_switching_reflects_snapshot(qapplication, monkeypatch):
    def _snap(gid: str):
        from app.global_overlay.overlay_gui_port import build_gui_overlay_snapshot

        base = build_gui_overlay_snapshot(gid)
        from dataclasses import replace

        return replace(base, gui_switching_available=False, gui_switching_block_reason="launcher missing (test)")

    monkeypatch.setattr("app.global_overlay.overlay_diagnostics.build_gui_overlay_snapshot", _snap)
    d = collect_overlay_diagnostics(GUI_ID_DEFAULT_WIDGET)
    assert d.gui_switching_support.startswith("no")


def test_capability_summary_matches_registry_widget(qapplication):
    d = collect_overlay_diagnostics(GUI_ID_DEFAULT_WIDGET)
    cap = {k: v for k, v in d.capability_rows}
    assert cap.get("chat") == "yes"
    assert cap.get("theme switching") == "yes"
    assert "global overlay" not in cap
    assert d.global_overlay_product_status in ("active (this session)", "not loaded")


def test_capability_summary_qml_blocks_theme_switching(qapplication):
    d = collect_overlay_diagnostics(GUI_ID_LIBRARY_QML)
    cap = {k: v for k, v in d.capability_rows}
    assert cap.get("theme switching") == "no"


def test_standard_overlay_escape_closes(qapplication):
    dlg = StandardOverlayDialog(None, active_gui_id=GUI_ID_DEFAULT_WIDGET)
    dlg.show()
    QApplication.processEvents()
    assert dlg.isVisible()
    QTest.keyClick(dlg, Qt.Key.Key_Escape)
    QApplication.processEvents()
    assert not dlg.isVisible()


def test_emergency_overlay_escape_closes(qapplication):
    dlg = EmergencyOverlayDialog(None, active_gui_id=GUI_ID_DEFAULT_WIDGET)
    dlg.show()
    QApplication.processEvents()
    QTest.keyClick(dlg, Qt.Key.Key_Escape)
    QApplication.processEvents()
    assert not dlg.isVisible()


def test_smoke_standard_overlay_diagnostics_section(qapplication):
    dlg = StandardOverlayDialog(None, active_gui_id=GUI_ID_DEFAULT_WIDGET)
    dlg.refresh_content()
    assert dlg._diag_group.title() == "Diagnostics"
    assert "Diagnostics" in dlg._diag_body.text()
    assert dlg._intro.text()
    dlg.close()


def test_smoke_emergency_overlay_refresh_stable(qapplication):
    dlg = EmergencyOverlayDialog(None, active_gui_id=GUI_ID_DEFAULT_WIDGET)
    dlg.refresh_content()
    assert dlg._emergency_revert_btn
    assert "GUI" in dlg._detail.text()
    dlg.close()


def test_host_toggle_normal_then_emergency_excludes_each_other(qapplication):
    win = QWidget()
    win.show()
    QApplication.processEvents()
    host = install_global_overlay_host(
        qapplication, active_gui_id=GUI_ID_DEFAULT_WIDGET, primary_window=win
    )
    assert isinstance(host, GlobalOverlayHost)
    host._on_toggle_normal()
    QApplication.processEvents()
    assert host.controller.normal_visible is True
    host._on_toggle_emergency()
    QApplication.processEvents()
    assert host.controller.emergency_visible is True
    assert host.controller.normal_visible is False
    host.close_all_overlays()
