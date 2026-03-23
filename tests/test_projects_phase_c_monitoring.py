"""Phase C: operatives Projekt-Monitoring (Chats, Workflow-Runs, Quellenanzahl)."""

from __future__ import annotations

import json
import sqlite3

from app.core.db.database_manager import DatabaseManager
from app.services.project_service import ProjectService
from app.services.workflow_service import reset_workflow_service
from app.workflows.persistence.workflow_repository import WorkflowRepository


def _fake_infra(db: DatabaseManager):
    return type("I", (), {"database": db})()


def _patch_infra(monkeypatch, db: DatabaseManager) -> None:
    fake = _fake_infra(db)
    monkeypatch.setattr("app.services.project_service.get_infrastructure", lambda: fake)
    monkeypatch.setattr("app.services.infrastructure.get_infrastructure", lambda: fake)


def test_c1_empty_project_snapshot(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "c1e.db"), ensure_default_project=False)
    pid = db.create_project("Leer")
    _patch_infra(monkeypatch, db)
    svc = ProjectService()
    snap = svc.get_project_monitoring_snapshot(pid)
    assert snap["last_activity_at"] is None
    assert snap["message_count_7d"] == 0
    assert snap["message_count_30d"] == 0
    assert snap["active_chats_30d"] == 0
    assert snap["last_workflow_run_at"] is None
    assert snap["last_workflow_run_status"] is None
    assert snap["failed_workflow_runs_30d"] == 0
    assert snap["source_count"] == 0
    assert "keine quellen" in snap["knowledge_hint"].lower()


def test_c1_activity_aggregation(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "c1a.db"), ensure_default_project=False)
    pid = db.create_project("P1")
    c1 = db.create_chat("C1")
    c2 = db.create_chat("C2")
    db.add_chat_to_project(pid, c1)
    db.add_chat_to_project(pid, c2)
    # Chat ohne Projekt – darf nicht zählen
    c_other = db.create_chat("Other")
    db.save_message(c_other, "user", "orphan")

    now_expr = "datetime('now')"
    with sqlite3.connect(db.db_path) as conn:
        conn.execute(
            f"INSERT INTO messages (chat_id, role, content, timestamp) VALUES (?, 'user', 'm1', {now_expr})",
            (c1,),
        )
        conn.execute(
            "INSERT INTO messages (chat_id, role, content, timestamp) VALUES (?, 'user', 'm2', datetime('now', '-5 days'))",
            (c1,),
        )
        conn.execute(
            "INSERT INTO messages (chat_id, role, content, timestamp) VALUES (?, 'user', 'm3', datetime('now', '-20 days'))",
            (c2,),
        )
        conn.execute(
            "INSERT INTO messages (chat_id, role, content, timestamp) VALUES (?, 'user', 'old', datetime('now', '-40 days'))",
            (c2,),
        )
        conn.commit()

    _patch_infra(monkeypatch, db)
    reset_workflow_service()
    svc = ProjectService()
    snap = svc.get_project_monitoring_snapshot(pid)

    assert snap["last_activity_at"] is not None
    assert snap["message_count_7d"] == 2  # m1 + m2
    assert snap["message_count_30d"] == 3  # m1, m2, m3
    assert snap["active_chats_30d"] == 2  # c1 und c2 mit Msg in 30d

    assert db.get_project_last_activity(pid) == snap["last_activity_at"]
    assert db.count_project_messages_in_days(pid, 7) == 2
    assert db.count_project_messages_in_days(pid, 30) == 3
    assert db.count_active_project_chats_in_days(pid, 30) == 2


def _insert_workflow(
    conn: sqlite3.Connection,
    workflow_id: str,
    project_id: int | None,
    *,
    now: str = "2026-01-01T00:00:00+00:00",
) -> None:
    definition = {"workflow_id": workflow_id, "name": workflow_id, "version": 1}
    conn.execute(
        """
        INSERT INTO workflows (
            workflow_id, name, description, version, schema_version,
            definition_status, definition_json, created_at, updated_at, project_id
        ) VALUES (?, ?, '', 1, 1, 'valid', ?, ?, ?, ?)
        """,
        (
            workflow_id,
            workflow_id,
            json.dumps(definition),
            now,
            now,
            project_id,
        ),
    )


