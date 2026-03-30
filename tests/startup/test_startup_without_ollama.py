"""
Startup ohne Ollama: App startet, wenn Ollama-Endpoint nicht erreichbar.

Fehlerklasse: degraded_mode_failure, startup_ordering.

Prüft:
- Ollama nicht erreichbar beim Start
- Modellliste kann nicht geladen werden
- Anwendung startet trotzdem
- Kein Crash im Startup
- Chat/Modellfunktionen degradieren (leere Modellliste)
"""

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from app.main import MainWindow
from app.core.config.settings import AppSettings
from app.gui.legacy import ChatWidget
from app.rag.service import RAGService


_orig_single_shot = QTimer.singleShot


def _noop_single_shot(ms, cb):
    """Blockiert QTimer.singleShot(0) um asyncio.create_task ohne Loop zu vermeiden."""
    if ms == 0:
        return
    _orig_single_shot(ms, cb)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def ollama_unreachable_client():
    """Client: Ollama nicht erreichbar – get_models/get_debug_info simulieren Fehler."""
    client = MagicMock()
    client.base_url = "http://localhost:11434"
    client.get_models = AsyncMock(return_value=[])  # Leer = nicht erreichbar
    client.get_debug_info = AsyncMock(
        return_value={
            "online": False,
            "base_url": "http://localhost:11434",
            "version": None,
            "models": [],
            "model_count": 0,
            "processes": [],
            "vram_used_mib": None,
        }
    )
    client.close = AsyncMock(return_value=None)
    return client


@pytest.fixture
def orchestrator_empty_models(ollama_unreachable_client):
    """Orchestrator mit leerer Modellliste (Ollama nicht erreichbar)."""
    orch = MagicMock()
    orch.close = AsyncMock(return_value=None)
    orch.refresh_available_models = AsyncMock(return_value=None)
    orch._registry = MagicMock()
    orch._registry._models = {}
    orch._local = MagicMock()
    orch._local.get_models = AsyncMock(return_value=[])
    orch._cloud = MagicMock()
    orch._cloud.has_api_key = lambda: False
    return orch


@pytest.mark.startup
def test_main_window_starts_when_ollama_unreachable(
    qtbot, temp_db, ollama_unreachable_client, orchestrator_empty_models
):
    """
    MainWindow startet, wenn Ollama-Endpoint nicht erreichbar.

    Modellliste leer, aber kein Crash.
    """
    with patch("app.main.DatabaseManager") as mock_dm:
        from app.core.db import DatabaseManager

        mock_dm.return_value = DatabaseManager(db_path=temp_db)

        with patch.object(QTimer, "singleShot", new=_noop_single_shot):
            settings = AppSettings()
            win = MainWindow(
                client=ollama_unreachable_client,
                orchestrator=orchestrator_empty_models,
                settings=settings,
            )
            qtbot.addWidget(win)
            QApplication.instance().processEvents()

    assert win is not None
    assert win.chat_widget is not None
    assert isinstance(win.chat_widget, ChatWidget)
    assert win.centralWidget() is not None


@pytest.mark.startup
@pytest.mark.asyncio
async def test_chat_available_after_startup_without_ollama(
    qtbot, temp_db, ollama_unreachable_client, orchestrator_empty_models
):
    """
    Nach Startup ohne Ollama: Chat ist nutzbar, Nachricht sendbar.

    Modellfunktionen degradiert (leere Liste), aber run_chat funktioniert mit Mock.
    """
    received = []

    async def fake_chat(model_id=None, model=None, messages=None, **kwargs):
        msgs = messages or kwargs.get("messages", [])
        received.append({"model": model_id or model, "messages": msgs})

        async def _gen():
            yield {"message": {"content": "Antwort ohne Ollama", "thinking": ""}, "done": True}

        return _gen()

    ollama_unreachable_client.chat = fake_chat
    orchestrator_empty_models.chat = fake_chat
    orchestrator_empty_models.select_model_for_prompt = lambda *a, **kw: (
        __import__("app.core.models.roles", fromlist=["ModelRole"]).ModelRole.DEFAULT,
        "test:latest",
    )

    with patch("app.main.DatabaseManager") as mock_dm:
        from app.core.db import DatabaseManager

        mock_dm.return_value = DatabaseManager(db_path=temp_db)

        with patch.object(QTimer, "singleShot", new=_noop_single_shot):
            settings = AppSettings()
            settings.model = "test:latest"
            win = MainWindow(
                client=ollama_unreachable_client,
                orchestrator=orchestrator_empty_models,
                settings=settings,
            )
            qtbot.addWidget(win)
            win.chat_widget.chat_id = win.db.create_chat("Ollama-offline-Test")
            QApplication.instance().processEvents()

            await win.chat_widget.run_chat("Test ohne Ollama")
            qtbot.wait(200)

    assert len(received) >= 1
