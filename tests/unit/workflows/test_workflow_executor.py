"""Tests für WorkflowExecutor."""

import uuid

from app.workflows.execution.context import AbortToken
from app.workflows.execution.executor import WorkflowExecutor
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.registry.node_registry import NodeRegistry, build_default_node_registry
from app.workflows.status import NodeRunStatus, WorkflowRunStatus


def _linear_se(start_to_end: bool = True):
    nodes = [
        WorkflowNode("s", "start", title="S"),
        WorkflowNode("e", "end", title="E"),
    ]
    edges = [WorkflowEdge("a1", "s", "e")]
    return WorkflowDefinition(workflow_id="w", name="L", nodes=nodes, edges=edges)


def test_start_end_final_output():
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = _linear_se()
    run = WorkflowRun(
        run_id="r1",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={"msg": "hi"},
        definition_snapshot=d.to_dict(),
    )
    abort = AbortToken()
    ex.execute(d, run, reg, abort)
    assert run.status == WorkflowRunStatus.COMPLETED
    assert run.final_output == {"msg": "hi"}
    assert len(run.node_runs) == 2
    assert [nr.node_id for nr in run.node_runs] == ["s", "e"]


def test_start_noop_end_merge_config():
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="N",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("n", "noop", title="N", config={"merge": {"k": 2}}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("e1", "s", "n"),
            WorkflowEdge("e2", "n", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r2",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={"a": 1},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.COMPLETED
    assert run.final_output == {"a": 1, "k": 2}


def test_topological_order_deterministic():
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    # s -> b, s -> a (lexicographic tie: a before b)
    d = WorkflowDefinition(
        workflow_id="w",
        name="D",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("b", "noop", title="B"),
            WorkflowNode("a", "noop", title="A"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("x1", "s", "b"),
            WorkflowEdge("x2", "s", "a"),
            WorkflowEdge("x3", "a", "e"),
            WorkflowEdge("x4", "b", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r3",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    order = [nr.node_id for nr in run.node_runs]
    assert order.index("a") < order.index("e")
    assert order.index("b") < order.index("e")
    assert order[0] == "s"
    assert order[-1] == "e"


def test_multi_predecessor_input_dict():
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="M",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("p1", "noop", title="P1", config={"merge": {"branch": 1}}),
            WorkflowNode("p2", "noop", title="P2", config={"merge": {"branch": 2}}),
            WorkflowNode("m", "noop", title="M"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("1", "s", "p1"),
            WorkflowEdge("2", "s", "p2"),
            WorkflowEdge("3", "p1", "m"),
            WorkflowEdge("4", "p2", "m"),
            WorkflowEdge("5", "m", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r4",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={"base": True},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.COMPLETED
    assert "p1" in run.final_output
    assert "p2" in run.final_output


def test_missing_executor_type():
    reg = NodeRegistry()  # leer
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = _linear_se()
    run = WorkflowRun(
        run_id="r5",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.FAILED
    assert run.error_message is not None
    assert "Executor" in run.error_message or "start" in run.error_message.lower()


def test_cancel_before_execute():
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="C",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            *[WorkflowNode(f"n{i}", "noop", title=str(i)) for i in range(30)],
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[WorkflowEdge("a0", "s", "n0")]
        + [WorkflowEdge(f"a{i+1}", f"n{i}", f"n{i+1}") for i in range(29)]
        + [WorkflowEdge("ae", "n29", "e")],
    )
    run = WorkflowRun(
        run_id="r6",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    abort = AbortToken()
    abort.cancel()
    ex.execute(d, run, reg, abort)
    assert run.status == WorkflowRunStatus.CANCELLED
    assert run.node_runs == []


def test_cancel_after_first_node_via_hook():
    """Kooperativer Abbruch zwischen Knoten (Abort nach Abschluss des Start-Knotens)."""

    class AbortAfterStart(WorkflowExecutor):
        def execute(self, definition, run, registry, abort, on_after_node=None):
            def wrapped(r: WorkflowRun, nr: NodeRun) -> None:
                if on_after_node:
                    on_after_node(r, nr)
                if nr.node_id == "s" and nr.status == NodeRunStatus.COMPLETED:
                    abort.cancel()

            return super().execute(definition, run, registry, abort, on_after_node=wrapped)

    reg = build_default_node_registry()
    ex = AbortAfterStart(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="C",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("n", "noop", title="N"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "n"),
            WorkflowEdge("a2", "n", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r8",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.CANCELLED
    assert len(run.node_runs) == 1
    assert run.node_runs[0].node_id == "s"
