"""
Chat Guard Service – Orchestrierung von Intent, Sanity und Prompt-Härtung.

v1: Heuristik
v2: Heuristik + optionale ML-/Embedding-Intent-Erkennung
"""

from typing import Any, Dict, List, Optional

from app.core.chat_guard.fusion import apply_fusion_to_result
from app.core.chat_guard.heuristics import assess_intent
from app.core.chat_guard.intent_model import ChatIntent, GuardResult
from app.core.chat_guard.prompt_hardening import apply_prompt_hardening
from app.core.chat_guard.sanity_check import run_sanity_check


def _ml_enabled() -> bool:
    """Prüft ob ML-Intent-Erkennung aktiviert ist."""
    try:
        from app.services.infrastructure import get_infrastructure
        return getattr(
            get_infrastructure().settings,
            "chat_guard_ml_enabled",
            False,
        )
    except Exception:
        return False


class ChatGuardService:
    """
    Chatwächter v1/v2: Bewertet User-Input, härtet Prompt bei Bedarf.
    v2: Optionale ML-/Embedding-Intent-Erkennung wenn chat_guard_ml_enabled.
    """

    def __init__(self, ml_classifier=None):
        self._ml_classifier = ml_classifier

    def assess(self, user_content: str) -> GuardResult:
        """Synchrone Bewertung (nur Heuristik). Für Tests."""
        intent, risk_flags = assess_intent(user_content)
        sanity_flags = run_sanity_check(user_content, intent.value, risk_flags)
        result = GuardResult(
            intent=intent,
            risk_flags=risk_flags,
            sanity_flags=sanity_flags,
        )
        return apply_prompt_hardening(result)

    async def assess_async(self, user_content: str) -> GuardResult:
        """
        Bewertet die User-Anfrage. v2: Nutzt ML wenn chat_guard_ml_enabled.
        """
        intent, risk_flags = assess_intent(user_content)
        sanity_flags = run_sanity_check(user_content, intent.value, risk_flags)
        result = GuardResult(
            intent=intent,
            risk_flags=risk_flags,
            sanity_flags=sanity_flags,
        )

        ml_intent: Optional[ChatIntent] = None
        ml_confidence = 0.0

        if _ml_enabled():
            try:
                from app.core.chat_guard.ml_intent_classifier import MLIntentClassifier
                classifier = self._ml_classifier or MLIntentClassifier()
                ml_intent, ml_confidence = await classifier.classify(user_content)
                result = apply_fusion_to_result(result, ml_intent, ml_confidence, True)
            except Exception:
                result = apply_fusion_to_result(result, None, 0.0, False)
        else:
            result.heuristic_intent = intent
            result.decision_source = "heuristic"

        return apply_prompt_hardening(result)

    def apply_to_messages(
        self,
        messages: List[Dict[str, Any]],
        guard_result: GuardResult,
    ) -> List[Dict[str, Any]]:
        """
        Wendet Guard-Ergebnis auf die Message-Liste an.

        Wenn system_hint gesetzt: System-Nachricht am Anfang einfügen.
        """
        if not messages or not guard_result.system_hint:
            return messages

        system_msg = {"role": "system", "content": guard_result.system_hint}
        return [system_msg] + messages


_chat_guard_service: ChatGuardService | None = None


def get_chat_guard_service() -> ChatGuardService:
    """Liefert den globalen ChatGuardService."""
    global _chat_guard_service
    if _chat_guard_service is None:
        _chat_guard_service = ChatGuardService()
    return _chat_guard_service


def set_chat_guard_service(service: ChatGuardService | None) -> None:
    """Setzt den ChatGuardService (für Tests)."""
    global _chat_guard_service
    _chat_guard_service = service
