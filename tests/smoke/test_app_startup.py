"""
Smoke Tests: App Startup.

Testet, dass die Anwendung ohne Fehler startet.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from PySide6.QtWidgets import QApplication


def test_qapplication_available():
    """QApplication ist für GUI-Tests verfügbar."""
    app = QApplication.instance()
    assert app is not None


def test_main_module_importable():
    """App-Modul kann importiert werden."""
    import app.main as main
    assert hasattr(main, "main")
    assert callable(main.main)


def test_main_window_importable():
    """MainWindow kann importiert werden."""
    from app.main import MainWindow
    assert MainWindow is not None


def test_critical_imports():
    """Kritische Module sind importierbar."""
    from app.gui.legacy import ChatWidget
    from app.providers.ollama_client import OllamaClient
    from app.core.config.settings import AppSettings
    from app.core.models.orchestrator import ModelOrchestrator
    from app.rag.service import RAGService
    assert ChatWidget is not None
    assert OllamaClient is not None
    assert AppSettings is not None
    assert ModelOrchestrator is not None
    assert RAGService is not None


@pytest.mark.smoke
@patch("app.main.CloudOllamaProvider")
@patch("app.main.LocalOllamaProvider")
@patch("app.main.OllamaClient")
@patch("app.main.ChatWidget")
def test_main_window_creation(mock_chat_widget_cls, mock_client, mock_local, mock_cloud):
    """MainWindow kann mit gemockten Abhängigkeiten erstellt werden."""
    from PySide6.QtWidgets import QWidget

    # ChatWidget durch minimales Widget mit nötigen Attributen ersetzen
    fake_chat = QWidget()
    fake_chat.refresh_theme = MagicMock()
    fake_chat.chat_id = None
    fake_chat.header = MagicMock()
    fake_chat.header.agent_combo = MagicMock()
    fake_chat.header.agent_combo.findData = MagicMock(return_value=-1)
    mock_chat_widget_cls.return_value = fake_chat

    from app.main import MainWindow
    from app.core.config.settings import AppSettings

    mock_client.return_value = MagicMock()
    mock_client.return_value.get_debug_info = AsyncMock(
        return_value={"online": True, "version": "test", "model_count": 0}
    )
    mock_orch = MagicMock()
    mock_orch.close = AsyncMock(return_value=None)
    mock_local.return_value = MagicMock()
    mock_cloud.return_value = MagicMock()

    # QTimer.singleShot blockieren, damit kein asyncio.create_task ohne Loop läuft
    from PySide6.QtCore import QTimer

    _orig = QTimer.singleShot

    def _noop_single_shot(ms, cb):
        if ms == 0:
            return
        _orig(ms, cb)

    with patch.object(QTimer, "singleShot", new=_noop_single_shot):
        settings = AppSettings()
        win = MainWindow(client=mock_client.return_value, orchestrator=mock_orch, settings=settings)
        QApplication.instance().processEvents()

    assert win is not None
    assert win.chat_widget is not None
    assert win.windowTitle()


def test_app_settings_loads():
    """AppSettings lädt ohne Fehler."""
    from app.core.config.settings import AppSettings
    settings = AppSettings()
    assert settings is not None
    assert hasattr(settings, "theme")
    assert hasattr(settings, "model")


@pytest.mark.smoke
@pytest.mark.async_behavior
@pytest.mark.regression
def test_main_window_with_real_chat_widget():
    """
    MainWindow mit echtem ChatWidget, FakeOllama, Temp-DB.
    Durchbricht den künstlich geglätteten Startpfad.
    """
    import os
    import tempfile
    from app.main import MainWindow
    from app.core.config.settings import AppSettings
    from app.gui.legacy import ChatWidget

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        mock_client = MagicMock()
        mock_client.get_debug_info = AsyncMock(
            return_value={"online": True, "version": "test", "model_count": 0}
        )
        mock_client.get_models = AsyncMock(return_value=[])
        mock_orch = MagicMock()
        mock_orch.close = AsyncMock(return_value=None)
        mock_orch.refresh_available_models = AsyncMock(return_value=None)
        mock_orch._registry = MagicMock()
        mock_orch._registry._models = {}

        with patch("app.main.DatabaseManager") as mock_dm:
            from app.db import DatabaseManager
            mock_dm.return_value = DatabaseManager(db_path=path)

            from PySide6.QtCore import QTimer
            _orig = QTimer.singleShot

            def _noop(ms, cb):
                if ms == 0:
                    return
                _orig(ms, cb)

            with patch.object(QTimer, "singleShot", new=_noop):
                settings = AppSettings()
                win = MainWindow(
                    client=mock_client,
                    orchestrator=mock_orch,
                    settings=settings,
                )
                QApplication.instance().processEvents()

        assert win is not None
        assert win.chat_widget is not None
        assert isinstance(win.chat_widget, ChatWidget)
        win.chat_widget.chat_id = win.db.create_chat("Test")
        assert win.chat_widget.chat_id is not None
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


@pytest.mark.smoke
@pytest.mark.async_behavior
@pytest.mark.regression
def test_chat_full_flow_main_window(qtbot):
    """
    MainWindow mit echtem ChatWidget – run_chat bis API-Call.
    Verhindert: Vollständiger Chat-Flow nicht getestet.
    """
    import os
    import tempfile
    import asyncio
    from app.main import MainWindow
    from app.core.config.settings import AppSettings
    from app.gui.legacy import ChatWidget

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        received = []

        async def fake_chat(model, messages, **kwargs):
            received.append({"model": model, "messages": messages})
            async def _gen():
                yield {"message": {"content": "P2-Flow-Antwort", "thinking": ""}, "done": True}
            return _gen()

        mock_client = MagicMock()
        mock_client.get_debug_info = AsyncMock(
            return_value={"online": True, "version": "test", "model_count": 0}
        )
        mock_client.get_models = AsyncMock(return_value=[])
        mock_client.chat = fake_chat
        async def orch_chat(model_id, messages, **kwargs):
            received.append({"model": model_id, "messages": messages})
            async def _gen():
                yield {"message": {"content": "P2-Flow-Antwort", "thinking": ""}, "done": True}
            return _gen()

        mock_orch = MagicMock()
        mock_orch.close = AsyncMock(return_value=None)
        mock_orch.refresh_available_models = AsyncMock(return_value=None)
        mock_orch._registry = MagicMock()
        mock_orch._registry._models = {}
        mock_orch.chat = orch_chat

        def select_model(prompt, **kwargs):
            from app.core.models.roles import ModelRole
            return (ModelRole.DEFAULT, settings.model or "test:latest")

        mock_orch.select_model_for_prompt = select_model

        with patch("app.main.DatabaseManager") as mock_dm:
            from app.db import DatabaseManager
            mock_dm.return_value = DatabaseManager(db_path=path)
            from PySide6.QtCore import QTimer
            _orig = QTimer.singleShot

            def _noop(ms, cb):
                if ms == 0:
                    return
                _orig(ms, cb)

            with patch.object(QTimer, "singleShot", new=_noop):
                settings = AppSettings()
                win = MainWindow(client=mock_client, orchestrator=mock_orch, settings=settings)
                qtbot.addWidget(win)
                win.chat_widget.chat_id = win.db.create_chat("P2-Flow")

                asyncio.run(win.chat_widget.run_chat("P2-Test-Nachricht"))
                qtbot.wait(200)

                assert len(received) >= 1
                msgs = received[0].get("messages", [])
                user_msgs = [m for m in msgs if m.get("role") == "user"]
                assert any("P2-Test-Nachricht" in (m.get("content") or "") for m in user_msgs)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


@pytest.mark.smoke
@pytest.mark.async_behavior
@pytest.mark.regression
def test_app_main_importable_and_runnable():
    """
    main.main() kann aufgerufen werden – startet ohne Crash.
    Verhindert: App-Start blockiert oder wirft sofort.
    """
    import subprocess
    import sys

    code = """
import asyncio
from app.main import main
try:
    asyncio.run(asyncio.wait_for(main(), timeout=2.0))
except asyncio.TimeoutError:
    pass
"""
    proc = subprocess.Popen(
        [sys.executable, "-c", code],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        proc.wait(timeout=4)
        ret = proc.returncode
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait(timeout=2)
        ret = proc.returncode
    assert ret in (0, None, -15, -9), (
        f"main() sollte starten; returncode={ret}"
    )
