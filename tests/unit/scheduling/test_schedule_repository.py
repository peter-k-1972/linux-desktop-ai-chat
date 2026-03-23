"""R3: ScheduleRepository, Migration, Claim, Log-Integrität."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timedelta, timezone

import pytest

from app.core.db.database_manager import DatabaseManager
from app.workflows.persistence.schedule_repository import ScheduleRepository
from app.workflows.scheduling.models import ScheduleTriggerType, WorkflowSchedule


def _utc(h=0, m=0) -> datetime:
    return datetime(2030, 1, 1, h, m, tzinfo=timezone.utc)


@pytest.fixture
def db_path(tmp_path) -> str:
    p = str(tmp_path / "sched.db")
    DatabaseManager(p, ensure_default_project=False)
    return p


def test_migration_creates_tables(db_path):
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN "
            "('workflow_schedules','schedule_run_log')"
        )
        names = {r[0] for r in cur.fetchall()}
    assert names == {"workflow_schedules", "schedule_run_log"}


def test_try_claim_second_winner_fails_when_locked(db_path):
    repo = ScheduleRepository(db_path)
    now = _utc()
    sch = WorkflowSchedule(
        schedule_id="s1",
        workflow_id="w1",
        enabled=True,
        initial_input_json="{}",
        next_run_at=now.isoformat(),
        last_fired_at=None,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        rule_json="{}",
    )
    repo.save_schedule(sch)
    a = repo.try_claim_schedule("s1", now)
    assert a is not None
    b = repo.try_claim_schedule("s1", now)
    assert b is None
    repo.clear_claim("s1")
    c = repo.try_claim_schedule("s1", now)
    assert c is not None


def test_schedule_run_log_unique_due_slot(db_path):
    repo = ScheduleRepository(db_path)
    now = _utc()
    repo.save_schedule(
        WorkflowSchedule(
            schedule_id="s2",
            workflow_id="w1",
            enabled=True,
            initial_input_json="{}",
            next_run_at=now.isoformat(),
            last_fired_at=None,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            rule_json="{}",
        )
    )
    due = now.isoformat()
    claimed = now.isoformat()
    repo.insert_run_log(
        schedule_id="s2",
        run_id="run_a",
        due_at=due,
        claimed_at=claimed,
        trigger_type=ScheduleTriggerType.DUE,
        finished_status="completed",
    )
    with pytest.raises(sqlite3.IntegrityError):
        repo.insert_run_log(
            schedule_id="s2",
            run_id="run_b",
            due_at=due,
            claimed_at=claimed,
            trigger_type=ScheduleTriggerType.DUE,
            finished_status="completed",
        )


def test_concurrent_claim_single_winner(db_path):
    repo = ScheduleRepository(db_path)
    now = _utc(12, 0)
    repo.save_schedule(
        WorkflowSchedule(
            schedule_id="s3",
            workflow_id="w1",
            enabled=True,
            initial_input_json="{}",
            next_run_at=now.isoformat(),
            last_fired_at=None,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            rule_json="{}",
        )
    )
    barrier = threading.Barrier(2)
    winners: list[bool] = []

    def worker():
        barrier.wait()
        r = ScheduleRepository(db_path).try_claim_schedule("s3", now)
        winners.append(r is not None)

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert sum(1 for w in winners if w) == 1


def test_manual_log_same_due_allowed_twice_different_run(db_path):
    repo = ScheduleRepository(db_path)
    now = _utc()
    repo.save_schedule(
        WorkflowSchedule(
            schedule_id="s4",
            workflow_id="w1",
            enabled=True,
            initial_input_json="{}",
            next_run_at=(now + timedelta(days=1)).isoformat(),
            last_fired_at=None,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            rule_json="{}",
        )
    )
    t1 = now.isoformat()
    repo.insert_run_log(
        schedule_id="s4",
        run_id="m1",
        due_at=t1,
        claimed_at=t1,
        trigger_type=ScheduleTriggerType.MANUAL,
        finished_status="completed",
    )
    repo.insert_run_log(
        schedule_id="s4",
        run_id="m2",
        due_at=t1,
        claimed_at=t1,
        trigger_type=ScheduleTriggerType.MANUAL,
        finished_status="completed",
    )
