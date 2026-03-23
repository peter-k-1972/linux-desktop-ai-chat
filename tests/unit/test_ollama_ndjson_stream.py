"""NDJSON-Streaming: Byte-Chunks dürfen Zeilen splitten (Ollama/aiohttp)."""

import json

import pytest

from app.providers.ollama_client import iter_ndjson_dicts


class _ChunkStream:
    """Minimal async-iterable of bytes (wie aiohttp StreamReader-Iteration)."""

    def __init__(self, chunks: list[bytes]):
        self._chunks = list(chunks)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._chunks:
            raise StopAsyncIteration
        return self._chunks.pop(0)


@pytest.mark.asyncio
async def test_ndjson_split_mid_line_yields_two_dicts():
    a = {"message": {"content": "Hel", "thinking": ""}, "done": False}
    b = {"message": {"content": "lo", "thinking": ""}, "done": True}
    line = (json.dumps(a) + "\n" + json.dumps(b) + "\n").encode("utf-8")
    mid = len(line) // 2
    stream = _ChunkStream([line[:mid], line[mid:]])

    out = [x async for x in iter_ndjson_dicts(stream)]

    assert len(out) == 2
    assert out[0]["message"]["content"] == "Hel"
    assert out[1]["message"]["content"] == "lo"
    assert out[1]["done"] is True


@pytest.mark.asyncio
async def test_ndjson_two_lines_one_chunk():
    a = {"x": 1}
    b = {"x": 2}
    blob = (json.dumps(a) + "\n" + json.dumps(b) + "\n").encode("utf-8")
    stream = _ChunkStream([blob])

    out = [x async for x in iter_ndjson_dicts(stream)]
    assert out == [a, b]


@pytest.mark.asyncio
async def test_ndjson_trailing_line_without_newline():
    d = {"message": {"content": "last", "thinking": ""}, "done": True}
    stream = _ChunkStream([json.dumps(d).encode("utf-8")])

    out = [x async for x in iter_ndjson_dicts(stream)]
    assert len(out) == 1
    assert out[0]["message"]["content"] == "last"
