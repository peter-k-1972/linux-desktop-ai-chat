"""
Semantic Sanity Check v1 für Chat Guard.

Konservativ: Bei Unsicherheit eher prüfen als halluzinieren.
Kein großes Fakten-Backend – nur Plausibilitätslogik.
"""

import re
from typing import List

from app.core.chat_guard.intent_model import GuardResult


def _has_attribution_pattern(text: str) -> bool:
    """Frage enthält Autor-/Werk-Zuschreibung."""
    t = (text or "").lower()
    patterns = [
        r"\bvon\s+\w+",
        r"\bautor\s+von\b",
        r"\bwerk\s+von\b",
        r"\bgedicht\s+von\b",
        r"\broman\s+von\b",
        r"\bwer\s+schrieb\b",
        r"\bgeschrieben\s+von\b",
    ]
    return any(re.search(p, t) for p in patterns)


def _has_question_mark(text: str) -> bool:
    return "?" in (text or "")


def run_sanity_check(text: str, intent: str, risk_flags: List[str]) -> List[str]:
    """
    Führt Sanity-Check durch. Gibt zusätzliche sanity_flags zurück.

    v1: Nur attribution_risk bei Wissensfragen mit Zuschreibung.
    """
    sanity: List[str] = []
    t = (text or "").strip()

    if intent == "knowledge_query" and _has_attribution_pattern(t) and _has_question_mark(t):
        if "mismatch_risk" in risk_flags or "attribution_risk" in risk_flags:
            sanity.append("verify_assumptions")

    return sanity
