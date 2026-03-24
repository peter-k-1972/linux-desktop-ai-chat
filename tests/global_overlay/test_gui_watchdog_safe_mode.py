"""GUI launch watchdog: failures window, auto safe mode, reset, overlay rescue."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.global_overlay.gui_launch_watchdog import (
    LAUNCH_FAILURE_THRESHOLD,
    LAUNCH_FAILURE_WINDOW_SEC,
    note_failed_gui_launch,
    note_gui_launch_attempt,
    note_successful_gui_launch,
    read_persisted_watchdog_snapshot_for_diagnostics,
    reset_watchdog_for_tests,
)
from app.global_overlay.overlay_diagnostics import collect_overlay_diagnostics
from app.global_overlay.overlay_gui_port import apply_gui_switch_via_product
from app.global_overlay.overlay_rescue_port import rescue_disable_safe_mode_watchdog
from app.gui_bootstrap import (
    product_qsettings,
    read_safe_mode_next_launch_pending,
    read_safe_mode_watchdog_banner,
    write_safe_mode_next_launch_flag,
    write_safe_mode_watchdog_banner,
)
from app.gui_registry import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML


@pytest.fixture(autouse=True)
def _wd_reset(qapplication):
    reset_watchdog_for_tests()
    yield
    reset_watchdog_for_tests()


def test_note_gui_launch_attempt_increments(qapplication):
    note_gui_launch_attempt()
    note_gui_launch_attempt()
    snap = read_persisted_watchdog_snapshot_for_diagnostics()
    assert snap["gui_start_attempts"] == "2"


def test_failure_counter_increments_and_success_resets(qapplication):
    note_failed_gui_launch()
    note_failed_gui_launch()
    snap = read_persisted_watchdog_snapshot_for_diagnostics()
    assert int(snap["failures_in_window"]) == 2
    note_successful_gui_launch()
    snap2 = read_persisted_watchdog_snapshot_for_diagnostics()
    assert snap2["failures_in_window"] == "0"


def test_three_failures_within_window_triggers_safe_mode(qapplication, monkeypatch):
    t = 1_700_000_000.0

    def fake_time() -> float:
        nonlocal t
        t += 0.3
        return t

    monkeypatch.setattr("app.global_overlay.gui_launch_watchdog.time.time", fake_time)
    for _ in range(LAUNCH_FAILURE_THRESHOLD):
        note_failed_gui_launch()
    assert read_safe_mode_next_launch_pending() is True
    assert read_safe_mode_watchdog_banner() is True


def test_failures_spread_beyond_window_do_not_trigger(qapplication, monkeypatch):
    monkeypatch.setattr(
        "app.global_overlay.gui_launch_watchdog.LAUNCH_FAILURE_WINDOW_SEC",
        1.0,
    )
    t = 0.0

    def fake_time() -> float:
        nonlocal t
        t += 2.0
        return t

    monkeypatch.setattr("app.global_overlay.gui_launch_watchdog.time.time", fake_time)
    for _ in range(LAUNCH_FAILURE_THRESHOLD):
        note_failed_gui_launch()
    assert read_safe_mode_next_launch_pending() is False


def test_corrupted_watchdog_json_does_not_crash(qapplication):
    qs = product_qsettings()
    qs.setValue("watchdog_failure_times_json", "{not valid json")
    qs.sync()
    note_failed_gui_launch()
    QApplication.processEvents()
    snap = read_persisted_watchdog_snapshot_for_diagnostics()
    assert "failures_in_window" in snap


def test_rescue_disable_safe_mode_clears_flags_and_persistence(qapplication):
    write_safe_mode_next_launch_flag(True)
    write_safe_mode_watchdog_banner(True)
    note_failed_gui_launch()
    r = rescue_disable_safe_mode_watchdog()
    assert r.ok
    assert read_safe_mode_next_launch_pending() is False
    assert read_safe_mode_watchdog_banner() is False
    assert read_persisted_watchdog_snapshot_for_diagnostics()["failures_in_window"] == "0"


def test_diagnostics_shows_safe_mode_overlay_status(qapplication):
    write_safe_mode_watchdog_banner(True)
    d = collect_overlay_diagnostics(GUI_ID_DEFAULT_WIDGET)
    assert "watchdog" in d.safe_mode_overlay_status.lower() or "active" in d.safe_mode_overlay_status.lower()


def test_apply_gui_switch_clears_watchdog_banner(monkeypatch, qapplication):
    write_safe_mode_watchdog_banner(True)
    monkeypatch.setattr(
        "app.global_overlay.overlay_gui_port.relaunch_via_run_gui_shell",
        lambda _gid: True,
    )
    monkeypatch.setattr("PySide6.QtWidgets.QApplication.instance", lambda: None)
    res = apply_gui_switch_via_product(GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML)
    assert res.ok
    assert read_safe_mode_watchdog_banner() is False


def test_threshold_constants_documented():
    assert LAUNCH_FAILURE_THRESHOLD == 3
    assert LAUNCH_FAILURE_WINDOW_SEC == 10.0
