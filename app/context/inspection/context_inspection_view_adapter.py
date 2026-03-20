"""
Context inspection view adapter – UI-neutral mapping layer.

Provides a stable, minimal interface for any UI layer without leaking internal structures.
Reuses existing formatter outputs. No transformation of semantics, no sorting or filtering.
Normalizes display for QA comparison: line endings \\n, trim trailing whitespace.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from app.context.debug.context_debug import (
    format_context_budget_summary,
    format_context_resolution_summary,
    format_context_source_summary,
    format_context_warnings,
    format_payload_preview,
)

if TYPE_CHECKING:
    from app.services.context_inspection_service import ContextInspectionResult


def _normalize_display_lines(lines: List[str]) -> List[str]:
    """
    Normalize lines for consistent QA comparison.
    - Line endings to \\n
    - Trim trailing whitespace per line
    - Preserve original ordering strictly
    - Do not collapse duplicate lines
    - No wrapping
    """
    out: List[str] = []
    for line in lines:
        normalized = line.replace("\r\n", "\n").replace("\r", "\n").rstrip()
        out.append(normalized)
    return out


@dataclass(frozen=True)
class ContextInspectionViewModel:
    """
    UI-neutral view model for context inspection.

    All fields are lists of lines from existing formatters. No internal structures exposed.
    """

    summary_lines: List[str]
    budget_lines: List[str]
    source_lines: List[str]
    warning_lines: List[str]
    payload_preview_lines: List[str]
    has_warnings: bool
    has_payload: bool


class ContextInspectionViewAdapter:
    """
    Pure mapping layer: ContextInspectionResult → ContextInspectionViewModel.

    Reuses existing formatter outputs. No transformation, no sorting, no filtering.
    """

    @staticmethod
    def to_view_model(result: "ContextInspectionResult") -> ContextInspectionViewModel:
        """
        Map inspection result to view model.

        Uses pre-built formatted blocks when present; otherwise formats on demand.
        """
        if result.formatted_summary is not None:
            summary_lines = _normalize_display_lines(result.formatted_summary.splitlines())
        else:
            summary_lines = _normalize_display_lines(
                format_context_resolution_summary(result.trace)
            )
        if result.formatted_budget is not None:
            budget_lines = _normalize_display_lines(result.formatted_budget.splitlines())
        else:
            budget_lines = _normalize_display_lines(
                format_context_budget_summary(result.explanation)
            )
        if result.formatted_sources is not None:
            source_lines = _normalize_display_lines(result.formatted_sources.splitlines())
        else:
            source_lines = _normalize_display_lines(
                format_context_source_summary(result.explanation)
            )
        if result.formatted_warnings is not None:
            warning_lines = _normalize_display_lines(result.formatted_warnings.splitlines())
        else:
            warning_lines = _normalize_display_lines(
                format_context_warnings(result.explanation)
            )
        if result.payload_preview is not None:
            payload_str = format_payload_preview(result.payload_preview)
            payload_preview_lines = (
                _normalize_display_lines(payload_str.splitlines())
                if payload_str
                else []
            )
            has_payload = not result.payload_preview.empty
        else:
            payload_preview_lines = []
            has_payload = False

        return ContextInspectionViewModel(
            summary_lines=summary_lines,
            budget_lines=budget_lines,
            source_lines=source_lines,
            warning_lines=warning_lines,
            payload_preview_lines=payload_preview_lines,
            has_warnings=result.formatted_warnings is not None or len(warning_lines) > 0,
            has_payload=has_payload,
        )
