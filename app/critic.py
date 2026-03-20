"""
Critic / Review Mode – Vorbereitung für zukünftige Erweiterung.

Ziel: DEFAULT/THINK erzeugt Antwort -> THINK/OVERKILL überprüft -> verbesserte Antwort.

Aktuell: Nur Struktur, noch nicht aktiv.
"""

from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.core.models.roles import ModelRole


@dataclass
class CriticConfig:
    """Konfiguration für den Critic-Modus."""

    enabled: bool = False
    primary_role: ModelRole = ModelRole.DEFAULT
    critic_role: ModelRole = ModelRole.THINK
    prompt_template: str = (
        "Überprüfe die folgende Antwort auf Korrektheit, Vollständigkeit und Klarheit. "
        "Gib eine verbesserte Version zurück, falls nötig:\n\n{response}"
    )


async def review_response(
    response: str,
    config: CriticConfig,
    chat_fn,  # Callable die chat() ausführt
) -> str:
    """
    Platzhalter für zukünftige Critic-Logik.

    Später: Antwort an critic_role senden, verbesserte Version zurückgeben.
    """
    if not config.enabled:
        return response
    # TODO: Implementierung wenn aktiviert
    return response
