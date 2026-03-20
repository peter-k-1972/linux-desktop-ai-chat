import asyncio
from typing import Any, Dict, List

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class FakeOllamaClient:
    """
    Minimaler Fake für OllamaClient.chat, der vorbereitete Chunk-Sequenzen liefert.
    """

    def __init__(self, chunks: List[Dict[str, Any]]):
        self._chunks = chunks
        self.last_model = None
        self.last_messages = None

    async def get_models(self):
        # Verhindert Fehler in ChatWidget.load_models
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
        self.last_model = model
        self.last_messages = list(messages)
        self.last_stream = stream

        async def _gen():
            for chunk in self._chunks:
                await asyncio.sleep(0)  # Eventloop kurz freigeben
                yield chunk

        return _gen()


class FakeDB:
    """
    Einfacher In-Memory-Ersatz für DatabaseManager für Streaming-Tests.
    """

    def __init__(self):
        self._messages = {}  # chat_id -> List[(role, content, timestamp)]
        self._next_chat_id = 1

    def create_chat(self, title: str = "Testchat") -> int:
        chat_id = self._next_chat_id
        self._next_chat_id += 1
        self._messages[chat_id] = []
        return chat_id

    def save_message(self, chat_id, role, content):
        self._messages.setdefault(chat_id, []).append((role, content, "ts"))

    def load_chat(self, chat_id):
        return list(self._messages.get(chat_id, []))

    def list_workspace_roots_for_chat(self, chat_id: int):
        # Für Streaming-Tests nicht relevant -> keine Files
        return []


class CapturingChatWidget(ChatWidget):
    """
    Ableitung von ChatWidget, die UI-Updates nur sammelt statt real zu rendern.
    """

    def __init__(self, client, settings, db):
        super().__init__(client, settings, db)
        self.updates = []  # List[(text, is_final)]

    def load_models(self):
        """No-op: verhindert asyncio.create_task ohne Event-Loop."""
        pass

    def on_update_chat(self, text, is_final):
        # Überschreibt den Slot aus der Basisklasse
        self.updates.append((text, is_final))


@pytest.fixture
def settings():
    s = AppSettings()
    s.model = "gpt-oss:latest"
    s.temperature = 0.3
    s.max_tokens = 128
    return s


@pytest.mark.asyncio
async def test_stream_content_only(settings):
    """
    Mehrere Chunks nur mit message.content -> finaler Text wird zusammengesetzt,
    gespeichert und als finaler UI-Update gesendet.
    """
    chunks = [
        {"message": {"content": "Hallo", "thinking": ""}, "done": False},
        {"message": {"content": " Welt", "thinking": ""}, "done": False},
        {"message": {"content": "!", "thinking": ""}, "done": True},
    ]
    client = FakeOllamaClient(chunks)
    db = FakeDB()
    chat_id = db.create_chat("Testchat")

    widget = CapturingChatWidget(client, settings, db)
    widget.chat_id = chat_id

    # Benutzer-Nachricht in die "DB" legen, wie es on_send tun würde
    db.save_message(chat_id, "user", "Sag Hallo")

    await widget.run_chat("Sag Hallo")

    # Finale Antwort
    assert widget.current_full_response == "Hallo Welt!"

    # In DB gespeichert
    history = db.load_chat(chat_id)
    assistant_messages = [m for m in history if m[0] == "assistant"]
    assert assistant_messages
    assert assistant_messages[-1][1] == "Hallo Welt!"

    # UI-Updates: letzter Eintrag muss final sein und den zusammengesetzten Text enthalten
    assert widget.updates
    last_text, is_final = widget.updates[-1]
    assert is_final is True
    assert "Hallo Welt!" in last_text


