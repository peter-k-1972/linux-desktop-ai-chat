"""
Phase A: ORM-Modelle, Services (Usage, Aggregation, Quota, Local Registry).

Nutzt In-Memory-SQLite und ``Base.metadata.create_all`` (parallel zu Alembic-Revision phase_a_001).
"""

from __future__ import annotations

import tempfile
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.domain.model_usage.periods import period_starts
from app.persistence.base import Base
from app.persistence.enums import (
    ModelAssetType,
    QuotaMode,
    QuotaScopeType,
    UsageStatus,
    UsageType,
)
from app.persistence.orm.models import (
    ModelAsset,
    ModelQuotaPolicy,
    ModelStorageRoot,
    ModelUsageAggregate,
    ModelUsageRecord,
)
from app.services.local_model_registry_service import (
    LocalModelRegistryError,
    LocalModelRegistryService,
)
from app.services.model_quota_service import (
    ModelQuotaService,
    PreflightDecision,
    QuotaEvaluationContext,
)
from app.services.model_usage_aggregation_service import ModelUsageAggregationService
from app.services.model_usage_service import ModelUsageService, UsageRecordInput, UsageValidationError


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine) -> Session:
    S = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)
    s = S()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


# --- ORM / defaults ---


@pytest.mark.model_usage_gate
def test_usage_record_defaults_db_timestamps(session: Session):
    row = ModelUsageRecord(
        model_id="m1",
        usage_type=UsageType.CHAT.value,
        is_online=False,
        status=UsageStatus.SUCCESS.value,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    assert row.id is not None
    assert row.created_at is not None
    assert row.prompt_tokens == 0
    assert row.estimated_tokens is False


@pytest.mark.model_usage_gate
def test_aggregate_unique_constraint(session: Session):
    starts = period_starts(datetime(2025, 6, 10, 14, 30, tzinfo=timezone.utc))
    a = ModelUsageAggregate(
        model_id="x",
        provider_id_key="",
        provider_credential_id_key=-1,
        scope_type="global",
        scope_ref_key="",
        period_type="day",
        period_start=starts["day"],
        prompt_tokens=1,
        completion_tokens=0,
        total_tokens=1,
        request_count=1,
        success_count=1,
        blocked_count=0,
        failed_count=0,
        cancelled_count=0,
        estimated_count=0,
    )
    b = ModelUsageAggregate(
        model_id="x",
        provider_id_key="",
        provider_credential_id_key=-1,
        scope_type="global",
        scope_ref_key="",
        period_type="day",
        period_start=starts["day"],
        prompt_tokens=2,
        completion_tokens=0,
        total_tokens=2,
        request_count=1,
        success_count=1,
        blocked_count=0,
        failed_count=0,
        cancelled_count=0,
        estimated_count=0,
    )
    session.add(a)
    session.commit()
    session.add(b)
    with pytest.raises(Exception):
        session.commit()
    session.rollback()


# --- Usage service ---


@pytest.mark.model_usage_gate
def test_usage_service_totals_and_estimated_flag(session: Session):
    svc = ModelUsageService()
    r = svc.create_record(
        session,
        UsageRecordInput(
            model_id="m",
            usage_type=UsageType.CHAT.value,
            is_online=True,
            prompt_tokens=3,
            completion_tokens=5,
            estimated_tokens=True,
            status=UsageStatus.SUCCESS.value,
        ),
    )
    session.commit()
    session.refresh(r)
    assert r.total_tokens == 8
    assert r.estimated_tokens is True


@pytest.mark.model_usage_gate
def test_usage_service_blocked_status(session: Session):
    svc = ModelUsageService()
    r = svc.create_record(
        session,
        UsageRecordInput(
            model_id="m",
            usage_type=UsageType.CHAT.value,
            is_online=False,
            status=UsageStatus.BLOCKED.value,
            block_reason="quota",
        ),
    )
    session.commit()
    assert r.status == UsageStatus.BLOCKED.value


@pytest.mark.model_usage_gate
def test_usage_service_validation_rejects_negative_tokens(session: Session):
    svc = ModelUsageService()
    with pytest.raises(UsageValidationError):
        svc.create_record(
            session,
            UsageRecordInput(
                model_id="m",
                usage_type=UsageType.CHAT.value,
                is_online=False,
                prompt_tokens=-1,
                status=UsageStatus.SUCCESS.value,
            ),
        )


# --- Aggregation ---


@pytest.mark.model_usage_gate
def test_aggregation_sums_and_status_counts(session: Session):
    usage = ModelUsageService()
    agg = ModelUsageAggregationService()
    t0 = datetime(2025, 3, 10, 12, 0, tzinfo=timezone.utc)
    r1 = ModelUsageRecord(
        model_id="m",
        usage_type=UsageType.CHAT.value,
        is_online=False,
        prompt_tokens=10,
        completion_tokens=2,
        total_tokens=12,
        estimated_tokens=False,
        request_count=1,
        status=UsageStatus.SUCCESS.value,
        created_at=t0,
        scope_type="global",
        scope_ref=None,
    )
    r2 = ModelUsageRecord(
        model_id="m",
        usage_type=UsageType.CHAT.value,
        is_online=False,
        prompt_tokens=5,
        completion_tokens=1,
        total_tokens=6,
        estimated_tokens=True,
        request_count=1,
        status=UsageStatus.BLOCKED.value,
        created_at=t0,
        scope_type="global",
        scope_ref=None,
    )
    session.add_all([r1, r2])
    session.commit()
    agg.apply_record(session, r1)
    agg.apply_record(session, r2)
    session.commit()

    starts = period_starts(t0)
    row = session.scalars(
        select(ModelUsageAggregate).where(
            ModelUsageAggregate.period_type == "day",
            ModelUsageAggregate.period_start == starts["day"],
            ModelUsageAggregate.model_id == "m",
        )
    ).first()
    assert row is not None
    assert row.prompt_tokens == 15
    assert row.total_tokens == 18
    assert row.success_count == 1
    assert row.blocked_count == 1
    assert row.estimated_count == 1


@pytest.mark.model_usage_gate
def test_aggregation_rebuild(session: Session):
    usage = ModelUsageService()
    agg = ModelUsageAggregationService()
    r = usage.create_record(
        session,
        UsageRecordInput(
            model_id="m",
            usage_type=UsageType.CHAT.value,
            is_online=False,
            prompt_tokens=1,
            completion_tokens=1,
            total_tokens=2,
            status=UsageStatus.FAILED.value,
        ),
    )
    session.commit()
    agg.apply_record(session, r)
    session.commit()
    n = agg.rebuild_from_ledger(session)
    session.commit()
    assert n == 1
    cnt = session.scalars(select(ModelUsageAggregate)).all()
    assert len(cnt) == 5


# --- Quota ---


@pytest.mark.model_usage_gate
def test_effective_quota_strictest_limit(session: Session):
    p1 = ModelQuotaPolicy(
        scope_type=QuotaScopeType.GLOBAL.value,
        mode=QuotaMode.WARN.value,
        source="manual",
        warn_percent=0.9,
        limit_day_tokens=1000,
        is_enabled=True,
        priority=1,
    )
    p2 = ModelQuotaPolicy(
        scope_type=QuotaScopeType.GLOBAL.value,
        mode=QuotaMode.HARD_BLOCK.value,
        source="manual",
        warn_percent=0.5,
        limit_day_tokens=500,
        is_enabled=True,
        priority=2,
    )
    session.add_all([p1, p2])
    session.commit()
    qsvc = ModelQuotaService()
    ctx = QuotaEvaluationContext(is_online=True, model_id="any")
    eff = qsvc.get_effective_quota(session, ctx)
    assert eff.limit_day_tokens == 500
    assert eff.mode == QuotaMode.HARD_BLOCK


@pytest.mark.model_usage_gate
def test_offline_default_policy_not_applied_when_online(session: Session):
    pol = ModelQuotaPolicy(
        scope_type=QuotaScopeType.OFFLINE_DEFAULT.value,
        mode=QuotaMode.NONE.value,
        source="default_offline",
        warn_percent=0.85,
        is_enabled=True,
        priority=0,
    )
    session.add(pol)
    session.commit()
    qsvc = ModelQuotaService()
    eff = qsvc.get_effective_quota(
        session, QuotaEvaluationContext(is_online=True, model_id="m")
    )
    assert eff.limit_day_tokens is None
    assert eff.mode == QuotaMode.NONE


@pytest.mark.model_usage_gate
def test_evaluate_quota_hard_block(session: Session):
    qsvc = ModelQuotaService()
    from app.services.model_quota_service import EffectiveQuota, UsageSnapshot

    eff = EffectiveQuota(
        limit_hour_tokens=100,
        mode=QuotaMode.HARD_BLOCK,
        warn_percent=0.8,
    )
    snap = UsageSnapshot(hour_tokens=90)
    res = qsvc.evaluate_usage_against_quota(
        effective=eff, snapshot=snap, projected_additional_tokens=20
    )
    assert res.decision == PreflightDecision.BLOCK


# --- Local registry ---


@pytest.mark.model_usage_gate
def test_storage_root_and_asset(tmp_path, session: Session):
    reg = LocalModelRegistryService()
    root = reg.register_storage_root(session, name="home_ai", path_absolute=str(tmp_path))
    session.commit()
    a = reg.upsert_asset(
        session,
        path_absolute=str(tmp_path / "w.gguf"),
        asset_type=ModelAssetType.GGUF.value,
        storage_root_id=root.id,
        is_available=True,
    )
    session.commit()
    reg.link_asset_to_model(session, a.id, "llama3:latest")
    session.commit()
    session.refresh(a)
    assert a.model_id == "llama3:latest"
    reg.set_asset_availability(session, a.id, False)
    session.commit()
    session.refresh(a)
    assert a.is_available is False


@pytest.mark.model_usage_gate
def test_storage_root_duplicate_name_raises(session: Session, tmp_path):
    reg = LocalModelRegistryService()
    reg.register_storage_root(session, name="r1", path_absolute=str(tmp_path / "a"))
    session.commit()
    with pytest.raises(LocalModelRegistryError):
        reg.register_storage_root(session, name="r1", path_absolute=str(tmp_path / "b"))
        session.flush()
    session.rollback()


def test_alembic_revision_file_exists():
    from pathlib import Path

    p = Path(__file__).resolve().parents[2] / "alembic" / "versions" / "phase_a_001_model_usage_foundation.py"
    assert p.is_file()
