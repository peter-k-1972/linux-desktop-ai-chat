"""
Zentrale LLM-Output-Pipeline.

Verarbeitet Modellantworten robust:
- Thinking-/Final-Zustand erkennen
- HTML/Markup bereinigen
- Leere Antworten erkennen
- Retry-Empfehlung aussprechen
- Strukturiertes Ergebnis liefern
"""

from typing import List, Optional

from app.core.llm.llm_response_cleaner import ResponseCleaner
from app.core.llm.llm_response_result import ResponseResult, ResponseStatus
from app.core.llm.llm_retry_policy import RetryPolicy


# Verständliche Fehlermeldungen für die UI (kompatibel mit bestehenden Tests)
_MSG_THINKING_ONLY = (
    "Ollama hat nur Thinking-Daten geliefert, aber keinen finalen Antworttext. "
    "Versuchen Sie es erneut ohne Thinking-Modus oder mit einem anderen Modell."
)
_MSG_EMPTY = "(Kein Inhalt von Ollama erhalten)"
_MSG_NO_STREAM = "(Ollama hat keinen Stream zurückgeliefert)"
_MSG_FAILED = "Antwort konnte nicht verarbeitet werden."


class OutputPipeline:
    """
    Zentrale Verarbeitungsschicht für LLM-Antworten.

    Nimmt Rohantwort (content + thinking_chunks) entgegen, bereinigt,
    erkennt Fehler und liefert ein strukturiertes ResponseResult.
    """

    def __init__(
        self,
        cleaner: Optional[ResponseCleaner] = None,
        retry_policy: Optional[RetryPolicy] = None,
        strip_html: bool = True,
        preserve_markdown: bool = True,
        retry_without_thinking: bool = True,
        max_retries: int = 1,
    ):
        self._cleaner = cleaner or ResponseCleaner(
            strip_html=strip_html,
            preserve_markdown=preserve_markdown,
        )
        self._retry_policy = retry_policy or RetryPolicy(
            retry_without_thinking=retry_without_thinking,
            max_retries=max_retries,
        )

    def process(
        self,
        raw_content: str,
        thinking_chunks: Optional[List[str]] = None,
        done: bool = True,
        retry_count: int = 0,
        retry_used: bool = False,
        fallback_used: bool = False,
    ) -> ResponseResult:
        """
        Verarbeitet die Rohantwort und liefert ein strukturiertes Ergebnis.

        Args:
            raw_content: Roher Content-Text aus dem Stream
            thinking_chunks: Liste der empfangenen Thinking-Chunks
            done: Ob der Stream abgeschlossen ist
            retry_count: Anzahl bereits durchgeführter Retries
            retry_used: Ob ein Retry durchgeführt wurde
            fallback_used: Ob ein Fallback-Modell verwendet wurde

        Returns:
            ResponseResult mit cleaned_text, status, Metadaten
        """
        thinking_chunks = thinking_chunks or []
        raw = (raw_content or "").strip()
        had_thinking = len(thinking_chunks) > 0
        had_final_text = bool(raw)

        # 1. None / leerer String
        if raw_content is None:
            return ResponseResult(
                raw_text="",
                cleaned_text="",
                status=ResponseStatus.EMPTY,
                had_html=False,
                had_thinking=had_thinking,
                had_final_text=False,
                retry_used=retry_used,
                fallback_used=fallback_used,
                error_message=_MSG_EMPTY,
            )

        # 2. Stream nicht abgeschlossen, kein Content
        if not done and not raw and not had_thinking:
            return ResponseResult(
                raw_text="",
                cleaned_text="",
                status=ResponseStatus.EMPTY,
                had_html=False,
                had_thinking=False,
                had_final_text=False,
                retry_used=retry_used,
                fallback_used=fallback_used,
                error_message=_MSG_NO_STREAM,
            )

        # 3. Nur Thinking, kein finaler Text
        if done and had_thinking and not had_final_text:
            should_retry = self._retry_policy.should_retry_without_thinking(
                ResponseStatus.THINKING_ONLY,
                retry_count,
            )
            return ResponseResult(
                raw_text="",
                cleaned_text="",
                status=ResponseStatus.THINKING_ONLY,
                had_html=False,
                had_thinking=True,
                had_final_text=False,
                retry_used=retry_used,
                fallback_used=fallback_used,
                error_message=_MSG_THINKING_ONLY,
                should_retry_without_thinking=should_retry,
            )

        # 4. done, aber weder Content noch Thinking
        if done and not had_final_text and not had_thinking:
            return ResponseResult(
                raw_text="",
                cleaned_text="",
                status=ResponseStatus.EMPTY,
                had_html=False,
                had_thinking=False,
                had_final_text=False,
                retry_used=retry_used,
                fallback_used=fallback_used,
                error_message=_MSG_EMPTY,
            )

        # 5. Content vorhanden -> bereinigen
        cleaned, had_html = self._cleaner.clean(raw)

        # 6. Nach Bereinigung leer oder Schrott?
        if self._cleaner.is_empty_or_junk(cleaned):
            return ResponseResult(
                raw_text=raw,
                cleaned_text="",
                status=ResponseStatus.EMPTY,
                had_html=had_html,
                had_thinking=had_thinking,
                had_final_text=False,
                retry_used=retry_used,
                fallback_used=fallback_used,
                error_message=_MSG_EMPTY,
            )

        # 7. Erfolg
        status = ResponseStatus.CLEANED_HTML if had_html else ResponseStatus.SUCCESS
        if retry_used:
            status = ResponseStatus.RETRY_USED
        if fallback_used:
            status = ResponseStatus.FALLBACK_USED

        return ResponseResult(
            raw_text=raw,
            cleaned_text=cleaned,
            status=status,
            had_html=had_html,
            had_thinking=had_thinking,
            had_final_text=True,
            retry_used=retry_used,
            fallback_used=fallback_used,
        )