@pytest.mark.asyncio
async def test_stream_thinking_only_no_persist_and_no_tools(settings):
    """
    Nur message.thinking, nie message.content:
    - es entsteht ein technischer Hinweis/Fallback,
    - dieser wird NICHT als normale Assistant-Nachricht gespeichert,
    - Tool-Calls werden NICHT ausgeführt.
    """
    chunks = [
        {"message": {"thinking": "ich überlege...", "content": ""}, "done": False},
        {"message": {"thinking": "weiter überlegen...", "content": ""}, "done": True},
    ]

    client = FakeOllamaClient(chunks)
    db = FakeDB()
    chat_id = db.create_chat("Testchat")

    widget = CapturingChatWidget(client, settings, db)
    widget.chat_id = chat_id

    # Dummy-Tools, die protokollieren, ob sie benutzt wurden
    class DummyTools:
        def __init__(self):
            self.used = False

        def list_dir(self, *_args, **_kwargs):
            self.used = True
            return "OK"

    dummy_tools = DummyTools()
    widget.tools = dummy_tools

    db.save_message(chat_id, "user", "Denke nach")

    await widget.run_chat("Denke nach")

    # Fallback-Text
    assert "Thinking-Daten" in widget.current_full_response

    # Fallback wird NICHT als Assistant-Antwort gespeichert
    history = db.load_chat(chat_id)
    assistant_messages = [m for m in history if m[0] == "assistant"]
    assert not assistant_messages

    # Keine Tool-Ausführung trotz ggf. Tool-Tags im Text (hier keine vorhanden, aber Flag muss False bleiben)
    assert dummy_tools.used is False


@pytest.mark.asyncio
async def test_stream_mixed_thinking_and_content(settings):
    """
    Gemischte Chunks (erst Thinking, dann Content, wieder Thinking, dann done):
    - nur Content bestimmt die finale Antwort,
    - Thinking stört die Endantwort nicht,
    - Antwort wird gespeichert.
    """
    chunks = [
        {"message": {"thinking": "planen...", "content": ""}, "done": False},
        {"message": {"thinking": "", "content": "Antwort Teil 1"}, "done": False},
        {"message": {"thinking": "noch ein Gedanke", "content": ""}, "done": False},
        {"message": {"thinking": "", "content": " und Teil 2"}, "done": True},
    ]

    client = FakeOllamaClient(chunks)
    db = FakeDB()
    chat_id = db.create_chat("Testchat")

    widget = CapturingChatWidget(client, settings, db)
    widget.chat_id = chat_id

    db.save_message(chat_id, "user", "Mische Thinking und Content")

    await widget.run_chat("Mische Thinking und Content")

    assert widget.current_full_response == "Antwort Teil 1 und Teil 2"

    history = db.load_chat(chat_id)
    assistant_messages = [m for m in history if m[0] == "assistant"]
    assert assistant_messages
    assert assistant_messages[-1][1] == "Antwort Teil 1 und Teil 2"


@pytest.mark.asyncio
async def test_stream_done_without_content(settings):
    """
    Stream liefert done=True aber keinen Content:
    - sauberer Fallback,
    - keine kaputte Assistant-Historie.
    """
    chunks = [
        {"message": {"thinking": "", "content": ""}, "done": True},
    ]

    client = FakeOllamaClient(chunks)
    db = FakeDB()
    chat_id = db.create_chat("Testchat")

    widget = CapturingChatWidget(client, settings, db)
    widget.chat_id = chat_id

    db.save_message(chat_id, "user", "Leere Antwort?")

    await widget.run_chat("Leere Antwort?")

    assert widget.current_full_response == "(Kein Inhalt von Ollama erhalten)"

    history = db.load_chat(chat_id)
    assistant_messages = [m for m in history if m[0] == "assistant"]
    # Fallback wird nicht persistiert
    assert not assistant_messages


@pytest.mark.asyncio
async def test_stream_api_error_chunk(settings):
    """
    Ein Chunk enthält {"error": "..."}:
    - Fehlertext wird korrekt verarbeitet,
    - keine kaputte Folge-Historie,
    - UI bekommt den Fehlerzustand.
    """
    chunks = [
        {"error": "API Fehler 500: intern"},
    ]

    client = FakeOllamaClient(chunks)
    db = FakeDB()
    chat_id = db.create_chat("Testchat")

    widget = CapturingChatWidget(client, settings, db)
    widget.chat_id = chat_id

    db.save_message(chat_id, "user", "Provoziere Fehler")

    await widget.run_chat("Provoziere Fehler")

    assert "Ollama Fehler" in widget.current_full_response
    assert "API Fehler 500" in widget.current_full_response

    history = db.load_chat(chat_id)
    assistant_messages = [m for m in history if m[0] == "assistant"]
    # Fehler wird als Assistant-Antwort persistiert, da er für Folge-Kontext relevant ist
    assert assistant_messages
    assert "API Fehler 500" in assistant_messages[-1][1]

    # UI-Updates enthalten den Fehlertext
    assert widget.updates
    texts = [t for (t, _is_final) in widget.updates]
    assert any("API Fehler 500" in t for t in texts)


