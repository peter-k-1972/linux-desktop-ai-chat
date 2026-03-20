"""
Retry-Policy für die LLM-Output-Pipeline.

Steuert wann und wie Retries ausgeführt werden:
- Retry ohne Thinking
- Konfigurierbar, keine Endlosschleifen
- Vorbereitet für Fallback-Modell / alternative Rolle
"""

from dataclasses import dataclass
from typing import Optional

from app.core.llm.llm_response_result import ResponseStatus


@dataclass
class RetryPolicy:
    """
    Konfiguration und Logik für Retries.

    - retry_without_thinking: Bei thinking_only automatisch Retry mit think=False
    - max_retries: Maximale Anzahl Retries (verhindert Endlosschleifen)
    - fallback_model: Optionales Fallback-Modell (vorbereitet)
    - fallback_role: Optionale alternative System-Rolle (vorbereitet)
    """

    retry_without_thinking: bool = True
    max_retries: int = 1
    fallback_model: Optional[str] = None
    fallback_role: Optional[str] = None

    def should_retry_without_thinking(
        self,
        status: ResponseStatus,
        retry_count: int,
    ) -> bool:
        """
        Prüft, ob ein Retry ohne Thinking sinnvoll ist.

        Nur bei thinking_only und wenn max_retries nicht überschritten.
        """
        if not self.retry_without_thinking:
            return False
        if status != ResponseStatus.THINKING_ONLY:
            return False
        return retry_count < self.max_retries

    def should_use_fallback(
        self,
        status: ResponseStatus,
        retry_count: int,
    ) -> bool:
        """
        Prüft, ob Fallback-Modell verwendet werden soll.

        Vorbereitet für spätere Erweiterung.
        """
        if not self.fallback_model:
            return False
        if status not in (ResponseStatus.THINKING_ONLY, ResponseStatus.EMPTY, ResponseStatus.FAILED):
            return False
        return retry_count >= self.max_retries
