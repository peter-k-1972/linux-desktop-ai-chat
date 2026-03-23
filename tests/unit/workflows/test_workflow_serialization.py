"""JSON/Dict-Roundtrip für WorkflowDefinition."""

import json

from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.serialization.json_io import (
    definition_from_dict,
    definition_from_json,
    definition_to_dict,
    definition_to_json,
)


def test_dict_roundtrip_preserves_schema_version():
    d = WorkflowDefinition(
        workflow_id="w",
        name="N",
        nodes=[
            WorkflowNode("s", "start", title="", description=""),
            WorkflowNode("e", "end"),
        ],
        edges=[WorkflowEdge("a", "s", "e")],
        description="desc",
        version=3,
        schema_version=7,
        metadata={"k": "v"},
    )
    d2 = definition_from_dict(definition_to_dict(d))
    assert d2.schema_version == 7
    assert d2.version == 3
    assert d2.metadata == {"k": "v"}
    assert len(d2.nodes) == 2


def test_json_roundtrip():
    d = WorkflowDefinition(
        "w2",
        "Name",
        [
            WorkflowNode("s", "start", position={"x": 1.0, "y": 2.0}),
            WorkflowNode("e", "end", is_enabled=False),
        ],
        [WorkflowEdge("e1", "s", "e")],
        schema_version=99,
    )
    s = definition_to_json(d, indent=None)
    d2 = definition_from_json(s)
    assert d2.workflow_id == "w2"
    assert d2.schema_version == 99
    assert d2.nodes[0].position == {"x": 1.0, "y": 2.0}
    assert d2.nodes[1].is_enabled is False


def test_json_loads_to_equivalent_keys():
    d = WorkflowDefinition(
        "w3",
        "X",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("a", "s", "e")],
    )
    blob = definition_to_json(d)
    parsed = json.loads(blob)
    assert "schema_version" in parsed
    assert parsed["schema_version"] == d.schema_version


def test_optional_fields_stable():
    d = WorkflowDefinition(
        "w4",
        "Y",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("a", "s", "e")],
    )
    dct = definition_to_dict(d)
    assert dct.get("description") == ""
    assert dct.get("project_id") is None
    d2 = definition_from_dict(dct)
    assert d2.nodes[0].title == ""
    assert d2.project_id is None


def test_project_id_roundtrip_dict_and_json():
    d = WorkflowDefinition(
        "w_proj",
        "P",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("a", "s", "e")],
        project_id=99,
    )
    d2 = definition_from_dict(definition_to_dict(d))
    assert d2.project_id == 99
    d3 = definition_from_json(definition_to_json(d, indent=None))
    assert d3.project_id == 99
