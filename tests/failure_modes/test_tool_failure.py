"""
Failure Injection: Tool-Fehler in handle_tool_calls.

Simuliert: list_dir wirft Exception –
ChatWidget zeigt Fehlermeldung, crasht nicht, Event mit status "failed" wird emittiert.
"""

from unittest.mock import MagicMock, patch

import pytest

from tests.failure_modes.conftest import MinimalChatWidget, FakeDB, failure_settings


class FailingTools:
    """FileSystemTools-Mock der bei list_dir fehlschlägt."""

    def list_dir(self, path):
        raise PermissionError("Zugriff verweigert auf /restricted")


@pytest.mark.failure_mode
@pytest.mark.integration
def test_tool_exception_returns_error_text_instead_of_crashing(failure_settings):
    """
    Wenn list_dir Exception wirft: handle_tool_calls gibt Fehlermeldung zurück, crasht nicht.
    Verhindert: Unbehandelte Exception bricht Chat ab.
    """
    widget = MinimalChatWidget(MagicMock(), failure_settings, FakeDB())
    widget.tools = FailingTools()
    widget.db.list_workspace_roots_for_chat = lambda cid: []

    text = 'Vorher <tool_call name="list_dir"/> Nachher'
    result = widget.handle_tool_calls(text)

    assert "Fehler" in result or "Zugriff" in result or "PermissionError" in result
    assert "Vorher" in result
    assert "Nachher" in result


@pytest.mark.failure_mode
@pytest.mark.integration
def test_tool_exception_emits_failed_event(failure_settings):
    """
    Wenn Tool Exception wirft: emit_event wird mit status "failed" und error aufgerufen.
    Verhindert: Stiller Abbruch ohne Debug-Feedback.
    """
    captured = []

    def capture_emit(event_type, agent_name="", task_id=None, message="", metadata=None):
        captured.append((str(event_type), metadata or {}))

    widget = MinimalChatWidget(MagicMock(), failure_settings, FakeDB())
    widget.tools = FailingTools()
    widget.db.list_workspace_roots_for_chat = lambda cid: []

    with patch("app.gui.legacy.chat_widget.emit_event", side_effect=capture_emit):
        text = 'X <tool_call name="list_dir"/> Y'
        widget.handle_tool_calls(text)

    failed = [c for c in captured if c[1].get("status") == "failed"]
    assert len(failed) >= 1
    assert "error" in failed[0][1]
