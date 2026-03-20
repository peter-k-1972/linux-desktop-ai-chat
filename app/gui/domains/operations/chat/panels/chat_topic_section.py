"""
ChatTopicSection – Collapsible topic section for chat navigation.

Groups chats under a topic header. Topics are flat, optional, lightweight.
Section can be expanded/collapsed.
"""

from typing import Callable, Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)
from PySide6.QtCore import Signal, Qt

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.domains.operations.chat.panels.chat_list_item import (
    ChatListItemWidget,
    format_relative_time,
)


class ChatTopicSection(QFrame):
    """
    Collapsible section for a topic (or "Ungruppiert").

    - Header: topic name + collapse toggle + optional add-chat button
    - Body: list of ChatListItemWidget (hidden when collapsed)

    Data binding: set_chats(chats: list[dict]) with keys:
      id, title, last_activity/created_at, preview (optional)
    """

    chat_selected = Signal(int)
    add_chat_requested = Signal(object)  # topic_id | None
    topic_header_menu_requested = Signal(object, object, int)  # topic_id, topic_name, chat_count
    chat_context_menu_requested = Signal(
        int, object, bool, bool
    )  # chat_id, topic_id, is_pinned, is_archived

    def __init__(
        self,
        topic_name: str,
        topic_id: Optional[int] = None,
        collapsible: bool = True,
        show_add_button: bool = True,
        show_topic_actions: bool = False,
        is_pinned_section: bool = False,
        is_archived_section: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("chatTopicSection")
        self._topic_id = topic_id
        self._topic_name = topic_name
        self._collapsible = collapsible
        self._show_add_button = show_add_button
        self._show_topic_actions = show_topic_actions
        self._is_pinned_section = is_pinned_section
        self._is_archived_section = is_archived_section
        self._expanded = True
        self._chat_widgets: dict[int, ChatListItemWidget] = {}
        self._current_chat_id: Optional[int] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._header = QFrame()
        self._header.setObjectName("chatTopicSectionHeader")
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(12, 8, 8, 6)
        header_layout.setSpacing(4)

        self._collapse_icon = QLabel("▼")
        self._collapse_icon.setObjectName("chatTopicCollapseIcon")
        self._collapse_icon.setStyleSheet("font-size: 10px; color: #64748b;")
        if self._collapsible:
            header_layout.addWidget(self._collapse_icon)
        else:
            self._collapse_icon.hide()

        self._label = QLabel(self._topic_name)
        self._label.setObjectName("chatTopicSectionLabel")
        self._label.setStyleSheet("""
            #chatTopicSectionLabel {
                font-size: 12px;
                font-weight: 600;
                color: #475569;
            }
        """)
        header_layout.addWidget(self._label)

        header_layout.addStretch()

        if self._show_add_button:
            self._btn_add = QPushButton()
            self._btn_add.setObjectName("chatTopicAddButton")
            self._btn_add.setIcon(IconManager.get(IconRegistry.ADD, size=14))
            self._btn_add.setFixedSize(24, 24)
            self._btn_add.setToolTip("Neuer Chat in diesem Topic")
            self._btn_add.setStyleSheet("""
                #chatTopicAddButton {
                    background: transparent;
                    border: none;
                    border-radius: 4px;
                    color: #64748b;
                }
                #chatTopicAddButton:hover {
                    background: #e2e8f0;
                    color: #475569;
                }
            """)
            self._btn_add.clicked.connect(
                lambda: self.add_chat_requested.emit(self._topic_id)
            )
            header_layout.addWidget(self._btn_add)

        self._header.setStyleSheet("""
            #chatTopicSectionHeader {
                background: #f8fafc;
                border-radius: 6px;
                margin-top: 8px;
            }
            #chatTopicSectionHeader:hover {
                background: #f1f5f9;
            }
        """)
        if self._collapsible:
            self._header.mousePressEvent = self._on_header_clicked
        if self._show_topic_actions:
            self._header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self._header.customContextMenuRequested.connect(self._on_header_context_menu)
        layout.addWidget(self._header)

        self._body = QWidget()
        self._body.setObjectName("chatTopicSectionBody")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(4, 4, 4, 4)
        self._body_layout.setSpacing(0)
        layout.addWidget(self._body)

        self.setStyleSheet("""
            #chatTopicSection {
                background: transparent;
                border: none;
            }
        """)

    def _on_header_clicked(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_expanded()

    def _on_header_context_menu(self, pos) -> None:
        if self._show_topic_actions and self._topic_id is not None:
            self.topic_header_menu_requested.emit(
                self._topic_id,
                self._topic_name,
                len(self._chat_widgets),
            )

    def toggle_expanded(self) -> None:
        self._expanded = not self._expanded
        self._body.setVisible(self._expanded)
        self._collapse_icon.setText("▼" if self._expanded else "▶")

    def set_expanded(self, expanded: bool) -> None:
        if self._expanded != expanded:
            self.toggle_expanded()

    def set_chats(
        self,
        chats: list,
        current_chat_id: Optional[int] = None,
        on_click: Optional[Callable[[int], None]] = None,
    ) -> None:
        """Populate section with chat items. chats: list of dicts with id, title, last_activity/created_at, preview."""
        self._current_chat_id = current_chat_id
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._chat_widgets.clear()

        for chat in chats:
            chat_id = chat.get("id")
            if chat_id is None:
                continue
            title = chat.get("title", "Neuer Chat")
            ts = chat.get("last_activity") or chat.get("created_at")
            time_str = format_relative_time(ts)
            preview = chat.get("preview")
            active = chat_id == current_chat_id
            item = ChatListItemWidget(
                chat_id, title, time_str, active=active, parent=self, preview=preview
            )
            item.mousePressEvent = lambda e, cid=chat_id: self._on_item_clicked(cid)
            item.context_menu_requested.connect(
                lambda cid: self.chat_context_menu_requested.emit(
                    cid,
                    self._topic_id,
                    self._is_pinned_section,
                    self._is_archived_section,
                )
            )
            self._chat_widgets[chat_id] = item
            self._body_layout.addWidget(item)

        self._body_layout.addStretch()

    def _on_item_clicked(self, chat_id: int) -> None:
        for wid in self._chat_widgets.values():
            wid.set_active(wid.chat_id == chat_id)
        self._current_chat_id = chat_id
        self.chat_selected.emit(chat_id)

    def set_current_chat(self, chat_id: Optional[int]) -> None:
        """Update active state without rebuilding."""
        self._current_chat_id = chat_id
        for wid in self._chat_widgets.values():
            wid.set_active(wid.chat_id == chat_id)
