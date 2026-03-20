"""
Context inspection serializer – stable machine-readable serialization for inspection results.

Explicit field mapping only. No raw object dumping. Deterministic output order.
Stable for snapshot tests.

ORDERING CONTRACT (QA surface):
- Top-level keys: explainability_schema_version, trace, explanation, payload_preview (if present), formatted_blocks (if present)
- formatted_blocks keys: summary, budget, sources, warnings (fixed order when present)
"""

from typing import Any, Dict

from app.context.explainability.context_explanation_serializer import (
    EXPLAINABILITY_SCHEMA_VERSION,
    explanation_to_dict,
    payload_preview_to_dict,
    trace_to_dict,
)


def _formatted_blocks_to_dict(result: Any) -> Dict[str, Any]:
    """
    Build formatted_blocks with explicit keys in deterministic order.

    Keys: summary, budget, sources, warnings (fixed order; only present when built).
    """
    block_order = ("summary", "budget", "sources", "warnings")
    block_sources = {
        "summary": result.formatted_summary,
        "budget": result.formatted_budget,
        "sources": result.formatted_sources,
        "warnings": result.formatted_warnings,
    }
    blocks: Dict[str, Any] = {}
    for key in block_order:
        if block_sources[key] is not None:
            blocks[key] = block_sources[key]
    return blocks


def inspection_result_to_dict(
    result: Any,
    *,
    include_budget: bool = True,
    include_dropped: bool = True,
) -> Dict[str, Any]:
    """
    Serialize ContextInspectionResult to dict with deterministic field order.

    Explicit schema mapping only. No __dict__ recursion. Stable for snapshot tests.
    payload_preview and formatted_blocks only when present (optional/lazy).
    """
    out: Dict[str, Any] = {
        "explainability_schema_version": EXPLAINABILITY_SCHEMA_VERSION,
        "trace": trace_to_dict(
            result.trace,
            include_explanation=False,
            include_budget=include_budget,
            include_dropped=include_dropped,
        ),
        "explanation": explanation_to_dict(
            result.explanation,
            include_budget=include_budget,
            include_dropped=include_dropped,
        ),
    }
    if result.payload_preview is not None:
        out["payload_preview"] = payload_preview_to_dict(result.payload_preview)
    formatted = _formatted_blocks_to_dict(result)
    if formatted:
        out["formatted_blocks"] = formatted
    return out
