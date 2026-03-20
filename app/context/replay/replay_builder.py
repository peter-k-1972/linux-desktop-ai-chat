"""
Replay builder – build ReplayInput from live request result.

No DB access. No randomness. No time dependency.
"""

from typing import Any, Optional

from app.context.replay.replay_models import CURRENT_VERSION, ReplayInput


def from_live_request(
    trace: Any,
    context: Any,
    render_options: Any,
) -> ReplayInput:
    """
    Build ReplayInput from a live context resolution result.

    Args:
        trace: ChatContextResolutionTrace from get_context_explanation(return_trace=True)
        context: ChatRequestContext from the resolution
        render_options: ChatContextRenderOptions from the resolution

    Returns:
        ReplayInput suitable for deterministic replay. No DB access.
    """
    limits_source = getattr(trace, "limits_source", "default") or "default"
    return ReplayInput(
        chat_id=context.chat_id or 0,
        project_id=context.project_id,
        project_name=context.project_name,
        chat_title=context.chat_title or "",
        topic_id=context.topic_id,
        topic_name=context.topic_name,
        is_global_chat=getattr(context, "is_global_chat", False),
        mode=getattr(trace, "mode", "semantic") or "semantic",
        detail=getattr(trace, "detail", "standard") or "standard",
        include_project=render_options.include_project if render_options else True,
        include_chat=render_options.include_chat if render_options else True,
        include_topic=render_options.include_topic if render_options else False,
        max_project_chars=getattr(trace, "max_project_chars", None),
        max_chat_chars=getattr(trace, "max_chat_chars", None),
        max_topic_chars=getattr(trace, "max_topic_chars", None),
        max_total_lines=getattr(trace, "max_total_lines", None),
        limits_source=limits_source,
        source=getattr(trace, "source", "individual_settings") or "individual_settings",
        profile=getattr(trace, "profile", None),
        policy=getattr(trace, "policy", None),
        hint=getattr(trace, "hint", None),
        chat_policy=getattr(trace, "chat_policy", None),
        project_policy=getattr(trace, "project_policy", None),
        profile_enabled=getattr(trace, "profile_enabled", False),
        fields=tuple(getattr(trace, "fields", []) or []),
        base_explanation=getattr(trace, "explanation", None),
        system_version=CURRENT_VERSION,
    )
