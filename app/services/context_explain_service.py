"""
ContextExplainService – Developer-Tooling für Kontext-Explainability.

Keine UI, keine Side Effects. Nur Lesen und Berechnen.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.context.explainability.context_explanation import ContextExplanation
from app.context.explainability.context_explanation_serializer import explainability_to_dict
from app.context.explainability.context_payload_preview import (
    ContextPayloadPreview,
    build_payload_preview,
)
from app.services.chat_service import get_chat_service


@dataclass
class ContextExplainRequest:
    """Anfrage für Kontext-Erklärung."""

    chat_id: int
    request_context_hint: Optional[str] = None
    context_policy: Optional[str] = None


class ContextExplainService:
    """
    Service für Kontext-Explainability (Developer-Tooling).
    """

    def preview(self, request: ContextExplainRequest) -> ContextExplanation:
        """
        Liefert die Kontext-Erklärung für die gegebene Anfrage.

        Keine Side Effects: keine DB-Änderung, keine Injection.
        """
        result = self._resolve(request, return_trace=False)
        return result or ContextExplanation()

    def preview_with_trace(self, request: ContextExplainRequest) -> Any:
        """
        Liefert den vollständigen ChatContextResolutionTrace.

        Enthält policy chain, limits, explanation.
        """
        return self._resolve(request, return_trace=True)

    def preview_with_trace_and_fragment(
        self, request: ContextExplainRequest
    ) -> tuple[Any, Optional[str], Optional[Any], Optional[Any]]:
        """
        Liefert Trace und Fragment in einem Aufruf (keine doppelte Auflösung).

        Returns:
            (trace, fragment, context, render_options)
        """
        result = self._resolve(request, return_trace=True, return_fragment=True)
        return result

    def preview_payload(self, request: ContextExplainRequest) -> ContextPayloadPreview:
        """
        Liefert eine sichere Vorschau des assemblierten Kontext-Payloads.

        Nur Metadaten und Preview-Text aus dem finalen Payload.
        Keine Rekonstruktion von verworfenem Inhalt.
        """
        from app.chat.context_policies import ChatContextPolicy
        from app.chat.request_context_hints import RequestContextHint

        hint = None
        if request.request_context_hint:
            try:
                hint = RequestContextHint(request.request_context_hint)
            except ValueError:
                pass

        policy = None
        if request.context_policy:
            try:
                policy = ChatContextPolicy(request.context_policy)
            except ValueError:
                pass

        fragment, context, render_options = get_chat_service().get_context_payload_fragment(
            chat_id=request.chat_id,
            request_context_hint=hint,
            context_policy=policy,
        )
        return build_payload_preview(
            fragment or "",
            context=context,
            render_options=render_options,
        )

    def preview_as_dict(
        self,
        request: ContextExplainRequest,
        *,
        include_trace: bool = False,
        include_budget: bool = True,
        include_dropped: bool = True,
        include_payload_preview: bool = False,
    ) -> Dict[str, Any]:
        """
        Liefert die Erklärung als Dict (JSON-serialisierbar).

        Nutzt den stabilen Serializer (explainability_to_dict).
        include_trace: policy chain, limits_source, fields
        include_budget: budget accounting fields
        include_dropped: dropped_by_source, dropped_reasons, dropped_total_tokens
        include_payload_preview: payload_preview with sections, tokens, lines
        """
        trace = self._resolve(request, return_trace=True)
        expl = trace.explanation or ContextExplanation()

        payload_preview = None
        if include_payload_preview:
            payload_preview = self.preview_payload(request)

        return explainability_to_dict(
            trace=trace,
            expl=expl,
            include_trace=include_trace,
            include_budget=include_budget,
            include_dropped=include_dropped,
            include_payload_preview=include_payload_preview,
            payload_preview=payload_preview,
        )

    def _resolve(
        self,
        request: ContextExplainRequest,
        *,
        return_trace: bool = False,
        return_fragment: bool = False,
    ) -> Any:
        from app.chat.context_policies import ChatContextPolicy
        from app.chat.request_context_hints import RequestContextHint

        invalid_sources: list[str] = []
        invalid_inputs: list[tuple[str, str]] = []
        hint = None
        if request.request_context_hint:
            try:
                hint = RequestContextHint(request.request_context_hint)
            except ValueError:
                invalid_sources.append("request_context_hint")
                invalid_inputs.append(("request_context_hint", request.request_context_hint))

        policy = None
        if request.context_policy:
            try:
                policy = ChatContextPolicy(request.context_policy)
            except ValueError:
                invalid_sources.append("explicit_context_policy")
                invalid_inputs.append(("explicit_context_policy", request.context_policy))

        return get_chat_service().get_context_explanation(
            chat_id=request.chat_id,
            request_context_hint=hint,
            context_policy=policy,
            return_trace=return_trace,
            return_fragment=return_fragment,
            invalid_override_sources=invalid_sources if invalid_sources else None,
            invalid_override_inputs=invalid_inputs if invalid_inputs else None,
        )


_context_explain_service: Optional[ContextExplainService] = None


def get_context_explain_service() -> ContextExplainService:
    """Liefert den globalen ContextExplainService."""
    global _context_explain_service
    if _context_explain_service is None:
        _context_explain_service = ContextExplainService()
    return _context_explain_service
