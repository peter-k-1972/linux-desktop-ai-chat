"""
Unit Tests: Completion-Heuristik und Status-Modell.

Prüft:
- vollständige Antwort wird nicht fälschlich markiert
- klar abgeschnittene Antwort wird markiert
- offener Codeblock wird erkannt
- Heuristik bleibt stabil und nachvollziehbar
"""

import pytest

from app.chat.completion_status import (
    CompletionStatus,
    completion_status_from_db,
    completion_status_to_db,
    is_incomplete,
    status_display_label,
)
from app.chat.completion_heuristics import (
    assess_completion_heuristic,
    get_heuristic_flags,
)


class TestCompletionStatus:
    def test_complete_not_incomplete(self):
        assert not is_incomplete(CompletionStatus.COMPLETE)
        assert not is_incomplete(None)

    def test_truncated_interrupted_error_incomplete(self):
        assert is_incomplete(CompletionStatus.POSSIBLY_TRUNCATED)
        assert is_incomplete(CompletionStatus.INTERRUPTED)
        assert is_incomplete(CompletionStatus.ERROR)

    def test_status_to_db(self):
        assert completion_status_to_db(CompletionStatus.COMPLETE) == "complete"
        assert completion_status_to_db(CompletionStatus.ERROR) == "error"
        assert completion_status_to_db(None) is None

    def test_status_from_db(self):
        assert completion_status_from_db("complete") == CompletionStatus.COMPLETE
        assert completion_status_from_db("possibly_truncated") == CompletionStatus.POSSIBLY_TRUNCATED
        assert completion_status_from_db("") is None
        assert completion_status_from_db(None) is None
        assert completion_status_from_db("invalid") is None

    def test_status_display_label(self):
        assert status_display_label(CompletionStatus.COMPLETE) is None
        assert status_display_label(None) is None
        assert status_display_label(CompletionStatus.POSSIBLY_TRUNCATED) == "möglicherweise unvollständig"
        assert status_display_label(CompletionStatus.INTERRUPTED) == "Antwort unterbrochen"
        assert status_display_label(CompletionStatus.ERROR) == "Generierung beendet mit Fehler"


class TestCompletionHeuristics:
    def test_complete_short_answer_not_marked(self):
        """Normale kurze Antwort wird nicht fälschlich markiert."""
        status = assess_completion_heuristic("Ja, das stimmt.")
        assert status == CompletionStatus.COMPLETE

    def test_complete_medium_answer_not_marked(self):
        """Mittellange vollständige Antwort bleibt complete."""
        status = assess_completion_heuristic(
            "Das ist eine vollständige Antwort mit mehreren Sätzen. "
            "Sie endet korrekt mit einem Punkt."
        )
        assert status == CompletionStatus.COMPLETE

    def test_error_chunk_returns_error(self):
        status = assess_completion_heuristic("irgendwas", had_error=True)
        assert status == CompletionStatus.ERROR

    def test_exception_returns_interrupted(self):
        status = assess_completion_heuristic("teilweise", had_exception=True)
        assert status == CompletionStatus.INTERRUPTED

    def test_provider_not_done_returns_interrupted(self):
        status = assess_completion_heuristic(
            "Vollständiger Text.",
            provider_finished_normally=False,
        )
        assert status == CompletionStatus.INTERRUPTED

    def test_open_code_block_marked_truncated(self):
        """Ungerade Anzahl ``` = offener Codeblock."""
        status = assess_completion_heuristic(
            "Hier ist der Code:\n```python\nprint('hello')\n"
        )
        assert status == CompletionStatus.POSSIBLY_TRUNCATED

    def test_closed_code_block_not_marked(self):
        status = assess_completion_heuristic(
            "Hier ist der Code:\n```python\nprint('hello')\n```\nFertig."
        )
        assert status == CompletionStatus.COMPLETE

    def test_ends_mid_word_marked(self):
        """Antwort endet mitten im Wort (>= 50 Zeichen)."""
        text = "Das ist eine längere Antwort die mitten im Wort abgebrochen erscheint weil sie mit einem unvollständigen Wo"
        assert len(text) >= 50
        status = assess_completion_heuristic(text)
        assert status == CompletionStatus.POSSIBLY_TRUNCATED

    def test_ends_with_sentence_not_marked(self):
        """Antwort mit Satzende nicht markieren."""
        text = "Das ist eine längere Antwort die korrekt mit einem Punkt endet."
        status = assess_completion_heuristic(text)
        assert status == CompletionStatus.COMPLETE

    def test_short_ends_mid_word_not_marked(self):
        """Kurze Antwort (OK, Ja) nicht markieren auch wenn mitten im Wort."""
        status = assess_completion_heuristic("O")
        assert status == CompletionStatus.COMPLETE

    def test_get_heuristic_flags(self):
        flags = get_heuristic_flags("```python\nx = 1\n")
        assert "open_code_block" in flags

        flags = get_heuristic_flags("Vollständiger Satz.")
        assert "open_code_block" not in flags
