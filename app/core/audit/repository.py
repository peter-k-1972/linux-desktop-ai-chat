"""SQLite-Zugriff für audit_events und incidents."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.audit.models import AuditEventRecord, IncidentRecord


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AuditRepository:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def append_audit_event(
        self,
        *,
        event_type: str,
        summary: str,
        actor: Optional[str] = "local",
        payload: Optional[Dict[str, Any]] = None,
        project_id: Optional[int] = None,
        workflow_id: Optional[str] = None,
        run_id: Optional[str] = None,
        incident_id: Optional[int] = None,
        occurred_at: Optional[str] = None,
    ) -> int:
        ts = occurred_at or _utc_iso()
        payload_json = json.dumps(payload, ensure_ascii=False) if payload else None
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO audit_events (
                    occurred_at, event_type, actor, summary, payload_json,
                    project_id, workflow_id, run_id, incident_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ts,
                    event_type,
                    actor,
                    summary,
                    payload_json,
                    project_id,
                    workflow_id,
                    run_id,
                    incident_id,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_audit_events(
        self,
        *,
        event_type: Optional[str] = None,
        project_id: Optional[int] = None,
        workflow_id: Optional[str] = None,
        run_id: Optional[str] = None,
        since_iso: Optional[str] = None,
        until_iso: Optional[str] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> List[AuditEventRecord]:
        clauses: List[str] = []
        params: List[Any] = []
        if event_type:
            clauses.append("event_type = ?")
            params.append(event_type)
        if project_id is not None:
            clauses.append("project_id = ?")
            params.append(project_id)
        if workflow_id:
            clauses.append("workflow_id = ?")
            params.append(workflow_id)
        if run_id:
            clauses.append("run_id = ?")
            params.append(run_id)
        if since_iso:
            clauses.append("occurred_at >= ?")
            params.append(since_iso)
        if until_iso:
            clauses.append("occurred_at <= ?")
            params.append(until_iso)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = (
            "SELECT id, occurred_at, event_type, actor, summary, payload_json, "
            "project_id, workflow_id, run_id, incident_id FROM audit_events"
            + where
            + " ORDER BY occurred_at DESC, id DESC LIMIT ? OFFSET ?"
        )
        params.extend([limit, offset])
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
        out: List[AuditEventRecord] = []
        for r in rows:
            out.append(
                AuditEventRecord(
                    id=int(r["id"]),
                    occurred_at=str(r["occurred_at"]),
                    event_type=str(r["event_type"]),
                    actor=r["actor"],
                    summary=str(r["summary"]),
                    payload_json=r["payload_json"],
                    project_id=r["project_id"],
                    workflow_id=r["workflow_id"],
                    run_id=r["run_id"],
                    incident_id=r["incident_id"],
                )
            )
        return out

    def get_incident_by_fingerprint(self, fingerprint: str) -> Optional[IncidentRecord]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM incidents WHERE fingerprint = ?", (fingerprint,))
            row = cur.fetchone()
        return self._row_to_incident(row) if row else None

    def insert_incident(self, rec: IncidentRecord) -> int:
        d = asdict(rec)
        d.pop("id", None)
        cols = ", ".join(d.keys())
        placeholders = ", ".join("?" * len(d))
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                f"INSERT INTO incidents ({cols}) VALUES ({placeholders})",
                tuple(d.values()),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_incident_recurrence(
        self,
        fingerprint: str,
        *,
        workflow_run_id: str,
        last_seen_at: str,
        updated_at: str,
        short_description: str,
    ) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE incidents SET
                    last_seen_at = ?,
                    updated_at = ?,
                    workflow_run_id = ?,
                    short_description = ?,
                    occurrence_count = occurrence_count + 1
                WHERE fingerprint = ?
                """,
                (last_seen_at, updated_at, workflow_run_id, short_description, fingerprint),
            )
            conn.commit()

    def get_incident(self, incident_id: int) -> Optional[IncidentRecord]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
            row = cur.fetchone()
        return self._row_to_incident(row) if row else None

    def update_incident_status(
        self,
        incident_id: int,
        *,
        status: str,
        resolution_note: Optional[str],
        updated_at: str,
    ) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE incidents SET status = ?, resolution_note = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, resolution_note, updated_at, incident_id),
            )
            conn.commit()

    def list_incidents(
        self,
        *,
        status: Optional[str] = None,
        project_id: Optional[int] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> List[IncidentRecord]:
        clauses: List[str] = []
        params: List[Any] = []
        if status:
            clauses.append("status = ?")
            params.append(status)
        if project_id is not None:
            clauses.append("project_id = ?")
            params.append(project_id)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = "SELECT * FROM incidents" + where + " ORDER BY last_seen_at DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [self._row_to_incident(r) for r in rows]

    @staticmethod
    def _row_to_incident(row: sqlite3.Row) -> IncidentRecord:
        return IncidentRecord(
            id=int(row["id"]),
            status=str(row["status"]),
            severity=str(row["severity"]),
            title=str(row["title"]),
            short_description=str(row["short_description"]),
            workflow_run_id=str(row["workflow_run_id"]),
            workflow_id=str(row["workflow_id"]),
            project_id=row["project_id"],
            first_seen_at=str(row["first_seen_at"]),
            last_seen_at=str(row["last_seen_at"]),
            occurrence_count=int(row["occurrence_count"]),
            fingerprint=str(row["fingerprint"]),
            diagnostic_code=row["diagnostic_code"],
            resolution_note=row["resolution_note"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )
