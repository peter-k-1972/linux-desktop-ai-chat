"""
Prompt-Härtung für Chat Guard v1.

Kurz, zielgerichtet, nachvollziehbar.
Keine Prompt-Monster.
"""

from typing import Optional

from app.core.chat_guard.intent_model import ChatIntent, GuardResult


_HINT_FORMAL = (
    "Antworte formal, ohne Meta-Kommentare, mit klarer Struktur. "
    "Vermeide lockere Formulierungen."
)
_HINT_CODING = (
    "Antworte technisch präzise, direkt und ohne Plaudertext. "
    "Code-Beispiele wenn sinnvoll."
)
_HINT_KNOWLEDGE_VERIFY = (
    "Prüfe zuerst, ob die Annahmen in der Frage korrekt sind. "
    "Korrigiere sie gegebenenfalls, bevor du antwortest. "
    "Bei Unsicherheit: explizit darauf hinweisen."
)
_HINT_KNOWLEDGE = (
    "Antworte sachlich und präzise. "
    "Bei Autor-/Werk-Zuschreibungen: Prüfe die Annahmen."
)
_HINT_AMBIGUOUS = (
    "Prüfe die Annahmen in der Frage. "
    "Korrigiere sie gegebenenfalls, bevor du antwortest."
)
_HINT_COMMAND_UNRECOGNIZED = (
    "Der Befehl wurde nicht erkannt. "
    "Antworte hilfreich und erkläre verfügbare Optionen."
)


def build_hint(result: GuardResult) -> Optional[str]:
    """
    Baut den System-Hint für Prompt-Härtung.

    Priorität: sanity_flags > risk_flags > intent
    """
    if "verify_assumptions" in result.sanity_flags:
        return _HINT_KNOWLEDGE_VERIFY

    if "command_unrecognized" in result.risk_flags:
        return _HINT_COMMAND_UNRECOGNIZED

    if "mismatch_risk" in result.risk_flags or "attribution_risk" in result.risk_flags:
        return _HINT_KNOWLEDGE_VERIFY

    if result.intent == ChatIntent.FORMAL_REASONING:
        return _HINT_FORMAL

    if result.intent == ChatIntent.CODING:
        return _HINT_CODING

    if result.intent == ChatIntent.KNOWLEDGE_QUERY:
        return _HINT_KNOWLEDGE

    if result.intent == ChatIntent.POSSIBLY_AMBIGUOUS:
        return _HINT_AMBIGUOUS

    return None


def apply_prompt_hardening(result: GuardResult) -> GuardResult:
    """Fügt system_hint und prompt_mode hinzu, wenn Härtung nötig."""
    hint = build_hint(result)
    if hint:
        result.system_hint = hint
        result.prompt_mode = _mode_for_intent(result.intent)
        if result.intent == ChatIntent.FORMAL_REASONING:
            result.routing_hint = "formal"
        elif result.intent == ChatIntent.CODING:
            result.routing_hint = "coding"
        elif result.intent == ChatIntent.KNOWLEDGE_QUERY:
            result.routing_hint = "knowledge"
    return result


def _mode_for_intent(intent: ChatIntent) -> str:
    m = {
        ChatIntent.FORMAL_REASONING: "formal",
        ChatIntent.CODING: "coding",
        ChatIntent.KNOWLEDGE_QUERY: "knowledge",
        ChatIntent.POSSIBLY_AMBIGUOUS: "verify",
        ChatIntent.COMMAND: "command",
    }
    return m.get(intent, "chat")
