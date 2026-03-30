"""Slice 3: Preset-Zustand, Persistenz, Aktivierung (ohne GUI/Theme-Orchestrierung)."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings

from app.core.startup_contract import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML
from app.workspace_presets.preset_activation import (
    WorkspacePresetActivationStatus,
    apply_workspace_preset_activation,
    evaluate_workspace_preset_activation,
    get_active_workspace_preset_id,
)
from app.workspace_presets.preset_registry import PRESET_ID_CHAT_FOCUS, PRESET_ID_WORKFLOW_STUDIO
from app.workspace_presets.preset_restart_boundaries import PresetEffectCategory
from app.workspace_presets.preset_state import (
    read_full_effect_pending_restart,
    read_preferred_start_domain_from_storage,
    read_raw_active_workspace_preset_id_from_storage,
    resolve_valid_active_workspace_preset_id,
)


@pytest.fixture(autouse=True)
def _isolated_workspace_preset_storage(tmp_path, monkeypatch):
    p = tmp_path / "wp_slice3.ini"
    store = QSettings(str(p), QSettings.IniFormat)
    monkeypatch.setattr("app.workspace_presets.preset_state._qs", lambda: store)
    monkeypatch.setattr("app.core.startup_contract.product_qsettings", lambda: store)
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


def test_default_active_preset_without_storage_key():
    assert read_raw_active_workspace_preset_id_from_storage() == ""
    assert resolve_valid_active_workspace_preset_id() == PRESET_ID_CHAT_FOCUS


def test_apply_persists_bundle_and_start_domain():
    r = apply_workspace_preset_activation(
        PRESET_ID_WORKFLOW_STUDIO,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="workbench",
    )
    assert r.ok
    assert r.active_preset_id == PRESET_ID_WORKFLOW_STUDIO
    assert read_raw_active_workspace_preset_id_from_storage() == PRESET_ID_WORKFLOW_STUDIO
    assert read_preferred_start_domain_from_storage() == "operations_workflows"
    assert get_active_workspace_preset_id() == PRESET_ID_WORKFLOW_STUDIO
    assert r.boundary_report is not None
    assert read_full_effect_pending_restart() == r.boundary_report.overall_requires_restart


def test_evaluate_does_not_persist():
    assert read_raw_active_workspace_preset_id_from_storage() == ""
    ev = evaluate_workspace_preset_activation(
        PRESET_ID_WORKFLOW_STUDIO,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    assert ev.ok
    assert ev.boundary_report is not None
    assert read_raw_active_workspace_preset_id_from_storage() == ""


def test_restart_flag_when_gui_mismatches():
    r = evaluate_workspace_preset_activation(
        PRESET_ID_CHAT_FOCUS,
        running_gui_id=GUI_ID_LIBRARY_QML,
        running_theme_id="light_default",
    )
    assert r.ok
    assert r.boundary_report is not None
    assert r.boundary_report.overall_requires_restart is True
    assert r.restart_required_for_full_effect is True
    assert r.status == WorkspacePresetActivationStatus.ACCEPTED_PENDING_RESTART
    gui_entries = [e for e in r.boundary_report.entries if e.field_name == "gui_id"]
    assert gui_entries and gui_entries[0].category == PresetEffectCategory.RESTART_REQUIRED


def test_invalid_stored_id_fail_closed_rewrites_default():
    from app.workspace_presets import preset_state as ps

    qs = ps._qs()
    qs.setValue("active_workspace_preset_id", "totally_unknown_preset")
    qs.sync()
    resolved = resolve_valid_active_workspace_preset_id()
    assert resolved == PRESET_ID_CHAT_FOCUS
    assert read_raw_active_workspace_preset_id_from_storage() == PRESET_ID_CHAT_FOCUS


def test_safe_mode_watchdog_blocks_activation(monkeypatch):
    monkeypatch.setattr(
        "app.workspace_presets.preset_activation.read_safe_mode_watchdog_banner",
        lambda: True,
    )
    r = apply_workspace_preset_activation(
        PRESET_ID_WORKFLOW_STUDIO,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    assert not r.ok
    assert r.status == WorkspacePresetActivationStatus.REJECTED
    assert read_raw_active_workspace_preset_id_from_storage() == ""
