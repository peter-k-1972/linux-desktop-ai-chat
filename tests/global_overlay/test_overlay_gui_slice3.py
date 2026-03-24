"""Slice 3: Overlay GUI switching, registry, validation, revert, fail-closed."""

from __future__ import annotations

import pytest

from app.global_overlay.overlay_dialogs import EmergencyOverlayDialog, StandardOverlayDialog
from app.global_overlay.overlay_gui_port import (
    apply_gui_switch_via_product,
    build_gui_overlay_snapshot,
    relaunch_via_run_gui_shell,
    revert_to_default_gui_via_product,
    validate_gui_switch_target,
)
from app.gui_registry import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML, resolve_repo_root
from app.gui_bootstrap import read_preferred_gui_id_from_qsettings, write_preferred_gui_id_to_qsettings


def test_build_gui_snapshot_shows_fallback(qapplication):
    gs = build_gui_overlay_snapshot(GUI_ID_DEFAULT_WIDGET)
    assert gs.active_gui_id == GUI_ID_DEFAULT_WIDGET
    assert gs.default_fallback_gui_id == GUI_ID_DEFAULT_WIDGET
    assert len(gs.registered_entries) >= 2
    ids = {e[0] for e in gs.registered_entries}
    assert GUI_ID_DEFAULT_WIDGET in ids
    assert GUI_ID_LIBRARY_QML in ids


def test_validate_rejects_unknown_gui(qapplication):
    ok, msg = validate_gui_switch_target("totally_unknown_gui_id")
    assert ok is False
    assert "registry" in msg.lower() or "unknown" in msg.lower()


def test_validate_default_widget_ok(qapplication):
    ok, msg = validate_gui_switch_target(GUI_ID_DEFAULT_WIDGET)
    assert ok is True
    assert msg == ""


def test_validate_library_qml_ok_in_repo(qapplication):
    ok, msg = validate_gui_switch_target(GUI_ID_LIBRARY_QML)
    assert ok is True, msg


def test_validate_uses_repo_root_entrypoint(tmp_path):
    ok, msg = validate_gui_switch_target(GUI_ID_DEFAULT_WIDGET, repo_root=tmp_path)
    assert ok is False
    assert "entrypoint" in msg.lower() or "missing" in msg.lower()


def test_validate_qml_fail_closed(monkeypatch, qapplication):
    monkeypatch.setattr(
        "app.qml_alternative_gui_validator.validate_library_qml_gui_launch_context",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("incompatible manifest (test)")),
    )
    ok, msg = validate_gui_switch_target(GUI_ID_LIBRARY_QML)
    assert ok is False
    assert "manifest" in msg.lower() or "failed" in msg.lower() or "incompatible" in msg.lower()


def test_apply_relaunch_failure_reverts_preference(qapplication, monkeypatch):
    write_preferred_gui_id_to_qsettings(GUI_ID_DEFAULT_WIDGET)
    before = read_preferred_gui_id_from_qsettings()

    monkeypatch.setattr(
        "app.global_overlay.overlay_gui_port.relaunch_via_run_gui_shell",
        lambda _gid: False,
    )
    res = apply_gui_switch_via_product(GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML)
    assert res.ok is False
    assert res.relaunch_scheduled is False
    assert read_preferred_gui_id_from_qsettings() == before


def test_apply_same_gui_syncs_no_relaunch(qapplication, monkeypatch):
    monkeypatch.setattr(
        "app.global_overlay.overlay_gui_port.relaunch_via_run_gui_shell",
        lambda _gid: pytest.fail("relaunch should not be called"),
    )
    write_preferred_gui_id_to_qsettings(GUI_ID_LIBRARY_QML)
    res = apply_gui_switch_via_product(GUI_ID_DEFAULT_WIDGET, GUI_ID_DEFAULT_WIDGET)
    assert res.ok is True
    assert res.relaunch_scheduled is False
    assert read_preferred_gui_id_from_qsettings() == GUI_ID_DEFAULT_WIDGET


def test_revert_to_default_reverts_pref_when_relaunch_fails(qapplication, monkeypatch):
    monkeypatch.setattr(
        "app.global_overlay.overlay_gui_port.relaunch_via_run_gui_shell",
        lambda _gid: False,
    )
    write_preferred_gui_id_to_qsettings(GUI_ID_LIBRARY_QML)
    res = revert_to_default_gui_via_product(GUI_ID_LIBRARY_QML)
    assert res.ok is False
    assert read_preferred_gui_id_from_qsettings() == GUI_ID_LIBRARY_QML


def test_standard_overlay_gui_and_theme_sections(qapplication):
    dlg = StandardOverlayDialog(None, active_gui_id=GUI_ID_DEFAULT_WIDGET)
    dlg.refresh_content()
    assert dlg._gui_group.title() == "GUI"
    assert dlg._theme_group.title() == "Theme"
    assert dlg._gui_combo.count() >= 2
    dlg.close()


def test_emergency_overlay_has_revert_button(qapplication):
    dlg = EmergencyOverlayDialog(None, active_gui_id=GUI_ID_DEFAULT_WIDGET)
    dlg.refresh_content()
    assert dlg._emergency_revert_btn.isEnabled()
    dlg.close()


def test_relaunch_invokes_run_gui_shell_argv(monkeypatch, qapplication):
    captured: dict = {}

    def _fake_start(program, arguments, workingDirectory=""):
        captured["program"] = program
        captured["arguments"] = list(arguments)
        captured["workingDirectory"] = workingDirectory
        return True

    monkeypatch.setattr(
        "PySide6.QtCore.QProcess.startDetached",
        staticmethod(_fake_start),
    )
    assert relaunch_via_run_gui_shell(GUI_ID_LIBRARY_QML) is True
    root = resolve_repo_root()
    assert captured["arguments"][0].endswith("run_gui_shell.py")
    assert captured["arguments"][1:3] == ["--gui", GUI_ID_LIBRARY_QML]
    assert str(root) in captured["workingDirectory"] or captured["workingDirectory"] == str(root)
