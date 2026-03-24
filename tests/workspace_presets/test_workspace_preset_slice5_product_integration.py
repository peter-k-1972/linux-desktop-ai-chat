"""Slice 5: Produktstart, Navigation, Kompatibilität, Safe-Mode-Grenzen."""

from __future__ import annotations

import logging

import pytest
from PySide6.QtCore import QSettings

from app.core.navigation.navigation_registry import get_entry
from app.gui.navigation.nav_areas import NavArea
from app.gui_registry import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML
from app.gui_bootstrap import read_preferred_gui_id_from_qsettings
from app.workspace_presets.preset_activation import (
    WorkspacePresetActivationStatus,
    apply_workspace_preset_activation,
    evaluate_workspace_preset_activation,
)
from app.workspace_presets.preset_compatibility import (
    FALLBACK_START_DOMAIN_ID,
    build_workspace_preset_compatibility_report,
)
from app.workspace_presets.preset_registry import PRESET_ID_CHAT_FOCUS, PRESET_ID_WORKFLOW_STUDIO
from app.workspace_presets.preset_restart_boundaries import build_workspace_preset_boundary_report
from app.workspace_presets.preset_startup import (
    resolve_shell_startup_navigation_targets,
    sync_workspace_preset_preferences_before_gui_resolution,
)


@pytest.fixture(autouse=True)
def _isolated_workspace_preset_storage(tmp_path, monkeypatch):
    p = tmp_path / "wp_slice5.ini"
    store = QSettings(str(p), QSettings.IniFormat)
    monkeypatch.setattr("app.workspace_presets.preset_state._qs", lambda: store)
    monkeypatch.setattr("app.gui_bootstrap.product_qsettings", lambda: store)
    yield store


@pytest.fixture(autouse=True)
def _no_safe_mode(monkeypatch):
    monkeypatch.setattr(
        "app.workspace_presets.preset_activation.read_safe_mode_watchdog_banner",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.workspace_presets.preset_activation.read_safe_mode_next_launch_pending",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.workspace_presets.preset_restart_boundaries.read_safe_mode_watchdog_banner",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.workspace_presets.preset_restart_boundaries.read_safe_mode_next_launch_pending",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.workspace_presets.preset_startup.safe_mode_runtime_active",
        lambda: False,
    )


def test_compatibility_report_all_ok_for_canonical_presets():
    from app.workspace_presets.preset_registry import get_workspace_preset

    p = get_workspace_preset(PRESET_ID_WORKFLOW_STUDIO)
    r = build_workspace_preset_compatibility_report(p)
    assert r.activation_allowed
    assert r.fully_compatible
    assert r.effective_start_domain == "operations_workflows"


def test_startup_navigation_matches_preset_start_domain():
    apply_workspace_preset_activation(
        PRESET_ID_WORKFLOW_STUDIO,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="workbench",
    )
    area, ws = resolve_shell_startup_navigation_targets()
    ent = get_entry("operations_workflows")
    assert ent is not None
    assert area == ent.area
    assert ws == ent.workspace


def test_startup_navigation_safe_mode_forces_command_center(monkeypatch):
    monkeypatch.setattr(
        "app.workspace_presets.preset_startup.safe_mode_runtime_active",
        lambda: True,
    )
    area, ws = resolve_shell_startup_navigation_targets()
    assert area == NavArea.COMMAND_CENTER
    assert ws is None


def test_launch_sync_writes_preferred_gui_when_preset_persisted():
    from app.workspace_presets.preset_state import read_raw_active_workspace_preset_id_from_storage

    apply_workspace_preset_activation(
        PRESET_ID_WORKFLOW_STUDIO,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="workbench",
    )
    assert read_raw_active_workspace_preset_id_from_storage() == PRESET_ID_WORKFLOW_STUDIO

    sync_workspace_preset_preferences_before_gui_resolution([])
    assert read_preferred_gui_id_from_qsettings() == "default_widget_gui"


def test_launch_sync_skipped_when_no_stored_preset_id(monkeypatch):
    from unittest.mock import MagicMock

    import app.workspace_presets.preset_state as ps

    spy = MagicMock(side_effect=AssertionError("bundle should not be rewritten"))
    monkeypatch.setattr(ps, "write_active_workspace_preset_bundle_to_storage", spy)
    sync_workspace_preset_preferences_before_gui_resolution([])
    spy.assert_not_called()


