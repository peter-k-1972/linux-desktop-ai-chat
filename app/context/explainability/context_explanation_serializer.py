"""
Context explainability – stable machine-readable serialization.

Explicit schema mapping only. No __dict__ recursion. Deterministic field order.
For QA and tooling consumption without parsing formatted text.

Performance: No recursive walk of arbitrary objects; explicit per-type mappers only.

ORDERING CONTRACT (QA surface):
- resolved_settings: by setting_name order [mode, detail_level, policy, project_enabled, chat_enabled, topic_enabled]
- decisions: list order (resolver append order)
- sources: list order (resolver processing order; no sorting applied)
- compressions: list order (resolver append order)
- warnings: list order (resolver append order)
- ignored_inputs: list order (resolver append order)
- dropped_by_source: list order (source iteration order)
- dropped_reasons: first-occurrence order (no set/dict iteration)
- payload sections: [header, project_context, chat_context, topic_context, instruction_block]
- dict keys: explicit fixed order, no implicit iteration
"""

from typing import Any, Dict, List, Optional

EXPLAINABILITY_SCHEMA_VERSION = "1.0"

# Explicit ordering: no dict/set iteration. Resolver order preserved for lists.
RESOLVED_SETTING_ORDER = (
    "mode",
    "detail_level",
    "policy",
    "project_enabled",
    "chat_enabled",
    "topic_enabled",
)
BUDGET_KEYS_ORDER = (
    "configured_budget_total",
    "effective_budget_total",
    "reserved_budget_system",
    "reserved_budget_user",
    "available_budget_for_context",
    "budget_strategy",
    "budget_source",
    "total_tokens_after",
)


