"""R3: ScheduleService mit echtem Repository und Mock/Real WorkflowService."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.core.db.database_manager import DatabaseManager
from app.services.schedule_service import ScheduleNotFoundError, ScheduleService
from app.services.workflow_service import WorkflowNotFoundError, WorkflowService
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.persistence.schedule_repository import ScheduleRepository
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.scheduling.models import ScheduleTriggerType, WorkflowSchedule


class _FlakyPersistRepo(ScheduleRepository):
    """Erster Aufruf von ``persist_due_tick_outcome`` schlägt künstlich fehl."""

    def __init__(self, db_path: str, fail_first_with: type[Exception]) -> None:
        super().__init__(db_path)
        self._fail_cls = fail_first_with
        self.persist_call_count = 0

    def persist_due_tick_outcome(self, **kwargs):
        self.persist_call_count += 1
        if self.persist_call_count == 1:
            raise self._fail_cls("simulated persist failure")
        return super().persist_due_tick_outcome(**kwargs)


class _CountingWorkflowProxy:
    def __init__(self, inner: WorkflowService) -> None:
        self._inner = inner
        self.start_run_calls = 0

    def load_workflow(self, workflow_id: str):
        return self._inner.load_workflow(workflow_id)

    def start_run(self, workflow_id: str, initial_input):
        self.start_run_calls += 1
        return self._inner.start_run(workflow_id, initial_input)


def _utc() -> datetime:
    return datetime(2030, 6, 15, 10, 0, tzinfo=timezone.utc)


def _defn(wid: str) -> WorkflowDefinition:
    return WorkflowDefinition(
        wid,
        "T",
        [
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        [WorkflowEdge("a1", "s", "e")],
    )


@pytest.fixture
def db_path(tmp_path) -> str:
    p = str(tmp_path / "ss.db")
    DatabaseManager(p, ensure_default_project=False)
    return p


@pytest.fixture
def wf_service(db_path) -> WorkflowService:
    return WorkflowService(WorkflowRepository(db_path))


@pytest.fixture
def sched_repo(db_path) -> ScheduleRepository:
    return ScheduleRepository(db_path)


def test_create_update_delete(sched_repo, wf_service):
    svc = ScheduleService(sched_repo, lambda: wf_service)
    wf_service.save_workflow(_defn("c1"))
    sch = svc.create_schedule(
        workflow_id="c1",
        initial_input_json="{}",
        next_run_at=_utc().isoformat(),
        rule_json="{}",
        enabled=True,
    )
    assert sch.schedule_id
    loaded = svc.get_schedule(sch.schedule_id)
    assert loaded.workflow_id == "c1"
    svc.update_schedule(sch.schedule_id, enabled=False)
    assert not svc.get_schedule(sch.schedule_id).enabled
    assert svc.delete_schedule(sch.schedule_id) is True
    with pytest.raises(ScheduleNotFoundError):
        svc.get_schedule(sch.schedule_id)


def test_create_rejects_missing_workflow(sched_repo, wf_service):
    svc = ScheduleService(sched_repo, lambda: wf_service)
    with pytest.raises(WorkflowNotFoundError):
        svc.create_schedule(
            workflow_id="missing",
            initial_input_json="{}",
            next_run_at=_utc().isoformat(),
            rule_json="{}",
        )


def test_tick_due_advances_next_run(sched_repo, wf_service):
    wf_service.save_workflow(_defn("tick_w"))
    svc = ScheduleService(sched_repo, lambda: wf_service)
    past = datetime(2020, 1, 1, tzinfo=timezone.utc)
    svc.create_schedule(
        workflow_id="tick_w",
        initial_input_json="{}",
        next_run_at=past.isoformat(),
        rule_json='{"repeat_interval_seconds": 120}',
        enabled=True,
    )
    rows = sched_repo.list_schedules_with_workflow_name()
    sid = rows[0][0].schedule_id
    n = svc.tick_due(datetime(2020, 1, 1, 0, 1, tzinfo=timezone.utc))
    assert n == 1
    after = svc.get_schedule(sid)
    assert after.enabled is True
    nxt = datetime.fromisoformat(after.next_run_at.replace("Z", "+00:00"))
    assert nxt > past
    logs = sched_repo.list_run_log_for_schedule(sid)
    assert len(logs) == 1
    assert logs[0].trigger_type == ScheduleTriggerType.DUE


def test_tick_due_one_shot_disables(sched_repo, wf_service):
    wf_service.save_workflow(_defn("once_w"))
    svc = ScheduleService(sched_repo, lambda: wf_service)
    past = datetime(2017, 1, 1, tzinfo=timezone.utc)
    sch = svc.create_schedule(
        workflow_id="once_w",
        initial_input_json="{}",
        next_run_at=past.isoformat(),
        rule_json="{}",
        enabled=True,
    )
    n = svc.tick_due(datetime(2018, 1, 1, tzinfo=timezone.utc))
    assert n == 1
    after = svc.get_schedule(sch.schedule_id)
    assert after.enabled is False


def test_tick_due_disabled_no_start(sched_repo, wf_service):
    wf_service.save_workflow(_defn("off_w"))
    svc = ScheduleService(sched_repo, lambda: wf_service)
    past = datetime(2019, 1, 1, tzinfo=timezone.utc)
    sch = svc.create_schedule(
        workflow_id="off_w",
        initial_input_json="{}",
        next_run_at=past.isoformat(),
        rule_json="{}",
        enabled=False,
    )
    n = svc.tick_due(datetime(2020, 1, 1, tzinfo=timezone.utc))
    assert n == 0
    assert svc.get_schedule(sch.schedule_id).enabled is False


def test_run_now_same_path_distinct_trigger(sched_repo, wf_service):
    wf_service.save_workflow(_defn("rn_w"))
    svc = ScheduleService(sched_repo, lambda: wf_service)
    future = datetime(2040, 1, 1, tzinfo=timezone.utc)
    sch = svc.create_schedule(
        workflow_id="rn_w",
        initial_input_json="{}",
        next_run_at=future.isoformat(),
        rule_json="{}",
        enabled=True,
    )
    rid = svc.run_now(sch.schedule_id)
    assert rid
    logs = sched_repo.list_run_log_for_schedule(sch.schedule_id)
    assert logs[0].trigger_type == ScheduleTriggerType.MANUAL
    after = svc.get_schedule(sch.schedule_id)
    assert after.next_run_at == future.isoformat()


def test_tick_due_no_refire_when_persist_fails_after_start_run(db_path, wf_service):
    repo = _FlakyPersistRepo(db_path, RuntimeError)
    wf_proxy = _CountingWorkflowProxy(wf_service)
    svc = ScheduleService(repo, lambda: wf_proxy)
    wf_service.save_workflow(_defn("nf_w"))
    past = datetime(2016, 1, 1, tzinfo=timezone.utc)
    sch = svc.create_schedule(
        workflow_id="nf_w",
        initial_input_json="{}",
        next_run_at=past.isoformat(),
        rule_json="{}",
        enabled=True,
    )
    t = datetime(2017, 1, 1, tzinfo=timezone.utc)
    assert svc.tick_due(t) == 1
    assert wf_proxy.start_run_calls == 1
    assert svc.get_schedule(sch.schedule_id).enabled is False
    assert svc.tick_due(t) == 0
    assert wf_proxy.start_run_calls == 1


def test_tick_due_integrity_error_on_persist_repairs_without_refire(db_path, wf_service):
    repo = _FlakyPersistRepo(db_path, sqlite3.IntegrityError)
    wf_proxy = _CountingWorkflowProxy(wf_service)
    svc = ScheduleService(repo, lambda: wf_proxy)
    wf_service.save_workflow(_defn("int_w"))
    past = datetime(2015, 6, 1, tzinfo=timezone.utc)
    sch = svc.create_schedule(
        workflow_id="int_w",
        initial_input_json="{}",
        next_run_at=past.isoformat(),
        rule_json="{}",
        enabled=True,
    )
    t = datetime(2016, 1, 1, tzinfo=timezone.utc)
    assert svc.tick_due(t) == 1
    assert wf_proxy.start_run_calls == 1
    assert svc.get_schedule(sch.schedule_id).enabled is False
    assert svc.tick_due(t) == 0
    assert wf_proxy.start_run_calls == 1


def test_tick_due_mock_workflow_failure_disables(sched_repo):
    mock_wf = MagicMock()

    def boom(_wid, _inp):
        raise RuntimeError("no run")

    mock_wf.start_run = boom
    mock_wf.load_workflow = MagicMock()
    svc = ScheduleService(sched_repo, lambda: mock_wf)
    past = datetime(2018, 1, 1, tzinfo=timezone.utc)
    sched_repo.save_schedule(
        WorkflowSchedule(
            schedule_id="sx",
            workflow_id="any",
            enabled=True,
            initial_input_json="{}",
            next_run_at=past.isoformat(),
            last_fired_at=None,
            created_at=past.isoformat(),
            updated_at=past.isoformat(),
            rule_json="{}",
        )
    )
    n = svc.tick_due(datetime(2019, 1, 1, tzinfo=timezone.utc))
    assert n == 0
    st = sched_repo.get_schedule("sx")
    assert st is not None and st.enabled is False
