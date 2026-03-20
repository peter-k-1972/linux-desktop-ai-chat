"""
Context debug formatter – deterministic, readable output for context explanation.

Plain text only, stable snapshot-friendly format. No dynamic sorting of dicts.
Dedicated formatters for grep-friendly logging with stable markers.

Stable across environments: \\n line endings only, no timestamps, no random IDs,
no memory addresses. Safe for CI snapshot comparison.

ORDERING CONTRACT (QA surface):
- resolved_settings: list order (setting_name order from resolver)
- decisions: list order (resolver append order)
- sources: list order (resolver processing order; no sorting)
- compressions: list order (resolver append order)
- dropped_by_source: list order (source iteration order)
- dropped_reasons: list order (first-occurrence, no set iteration)
- warnings: list order (resolver append order)
- payload sections: list order (header, project, chat, topic, instruction_block)
- Section order: resolution, resolved_settings, empty_result, budget, dropped, decisions, sources, compression, ignored, warnings
"""

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.chat.context_profiles import ChatContextResolutionTrace
    from app.context.explainability.context_explanation import ContextExplanation
    from app.context.explainability.context_payload_preview import ContextPayloadPreview

CTX_RESOLUTION = "[CTX_RESOLUTION]"
CTX_BUDGET = "[CTX_BUDGET]"
CTX_SOURCES = "[CTX_SOURCES]"
CTX_WARN = "[CTX_WARN]"


