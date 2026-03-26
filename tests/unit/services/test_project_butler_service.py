"""Unit-Tests: Project Butler (Klassifikation und Orchestrierung)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.agents.agent_repository import AgentRepository
from app.agents.seed_agents import ensure_seed_agents
from app.core.db.database_manager import DatabaseManager
from app.services.project_butler_service import (
    AGENT_ID_PROJECT_BUTLER,
    ProjectButlerService,
    WORKFLOW_ID_ANALYZE_DECIDE_DOCUMENT,
    WORKFLOW_ID_CONTEXT_INSPECT,
    classify_user_request,
)
from app.services.workflow_service import WorkflowService, reset_workflow_service
from app.workflows.butler_support_definitions import (
    all_butler_support_definitions,
    build_analyze_decide_document_workflow_definition,
    build_context_inspect_workflow_definition,
)
from app.workflows.dev_assist_definition import WORKFLOW_ID as WORKFLOW_ID_DEV_ASSIST
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.registry.node_registry import build_default_node_registry
from app.workflows.status import WorkflowRunStatus
from app.workflows.validation.graph_validator import GraphValidator


@pytest.fixture
def workflow_service(tmp_path):
    db_path = str(tmp_path / "butler_wf.db")
    DatabaseManager(db_path, ensure_default_project=False)
    ensure_seed_agents(AgentRepository(db_path))
    reset_workflow_service()
    svc = WorkflowService(WorkflowRepository(db_path))
    for d in all_butler_support_definitions():
        vr = svc.save_workflow(d)
        assert vr.is_valid, vr.errors
    yield svc
    reset_workflow_service()


def test_classify_bugfix_selects_dev_assist():
    wf, reason = classify_user_request("Bitte den Login-Bug fixen")
    assert wf == WORKFLOW_ID_DEV_ASSIST
    assert "fix" in reason.lower() or "treffer" in reason.lower()


def test_classify_analysis_selects_analyze_workflow():
    wf, reason = classify_user_request("Analysiere die Modulgrenzen und erkläre Abhängigkeiten")
    assert wf == WORKFLOW_ID_ANALYZE_DECIDE_DOCUMENT
    assert "analysiere" in reason.lower() or "erkläre" in reason.lower()


def test_classify_unknown_is_fallback():
    wf, reason = classify_user_request("Hallo, wie geht es dir?")
    assert wf is None
    assert "keine" in reason.lower() or "präzisieren" in reason.lower()


def test_butler_runs_analyze_workflow(workflow_service):
    butler = ProjectButlerService(workflow_service)
    out = butler.handle("Bewerte die Architektur der Serviceschicht")
    assert out["selected_workflow"] == WORKFLOW_ID_ANALYZE_DECIDE_DOCUMENT
    res = out["result"]
    assert res["outcome"] == "workflow_finished"
    assert res["status"] == WorkflowRunStatus.COMPLETED.value
    fo = res.get("final_output") or {}
    assert fo.get("phase") == "analyze_decide_document"


def test_butler_fallback_no_run(workflow_service):
    butler = ProjectButlerService(workflow_service)
    out = butler.handle("xyzabc keine passenden wörter")
    assert out["selected_workflow"] is None
    assert out["result"]["outcome"] == "no_workflow_matched"


def test_butler_context_inspect_workflow(workflow_service):
    d = build_context_inspect_workflow_definition()
    assert GraphValidator().validate(d, build_default_node_registry()).is_valid
    butler = ProjectButlerService(workflow_service)
    out = butler.handle("Warum wurde dieser Kontext so aufgebaut?")
    assert out["selected_workflow"] == WORKFLOW_ID_CONTEXT_INSPECT
    fo = (out.get("result") or {}).get("final_output") or {}
    assert fo.get("phase") == "context_inspect"


def test_butler_workflow_not_registered_returns_error():
    mock_svc = MagicMock()
    from app.services.workflow_service import WorkflowNotFoundError

    mock_svc.start_run.side_effect = WorkflowNotFoundError("workflow.x")
    butler = ProjectButlerService(mock_svc)
    out = butler.handle("fix the parser bug")
    assert out["selected_workflow"] == WORKFLOW_ID_DEV_ASSIST
    assert out["result"]["outcome"] == "error"
    assert out["result"]["error"] == "workflow_not_found"


def test_seed_includes_project_butler_id():
    """Profil nutzt feste ID für Dokumentation / Routing."""
    from app.agents.seed_agents import _seed_profiles

    profiles = _seed_profiles()
    butlers = [p for p in profiles if p.slug == "project_butler"]
    assert len(butlers) == 1
    assert butlers[0].id == AGENT_ID_PROJECT_BUTLER


def test_analyze_definition_validates():
    d = build_analyze_decide_document_workflow_definition()
    vr = GraphValidator().validate(d, build_default_node_registry())
    assert vr.is_valid, vr.errors
