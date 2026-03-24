"""Slice 4: Restart-Grenzen, BoundaryReport, Pending-Marker, Safe-Mode-Klassifikation."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings

from app.gui_registry import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML
from app.workspace_presets.preset_registry import PRESET_ID_CHAT_FOCUS, get_workspace_preset
from app.workspace_presets.preset_restart_boundaries import (
    PresetEffectCategory,
    build_workspace_preset_boundary_report,
    format_workspace_preset_boundary_report_rich_html,
    list_entries_by_category,
)
from app.workspace_presets.preset_state import read_full_effect_pending_restart
from app.workspace_presets.workspace_preset_port import (
    build_active_workspace_preset_boundary_report_for_overlay,
    request_preset_activation,
)


@pytest.fixture(autouse=True)
def _isolated_workspace_preset_storage(tmp_path, monkeypatch):
    p = tmp_path / "wp_slice4.ini"
    store = QSettings(str(p), QSettings.IniFormat)
    monkeypatch.setattr("app.workspace_presets.preset_state._qs", lambda: store)
    monkeypatch.setattr("app.gui_bootstrap.product_qsettings", lambda: store)
    yield store


@pytest.fixture(autouse=True)
def _no_safe_mode(monkeypatch):
    monkeypatch.setattr(
        "app.workspace_presets.preset_restart_boundaries.read_safe_mode_watchdog_banner",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.workspace_presets.preset_restart_boundaries.read_safe_mode_next_launch_pending",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.workspace_presets.preset_activation.read_safe_mode_watchdog_banner",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.workspace_presets.preset_activation.read_safe_mode_next_launch_pending",
        lambda: False,
    )


def test_gui_id_restart_when_shell_differs():
    p = get_workspace_preset(PRESET_ID_CHAT_FOCUS)
    r = build_workspace_preset_boundary_report(
        p,
        running_gui_id=GUI_ID_LIBRARY_QML,
        running_theme_id="light_default",
        safe_mode_runtime_override=False,
    )
    gui = next(e for e in r.entries if e.field_name == "gui_id")
    assert gui.category == PresetEffectCategory.RESTART_REQUIRED
    assert r.overall_requires_restart is True


def test_theme_restart_when_no_runtime_switch_cap():
    p = get_workspace_preset(PRESET_ID_CHAT_FOCUS)
    r = build_workspace_preset_boundary_report(
        p,
        running_gui_id=GUI_ID_LIBRARY_QML,
        running_theme_id="light_default",
        safe_mode_runtime_override=False,
    )
    # gui already restart; theme also restart_required (QML)
    th = next(e for e in r.entries if e.field_name == "theme_id")
    assert th.category == PresetEffectCategory.RESTART_REQUIRED


def test_layout_mode_unsupported():
    p = get_workspace_preset(PRESET_ID_CHAT_FOCUS)
    r = build_workspace_preset_boundary_report(
        p,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
        safe_mode_runtime_override=False,
    )
    lo = next(e for e in r.entries if e.field_name == "layout_mode")
    assert lo.category == PresetEffectCategory.UNSUPPORTED


def test_overlay_mode_context_immediate():
    p = get_workspace_preset(PRESET_ID_CHAT_FOCUS)
    r = build_workspace_preset_boundary_report(
        p,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
        safe_mode_runtime_override=False,
    )
    im = list_entries_by_category(r, PresetEffectCategory.IMMEDIATE)
    names = {e.field_name for e in im}
    assert "overlay_mode" in names and "context_profile" in names


def test_safe_mode_ignores_gui_theme():
    p = get_workspace_preset(PRESET_ID_CHAT_FOCUS)
    r = build_workspace_preset_boundary_report(
        p,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
        safe_mode_runtime_override=True,
    )
    assert r.safe_mode_runtime_override_active is True
    g = next(e for e in r.entries if e.field_name == "gui_id")
    t = next(e for e in r.entries if e.field_name == "theme_id")
    assert g.category == PresetEffectCategory.IGNORED_IN_SAFE_MODE
    assert t.category == PresetEffectCategory.IGNORED_IN_SAFE_MODE


def test_boundary_html_contains_sections():
    p = get_workspace_preset(PRESET_ID_CHAT_FOCUS)
    r = build_workspace_preset_boundary_report(
        p,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
        safe_mode_runtime_override=False,
    )
    html_out = format_workspace_preset_boundary_report_rich_html(r)
    assert "Overall" in html_out
    assert "Immediate" in html_out


def test_pending_marker_updates_after_resync():
    r = request_preset_activation(
        PRESET_ID_CHAT_FOCUS,
        running_gui_id=GUI_ID_LIBRARY_QML,
        running_theme_id="light_default",
    )
    assert r.ok
    assert read_full_effect_pending_restart() is True

    build_active_workspace_preset_boundary_report_for_overlay(
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    assert read_full_effect_pending_restart() is False