def format_context_explanation(
    expl: Optional["ContextExplanation"] = None,
    trace: Optional["ChatContextResolutionTrace"] = None,
    *,
    include_budget: bool = True,
    include_dropped: bool = True,
) -> str:
    """
    Format context explanation in a deterministic, readable multi-line format.

    Sections: budget, source budget consumption, dropped context summary,
    decisions (resolver order), sources (selection order), compression, warnings.

    Args:
        expl: ContextExplanation to format. If None and trace has explanation, uses trace.explanation.
        trace: Optional trace for mode/detail/policy. If provided, includes resolution metadata.

    Returns:
        Multi-line string, deterministic output.
    """
    from app.context.explainability.context_explanation import ContextExplanation

    explanation = expl or (trace.explanation if trace else None)
    lines: list[str] = []

    if trace:
        lines.append("=== Context Resolution ===")
        lines.append(f"source: {trace.source}")
        lines.append(f"mode: {trace.mode}")
        lines.append(f"detail: {trace.detail}")
        lines.append(f"profile: {trace.profile or 'none'}")
        lines.append(f"policy: {trace.policy or 'none'}")
        lines.append(f"hint: {trace.hint or 'none'}")
        lines.append(f"fields: {','.join(trace.fields) if trace.fields else 'none'}")
        lines.append("")

    # --- Resolved Settings (priority chain) ---
    resolved_settings = getattr(explanation, "resolved_settings", None) or []
    if resolved_settings:
        lines.append("=== Resolved Settings (Priority Chain) ===")
        for e in resolved_settings:
            lines.append(f"  {e.setting_name}: final={e.final_value} winning_source={e.winning_source} fallback_used={e.fallback_used}")
            for c in e.candidates:
                status = "APPLIED" if c.applied else f"skipped={c.skipped_reason or '?'}"
                val = c.value if c.value is not None else "—"
                lines.append(f"    [{c.priority_index}] {c.source}: {val} ({status})")
        lines.append("")

    if not explanation:
        return "\n".join(lines) if lines else "(no explanation)"

    # --- Empty Result (edge-case explainability) ---
    empty_result = getattr(explanation, "empty_result", False)
    empty_reason = getattr(explanation, "empty_result_reason", None)
    if empty_result or empty_reason:
        lines.append("=== Empty Result ===")
        lines.append(f"  empty_result={empty_result}")
        if empty_reason:
            lines.append(f"  empty_result_reason={empty_reason}")
        lines.append("")

    # --- Budget ---
    if include_budget:
        lines.append("=== Budget ===")
        if any(
            getattr(explanation, k) is not None
            for k in (
                "configured_budget_total",
                "effective_budget_total",
                "reserved_budget_system",
                "reserved_budget_user",
                "available_budget_for_context",
                "budget_strategy",
                "budget_source",
            )
        ):
            if explanation.configured_budget_total is not None:
                lines.append(f"  configured={explanation.configured_budget_total}")
            if explanation.effective_budget_total is not None:
                lines.append(f"  effective={explanation.effective_budget_total}")
            if explanation.reserved_budget_system is not None:
                lines.append(f"  reserved_system={explanation.reserved_budget_system}")
            if explanation.reserved_budget_user is not None:
                lines.append(f"  reserved_user={explanation.reserved_budget_user}")
            if explanation.available_budget_for_context is not None:
                lines.append(f"  available_context={explanation.available_budget_for_context}")
            if explanation.budget_strategy:
                lines.append(f"  strategy={explanation.budget_strategy}")
            if explanation.budget_source:
                lines.append(f"  source={explanation.budget_source}")
        else:
            lines.append("  (none)")
        lines.append("")

        lines.append("=== Source Budget Consumption ===")
        if explanation.sources:
            for s in explanation.sources:
                used = s.budget_used if s.budget_used is not None else 0
                dropped = s.budget_dropped if s.budget_dropped is not None else 0
                lines.append(f"  {s.source_type} used={used} dropped={dropped}")
        else:
            lines.append("  (none)")
        lines.append("")

    # --- Dropped Context ---
    if include_dropped:
        lines.append("=== Dropped Context Summary ===")
        total_dropped = getattr(explanation, "dropped_total_tokens", None)
        if total_dropped is None and explanation.compressions:
            for c in explanation.compressions:
                if c.dropped_tokens is not None:
                    total_dropped = (total_dropped or 0) + c.dropped_tokens
        if total_dropped is not None:
            lines.append(f"  total_dropped_tokens={total_dropped}")
        else:
            lines.append("  (none)")
        lines.append("")

        dropped_by = getattr(explanation, "dropped_by_source", None) or []
        if dropped_by:
            lines.append("=== Dropped By Source ===")
            for e in dropped_by:
                parts = [e.source_type, f"reason={e.reason}"]
                if e.dropped_tokens is not None:
                    parts.append(f"dropped_tokens={e.dropped_tokens}")
                if e.source_id:
                    id_preview = e.source_id[:40] + ("..." if len(e.source_id) > 40 else "")
                    parts.append(f"id={id_preview}")
                lines.append("  " + " ".join(parts))
            lines.append("")

        dropped_reasons = getattr(explanation, "dropped_reasons", None) or []
        if dropped_reasons:
            lines.append("=== Dropped Reasons ===")
            for r in dropped_reasons:
                lines.append(f"  {r}")
            lines.append("")

    # --- Decisions (resolver order) ---
    lines.append("=== Decisions ===")
    if explanation.decisions:
        for d in explanation.decisions:
            line = f"  {d.decision_type}"
            if d.reason:
                line += f" reason={d.reason}"
            if d.outcome:
                line += f" outcome={d.outcome}"
            lines.append(line)
    else:
        lines.append("  (none)")
    lines.append("")

    # --- Sources (selection order) ---
    lines.append("=== Sources ===")
    if explanation.sources:
        for s in explanation.sources:
            parts = [f"{s.source_type}", f"included={s.included}"]
            if s.selection_order is not None:
                parts.append(f"order={s.selection_order}")
            if s.identifier:
                id_preview = s.identifier[:40] + ("..." if len(s.identifier) > 40 else "")
                parts.append(f"id={id_preview}")
            if s.chars_before is not None:
                parts.append(f"chars_before={s.chars_before}")
            if s.chars_after is not None:
                parts.append(f"chars_after={s.chars_after}")
            if s.budget_allocated is not None:
                parts.append(f"allocated={s.budget_allocated}")
            if s.budget_used is not None:
                parts.append(f"used={s.budget_used}")
            if s.budget_dropped is not None:
                parts.append(f"dropped={s.budget_dropped}")
            if s.reason:
                parts.append(f"reason={s.reason}")
            lines.append("  " + " ".join(parts))
    else:
        lines.append("  (none)")
    lines.append("")

    # --- Compression (source order / list order) ---
    lines.append("=== Compression ===")
    if explanation.compressions:
        for c in explanation.compressions:
            parts = [c.operation]
            if c.original_chars is not None:
                parts.append(f"original_chars={c.original_chars}")
            if c.final_chars is not None:
                parts.append(f"final_chars={c.final_chars}")
            if c.before_tokens is not None:
                parts.append(f"before_tokens={c.before_tokens}")
            if c.after_tokens is not None:
                parts.append(f"after_tokens={c.after_tokens}")
            if c.dropped_tokens is not None:
                parts.append(f"dropped_tokens={c.dropped_tokens}")
            if c.reason:
                parts.append(f"reason={c.reason}")
            lines.append("  " + " ".join(parts))
    else:
        lines.append("  (none)")
    lines.append("")

    # --- Ignored Inputs ---
    ignored_inputs = getattr(explanation, "ignored_inputs", None) or []
    if ignored_inputs:
        lines.append("=== Ignored Inputs ===")
        for e in ignored_inputs:
            val = e.raw_value if e.raw_value is not None else "—"
            lines.append(f"  {e.input_name} source={e.input_source} raw={val} reason={e.reason} effect={e.resolution_effect}")
        lines.append("")

    # --- Warnings (append order) ---
    lines.append("=== Warnings ===")
    if explanation.warnings:
        for w in explanation.warnings:
            line = f"  {w.warning_type}"
            if w.message:
                line += f": {w.message}"
            if getattr(w, "effect", None):
                line += f" effect={w.effect}"
            if getattr(w, "source_type", None):
                line += f" source_type={w.source_type}"
            if getattr(w, "source_id", None):
                line += f" source_id={w.source_id}"
            if getattr(w, "dropped_tokens", None) is not None:
                line += f" dropped_tokens={w.dropped_tokens}"
            lines.append(line)
    else:
        lines.append("  (none)")

    return "\n".join(lines) + "\n"


