"""Mapping Definition ↔ NodeRun-Status (ohne Qt)."""

from __future__ import annotations

from app.gui.domains.operations.workflows.run_status_mapper import (
    canvas_status_by_node_id,
    find_node_run_for_node,
    latest_node_run_by_node_id,
)
from app.workflows.models.run import NodeRun
from app.workflows.status import NodeRunStatus


def test_latest_node_run_by_node_id_last_wins() -> None:
    a = NodeRun("nr1", "r1", "n1", "noop", status=NodeRunStatus.COMPLETED)
    b = NodeRun("nr2", "r1", "n1", "noop", status=NodeRunStatus.FAILED)
    m = latest_node_run_by_node_id([a, b])
    assert m["n1"].node_run_id == "nr2"
    assert m["n1"].status == NodeRunStatus.FAILED


def test_canvas_status_covers_all_definition_nodes() -> None:
    nrs = [
        NodeRun("1", "r", "a", "start", status=NodeRunStatus.COMPLETED),
        NodeRun("2", "r", "b", "noop", status=NodeRunStatus.FAILED),
    ]
    m = canvas_status_by_node_id(["a", "b", "c"], nrs)
    assert m["a"] == NodeRunStatus.COMPLETED
    assert m["b"] == NodeRunStatus.FAILED
    assert m["c"] is None


def test_find_node_run_for_node() -> None:
    nrs = [NodeRun("1", "r", "x", "noop", status=NodeRunStatus.PENDING)]
    assert find_node_run_for_node(nrs, "x") is not None
    assert find_node_run_for_node(nrs, "y") is None


def test_empty_node_runs_no_crash() -> None:
    m = canvas_status_by_node_id(["only"], [])
    assert m["only"] is None
