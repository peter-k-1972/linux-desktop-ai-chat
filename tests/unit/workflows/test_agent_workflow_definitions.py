"""R2: Workflow-Definitionen mit Agent-Knoten."""

from app.workflows.models.definition import WorkflowDefinition, WorkflowNode
from app.workflows.queries.agent_workflow_definitions import (
    definition_references_agent,
    list_workflow_ids_referencing_agent,
)


def test_definition_matches_slug():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="A",
        nodes=[
            WorkflowNode("n1", "agent", config={"agent_slug": "planner"}),
        ],
        edges=[],
    )
    assert definition_references_agent(d, agent_id=None, slug="planner")
    assert not definition_references_agent(d, agent_id=None, slug="other")


def test_definition_matches_agent_id():
    d = WorkflowDefinition(
        workflow_id="w2",
        name="B",
        nodes=[
            WorkflowNode("n1", "agent", config={"agent_id": "uuid-1"}),
        ],
        edges=[],
    )
    assert definition_references_agent(d, agent_id="uuid-1", slug=None)


def test_disabled_agent_node_ignored():
    d = WorkflowDefinition(
        workflow_id="w3",
        name="C",
        nodes=[
            WorkflowNode("n1", "agent", config={"agent_slug": "x"}, is_enabled=False),
        ],
        edges=[],
    )
    assert not definition_references_agent(d, agent_id=None, slug="x")


def test_list_workflow_ids_sorted():
    a = WorkflowDefinition(
        "b",
        "B",
        [WorkflowNode("n", "agent", config={"agent_slug": "s"})],
        [],
    )
    c = WorkflowDefinition(
        "a",
        "A",
        [WorkflowNode("n", "agent", config={"agent_slug": "s"})],
        [],
    )
    ids = list_workflow_ids_referencing_agent([a, c], agent_id=None, slug="s")
    assert ids == ["a", "b"]
