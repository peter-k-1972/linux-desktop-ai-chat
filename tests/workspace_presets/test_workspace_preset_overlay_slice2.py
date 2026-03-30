"""Slice 2–3: Overlay-Preset-Port (Snapshot, UI-Smoke) mit isoliertem QSettings."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings

from app.global_overlay.overlay_dialogs import EmergencyOverlayDialog, StandardOverlayDialog
from app.core.startup_contract import GUI_ID_DEFAULT_WIDGET
from app.workspace_presets.preset_models import PresetReleaseStatus, WorkspacePreset
from app.workspace_presets.preset_registry import PRESET_ID_CHAT_FOCUS, canonical_workspace_preset_ids
from app.workspace_presets.workspace_preset_port import (
    build_active_workspace_preset_boundary_report_for_overlay,
    build_workspace_preset_overlay_snapshot,
    format_workspace_preset_detail_rich_html,
    get_workspace_preset,
    list_selectable_presets_for_overlay,
    request_preset_activation,
)


@pytest.fixture(autouse=True)
def _isolated_workspace_preset_storage(tmp_path, monkeypatch):
    p = tmp_path / "workspace_presets.ini"
    store = QSettings(str(p), QSettings.IniFormat)
    monkeypatch.setattr("app.workspace_presets.preset_state._qs", lambda: store)
    monkeypatch.setattr("app.core.startup_contract.product_qsettings", lambda: store)
    yield store


@pytest.fixture(autouse=True)
def _no_safe_mode_for_preset_activation(monkeypatch):
    monkeypatch.setattr(
        "app.workspace_presets.preset_activation.read_safe_mode_watchdog_banner",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.workspace_presets.preset_activation.read_safe_mode_next_launch_pending",
        lambda: False,
    )


def _snap():
    build_active_workspace_preset_boundary_report_for_overlay(
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    return build_workspace_preset_overlay_snapshot(
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )


def test_overlay_snapshot_default_matches_registry_default():
    snap = _snap()
    assert snap.registry_default_preset_id == PRESET_ID_CHAT_FOCUS
    assert snap.effective_preset_id == snap.registry_default_preset_id
    assert snap.session_override_active is False
    assert snap.safe_mode_runtime_override_active is False


def test_selectable_presets_are_approved_only_and_cover_canonical():
    sel = list_selectable_presets_for_overlay()
    ids = {p.preset_id for p in sel}
    for pid in canonical_workspace_preset_ids():
        assert pid in ids
    assert all(p.release_status == PresetReleaseStatus.APPROVED for p in sel)


def test_activation_persists_preset_id():
    target = "workflow_studio"
    r = request_preset_activation(
        target,
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    assert r.ok
    assert r.active_preset_id == target
    snap = _snap()
    assert snap.effective_preset_id == target


def test_activation_unknown_preset_fails():
    r = request_preset_activation(
        "no_such_preset_xyz",
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    assert not r.ok
    assert r.status.value == "rejected"


def test_activation_rejects_non_approved(monkeypatch):
    draft = WorkspacePreset(
        preset_id="draft_only_test",
        display_name="Draft",
        description="Test draft",
        gui_id=GUI_ID_DEFAULT_WIDGET,
        theme_id="light_default",
        start_domain="operations_chat",
        requires_restart=False,
        release_status=PresetReleaseStatus.DRAFT,
        compatible_app_versions=("0.9.1",),
    )

    def _fake_get(_pid: str) -> WorkspacePreset:
        return draft

    monkeypatch.setattr("app.workspace_presets.preset_activation.get_workspace_preset", _fake_get)
    r = request_preset_activation(
        "draft_only_test",
        running_gui_id=GUI_ID_DEFAULT_WIDGET,
        running_theme_id="light_default",
    )
    assert not r.ok
    assert "approved" in r.message.lower()


def test_preset_detail_html_contains_core_fields():
    p = get_workspace_preset(PRESET_ID_CHAT_FOCUS)
    html_out = format_workspace_preset_detail_rich_html(p)
    assert PRESET_ID_CHAT_FOCUS in html_out
    assert "gui_id" in html_out
    assert p.gui_id in html_out


def test_standard_overlay_preset_section_populated(qapplication):
    dlg = StandardOverlayDialog(None, active_gui_id=GUI_ID_DEFAULT_WIDGET)
    dlg.refresh_content()
    assert dlg._preset_group.title() == "Workspace Presets"
    assert dlg._preset_combo.count() == len(canonical_workspace_preset_ids())
    assert "Slice 5" in dlg._preset_slice_hint.text()


def test_emergency_overlay_has_no_preset_workspace_controls(qapplication):
    dlg = EmergencyOverlayDialog(None, active_gui_id=GUI_ID_DEFAULT_WIDGET)
    assert not hasattr(dlg, "_preset_group")
