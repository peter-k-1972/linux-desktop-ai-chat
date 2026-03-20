"""
Chat Guard v1/v2 – Heuristische und optionale ML-Bewertung vor Modellaufruf.

v1: Intent-Erkennung, Risk-Flags, Sanity-Check, Prompt-Härtung
v2: + optionale Embedding-basierte Intent-Erkennung, Fusion
"""

from app.core.chat_guard.intent_model import (
    ChatIntent,
    GuardResult,
)
from app.core.chat_guard.service import ChatGuardService

__all__ = [
    "ChatIntent",
    "GuardResult",
    "ChatGuardService",
]
