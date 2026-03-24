"""Slice 4: Rescue actions, safe mode flag, bootstrap helpers."""

from __future__ import annotations

import pytest

from app.global_overlay.overlay_rescue_port import (
    rescue_enable_safe_mode_next_launch,
    rescue_reset_preferred_gui_only,
    rescue_reset_preferred_theme_only,
    rescue_revert_to_default_gui_relaunch,
)
from app.gui_bootstrap import (
    argv_has_long_option,
    consume_safe_mode_next_launch,
    read_preferred_gui_id_from_qsettings,
    read_safe_mode_next_launch_pending,
    write_preferred_gui_id_to_qsettings,
    write_safe_mode_next_launch_flag,
)
from app.gui_registry import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML


def test_argv_has_long_option():
    assert argv_has_long_option(["bin", "--gui", "x"], "--gui") is True
    assert argv_has_long_option(["bin", "--gui=library_qml_gui"], "--gui") is True
    assert argv_has_long_option(["bin", "--theme", "dark_default"], "--gui") is False


def test_safe_mode_flag_roundtrip(qapplication):
    write_safe_mode_next_launch_flag(False)
    assert read_safe_mode_next_launch_pending() is False
    write_safe_mode_next_launch_flag(True)
    assert read_safe_mode_next_launch_pending() is True


def test_consume_safe_mode_one_shot(qapplication):
    write_safe_mode_next_launch_flag(True)
    assert consume_safe_mode_next_launch() is True
    assert read_safe_mode_next_launch_pending() is False
    assert consume_safe_mode_next_launch() is False


def test_rescue_reset_preferred_gui_only(qapplication):
    write_preferred_gui_id_to_qsettings(GUI_ID_LIBRARY_QML)
    r = rescue_reset_preferred_gui_only()
    assert r.ok, r.message
    assert read_preferred_gui_id_from_qsettings() == GUI_ID_DEFAULT_WIDGET


def test_rescue_enable_safe_mode(qapplication):
    write_safe_mode_next_launch_flag(False)
    r = rescue_enable_safe_mode_next_launch()
    assert r.ok
    assert read_safe_mode_next_launch_pending() is True


def test_rescue_reset_theme_only_widget(qapplication):
    r = rescue_reset_preferred_theme_only(GUI_ID_DEFAULT_WIDGET)
    assert r.ok, r.message


def test_rescue_revert_wraps_gui_apply(monkeypatch, qapplication):
    monkeypatch.setattr(
        "app.global_overlay.overlay_gui_port.relaunch_via_run_gui_shell",
        lambda _gid: False,
    )
    write_preferred_gui_id_to_qsettings(GUI_ID_DEFAULT_WIDGET)
    r = rescue_revert_to_default_gui_relaunch(GUI_ID_LIBRARY_QML)
    assert r.ok is False
