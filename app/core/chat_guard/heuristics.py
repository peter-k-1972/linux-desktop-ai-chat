"""
Heuristische Erkennung für Chat Guard v1.

A. Command / Slash-Pfade
B. Formale Fragen
C. Coding-/Technikfragen
D. Knowledge-/Attributionsfragen
E. Mögliche Ambiguität / Mismatch
"""

import re
from typing import List, Optional, Tuple

from app.core.chat_guard.intent_model import ChatIntent, GuardResult


# --- A. Command / Slash-Pfade ---
_SLASH_PATTERN = re.compile(r"^\s*/(\w+)", re.IGNORECASE)
_KNOWN_COMMANDS = {"think", "agent", "tool", "rag", "code", "formal", "help"}


def _detect_command(text: str) -> Tuple[bool, Optional[str]]:
    """Erkennt /command. Gibt (is_command, command_name) zurück."""
    m = _SLASH_PATTERN.search(text)
    if not m:
        return False, None
    cmd = m.group(1).lower()
    return True, cmd


# --- B. Formale Fragen ---
_FORMAL_PATTERNS = [
    r"\bbeweis",  # Beweis, Beweise, beweisen, etc.
    r"\baxiom\b",
    r"\bdefinition\b",
    r"\bformale?\s+herleitung\b",
    r"\blogisch\b",
    r"\bmathematisch\b",
    r"\btheorem\b",
    r"\bsatz\s+(des|der|von)\b",  # Satz des Pythagoras
    r"\blemma\b",
    r"\bkorollar\b",
    r"\bformal\s+ableiten\b",
    r"\bdeduktiv\b",
    r"\bimplikation\b",
]


def _detect_formal_reasoning(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t, re.IGNORECASE) for p in _FORMAL_PATTERNS)


# --- C. Coding-/Technikfragen ---
_CODING_PATTERNS = [
    r"\bpython\b",
    r"\bcode\b",
    r"\bklasse\b",
    r"\bfunktion\b",
    r"\bdebug\b",
    r"\bdebuggen\b",
    r"\brefactor\b",
    r"\brefaktor\b",
    r"\bstacktrace\b",
    r"\bexception\b",
    r"\bsyntax\b",
    r"\bapi\b",
    r"\bframework\b",
    r"\bimport\b",
    r"\bdef\s+\w+\s*\(",
    r"\bclass\s+\w+",
    r"\berror\b",
    r"\bbug\b",
]


def _detect_coding(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t, re.IGNORECASE) for p in _CODING_PATTERNS)


# --- D. Knowledge-/Attributionsfragen ---
_KNOWLEDGE_PATTERNS = [
    r"\bvon\s+(\w+)",  # "von Goethe"
    r"\bwer\s+schrieb\b",
    r"\bwer\s+hat\s+geschrieben\b",
    r"\bgedicht\b",
    r"\bautor\b",
    r"\bwerk\b",
    r"\broman\b",
    r"\bballade\b",
    r"\bnovelle\b",
    r"\bstück\b",
    r"\bkomponist\b",
    r"\bmaler\b",
    r"\bkünstler\b",
    r"\bverfasser\b",
    r"\bstammt\s+von\b",
    r"\bzugeschrieben\b",
    r"\bgeschrieben\s+von\b",
]


def _detect_knowledge_query(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t, re.IGNORECASE) for p in _KNOWLEDGE_PATTERNS)


# --- E. Mismatch / Ambiguität ---
# Kombination: Wissensfrage + Zuschreibung (Autor/Werk) = Mismatch-Risiko
_MISMATCH_INDICATORS = [
    r"\bvon\s+\w+.*\?",
    r"\bwer\s+schrieb.*\?",
    r"\bautor\s+von\b",
    r"\bwerk\s+von\b",
    r"\bgedicht\s+von\b",
    r"\broman\s+von\b",
]


def _detect_possibly_ambiguous(text: str) -> bool:
    """Mismatch-Risiko: Frage enthält Zuschreibung, die falsch sein könnte."""
    t = (text or "").strip()
    if len(t) < 20:
        return False
    return any(re.search(p, t, re.IGNORECASE) for p in _MISMATCH_INDICATORS)


def assess_intent(text: str) -> Tuple[ChatIntent, List[str]]:
    """
    Heuristische Intent-Erkennung.

    Returns:
        (intent, risk_flags)
    """
    t = (text or "").strip()
    risk_flags: List[str] = []

    # A. Command hat Priorität
    is_cmd, cmd_name = _detect_command(t)
    if is_cmd:
        if cmd_name not in _KNOWN_COMMANDS:
            risk_flags.append("command_unrecognized")
        return ChatIntent.COMMAND, risk_flags

    # B–E. Andere Intents (Priorität: formal > coding > knowledge > ambiguous > chat)
    if _detect_formal_reasoning(t):
        return ChatIntent.FORMAL_REASONING, risk_flags

    if _detect_coding(t):
        return ChatIntent.CODING, risk_flags

    if _detect_knowledge_query(t):
        if _detect_possibly_ambiguous(t):
            risk_flags.append("attribution_risk")
            risk_flags.append("mismatch_risk")
        return ChatIntent.KNOWLEDGE_QUERY, risk_flags

    if _detect_possibly_ambiguous(t):
        risk_flags.append("mismatch_risk")
        return ChatIntent.POSSIBLY_AMBIGUOUS, risk_flags

    return ChatIntent.CHAT, risk_flags
