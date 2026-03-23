"""
Aggregationsservice – leitet ``ModelUsageAggregate`` aus dem Ledger ab.

Rebuild: Ledger bleibt Source of Truth; Aggregates werden verworfen und neu berechnet.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.domain.model_usage.periods import period_starts
from app.persistence.enums import PeriodType, UsageStatus
from app.persistence.orm.models import ModelUsageAggregate, ModelUsageRecord


def _norm_provider_id(v: str | None) -> str:
    return (v or "").strip()


def _norm_cred_id(v: int | None) -> int:
    return -1 if v is None else int(v)


def _norm_scope(scope_type: str | None, scope_ref: str | None) -> Tuple[str, str]:
    st = (scope_type or "").strip() or "global"
    sr = (scope_ref or "").strip()
    return st, sr


class ModelUsageAggregationService:
    def aggregate_key_from_record(self, record: ModelUsageRecord) -> Dict[str, Any]:
        st, sr = _norm_scope(record.scope_type, record.scope_ref)
        return {
            "model_id": record.model_id,
            "provider_id_key": _norm_provider_id(record.provider_id),
            "provider_credential_id_key": _norm_cred_id(record.provider_credential_id),
            "scope_type": st,
            "scope_ref_key": sr,
        }

    def _status_deltas(self, record: ModelUsageRecord) -> Dict[str, int]:
        rc = max(1, int(record.request_count))
        st = record.status
        d = {
            "request_count": rc,
            "success_count": 0,
            "blocked_count": 0,
            "failed_count": 0,
            "cancelled_count": 0,
            "estimated_count": rc if record.estimated_tokens else 0,
        }
        if st == UsageStatus.SUCCESS.value:
            d["success_count"] = rc
        elif st == UsageStatus.BLOCKED.value:
            d["blocked_count"] = rc
        elif st == UsageStatus.FAILED.value:
            d["failed_count"] = rc
        elif st == UsageStatus.CANCELLED.value:
            d["cancelled_count"] = rc
        else:
            d["failed_count"] = rc
        return d

    def _upsert_one_bucket(
        self,
        session: Session,
        *,
        model_id: str,
        provider_id_key: str,
        provider_credential_id_key: int,
        scope_type: str,
        scope_ref_key: str,
        period_type: str,
        period_start: datetime,
        prompt_delta: int,
        completion_delta: int,
        total_delta: int,
        deltas: Dict[str, int],
        cost_delta: float | None,
    ) -> None:
        pt = period_type
        ps = period_start
        values = {
            "model_id": model_id,
            "provider_id_key": provider_id_key,
            "provider_credential_id_key": provider_credential_id_key,
            "scope_type": scope_type,
            "scope_ref_key": scope_ref_key,
            "period_type": pt,
            "period_start": ps,
            "prompt_tokens": prompt_delta,
            "completion_tokens": completion_delta,
            "total_tokens": total_delta,
            "request_count": deltas["request_count"],
            "success_count": deltas["success_count"],
            "blocked_count": deltas["blocked_count"],
            "failed_count": deltas["failed_count"],
            "cancelled_count": deltas["cancelled_count"],
            "estimated_count": deltas["estimated_count"],
            "cost_total": cost_delta,
        }
        stmt = sqlite_insert(ModelUsageAggregate).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                ModelUsageAggregate.model_id,
                ModelUsageAggregate.provider_id_key,
                ModelUsageAggregate.provider_credential_id_key,
                ModelUsageAggregate.scope_type,
                ModelUsageAggregate.scope_ref_key,
                ModelUsageAggregate.period_type,
                ModelUsageAggregate.period_start,
            ],
            set_={
                "prompt_tokens": ModelUsageAggregate.prompt_tokens + stmt.excluded.prompt_tokens,
                "completion_tokens": ModelUsageAggregate.completion_tokens
                + stmt.excluded.completion_tokens,
                "total_tokens": ModelUsageAggregate.total_tokens + stmt.excluded.total_tokens,
                "request_count": ModelUsageAggregate.request_count + stmt.excluded.request_count,
                "success_count": ModelUsageAggregate.success_count + stmt.excluded.success_count,
                "blocked_count": ModelUsageAggregate.blocked_count + stmt.excluded.blocked_count,
                "failed_count": ModelUsageAggregate.failed_count + stmt.excluded.failed_count,
                "cancelled_count": ModelUsageAggregate.cancelled_count + stmt.excluded.cancelled_count,
                "estimated_count": ModelUsageAggregate.estimated_count + stmt.excluded.estimated_count,
                "cost_total": func.coalesce(ModelUsageAggregate.cost_total, 0)
                + func.coalesce(stmt.excluded.cost_total, 0),
                "updated_at": func.now(),
            },
        )
        session.execute(stmt)

    def apply_record(self, session: Session, record: ModelUsageRecord) -> None:
        base = self.aggregate_key_from_record(record)
        starts = period_starts(record.created_at)
        deltas = self._status_deltas(record)
        ptokens = record.prompt_tokens
        ctokens = record.completion_tokens
        ttokens = record.total_tokens
        cost = float(record.cost_total) if record.cost_total is not None else None

        mapping = [
            (PeriodType.HOUR.value, starts["hour"]),
            (PeriodType.DAY.value, starts["day"]),
            (PeriodType.WEEK.value, starts["week"]),
            (PeriodType.MONTH.value, starts["month"]),
            (PeriodType.TOTAL.value, starts["total"]),
        ]

        for ptype, pstart in mapping:
            self._upsert_one_bucket(
                session,
                model_id=base["model_id"],
                provider_id_key=base["provider_id_key"],
                provider_credential_id_key=base["provider_credential_id_key"],
                scope_type=base["scope_type"],
                scope_ref_key=base["scope_ref_key"],
                period_type=ptype,
                period_start=pstart,
                prompt_delta=ptokens,
                completion_delta=ctokens,
                total_delta=ttokens,
                deltas=deltas,
                cost_delta=cost,
            )

    def rebuild_from_ledger(self, session: Session) -> int:
        """
        Löscht alle Aggregate und baut sie aus ``model_usage_records`` neu auf.
        Returns: Anzahl verarbeiteter Ledger-Zeilen.
        """
        session.execute(delete(ModelUsageAggregate))
        rows = session.scalars(select(ModelUsageRecord).order_by(ModelUsageRecord.id)).all()
        for r in rows:
            self.apply_record(session, r)
        return len(rows)


def get_model_usage_aggregation_service() -> ModelUsageAggregationService:
    return ModelUsageAggregationService()
