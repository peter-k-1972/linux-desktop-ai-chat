"""SQLite-Persistenz für Workflows und Runs."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.workflows.models.definition import WorkflowDefinition
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.models.run_summary import WorkflowRunSummary
from app.workflows.status import NodeRunStatus, WorkflowRunStatus

logger = logging.getLogger(__name__)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _loads(s: Optional[str]) -> Any:
    if s is None or s == "":
        return None
    return json.loads(s)


def _definition_from_json_dict(raw: Any) -> Optional[WorkflowDefinition]:
    """Liest eine Definition aus JSON-Daten; bei defekten Daten None (kein Abbruch der ganzen Liste)."""
    if not isinstance(raw, dict):
        return None
    try:
        return WorkflowDefinition.from_dict(raw)
    except Exception as e:
        logger.warning("WorkflowDefinition konnte nicht gelesen werden: %s", e)
        return None


def _definition_from_row(row: sqlite3.Row) -> Optional[WorkflowDefinition]:
    """JSON parsen; project_id-Spalte nur nutzen, wenn JSON keinen project_id-Schlüssel hat (Migration)."""
    raw = _loads(row["definition_json"])
    if not isinstance(raw, dict):
        raw = {}
    d = _definition_from_json_dict(raw)
    if d is None:
        return None
    has_json_project_key = "project_id" in raw
    keys = row.keys()
    col_pid = row["project_id"] if "project_id" in keys else None
    if not has_json_project_key and col_pid is not None:
        try:
            d.project_id = int(col_pid)
        except (TypeError, ValueError):
            pass
    return d


class WorkflowRepository:
    """CRUD für workflows, workflow_runs, workflow_node_runs."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def save_workflow(self, definition: WorkflowDefinition) -> None:
        data = definition.to_dict()
        blob = _dumps(data)
        now = _utc_iso()
        created = data.get("created_at") or now
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO workflows (
                    workflow_id, name, description, version, schema_version,
                    definition_status, definition_json, created_at, updated_at, project_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workflow_id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    version = excluded.version,
                    schema_version = excluded.schema_version,
                    definition_status = excluded.definition_status,
                    definition_json = excluded.definition_json,
                    updated_at = excluded.updated_at,
                    project_id = excluded.project_id
                """,
                (
                    definition.workflow_id,
                    definition.name,
                    definition.description,
                    definition.version,
                    definition.schema_version,
                    definition.status.value,
                    blob,
                    created,
                    now,
                    definition.project_id,
                ),
            )
            conn.commit()

    def load_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT definition_json, project_id FROM workflows WHERE workflow_id = ?",
                (workflow_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return _definition_from_row(row)

    def list_workflows(
        self,
        *,
        project_scope_id: Optional[int] = None,
        include_global: bool = True,
    ) -> List[WorkflowDefinition]:
        """
        Liste gespeicherter Workflows.

        - project_scope_id None: alle Workflows (kein aktives Projekt / volle Liste).
        - project_scope_id gesetzt + include_global: dieses Projekt + globale (project_id IS NULL).
        - project_scope_id gesetzt + not include_global: nur dieses Projekt.
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if project_scope_id is None:
                cursor.execute(
                    "SELECT definition_json, project_id FROM workflows ORDER BY updated_at DESC"
                )
            elif include_global:
                cursor.execute(
                    """
                    SELECT definition_json, project_id FROM workflows
                    WHERE project_id IS NULL OR project_id = ?
                    ORDER BY updated_at DESC
                    """,
                    (project_scope_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT definition_json, project_id FROM workflows
                    WHERE project_id = ?
                    ORDER BY updated_at DESC
                    """,
                    (project_scope_id,),
                )
            out: List[WorkflowDefinition] = []
            for row in cursor.fetchall():
                d = _definition_from_row(row)
                if d is not None:
                    out.append(d)
            return out

    def delete_workflow(self, workflow_id: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM workflows WHERE workflow_id = ?", (workflow_id,))
            existed = cursor.fetchone() is not None
            cursor.execute("SELECT run_id FROM workflow_runs WHERE workflow_id = ?", (workflow_id,))
            run_ids = [r[0] for r in cursor.fetchall()]
            for rid in run_ids:
                cursor.execute("DELETE FROM workflow_node_runs WHERE run_id = ?", (rid,))
            cursor.execute("DELETE FROM workflow_runs WHERE workflow_id = ?", (workflow_id,))
            cursor.execute(
                "DELETE FROM schedule_run_log WHERE schedule_id IN "
                "(SELECT schedule_id FROM workflow_schedules WHERE workflow_id = ?)",
                (workflow_id,),
            )
            cursor.execute("DELETE FROM workflow_schedules WHERE workflow_id = ?", (workflow_id,))
            cursor.execute("DELETE FROM workflows WHERE workflow_id = ?", (workflow_id,))
            conn.commit()
            return existed

    def save_run(self, run: WorkflowRun) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO workflow_runs (
                    run_id, workflow_id, workflow_version, status,
                    initial_input_json, final_output_json, error_message,
                    definition_snapshot_json, created_at, started_at, finished_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.workflow_id,
                    run.workflow_version,
                    run.status.value,
                    _dumps(run.initial_input),
                    _dumps(run.final_output) if run.final_output is not None else None,
                    run.error_message,
                    _dumps(run.definition_snapshot),
                    (run.created_at or datetime.now(timezone.utc)).isoformat()
                    if run.created_at
                    else _utc_iso(),
                    run.started_at.isoformat() if run.started_at else None,
                    run.finished_at.isoformat() if run.finished_at else None,
                ),
            )
            conn.commit()

    def update_run(self, run: WorkflowRun) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE workflow_runs SET
                    status = ?,
                    final_output_json = ?,
                    error_message = ?,
                    started_at = ?,
                    finished_at = ?
                WHERE run_id = ?
                """,
                (
                    run.status.value,
                    _dumps(run.final_output) if run.final_output is not None else None,
                    run.error_message,
                    run.started_at.isoformat() if run.started_at else None,
                    run.finished_at.isoformat() if run.finished_at else None,
                    run.run_id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Run nicht gefunden: {run.run_id!r}")
            conn.commit()

    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workflow_runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            run = self._row_to_run(row)
            run.node_runs = self.list_node_runs(run_id)
            return run

    def list_runs(self, workflow_id: Optional[str] = None) -> List[WorkflowRun]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if workflow_id:
                cursor.execute(
                    "SELECT * FROM workflow_runs WHERE workflow_id = ? ORDER BY created_at DESC",
                    (workflow_id,),
                )
            else:
                cursor.execute("SELECT * FROM workflow_runs ORDER BY created_at DESC")
            runs = [self._row_to_run(row) for row in cursor.fetchall()]
        for r in runs:
            r.node_runs = self.list_node_runs(r.run_id)
        return runs

    def list_run_summaries(
        self,
        workflow_id: Optional[str] = None,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[WorkflowRunSummary]:
        """
        Run-Übersicht mit Workflow-Metadaten; **ohne** NodeRuns.

        Filter: ``workflow_id`` und/oder ``project_id`` (exakt auf ``workflows.project_id``).
        Keine Filter = alle Runs (über INNER JOIN nur solche mit existierender Workflow-Zeile).
        """
        sql = """
            SELECT
                wr.run_id,
                wr.workflow_id,
                wr.workflow_version,
                wr.status,
                wr.created_at,
                wr.started_at,
                wr.finished_at,
                wr.error_message,
                w.name AS workflow_name,
                w.project_id AS workflow_project_id
            FROM workflow_runs wr
            INNER JOIN workflows w ON w.workflow_id = wr.workflow_id
            WHERE 1=1
        """
        params: List[Any] = []
        if workflow_id is not None:
            sql += " AND wr.workflow_id = ?"
            params.append(workflow_id)
        if project_id is not None:
            sql += " AND w.project_id = ?"
            params.append(int(project_id))
        if status is not None and str(status).strip():
            sql += " AND wr.status = ?"
            params.append(str(status).strip())
        sql += """
            ORDER BY datetime(
                COALESCE(wr.finished_at, wr.started_at, wr.created_at)
            ) DESC
        """
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([int(limit), int(offset)])

        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        out: List[WorkflowRunSummary] = []
        for row in rows:
            pid = row["workflow_project_id"]
            if pid is None:
                proj: Optional[int] = None
            else:
                try:
                    proj = int(pid)
                except (TypeError, ValueError):
                    proj = None
            st_raw = row["status"]
            try:
                run_st = WorkflowRunStatus(str(st_raw))
                st_val = run_st.value
            except ValueError:
                st_val = str(st_raw) if st_raw is not None else WorkflowRunStatus.PENDING.value
            out.append(
                WorkflowRunSummary(
                    run_id=str(row["run_id"]),
                    workflow_id=str(row["workflow_id"]),
                    workflow_name=str(row["workflow_name"] or ""),
                    workflow_version=int(row["workflow_version"] or 0),
                    project_id=proj,
                    status=st_val,
                    created_at=_parse_iso(row["created_at"]),
                    started_at=_parse_iso(row["started_at"]),
                    finished_at=_parse_iso(row["finished_at"]),
                    error_message=row["error_message"],
                )
            )
        return out

    def aggregate_project_workflow_runs(self, project_id: int) -> Dict[str, Any]:
        """
        Monitoring: nur Runs von Workflows mit ``workflows.project_id = project_id``.
        Globale Workflows (project_id IS NULL) werden nicht einbezogen.
        """
        pid = int(project_id)
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT wr.status,
                       COALESCE(wr.finished_at, wr.started_at, wr.created_at) AS run_ts
                FROM workflow_runs wr
                INNER JOIN workflows w ON w.workflow_id = wr.workflow_id
                WHERE w.project_id = ?
                ORDER BY datetime(
                    COALESCE(wr.finished_at, wr.started_at, wr.created_at)
                ) DESC
                LIMIT 1
                """,
                (pid,),
            )
            row = cursor.fetchone()
            last_status: Optional[str] = row[0] if row else None
            last_ts: Optional[str] = row[1] if row else None

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM workflow_runs wr
                INNER JOIN workflows w ON w.workflow_id = wr.workflow_id
                WHERE w.project_id = ?
                  AND wr.status = ?
                  AND datetime(COALESCE(wr.finished_at, wr.started_at, wr.created_at))
                      >= datetime('now', '-30 days')
                """,
                (pid, WorkflowRunStatus.FAILED.value),
            )
            failed_30d = int(cursor.fetchone()[0] or 0)

        return {
            "last_workflow_run_at": last_ts,
            "last_workflow_run_status": last_status,
            "failed_workflow_runs_30d": failed_30d,
        }

    def _row_to_run(self, row: sqlite3.Row) -> WorkflowRun:
        snap = _loads(row["definition_snapshot_json"])
        if not isinstance(snap, dict):
            snap = {}
        init_in = _loads(row["initial_input_json"])
        if not isinstance(init_in, dict):
            init_in = {}
        final_out = _loads(row["final_output_json"])
        if final_out is not None and not isinstance(final_out, dict):
            final_out = None
        try:
            run_st = WorkflowRunStatus(str(row["status"]))
        except ValueError:
            logger.warning("Unbekannter workflow_run status %r – verwende pending.", row["status"])
            run_st = WorkflowRunStatus.PENDING
        return WorkflowRun(
            run_id=str(row["run_id"]),
            workflow_id=str(row["workflow_id"]),
            workflow_version=int(row["workflow_version"]),
            status=run_st,
            created_at=_parse_iso(row["created_at"]),
            started_at=_parse_iso(row["started_at"]),
            finished_at=_parse_iso(row["finished_at"]),
            initial_input=init_in,
            final_output=final_out,
            error_message=row["error_message"],
            definition_snapshot=snap,
            node_runs=[],
        )

    def save_node_run(self, node_run: NodeRun) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO workflow_node_runs (
                    node_run_id, run_id, node_id, node_type, status,
                    input_payload_json, output_payload_json, error_message,
                    retry_count, started_at, finished_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node_run.node_run_id,
                    node_run.run_id,
                    node_run.node_id,
                    node_run.node_type,
                    node_run.status.value,
                    _dumps(node_run.input_payload) if node_run.input_payload is not None else None,
                    _dumps(node_run.output_payload) if node_run.output_payload is not None else None,
                    node_run.error_message,
                    node_run.retry_count,
                    node_run.started_at.isoformat() if node_run.started_at else None,
                    node_run.finished_at.isoformat() if node_run.finished_at else None,
                ),
            )
            conn.commit()

    def update_node_run(self, node_run: NodeRun) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE workflow_node_runs SET
                    status = ?,
                    input_payload_json = ?,
                    output_payload_json = ?,
                    error_message = ?,
                    retry_count = ?,
                    started_at = ?,
                    finished_at = ?
                WHERE node_run_id = ?
                """,
                (
                    node_run.status.value,
                    _dumps(node_run.input_payload) if node_run.input_payload is not None else None,
                    _dumps(node_run.output_payload) if node_run.output_payload is not None else None,
                    node_run.error_message,
                    node_run.retry_count,
                    node_run.started_at.isoformat() if node_run.started_at else None,
                    node_run.finished_at.isoformat() if node_run.finished_at else None,
                    node_run.node_run_id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"NodeRun nicht gefunden: {node_run.node_run_id!r}")
            conn.commit()

    def list_node_runs(self, run_id: str) -> List[NodeRun]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM workflow_node_runs WHERE run_id = ?
                ORDER BY
                    (started_at IS NULL) ASC,
                    started_at ASC,
                    node_run_id ASC
                """,
                (run_id,),
            )
            return [self._row_to_node_run(row) for row in cursor.fetchall()]

    def _row_to_node_run(self, row: sqlite3.Row) -> NodeRun:
        inp = _loads(row["input_payload_json"])
        out = _loads(row["output_payload_json"])
        try:
            nst = NodeRunStatus(str(row["status"]))
        except ValueError:
            logger.warning("Unbekannter node_run status %r – verwende pending.", row["status"])
            nst = NodeRunStatus.PENDING
        return NodeRun(
            node_run_id=str(row["node_run_id"]),
            run_id=str(row["run_id"]),
            node_id=str(row["node_id"]),
            node_type=str(row["node_type"]),
            status=nst,
            started_at=_parse_iso(row["started_at"]),
            finished_at=_parse_iso(row["finished_at"]),
            input_payload=dict(inp) if isinstance(inp, dict) else None,
            output_payload=dict(out) if isinstance(out, dict) else None,
            error_message=row["error_message"],
            retry_count=int(row["retry_count"] or 0),
        )


def _parse_iso(raw: Optional[str]) -> Optional[datetime]:
    if raw is None:
        return None
    s = str(raw).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None
