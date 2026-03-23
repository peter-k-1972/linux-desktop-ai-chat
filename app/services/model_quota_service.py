"""
Quota-Service: Policies laden, effektive Limits, Preflight-Vorbereitung.

Offline: Standard ohne Limits über Seed-Policy ``offline_default`` (mode=none).
Online: Limits über Policies (model/provider/api_key/global) – strengstes Limit gewinnt.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.model_usage.periods import period_starts
from app.persistence.enums import PeriodType, QuotaMode, QuotaScopeType
from app.persistence.orm.models import ModelQuotaPolicy, ModelUsageAggregate


@dataclass
class QuotaEvaluationContext:
    """Kontext für Policy-Matching und Verbrauch."""

    is_online: bool
    model_id: str
    provider_id: Optional[str] = None
    provider_credential_id: Optional[int] = None
    api_key_fingerprint: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class EffectiveQuota:
    """Zusammengeführte Limits (Minimum je Fenster) und Modus."""

    limit_hour_tokens: Optional[int] = None
    limit_day_tokens: Optional[int] = None
    limit_week_tokens: Optional[int] = None
    limit_month_tokens: Optional[int] = None
    limit_total_tokens: Optional[int] = None
    warn_percent: float = 0.8
    mode: QuotaMode = QuotaMode.NONE
    matched_policy_ids: Tuple[int, ...] = ()


@dataclass
class UsageSnapshot:
    """Aktueller Verbrauch aus Aggregaten (globaler Schlüssel, normiert)."""

    hour_tokens: int = 0
    day_tokens: int = 0
    week_tokens: int = 0
    month_tokens: int = 0
    total_tokens: int = 0


class PreflightDecision:
    ALLOW = "allow"
    ALLOW_WITH_WARNING = "allow_with_warning"
    BLOCK = "block"


@dataclass
class QuotaPreflightResult:
    decision: str
    message: str = ""
    at_warn_threshold: bool = False


class ModelQuotaService:
    def list_enabled_policies(self, session: Session) -> List[ModelQuotaPolicy]:
        stmt = (
            select(ModelQuotaPolicy)
            .where(ModelQuotaPolicy.is_enabled.is_(True))
            .order_by(ModelQuotaPolicy.priority.desc(), ModelQuotaPolicy.id.asc())
        )
        return list(session.scalars(stmt))

    def _policy_matches(self, p: ModelQuotaPolicy, ctx: QuotaEvaluationContext) -> bool:
        if p.scope_type == QuotaScopeType.GLOBAL.value:
            pass
        elif p.scope_type == QuotaScopeType.OFFLINE_DEFAULT.value:
            if ctx.is_online:
                return False
        elif p.scope_type == QuotaScopeType.MODEL.value:
            if not p.model_id:
                return False
            if not fnmatch.fnmatchcase(ctx.model_id, p.model_id):
                return False
        elif p.scope_type == QuotaScopeType.API_KEY.value:
            fp = (ctx.api_key_fingerprint or "").strip()
            if not fp or not p.scope_ref or p.scope_ref != fp:
                return False
        elif p.scope_type == QuotaScopeType.PROJECT.value:
            if ctx.project_id is None or p.scope_ref != ctx.project_id:
                return False
        elif p.scope_type == QuotaScopeType.WORKSPACE.value:
            if ctx.workspace_id is None or p.scope_ref != ctx.workspace_id:
                return False
        elif p.scope_type == QuotaScopeType.USER.value:
            if ctx.user_id is None or p.scope_ref != ctx.user_id:
                return False
        else:
            return False

        if p.provider_id:
            pid = (ctx.provider_id or "").strip()
            if not fnmatch.fnmatchcase(pid, p.provider_id):
                return False
        if p.provider_credential_id is not None:
            if ctx.provider_credential_id != p.provider_credential_id:
                return False
        return True

    def filter_applicable_policies(
        self, policies: Sequence[ModelQuotaPolicy], ctx: QuotaEvaluationContext
    ) -> List[ModelQuotaPolicy]:
        return [p for p in policies if self._policy_matches(p, ctx)]

    def merge_effective_quota(self, policies: Sequence[ModelQuotaPolicy]) -> EffectiveQuota:
        def _min(a: Optional[int], b: Optional[int]) -> Optional[int]:
            if a is None:
                return b
            if b is None:
                return a
            return min(a, b)

        eff = EffectiveQuota()
        modes: List[QuotaMode] = []
        ids: List[int] = []
        warns: List[float] = []

        for p in policies:
            modes.append(QuotaMode(p.mode))
            ids.append(p.id)
            eff.limit_hour_tokens = _min(eff.limit_hour_tokens, p.limit_hour_tokens)
            eff.limit_day_tokens = _min(eff.limit_day_tokens, p.limit_day_tokens)
            eff.limit_week_tokens = _min(eff.limit_week_tokens, p.limit_week_tokens)
            eff.limit_month_tokens = _min(eff.limit_month_tokens, p.limit_month_tokens)
            eff.limit_total_tokens = _min(eff.limit_total_tokens, p.limit_total_tokens)
            warns.append(float(p.warn_percent))

        if QuotaMode.HARD_BLOCK in modes:
            eff.mode = QuotaMode.HARD_BLOCK
        elif QuotaMode.WARN in modes:
            eff.mode = QuotaMode.WARN
        else:
            eff.mode = QuotaMode.NONE

        if warns:
            eff.warn_percent = min(warns)
        eff.matched_policy_ids = tuple(ids)
        return eff

    def get_effective_quota(self, session: Session, ctx: QuotaEvaluationContext) -> EffectiveQuota:
        policies = self.filter_applicable_policies(self.list_enabled_policies(session), ctx)
        return self.merge_effective_quota(policies)

    def _aggregate_tokens(
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
    ) -> int:
        stmt = select(ModelUsageAggregate.total_tokens).where(
            ModelUsageAggregate.model_id == model_id,
            ModelUsageAggregate.provider_id_key == provider_id_key,
            ModelUsageAggregate.provider_credential_id_key == provider_credential_id_key,
            ModelUsageAggregate.scope_type == scope_type,
            ModelUsageAggregate.scope_ref_key == scope_ref_key,
            ModelUsageAggregate.period_type == period_type,
            ModelUsageAggregate.period_start == period_start,
        )
        row = session.scalars(stmt).first()
        return int(row or 0)

    def get_usage_snapshot(
        self,
        session: Session,
        *,
        model_id: str,
        provider_id: Optional[str],
        provider_credential_id: Optional[int],
        scope_type: Optional[str],
        scope_ref: Optional[str],
        at: Optional[datetime] = None,
    ) -> UsageSnapshot:
        st, sr = (scope_type or "").strip() or "global", (scope_ref or "").strip()
        pk = (provider_id or "").strip()
        ck = -1 if provider_credential_id is None else int(provider_credential_id)
        starts = period_starts(at)
        return UsageSnapshot(
            hour_tokens=self._aggregate_tokens(
                session,
                model_id=model_id,
                provider_id_key=pk,
                provider_credential_id_key=ck,
                scope_type=st,
                scope_ref_key=sr,
                period_type=PeriodType.HOUR.value,
                period_start=starts["hour"],
            ),
            day_tokens=self._aggregate_tokens(
                session,
                model_id=model_id,
                provider_id_key=pk,
                provider_credential_id_key=ck,
                scope_type=st,
                scope_ref_key=sr,
                period_type=PeriodType.DAY.value,
                period_start=starts["day"],
            ),
            week_tokens=self._aggregate_tokens(
                session,
                model_id=model_id,
                provider_id_key=pk,
                provider_credential_id_key=ck,
                scope_type=st,
                scope_ref_key=sr,
                period_type=PeriodType.WEEK.value,
                period_start=starts["week"],
            ),
            month_tokens=self._aggregate_tokens(
                session,
                model_id=model_id,
                provider_id_key=pk,
                provider_credential_id_key=ck,
                scope_type=st,
                scope_ref_key=sr,
                period_type=PeriodType.MONTH.value,
                period_start=starts["month"],
            ),
            total_tokens=self._aggregate_tokens(
                session,
                model_id=model_id,
                provider_id_key=pk,
                provider_credential_id_key=ck,
                scope_type=st,
                scope_ref_key=sr,
                period_type=PeriodType.TOTAL.value,
                period_start=starts["total"],
            ),
        )

    def evaluate_usage_against_quota(
        self,
        *,
        effective: EffectiveQuota,
        snapshot: UsageSnapshot,
        projected_additional_tokens: int,
    ) -> QuotaPreflightResult:
        """
        Prüft ob aktueller Verbrauch + projizierte Tokens Limits überschreiten.

        - hard_block: bei Überschreitung → BLOCK
        - warn: Überschreitung erzeugt nur Hinweis (kein Block), Warnschwelle bei % des Limits
        - none: immer ALLOW
        """
        if effective.mode == QuotaMode.NONE:
            return QuotaPreflightResult(PreflightDecision.ALLOW, "")

        checks: List[Tuple[Optional[int], int, str]] = [
            (effective.limit_hour_tokens, snapshot.hour_tokens, "hour"),
            (effective.limit_day_tokens, snapshot.day_tokens, "day"),
            (effective.limit_week_tokens, snapshot.week_tokens, "week"),
            (effective.limit_month_tokens, snapshot.month_tokens, "month"),
            (effective.limit_total_tokens, snapshot.total_tokens, "total"),
        ]

        messages: List[str] = []
        at_warn = False

        for lim, used, label in checks:
            if lim is None or lim <= 0:
                continue
            projected = used + projected_additional_tokens
            wp = effective.warn_percent
            if projected > lim:
                msg = f"{label}: Limit {lim} überschritten (aktuell {used}, +{projected_additional_tokens} geschätzt)"
                if effective.mode == QuotaMode.HARD_BLOCK:
                    return QuotaPreflightResult(PreflightDecision.BLOCK, msg)
                messages.append(msg)
            elif wp > 0 and projected >= int(lim * wp):
                at_warn = True
                messages.append(
                    f"{label}: Warnschwelle {int(wp * 100)}% erreicht ({used}/{lim})"
                )

        if messages and effective.mode == QuotaMode.WARN:
            return QuotaPreflightResult(
                PreflightDecision.ALLOW_WITH_WARNING, "; ".join(messages), at_warn_threshold=at_warn
            )
        if at_warn:
            return QuotaPreflightResult(
                PreflightDecision.ALLOW_WITH_WARNING, "; ".join(messages), at_warn_threshold=True
            )
        return QuotaPreflightResult(PreflightDecision.ALLOW, "")


def get_model_quota_service() -> ModelQuotaService:
    return ModelQuotaService()
