"""
Phase B: Zentrale Instrumentierung für produktive Modellaufrufe (Preflight, Usage-Commit).

Ein einziger Laufweg: ModelOrchestrator.chat delegiert hierher. Kein paralleler Legacy-Pfad.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, List, Optional

from app.persistence.enums import UsageStatus, UsageType
from app.persistence.session import session_scope
from app.runtime.model_invocation import (
    ModelInvocationChunkPayload,
    ModelInvocationOutcome,
    attach_model_invocation,
)
from app.services.model_quota_service import (
    ModelQuotaService,
    PreflightDecision,
    QuotaEvaluationContext,
)
from app.services.model_usage_aggregation_service import ModelUsageAggregationService
from app.services.model_usage_service import ModelUsageService, UsageRecordInput
from app.services.provider_usage_normalizer import (
    ProviderUsageState,
    finalize_token_counts,
    merge_provider_usage_state,
)
from app.services.token_usage_estimation import preflight_upper_bound_tokens

from app.chat.provider_stream_normalize import parse_provider_chat_chunk
from app.chat.stream_accumulator import absorb_incremental_or_cumulative

if TYPE_CHECKING:
    from app.core.config.settings import AppSettings
    from app.core.models.orchestrator import ModelOrchestrator

_log = logging.getLogger(__name__)

ERROR_KIND_POLICY_BLOCK = "policy_block"
ERROR_KIND_CONFIG_ERROR = "config_error"
ERROR_KIND_PROVIDER_ERROR = "provider_error"


def _api_key_fingerprint(secret: str) -> str:
    s = (secret or "").strip()
    if not s:
        return ""
    return hashlib.sha256(s.encode()).hexdigest()[:32]


def _resolve_project_id_str(chat_id: Optional[int]) -> Optional[str]:
    if chat_id is None:
        return None
    try:
        from app.services.project_service import get_project_service

        pid = get_project_service().get_project_of_chat(chat_id)
        if pid is None:
            return None
        return str(int(pid))
    except Exception:
        return None


def _meta_json(**payload: Any) -> Optional[str]:
    try:
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return None


def _commit_usage_record(inp: UsageRecordInput) -> int:
    usage_svc = ModelUsageService()
    agg_svc = ModelUsageAggregationService()
    with session_scope() as session:
        row = usage_svc.create_record(session, inp)
        agg_svc.apply_record(session, row)
        return int(row.id)


async def stream_instrumented_model_chat(
    orchestrator: ModelOrchestrator,
    *,
    settings: AppSettings,
    model_id: str,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
    stream: bool,
    think: Any,
    cloud_via_local: bool,
    chat_id: Optional[int],
    usage_type: str,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Preflight (Quota), Provider-Stream, einmaliger Usage-Commit inkl. Aggregation.

    Bei deaktiviertem Tracking: reiner Delegationsstream ohne DB.
    """
    tracking = getattr(settings, "model_usage_tracking_enabled", True)

    def _sync_cloud_key() -> None:
        from app.providers.cloud_ollama_provider import get_ollama_api_key

        raw = (settings.ollama_api_key or "").strip() or get_ollama_api_key()
        orchestrator.cloud_provider.set_api_key(raw)

    _sync_cloud_key()

    entry = orchestrator._registry.get(model_id)
    if (
        entry
        and entry.source_type == "cloud"
        and not cloud_via_local
        and not orchestrator.cloud_provider.has_api_key()
    ):
        msg = "Cloud-Modell erfordert Ollama-API-Key (Einstellungen oder OLLAMA_API_KEY)."
        meta = _meta_json(
            error_kind=ERROR_KIND_CONFIG_ERROR,
            chat_id=chat_id,
            model_id=model_id,
        )
        if tracking:
            rid = _commit_usage_record(
                UsageRecordInput(
                    model_id=model_id,
                    usage_type=usage_type,
                    is_online=True,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    estimated_tokens=False,
                    status=UsageStatus.FAILED.value,
                    provider_id=orchestrator.cloud_provider.provider_id,
                    scope_type="global",
                    scope_ref="",
                    raw_request_meta_json=meta,
                )
            )
        else:
            rid = None
        err_chunk: Dict[str, Any] = {
            "error": msg,
            "error_kind": ERROR_KIND_CONFIG_ERROR,
            "done": True,
        }
        yield attach_model_invocation(
            err_chunk,
            ModelInvocationChunkPayload(
                outcome=ModelInvocationOutcome.CONFIG_ERROR.value,
                usage_record_id=rid,
                preflight_decision=None,
                block_reason="missing_api_key",
            ),
        )
        return

    provider = orchestrator.get_provider_for_model(model_id, cloud_via_local=cloud_via_local)
    provider_id = provider.provider_id
    is_online = provider.source_type == "cloud" and not cloud_via_local
    api_fp = _api_key_fingerprint(settings.ollama_api_key or "") if is_online else ""

    project_id_str = _resolve_project_id_str(chat_id)
    quota_ctx = QuotaEvaluationContext(
        is_online=is_online,
        model_id=model_id,
        provider_id=provider_id,
        api_key_fingerprint=api_fp or None,
        project_id=project_id_str,
    )

    preflight_decision = PreflightDecision.ALLOW
    preflight_message = ""
    warning_active = False

    if tracking:
        quota_svc = ModelQuotaService()
        try:
            with session_scope() as session:
                eff = quota_svc.get_effective_quota(session, quota_ctx)
                snap = quota_svc.get_usage_snapshot(
                    session,
                    model_id=model_id,
                    provider_id=provider_id,
                    provider_credential_id=None,
                    scope_type="global",
                    scope_ref="",
                )
                projected = preflight_upper_bound_tokens(messages, max_tokens)
                pf = quota_svc.evaluate_usage_against_quota(
                    effective=eff,
                    snapshot=snap,
                    projected_additional_tokens=projected,
                )
                preflight_decision = pf.decision
                preflight_message = pf.message or ""
                warning_active = bool(pf.at_warn_threshold) or (
                    pf.decision == PreflightDecision.ALLOW_WITH_WARNING
                )
        except Exception as ex:
            _log.exception("Preflight quota evaluation failed: %s", ex)
            preflight_decision = PreflightDecision.ALLOW
            preflight_message = ""

        if preflight_decision == PreflightDecision.BLOCK:
            meta = _meta_json(
                preflight_decision=preflight_decision,
                chat_id=chat_id,
                model_id=model_id,
                provider_id=provider_id,
                is_online=is_online,
            )
            rid = _commit_usage_record(
                UsageRecordInput(
                    model_id=model_id,
                    usage_type=usage_type,
                    is_online=is_online,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    estimated_tokens=False,
                    status=UsageStatus.BLOCKED.value,
                    provider_id=provider_id,
                    scope_type="global",
                    scope_ref="",
                    block_reason=preflight_message or "quota_block",
                    raw_request_meta_json=meta,
                )
            )
            err_chunk = {
                "error": f"Anfrage blockiert (Limit): {preflight_message or 'Quota'}",
                "error_kind": ERROR_KIND_POLICY_BLOCK,
                "done": True,
            }
            yield attach_model_invocation(
                err_chunk,
                ModelInvocationChunkPayload(
                    outcome=ModelInvocationOutcome.POLICY_BLOCK.value,
                    preflight_decision=preflight_decision,
                    preflight_message=preflight_message,
                    block_reason=preflight_message or "quota_block",
                    usage_record_id=rid,
                    warning_active=False,
                ),
            )
            return

    usage_state = ProviderUsageState()
    assistant_visible = ""
    had_error = False
    error_text: Optional[str] = None
    committed = False
    t0 = time.perf_counter_ns()

    prev_out: Optional[Dict[str, Any]] = None
    try:
        async for raw in orchestrator.stream_raw_chat(
            model_id=model_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            think=think,
            cloud_via_local=cloud_via_local,
        ):
            chunk = dict(raw)
            merge_provider_usage_state(usage_state, chunk)
            if chunk.get("error"):
                had_error = True
                error_text = str(chunk.get("error") or "")
            p_norm = parse_provider_chat_chunk(chunk)
            if p_norm.visible_piece:
                assistant_visible = absorb_incremental_or_cumulative(
                    assistant_visible, p_norm.visible_piece
                )
            extra = ModelInvocationChunkPayload(
                preflight_decision=preflight_decision,
                preflight_message=preflight_message or None,
                warning_active=warning_active
                and preflight_decision == PreflightDecision.ALLOW_WITH_WARNING,
            )
            merged = attach_model_invocation(chunk, extra)
            if prev_out is not None:
                yield prev_out
            prev_out = merged

        latency_ms = int((time.perf_counter_ns() - t0) / 1_000_000)
        assistant_text = assistant_visible

        p_tok, c_tok, t_tok, is_estimated = finalize_token_counts(
            usage_state, messages, assistant_text, max_tokens
        )
        raw_usage_json = usage_state.to_raw_json()

        if not tracking:
            if prev_out is not None:
                yield prev_out
            return

        if had_error:
            if prev_out is not None:
                yield prev_out
            meta = _meta_json(
                error_kind=ERROR_KIND_PROVIDER_ERROR,
                chat_id=chat_id,
                preflight_decision=preflight_decision,
            )
            rid = _commit_usage_record(
                UsageRecordInput(
                    model_id=model_id,
                    usage_type=usage_type,
                    is_online=is_online,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    estimated_tokens=False,
                    status=UsageStatus.FAILED.value,
                    provider_id=provider_id,
                    scope_type="global",
                    scope_ref="",
                    latency_ms=latency_ms,
                    raw_provider_usage_json=raw_usage_json,
                    raw_request_meta_json=meta,
                )
            )
            committed = True
            done_tip: Dict[str, Any] = {"done": True}
            yield attach_model_invocation(
                done_tip,
                ModelInvocationChunkPayload(
                    outcome=ModelInvocationOutcome.PROVIDER_ERROR.value,
                    usage_record_id=rid,
                    latency_ms=latency_ms,
                    preflight_decision=preflight_decision,
                    warning_active=warning_active,
                ),
            )
            return

        meta_ok = _meta_json(
            chat_id=chat_id,
            preflight_decision=preflight_decision,
            token_counts_exact=not is_estimated,
        )
        rid = _commit_usage_record(
            UsageRecordInput(
                model_id=model_id,
                usage_type=usage_type,
                is_online=is_online,
                prompt_tokens=p_tok,
                completion_tokens=c_tok,
                total_tokens=t_tok,
                estimated_tokens=is_estimated,
                status=UsageStatus.SUCCESS.value,
                provider_id=provider_id,
                scope_type="global",
                scope_ref="",
                latency_ms=latency_ms,
                raw_provider_usage_json=raw_usage_json,
                raw_request_meta_json=meta_ok,
            )
        )
        committed = True
        summary = ModelInvocationChunkPayload(
            outcome=ModelInvocationOutcome.SUCCESS.value,
            usage_record_id=rid,
            latency_ms=latency_ms,
            token_counts_exact=not is_estimated,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            total_tokens=t_tok,
            preflight_decision=preflight_decision,
            warning_active=warning_active
            and preflight_decision == PreflightDecision.ALLOW_WITH_WARNING,
        )
        if prev_out is not None:
            yield attach_model_invocation(prev_out, summary)
        else:
            yield attach_model_invocation({"done": True}, summary)

    except asyncio.CancelledError:
        latency_ms = int((time.perf_counter_ns() - t0) / 1_000_000)
        assistant_text = assistant_visible
        if tracking and not committed:
            p_tok, c_tok, t_tok, is_estimated = finalize_token_counts(
                usage_state, messages, assistant_text, max_tokens
            )
            raw_usage_json = usage_state.to_raw_json()
            meta = _meta_json(
                chat_id=chat_id,
                cancelled=True,
                preflight_decision=preflight_decision,
            )
            rid = _commit_usage_record(
                UsageRecordInput(
                    model_id=model_id,
                    usage_type=usage_type,
                    is_online=is_online,
                    prompt_tokens=p_tok,
                    completion_tokens=c_tok,
                    total_tokens=t_tok,
                    estimated_tokens=is_estimated,
                    status=UsageStatus.CANCELLED.value,
                    provider_id=provider_id,
                    scope_type="global",
                    scope_ref="",
                    latency_ms=latency_ms,
                    raw_provider_usage_json=raw_usage_json,
                    raw_request_meta_json=meta,
                )
            )
            committed = True
            yield attach_model_invocation(
                {"done": True},
                ModelInvocationChunkPayload(
                    outcome=ModelInvocationOutcome.CANCELLED.value,
                    usage_record_id=rid,
                    latency_ms=latency_ms,
                    preflight_decision=preflight_decision,
                    token_counts_exact=not is_estimated,
                    prompt_tokens=p_tok,
                    completion_tokens=c_tok,
                    total_tokens=t_tok,
                ),
            )
        raise

    except Exception as ex:
        latency_ms = int((time.perf_counter_ns() - t0) / 1_000_000)
        if tracking and not committed:
            meta = _meta_json(
                chat_id=chat_id,
                exception_type=type(ex).__name__,
                preflight_decision=preflight_decision,
            )
            rid = _commit_usage_record(
                UsageRecordInput(
                    model_id=model_id,
                    usage_type=usage_type,
                    is_online=is_online,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    estimated_tokens=False,
                    status=UsageStatus.FAILED.value,
                    provider_id=provider_id,
                    scope_type="global",
                    scope_ref="",
                    latency_ms=latency_ms,
                    raw_request_meta_json=meta,
                )
            )
            committed = True
            yield attach_model_invocation(
                {"done": True},
                ModelInvocationChunkPayload(
                    outcome=ModelInvocationOutcome.FAILED.value,
                    usage_record_id=rid,
                    latency_ms=latency_ms,
                    preflight_decision=preflight_decision,
                ),
            )
        raise
