"""tool_call über python_callable + Stub."""

import pytest

from app.workflows.execution.context import AbortToken, RunContext
from app.workflows.execution.node_executors.tool_call import ToolCallNodeExecutor
from app.workflows.models.definition import WorkflowDefinition, WorkflowNode


def _ctx() -> RunContext:
    d = WorkflowDefinition("w", "w", [], [])
    return RunContext(run_id="r", definition=d, initial_input={}, abort=AbortToken())


def test_tool_call_python_callable_success():
    node = WorkflowNode(
        "t",
        "tool_call",
        config={
            "executor_type": "python_callable",
            "executor_config": {
                "callable": "tests.unit.workflows.workflow_tool_stub.stub_concat_tool",
            },
        },
    )
    ex = ToolCallNodeExecutor()
    out = ex.execute(node, {"a": "foo", "b": "bar"}, _ctx())
    assert out["tool_result"]["tool_result"] == "foobar"


def test_tool_call_failure_soft_fail():
    node = WorkflowNode(
        "t",
        "tool_call",
        config={
            "executor_type": "python_callable",
            "executor_config": {
                "callable": "tests.unit.workflows.workflow_tool_stub.stub_fail_tool",
            },
        },
    )
    ex = ToolCallNodeExecutor()
    out = ex.execute(node, {}, _ctx())
    assert out.get("tool_call_success") is False
    assert "stub_absichtlich" in (out.get("tool_call_error") or "")


def test_tool_call_unknown_executor_type():
    node = WorkflowNode("t", "tool_call", config={"executor_type": "nonexistent_xyz"})
    ex = ToolCallNodeExecutor()
    with pytest.raises(ValueError, match="unbekannter"):
        ex.execute(node, {}, _ctx())
