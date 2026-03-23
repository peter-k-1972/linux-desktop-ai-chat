"""Reine Layout-Hilfen für Workflow-Canvas (ohne Qt)."""

from __future__ import annotations

from app.gui.domains.operations.workflows.canvas.canvas_layout import (
    CELL_H,
    CELL_W,
    MARGIN,
    GRID_COLS,
    ensure_missing_positions,
    position_for_grid_index,
    positions_dict_for_definition,
    write_position,
)
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode


def test_position_for_grid_index_is_deterministic() -> None:
    assert position_for_grid_index(0) == {"x": MARGIN, "y": MARGIN}
    col, row = 1, 0
    assert position_for_grid_index(1) == {"x": MARGIN + col * CELL_W, "y": MARGIN + row * CELL_H}
    idx = GRID_COLS
    col, row = 0, 1
    assert position_for_grid_index(idx) == {"x": MARGIN + col * CELL_W, "y": MARGIN + row * CELL_H}


def test_ensure_missing_positions_fills_only_missing_sorted_by_node_id() -> None:
    wf = WorkflowDefinition(
        workflow_id="w1",
        name="w1",
        nodes=[
            WorkflowNode("z", "noop", title="z", position={"x": 1.0, "y": 2.0}),
            WorkflowNode("a", "noop", title="a"),
        ],
        edges=[],
    )
    n = ensure_missing_positions(wf)
    assert n == 1
    by_id = {node.node_id: node for node in wf.nodes}
    assert by_id["z"].position == {"x": 1.0, "y": 2.0}
    assert by_id["a"].position is not None
    assert "x" in by_id["a"].position and "y" in by_id["a"].position


def test_write_position_roundtrip_in_positions_dict() -> None:
    n = WorkflowNode("n1", "noop", title="t")
    write_position(n, 10.5, -3.25)
    wf = WorkflowDefinition(workflow_id="w", name="w", nodes=[n], edges=[])
    pos = positions_dict_for_definition(wf)
    assert pos["n1"] == (10.5, -3.25)


def test_ensure_missing_positions_idempotent() -> None:
    wf = WorkflowDefinition(
        workflow_id="w",
        name="w",
        nodes=[WorkflowNode("only", "noop", title="t")],
        edges=[],
    )
    assert ensure_missing_positions(wf) == 1
    assert ensure_missing_positions(wf) == 0


def test_after_roundtrip_no_new_auto_layout() -> None:
    """Persistenz: gespeicherte Definition mit Positionen erzeugt beim erneuten Anwenden 0 neue Fills."""
    wf = WorkflowDefinition(
        workflow_id="w",
        name="w",
        nodes=[WorkflowNode("n", "noop", title="t")],
        edges=[],
    )
    ensure_missing_positions(wf)
    data = wf.to_dict()
    wf2 = WorkflowDefinition.from_dict(data)
    assert ensure_missing_positions(wf2) == 0


def test_semantic_preserved_after_layout_and_position_write() -> None:
    wf = WorkflowDefinition(
        workflow_id="w",
        name="w",
        nodes=[
            WorkflowNode("start", "start", title="S"),
            WorkflowNode("end", "end", title="E"),
        ],
        edges=[WorkflowEdge("e1", "start", "end")],
    )
    ensure_missing_positions(wf)
    write_position(wf.nodes[0], 99.0, 100.0)
    assert len(wf.nodes) == 2
    assert wf.edges[0].source_node_id == "start"
    assert wf.edges[0].target_node_id == "end"
