"""
Context debug flag – gates inspection tooling and explainability logging.

Environment: CONTEXT_DEBUG_ENABLED (truthy: 1, true, yes, on)
Config: context_debug_enabled (AppSettings)
Default: False. Env takes precedence over config.

Gates (no debug overhead when disabled):
- Debug logs: chat_service._inject_chat_context checks before format_context_debug_blocks
- Inspection panel: chat_workspace, introspection_workspace check before adding
- Request capture: request_capture.capture/get_last_request no-op when disabled
- CLI: context_inspect.py, context_explain.py exit 0 with message when disabled
"""

import os
from typing import Optional


def _env_enabled() -> bool:
    v = os.environ.get("CONTEXT_DEBUG_ENABLED", "")
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def _config_enabled() -> bool:
    try:
        from app.services.infrastructure import get_infrastructure
        s = get_infrastructure().settings
        return getattr(s, "context_debug_enabled", False)
    except Exception:
        return False


def is_context_debug_enabled() -> bool:
    """True when context inspection tooling and explainability logging are active."""
    if _env_enabled():
        return True
    return _config_enabled()
