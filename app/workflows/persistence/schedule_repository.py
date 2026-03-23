"""SQLite: Workflow-Schedules, Claim und schedule_run_log."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from app.workflows.scheduling.models import (
    ScheduleRunLogEntry,
    ScheduleTriggerType,
    WorkflowSchedule,
)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_schedule(row: sqlite3.Row) -> WorkflowSchedule:
    keys = row.keys()
    claim = row["claim_until"] if "claim_until" in keys else None
    if claim == "":
        claim = None
    return WorkflowSchedule(
        schedule_id=row["schedule_id"],
        workflow_id=row["workflow_id"],
        enabled=bool(row["enabled"]),
        initial_input_json=row["initial_input_json"],
        next_run_at=row["next_run_at"],
        last_fired_at=row["last_fired_at"] or None,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        rule_json=row["rule_json"] or "{}",
        claim_until=claim,
    )


def _parse_iso_utc(value: str) -> datetime:
    s = (value or "").strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class ScheduleRepository:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def save_schedule(self, schedule: WorkflowSchedule) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO workflow_schedules (
                    schedule_id, workflow_id, enabled, initial_input_json,
                    next_run_at, last_fired_at, created_at, updated_at, rule_json, claim_until
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(schedule_id) DO UPDATE SET
                    workflow_id = excluded.workflow_id,
                    enabled = excluded.enabled,
                    initial_input_json = excluded.initial_input_json,
                    next_run_at = excluded.next_run_at,
                    last_fired_at = excluded.last_fired_at,
                    updated_at = excluded.updated_at,
                    rule_json = excluded.rule_json,
                    claim_until = excluded.claim_until
                """,
                (
                    schedule.schedule_id,
                    schedule.workflow_id,
                    1 if schedule.enabled else 0,
                    schedule.initial_input_json,
                    schedule.next_run_at,
                    schedule.last_fired_at,
                    schedule.created_at,
                    schedule.updated_at,
                    schedule.rule_json,
                    schedule.claim_until,
                ),
            )
            conn.commit()

    def get_schedule(self, schedule_id: str) -> Optional[WorkflowSchedule]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT * FROM workflow_schedules WHERE schedule_id = ?",
                (schedule_id,),
            )
            row = cur.fetchone()
            return _row_to_schedule(row) if row else None

    def delete_schedule(self, schedule_id: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM schedule_run_log WHERE schedule_id = ?", (schedule_id,))
            cur = conn.execute("DELETE FROM workflow_schedules WHERE schedule_id = ?", (schedule_id,))
            conn.commit()
            return cur.rowcount > 0

    def list_schedule_ids_due(self, now_utc: datetime, *, limit: int = 50) -> List[str]:
        """Schedules mit Fälligkeit und ohne aktive Sperre (nur IDs, sortiert)."""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT schedule_id, next_run_at, enabled, claim_until FROM workflow_schedules "
                "WHERE enabled = 1 ORDER BY next_run_at ASC"
            )
            due: List[Tuple[str, str]] = []
            for row in cur.fetchall():
                if not bool(row["enabled"]):
                    continue
                nxt = _parse_iso_utc(row["next_run_at"])
                if nxt > now_utc:
                    continue
                cu = row["claim_until"]
                if cu:
                    try:
                        if _parse_iso_utc(cu) > now_utc:
                            continue
                    except ValueError:
                        pass
                due.append((row["schedule_id"], row["next_run_at"]))
            due.sort(key=lambda t: t[1])
            return [s for s, _ in due[:limit]]

    def try_claim_schedule(
        self,
        schedule_id: str,
        now_utc: datetime,
        *,
        lock_seconds: int = 300,
    ) -> Optional[Tuple[WorkflowSchedule, str]]:
        """
        Setzt ``claim_until`` nur wenn Schedule fällig und nicht gesperrt.

        Returns:
            (Schedule, due_at_snapshot) oder None.
        """
        now_iso = now_utc.isoformat()
        lock_until = (now_utc + timedelta(seconds=lock_seconds)).isoformat()
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT * FROM workflow_schedules WHERE schedule_id = ?",
                (schedule_id,),
            )
            row = cur.fetchone()
            if row is None or not bool(row["enabled"]):
                conn.rollback()
                return None
            sch = _row_to_schedule(row)
            try:
                due_at = _parse_iso_utc(sch.next_run_at)
            except ValueError:
                conn.rollback()
                return None
            if due_at > now_utc:
                conn.rollback()
                return None
            if sch.claim_until:
                try:
                    if _parse_iso_utc(sch.claim_until) > now_utc:
                        conn.rollback()
                        return None
                except ValueError:
                    pass
            due_snapshot = sch.next_run_at
            cur2 = conn.execute(
                """
                UPDATE workflow_schedules
                SET claim_until = ?, updated_at = ?
                WHERE schedule_id = ?
                  AND enabled = 1
                  AND next_run_at = ?
                  AND (claim_until IS NULL OR claim_until = '' OR claim_until < ?)
                """,
                (lock_until, now_iso, schedule_id, due_snapshot, now_iso),
            )
            if cur2.rowcount != 1:
                conn.rollback()
                return None
            conn.commit()
            sch.claim_until = lock_until
            sch.updated_at = now_iso
            return sch, due_snapshot

    def clear_claim(self, schedule_id: str) -> None:
        now_iso = _utc_iso()
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "UPDATE workflow_schedules SET claim_until = NULL, updated_at = ? WHERE schedule_id = ?",
                (now_iso, schedule_id),
            )
            conn.commit()

    def update_schedule_after_due_run(
        self,
        schedule_id: str,
        *,
        next_run_at: Optional[str],
        enabled: bool,
        last_fired_at: str,
    ) -> None:
        now_iso = _utc_iso()
        with sqlite3.connect(self._db_path) as conn:
            if next_run_at is None:
                conn.execute(
                    """
                    UPDATE workflow_schedules
                    SET enabled = ?, last_fired_at = ?, claim_until = NULL, updated_at = ?
                    WHERE schedule_id = ?
                    """,
                    (1 if enabled else 0, last_fired_at, now_iso, schedule_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE workflow_schedules
                    SET enabled = ?, next_run_at = ?, last_fired_at = ?, claim_until = NULL, updated_at = ?
                    WHERE schedule_id = ?
                    """,
                    (1 if enabled else 0, next_run_at, last_fired_at, now_iso, schedule_id),
                )
            conn.commit()

    def insert_run_log(
        self,
        *,
        schedule_id: str,
        run_id: str,
        due_at: str,
        claimed_at: str,
        trigger_type: ScheduleTriggerType,
        finished_status: Optional[str] = None,
    ) -> int:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO schedule_run_log (
                    schedule_id, run_id, due_at, claimed_at, trigger_type, finished_status
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    schedule_id,
                    run_id,
                    due_at,
                    claimed_at,
                    trigger_type.value,
                    finished_status,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def persist_due_tick_outcome(
        self,
        *,
        schedule_id: str,
        run_id: str,
        due_at: str,
        claimed_at: str,
        finished_status: Optional[str],
        next_run_at: Optional[str],
        enabled: bool,
        last_fired_at: str,
    ) -> None:
        """
        Log-Zeile (due) und Schedule-Fortschreibung in **einer** Transaktion.

        Verhindert Zustände, in denen der Lauf existiert, der Schedule aber noch
        auf dem alten fälligen ``next_run_at`` steht.
        """
        now_iso = _utc_iso()
        en = 1 if enabled else 0
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute(
                    """
                    INSERT INTO schedule_run_log (
                        schedule_id, run_id, due_at, claimed_at, trigger_type, finished_status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        schedule_id,
                        run_id,
                        due_at,
                        claimed_at,
                        ScheduleTriggerType.DUE.value,
                        finished_status,
                    ),
                )
                if next_run_at is None:
                    conn.execute(
                        """
                        UPDATE workflow_schedules
                        SET enabled = ?, last_fired_at = ?, claim_until = NULL, updated_at = ?
                        WHERE schedule_id = ?
                        """,
                        (en, last_fired_at, now_iso, schedule_id),
                    )
                else:
                    conn.execute(
                        """
                        UPDATE workflow_schedules
                        SET enabled = ?, next_run_at = ?, last_fired_at = ?, claim_until = NULL, updated_at = ?
                        WHERE schedule_id = ?
                        """,
                        (en, next_run_at, last_fired_at, now_iso, schedule_id),
                    )
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def update_run_log_finished(self, run_id: str, finished_status: str) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "UPDATE schedule_run_log SET finished_status = ? WHERE run_id = ?",
                (finished_status, run_id),
            )
            conn.commit()

    def list_run_log_for_schedule(self, schedule_id: str, *, limit: int = 100) -> List[ScheduleRunLogEntry]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """
                SELECT id, schedule_id, run_id, due_at, claimed_at, trigger_type, finished_status
                FROM schedule_run_log
                WHERE schedule_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (schedule_id, limit),
            )
            out: List[ScheduleRunLogEntry] = []
            for row in cur.fetchall():
                out.append(
                    ScheduleRunLogEntry(
                        id=row["id"],
                        schedule_id=row["schedule_id"],
                        run_id=row["run_id"],
                        due_at=row["due_at"],
                        claimed_at=row["claimed_at"],
                        trigger_type=ScheduleTriggerType(row["trigger_type"]),
                        finished_status=row["finished_status"],
                    )
                )
            return out

    def list_schedules_with_workflow_name(
        self,
        *,
        project_scope_id: Optional[int] = None,
        include_global: bool = True,
    ) -> List[Tuple[WorkflowSchedule, str]]:
        """
        Alle Schedules mit Workflow-Name (leerer String wenn Join fehlt).
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            if project_scope_id is None:
                cur = conn.execute(
                    """
                    SELECT s.*, COALESCE(w.name, '') AS workflow_name
                    FROM workflow_schedules s
                    LEFT JOIN workflows w ON w.workflow_id = s.workflow_id
                    ORDER BY s.next_run_at ASC
                    """
                )
            elif include_global:
                cur = conn.execute(
                    """
                    SELECT s.*, COALESCE(w.name, '') AS workflow_name
                    FROM workflow_schedules s
                    LEFT JOIN workflows w ON w.workflow_id = s.workflow_id
                    WHERE w.workflow_id IS NULL OR w.project_id IS NULL OR w.project_id = ?
                    ORDER BY s.next_run_at ASC
                    """,
                    (project_scope_id,),
                )
            else:
                cur = conn.execute(
                    """
                    SELECT s.*, COALESCE(w.name, '') AS workflow_name
                    FROM workflow_schedules s
                    LEFT JOIN workflows w ON w.workflow_id = s.workflow_id
                    WHERE w.project_id = ?
                    ORDER BY s.next_run_at ASC
                    """,
                    (project_scope_id,),
                )
            rows: List[Tuple[WorkflowSchedule, str]] = []
            for row in cur.fetchall():
                name = row["workflow_name"] or ""
                sch = WorkflowSchedule(
                    schedule_id=row["schedule_id"],
                    workflow_id=row["workflow_id"],
                    enabled=bool(row["enabled"]),
                    initial_input_json=row["initial_input_json"],
                    next_run_at=row["next_run_at"],
                    last_fired_at=row["last_fired_at"] or None,
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    rule_json=row["rule_json"] or "{}",
                    claim_until=(row["claim_until"] or None) or None,
                )
                rows.append((sch, name))
            return rows

    def get_last_run_id_for_schedule(self, schedule_id: str) -> Optional[str]:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute(
                "SELECT run_id FROM schedule_run_log WHERE schedule_id = ? ORDER BY id DESC LIMIT 1",
                (schedule_id,),
            )
            row = cur.fetchone()
            return row[0] if row else None

    def update_last_fired_only(self, schedule_id: str, last_fired_at: str) -> None:
        now_iso = _utc_iso()
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "UPDATE workflow_schedules SET last_fired_at = ?, updated_at = ? WHERE schedule_id = ?",
                (last_fired_at, now_iso, schedule_id),
            )
            conn.commit()
