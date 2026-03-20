"""
Intent- und Request-Modell für Chat Guard v1.

Klein, belastbar, nicht übermodelliert.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ChatIntent(str, Enum):
    """
    Heuristisch erkannter Intent der User-Anfrage.

    - chat: Normale Unterhaltung
    - command: Slash-/Command-Pfad (/think, /agent, etc.)
    - formal_reasoning: Beweis, Axiom, formale Herleitung, Definition
    - coding: Code, Technik, Debug, Refactor
    - knowledge_query: Wissensfrage, Attribution (Autor, Werk)
    - possibly_ambiguous: Mögliche Ambiguität / Mismatch-Risiko
    """

    CHAT = "chat"
    COMMAND = "command"
    FORMAL_REASONING = "formal_reasoning"
    CODING = "coding"
    KNOWLEDGE_QUERY = "knowledge_query"
    POSSIBLY_AMBIGUOUS = "possibly_ambiguous"


@dataclass
class GuardResult:
    """
    Ergebnis der Guard-Bewertung.

    v1-Felder:
    - intent: Primärer Intent (final)
    - risk_flags, sanity_flags
    - routing_hint, prompt_mode, system_hint, user_prefix

    v2-Hybrid-Felder (optional):
    - heuristic_intent: Heuristik-Ergebnis
    - ml_intent: ML-/Embedding-Ergebnis (wenn ML aktiv)
    - final_intent: Fusions-Ergebnis (= intent)
    - ml_confidence: 0.0–1.0, nur bei ML
    - decision_source: "heuristic" | "ml" | "fusion" | "fallback"
    """

    intent: ChatIntent = ChatIntent.CHAT
    risk_flags: List[str] = field(default_factory=list)
    sanity_flags: List[str] = field(default_factory=list)
    routing_hint: Optional[str] = None
    prompt_mode: Optional[str] = None
    system_hint: Optional[str] = None
    user_prefix: Optional[str] = None

    # v2 Hybrid
    heuristic_intent: Optional[ChatIntent] = None
    ml_intent: Optional[ChatIntent] = None
    ml_confidence: float = 0.0
    decision_source: str = "heuristic"
