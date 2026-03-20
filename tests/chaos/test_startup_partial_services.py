"""
Chaos: Startup mit partiell defekten Diensten.

Szenario: Startup mit partiell defekten Diensten (RAG degraded, Provider mock).
Erwartung: MainWindow startet, degradierter Modus konsistent, keine Halbzustände.
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


_orig_single_shot = QTimer.singleShot


def _noop_single_shot(ms, cb):
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


@pytest.mark.chaos
@pytest.mark.startup
def test_main_window_starts_with_degraded_rag(qtbot, temp_db, mock_client, mock_orchestrator):
    """
    MainWindow startet mit degradiertem RAG (Chroma fehlt).
    Erwartung: App startet, Chat-Widget vorhanden, keine Halbzustände.
    """
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

    assert win is not None
    assert win.chat_widget is not None
    assert isinstance(win.chat_widget, ChatWidget)
    assert win.centralWidget() is not None
    assert win.chat_widget.composer is not None
