"""WorkflowGraphicsScene: Auto-Layout-Signal nur bei echter Positions-Mutation."""

from __future__ import annotations

from app.gui.domains.operations.workflows.canvas.workflow_scene import WorkflowGraphicsScene
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode


def test_rebuild_returns_fill_count_matches_ensure_missing_positions(qapplication) -> None:
    wf = WorkflowDefinition(
        workflow_id="w",
        name="w",
        nodes=[
            WorkflowNode("a", "noop", title="A"),
            WorkflowNode("b", "noop", title="B"),
        ],
        edges=[],
    )
    scene = WorkflowGraphicsScene()
    hits: list[int] = []
    scene.definition_user_modified.connect(lambda: hits.append(1))

    n1 = scene.set_definition(wf)
    assert n1 == 2
    assert len(hits) == 1

    hits.clear()
    n2 = scene.set_definition(wf)
    assert n2 == 0
    assert hits == []


def test_rebuild_no_signal_when_all_positions_preset(qapplication) -> None:
    wf = WorkflowDefinition(
        workflow_id="w",
        name="w",
        nodes=[
            WorkflowNode("x", "noop", title="X", position={"x": 0.0, "y": 0.0}),
        ],
        edges=[],
    )
    scene = WorkflowGraphicsScene()
    hits: list[int] = []
    scene.definition_user_modified.connect(lambda: hits.append(1))

    assert scene.set_definition(wf) == 0
    assert hits == []


def test_rebuild_after_explicit_mutation_no_extra_layout_signal(qapplication) -> None:
    """Wie nach neuer Kante: ein explizites definition_user_modified, dann rebuild; kein zusätzliches Layout-Signal."""
    wf = WorkflowDefinition(
        workflow_id="w",
        name="w",
        nodes=[
            WorkflowNode("a", "noop", title="A"),
            WorkflowNode("b", "noop", title="B"),
        ],
        edges=[],
    )
    scene = WorkflowGraphicsScene()
    hits: list[int] = []
    scene.definition_user_modified.connect(lambda: hits.append(1))

    scene.set_definition(wf)
    assert len(hits) == 1
    wf.edges.append(WorkflowEdge("e1", "a", "b"))
    scene.definition_user_modified.emit()
    scene.rebuild()
    assert len(hits) == 2
