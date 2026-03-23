"""
Layout-Regression nach Chat-Refactor: keine festen 1200/1000-Zwänge, Metriken aus design_metrics.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QWidget

from app.gui.domains.operations.chat.panels.chat_composer_widget import ChatComposerWidget
from app.gui.domains.operations.chat.panels.chat_message_widget import ChatMessageWidget
from app.gui.domains.operations.chat.panels.conversation_panel import ChatConversationPanel
from app.gui.domains.operations.chat.panels.conversation_view import ConversationView
from app.gui.domains.operations.chat.panels.input_panel import ChatInputPanel
from app.gui.theme import design_metrics as dm
from tests.qt_ui import process_events_and_wait


def test_conversation_view_instanciable(qapplication):
    view = ConversationView(theme="dark")
    view.show()
    process_events_and_wait(0)
    assert view.message_container is not None


def test_conversation_view_no_forced_1200_width(qapplication):
    view = ConversationView(theme="dark")
    assert view.message_container.minimumWidth() == 0
    assert view.message_container.maximumWidth() == dm.CHAT_CONTENT_MAX_WIDTH_PX
    assert view.message_container.maximumWidth() != 1200


def test_conversation_view_resize_no_exception(qapplication):
    view = ConversationView(theme="dark")
    view.resize(320, 480)
    view.show()
    process_events_and_wait(30)
    view.resize(900, 700)
    process_events_and_wait(30)
    view.add_message("user", "x")
    process_events_and_wait(30)


def test_chat_composer_instanciable(qapplication):
    composer = ChatComposerWidget(icons_path="")
    composer.show()
    process_events_and_wait(0)
    assert composer.isVisible()


def test_chat_composer_no_fixed_1000_width(qapplication):
    composer = ChatComposerWidget(icons_path="")
    container = composer.findChild(QWidget, "composerContainer")
    assert container is not None
    assert container.minimumWidth() == 0
    assert container.maximumWidth() == dm.CHAT_CONTENT_MAX_WIDTH_PX


def test_chat_composer_resize_no_exception(qapplication):
    composer = ChatComposerWidget(icons_path="")
    composer.resize(400, 200)
    composer.show()
    process_events_and_wait(20)
    composer.resize(1100, 220)
    process_events_and_wait(20)


def test_chat_message_widget_bubble_max_matches_policy(qapplication):
    msg = ChatMessageWidget(
        role="user", content="hello", theme="dark", parent=None
    )
    assert msg.bubble.maximumWidth() == dm.CHAT_BUBBLE_MAX_WIDTH_PX


def test_conversation_panel_instanciable_and_resize(qapplication):
    panel = ChatConversationPanel()
    panel.resize(500, 400)
    panel.show()
    process_events_and_wait(20)
    panel.add_user_message("hi")
    process_events_and_wait(20)


def test_input_panel_button_heights_after_show(qapplication):
    panel = ChatInputPanel()
    panel.show()
    process_events_and_wait(30)
    assert panel._btn_prompt.height() == dm.INPUT_MD_HEIGHT_PX
    assert panel._btn_send.height() == dm.CHAT_PRIMARY_SEND_HEIGHT_PX