def test_c2_repository_project_scope_last_run_and_failed_window(tmp_path):
    db = DatabaseManager(str(tmp_path / "c2r.db"), ensure_default_project=False)
    pa = db.create_project("A")
    pb = db.create_project("B")
    base = "2026-01-01T00:00:00+00:00"
    with sqlite3.connect(db.db_path) as conn:
        _insert_workflow(conn, "wf_a", pa, now=base)
        _insert_workflow(conn, "wf_b", pb, now=base)
        _insert_workflow(conn, "wf_global", None, now=base)
        conn.execute(
            """
            INSERT INTO workflow_runs (
                run_id, workflow_id, workflow_version, status,
                initial_input_json, definition_snapshot_json,
                created_at, started_at, finished_at
            ) VALUES ('r_old', 'wf_a', 1, 'completed', '{}', '{}',
                datetime('now', '-20 days'), datetime('now', '-20 days'), datetime('now', '-20 days'))
            """
        )
        conn.execute(
            """
            INSERT INTO workflow_runs (
                run_id, workflow_id, workflow_version, status,
                initial_input_json, definition_snapshot_json,
                created_at, started_at, finished_at
            ) VALUES ('r_new', 'wf_a', 1, 'failed', '{}', '{}',
                datetime('now', '-1 days'), datetime('now', '-1 days'), datetime('now', '-1 days'))
            """
        )
        conn.execute(
            """
            INSERT INTO workflow_runs (
                run_id, workflow_id, workflow_version, status,
                initial_input_json, definition_snapshot_json,
                created_at, started_at, finished_at
            ) VALUES ('r_b', 'wf_b', 1, 'failed', '{}', '{}',
                datetime('now', '-2 hours'), datetime('now', '-2 hours'), datetime('now', '-2 hours'))
            """
        )
        conn.execute(
            """
            INSERT INTO workflow_runs (
                run_id, workflow_id, workflow_version, status,
                initial_input_json, definition_snapshot_json,
                created_at, started_at, finished_at
            ) VALUES ('r_g', 'wf_global', 1, 'failed', '{}', '{}',
                datetime('now', '-1 hours'), datetime('now', '-1 hours'), datetime('now', '-1 hours'))
            """
        )
        conn.execute(
            """
            INSERT INTO workflow_runs (
                run_id, workflow_id, workflow_version, status,
                initial_input_json, definition_snapshot_json,
                created_at, started_at, finished_at
            ) VALUES ('r_ancient_fail', 'wf_a', 1, 'failed', '{}', '{}',
                datetime('now', '-90 days'), datetime('now', '-90 days'), datetime('now', '-90 days'))
            """
        )
        conn.commit()

    repo = WorkflowRepository(db.db_path)
    agg = repo.aggregate_project_workflow_runs(pa)
    assert agg["last_workflow_run_status"] == "failed"
    assert agg["last_workflow_run_at"] is not None
    assert agg["failed_workflow_runs_30d"] == 1

    agg_b = repo.aggregate_project_workflow_runs(pb)
    assert agg_b["last_workflow_run_status"] == "failed"
    assert agg_b["failed_workflow_runs_30d"] == 1

    agg_empty = repo.aggregate_project_workflow_runs(99999)
    assert agg_empty["last_workflow_run_at"] is None
    assert agg_empty["failed_workflow_runs_30d"] == 0


def test_c2_project_service_snapshot_merges_workflow(tmp_path, monkeypatch):
    db = DatabaseManager(str(tmp_path / "c2s.db"), ensure_default_project=False)
    pid = db.create_project("Mon")
    base = "2026-01-01T00:00:00+00:00"
    with sqlite3.connect(db.db_path) as conn:
        _insert_workflow(conn, "wf_p", pid, now=base)
        conn.execute(
            """
            INSERT INTO workflow_runs (
                run_id, workflow_id, workflow_version, status,
                initial_input_json, definition_snapshot_json,
                created_at, started_at, finished_at
            ) VALUES ('r1', 'wf_p', 1, 'completed', '{}', '{}',
                datetime('now', '-3 days'), datetime('now', '-3 days'), datetime('now', '-3 days'))
            """
        )
        conn.commit()

    _patch_infra(monkeypatch, db)
    reset_workflow_service()
    svc = ProjectService()
    snap = svc.get_project_monitoring_snapshot(pid)
    assert snap["last_workflow_run_status"] == "completed"
    assert snap["failed_workflow_runs_30d"] == 0
    assert snap["last_workflow_run_at"] is not None
