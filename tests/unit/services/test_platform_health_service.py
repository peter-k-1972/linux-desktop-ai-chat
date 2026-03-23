"""R2: Platform Health Service."""

from unittest.mock import patch

from app.services.infrastructure_snapshot import DataStoreSnapshotRow
from app.services.platform_health_service import build_platform_health_summary


def test_platform_health_overall_worst_wins():
    rows = [
        DataStoreSnapshotRow("Chat / App-DB", "SQLite", "/x", "OK"),
        DataStoreSnapshotRow("RAG", "Chroma", "/y", "Kein Index"),
    ]
    with patch("app.services.platform_health_service.build_data_store_rows", return_value=rows):
        with patch("app.services.platform_health_service.probe_ollama_localhost", return_value=(True, "http://127.0.0.1:11434")):
            with patch("app.services.platform_health_service.build_tool_snapshot_rows", return_value=[]):
                s = build_platform_health_summary()
    assert s.overall == "warning"
    assert any(c.severity == "warning" for c in s.checks)
    assert any(c.severity == "ok" for c in s.checks)
    assert s.checked_at


def test_platform_health_ollama_down_is_error():
    rows = [
        DataStoreSnapshotRow("Chat / App-DB", "SQLite", "/x", "OK"),
    ]
    with patch("app.services.platform_health_service.build_data_store_rows", return_value=rows):
        with patch("app.services.platform_health_service.probe_ollama_localhost", return_value=(False, "connection refused")):
            with patch("app.services.platform_health_service.build_tool_snapshot_rows", return_value=[]):
                s = build_platform_health_summary()
    assert s.overall == "error"
    assert any(c.check_id == "provider:ollama_local" and c.severity == "error" for c in s.checks)


def test_platform_health_db_missing_is_error():
    rows = [
        DataStoreSnapshotRow("Chat / App-DB", "SQLite", "/nope", "Keine Datei"),
    ]
    with patch("app.services.platform_health_service.build_data_store_rows", return_value=rows):
        with patch("app.services.platform_health_service.probe_ollama_localhost", return_value=(True, "http://127.0.0.1:11434")):
            with patch("app.services.platform_health_service.build_tool_snapshot_rows", return_value=[]):
                s = build_platform_health_summary()
    assert s.overall == "error"


def test_platform_health_tool_snapshot_failure_adds_warning():
    rows = [
        DataStoreSnapshotRow("Chat / App-DB", "SQLite", "/x", "OK"),
    ]
    with patch("app.services.platform_health_service.build_data_store_rows", return_value=rows):
        with patch("app.services.platform_health_service.probe_ollama_localhost", return_value=(True, "http://127.0.0.1:11434")):
            with patch(
                "app.services.platform_health_service.build_tool_snapshot_rows",
                side_effect=RuntimeError("boom"),
            ):
                s = build_platform_health_summary()
    assert any(c.check_id == "tool:snapshot" for c in s.checks)
    assert s.overall in ("warning", "error")
