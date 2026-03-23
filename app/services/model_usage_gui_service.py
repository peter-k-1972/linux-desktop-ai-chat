"""
Aggregierte Lese-/Schreibzugriffe für Modell-Usage, Quota und lokale Assets (GUI-Schicht).

Keine Qt-Abhängigkeit. Widgets rufen diese Methoden auf, keine direkte ORM-Nutzung.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.core.config.settings import AppSettings
from app.core.models.registry import get_registry
from app.domain.model_usage.periods import period_starts
from app.persistence.enums import PeriodType, QuotaMode
from app.persistence.orm.models import ModelAsset, ModelQuotaPolicy, ModelStorageRoot, ModelUsageAggregate
from app.persistence.session import session_scope
from app.services.local_model_registry_service import get_local_model_registry_service
from app.services.local_model_scanner_service import get_local_model_scanner_service
from app.services.model_quota_service import (
    EffectiveQuota,
    ModelQuotaService,
    QuotaEvaluationContext,
    UsageSnapshot,
)
from app.services.infrastructure import get_infrastructure


def _api_key_fingerprint(secret: str) -> str:
    s = (secret or "").strip()
    if not s:
        return ""
    return hashlib.sha256(s.encode()).hexdigest()[:32]


class ModelUsageGuiService:
    """Facade für Control-Center, Chat-Details und Einstellungen."""

    def resolve_registry_route(self, model_id: str, settings: AppSettings) -> Dict[str, Any]:
        entry = get_registry().get(model_id)
        cloud_via = bool(getattr(settings, "cloud_via_local", False))
        if entry:
            is_cloud_entry = entry.source_type == "cloud"
            is_online = is_cloud_entry and not cloud_via
            provider_key = entry.provider or ("ollama_cloud" if is_cloud_entry else "local")
            return {
                "model_id": model_id,
                "in_registry": True,
                "display_name": entry.display_name,
                "provider_id": provider_key,
                "source_type": entry.source_type,
                "is_online_route": is_online,
                "requires_api_key": bool(entry.requires_api_key or (is_cloud_entry and not cloud_via)),
                "credential_hint": self._credential_hint(is_online, settings),
            }
        return {
            "model_id": model_id,
            "in_registry": False,
            "display_name": model_id,
            "provider_id": "local",
            "source_type": "local",
            "is_online_route": False,
            "requires_api_key": False,
            "credential_hint": "Lokal (Ollama)",
        }

    def _credential_hint(self, is_online: bool, settings: AppSettings) -> str:
        if not is_online:
            return "Lokal (Ollama)"
        key = (settings.ollama_api_key or "").strip()
        if key:
            fp = _api_key_fingerprint(key)
            return f"Ollama Cloud · API-Key (Kennung …{fp[-6:]})"
        return "Ollama Cloud · kein API-Key in den Einstellungen"

    def get_model_operational_bundle(self, model_id: str, settings: AppSettings) -> Dict[str, Any]:
        """
        Verbrauch, effektive Quota, gematchte Policies, Usage-Qualität, Assets — für Detailansichten.
        """
        route = self.resolve_registry_route(model_id, settings)
        provider_id = route["provider_id"]
        is_online = route["is_online_route"]
        api_fp = _api_key_fingerprint(settings.ollama_api_key or "") if is_online else ""

        out: Dict[str, Any] = {
            "route": route,
            "usage_tokens": {},
            "usage_quality": {},
            "effective_quota": {},
            "matched_policies": [],
            "assets_for_model": [],
            "unassigned_assets": [],
            "storage_roots": [],
            "db_error": None,
        }

        try:
            with session_scope() as session:
                quota = ModelQuotaService()
                ctx = QuotaEvaluationContext(
                    is_online=is_online,
                    model_id=model_id,
                    provider_id=provider_id,
                    api_key_fingerprint=api_fp or None,
                )
                eff = quota.get_effective_quota(session, ctx)
                snap = quota.get_usage_snapshot(
                    session,
                    model_id=model_id,
                    provider_id=provider_id,
                    provider_credential_id=None,
                    scope_type="global",
                    scope_ref="",
                )
                policies = quota.filter_applicable_policies(quota.list_enabled_policies(session), ctx)
                out["usage_tokens"] = {
                    "hour": snap.hour_tokens,
                    "day": snap.day_tokens,
                    "week": snap.week_tokens,
                    "month": snap.month_tokens,
                    "total": snap.total_tokens,
                }
                out["effective_quota"] = {
                    "mode": eff.mode.value,
                    "warn_percent": float(eff.warn_percent),
                    "limit_hour": eff.limit_hour_tokens,
                    "limit_day": eff.limit_day_tokens,
                    "limit_week": eff.limit_week_tokens,
                    "limit_month": eff.limit_month_tokens,
                    "limit_total": eff.limit_total_tokens,
                    "matched_policy_ids": list(eff.matched_policy_ids),
                }
                out["matched_policies"] = [self._policy_to_row(p) for p in policies]
                out["usage_quality"] = self._usage_quality_for_bucket(
                    session, model_id=model_id, provider_id_key=provider_id
                )
                reg = get_local_model_registry_service()
                roots = reg.list_storage_roots(session)
                out["storage_roots"] = [self._root_to_row(r) for r in roots]
                assets = reg.list_assets(session, storage_root_id=None)
                mid = (model_id or "").strip()
                for a in assets:
                    row = self._asset_to_row(a, roots)
                    if (a.model_id or "").strip() == mid:
                        out["assets_for_model"].append(row)
                    elif not (a.model_id or "").strip():
                        out["unassigned_assets"].append(row)
        except OperationalError as e:
            out["db_error"] = str(e)

        return out

    def _usage_quality_for_bucket(self, session, *, model_id: str, provider_id_key: str) -> Dict[str, Any]:
        ps = period_starts()["total"]
        row = session.scalars(
            select(ModelUsageAggregate).where(
                ModelUsageAggregate.model_id == model_id,
                ModelUsageAggregate.provider_id_key == (provider_id_key or "").strip(),
                ModelUsageAggregate.provider_credential_id_key == -1,
                ModelUsageAggregate.scope_type == "global",
                ModelUsageAggregate.scope_ref_key == "",
                ModelUsageAggregate.period_type == PeriodType.TOTAL.value,
                ModelUsageAggregate.period_start == ps,
            )
        ).first()
        if row is None:
            return {"estimated_requests": 0, "total_requests": 0, "note": "noch keine aggregierten Daten"}
        tr = max(0, int(row.request_count or 0))
        est = max(0, int(row.estimated_count or 0))
        exact = max(0, tr - est)
        return {
            "total_requests": tr,
            "estimated_requests": est,
            "exact_requests": exact,
            "note": "Anteil geschätzt: "
            f"{est}/{tr} Anfragen" if tr else "Keine Anfragen erfasst",
        }

    def _policy_to_row(self, p: ModelQuotaPolicy) -> Dict[str, Any]:
        return {
            "id": p.id,
            "enabled": p.is_enabled,
            "scope_type": p.scope_type,
            "scope_ref": p.scope_ref or "",
            "model_id": p.model_id or "",
            "provider_id": p.provider_id or "",
            "mode": p.mode,
            "source": p.source,
            "warn_percent": float(p.warn_percent),
            "limit_hour": p.limit_hour_tokens,
            "limit_day": p.limit_day_tokens,
            "limit_week": p.limit_week_tokens,
            "limit_month": p.limit_month_tokens,
            "limit_total": p.limit_total_tokens,
            "priority": p.priority,
            "notes": p.notes or "",
        }

    def _root_to_row(self, r: ModelStorageRoot) -> Dict[str, Any]:
        return {
            "id": r.id,
            "name": r.name,
            "path_absolute": r.path_absolute,
            "is_enabled": r.is_enabled,
            "is_managed": r.is_managed,
            "is_read_only": r.is_read_only,
            "scan_enabled": r.scan_enabled,
        }

    def _asset_to_row(self, a: ModelAsset, roots: List[ModelStorageRoot]) -> Dict[str, Any]:
        root_name = ""
        for r in roots:
            if r.id == a.storage_root_id:
                root_name = r.name
                break
        st = (a.asset_type or "").strip()
        assigned = bool((a.model_id or "").strip())
        avail = bool(a.is_available)
        return {
            "id": a.id,
            "model_id": a.model_id or "",
            "storage_root_id": a.storage_root_id,
            "storage_root_name": root_name or ("—" if a.storage_root_id is None else "?"),
            "asset_type": st,
            "path_absolute": a.path_absolute,
            "path_relative": a.path_relative or "",
            "is_available": avail,
            "is_managed": a.is_managed,
            "status_label": self._asset_status_label(assigned, avail),
        }

    @staticmethod
    def _asset_status_label(assigned: bool, available: bool) -> str:
        if not assigned:
            return "Nicht zugewiesen"
        if not available:
            return "Fehlt / nicht erreichbar"
        return "OK"

    def list_all_policies(self) -> List[Dict[str, Any]]:
        try:
            with session_scope() as session:
                stmt = select(ModelQuotaPolicy).order_by(
                    ModelQuotaPolicy.priority.desc(), ModelQuotaPolicy.id.asc()
                )
                rows = list(session.scalars(stmt))
                return [self._policy_to_row(p) for p in rows]
        except OperationalError:
            return []

    @staticmethod
    def _norm_limit(v: Optional[int]) -> Optional[int]:
        if v is None or int(v) <= 0:
            return None
        return int(v)

    def save_policy(
        self,
        policy_id: int,
        *,
        is_enabled: bool,
        mode: str,
        warn_percent: float,
        limit_hour: Optional[int],
        limit_day: Optional[int],
        limit_week: Optional[int],
        limit_month: Optional[int],
        limit_total: Optional[int],
        notes: Optional[str],
    ) -> Dict[str, Any]:
        try:
            with session_scope() as session:
                p = session.get(ModelQuotaPolicy, int(policy_id))
                if p is None:
                    return {"ok": False, "error": "Policy nicht gefunden"}
                p.is_enabled = bool(is_enabled)
                p.mode = mode
                p.warn_percent = Decimal(str(warn_percent))
                p.limit_hour_tokens = self._norm_limit(limit_hour)
                p.limit_day_tokens = self._norm_limit(limit_day)
                p.limit_week_tokens = self._norm_limit(limit_week)
                p.limit_month_tokens = self._norm_limit(limit_month)
                p.limit_total_tokens = self._norm_limit(limit_total)
                p.notes = notes
                session.flush()
                return {"ok": True, "policy": self._policy_to_row(p)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def list_all_assets_flat(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"roots": [], "assets": [], "db_error": None}
        try:
            with session_scope() as session:
                reg = get_local_model_registry_service()
                roots = reg.list_storage_roots(session)
                out["roots"] = [self._root_to_row(r) for r in roots]
                assets = reg.list_assets(session, None)
                out["assets"] = [self._asset_to_row(a, roots) for a in assets]
        except OperationalError as e:
            out["db_error"] = str(e)
        return out

    def run_local_inventory_scan(self, *, ensure_default_user_ai_root: bool = True) -> Dict[str, Any]:
        """
        Führt den lokalen Modell-Scan über alle aktiven, scan-fähigen Storage Roots aus.

        Keine Qt-Logik; Ergebnis als Dict für Panels/Tests.
        """
        try:
            with session_scope() as session:
                scanner = get_local_model_scanner_service()
                report = scanner.scan_all_enabled_roots(
                    session, ensure_default_user_ai_root=ensure_default_user_ai_root
                )
                return {"ok": True, **report.to_dict()}
        except OperationalError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def provider_token_summary(self, provider_id_key: str) -> Dict[str, Any]:
        """Summe total-Tokens je Provider (globaler Scope, alle Modelle)."""
        summary: Dict[str, Any] = {"provider_id": provider_id_key, "total_tokens": 0, "models": [], "db_error": None}
        try:
            ps = period_starts()["total"]
            with session_scope() as session:
                stmt = select(ModelUsageAggregate).where(
                    ModelUsageAggregate.provider_id_key == (provider_id_key or "").strip(),
                    ModelUsageAggregate.scope_type == "global",
                    ModelUsageAggregate.scope_ref_key == "",
                    ModelUsageAggregate.period_type == PeriodType.TOTAL.value,
                    ModelUsageAggregate.period_start == ps,
                )
                rows = list(session.scalars(stmt))
                by_model: Dict[str, int] = {}
                for r in rows:
                    by_model[r.model_id] = by_model.get(r.model_id, 0) + int(r.total_tokens or 0)
                summary["total_tokens"] = sum(by_model.values())
                summary["models"] = [
                    {"model_id": k, "total_tokens": v} for k, v in sorted(by_model.items(), key=lambda x: -x[1])
                ][:25]
        except OperationalError as e:
            summary["db_error"] = str(e)
        return summary

    def quick_sidebar_hint(self) -> str:
        """Kurzzeile für Modell-Tab (Chat-Seitenleiste)."""
        try:
            settings = get_infrastructure().settings
            from app.services.model_service import get_model_service

            mid = get_model_service().get_default_model() or "—"
            b = self.get_model_operational_bundle(mid, settings)
            if b.get("db_error"):
                return f"Verbrauch: Datenbank nicht bereit ({mid})"
            u = b.get("usage_tokens") or {}
            return (
                f"Standardmodell {mid}: "
                f"Tag {u.get('day', 0)} / Monat {u.get('month', 0)} / gesamt {u.get('total', 0)} Tokens"
            )
        except Exception:
            return "Verbrauch: —"

    @staticmethod
    def _format_usage_summary_line(snap: UsageSnapshot) -> str:
        def fmt(n: int) -> str:
            n = int(n or 0)
            if n >= 1_000_000:
                return f"{n / 1_000_000:.1f}M"
            if n >= 1000:
                return f"{n / 1000:.1f}k"
            return str(n)

        if not any(
            (
                snap.hour_tokens,
                snap.day_tokens,
                snap.week_tokens,
                snap.month_tokens,
                snap.total_tokens,
            )
        ):
            return "Verbrauch: noch keine Tokens erfasst"
        return (
            f"Tokens · h {fmt(snap.hour_tokens)} · Tag {fmt(snap.day_tokens)} · "
            f"Wo {fmt(snap.week_tokens)} · Mon {fmt(snap.month_tokens)} · Σ {fmt(snap.total_tokens)}"
        )

    @staticmethod
    def _format_quota_summary_line(eff: EffectiveQuota) -> str:
        mode_v = eff.mode.value if hasattr(eff.mode, "value") else str(eff.mode)
        parts = [f"Quota: {mode_v}", f"Warn {float(eff.warn_percent) * 100:.0f}%"]
        lims: List[str] = []
        if eff.limit_day_tokens:
            lims.append(f"Tag≤{eff.limit_day_tokens}")
        if eff.limit_month_tokens:
            lims.append(f"Mon≤{eff.limit_month_tokens}")
        if eff.limit_total_tokens:
            lims.append(f"Σ≤{eff.limit_total_tokens}")
        if lims:
            parts.append(" · ".join(lims))
        elif eff.mode == QuotaMode.NONE:
            parts.append("kein hartes Limit")
        return " · ".join(parts)

    def enrich_unified_catalog_rows(self, rows: List[Dict[str, Any]], settings: AppSettings) -> None:
        """Ergänzt Unified-Katalogzeilen um Usage-/Quota-/Qualitätszeilen (in-place, eine DB-Session)."""
        for row in rows:
            row.setdefault("usage_summary", "")
            row.setdefault("quota_summary", "")
            row.setdefault("usage_quality_note", "")
        try:
            with session_scope() as session:
                quota = ModelQuotaService()
                for row in rows:
                    sid = (row.get("selection_id") or "").strip()
                    if sid.startswith("local-asset:"):
                        row["usage_summary"] = "—"
                        row["quota_summary"] = "Nur registriertes Asset (nicht chat-fähig)"
                        at = (row.get("asset_type") or "").strip()
                        ph = (row.get("path_hint") or "").strip()
                        bits = []
                        if at:
                            bits.append(f"Typ {at}")
                        if ph:
                            bits.append(ph[:80] + ("…" if len(ph) > 80 else ""))
                        row["usage_quality_note"] = " · ".join(bits) if bits else "Keine Modell-Zuordnung"
                        continue
                    route = self.resolve_registry_route(sid, settings)
                    provider_id = route["provider_id"]
                    is_online = route["is_online_route"]
                    api_fp = _api_key_fingerprint(settings.ollama_api_key or "") if is_online else ""
                    ctx = QuotaEvaluationContext(
                        is_online=is_online,
                        model_id=sid,
                        provider_id=provider_id,
                        api_key_fingerprint=api_fp or None,
                    )
                    eff = quota.get_effective_quota(session, ctx)
                    snap = quota.get_usage_snapshot(
                        session,
                        model_id=sid,
                        provider_id=provider_id,
                        provider_credential_id=None,
                        scope_type="global",
                        scope_ref="",
                    )
                    qual = self._usage_quality_for_bucket(
                        session, model_id=sid, provider_id_key=provider_id
                    )
                    row["usage_summary"] = self._format_usage_summary_line(snap)
                    row["quota_summary"] = self._format_quota_summary_line(eff)
                    row["usage_quality_note"] = str(qual.get("note") or "")
        except OperationalError:
            for row in rows:
                if str(row.get("selection_id") or "").startswith("local-asset:"):
                    continue
                row["usage_summary"] = "—"
                row["quota_summary"] = "Datenbank nicht erreichbar"
                row["usage_quality_note"] = ""


def get_model_usage_gui_service() -> ModelUsageGuiService:
    return ModelUsageGuiService()
