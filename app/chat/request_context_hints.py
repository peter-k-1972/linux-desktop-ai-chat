"""
Chat-Request – explizite Kontext-Hints.

Nur vom Aufrufer gesetzt. Keine automatische Klassifikation, kein NLP, kein LLM-Routing.
"""

from enum import Enum


class RequestContextHint(str, Enum):
    """Expliziter Hint für Kontextprofil-Wahl. Beeinflusst nur Profil, nicht Texte."""

    GENERAL_QUESTION = "general_question"
    ARCHITECTURE_WORK = "architecture_work"
    TOPIC_FOCUS = "topic_focus"
    LOW_CONTEXT_QUERY = "low_context_query"
