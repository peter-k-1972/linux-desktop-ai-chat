"""Tests für GraphValidator."""

import pytest

from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.registry.node_registry import build_default_node_registry
from app.workflows.validation.graph_validator import GraphValidator


def _reg():
    return build_default_node_registry()


def test_valid_minimal_workflow():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="Minimal",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[WorkflowEdge("a1", "s", "e")],
    )
    r = GraphValidator().validate(d, _reg())
    assert r.is_valid
    assert not r.errors


def test_missing_start():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="X",
        nodes=[
            WorkflowNode("n", "noop", title="N"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[WorkflowEdge("a1", "n", "e")],
    )
    r = GraphValidator().validate(d, _reg())
    assert not r.is_valid
    assert any("Start" in e for e in r.errors)


def test_missing_end():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("n", "noop", title="N"),
        ],
        edges=[WorkflowEdge("a1", "s", "n")],
    )
    r = GraphValidator().validate(d, _reg())
    assert not r.is_valid
    assert any("End" in e for e in r.errors)


def test_cycle_detected():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="C",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("a", "noop", title="A"),
            WorkflowNode("b", "noop", title="B"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("e1", "s", "a"),
            WorkflowEdge("e2", "a", "b"),
            WorkflowEdge("e3", "b", "a"),
            WorkflowEdge("e4", "b", "e"),
        ],
    )
    r = GraphValidator().validate(d, _reg())
    assert not r.is_valid
    assert any("Zyklus" in e for e in r.errors)


def test_edge_unknown_node():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[WorkflowEdge("a1", "s", "ghost")],
    )
    r = GraphValidator().validate(d, _reg())
    assert not r.is_valid
    assert any("unbekannte target_node_id" in e for e in r.errors)


def test_duplicate_node_id():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="X",
        nodes=[
            WorkflowNode("x", "start", title="S"),
            WorkflowNode("x", "end", title="E"),
        ],
        edges=[],
    )
    r = GraphValidator().validate(d, _reg())
    assert not r.is_valid
    assert any("Doppelte node_id" in e for e in r.errors)


def test_duplicate_edge_id():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("dup", "s", "e"),
            WorkflowEdge("dup", "s", "e"),
        ],
    )
    r = GraphValidator().validate(d, _reg())
    assert not r.is_valid
    assert any("Doppelte edge_id" in e for e in r.errors)


def test_orphan_node_unreachable():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
            WorkflowNode("o", "noop", title="Orphan"),
        ],
        edges=[WorkflowEdge("a1", "s", "e")],
    )
    r = GraphValidator().validate(d, _reg())
    assert not r.is_valid
    assert any("nicht erreichbar" in e for e in r.errors)


def test_unknown_node_type():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("x", "alien_tool", title="X"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "x"),
            WorkflowEdge("a2", "x", "e"),
        ],
    )
    r = GraphValidator().validate(d, _reg())
    assert not r.is_valid
    assert any("unbekannter" in e.lower() or "registrierter" in e.lower() for e in r.errors)


def test_disabled_node_excluded_from_topology():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("n", "noop", title="N", is_enabled=False),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "n"),
            WorkflowEdge("a2", "n", "e"),
            WorkflowEdge("a3", "s", "e"),
        ],
    )
    r = GraphValidator().validate(d, _reg())
    assert r.is_valid
    assert any("ignoriert" in w for w in r.warnings)


def test_two_start_nodes_one_disabled_is_valid():
    """Nur aktivierte Start-Knoten zählen für die „genau ein Start“-Regel."""
    d = WorkflowDefinition(
        workflow_id="w1",
        name="TwoStarts",
        nodes=[
            WorkflowNode("s1", "start", title="S1", is_enabled=False),
            WorkflowNode("s2", "start", title="S2"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s2", "e"),
        ],
    )
    r = GraphValidator().validate(d, _reg())
    assert r.is_valid


def test_noop_invalid_config():
    d = WorkflowDefinition(
        workflow_id="w1",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("n", "noop", title="N", config={"bad_key": 1}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "n"),
            WorkflowEdge("a2", "n", "e"),
        ],
    )
    r = GraphValidator().validate(d, _reg())
    assert not r.is_valid
    assert any("Unbekannte" in e or "Schlüssel" in e for e in r.errors)