# --- Dedicated log formatters (grep-friendly, stable markers) ---


def format_context_trace_block(trace: "ChatContextResolutionTrace") -> str:
    """
    Multi-line trace block: source, mode, detail, profile, policy, hint, fields.
    Deterministic, snapshot-friendly.
    """
    lines = [
        "=== Context Resolution ===",
        f"source: {trace.source}",
        f"mode: {trace.mode}",
        f"detail: {trace.detail}",
        f"profile: {trace.profile or 'none'}",
        f"policy: {trace.policy or 'none'}",
        f"hint: {trace.hint or 'none'}",
        f"fields: {','.join(trace.fields) if trace.fields else 'none'}",
    ]
    return "\n".join(lines) + "\n"


def format_context_resolution_summary(trace: "ChatContextResolutionTrace") -> List[str]:
    """
    One summary line for resolution. Each line prefixed with [CTX_RESOLUTION].
    Deterministic, snapshot-friendly.
    """
    fields_str = ",".join(trace.fields) if trace.fields else "none"
    parts = [
        f"source={trace.source}",
        f"mode={trace.mode}",
        f"detail={trace.detail}",
        f"profile={trace.profile or 'none'}",
        f"policy={trace.policy or 'none'}",
        f"hint={trace.hint or 'none'}",
        f"profile_enabled={trace.profile_enabled}",
        f"fields={fields_str}",
    ]
    return [f"{CTX_RESOLUTION} " + " ".join(parts)]


def format_context_budget_summary(explanation: "ContextExplanation") -> List[str]:
    """
    Budget block. Each line prefixed with [CTX_BUDGET].
    Deterministic ordering.
    """
    lines: List[str] = []
    if explanation.configured_budget_total is not None:
        lines.append(f"{CTX_BUDGET} configured={explanation.configured_budget_total}")
    if explanation.effective_budget_total is not None:
        lines.append(f"{CTX_BUDGET} effective={explanation.effective_budget_total}")
    if explanation.reserved_budget_system is not None:
        lines.append(f"{CTX_BUDGET} reserved_system={explanation.reserved_budget_system}")
    if explanation.reserved_budget_user is not None:
        lines.append(f"{CTX_BUDGET} reserved_user={explanation.reserved_budget_user}")
    if explanation.available_budget_for_context is not None:
        lines.append(f"{CTX_BUDGET} available_context={explanation.available_budget_for_context}")
    if explanation.budget_strategy:
        lines.append(f"{CTX_BUDGET} strategy={explanation.budget_strategy}")
    if explanation.budget_source:
        lines.append(f"{CTX_BUDGET} source={explanation.budget_source}")
    if explanation.sources:
        for s in explanation.sources:
            used = s.budget_used if s.budget_used is not None else 0
            dropped = s.budget_dropped if s.budget_dropped is not None else 0
            lines.append(f"{CTX_BUDGET} {s.source_type} used={used} dropped={dropped}")
    if not lines:
        lines.append(f"{CTX_BUDGET} (none)")
    return lines


