"""
Abbildung UI-Settings → Ollama-``think``-Parameter für /api/chat.

Der Presenter-/Port-Chatpfad muss dieselbe Logik nutzen wie Legacy ChatWidget,
sonst liefert Ollama bei Reasoning-Modellen andere Feldaufteilungen als erwartet.
"""

from __future__ import annotations

from typing import Any


def resolve_think_payload_for_ollama(settings: Any) -> Any:
    """
    - ``off`` → ``False`` (explizit kein Thinking-Stream).
    - ``low`` / ``medium`` / ``high`` → durchreichen (u. a. gpt-oss).
    - ``auto`` → ``None`` (Provider/Client-Defaults, z. B. gpt-oss: low im Client).
    """
    mode = getattr(settings, "think_mode", "auto")
    if mode == "off":
        return False
    if mode in ("low", "medium", "high"):
        return mode
    return None
