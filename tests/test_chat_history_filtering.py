import asyncio
from typing import Any, Dict, List

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class RecordingOllamaClient:
    """
    Fake-Client, der nur die übergebenen Messages aufzeichnet und
    einen minimalen Stream zurückliefert.
    """

    def __init__(self):
        self.last_messages: List[Dict[str, Any]] | None = None

    async def get_models(self):
        return []

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
    ):
        self.last_messages = list(messages)

        async def _gen():
            # Ein leerer, sofort beendeter Stream
            yield {"message": {"content": "", "thinking": ""}, "done": True}

        return _gen()


class HistoryDB:
    """
    In-Memory-DB, die gezielt kaputte/Placeholder-Einträge für History-Tests liefert.
    """

    def __init__(self, rows):
        # rows: List[(role, content, timestamp)]
        self._rows = rows

    def load_chat(self, chat_id):
        return list(self._rows)

    def save_message(self, chat_id, role, content):
        # Für diese Tests nicht relevant; wir wollen nur die Eingabeseite prüfen
        self._rows.append((role, content, "ts"))

    def list_workspace_roots_for_chat(self, chat_id: int):
        return []

    def create_chat(self, title: str = "Testchat") -> int:
        return 1


class HistoryChatWidget(ChatWidget):
    """
    Verhindert echte UI-Operationen; wir interessieren uns nur für den Prompt-Aufbau.
    """

    def __init__(self, client, settings, db):
        super().__init__(client, settings, db)

    def load_models(self):
        """No-op: verhindert asyncio.create_task ohne Event-Loop."""
        pass

    def on_update_chat(self, text, is_final):
        # UI Tests sind hier nicht relevant
        pass


@pytest.fixture
def settings():
    s = AppSettings()
    s.model = "gpt-oss:latest"
    s.temperature = 0.3
    s.max_tokens = 64
    return s


@pytest.mark.asyncio
async def test_placeholder_and_error_texts_filtered_from_history(settings):
    """
    Platzhalter-/Fehltexte wie '...', '(Kein Inhalt ...)', '(Ollama hat keinen finalen Antworttext geliefert)'
    werden beim Aufbau der Nachrichtenhistorie NICHT an Ollama gesendet.
    """
    history_rows = [
        ("user", "Hallo", "ts"),
        ("assistant", "...", "ts"),
        ("assistant", "(Kein Inhalt von Ollama erhalten)", "ts"),
        ("assistant", "(Ollama hat keinen finalen Antworttext geliefert)", "ts"),
        ("assistant", "Echte frühere Antwort", "ts"),
    ]
    db = HistoryDB(history_rows)
    client = RecordingOllamaClient()

    widget = HistoryChatWidget(client, settings, db)
    widget.chat_id = 1

    await widget.run_chat("Neue Frage")

    assert client.last_messages is not None
    # Alle Assistant-Nachrichten in den an Ollama gesendeten Messages
    assistant_contents = [
        m["content"] for m in client.last_messages if m["role"] == "assistant"
    ]

    # Platzhalter/Fehltexte dürfen nicht enthalten sein
    assert "..." not in assistant_contents
    assert "(Kein Inhalt von Ollama erhalten)" not in assistant_contents
    assert "(Ollama hat keinen finalen Antworttext geliefert)" not in assistant_contents

    # Die sinnvolle frühere Antwort muss enthalten sein
    assert "Echte frühere Antwort" in assistant_contents


@pytest.mark.asyncio
async def test_empty_or_none_like_history_entries_are_ignored(settings):
    """
    Leere, None-artige oder kaputte Inhalte in der DB-Historie
    dürfen nicht als Messages an Ollama weitergereicht werden.
    """
    history_rows = [
        ("user", "Frage 1", "ts"),
        ("assistant", "", "ts"),
        ("assistant", None, "ts"),  # type: ignore[arg-type]
        ("assistant", "  ", "ts"),
        ("assistant", "Valider Inhalt", "ts"),
    ]
    db = HistoryDB(history_rows)
    client = RecordingOllamaClient()

    widget = HistoryChatWidget(client, settings, db)

    widget.chat_id = 1
    await widget.run_chat("Frage 2")

    assert client.last_messages is not None

    contents = [m.get("content") for m in client.last_messages]
    # Keine exakt leeren oder nur aus Spaces bestehenden Nachrichten weitergeben
    assert "" not in contents
    assert "  " not in contents

    # Valider Inhalt und aktuelle Frage müssen enthalten sein
    assert any(c == "Valider Inhalt" for c in contents)
    assert any(c == "Frage 2" for c in contents)

