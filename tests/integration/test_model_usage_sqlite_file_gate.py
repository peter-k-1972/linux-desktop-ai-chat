"""
Echte SQLite-Datei (kein :memory:): Ledger + Aggregation über Engine-Reopen.

Ergänzt das model_usage_gate um Persistenzsemantik ohne globalen Engine-State.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.domain.model_usage.periods import period_starts
from app.persistence.base import Base
from app.persistence.enums import PeriodType, UsageStatus, UsageType
from app.persistence.orm.models import ModelUsageAggregate, ModelUsageRecord
from app.services.model_usage_aggregation_service import ModelUsageAggregationService
from app.services.model_usage_service import ModelUsageService, UsageRecordInput


@pytest.mark.integration
@pytest.mark.model_usage_gate
def test_usage_ledger_and_aggregate_survive_engine_reopen(tmp_path):
    db_path = tmp_path / "model_usage_gate.db"
    url = f"sqlite:///{db_path.as_posix()}"
    connect_args = {"check_same_thread": False}

    def open_engine():
        return create_engine(url, future=True, connect_args=connect_args)

    eng1 = open_engine()
    Base.metadata.create_all(eng1)
    SF = sessionmaker(bind=eng1, autoflush=False, expire_on_commit=False, future=True)

    with SF() as s:
        usage = ModelUsageService()
        agg = ModelUsageAggregationService()
        rec = usage.create_record(
            s,
            UsageRecordInput(
                model_id="persist-m",
                usage_type=UsageType.CHAT.value,
                is_online=False,
                prompt_tokens=3,
                completion_tokens=5,
                total_tokens=8,
                estimated_tokens=False,
                status=UsageStatus.SUCCESS.value,
                provider_id="local",
                scope_type="global",
                scope_ref="",
            ),
        )
        s.commit()
        s.refresh(rec)
        created_at = rec.created_at
        agg.apply_record(s, rec)
        s.commit()

    eng1.dispose()

    eng2 = open_engine()
    SF2 = sessionmaker(bind=eng2, autoflush=False, expire_on_commit=False, future=True)
    with SF2() as s:
        loaded = s.scalars(select(ModelUsageRecord).where(ModelUsageRecord.model_id == "persist-m")).first()
        assert loaded is not None
        assert loaded.total_tokens == 8
        assert loaded.prompt_tokens == 3
        assert loaded.completion_tokens == 5

        starts = period_starts(created_at)
        bucket = s.scalars(
            select(ModelUsageAggregate).where(
                ModelUsageAggregate.model_id == "persist-m",
                ModelUsageAggregate.provider_id_key == "local",
                ModelUsageAggregate.period_type == PeriodType.TOTAL.value,
                ModelUsageAggregate.period_start == starts["total"],
            )
        ).first()
        assert bucket is not None
        assert bucket.total_tokens == 8
        assert bucket.success_count == 1

    eng2.dispose()
