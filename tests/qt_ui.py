"""Qt-Test-Helfer ohne pytest-qt (liegt außerhalb von tests.helpers, kein schwerer Paket-Import)."""

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication


def process_events_and_wait(ms: int = 50) -> None:
    QApplication.processEvents()
    if ms > 0:
        QTest.qWait(ms)
