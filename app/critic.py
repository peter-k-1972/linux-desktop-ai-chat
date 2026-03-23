"""
Chat-weiter „Critic / Review“-Pfad (app.critic) – **nicht** der Agent ``CriticAgent``.

Dieses Modul ist **nicht** in die Chat-Oberfläche oder Settings eingebunden. Es existiert
als interne API für künftige oder testgestützte Experimente. Produktive Agenten-Reviews
laufen über ``app.agents.critic.CriticAgent`` (z. B. ResearchAgent), nicht über
``review_response`` hier.

``review_response(..., enabled=True, ...)`` führt **keinen** zweiten LLM-Lauf aus und
gibt die Primärantwort unverändert zurück; es wird nur geloggt, damit kein stiller
Schein-Erfolg entsteht.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from app.core.models.roles import ModelRole


@dataclass
class CriticConfig:
    """Konfiguration für den (derzeit nicht produktiv genutzten) Critic-Pfad."""

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
    Bei ``enabled=False``: Primärantwort unverändert.

    Bei ``enabled=True``: Kein Review-Lauf (Modul nicht produktiv angebunden);
    Warnlog + unveränderte Primärantwort. ``chat_fn`` wird nicht aufgerufen.
    """
    if not config.enabled:
        return response
    logger.warning(
        "app.critic.review_response: enabled=True, aber dieser Pfad ist keine "
        "aktive Produktfunktion (kein zweiter LLM-Lauf); Primärantwort unverändert."
    )
    return response
