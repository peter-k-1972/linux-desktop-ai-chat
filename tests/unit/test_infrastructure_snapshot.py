"""Tests für Control-Center-/Dashboard-Snapshots (ohne GUI)."""

import sqlite3
from pathlib import Path

import pytest

from app.services import infrastructure_snapshot as snap


def test_sqlite_probe_ok(tmp_path: Path) -> None:
    db = tmp_path / "t.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE x (a INT)")
    conn.commit()
    conn.close()
    state, detail = snap._sqlite_probe(str(db))
    assert state == "OK"
    assert str(db.resolve()) in detail or detail.startswith(str(db))


def test_sqlite_probe_missing(tmp_path: Path) -> None:
    state, detail = snap._sqlite_probe(str(tmp_path / "nope.db"))
    assert state == "Keine Datei"


def test_build_tool_snapshot_rows_no_crash() -> None:
    rows = snap.build_tool_snapshot_rows()
    assert len(rows) >= 3
    ids = {r.tool_id for r in rows}
    assert "filesystem_tools" in ids


def test_build_data_store_rows_no_crash() -> None:
    rows = snap.build_data_store_rows()
    assert len(rows) == 3
    assert any("SQLite" in r.store_type for r in rows)


def test_sqlite_probe_not_a_database(tmp_path: Path) -> None:
    """SQLite akzeptiert manchmal beliebige Dateien als leere DB — daher echtes Fehlerszenario: ungültiger URI."""
    state, detail = snap._sqlite_probe("file:no_such_dir_xyz/db.sqlite?mode=ro")
    assert state in ("Keine Datei", "Fehler")
    assert detail


def test_chroma_status_missing_base(tmp_path: Path) -> None:
    missing = tmp_path / "no_such_rag"
    st, det = snap._chroma_status_for_rag_base(missing)
    assert st == "Leer"
    assert "fehlt" in det.lower() or "fehlt" in det


def test_chroma_status_with_index_file(tmp_path: Path) -> None:
    """Wenn chromadb importierbar und chroma.sqlite3 existiert → OK-Pfad."""
    base = tmp_path / "rag_root"
    base.mkdir()
    (base / "chroma.sqlite3").write_bytes(b"")
    st, det = snap._chroma_status_for_rag_base(base)
    try:
        import chromadb  # noqa: F401
    except ImportError:
        assert st == "Modul fehlt"
    else:
        assert st == "OK"
        assert "Store" in det or "store" in det.lower()


def test_chroma_status_no_sqlite_under_base(tmp_path: Path) -> None:
    base = tmp_path / "empty_rag"
    base.mkdir()
    st, _ = snap._chroma_status_for_rag_base(base)
    try:
        import chromadb  # noqa: F401
    except ImportError:
        assert st == "Modul fehlt"
    else:
        assert st == "Kein Index"


def test_build_data_store_health_summary_colors() -> None:
    rows = [
        snap.DataStoreSnapshotRow("A", "T", "c", "OK"),
        snap.DataStoreSnapshotRow("B", "T", "c", "Fehler"),
        snap.DataStoreSnapshotRow("C", "T", "c", "Leer"),
    ]
    summary = snap.build_data_store_health_summary(rows)
    assert summary[0][2] == "#10b981"
    assert summary[1][2] == "#ef4444"
    assert summary[2][2] == "#64748b"


def test_probe_ollama_localhost_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _fake_urlopen(url, timeout=None):
        assert "/api/tags" in url
        return _Resp()

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)
    ok, hint = snap.probe_ollama_localhost("http://127.0.0.1:11434")
    assert ok is True
    assert "11434" in hint


def test_probe_ollama_localhost_connection_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.error

    def _boom(url, timeout=None):
        raise urllib.error.URLError("refused")

    monkeypatch.setattr("urllib.request.urlopen", _boom)
    ok, _ = snap.probe_ollama_localhost()
    assert ok is False


def test_tool_snapshot_includes_rag_row_reflecting_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """RAG-Zeile folgt settings.rag_enabled wenn Infrastruktur verfügbar."""

    class _S:
        rag_enabled = True
        web_search = False

    class _Db:
        db_path = "chat_history.db"

    class _Infra:
        settings = _S()
        database = _Db()

    monkeypatch.setattr(snap, "_try_get_infrastructure", lambda: _Infra())
    rows = snap.build_tool_snapshot_rows()
    rag = next(r for r in rows if r.tool_id == "rag_augmentation")
    assert "Aktiv" in rag.status
