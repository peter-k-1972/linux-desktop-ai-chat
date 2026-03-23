"""
ModelUsageService – Ledger-Einträge, Validierung, Abfragen.

Keine GUI; keine Runtime-Hooks (Phase B).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional, Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.persistence.enums import UsageStatus, UsageType
from app.persistence.orm.models import ModelUsageRecord


class UsageValidationError(ValueError):
    """Ungültige Token- oder Status-Eingaben."""


@dataclass
class UsageRecordInput:
    model_id: str
    usage_type: str
    is_online: bool
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: Optional[int] = None
    estimated_tokens: bool = False
    request_count: int = 1
    status: str = UsageStatus.SUCCESS.value
    provider_id: Optional[str] = None
    provider_credential_id: Optional[int] = None
    scope_type: Optional[str] = None
    scope_ref: Optional[str] = None
    block_reason: Optional[str] = None
    latency_ms: Optional[int] = None
    cost_input: Optional[Decimal] = None
    cost_output: Optional[Decimal] = None
    cost_total: Optional[Decimal] = None
    currency: Optional[str] = None
    raw_provider_usage_json: Optional[str] = None
    raw_request_meta_json: Optional[str] = None


class ModelUsageService:
    def normalize_and_validate(self, inp: UsageRecordInput) -> UsageRecordInput:
        if not (inp.model_id or "").strip():
            raise UsageValidationError("model_id fehlt")
        try:
            UsageType(inp.usage_type)
        except ValueError as e:
            raise UsageValidationError(f"usage_type ungültig: {inp.usage_type}") from e
        try:
            UsageStatus(inp.status)
        except ValueError as e:
            raise UsageValidationError(f"status ungültig: {inp.status}") from e
        if inp.prompt_tokens < 0 or inp.completion_tokens < 0:
            raise UsageValidationError("prompt_tokens/completion_tokens dürfen nicht negativ sein")
        if inp.request_count < 1:
            raise UsageValidationError("request_count muss >= 1 sein")
        total = inp.total_tokens
        if total is None:
            total = inp.prompt_tokens + inp.completion_tokens
        elif total < 0:
            raise UsageValidationError("total_tokens negativ")
        if inp.latency_ms is not None and inp.latency_ms < 0:
            raise UsageValidationError("latency_ms negativ")
        return UsageRecordInput(
            model_id=inp.model_id.strip(),
            usage_type=inp.usage_type,
            is_online=inp.is_online,
            prompt_tokens=inp.prompt_tokens,
            completion_tokens=inp.completion_tokens,
            total_tokens=total,
            estimated_tokens=bool(inp.estimated_tokens),
            request_count=inp.request_count,
            status=inp.status,
            provider_id=(inp.provider_id or "").strip() or None,
            provider_credential_id=inp.provider_credential_id,
            scope_type=(inp.scope_type or "").strip() or None,
            scope_ref=(inp.scope_ref or "").strip() or None,
            block_reason=inp.block_reason,
            latency_ms=inp.latency_ms,
            cost_input=inp.cost_input,
            cost_output=inp.cost_output,
            cost_total=inp.cost_total,
            currency=(inp.currency or "").strip() or None,
            raw_provider_usage_json=inp.raw_provider_usage_json,
            raw_request_meta_json=inp.raw_request_meta_json,
        )

    def create_record(self, session: Session, inp: UsageRecordInput) -> ModelUsageRecord:
        v = self.normalize_and_validate(inp)
        row = ModelUsageRecord(
            model_id=v.model_id,
            provider_id=v.provider_id,
            provider_credential_id=v.provider_credential_id,
            usage_type=v.usage_type,
            scope_type=v.scope_type,
            scope_ref=v.scope_ref,
            is_online=v.is_online,
            prompt_tokens=v.prompt_tokens,
            completion_tokens=v.completion_tokens,
            total_tokens=v.total_tokens or 0,
            estimated_tokens=v.estimated_tokens,
            request_count=v.request_count,
            status=v.status,
            block_reason=v.block_reason,
            latency_ms=v.latency_ms,
            cost_input=v.cost_input,
            cost_output=v.cost_output,
            cost_total=v.cost_total,
            currency=v.currency,
            raw_provider_usage_json=v.raw_provider_usage_json,
            raw_request_meta_json=v.raw_request_meta_json,
        )
        session.add(row)
        session.flush()
        return row

    def query_by_time_range(
        self,
        session: Session,
        *,
        start: datetime,
        end: datetime,
        model_id: Optional[str] = None,
        is_online: Optional[bool] = None,
        scope_type: Optional[str] = None,
        scope_ref: Optional[str] = None,
    ) -> Sequence[ModelUsageRecord]:
        stmt: Select[tuple[ModelUsageRecord]] = select(ModelUsageRecord).where(
            ModelUsageRecord.created_at >= start,
            ModelUsageRecord.created_at < end,
        )
        if model_id:
            stmt = stmt.where(ModelUsageRecord.model_id == model_id)
        if is_online is not None:
            stmt = stmt.where(ModelUsageRecord.is_online == is_online)
        if scope_type is not None:
            stmt = stmt.where(ModelUsageRecord.scope_type == scope_type)
        if scope_ref is not None:
            stmt = stmt.where(ModelUsageRecord.scope_ref == scope_ref)
        stmt = stmt.order_by(ModelUsageRecord.id)
        return list(session.scalars(stmt))

    def sum_tokens_in_range(
        self,
        session: Session,
        *,
        start: datetime,
        end: datetime,
        model_id: Optional[str] = None,
        is_online: Optional[bool] = None,
    ) -> dict[str, Any]:
        rows = self.query_by_time_range(
            session, start=start, end=end, model_id=model_id, is_online=is_online
        )
        total = sum(r.total_tokens for r in rows)
        exact_records = sum(1 for r in rows if not r.estimated_tokens)
        est_records = sum(1 for r in rows if r.estimated_tokens)
        return {
            "total_tokens": total,
            "record_count": len(rows),
            "records_with_exact_token_counts": exact_records,
            "records_with_estimated_token_counts": est_records,
        }


def get_model_usage_service() -> ModelUsageService:
    return ModelUsageService()