@pytest.mark.asyncio
async def test_stream_thinking_only_then_retry_succeeds(settings):
    """
    Erst nur Thinking, Retry ohne Thinking liefert Content:
    - automatischer Retry ohne Thinking
    - zweiter Versuch liefert echte Antwort
    - Antwort wird gespeichert
    """
    call_count = 0

    class RetryAwareFakeClient(FakeOllamaClient):
        def __init__(self):
            super().__init__([])  # Dummy, chat() wird überschrieben
            self._first_chunks = [
                {"message": {"thinking": "denke...", "content": ""}, "done": False},
                {"message": {"thinking": "weiter...", "content": ""}, "done": True},
            ]
            self._retry_chunks = [
                {"message": {"content": "Antwort nach Retry", "thinking": ""}, "done": True},
            ]

        async def chat(self, model, messages, temperature=0.7, max_tokens=512, stream=True, think=None):
            nonlocal call_count
            call_count += 1
            chunks = self._retry_chunks if call_count > 1 else self._first_chunks
            async def _gen():
                for c in chunks:
                    await asyncio.sleep(0)
                    yield c
            return _gen()

    settings.retry_without_thinking = True
    settings.max_retries = 1

    client = RetryAwareFakeClient()
    db = FakeDB()
    chat_id = db.create_chat("Testchat")

    widget = CapturingChatWidget(client, settings, db)
    widget.chat_id = chat_id

    db.save_message(chat_id, "user", "Denke und antworte")

    await widget.run_chat("Denke und antworte")

    assert call_count == 2
    assert widget.current_full_response == "Antwort nach Retry"
    history = db.load_chat(chat_id)
    assistant_messages = [m for m in history if m[0] == "assistant"]
    assert assistant_messages
    assert assistant_messages[-1][1] == "Antwort nach Retry"


@pytest.mark.asyncio
async def test_streaming_off_legacy_widget_passes_stream_false(settings):
    """
    Streaming AUS: Legacy-ChatWidget übergibt stream=False an den Chat-Client.
    Verifiziert, dass der Toggle zur Laufzeit wirkt.
    """
    chunks = [
        {"message": {"content": "Vollständige Antwort", "thinking": ""}, "done": True},
    ]
    client = FakeOllamaClient(chunks)
    db = FakeDB()
    chat_id = db.create_chat("Testchat")

    settings.chat_streaming_enabled = False
    widget = CapturingChatWidget(client, settings, db)
    widget.chat_id = chat_id
    widget.orchestrator = None  # Nutze client direkt

    db.save_message(chat_id, "user", "Antworte einmalig")

    await widget.run_chat("Antworte einmalig")

    assert client.last_stream is False
    assert widget.current_full_response == "Vollständige Antwort"


@pytest.mark.asyncio
async def test_streaming_on_legacy_widget_passes_stream_true(settings):
    """
    Streaming EIN (Standard): Legacy-ChatWidget übergibt stream=True.
    """
    chunks = [
        {"message": {"content": "Teil1", "thinking": ""}, "done": False},
        {"message": {"content": " Teil2", "thinking": ""}, "done": True},
    ]
    client = FakeOllamaClient(chunks)
    db = FakeDB()
    chat_id = db.create_chat("Testchat")

    settings.chat_streaming_enabled = True
    widget = CapturingChatWidget(client, settings, db)
    widget.chat_id = chat_id
    widget.orchestrator = None

    db.save_message(chat_id, "user", "Antworte gestreamt")

    await widget.run_chat("Antworte gestreamt")

    assert client.last_stream is True
    assert widget.current_full_response == "Teil1 Teil2"

