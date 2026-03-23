"""Tests PromptBuildNodeExecutor und Hilfsfunktionen."""

import pytest

from app.workflows.execution.context import AbortToken, RunContext
from app.workflows.execution.node_executors.prompt_build import (
    PromptBuildNodeExecutor,
    normalize_prompt_variables,
    render_prompt_template,
    stringify_template_variables,
)
from app.workflows.models.definition import WorkflowDefinition, WorkflowNode


def _ctx() -> RunContext:
    d = WorkflowDefinition("w", "w", [], [])
    return RunContext(run_id="r", definition=d, initial_input={}, abort=AbortToken())


def test_normalize_single_predecessor_flat():
    assert normalize_prompt_variables({"a": 1, "b": "x"}) == {"a": 1, "b": "x"}


def test_normalize_multi_predecessor_prefix():
    inp = {"p1": {"a": 1}, "p2": {"b": 2}}
    m = normalize_prompt_variables(inp)
    assert m == {"p1__a": 1, "p2__b": 2}


def test_render_template_ok():
    s = stringify_template_variables({"name": "Ada"})
    out, used = render_prompt_template("Hi {name}", s)
    assert out == "Hi Ada"
    assert used == {"name": "Ada"}


def test_render_template_missing_var():
    with pytest.raises(ValueError, match="Fehlende"):
        render_prompt_template("Hi {name}", {})


def test_executor_static_prompt_text():
    node = WorkflowNode("n", "prompt_build", config={"prompt_text": "fixed"})
    ex = PromptBuildNodeExecutor()
    out = ex.execute(node, {"ignored": True}, _ctx())
    assert out["prompt_text"] == "fixed"
    assert "rendered_variables" in out


def test_executor_template_with_input():
    node = WorkflowNode("n", "prompt_build", config={"template": "v={v}"})
    ex = PromptBuildNodeExecutor()
    out = ex.execute(node, {"v": 42}, _ctx())
    assert out["prompt_text"] == "v=42"


def test_executor_variable_map():
    node = WorkflowNode(
        "n",
        "prompt_build",
        config={"template": "x={x}", "variable_map": {"x": "src"}},
    )
    ex = PromptBuildNodeExecutor()
    out = ex.execute(node, {"src": "mapped"}, _ctx())
    assert out["prompt_text"] == "x=mapped"
