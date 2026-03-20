"""
ContextInspectionService – read-only context inspection for developers and QA.

Exposes context resolution, explainability, payload preview, and trace data
through one stable service entrypoint. No mutation, no persistence, no UI imports.
Composes existing resolver, explainability, serializer, and formatter modules.

Performance: Single resolution path, payload preview and formatted blocks optional.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.context.debug.context_debug import (
    format_context_budget_summary,
    format_context_resolution_summary,
    format_context_source_summary,
    format_context_warnings,
)
from app.context.explainability.context_explanation import ContextExplanation
from app.context.explainability.context_explanation_serializer import (
    explanation_to_dict,
    payload_preview_to_dict,
    trace_to_dict,
)
from app.context.explainability.context_payload_preview import (
    ContextPayloadPreview,
    build_payload_preview,
)
from app.services.context_explain_service import (
    ContextExplainRequest,
    get_context_explain_service,
)


@dataclass(frozen=True)
class ContextInspectionResult:
    """
    Read-only inspection result: explanation, trace, optional payload preview, optional formatted blocks.

    Single entrypoint for all explainability. No mutation, no persistence.

    Required (always present):
        explanation: ContextExplanation – never None
        trace: ChatContextResolutionTrace – never None

    Optional (built lazily when requested):
        payload_preview: built when include_payload_preview=True
        formatted_*: built when include_formatted=True.
        formatted_blocks: property aggregating summary, budget, sources, warnings
    """

    explanation: ContextExplanation
    trace: Any  # ChatContextResolutionTrace
    payload_preview: Optional[ContextPayloadPreview] = None
    formatted_summary: Optional[str] = None
    formatted_budget: Optional[str] = None
    formatted_sources: Optional[str] = None
    formatted_warnings: Optional[str] = None

    @property
    def formatted_blocks(self) -> Optional[Dict[str, str]]:
        """
        Single entrypoint for all formatted blocks. Returns dict when include_formatted=True.

        Keys: summary, budget, sources, warnings (only present when built).
        """
        blocks: Dict[str, str] = {}
        if self.formatted_summary is not None:
            blocks["summary"] = self.formatted_summary
        if self.formatted_budget is not None:
            blocks["budget"] = self.formatted_budget
        if self.formatted_sources is not None:
            blocks["sources"] = self.formatted_sources
        if self.formatted_warnings is not None:
            blocks["warnings"] = self.formatted_warnings
        return blocks if blocks else None


class ContextInspectionService:
    """
    Read-only context inspection service for developers and QA.

    Composes existing resolver, explainability, serializer, and formatter logic.
    No mutation, no persistence, no UI imports.
    """

    def inspect(
        self,
        request: ContextExplainRequest,
        *,
        include_payload_preview: bool = True,
        include_formatted: bool = True,
    ) -> ContextInspectionResult:
        """
        Inspect context resolution for the given request.

        Single resolution path: no duplicate context assembly.
        include_payload_preview: build payload preview from fragment (default True).
        include_formatted: build formatted text blocks (summary, budget, sources, warnings).
        """
        explain = get_context_explain_service()
        trace, fragment, context, render_options = explain.preview_with_trace_and_fragment(
            request
        )
        expl = trace.explanation or ContextExplanation()

        payload_preview: Optional[ContextPayloadPreview] = None
        if include_payload_preview:
            payload_preview = build_payload_preview(
                fragment or "",
                context=context,
                render_options=render_options,
            )

        formatted_summary: Optional[str] = None
        formatted_budget: Optional[str] = None
        formatted_sources: Optional[str] = None
        formatted_warnings: Optional[str] = None
        if include_formatted:
            summary_lines: List[str] = format_context_resolution_summary(trace)
            formatted_summary = "\n".join(summary_lines) if summary_lines else ""

            budget_lines: List[str] = format_context_budget_summary(expl)
            formatted_budget = "\n".join(budget_lines) if budget_lines else ""

            source_lines: List[str] = format_context_source_summary(expl)
            formatted_sources = "\n".join(source_lines) if source_lines else ""

            warn_lines: List[str] = format_context_warnings(expl)
            formatted_warnings = "\n".join(warn_lines) if warn_lines else None

        return ContextInspectionResult(
            explanation=expl,
            trace=trace,
            payload_preview=payload_preview,
            formatted_summary=formatted_summary,
            formatted_budget=formatted_budget,
            formatted_sources=formatted_sources,
            formatted_warnings=formatted_warnings,
        )

    def inspect_as_dict(
        self,
        request: ContextExplainRequest,
        *,
        include_budget: bool = True,
        include_dropped: bool = True,
        include_payload_preview: bool = True,
        include_formatted: bool = True,
    ) -> Dict[str, Any]:
        """
        Inspect context resolution and return a JSON-serializable dict.

        Keys: explanation, trace; payload_preview and formatted_* when requested.
        """
        result = self.inspect(
            request,
            include_payload_preview=include_payload_preview,
            include_formatted=include_formatted,
        )

        out: Dict[str, Any] = {
            "explanation": explanation_to_dict(
                result.explanation,
                include_budget=include_budget,
                include_dropped=include_dropped,
            ),
            "trace": trace_to_dict(
                result.trace,
                include_explanation=False,
                include_budget=include_budget,
                include_dropped=include_dropped,
            ),
        }
        if result.payload_preview is not None:
            out["payload_preview"] = payload_preview_to_dict(result.payload_preview)
        if result.formatted_blocks is not None:
            out["formatted_blocks"] = result.formatted_blocks
        return out


_context_inspection_service: Optional[ContextInspectionService] = None


def get_context_inspection_service() -> ContextInspectionService:
    """Return the global ContextInspectionService instance."""
    global _context_inspection_service
    if _context_inspection_service is None:
        _context_inspection_service = ContextInspectionService()
    return _context_inspection_service
