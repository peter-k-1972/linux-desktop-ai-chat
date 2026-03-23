"""
Workflow → ContextExplainService: baut serialisierbare Kontext-Bundles ohne GUI.

Nutzt dieselbe Auflösung wie Explainability (ChatService.get_context_explanation /
get_context_payload_fragment). Tests können den synchronen Einstieg überschreiben.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

WorkflowContextBuildFn = Callable[..., Dict[str, Any]]

_override: Optional[WorkflowContextBuildFn] = None


def set_workflow_context_build_override(fn: Optional[WorkflowContextBuildFn]) -> None:
    """Nur für Tests: Stub statt echtem ContextExplainService / ChatService."""
    global _override
    _override = fn


def _context_text_from_explain_dict(expl_dict: Dict[str, Any]) -> str:
    pp = expl_dict.get("payload_preview")
    if not isinstance(pp, dict):
        return ""
    sections = pp.get("sections") or []
    parts: list[str] = []
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        pt = sec.get("preview_text")
        if isinstance(pt, str) and pt.strip():
            parts.append(pt.strip())
    return "\n".join(parts).strip()


def build_workflow_context_bundle(
    chat_id: int,
    *,
    request_context_hint: Optional[str] = None,
    context_policy: Optional[str] = None,
    include_payload_preview: bool = True,
    include_trace: bool = False,
) -> Dict[str, Any]:
    """
    Liefert JSON-taugliches Bundle für Workflow-Knoten ``context_load``.

    Keys:
        context_payload: Explainability-Dict (Schema wie ContextExplainService.preview_as_dict)
        context_text: zusammengefügte Section-Previews aus payload_preview
        metadata: chat_id, request_context_hint, context_policy
    """
    if _override is not None:
        return _override(
            chat_id,
            request_context_hint=request_context_hint,
            context_policy=context_policy,
            include_payload_preview=include_payload_preview,
            include_trace=include_trace,
        )

    from app.services.context_explain_service import ContextExplainRequest, get_context_explain_service

    req = ContextExplainRequest(
        chat_id=chat_id,
        request_context_hint=request_context_hint,
        context_policy=context_policy,
    )
    svc = get_context_explain_service()
    expl_dict = svc.preview_as_dict(
        req,
        include_trace=include_trace,
        include_budget=True,
        include_dropped=True,
        include_payload_preview=include_payload_preview,
    )
    text = _context_text_from_explain_dict(expl_dict) if include_payload_preview else ""
    return {
        "context_payload": expl_dict,
        "context_text": text,
        "metadata": {
            "chat_id": chat_id,
            "request_context_hint": request_context_hint,
            "context_policy": context_policy,
        },
    }
