from app.gui.legacy import (
    is_placeholder_or_invalid_assistant_message,
    finalize_stream_response,
)


def test_placeholder_detection():
    assert is_placeholder_or_invalid_assistant_message("")
    assert is_placeholder_or_invalid_assistant_message("...")
    assert is_placeholder_or_invalid_assistant_message("(Kein Inhalt von Ollama erhalten)")
    assert is_placeholder_or_invalid_assistant_message(
        "(Ollama hat keinen finalen Antworttext geliefert)"
    )
    assert not is_placeholder_or_invalid_assistant_message("Echte Antwort")


def test_finalize_response_content_only():
    # Nur normaler Content -> wird direkt übernommen
    result = finalize_stream_response("Hallo Welt", [], False)
    assert result == "Hallo Welt"


def test_finalize_response_thinking_only():
    # Nur Thinking-Chunks, kein Content
    result = finalize_stream_response("", ["denke...", "überlege..."], True)
    assert "Thinking-Daten" in result


def test_finalize_response_content_and_thinking():
    # Content gewinnt, selbst wenn Thinking vorhanden ist
    result = finalize_stream_response("Antwort", ["denk"], True)
    assert result == "Antwort"


def test_finalize_response_done_without_content():
    # done=True ohne Content, aber mit empfangenen Chunks
    result = finalize_stream_response("", [], True)
    assert "(Kein Inhalt von Ollama erhalten)" == result


def test_finalize_response_no_stream():
    # Weder Content noch Thinking, kein Chunk empfangen
    result = finalize_stream_response("", [], False)
    assert "(Ollama hat keinen Stream zurückgeliefert)" == result

