"""
Semantik und Datenintegrität beim Projektlöschen (DatabaseManager / ProjectService).
"""

import json
import os
import sqlite3
import tempfile

import pytest

from app.core.context.project_context_manager import ProjectContextManager, set_project_context_manager
from app.agents.agent_repository import AgentRepository
from app.core.db.database_manager import DatabaseManager
from app.prompts.prompt_models import Prompt
from app.prompts.prompt_repository import PromptRepository
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.knowledge_service import KnowledgeService, set_knowledge_service
from app.services.project_service import ProjectService, set_project_service
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.persistence.workflow_repository import WorkflowRepository


@pytest.fixture
def tmp_paths():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    rag_root = tempfile.mkdtemp()
    yield db_path, rag_root
    try:
        os.unlink(db_path)
    except OSError:
        pass
    import shutil

    shutil.rmtree(rag_root, ignore_errors=True)


def test_database_delete_project_sqlite_semantics(tmp_paths):
    db_path, _rag = tmp_paths
    db = DatabaseManager(db_path, ensure_default_project=False)
    WorkflowRepository(db_path)
    PromptRepository(db_path)
    AgentRepository(db_path)

    pid = db.create_project("DelProj", "", "active")
    cid = db.create_chat("Chat1")
    db.add_chat_to_project(pid, cid, None)
    tid = db.create_topic(pid, "TopicA")
    assert tid > 0

    fid = db.get_or_create_file("/tmp/x.txt", "x", "text")
    db.add_file_to_project(pid, fid)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO agents (id, name, slug, department, status, project_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("ag_test", "Agent", "ag-test", "general", "active", pid),
        )
        conn.commit()

    pr = PromptRepository(db_path)
    pr.create(
        Prompt(
            id=None,
            title="P1",
            category="general",
            description="",
            content="c",
            tags=[],
            prompt_type="user",
            scope="project",
            project_id=pid,
            created_at=None,
            updated_at=None,
        )
    )

    wf = WorkflowDefinition(
        workflow_id="wf_del",
        name="W",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[WorkflowEdge("x", "s", "e")],
        project_id=pid,
    )
    WorkflowRepository(db_path).save_workflow(wf)

    db.delete_project(pid)

    assert db.get_project(pid) is None
    assert db.get_project_of_chat(cid) is None
    assert len(db.list_topics_for_project(pid)) == 0

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        n = conn.execute("SELECT COUNT(*) FROM project_files WHERE project_id = ?", (pid,)).fetchone()[0]
        assert n == 0
        row = conn.execute("SELECT project_id FROM prompts WHERE title = ?", ("P1",)).fetchone()
        assert row is not None
        assert row["project_id"] is None
        row = conn.execute("SELECT project_id FROM agents WHERE id = ?", ("ag_test",)).fetchone()
        assert row["project_id"] is None
        row = conn.execute(
            "SELECT project_id, definition_json FROM workflows WHERE workflow_id = ?",
            ("wf_del",),
        ).fetchone()
        assert row["project_id"] is None
        data = json.loads(row["definition_json"])
        assert data.get("project_id") is None


def test_project_service_clears_active_and_rag_folder(tmp_paths):
    db_path, rag_root = tmp_paths
    db = DatabaseManager(db_path, ensure_default_project=False)
    WorkflowRepository(db_path)

    pid = db.create_project("ActiveDel", "", "active")

    infra = _ServiceInfrastructure()
    infra._db = db
    set_infrastructure(infra)
    set_project_service(None)
    set_knowledge_service(KnowledgeService(rag_root))

    space = KnowledgeService(rag_root).get_space_for_project(pid)
    space_dir = KnowledgeService(rag_root).base_path / space
    space_dir.mkdir(parents=True)
    (space_dir / "sources.json").write_text("[]", encoding="utf-8")

    set_project_context_manager(ProjectContextManager())
    from app.core.context.project_context_manager import get_project_context_manager

    get_project_context_manager().set_active_project(pid)
    assert get_project_context_manager().get_active_project_id() == pid

    ProjectService().delete_project(pid)

    assert get_project_context_manager().get_active_project_id() is None
    assert not space_dir.exists()

    set_project_context_manager(None)
    set_knowledge_service(None)
    set_project_service(None)
    set_infrastructure(None)
