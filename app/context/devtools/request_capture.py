"""
Request capture – safe, minimal capture for inspection.

Stores only: chat_id, project_id, message (truncated), explicit context parameters.
Does NOT store: full context payload, resolved context, provider output.

In-memory only. No file storage. Deterministic truncation. No side effects.
Zero sensitive leakage: explicit blocklist enforced.
"""

from typing import Any, Dict, List, Optional

MAX_MESSAGE_CHARS = 500

# Whitelist: only these keys may appear in captured data
ALLOWED_KEYS = frozenset({
    "chat_id",
    "project_id",
    "message",
    "request_context_hint",
    "context_policy",
})

# Blocklist: never stored; enforced on capture and on get
FORBIDDEN_KEYS = frozenset({
    "context_payload",
    "context_payload_preview",
    "resolved_context",
    "fragment",
    "response",
    "chunk",
    "provider_output",
    "provider_response",
    "stream",
    "messages",
    "full_context",
    "injected_context",
})

_captured: Optional[Dict[str, Any]] = None


def _truncate_message(content: str) -> str:
    """Deterministic truncation. Returns at most MAX_MESSAGE_CHARS chars."""
    if not content:
        return ""
    s = str(content)
    if len(s) <= MAX_MESSAGE_CHARS:
        return s
    return s[:MAX_MESSAGE_CHARS]


def _sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return dict with only allowed keys; never any forbidden keys."""
    out: Dict[str, Any] = {}
    for k, v in data.items():
        if k in FORBIDDEN_KEYS:
            continue
        if k in ALLOWED_KEYS:
            out[k] = v
    return out


def _last_user_message(messages: List[Dict[str, str]]) -> str:
    """Extract last user message content. Empty if none."""
    for m in reversed(messages):
        if m.get("role") == "user":
            return m.get("content") or ""
    return ""


def capture(
    chat_id: int,
    messages: List[Dict[str, str]],
    project_id: Optional[int] = None,
    request_context_hint: Optional[str] = None,
    context_policy: Optional[str] = None,
) -> None:
    """
    Capture minimal request data for inspection.

    Stores: chat_id, project_id, message (truncated), explicit context params.
    Does NOT store: full context payload, resolved context, provider output.
    In-memory only. No-op when CONTEXT_DEBUG_ENABLED is False.
    """
    try:
        from app.context.debug.context_debug_flag import is_context_debug_enabled
        if not is_context_debug_enabled():
            return
    except Exception:
        return
    global _captured
    message = _truncate_message(_last_user_message(messages))
    raw = {
        "chat_id": chat_id,
        "project_id": project_id,
        "message": message,
        "request_context_hint": request_context_hint,
        "context_policy": context_policy,
    }
    _captured = _sanitize(raw)


def get_last_request() -> Optional[Dict[str, Any]]:
    """Return last captured request dict, or None if none. Returns a copy. None when debug disabled."""
    try:
        from app.context.debug.context_debug_flag import is_context_debug_enabled
        if not is_context_debug_enabled():
            return None
    except Exception:
        return None
    if _captured is None:
        return None
    return _sanitize(dict(_captured))


def clear_capture() -> None:
    """Clear captured request (for tests)."""
    global _captured
    _captured = None