def format_context_source_summary(explanation: "ContextExplanation") -> List[str]:
    """
    Sources block. Each line prefixed with [CTX_SOURCES].
    List order (resolver processing order; no sorting).
    """
    lines: List[str] = []
    if explanation.sources:
        for s in explanation.sources:
            parts = [f"{s.source_type}", f"included={s.included}"]
            if s.selection_order is not None:
                parts.append(f"order={s.selection_order}")
            if s.identifier:
                id_preview = s.identifier[:40] + ("..." if len(s.identifier) > 40 else "")
                parts.append(f"id={id_preview}")
            if s.chars_before is not None:
                parts.append(f"chars_before={s.chars_before}")
            if s.chars_after is not None:
                parts.append(f"chars_after={s.chars_after}")
            if s.budget_allocated is not None:
                parts.append(f"allocated={s.budget_allocated}")
            if s.budget_used is not None:
                parts.append(f"used={s.budget_used}")
            if s.budget_dropped is not None:
                parts.append(f"dropped={s.budget_dropped}")
            if s.reason:
                parts.append(f"reason={s.reason}")
            lines.append(f"{CTX_SOURCES} " + " ".join(parts))
    else:
        lines.append(f"{CTX_SOURCES} (none)")
    return lines


def format_context_warnings(explanation: "ContextExplanation") -> List[str]:
    """
    Warnings block. Each line prefixed with [CTX_WARN].
    Returns empty list if no warnings (caller should skip logging).
    Includes effect, source_type, source_id, dropped_tokens when present.
    """
    lines: List[str] = []
    for w in explanation.warnings:
        line = f"{CTX_WARN} {w.warning_type}"
        if w.message:
            line += f": {w.message}"
        if getattr(w, "effect", None):
            line += f" effect={w.effect}"
        if getattr(w, "source_type", None):
            line += f" source_type={w.source_type}"
        if getattr(w, "source_id", None):
            line += f" source_id={w.source_id}"
        if getattr(w, "dropped_tokens", None) is not None:
            line += f" dropped_tokens={w.dropped_tokens}"
        lines.append(line)
    return lines


def format_context_injection_summary(
    chars: int,
    lines: int,
    fields: List[str],
) -> List[str]:
    """One line for successful injection. Prefixed with [CTX_RESOLUTION]."""
    fields_str = ",".join(fields) if fields else "none"
    return [f"{CTX_RESOLUTION} injected chars={chars} lines={lines} fields={fields_str}"]


def format_context_debug_blocks(trace: "ChatContextResolutionTrace") -> List[str]:
    """
    All debug blocks for resolver logging: resolution, budget, sources, warnings.
    One summary line, one budget block, one sources block, warnings only if present.
    No duplication. Deterministic order. Each line has stable marker.
    """
    expl = trace.explanation
    lines: List[str] = []
    lines.extend(format_context_resolution_summary(trace))
    if expl:
        empty_result = getattr(expl, "empty_result", False)
        empty_reason = getattr(expl, "empty_result_reason", None)
        if empty_result or empty_reason:
            lines.append(f"{CTX_RESOLUTION} empty_result={empty_result} empty_result_reason={empty_reason or 'none'}")
        lines.extend(format_context_budget_summary(expl))
        lines.extend(format_context_source_summary(expl))
        warn_lines = format_context_warnings(expl)
        if warn_lines:
            lines.extend(warn_lines)
    return lines


def format_payload_preview(preview: "ContextPayloadPreview") -> str:
    """
    Format payload preview in a deterministic, readable multi-line format.

    Sections: summary, then each section with metadata and optional preview_text.
    """
    lines: list[str] = []
    lines.append("=== Payload Preview ===")
    lines.append(f"empty: {preview.empty}")
    lines.append(f"total_tokens: {preview.total_tokens}")
    lines.append(f"total_lines: {preview.total_lines}")
    lines.append("")

    if preview.sections:
        lines.append("=== Sections ===")
        for s in preview.sections:
            parts = [f"{s.section_name}", f"included={s.included}", f"lines={s.line_count}", f"tokens={s.token_count}"]
            if s.source_type:
                parts.append(f"source_type={s.source_type}")
            if s.source_id:
                id_preview = s.source_id[:40] + ("..." if len(s.source_id) > 40 else "")
                parts.append(f"source_id={id_preview}")
            lines.append("  " + " ".join(parts))
            if s.preview_text:
                for ln in s.preview_text.splitlines():
                    lines.append(f"    | {ln}")
                if s.truncated_preview:
                    lines.append("    | ...")
        lines.append("")

    return "\n".join(lines) + "\n"