def test_evaluate_restart_required_when_running_gui_differs():
    from app.gui_registry import GUI_ID_LIBRARY_QML

    ev = evaluate_workspace_preset_activation(
        PRESET_ID_CHAT_FOCUS,
        running_gui_id=GUI_ID_LIBRARY_QML,
        running_theme_id="light_default",
    )
    assert ev.ok
    assert ev.status == WorkspacePresetActivationStatus.ACCEPTED_PENDING_RESTART
    assert ev.restart_required_for_full_effect is True


def test_activation_rejected_when_gui_unknown(monkeypatch):
    monkeypatch.setattr("app.workspace_presets.preset_compatibility.list_registered_gui_ids", lambda: ())
    r = evaluate_workspace_preset_activation(
        PRESET_ID_CHAT_FOCUS,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    assert not r.ok
    assert r.compatibility_report is not None


def test_domain_fallback_constant_registered():
    assert get_entry(FALLBACK_START_DOMAIN_ID) is not None


def test_sync_theme_env_override_still_writes_preferred_gui_from_preset(monkeypatch):
    """F1: theme override must not skip GUI line from preset."""
    monkeypatch.setenv("LINUX_DESKTOP_CHAT_THEME", "dark_default")
    apply_workspace_preset_activation(
        PRESET_ID_WORKFLOW_STUDIO,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="workbench",
    )
    from app.workspace_presets import preset_state as ps

    qs = ps._qs()
    qs.setValue("preferred_gui", GUI_ID_LIBRARY_QML)
    qs.sync()

    sync_workspace_preset_preferences_before_gui_resolution(["python"])

    assert read_preferred_gui_id_from_qsettings() == GUI_ID_DEFAULT_WIDGET


def test_sync_gui_env_override_still_writes_theme_from_preset(monkeypatch):
    """F1: GUI override must not skip theme persistence from preset."""
    monkeypatch.setenv("LINUX_DESKTOP_CHAT_GUI", "library_qml_gui")
    monkeypatch.delenv("LINUX_DESKTOP_CHAT_THEME", raising=False)

    apply_workspace_preset_activation(
        PRESET_ID_CHAT_FOCUS,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    from app.workspace_presets import preset_state as ps

    qs = ps._qs()
    qs.setValue("theme_id", "workbench")
    qs.setValue("theme", "dark")
    qs.sync()

    sync_workspace_preset_preferences_before_gui_resolution(["python"])

    assert str(qs.value("theme_id", "") or "").strip() == "light_default"


def test_boundary_start_domain_text_widget_shell():
    from app.workspace_presets.preset_registry import get_workspace_preset

    p = get_workspace_preset(PRESET_ID_CHAT_FOCUS)
    r = build_workspace_preset_boundary_report(
        p,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    sd = next(e for e in r.entries if e.field_name == "start_domain")
    assert "Widget shell" in sd.detail


def test_boundary_start_domain_text_qml_shell_when_gui_matches_preset():
    from app.application_release_info import APP_RELEASE_VERSION
    from app.workspace_presets.preset_models import PresetReleaseStatus, WorkspacePreset

    p = WorkspacePreset(
        preset_id="qa_qml_shell_match",
        display_name="QA",
        description="Synthetic row for boundary copy",
        gui_id=GUI_ID_LIBRARY_QML,
        theme_id="light_default",
        start_domain="operations_chat",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=(APP_RELEASE_VERSION,),
    )
    r = build_workspace_preset_boundary_report(
        p,
        running_gui_id=GUI_ID_LIBRARY_QML,
        running_theme_id="light_default",
    )
    sd = next(e for e in r.entries if e.field_name == "start_domain")
    assert "Qt Quick" in sd.detail


def test_main_window_logs_when_preset_navigation_raises(qapplication, caplog, monkeypatch):
    def _boom():
        raise RuntimeError("preset_nav_probe")

    monkeypatch.setattr(
        "app.workspace_presets.preset_startup.resolve_shell_startup_navigation_targets",
        _boom,
    )
    from app.gui.shell.main_window import ShellMainWindow

    mod = ShellMainWindow.__module__
    with caplog.at_level(logging.ERROR, logger=mod):
        win = ShellMainWindow()
    win.close()
    combined = caplog.text
    assert "preset_nav_probe" in combined or "initial navigation" in combined
