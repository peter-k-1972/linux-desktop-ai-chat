"""
Debug-Metadaten für Chat Guard v2.

Nicht als Log-Spam. Nutzbar für Debug, QA, Runtime/Inspector.
"""

from typing import Any, Dict

from app.core.chat_guard.intent_model import GuardResult


def guard_result_to_debug_dict(result: GuardResult) -> Dict[str, Any]:
    """
    Konvertiert GuardResult zu Debug-Metadaten.

    Für Runtime-Inspector, QA, Tracing.
    """
    d: Dict[str, Any] = {
        "intent": result.intent.value,
        "decision_source": result.decision_source,
        "risk_flags": result.risk_flags,
        "sanity_flags": result.sanity_flags,
    }
    if result.heuristic_intent is not None:
        d["heuristic_intent"] = result.heuristic_intent.value
    if result.ml_intent is not None:
        d["ml_intent"] = result.ml_intent.value
    if result.ml_confidence > 0:
        d["ml_confidence"] = round(result.ml_confidence, 3)
    if result.prompt_mode:
        d["prompt_mode"] = result.prompt_mode
    if result.routing_hint:
        d["routing_hint"] = result.routing_hint
    return d
