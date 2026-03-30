from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "dev" / "classify_pytest_failures.py"


def run_script(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        input=input_text,
    )


def test_architecture_guard_failure_is_classified():
    result = run_script(
        input_text="""
============================= test session starts =============================
FAILED tests/architecture/test_startup_governance_guards.py::test_x - AssertionError: governance guard failed
============================== 1 failed in 0.12s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert "architecture_guard: 1" in result.stdout
    assert "tests/architecture/test_startup_governance_guards.py::test_x -> architecture_guard" in result.stdout


def test_segment_dependency_failure_is_classified():
    result = run_script(
        input_text="""
FAILED tests/architecture/test_segment_dependency_rules.py::test_gui_rules - AssertionError: segment dependency rule violated
============================== 1 failed in 0.10s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert "segment_dependency: 1" in result.stdout


def test_smoke_failure_is_classified():
    result = run_script(
        input_text="""
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: window missing
============================== 1 failed in 0.15s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert "smoke: 1" in result.stdout


def test_qt_ui_failure_is_classified():
    result = run_script(
        input_text="""
FAILED tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots - RuntimeError: Qt platform plugin "xcb" could not be initialized in offscreen PySide6 mode
============================== 1 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert "qt_ui: 1" in result.stdout
    assert "tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots -> qt_ui" in result.stdout


def test_database_failure_is_classified():
    result = run_script(
        input_text="""
FAILED tests/integration/test_sqlite.py::test_write - sqlalchemy.exc.OperationalError: database locked on sqlite session engine
============================== 1 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert "database: 1" in result.stdout


def test_async_behavior_failure_is_classified():
    result = run_script(
        input_text="""
FAILED tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel - RuntimeError: asyncio event loop closed and task was destroyed
============================== 1 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert "async_behavior: 1" in result.stdout


def test_priority_prefers_async_behavior_over_qt_ui_when_qasync_is_present():
    result = run_script(
        input_text="""
FAILED tests/ui/test_chat_ui.py::test_render - RuntimeError: qasync event loop stopped while QApplication window stayed open
============================== 1 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert "async_behavior: 1" in result.stdout
    assert "qt_ui: 0" in result.stdout
    assert "tests/ui/test_chat_ui.py::test_render -> async_behavior" in result.stdout


def test_unknown_failure_is_classified():
    result = run_script(
        input_text="""
FAILED tests/unit/test_misc.py::test_edge_case - ValueError: something odd happened
============================== 1 failed in 0.11s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert "unknown: 1" in result.stdout


def test_empty_input_returns_clear_error():
    result = run_script(input_text="")
    assert result.returncode == 2
    assert "Input is empty." in result.stderr


def test_json_output_contains_summary_and_failed_tests():
    result = run_script(
        "--format",
        "json",
        input_text="""
============================= test session starts =============================
FAILED tests/architecture/test_startup_governance_guards.py::test_x - AssertionError: governance guard failed
FAILED tests/smoke/test_help_window_smoke.py::test_help - AssertionError: smoke broke
============================== 2 failed in 0.12s ==============================
""".strip(),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"]["total_failed"] == 2
    assert payload["summary"]["architecture_guard"] == 1
    assert payload["summary"]["smoke"] == 1
    assert payload["summary"]["qt_ui"] == 0
    assert payload["summary"]["database"] == 0
    assert payload["summary"]["async_behavior"] == 0
    assert payload["summary"]["unknown"] == 0
    assert payload["failed_tests"] == [
        {
            "nodeid": "tests/architecture/test_startup_governance_guards.py::test_x",
            "class": "architecture_guard",
        },
        {
            "nodeid": "tests/smoke/test_help_window_smoke.py::test_help",
            "class": "smoke",
        },
    ]
