"""
Object-bound actions for the contextual toolbar (and shared with palette handlers).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from PySide6.QtCore import QTimer

from app.gui.workbench.focus.active_object import (
    OBJECT_AGENT,
    OBJECT_AI_CANVAS,
    OBJECT_KNOWLEDGE_BASE,
    OBJECT_MODEL_COMPARE,
    OBJECT_PROMPT,
    OBJECT_WORKFLOW,
    ActiveObject,
)
from app.gui.workbench.focus.object_status import ObjectStatus


def _log(window: Any, msg: str) -> None:
    window.console_panel.log_output(msg)


def _schedule_ready(window: Any, tab_key: str | None) -> None:
    def _done() -> None:
        window.focus_controller.set_active_status(ObjectStatus.READY)
        if tab_key:
            window.canvas_tabs.set_tab_status(tab_key, ObjectStatus.READY)

    QTimer.singleShot(600, _done)


def contextual_action_tuples(window: Any, active: ActiveObject) -> Sequence[tuple[str, Callable[[], None]]]:
    """(label, callback) pairs for the bar above the canvas."""
    t = active.object_type
    oid = active.object_id or ""
    tk = active.tab_key

    if t == OBJECT_AGENT:

        def run() -> None:
            _log(window, f"[Agent {oid}] Run Agent (stub)")
            window.focus_controller.set_active_status(ObjectStatus.RUNNING)
            if tk:
                window.canvas_tabs.set_tab_status(tk, ObjectStatus.RUNNING)
            _schedule_ready(window, tk)

        def reset() -> None:
            _log(window, f"[Agent {oid}] Reset Context (stub)")

        def dup() -> None:
            window.canvas_router.open_agent_test(f"{oid}-copy" if oid else "copy")

        def settings() -> None:
            _log(window, f"[Agent {oid}] Settings (stub)")

        return (
            ("Run", run),
            ("Reset Context", reset),
            ("Duplicate", dup),
            ("Settings", settings),
        )

    if t == OBJECT_WORKFLOW:

        def run_wf() -> None:
            _log(window, f"[Workflow {oid}] Run (stub)")
            window.focus_controller.set_active_status(ObjectStatus.RUNNING)
            if tk:
                window.canvas_tabs.set_tab_status(tk, ObjectStatus.RUNNING)
            _schedule_ready(window, tk)

        def validate() -> None:
            _log(window, f"[Workflow {oid}] Validate (stub)")

        def export() -> None:
            _log(window, f"[Workflow {oid}] Export (stub)")

        return (
            ("Run", run_wf),
            ("Validate", validate),
            ("Export", export),
        )

    if t == OBJECT_PROMPT:

        def test() -> None:
            _log(window, f"[Prompt {oid}] Test (stub)")

        def save() -> None:
            _log(window, f"[Prompt {oid}] Save (stub)")

        def dup_p() -> None:
            window.canvas_router.open_prompt_development(f"{oid}-copy" if oid else "copy")

        return (
            ("Test", test),
            ("Save", save),
            ("Duplicate", dup_p),
        )

    if t == OBJECT_KNOWLEDGE_BASE:

        def add_files() -> None:
            _log(window, f"[KB {oid}] Add Files (stub)")

        def reindex() -> None:
            _log(window, f"[KB {oid}] Reindex (stub)")
            if tk:
                window.canvas_tabs.set_tab_status(tk, ObjectStatus.INDEXING)
            window.focus_controller.set_active_status(ObjectStatus.INDEXING)

            def _idx_done() -> None:
                window.focus_controller.set_active_status(ObjectStatus.READY)
                if tk:
                    window.canvas_tabs.set_tab_status(tk, ObjectStatus.READY)

            QTimer.singleShot(700, _idx_done)

        def test_retrieval() -> None:
            _log(window, f"[KB {oid}] Test Retrieval (stub)")

        return (
            ("Add Files", add_files),
            ("Reindex", reindex),
            ("Test Retrieval", test_retrieval),
        )

    if t == OBJECT_MODEL_COMPARE:

        def run_cmp() -> None:
            _log(window, "[Compare] Run comparison (stub)")
            window.focus_controller.set_active_status(ObjectStatus.RUNNING)
            if tk:
                window.canvas_tabs.set_tab_status(tk, ObjectStatus.RUNNING)
            _schedule_ready(window, tk)

        def export_cmp() -> None:
            _log(window, "[Compare] Export (stub)")

        return (
            ("Run Comparison", run_cmp),
            ("Export", export_cmp),
        )

    if t == OBJECT_AI_CANVAS:

        def run_graph() -> None:
            _log(window, "[AI Canvas] Execute graph (stub)")
            window.focus_controller.set_active_status(ObjectStatus.RUNNING)
            if tk:
                window.canvas_tabs.set_tab_status(tk, ObjectStatus.RUNNING)
            _schedule_ready(window, tk)

        return (("Run", run_graph),)

    return ()
