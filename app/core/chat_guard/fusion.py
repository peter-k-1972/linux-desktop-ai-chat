"""
Entscheidungsfusion: Heuristik + ML → finaler Intent.

Klare Regeln, nachvollziehbar, keine Blackbox.
"""

from app.core.chat_guard.intent_model import ChatIntent, GuardResult

# Heuristik gilt als "stark" bei diesen Intents (eindeutige Signale)
_HEURISTIC_STRONG_INTENTS = {ChatIntent.COMMAND}

# Heuristik gilt als "schwach/unklar" bei chat (Default)
_HEURISTIC_WEAK_INTENTS = {ChatIntent.CHAT}

# ML Confidence-Schwelle: darunter ML ignorieren
ML_CONFIDENCE_THRESHOLD = 0.5

# Confidence für "stark": Heuristik-Command ist immer stark
HEURISTIC_STRONG_CONFIDENCE = 1.0


def fuse(
    heuristic_intent: ChatIntent,
    heuristic_risk_flags: list[str],
    ml_intent: ChatIntent | None,
    ml_confidence: float,
    ml_enabled: bool,
) -> tuple[ChatIntent, str]:
    """
    Führt Heuristik und ML zu finalem Intent zusammen.

    Returns:
        (final_intent, decision_source)
    """
    if not ml_enabled or ml_intent is None:
        return heuristic_intent, "heuristic"

    # 1. Heuristik stark (z.B. command) → Heuristik gewinnt
    if heuristic_intent in _HEURISTIC_STRONG_INTENTS:
        return heuristic_intent, "heuristic"

    # 2. ML niedrige Confidence → Heuristik
    if ml_confidence < ML_CONFIDENCE_THRESHOLD:
        return heuristic_intent, "fallback"

    # 3. Heuristik schwach (chat), ML hat hohe Confidence → ML kann helfen
    if heuristic_intent in _HEURISTIC_WEAK_INTENTS and ml_confidence >= ML_CONFIDENCE_THRESHOLD:
        return ml_intent, "ml"

    # 4. Widerspruch: Heuristik sagt X, ML sagt Y (beide nicht chat)
    if heuristic_intent != ml_intent and heuristic_intent != ChatIntent.CHAT:
        # Konservativ: Heuristik gewinnt, aber ambiguity flag könnte gesetzt werden
        return heuristic_intent, "fusion"

    # 5. Übereinstimmung
    if heuristic_intent == ml_intent:
        return heuristic_intent, "fusion"

    # 6. Heuristik chat, ML etwas anderes mit hoher Confidence
    if heuristic_intent == ChatIntent.CHAT:
        return ml_intent, "ml"

    return heuristic_intent, "fallback"


def apply_fusion_to_result(
    result: GuardResult,
    ml_intent: ChatIntent | None,
    ml_confidence: float,
    ml_enabled: bool,
) -> GuardResult:
    """
    Wendet Fusion auf GuardResult an.
    Setzt intent, heuristic_intent, ml_intent, ml_confidence, decision_source.
    """
    result.heuristic_intent = result.intent
    result.ml_intent = ml_intent
    result.ml_confidence = ml_confidence

    if not ml_enabled or ml_intent is None:
        result.decision_source = "heuristic"
        return result

    final_intent, source = fuse(
        result.intent,
        result.risk_flags,
        ml_intent,
        ml_confidence,
        ml_enabled,
    )
    result.intent = final_intent
    result.decision_source = source
    return result
