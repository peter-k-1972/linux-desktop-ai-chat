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


def test_top_class_only_returns_leading_class_for_mixed_failures():
    result = run_script(
        "--top-class-only",
        input_text="""
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
FAILED tests/integration/test_sqlite.py::test_write - sqlalchemy.exc.OperationalError: database locked on sqlite session engine
============================== 2 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "database"


def test_top_class_only_json_output_returns_compact_payload():
    result = run_script(
        "--top-class-only",
        "--format",
        "json",
        input_text="""
FAILED tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots - RuntimeError: Qt platform plugin "xcb" could not be initialized in offscreen PySide6 mode
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
============================== 2 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {"top_class": "qt_ui"}


def test_class_counts_outputs_compact_one_line_summary():
    result = run_script(
        "--class-counts",
        input_text="""
FAILED tests/integration/test_sqlite.py::test_write - sqlalchemy.exc.OperationalError: database locked on sqlite session engine
FAILED tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots - RuntimeError: Qt platform plugin "xcb" could not be initialized in offscreen PySide6 mode
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
============================== 3 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == (
        "total_failed=3 architecture_guard=0 segment_dependency=0 qt_ui=1 "
        "database=1 async_behavior=0 import_path=0 runtime_behavior=0 "
        "smoke=1 doc_contract=0 packaging=0 unknown=0"
    )


def test_class_counts_handles_json_like_multiple_failures():
    result = run_script(
        "--class-counts",
        input_text="""
{
  "tests": [
    {
      "nodeid": "tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel",
      "outcome": "failed",
      "longrepr": "RuntimeError: asyncio event loop closed and task was destroyed"
    },
    {
      "nodeid": "tests/unit/test_misc.py::test_edge_case",
      "outcome": "failed",
      "longrepr": "ValueError: something odd happened"
    }
  ]
}
""".strip(),
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == (
        "total_failed=2 architecture_guard=0 segment_dependency=0 qt_ui=0 "
        "database=0 async_behavior=1 import_path=0 runtime_behavior=0 "
        "smoke=0 doc_contract=0 packaging=0 unknown=1"
    )


def test_class_sequence_outputs_first_seen_class_order():
    result = run_script(
        "--class-sequence",
        input_text="""
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
FAILED tests/integration/test_sqlite.py::test_write - sqlalchemy.exc.OperationalError: database locked on sqlite session engine
FAILED tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots - RuntimeError: Qt platform plugin "xcb" could not be initialized in offscreen PySide6 mode
FAILED tests/integration/test_sqlite.py::test_retry - sqlalchemy.exc.OperationalError: engine failed again
============================== 4 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "smoke database qt_ui"


def test_class_sequence_handles_json_like_input_in_input_order():
    result = run_script(
        "--class-sequence",
        input_text="""
{
  "tests": [
    {
      "nodeid": "tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots",
      "outcome": "failed",
      "longrepr": "Qt platform plugin xcb could not be initialized in offscreen PySide6 mode"
    },
    {
      "nodeid": "tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel",
      "outcome": "failed",
      "longrepr": "RuntimeError: asyncio event loop closed and task was destroyed"
    },
    {
      "nodeid": "tests/unit/test_misc.py::test_edge_case",
      "outcome": "failed",
      "longrepr": "ValueError: something odd happened"
    }
  ]
}
""".strip(),
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "qt_ui async_behavior unknown"


def test_first_nodeids_outputs_first_seen_nodeid_per_class():
    result = run_script(
        "--first-nodeids",
        input_text="""
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
FAILED tests/integration/test_sqlite.py::test_write - sqlalchemy.exc.OperationalError: database locked on sqlite session engine
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_retry - AssertionError: smoke broke again
FAILED tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots - RuntimeError: Qt platform plugin "xcb" could not be initialized in offscreen PySide6 mode
============================== 4 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == (
        "smoke=tests/smoke/test_help_window_smoke.py::test_help_window_opens "
        "database=tests/integration/test_sqlite.py::test_write "
        "qt_ui=tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots"
    )


def test_first_nodeids_handles_json_like_input_and_preserves_input_order():
    result = run_script(
        "--first-nodeids",
        input_text="""
{
  "tests": [
    {
      "nodeid": "tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots",
      "outcome": "failed",
      "longrepr": "Qt platform plugin xcb could not be initialized in offscreen PySide6 mode"
    },
    {
      "nodeid": "tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel",
      "outcome": "failed",
      "longrepr": "RuntimeError: asyncio event loop closed and task was destroyed"
    },
    {
      "nodeid": "tests/unit/test_misc.py::test_edge_case",
      "outcome": "failed",
      "longrepr": "ValueError: something odd happened"
    }
  ]
}
""".strip(),
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == (
        "qt_ui=tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots "
        "async_behavior=tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel "
        "unknown=tests/unit/test_misc.py::test_edge_case"
    )


def test_class_counts_sequence_outputs_counts_in_first_seen_class_order():
    result = run_script(
        "--class-counts-sequence",
        input_text="""
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
FAILED tests/integration/test_sqlite.py::test_write - sqlalchemy.exc.OperationalError: database locked on sqlite session engine
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_retry - AssertionError: smoke broke again
FAILED tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots - RuntimeError: Qt platform plugin "xcb" could not be initialized in offscreen PySide6 mode
============================== 4 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "smoke=2 database=1 qt_ui=1"


def test_class_counts_sequence_handles_json_like_input_in_input_order():
    result = run_script(
        "--class-counts-sequence",
        input_text="""
{
  "tests": [
    {
      "nodeid": "tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots",
      "outcome": "failed",
      "longrepr": "Qt platform plugin xcb could not be initialized in offscreen PySide6 mode"
    },
    {
      "nodeid": "tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel",
      "outcome": "failed",
      "longrepr": "RuntimeError: asyncio event loop closed and task was destroyed"
    },
    {
      "nodeid": "tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots_again",
      "outcome": "failed",
      "longrepr": "Qt platform plugin xcb could not be initialized in offscreen PySide6 mode"
    },
    {
      "nodeid": "tests/unit/test_misc.py::test_edge_case",
      "outcome": "failed",
      "longrepr": "ValueError: something odd happened"
    }
  ]
}
""".strip(),
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "qt_ui=2 async_behavior=1 unknown=1"


def test_class_first_last_outputs_first_and_last_seen_classes():
    result = run_script(
        "--class-first-last",
        input_text="""
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
FAILED tests/integration/test_sqlite.py::test_write - sqlalchemy.exc.OperationalError: database locked on sqlite session engine
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_retry - AssertionError: smoke broke again
============================== 3 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "first=smoke last=smoke"


def test_class_first_last_handles_json_like_input_in_input_order():
    result = run_script(
        "--class-first-last",
        input_text="""
{
  "tests": [
    {
      "nodeid": "tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots",
      "outcome": "failed",
      "longrepr": "Qt platform plugin xcb could not be initialized in offscreen PySide6 mode"
    },
    {
      "nodeid": "tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel",
      "outcome": "failed",
      "longrepr": "RuntimeError: asyncio event loop closed and task was destroyed"
    },
    {
      "nodeid": "tests/unit/test_misc.py::test_edge_case",
      "outcome": "failed",
      "longrepr": "ValueError: something odd happened"
    }
  ]
}
""".strip(),
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "first=qt_ui last=unknown"


def test_unknown_failure_is_classified():
    result = run_script(
        input_text="""
FAILED tests/unit/test_misc.py::test_edge_case - ValueError: something odd happened
============================== 1 failed in 0.11s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert "unknown: 1" in result.stdout


def test_top_class_only_remains_unchanged_when_class_counts_exists():
    result = run_script(
        "--top-class-only",
        input_text="""
FAILED tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel - RuntimeError: asyncio event loop closed and task was destroyed
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
============================== 2 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "async_behavior"


def test_class_counts_remains_unchanged_when_class_sequence_exists():
    result = run_script(
        "--class-counts",
        input_text="""
FAILED tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel - RuntimeError: asyncio event loop closed and task was destroyed
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
============================== 2 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == (
        "total_failed=2 architecture_guard=0 segment_dependency=0 qt_ui=0 "
        "database=0 async_behavior=1 import_path=0 runtime_behavior=0 "
        "smoke=1 doc_contract=0 packaging=0 unknown=0"
    )


def test_first_nodeids_is_robust_when_some_failures_have_no_recognizable_nodeid():
    result = run_script(
        "--first-nodeids",
        input_text="""
{
  "tests": [
    {
      "outcome": "failed",
      "longrepr": "database locked on sqlite session engine"
    },
    {
      "nodeid": "tests/integration/test_sqlite.py::test_write",
      "outcome": "failed",
      "longrepr": "sqlalchemy.exc.OperationalError: database locked on sqlite session engine"
    }
  ]
}
""".strip(),
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "database=tests/integration/test_sqlite.py::test_write"


def test_class_sequence_remains_unchanged_when_first_nodeids_exists():
    result = run_script(
        "--class-sequence",
        input_text="""
FAILED tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel - RuntimeError: asyncio event loop closed and task was destroyed
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
============================== 2 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "async_behavior smoke"


def test_first_nodeids_remains_unchanged_when_class_counts_sequence_exists():
    result = run_script(
        "--first-nodeids",
        input_text="""
FAILED tests/integration/test_sqlite.py::test_write - sqlalchemy.exc.OperationalError: database locked on sqlite session engine
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
============================== 2 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == (
        "database=tests/integration/test_sqlite.py::test_write "
        "smoke=tests/smoke/test_help_window_smoke.py::test_help_window_opens"
    )


def test_class_counts_sequence_remains_unchanged_when_class_first_last_exists():
    result = run_script(
        "--class-counts-sequence",
        input_text="""
FAILED tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel - RuntimeError: asyncio event loop closed and task was destroyed
FAILED tests/smoke/test_help_window_smoke.py::test_help_window_opens - AssertionError: smoke broke
FAILED tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel_retry - RuntimeError: task was destroyed
============================== 3 failed in 0.20s ==============================
""".strip()
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "async_behavior=2 smoke=1"


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


def test_json_like_multiple_failures_are_extracted_and_classified():
    result = run_script(
        "--format",
        "json",
        input_text="""
{
  "tests": [
    {
      "nodeid": "tests/integration/test_sqlite.py::test_write",
      "outcome": "failed",
      "longrepr": "sqlalchemy.exc.OperationalError: database locked on sqlite session engine"
    },
    {
      "nodeid": "tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots",
      "outcome": "failed",
      "longrepr": "Qt platform plugin xcb could not be initialized in offscreen PySide6 mode"
    },
    {
      "nodeid": "tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel",
      "outcome": "failed",
      "longrepr": "RuntimeError: asyncio event loop closed and task was destroyed"
    }
  ]
}
""".strip(),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"]["total_failed"] == 3
    assert payload["summary"]["database"] == 1
    assert payload["summary"]["qt_ui"] == 1
    assert payload["summary"]["async_behavior"] == 1
    assert payload["failed_tests"] == [
        {
            "nodeid": "tests/integration/test_sqlite.py::test_write",
            "class": "database",
        },
        {
            "nodeid": "tests/ui_runtime/test_qml_engine_smoke.py::test_engine_boots",
            "class": "qt_ui",
        },
        {
            "nodeid": "tests/async_behavior/test_rag_concurrent_retrieval.py::test_cancel",
            "class": "async_behavior",
        },
    ]