def _source_entry_to_dict(s: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextSourceEntry."""
    out: Dict[str, Any] = {
        "source_type": s.source_type,
        "identifier": s.identifier or "",
        "included": s.included,
    }
    if s.chars_before is not None:
        out["chars_before"] = s.chars_before
    if s.chars_after is not None:
        out["chars_after"] = s.chars_after
    if s.chars is not None:
        out["chars"] = s.chars
    if s.lines is not None:
        out["lines"] = s.lines
    if s.budget_allocated is not None:
        out["budget_allocated"] = s.budget_allocated
    if s.budget_used is not None:
        out["budget_used"] = s.budget_used
    if s.budget_dropped is not None:
        out["budget_dropped"] = s.budget_dropped
    if s.selection_order is not None:
        out["selection_order"] = s.selection_order
    if s.reason:
        out["reason"] = s.reason
    return out


def _decision_entry_to_dict(d: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextDecisionEntry."""
    out: Dict[str, Any] = {"decision_type": d.decision_type}
    if d.reason:
        out["reason"] = d.reason
    if d.outcome:
        out["outcome"] = d.outcome
    return out


def _compression_entry_to_dict(c: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextCompressionEntry."""
    out: Dict[str, Any] = {"operation": c.operation}
    if c.original_chars is not None:
        out["original_chars"] = c.original_chars
    if c.final_chars is not None:
        out["final_chars"] = c.final_chars
    if c.before_tokens is not None:
        out["before_tokens"] = c.before_tokens
    if c.after_tokens is not None:
        out["after_tokens"] = c.after_tokens
    if c.dropped_tokens is not None:
        out["dropped_tokens"] = c.dropped_tokens
    if c.reason:
        out["reason"] = c.reason
    return out


def _warning_entry_to_dict(w: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextWarningEntry."""
    out: Dict[str, Any] = {"warning_type": w.warning_type}
    if w.message:
        out["message"] = w.message
    if getattr(w, "source_type", None) is not None:
        out["source_type"] = w.source_type
    if getattr(w, "source_id", None) is not None:
        out["source_id"] = w.source_id
    if getattr(w, "effect", None) is not None:
        out["effect"] = w.effect
    if getattr(w, "dropped_tokens", None) is not None:
        out["dropped_tokens"] = w.dropped_tokens
    return out


def _setting_candidate_to_dict(c: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextSettingCandidate."""
    out: Dict[str, Any] = {
        "priority_index": c.priority_index,
        "source": c.source,
        "value": c.value,
        "applied": c.applied,
    }
    if c.skipped_reason is not None:
        out["skipped_reason"] = c.skipped_reason
    return out


def _resolved_setting_entry_to_dict(e: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextResolvedSettingEntry."""
    return {
        "setting_name": e.setting_name,
        "final_value": e.final_value,
        "winning_source": e.winning_source,
        "candidates": [_setting_candidate_to_dict(c) for c in e.candidates],
        "fallback_used": e.fallback_used,
    }


def _ignored_input_entry_to_dict(e: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextIgnoredInputEntry."""
    out: Dict[str, Any] = {
        "input_name": e.input_name,
        "input_source": e.input_source,
        "reason": e.reason,
        "resolution_effect": e.resolution_effect,
    }
    if e.raw_value is not None:
        out["raw_value"] = e.raw_value
    return out


def _dropped_entry_to_dict(e: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextDroppedEntry."""
    out: Dict[str, Any] = {
        "source_type": e.source_type,
        "reason": e.reason,
    }
    if e.dropped_tokens is not None:
        out["dropped_tokens"] = e.dropped_tokens
    if e.source_id is not None:
        out["source_id"] = e.source_id
    return out


def _payload_section_to_dict(s: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextPayloadSection."""
    out: Dict[str, Any] = {
        "section_name": s.section_name,
        "included": s.included,
        "line_count": s.line_count,
        "token_count": s.token_count,
        "truncated_preview": s.truncated_preview,
    }
    if s.source_type is not None:
        out["source_type"] = s.source_type
    if s.source_id is not None:
        out["source_id"] = s.source_id
    if s.preview_text is not None:
        out["preview_text"] = s.preview_text
    return out


def _payload_preview_to_dict(p: Any) -> Dict[str, Any]:
    """Explicit mapping for ContextPayloadPreview."""
    return {
        "empty": p.empty,
        "total_tokens": p.total_tokens,
        "total_lines": p.total_lines,
        "sections": [_payload_section_to_dict(s) for s in p.sections],
    }


def payload_preview_to_dict(preview: Any) -> Dict[str, Any]:
    """
    Serialize ContextPayloadPreview to dict with deterministic field order.

    Public API for QA and inspection tooling.
    """
    return _payload_preview_to_dict(preview)


def _resolved_settings_by_order(settings: List[Any]) -> List[Any]:
    """Return resolved_settings sorted by RESOLVED_SETTING_ORDER. Deterministic."""
    order_map = {name: i for i, name in enumerate(RESOLVED_SETTING_ORDER)}
    return sorted(
        settings,
        key=lambda e: order_map.get(e.setting_name, 999) if hasattr(e, "setting_name") else 999,
    )


def explanation_to_dict(
    expl: Any,
    *,
    include_budget: bool = True,
    include_dropped: bool = True,
) -> Dict[str, Any]:
    """
    Serialize ContextExplanation to dict with deterministic field order.

    No __dict__ recursion. Explicit schema mapping only.
    Omits None for optional fields.
    Order: resolved_settings, decisions, sources (list order), compressions,
    warnings, ignored_inputs, budget, dropped, then scalar fields.
    """
    # Sources: list order (resolver processing order; no sorting)
    sources_list = list(expl.sources)
    # Resolved settings: explicit setting_name order
    ordered_settings = _resolved_settings_by_order(expl.resolved_settings)

    out: Dict[str, Any] = {
        "resolved_settings": [_resolved_setting_entry_to_dict(e) for e in ordered_settings],
        "decisions": [_decision_entry_to_dict(d) for d in expl.decisions],
        "sources": [_source_entry_to_dict(s) for s in sources_list],
        "compressions": [_compression_entry_to_dict(c) for c in expl.compressions],
        "warnings": [_warning_entry_to_dict(w) for w in expl.warnings],
        "ignored_inputs": [_ignored_input_entry_to_dict(e) for e in expl.ignored_inputs],
    }

    if include_budget:
        budget: Dict[str, Any] = {}
        for key in BUDGET_KEYS_ORDER:
            val = getattr(expl, key, None)
            if val is not None:
                budget[key] = val
        out["budget"] = budget

    if include_dropped:
        # dropped_by_source: list order (source iteration). dropped_reasons: list order (no set).
        dropped: Dict[str, Any] = {
            "dropped_by_source": [_dropped_entry_to_dict(e) for e in expl.dropped_by_source],
            "dropped_reasons": list(expl.dropped_reasons),
        }
        if expl.dropped_total_tokens is not None:
            dropped["dropped_total_tokens"] = expl.dropped_total_tokens
        out["dropped"] = dropped

    out["warning_count"] = getattr(expl, "warning_count", len(expl.warnings))
    out["failsafe_triggered"] = getattr(expl, "failsafe_triggered", False)
    out["empty_result"] = getattr(expl, "empty_result", False)
    empty_reason = getattr(expl, "empty_result_reason", None)
    if empty_reason is not None:
        out["empty_result_reason"] = empty_reason

    return out


POLICY_CHAIN_REQUIRED_KEYS = (
    "source",
    "profile",
    "policy",
    "chat_policy",
    "project_policy",
    "hint",
    "profile_enabled",
    "mode",
    "detail",
    "fields",
    "limits_source",
)
POLICY_CHAIN_OPTIONAL_KEYS = (
    "max_project_chars",
    "max_chat_chars",
    "max_topic_chars",
    "max_total_lines",
)


def _policy_chain_to_dict(trace: Any) -> Dict[str, Any]:
    """Build policy_chain dict with explicit key order. No dict iteration."""
    pc: Dict[str, Any] = {}
    pc["source"] = trace.source
    pc["profile"] = trace.profile
    pc["policy"] = trace.policy
    pc["chat_policy"] = trace.chat_policy
    pc["project_policy"] = trace.project_policy
    pc["hint"] = trace.hint
    pc["profile_enabled"] = trace.profile_enabled
    pc["mode"] = trace.mode
    pc["detail"] = trace.detail
    pc["fields"] = list(trace.fields) if trace.fields else []
    pc["limits_source"] = trace.limits_source
    for key in POLICY_CHAIN_OPTIONAL_KEYS:
        val = getattr(trace, key, None)
        if val is not None:
            pc[key] = val
    return pc


def trace_to_dict(
    trace: Any,
    *,
    include_explanation: bool = True,
    include_budget: bool = True,
    include_dropped: bool = True,
) -> Dict[str, Any]:
    """
    Serialize ChatContextResolutionTrace to dict with deterministic field order.

    No __dict__ recursion. Explicit schema mapping only.
    Omits None for optional fields.
    """
    out: Dict[str, Any] = {
        "explainability_schema_version": EXPLAINABILITY_SCHEMA_VERSION,
        "policy_chain": _policy_chain_to_dict(trace),
    }

    if include_explanation and trace.explanation:
        out["explanation"] = explanation_to_dict(
            trace.explanation,
            include_budget=include_budget,
            include_dropped=include_dropped,
        )

    return out


def explainability_to_dict(
    trace: Any,
    expl: Any,
    *,
    include_trace: bool = False,
    include_budget: bool = True,
    include_dropped: bool = True,
    include_payload_preview: bool = False,
    payload_preview: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Serialize full explainability output for JSON export.

    Deterministic field order. Uses explainability_schema_version.
    """
    out: Dict[str, Any] = {
        "explainability_schema_version": EXPLAINABILITY_SCHEMA_VERSION,
        "explanation": explanation_to_dict(
            expl,
            include_budget=include_budget,
            include_dropped=include_dropped,
        ),
    }

    if include_trace:
        out["policy_chain"] = _policy_chain_to_dict(trace)

    if include_payload_preview and payload_preview is not None:
        out["payload_preview"] = _payload_preview_to_dict(payload_preview)

    return out
