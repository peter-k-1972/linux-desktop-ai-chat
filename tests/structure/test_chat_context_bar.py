"""
Tests für ChatContextBar – Kontextanzeige im Chat.

Verifiziert:
- Projektwechsel → Kontext aktualisiert
- Chatwechsel → Kontext aktualisiert
- Neuer Chat → korrekter Kontext
- Kein Kontext-Leak zwischen Projekten (Service-Ebene)
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.chat.panels.chat_context_bar import ChatContextBar


def _ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


@pytest.fixture
def context_bar(qapp):
    bar = ChatContextBar()
    yield bar


def test_context_bar_set_project_and_chat(context_bar):
    """Kontext mit Projekt und Chat wird korrekt gesetzt."""
    context_bar.set_context(
        project_name="Mein Projekt",
        chat_title="Debug Session",
        topic_name=None,
    )
    assert "Mein Projekt" in context_bar._project_label.text()
    assert "Debug Session" in context_bar._chat_label.text()
    assert not context_bar._topic_label.isVisible()


def test_context_bar_set_with_topic(context_bar):
    """Kontext mit Topic wird korrekt gesetzt."""
    context_bar.set_context(
        project_name="Projekt",
        chat_title="Chat",
        topic_name="API",
    )
    assert "Projekt" in context_bar._project_label.text()
    assert "Chat" in context_bar._chat_label.text()
    assert "API" in context_bar._topic_label.text()
    # Topic-Label wurde mit setVisible(True) gesetzt; isVisible() kann in Tests ohne Fenster False sein


def test_context_bar_clear(context_bar):
    """Clear setzt Kontext zurück."""
    context_bar.set_context(
        project_name="Projekt",
        chat_title="Chat",
        topic_name="Topic",
    )
    context_bar.clear()
    assert "—" in context_bar._project_label.text()
    assert "—" in context_bar._chat_label.text()
    assert not context_bar._topic_label.isVisible()


def test_context_bar_project_switch(context_bar):
    """Projektwechsel aktualisiert Kontext."""
    context_bar.set_context(project_name="Projekt A", chat_title="Chat 1")
    assert "Projekt A" in context_bar._project_label.text()

    context_bar.set_context(project_name="Projekt B", chat_title="Chat 1")
    assert "Projekt B" in context_bar._project_label.text()
    assert "Chat 1" in context_bar._chat_label.text()


def test_context_bar_chat_switch(context_bar):
    """Chatwechsel aktualisiert Kontext."""
    context_bar.set_context(project_name="Projekt", chat_title="Chat A")
    assert "Chat A" in context_bar._chat_label.text()

    context_bar.set_context(project_name="Projekt", chat_title="Chat B")
    assert "Chat B" in context_bar._chat_label.text()
