"""
Contract Tests: Tool Result und LLM Response Strukturen.

Sichert den Vertrag zwischen:
- ToolExecutionEntry und DebugStore / ToolExecutionView
- ResponseResult und OutputPipeline / ChatWidget
- Task.output und ExecutionEngine / Agenten
"""

from datetime import datetime, timezone

import pytest

from app.debug.debug_store import ToolExecutionEntry, TaskInfo
from app.core.llm.llm_response_result import ResponseResult, ResponseStatus


# Pflichtfelder für ToolExecutionEntry (DebugStore, ToolExecutionView)
REQUIRED_TOOL_EXECUTION_FIELDS = ["tool_name", "status", "agent_name", "task_id", "timestamp", "error"]


@pytest.mark.contract
def test_tool_execution_entry_has_required_fields():
    """ToolExecutionEntry hat alle Felder, die DebugStore und UI erwarten."""
    entry = ToolExecutionEntry(
        tool_name="list_dir",
        status="completed",
        agent_name="Chat",
    )
    for field in REQUIRED_TOOL_EXECUTION_FIELDS:
        assert hasattr(entry, field), f"ToolExecutionEntry fehlt Feld '{field}'"


@pytest.mark.contract
def test_tool_execution_entry_status_values():
    """ToolExecutionEntry.status akzeptiert started, completed, failed."""
    for status in ("started", "completed", "failed"):
        entry = ToolExecutionEntry(tool_name="x", status=status)
        assert entry.status == status


@pytest.mark.contract
def test_task_info_has_required_fields():
    """TaskInfo hat alle Felder, die DebugStore und AgentActivityView erwarten."""
    info = TaskInfo(
        task_id="t1",
        description="desc",
        agent_name="A",
        status="completed",
        error=None,
    )
    assert hasattr(info, "task_id")
    assert hasattr(info, "description")
    assert hasattr(info, "agent_name")
    assert hasattr(info, "status")
    assert hasattr(info, "error")
    assert info.status in ("pending", "running", "completed", "failed")


# ResponseResult – Vertrag für OutputPipeline → ChatWidget
REQUIRED_RESPONSE_RESULT_FIELDS = [
    "raw_text", "cleaned_text", "status", "error_message",
    "is_success", "display_text",
]


@pytest.mark.contract
def test_response_result_has_required_fields():
    """ResponseResult hat alle Felder, die ChatWidget und Pipeline erwarten."""
    result = ResponseResult(
        raw_text="x",
        cleaned_text="x",
        status=ResponseStatus.SUCCESS,
    )
    assert hasattr(result, "raw_text")
    assert hasattr(result, "cleaned_text")
    assert hasattr(result, "status")
    assert hasattr(result, "display_text")
    assert callable(result.display_text)
    assert callable(result.is_success)


@pytest.mark.contract
def test_response_result_display_text_on_success():
    """display_text() liefert cleaned_text bei Erfolg."""
    result = ResponseResult(
        raw_text="<p>Hi</p>",
        cleaned_text="Hi",
        status=ResponseStatus.SUCCESS,
    )
    assert result.display_text() == "Hi"


@pytest.mark.contract
def test_response_result_display_text_on_failure():
    """display_text() liefert error_message bei Fehler."""
    result = ResponseResult(
        raw_text="",
        cleaned_text="",
        status=ResponseStatus.FAILED,
        error_message="Ollama nicht erreichbar",
    )
    assert result.display_text() == "Ollama nicht erreichbar"


@pytest.mark.contract
def test_response_status_values_stable():
    """ResponseStatus-Enum-Werte sind stabil für Pipeline und UI."""
    assert ResponseStatus.SUCCESS.value == "success"
    assert ResponseStatus.FAILED.value == "failed"
    assert ResponseStatus.THINKING_ONLY.value == "thinking_only"
    assert ResponseStatus.EMPTY.value == "empty"
