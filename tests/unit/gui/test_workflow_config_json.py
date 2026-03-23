"""Tests für GUI-Hilfen (Workflow-Knoten-JSON), ohne Qt."""

from app.gui.domains.operations.workflows.config_json import format_node_config_json, parse_node_config_json


def test_parse_empty():
    d, err = parse_node_config_json("")
    assert err is None
    assert d == {}


def test_parse_valid():
    d, err = parse_node_config_json('{"merge": {"a": 1}}')
    assert err is None
    assert d == {"merge": {"a": 1}}


def test_parse_invalid_json():
    d, err = parse_node_config_json("{no")
    assert d is None
    assert err is not None


def test_parse_not_object():
    d, err = parse_node_config_json("[1,2]")
    assert d is None
    assert "Objekt" in err


def test_format_roundtrip():
    cfg = {"z": 1, "a": {"b": 2}}
    text = format_node_config_json(cfg)
    d, err = parse_node_config_json(text)
    assert err is None
    assert d == cfg
