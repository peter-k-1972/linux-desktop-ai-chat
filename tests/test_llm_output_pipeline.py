"""
Tests für die LLM-Output-Pipeline.

Abdeckung:
- Plaintext-Antwort
- HTML-Antwort mit <br>, <h3>, <b>
- Antwort mit nur Thinking-Inhalt
- Antwort mit Thinking + Finaltext
- Leere Antwort
- Retry ohne Thinking
- Fallback (vorbereitet)
"""

import pytest

from app.core.llm.llm_output_pipeline import OutputPipeline
from app.core.llm.llm_response_cleaner import ResponseCleaner
from app.core.llm.llm_response_result import ResponseResult, ResponseStatus
from app.core.llm.llm_retry_policy import RetryPolicy


# --- ResponseCleaner ---


def test_cleaner_plaintext():
    """Normale Textantwort unverändert bzw. leicht bereinigt."""
    cleaner = ResponseCleaner(strip_html=True, preserve_markdown=True)
    text, had_html = cleaner.clean("Hallo Welt, das ist eine normale Antwort.")
    assert text == "Hallo Welt, das ist eine normale Antwort."
    assert had_html is False


def test_cleaner_html_br():
    """<br> in Zeilenumbrüche umwandeln."""
    cleaner = ResponseCleaner(strip_html=True, preserve_markdown=True)
    text, had_html = cleaner.clean("Zeile 1<br>Zeile 2<br/>Zeile 3")
    assert "Zeile 1" in text
    assert "Zeile 2" in text
    assert "Zeile 3" in text
    assert "<br" not in text
    assert had_html is True


def test_cleaner_html_headers():
    """<h3> etc. sinnvoll in Absätze umwandeln."""
    cleaner = ResponseCleaner(strip_html=True, preserve_markdown=True)
    text, had_html = cleaner.clean("<h3>Überschrift</h3>Inhalt darunter")
    assert "Überschrift" in text
    assert "Inhalt darunter" in text
    assert "<h3" not in text
    assert had_html is True


def test_cleaner_html_inline():
    """<b>, <i> etc. glätten."""
    cleaner = ResponseCleaner(strip_html=True, preserve_markdown=True)
    text, had_html = cleaner.clean("<b>fett</b> und <i>kursiv</i>")
    assert "fett" in text
    assert "kursiv" in text
    assert "<b" not in text
    assert "<i" not in text
    assert had_html is True


def test_cleaner_html_entities():
    """HTML-Entities dekodieren."""
    cleaner = ResponseCleaner(strip_html=True, preserve_markdown=True)
    text, _ = cleaner.clean("&amp; &lt; &gt; &quot;")
    assert "&" in text
    assert "<" in text
    assert ">" in text
    assert '"' in text


def test_cleaner_preserve_markdown():
    """Markdown und Codeblöcke erhalten."""
    cleaner = ResponseCleaner(strip_html=True, preserve_markdown=True)
    md = "```python\nprint('hello')\n```"
    text, _ = cleaner.clean(md)
    assert "```" in text
    assert "print" in text


def test_cleaner_is_empty_junk():
    """Leer-/Schrottantworten erkennen."""
    cleaner = ResponseCleaner(strip_html=True, preserve_markdown=True)
    assert cleaner.is_empty_or_junk("") is True
    assert cleaner.is_empty_or_junk("   ") is True
    assert cleaner.is_empty_or_junk("<div></div>") is True
    assert cleaner.is_empty_or_junk("Hallo") is False


# --- OutputPipeline ---


def test_pipeline_plaintext():
    """Plaintext-Antwort: success."""
    pipeline = OutputPipeline()
    result = pipeline.process("Hallo Welt", thinking_chunks=[], done=True)
    assert result.status == ResponseStatus.SUCCESS
    assert result.cleaned_text == "Hallo Welt"
    assert result.had_final_text is True
    assert result.is_success() is True


