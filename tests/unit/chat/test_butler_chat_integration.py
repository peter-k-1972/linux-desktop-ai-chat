"""Tests: Butler-Chat-Trigger und Antwortformat."""

from __future__ import annotations

import pytest

from app.chat.butler_chat_integration import (
    build_butler_optional_context,
    format_butler_result_as_chat_message,
    should_activate_butler_for_chat_message,
)
from app.services.project_butler_service import classify_user_request
from app.workflows.butler_support_definitions import WORKFLOW_ID_ANALYZE_DECIDE_DOCUMENT
from app.workflows.dev_assist_definition import WORKFLOW_ID as WORKFLOW_ID_DEV_ASSIST


def test_trigger_bugfix_message():
    use, req = should_activate_butler_for_chat_message("Kannst du den Login-Bug fixen?")
    assert use is True
    assert "Login-Bug" in req


def test_trigger_analysis_message():
    use, req = should_activate_butler_for_chat_message("Bitte analysiere die Service-Schicht")
    assert use is True
    assert "analysiere" in req.lower()


def test_trigger_butler_prefix():
    use, req = should_activate_butler_for_chat_message("/butler Erkläre kurz das Modul")
    assert use is True
    assert req.startswith("Erkläre")


def test_normal_smalltalk_no_butler():
    use, req = should_activate_butler_for_chat_message("Wie war dein Wochenende?")
    assert use is False
    assert req == "Wie war dein Wochenende?"


def test_trigger_warum():
    use, req = should_activate_butler_for_chat_message("Warum wird hier dieser Kontext geladen?")
    assert use is True
    assert "Kontext" in req


def test_chat_bugfix_triggers_butler_and_classifies_dev_assist():
    use, req = should_activate_butler_for_chat_message("Bitte den Parser-Bug fixen")
    assert use is True
    wf_id, _reason = classify_user_request(req)
    assert wf_id == WORKFLOW_ID_DEV_ASSIST


def test_chat_analyse_triggers_butler_and_classifies_analyze_workflow():
    use, req = should_activate_butler_for_chat_message("Analysiere die Modulgrenzen")
    assert use is True
    wf_id, _reason = classify_user_request(req)
    assert wf_id == WORKFLOW_ID_ANALYZE_DECIDE_DOCUMENT


def test_build_butler_optional_context_includes_chat_id(monkeypatch):
    monkeypatch.setattr(
        "app.chat.butler_chat_integration.resolve_workspace_root_for_butler",
        lambda _cid: "/tmp/ws",
    )
    ctx = build_butler_optional_context(7)
    assert ctx == {"chat_id": 7, "workspace_root": "/tmp/ws"}


def test_build_butler_optional_context_chat_id_only(monkeypatch):
    monkeypatch.setattr(
        "app.chat.butler_chat_integration.resolve_workspace_root_for_butler",
        lambda _cid: None,
    )
    ctx = build_butler_optional_context(42)
    assert ctx == {"chat_id": 42}


def test_format_no_workflow_matched():
    text = format_butler_result_as_chat_message(
        {
            "selected_workflow": None,
            "reasoning": "Keine Keywords.",
            "result": {"outcome": "no_workflow_matched", "detail": "Keine Keywords."},
        }
    )
    assert "Project Butler" in text
    assert "project butler konnte keine passende aufgabe erkennen" in text.lower()
    assert "keine keywords" in text.lower()


def test_format_workflow_service_error():
    text = format_butler_result_as_chat_message(
        {
            "selected_workflow": "workflow.dev_assist.analyze_modify_test_review",
            "reasoning": "Treffer: fix",
            "result": {"outcome": "error", "error": "workflow_not_found", "detail": "fehlt in DB"},
        }
    )
    assert "Project Butler" in text
    assert "Fehler:" in text
    assert "fehlt in DB" in text


def test_format_dev_assist_sections():
    text = format_butler_result_as_chat_message(
        {
            "selected_workflow": "workflow.dev_assist.analyze_modify_test_review",
            "reasoning": "Treffer: fix",
            "result": {
                "outcome": "workflow_finished",
                "status": "completed",
                "final_output": {
                    "analysis": "Risiko gering.",
                    "plan": "Konstante ändern.",
                    "review": "OK.",
                    "documentation": "Hinweis im README.",
                    "patch_applied": True,
                    "test_results": "2 passed",
                },
            },
        }
    )
    assert "dev_assist.analyze_modify_test_review" in text
    assert "Analyse" in text
    assert "Plan" in text
    assert "Review" in text
    assert "Dokumentation" in text
    assert "2 passed" in text


def test_disable_butler_env(monkeypatch):
    monkeypatch.setenv("LINUX_DESKTOP_CHAT_DISABLE_BUTLER", "1")
    use, _ = should_activate_butler_for_chat_message("fix everything")
    assert use is False
    monkeypatch.delenv("LINUX_DESKTOP_CHAT_DISABLE_BUTLER", raising=False)
