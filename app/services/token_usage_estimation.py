"""
Zentrale Token-Schätzung (Fallback wenn Provider keine Usage liefert).

Heuristik: Zeichen/4 (konsistent mit früherem ChatService-Kontext-Accounting).
"""

from __future__ import annotations

from typing import Dict, List


CHARS_PER_TOKEN = 4


def chars_to_tokens(chars: int) -> int:
    if chars <= 0:
        return 0
    return max(1, chars // CHARS_PER_TOKEN)


def estimate_messages_prompt_tokens(messages: List[Dict[str, str]]) -> int:
    total = 0
    for m in messages:
        c = m.get("content") or ""
        if not isinstance(c, str):
            c = str(c)
        total += chars_to_tokens(len(c))
    return total


def estimate_completion_tokens(assistant_text: str) -> int:
    return chars_to_tokens(len(assistant_text or ""))


def preflight_upper_bound_tokens(messages: List[Dict[str, str]], max_tokens: int) -> int:
    """Obere Schranke für Quota-Preflight: Eingabe-Schätzung + angefragte Completion-Obergrenze."""
    return estimate_messages_prompt_tokens(messages) + max(0, int(max_tokens))