def test_pipeline_html_answer():
    """HTML-Antwort mit <br>, <h3>, <b> bereinigen."""
    pipeline = OutputPipeline()
    raw = "<h3>Titel</h3><br>Text mit <b>Fett</b>"
    result = pipeline.process(raw, thinking_chunks=[], done=True)
    assert result.is_success() is True
    assert result.had_html is True
    assert "Titel" in result.cleaned_text
    assert "Text" in result.cleaned_text
    assert "Fett" in result.cleaned_text
    assert "<h3" not in result.cleaned_text
    assert "<br" not in result.cleaned_text


def test_pipeline_thinking_only():
    """Nur Thinking-Chunks, kein Content: thinking_only."""
    pipeline = OutputPipeline()
    result = pipeline.process(
        "",
        thinking_chunks=["denke...", "überlege..."],
        done=True,
    )
    assert result.status == ResponseStatus.THINKING_ONLY
    assert result.had_thinking is True
    assert result.had_final_text is False
    assert result.is_success() is False
    assert "Thinking-Daten" in result.display_text()
    assert result.should_retry_without_thinking is True


def test_pipeline_thinking_and_content():
    """Thinking + Content: Content gewinnt."""
    pipeline = OutputPipeline()
    result = pipeline.process(
        "Die eigentliche Antwort",
        thinking_chunks=["denke..."],
        done=True,
    )
    assert result.status == ResponseStatus.SUCCESS
    assert result.cleaned_text == "Die eigentliche Antwort"
    assert result.had_thinking is True
    assert result.had_final_text is True


def test_pipeline_empty():
    """Leere Antwort: empty."""
    pipeline = OutputPipeline()
    result = pipeline.process("", thinking_chunks=[], done=True)
    assert result.status == ResponseStatus.EMPTY
    assert result.cleaned_text == ""
    assert result.is_success() is False


def test_pipeline_none():
    """None als Antwort."""
    pipeline = OutputPipeline()
    result = pipeline.process(None, thinking_chunks=[], done=True)
    assert result.status == ResponseStatus.EMPTY
    assert result.error_message is not None


def test_pipeline_retry_without_thinking():
    """Retry-Empfehlung bei thinking_only und retry_count < max."""
    policy = RetryPolicy(retry_without_thinking=True, max_retries=1)
    pipeline = OutputPipeline(retry_policy=policy)
    result = pipeline.process("", thinking_chunks=["x"], done=True, retry_count=0)
    assert result.should_retry_without_thinking is True


def test_pipeline_no_retry_when_max_reached():
    """Kein Retry wenn max_retries erreicht."""
    policy = RetryPolicy(retry_without_thinking=True, max_retries=1)
    pipeline = OutputPipeline(retry_policy=policy)
    result = pipeline.process("", thinking_chunks=["x"], done=True, retry_count=1)
    assert result.should_retry_without_thinking is False


def test_pipeline_retry_disabled():
    """Kein Retry wenn retry_without_thinking=False."""
    policy = RetryPolicy(retry_without_thinking=False, max_retries=1)
    pipeline = OutputPipeline(retry_policy=policy)
    result = pipeline.process("", thinking_chunks=["x"], done=True, retry_count=0)
    assert result.should_retry_without_thinking is False


def test_pipeline_retry_used_flag():
    """retry_used im Ergebnis."""
    pipeline = OutputPipeline()
    result = pipeline.process(
        "Antwort nach Retry",
        thinking_chunks=[],
        done=True,
        retry_used=True,
    )
    assert result.retry_used is True
    assert result.status == ResponseStatus.RETRY_USED


def test_pipeline_display_text_on_error():
    """display_text() liefert Fehlermeldung bei Fehlern."""
    pipeline = OutputPipeline()
    result = pipeline.process("", thinking_chunks=["x"], done=True)
    assert not result.is_success()
    assert result.display_text() == result.error_message
    assert "Thinking-Daten" in result.display_text()
