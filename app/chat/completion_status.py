"""
Completion-Status-Modell für Chat-Antworten.

Kleines, klares Modell zur Kennzeichnung der Vollständigkeit einer Antwort.
Wird auf Nachrichten- bzw. Response-Ebene verwendet.
"""

from enum import Enum
from typing import Optional


class CompletionStatus(str, Enum):
    """
    Status der Antwortvollständigkeit.

    - complete: Regulär beendet, keine Anzeichen für Abbruch
    - possibly_truncated: Heuristisch oder Provider-Hinweis auf Trunkierung
    - interrupted: Abbruch (CancelledError, Exception, Stream abgebrochen)
    - error: Provider-Fehler oder Exception mit Fehlermeldung
    """

    COMPLETE = "complete"
    POSSIBLY_TRUNCATED = "possibly_truncated"
    INTERRUPTED = "interrupted"
    ERROR = "error"


def completion_status_to_db(status: Optional[CompletionStatus]) -> Optional[str]:
    """Konvertiert Status für DB-Persistenz. None → None."""
    if status is None:
        return None
    return status.value


def completion_status_from_db(value: Optional[str]) -> Optional[CompletionStatus]:
    """Liest Status aus DB. Ungültige Werte → None (behandelt als complete)."""
    if value is None or value == "":
        return None
    try:
        return CompletionStatus(value)
    except ValueError:
        return None


def is_incomplete(status: Optional[CompletionStatus]) -> bool:
    """True wenn Antwort als unvollständig/fehlerhaft gilt."""
    if status is None:
        return False
    return status in (
        CompletionStatus.POSSIBLY_TRUNCATED,
        CompletionStatus.INTERRUPTED,
        CompletionStatus.ERROR,
    )


def status_display_label(status: Optional[CompletionStatus]) -> Optional[str]:
    """Anzeige-Label für UI. None/complete → None (kein Badge)."""
    if status is None or status == CompletionStatus.COMPLETE:
        return None
    labels = {
        CompletionStatus.POSSIBLY_TRUNCATED: "möglicherweise unvollständig",
        CompletionStatus.INTERRUPTED: "Antwort unterbrochen",
        CompletionStatus.ERROR: "Generierung beendet mit Fehler",
    }
    return labels.get(status)


# Recovery-Vorbereitung: Struktur so, dass später möglich wäre:
# - "Antwort fortsetzen" (continue_from_message_id)
# - "Erneut generieren" (regenerate_message_id)
# - "Letzte Antwort vervollständigen"
# Aktuell kein Callback/Action-Hook – nur Status-Modell vorhanden.
