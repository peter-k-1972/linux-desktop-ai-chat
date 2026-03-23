"""Regression: betroffene Widgets nach Doppelquellen-Cleanup weiter instanziierbar."""

from __future__ import annotations

from pathlib import Path

from app.gui.domains.operations.chat.panels.conversation_view import ConversationView
from app.gui.domains.operations.chat.panels.input_panel import ChatInputPanel
from app.gui.theme import design_metrics as dm
from app.gui.workbench.ui.panel_header import PanelHeader
from tests.qt_ui import process_events_and_wait

ROOT = Path(__file__).resolve().parents[3]


def test_chat_input_panel_instantiable(qapplication):
    p = ChatInputPanel()
    p.show()
    process_events_and_wait(0)
    assert p._model_combo is not None


def test_conversation_view_still_valid(qapplication):
    v = ConversationView(theme="dark")
    assert v.message_container.maximumWidth() == dm.CHAT_CONTENT_MAX_WIDTH_PX


def test_panel_header_instantiable(qapplication):
    h = PanelHeader("T", "S")
    h.show()
    process_events_and_wait(0)


def test_sidebar_widget_source_uses_metrics_not_adhoc_heights():
    """Kein Import von ``app.gui.legacy`` (löst qasync über ``legacy.__init__`` aus)."""
    src = (ROOT / "app" / "gui" / "legacy" / "sidebar_widget.py").read_text(encoding="utf-8")
    assert "design_metrics" in src
    assert "setMinimumHeight(44)" not in src
    assert "setFixedSize(44, 44)" not in src
