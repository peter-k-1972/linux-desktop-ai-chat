"""
Simulation: NDJSON-Stream (gesplittete Bytes) → Parser → gleiche Aggregation wie ChatWorkspace.

Kein Live-Ollama; validiert Parser + Append-Kette deterministisch.
"""

import json

import pytest

from app.gui.domains.operations.chat.chat_workspace import _extract_content
from app.providers.ollama_client import iter_ndjson_dicts


class _ChunkStream:
    def __init__(self, chunks: list[bytes]):
        self._chunks = list(chunks)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._chunks:
            raise StopAsyncIteration
        return self._chunks.pop(0)


def _split_bytes_every_n(blob: bytes, n: int) -> list[bytes]:
    return [blob[i : i + n] for i in range(0, len(blob), n)]


def _aggregate_like_chat_ui(chunks: list[dict]) -> str:
    """Entspricht ChatWorkspace._run_send (nur content-Append, kein error-break hier)."""
    full = ""
    for chunk in chunks:
        content, _, error, _done = _extract_content(chunk)
        if error:
            return full  # wie break nach Fehlerchunk
        if content:
            full += content
    return full


async def _collect_dicts(blob: bytes, chunk_size: int) -> list[dict]:
    parts = _split_bytes_every_n(blob, chunk_size)
    stream = _ChunkStream(parts)
    return [x async for x in iter_ndjson_dicts(stream)]


@pytest.mark.asyncio
async def test_long_stream_many_tokens_tiny_chunks():
    """Viele Ollama-Zeilenevents, Bytes in 1-Byte-Schritten → volle Aggregation."""
    pieces = [f"Wort{i} " for i in range(40)]
    lines = []
    for i, p in enumerate(pieces):
        done = i == len(pieces) - 1
        lines.append(
            {"message": {"content": p, "thinking": ""}, "done": done},
        )
    ndjson = "".join(json.dumps(row) + "\n" for row in lines).encode("utf-8")
    collected = await _collect_dicts(ndjson, chunk_size=1)
    assert len(collected) == len(lines)
    merged = _aggregate_like_chat_ui(collected)
    assert merged == "".join(pieces)


@pytest.mark.asyncio
async def test_paragraphs_and_code_preserved_in_content():
    """Leerzeilen, Codeblock — alles im JSON-String; ein Event stark fragmentiert."""
    inner = "Einleitung\n\nZweiter Absatz.\n\n```python\nx = 1\n```\n\n- a\n- b"
    row = {"message": {"content": inner, "thinking": ""}, "done": True}
    ndjson = (json.dumps(row) + "\n").encode("utf-8")
    collected = await _collect_dicts(ndjson, chunk_size=7)
    assert len(collected) == 1
    assert _aggregate_like_chat_ui(collected) == inner


@pytest.mark.asyncio
async def test_final_chunk_done_true_includes_trailing_content():
    """Letztes Event: content + done (wie Ollama)."""
    rows = [
        {"message": {"content": "vor ", "thinking": ""}, "done": False},
        {"message": {"content": "ende", "thinking": ""}, "done": True},
    ]
    ndjson = "".join(json.dumps(r) + "\n" for r in rows).encode("utf-8")
    collected = await _collect_dicts(ndjson, chunk_size=5)
    merged = _aggregate_like_chat_ui(collected)
    assert merged == "vor ende"
    assert collected[-1].get("done") is True


@pytest.mark.asyncio
async def test_malformed_line_skipped_valid_lines_preserved():
    """Kaputte NDJSON-Zeile wird übersprungen; Folgezeilen zählen."""
    good1 = {"message": {"content": "ok1", "thinking": ""}, "done": False}
    good2 = {"message": {"content": "ok2", "thinking": ""}, "done": True}
    ndjson = (
        json.dumps(good1) + "\n"
        + "this is not json {{{\n"
        + json.dumps(good2) + "\n"
    ).encode("utf-8")
    collected = await _collect_dicts(ndjson, chunk_size=3)
    assert len(collected) == 2
    assert _aggregate_like_chat_ui(collected) == "ok1ok2"


@pytest.mark.asyncio
async def test_empty_ndjson_lines_between_records():
    """Doppelte Newlines / leere Zeilen stören nicht."""
    r = {"message": {"content": "x", "thinking": ""}, "done": True}
    ndjson = ("\n\n" + json.dumps(r) + "\n\n").encode("utf-8")
    collected = await _collect_dicts(ndjson, chunk_size=2)
    assert len(collected) == 1
    assert _aggregate_like_chat_ui(collected) == "x"


@pytest.mark.asyncio
async def test_utf8_multibyte_split_across_tcp_chunks():
    """Umlaut in einer Zeile, Bytes mitten im Zeichen geteilt."""
    inner = "Straße und Größe"
    row = {"message": {"content": inner, "thinking": ""}, "done": True}
    ndjson = (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")
    # Split so dass mindestens ein Chunk mitten im UTF-8-Sequenz endet
    collected = await _collect_dicts(ndjson, chunk_size=1)
    assert _aggregate_like_chat_ui(collected) == inner
