"""Chat-Panels."""

from app.gui.domains.operations.chat.panels.chat_message_bubble import ChatMessageBubbleWidget
from app.gui.domains.operations.chat.panels.conversation_panel import ChatConversationPanel
from app.gui.domains.operations.chat.panels.input_panel import ChatInputPanel
from app.gui.domains.operations.chat.panels.chat_navigation_panel import ChatNavigationPanel
from app.gui.domains.operations.chat.panels.chat_topic_section import ChatTopicSection
from app.gui.domains.operations.chat.panels.chat_details_panel import ChatDetailsPanel
from app.gui.domains.operations.chat.panels.chat_context_bar import ChatContextBar
from app.gui.domains.operations.chat.panels.chat_message_widget import ChatMessageWidget
from app.gui.domains.operations.chat.panels.conversation_view import ConversationView
from app.gui.domains.operations.chat.panels.chat_header_widget import ChatHeaderWidget
from app.gui.domains.operations.chat.panels.chat_composer_widget import (
    ChatComposerWidget,
    ChatInput,
)
from app.gui.domains.operations.chat.panels.topic_editor_dialog import (
    TopicCreateDialog,
    TopicRenameDialog,
    TopicDeleteConfirmDialog,
)
from app.gui.domains.operations.chat.panels.topic_actions import (
    create_topic,
    rename_topic,
    delete_topic,
    assign_chat_to_topic,
    remove_chat_from_topic,
)
from app.gui.domains.operations.chat.panels.chat_item_context_menu import build_chat_item_context_menu

__all__ = [
    "ChatMessageBubbleWidget",
    "ChatConversationPanel",
    "ChatInputPanel",
    "ChatNavigationPanel",
    "ChatTopicSection",
    "ChatDetailsPanel",
    "ChatContextBar",
    "ChatMessageWidget",
    "ConversationView",
    "ChatHeaderWidget",
    "ChatComposerWidget",
    "ChatInput",
    "TopicCreateDialog",
    "TopicRenameDialog",
    "TopicDeleteConfirmDialog",
    "create_topic",
    "rename_topic",
    "delete_topic",
    "assign_chat_to_topic",
    "remove_chat_from_topic",
    "build_chat_item_context_menu",
]
