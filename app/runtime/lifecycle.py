"""
Runtime Lifecycle – Single-Instance und Shutdown-Orchestrierung.

Single-Instance: QLockFile verhindert parallele GUI-Instanzen.
- Lock-Erwerb: try_acquire_single_instance_lock() in run_gui_shell vor QApplication
- Lock-Freigabe: release_single_instance_lock() in run_shutdown_cleanup (aboutToQuit)
- Stale Lock: 30s Timeout, removeStaleLockFile bei LockFailedError

Shutdown: Zentrale Cleanup-Hooks für MetricsCollector, ChatService/OllamaClient, Lock.
- aboutToQuit → run_shutdown_cleanup → MetricsCollector.stop(), ChatService.close(), Lock frei

Regeln: docs/04_architecture/RUNTIME_LIFECYCLE_POLICY.md
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Lock-Datei für Single-Instance
_LOCK_FILE_PATH: Optional[Path] = None
_LOCK_FILE: Optional["QLockFile"] = None  # type: ignore[name-defined]


def _get_lock_path() -> Path:
    """Lock-Pfad: XDG_RUNTIME_DIR oder /tmp."""
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime:
        base = Path(runtime)
    else:
        base = Path("/tmp")
    # Unterverzeichnis für saubere Trennung
    lock_dir = base / "linux-desktop-chat"
    lock_dir.mkdir(mode=0o700, exist_ok=True)
    return lock_dir / "instance.lock"


def try_acquire_single_instance_lock() -> bool:
    """
    Versucht, die Single-Instance-Lock zu erwerben.

    Returns:
        True wenn Lock erfolgreich, False wenn bereits eine Instanz läuft.

    Umgehen: LINUX_DESKTOP_CHAT_SINGLE_INSTANCE=0 (z.B. für Tests).
    """
    global _LOCK_FILE, _LOCK_FILE_PATH
    if os.environ.get("LINUX_DESKTOP_CHAT_SINGLE_INSTANCE", "1") == "0":
        return True

    try:
        from PySide6.QtCore import QLockFile
    except ImportError:
        logger.warning("QLockFile nicht verfügbar, Single-Instance übersprungen")
        return True

    path = _get_lock_path()
    lock = QLockFile(str(path))
    # Stale Lock nach 30 Sekunden entfernen (z.B. nach Crash)
    lock.setStaleLockTime(30)

    if lock.tryLock(0):
        _LOCK_FILE = lock
        _LOCK_FILE_PATH = path
        logger.debug("Single-Instance-Lock erworben: %s", path)
        return True

    err = lock.error()
    if err == QLockFile.LockError.LockFailedError:
        logger.info("Bereits eine Instanz aktiv (Lock: %s)", path)
        return False
    if err == QLockFile.LockError.PermissionError:
        logger.warning("Keine Berechtigung für Lock-Datei: %s", path)
        return True  # Weiterlaufen ohne Lock
    # Stale Lock entfernen und erneut versuchen
    if lock.removeStaleLockFile():
        if lock.tryLock(0):
            _LOCK_FILE = lock
            _LOCK_FILE_PATH = path
            return True
    return False


def release_single_instance_lock() -> None:
    """Gibt die Single-Instance-Lock frei."""
    global _LOCK_FILE, _LOCK_FILE_PATH
    if _LOCK_FILE is not None:
        try:
            _LOCK_FILE.unlock()
        except Exception as e:
            logger.debug("Lock-Freigabe: %s", e)
        _LOCK_FILE = None
        _LOCK_FILE_PATH = None


def _run_async_cleanup_blocking() -> None:
    """
    Führt async Cleanup (ChatService/OllamaClient) aus.
    Blockiert kurz mit processEvents, damit die Loop den Task verarbeiten kann.
    """
    import time
    try:
        from PySide6.QtWidgets import QApplication
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        if loop.is_closed():
            return
        task = asyncio.ensure_future(run_shutdown_cleanup_async(), loop=loop)
        app = QApplication.instance()
        if not app:
            return
        deadline = time.monotonic() + 2.0
        while not task.done() and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
    except Exception as e:
        logger.debug("Shutdown async cleanup: %s", e)


def run_shutdown_cleanup() -> None:
    """
    Führt synchronen und asynchronen Shutdown-Cleanup aus.

    Wird von aboutToQuit aufgerufen.
    - Sync: MetricsCollector.stop(), Lock freigeben
    - Async: ChatService.close() (OllamaClient aiohttp Session)
    """
    try:
        from app.metrics import get_metrics_collector
        collector = get_metrics_collector()
        collector.stop()
        logger.debug("MetricsCollector gestoppt")
    except Exception as e:
        logger.debug("Shutdown MetricsCollector: %s", e)

    _run_async_cleanup_blocking()
    release_single_instance_lock()


async def run_shutdown_cleanup_async() -> None:
    """
    Async-Cleanup: OllamaClient Session schließen.
    """
    try:
        from app.services.chat_service import get_chat_service
        chat = get_chat_service()
        await chat.close()
        logger.debug("ChatService/OllamaClient geschlossen")
    except Exception as e:
        logger.debug("Shutdown ChatService: %s", e)


def register_shutdown_hooks(app: "QApplication") -> None:  # type: ignore[name-defined]
    """
    Registriert Shutdown-Hooks an der QApplication.

    - aboutToQuit: synchroner Cleanup (MetricsCollector, Lock)
    - Optional: async Cleanup vor Loop-Ende (qasync handhabt aboutToQuit)
    """
    app.aboutToQuit.connect(run_shutdown_cleanup)
