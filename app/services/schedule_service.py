"""
R3: Geplante Workflow-Ausführung.

Ausführung ausschließlich über WorkflowService.start_run (kein zweiter Orchestrator).
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Callable, List, Optional, TYPE_CHECKING

from app.workflows.persistence.schedule_repository import ScheduleRepository
from app.workflows.scheduling.models import ScheduleListRow, ScheduleTriggerType, WorkflowSchedule
from app.workflows.scheduling.next_run import (
    format_utc_iso,
    next_run_after_due_execution,
    parse_rule_json,
    parse_utc_iso,
    utc_now,
    validate_rule_dict,
)

if TYPE_CHECKING:
    from app.services.workflow_service import WorkflowService

_log = logging.getLogger(__name__)


class ScheduleNotFoundError(Exception):
    """Unbekannte schedule_id."""


class ScheduleService:
    def __init__(
        self,
        repository: ScheduleRepository,
        workflow_service_getter: Callable[[], "WorkflowService"],
    ) -> None:
        self._repo = repository
        self._workflow_service_getter = workflow_service_getter

    def _wf(self) -> "WorkflowService":
        return self._workflow_service_getter()

    @staticmethod
    def _new_schedule_id() -> str:
        return f"ws_{uuid.uuid4().hex[:12]}"

    def _validate_initial_input_json(self, raw: str) -> str:
        text = (raw or "").strip() or "{}"
        try:
            val = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"initial_input_json ist kein gültiges JSON: {e}") from e
        if not isinstance(val, dict):
            raise ValueError("initial_input_json muss ein JSON-Objekt sein.")
        return json.dumps(val, ensure_ascii=False, sort_keys=True)

    def _validate_workflow_exists(self, workflow_id: str) -> None:
        wid = (workflow_id or "").strip()
        if not wid:
            raise ValueError("workflow_id darf nicht leer sein.")
        self._wf().load_workflow(wid)

    def _validate_next_run_at(self, next_run_at: str) -> str:
        s = (next_run_at or "").strip()
        if not s:
            raise ValueError("next_run_at ist erforderlich.")
        parse_utc_iso(s)
        return s

    def create_schedule(
        self,
        *,
        workflow_id: str,
        initial_input_json: str,
        next_run_at: str,
        rule_json: str,
        enabled: bool = True,
    ) -> WorkflowSchedule:
        self._validate_workflow_exists(workflow_id)
        inp = self._validate_initial_input_json(initial_input_json)
        nxt = self._validate_next_run_at(next_run_at)
        rule = parse_rule_json(rule_json)
        validate_rule_dict(rule)
        now = format_utc_iso(utc_now())
        sid = self._new_schedule_id()
        sch = WorkflowSchedule(
            schedule_id=sid,
            workflow_id=(workflow_id or "").strip(),
            enabled=enabled,
            initial_input_json=inp,
            next_run_at=nxt,
            last_fired_at=None,
            created_at=now,
            updated_at=now,
            rule_json=json.dumps(rule, ensure_ascii=False, sort_keys=True),
            claim_until=None,
        )
        self._repo.save_schedule(sch)
        return sch

    def update_schedule(
        self,
        schedule_id: str,
        *,
        workflow_id: Optional[str] = None,
        initial_input_json: Optional[str] = None,
        next_run_at: Optional[str] = None,
        rule_json: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> WorkflowSchedule:
        cur = self._repo.get_schedule(schedule_id)
        if cur is None:
            raise ScheduleNotFoundError(schedule_id)
        wf_id = cur.workflow_id if workflow_id is None else workflow_id
        self._validate_workflow_exists(wf_id)
        inp = (
            self._validate_initial_input_json(initial_input_json)
            if initial_input_json is not None
            else cur.initial_input_json
        )
        nxt = self._validate_next_run_at(next_run_at) if next_run_at is not None else cur.next_run_at
        if rule_json is not None:
            rule = parse_rule_json(rule_json)
            validate_rule_dict(rule)
            rj = json.dumps(rule, ensure_ascii=False, sort_keys=True)
        else:
            rj = cur.rule_json
        en = cur.enabled if enabled is None else enabled
        now = format_utc_iso(utc_now())
        updated = WorkflowSchedule(
            schedule_id=cur.schedule_id,
            workflow_id=(wf_id or "").strip(),
            enabled=en,
            initial_input_json=inp,
            next_run_at=nxt,
            last_fired_at=cur.last_fired_at,
            created_at=cur.created_at,
            updated_at=now,
            rule_json=rj,
            claim_until=cur.claim_until,
        )
        self._repo.save_schedule(updated)
        return updated

    def delete_schedule(self, schedule_id: str) -> bool:
        return self._repo.delete_schedule(schedule_id)

    def get_schedule(self, schedule_id: str) -> WorkflowSchedule:
        s = self._repo.get_schedule(schedule_id)
        if s is None:
            raise ScheduleNotFoundError(schedule_id)
        return s

    def get_last_run_id(self, schedule_id: str) -> Optional[str]:
        return self._repo.get_last_run_id_for_schedule(schedule_id)

    def list_schedules(
        self,
        *,
        project_scope_id: Optional[int] = None,
        include_global: bool = True,
    ) -> List[ScheduleListRow]:
        rows = self._repo.list_schedules_with_workflow_name(
            project_scope_id=project_scope_id,
            include_global=include_global,
        )
        return [ScheduleListRow(schedule=s, workflow_name=n) for s, n in rows]

    def tick_due(self, now_utc: Optional[datetime] = None) -> int:
        """
        Verarbeitet fällige Schedules (Claim → start_run → Log → Next-Run).

        Returns:
            Anzahl erfolgreich gestarteter Laufs (mit persistiertem Run).
        """
        now = now_utc or utc_now()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)

        ids = self._repo.list_schedule_ids_due(now, limit=50)
        started = 0
        for sid in ids:
            claimed = self._repo.try_claim_schedule(sid, now)
            if claimed is None:
                continue
            sch, due_snapshot = claimed
            try:
                rule = parse_rule_json(sch.rule_json)
                repeat = validate_rule_dict(rule)
            except ValueError as e:
                _log.warning("Schedule %s: ungültige rule_json, deaktiviere: %s", sid, e)
                self._repo.clear_claim(sid)
                self._repo.update_schedule_after_due_run(
                    sid,
                    next_run_at=None,
                    enabled=False,
                    last_fired_at=format_utc_iso(now),
                )
                continue

            initial_input = json.loads(sch.initial_input_json)
            wf = self._wf()
            try:
                run = wf.start_run(sch.workflow_id, initial_input)
            except Exception as e:
                _log.warning(
                    "Schedule %s: start_run fehlgeschlagen (kein Run): %s",
                    sid,
                    e,
                    exc_info=True,
                )
                self._repo.clear_claim(sid)
                self._repo.update_schedule_after_due_run(
                    sid,
                    next_run_at=None,
                    enabled=False,
                    last_fired_at=format_utc_iso(now),
                )
                continue

            claimed_at = format_utc_iso(now)
            due_dt = parse_utc_iso(due_snapshot)
            next_iso, disable = next_run_after_due_execution(
                due_at_utc=due_dt,
                now_utc=now,
                repeat_interval_seconds=repeat,
            )
            enabled_after = False if disable else True
            try:
                self._repo.persist_due_tick_outcome(
                    schedule_id=sid,
                    run_id=run.run_id,
                    due_at=due_snapshot,
                    claimed_at=claimed_at,
                    finished_status=run.status.value,
                    next_run_at=next_iso,
                    enabled=enabled_after,
                    last_fired_at=claimed_at,
                )
            except Exception as e:
                _log.warning(
                    "Schedule %s: Nachlauf nach start_run fehlgeschlagen (%s); repariere Schedule.",
                    sid,
                    e,
                    exc_info=True,
                )
                try:
                    self._repo.update_schedule_after_due_run(
                        sid,
                        next_run_at=next_iso,
                        enabled=enabled_after,
                        last_fired_at=claimed_at,
                    )
                except Exception as repair_e:
                    _log.warning(
                        "Schedule %s: erste Reparatur fehlgeschlagen (%s); deaktiviere.",
                        sid,
                        repair_e,
                        exc_info=True,
                    )
                    self._repo.update_schedule_after_due_run(
                        sid,
                        next_run_at=None,
                        enabled=False,
                        last_fired_at=claimed_at,
                    )
            started += 1

        return started

    def run_now(self, schedule_id: str) -> str:
        """
        Manueller Start: gleicher ``start_run``-Pfad, eigene Log-Kennzeichnung.

        Returns:
            run_id
        """
        sch = self._repo.get_schedule(schedule_id)
        if sch is None:
            raise ScheduleNotFoundError(schedule_id)
        if not sch.enabled:
            raise ValueError("Schedule ist deaktiviert.")

        initial_input = json.loads(sch.initial_input_json)
        now = utc_now()
        claimed_at = format_utc_iso(now)
        run = self._wf().start_run(sch.workflow_id, initial_input)

        self._repo.insert_run_log(
            schedule_id=schedule_id,
            run_id=run.run_id,
            due_at=claimed_at,
            claimed_at=claimed_at,
            trigger_type=ScheduleTriggerType.MANUAL,
            finished_status=run.status.value,
        )
        self._repo.update_last_fired_only(schedule_id, claimed_at)
        return run.run_id


_schedule_service: Optional[ScheduleService] = None


def get_schedule_service() -> ScheduleService:
    global _schedule_service
    if _schedule_service is None:
        from app.services.infrastructure import get_infrastructure
        from app.services.workflow_service import get_workflow_service

        db = get_infrastructure().database
        _schedule_service = ScheduleService(
            ScheduleRepository(db.db_path),
            workflow_service_getter=get_workflow_service,
        )
    return _schedule_service


def reset_schedule_service() -> None:
    global _schedule_service
    _schedule_service = None
