"""Smoke: DocSearchService meldet fehlenden Index ohne Crash."""

from pathlib import Path

from app.services.doc_search_service import DocSearchService


async def test_doc_search_empty_chroma_returns_empty_hits(tmp_path):
    """Ohne gültigen Chroma-Ordner: leere Trefferliste, kein Exception."""
    svc = DocSearchService(chroma_path=tmp_path / "nonexistent_chroma")
    hits = await svc.search_docs("test query", context={"top_k": 3})
    assert hits == []


def test_doc_search_snippet_helper():
    from app.services import doc_search_service as m

    assert m._snippet("", 10) == ""
    assert m._snippet("a  b\nc", 20) == "a b c"
    long = "x" * 50
    s = m._snippet(long, 10)
    assert len(s) <= 11
    assert s.endswith("…")
