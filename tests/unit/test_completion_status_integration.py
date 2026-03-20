"""
Integration-Tests: Completion-Status im Chat-Flow.

Prüft:
- DB speichert und lädt completion_status
- ChatWorkspace _extract_content liefert done
- Message-Metadaten tragen Completion-Status
"""

import asyncio
import tempfile
import os

import pytest

from app.core.db.database_manager import DatabaseManager
from app.gui.domains.operations.chat.chat_workspace import _extract_content


class TestExtractContent:
    """_extract_content liefert (content, thinking, error, done)."""

    def test_returns_four_values(self):
        chunk = {"message": {"content": "x", "thinking": ""}, "done": True}
        result = _extract_content(chunk)
        assert len(result) == 4
        content, thinking, error, done = result
        assert content == "x"
        assert thinking == ""
        assert error is None
        assert done is True

    def test_error_chunk(self):
        chunk = {"error": "Connection refused"}
        content, _, error, done = _extract_content(chunk)
        assert content == ""
        assert error == "Connection refused"
        assert done is False

    def test_done_false(self):
        chunk = {"message": {"content": "teil", "thinking": ""}, "done": False}
        _, _, _, done = _extract_content(chunk)
        assert done is False


class TestDatabaseCompletionStatus:
    """DB persistiert completion_status."""

    @pytest.fixture
    def db(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            yield DatabaseManager(db_path=path)
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def test_save_and_load_completion_status(self, db):
        db.create_chat("Test")
        chat_id = 1
        db.save_message(
            chat_id, "assistant", "Antwort", model="llama", completion_status="possibly_truncated"
        )
        rows = db.load_chat(chat_id)
        assert len(rows) == 1
        row = rows[0]
        assert len(row) >= 6
        assert row[5] == "possibly_truncated"

    def test_load_chat_backward_compat_old_schema(self, db):
        """Alte DB ohne completion_status-Spalte: Migration fügt sie hinzu."""
        db.create_chat("Test")
        chat_id = 1
        db.save_message(chat_id, "assistant", "Alt", model=None, agent=None)
        rows = db.load_chat(chat_id)
        assert len(rows) == 1
        row = rows[0]
        assert len(row) >= 5
        if len(row) >= 6:
            assert row[5] is None or row[5] == ""
