"""
Startup in Degraded Mode: App startet mit fehlenden optionalen Abhängigkeiten.

Fehlerklasse: optional dependency missing breaks startup or leaves inconsistent state.

Prüft:
- optionale RAG-/Chroma-Abhängigkeit fehlt
- Startup läuft trotzdem weiter
- App bleibt benutzbar
- degradierter Modus ist konsistent
- keine halb-initialisierten Zustände
"""

import os
import tempfile
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from app.main import MainWindow
from app.core.config.settings import AppSettings
from app.gui.legacy import ChatWidget
from app.rag.service import RAGService
from tests.helpers.diagnostics import dump_startup_mode_state


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
def mock_orchestrator():
    orch = MagicMock()
    orch.close = AsyncMock(return_value=None)
    orch.refresh_available_models = AsyncMock(return_value=None)
    orch._registry = MagicMock()
    orch._registry._models = {}
    return orch


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.get_debug_info = AsyncMock(
        return_value={"online": True, "version": "test", "model_count": 0}
    )
    client.get_models = AsyncMock(return_value=[])
    return client


@pytest.mark.startup
def test_main_window_starts_with_rag_service_degraded(
    qtbot, temp_db, mock_client, mock_orchestrator
):
    """
    MainWindow startet mit RAGService, der Chroma nicht nutzen kann.

    Simuliert: chromadb fehlt – RAGService liefert keine Augmentierung.
    Erwartung: App startet, Chat bleibt verfügbar.
    """
    # RAGService mit degradiertem Pipeline: augment liefert immer (query, False)
    degraded_rag = MagicMock(spec=RAGService)
    async def augment_degraded(query, enabled=True, **kwargs):
        return query, False
    degraded_rag.augment_if_enabled = augment_degraded
    degraded_rag.get_context = AsyncMock(return_value="")
    degraded_rag.get_knowledge_updater = MagicMock(return_value=None)
    degraded_rag.get_manager = MagicMock(side_effect=Exception("Chroma nicht verfügbar"))
    degraded_rag.get_pipeline = MagicMock(side_effect=Exception("Chroma nicht verfügbar"))

    with patch("app.main.DatabaseManager") as mock_dm:
        from app.db import DatabaseManager
        mock_dm.return_value = DatabaseManager(db_path=temp_db)

        with patch("app.main.RAGService", return_value=degraded_rag):
            with patch.object(QTimer, "singleShot", new=_noop_single_shot):
                settings = AppSettings()
                win = MainWindow(
                    client=mock_client,
                    orchestrator=mock_orchestrator,
                    settings=settings,
                )
                qtbot.addWidget(win)
                QApplication.instance().processEvents()

    assert win is not None, dump_startup_mode_state(win)
    assert win.chat_widget is not None
    assert isinstance(win.chat_widget, ChatWidget)
    assert win.centralWidget() is not None
    assert win.chat_widget.composer is not None
    assert win.chat_widget.conversation_view is not None


@pytest.mark.startup
@pytest.mark.asyncio
async def test_chat_available_after_startup_with_degraded_rag(
    qtbot, temp_db, mock_client, mock_orchestrator
):
    """
    Nach Startup mit fehlender Chroma: Chat ist nutzbar, Nachricht sendbar.
    """
    degraded_rag = MagicMock(spec=RAGService)
    async def augment_degraded(query, enabled=True, **kwargs):
        return query, False
    degraded_rag.augment_if_enabled = augment_degraded
    degraded_rag.get_context = AsyncMock(return_value="")
    degraded_rag.get_knowledge_updater = MagicMock(return_value=None)

    received = []

    async def fake_chat(model_id=None, model=None, messages=None, **kwargs):
        msgs = messages or kwargs.get("messages", [])
        received.append({"model": model_id or model, "messages": msgs})
        async def _gen():
            yield {"message": {"content": "Degraded-Mode-Antwort", "thinking": ""}, "done": True}
        return _gen()

    mock_client.chat = fake_chat
    mock_orchestrator.chat = fake_chat
    mock_orchestrator.select_model_for_prompt = lambda *a, **kw: (
        __import__("app.core.models.roles", fromlist=["ModelRole"]).ModelRole.DEFAULT,
        "test:latest",
    )

    with patch("app.main.DatabaseManager") as mock_dm:
        from app.db import DatabaseManager
        mock_dm.return_value = DatabaseManager(db_path=temp_db)

        with patch("app.main.RAGService", return_value=degraded_rag):
            with patch.object(QTimer, "singleShot", new=_noop_single_shot):
                settings = AppSettings()
                settings.rag_enabled = False  # RAG aus – kein Chroma nötig
                win = MainWindow(
                    client=mock_client,
                    orchestrator=mock_orchestrator,
                    settings=settings,
                )
                qtbot.addWidget(win)
                win.chat_widget.chat_id = win.db.create_chat("Degraded-Test")
                QApplication.instance().processEvents()

                await win.chat_widget.run_chat("Test-Nachricht im degradierten Modus")
                qtbot.wait(200)

    assert len(received) >= 1
    msgs = received[0].get("messages", [])
    user_msgs = [m for m in msgs if m.get("role") == "user"]
    assert any("Test-Nachricht" in (m.get("content") or "") for m in user_msgs)


@pytest.mark.startup
def test_main_window_starts_with_real_rag_service_no_chroma_import(temp_db, mock_client, mock_orchestrator):
    """
    MainWindow mit echtem RAGService – Chroma-Import erfolgt lazy, nicht beim Start.

    Verifiziert: RAGService()-Konstruktor importiert kein chromadb.
    """
    import builtins

    with patch("app.main.DatabaseManager") as mock_dm:
        from app.db import DatabaseManager
        mock_dm.return_value = DatabaseManager(db_path=temp_db)

        chroma_imported = []
        orig_import = builtins.__import__

        def track_import(name, *args, **kwargs):
            if name == "chromadb" or (isinstance(name, str) and name.startswith("chromadb.")):
                chroma_imported.append(name)
            return orig_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=track_import):
            with patch.object(QTimer, "singleShot", new=_noop_single_shot):
                settings = AppSettings()
                win = MainWindow(
                    client=mock_client,
                    orchestrator=mock_orchestrator,
                    settings=settings,
                )
                QApplication.instance().processEvents()

    # Chroma darf beim MainWindow-Start nicht importiert worden sein
    assert len(chroma_imported) == 0, (
        f"Chroma wurde beim Startup importiert: {chroma_imported}. "
        "Optionale Deps sollen lazy geladen werden."
    )
