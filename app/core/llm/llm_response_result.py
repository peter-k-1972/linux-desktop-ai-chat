"""
Strukturiertes Ergebnisobjekt für die LLM-Output-Pipeline.

Liefert nicht nur String rein/String raus, sondern ein vollständiges
Status-/Ergebnismodell für robuste Verarbeitung und UI-Feedback.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ResponseStatus(str, Enum):
    """Status der Pipeline-Verarbeitung."""

    SUCCESS = "success"
    """Antwort erfolgreich verarbeitet."""

    THINKING_ONLY = "thinking_only"
    """Nur Thinking-Daten, kein finaler Antworttext."""

    EMPTY = "empty"
    """Leere oder unbrauchbare Antwort."""

    CLEANED_HTML = "cleaned_html"
    """HTML wurde bereinigt (zusätzlich zu success)."""

    RETRY_USED = "retry_used"
    """Retry wurde ausgeführt."""

    FALLBACK_USED = "fallback_used"
    """Fallback-Modell wurde verwendet."""

    FAILED = "failed"
    """Verarbeitung fehlgeschlagen."""


@dataclass
class ResponseResult:
    """
    Strukturiertes Ergebnis der LLM-Output-Pipeline.

    Enthält Roh- und bereinigten Text, Metadaten und optional
    Hinweise für Retry/Fallback.
    """

    raw_text: str
    """Ursprünglicher Rohtext."""

    cleaned_text: str
    """Bereinigter, normalisierter Text für die UI."""

    status: ResponseStatus
    """Hauptstatus der Verarbeitung."""

    had_html: bool = False
    """Enthielt die Antwort HTML-artige Tags."""

    had_thinking: bool = False
    """Enthielt die Antwort Thinking-Daten."""

    had_final_text: bool = False
    """War finaler Antworttext (nicht nur Thinking) vorhanden."""

    retry_used: bool = False
    """Wurde ein Retry durchgeführt."""

    fallback_used: bool = False
    """Wurde ein Fallback-Modell verwendet."""

    error_message: Optional[str] = None
    """Fehlermeldung bei failed oder für UI-Feedback."""

    should_retry_without_thinking: bool = False
    """Pipeline empfiehlt Retry ohne Thinking."""

    def is_success(self) -> bool:
        """Liefert True, wenn die Antwort brauchbar ist."""
        return self.status in (
            ResponseStatus.SUCCESS,
            ResponseStatus.CLEANED_HTML,
            ResponseStatus.RETRY_USED,
            ResponseStatus.FALLBACK_USED,
        )

    def display_text(self) -> str:
        """
        Text für die UI-Anzeige.
        Bei Fehlern: verständliche Meldung statt Rohfehler.
        """
        if self.error_message and not self.is_success():
            return self.error_message
        return self.cleaned_text
