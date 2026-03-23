"""
ChatNavigationPanel – Scalable left-side chat navigation for ChatWorkspace.

Sections:
- Search field
- New Chat button
- Angeheftet (pinned chats)
- Topics (collapsible)
- Ungruppiert (ungrouped chats)
- Archiviert (archived chats, collapsible)

Daten kommen aus ChatService / SQLite: Chats pro Projekt inkl. Topic, pinned und
archived (project_chats). Optional können Listen auch per set_chats() injiziert
werden (Tests); ohne Override lädt load_chats_from_backend() über den Service.
"""

from typing import Any, Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QWidget,
    QCheckBox,
    QComboBox,
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QCursor

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.widgets import EmptyStateWidget
from app.gui.domains.operations.chat.panels.chat_topic_section import ChatTopicSection
from app.gui.domains.operations.chat.panels.topic_actions import (
    create_topic,
    build_topic_header_menu,
)
from app.gui.domains.operations.chat.panels.chat_item_context_menu import build_chat_item_context_menu


# Internal key for chats without topic (UI language: DE)
_UNGROUPED_KEY = "Ungruppiert"


def _group_chats_by_topic(chats: list) -> list[tuple[str | None, int | None, list]]:
    """
    Group chats by topic.
    Returns: [(topic_name, topic_id, [chats]), ...]
    topic_name=None, topic_id=None = Ungruppiert
    """
    groups: dict[tuple[str | None, int | None], list] = {}
    for chat in chats:
        topic_id = chat.get("topic_id")
        topic_name = chat.get("topic_name")
        if topic_id is None and (topic_name is None or topic_name == ""):
            key = (_UNGROUPED_KEY, None)
        else:
            key = (topic_name or "Topic", topic_id)
        if key not in groups:
            groups[key] = []
        groups[key].append(chat)

    def sort_key(item):
        name, tid = item[0]
        return (name == _UNGROUPED_KEY, name or "")

    result = []
    for (name, tid), group_chats in sorted(groups.items(), key=sort_key):
        group_chats.sort(
            key=lambda c: (c.get("last_activity") or c.get("created_at") or ""),
            reverse=True,
        )
        result.append((name, tid, group_chats))
    return result


class ChatNavigationPanel(QFrame):
    """
    Left-side chat navigation panel for ChatWorkspace.

    Sections: Search, New Chat, Angeheftet, Topics, Ungruppiert, Archiviert.
    Topics and Archiviert are collapsible.

    Data binding interface:
      - set_project(project_id, project_name)
      - set_chats(pinned, topics_data, ungrouped, archived)
        pinned/archived: list of chat dicts
        topics_data: list of (topic_id, topic_name, [chats])
        ungrouped: list of chat dicts
      - set_current_chat(chat_id)
    """

    chat_selected = Signal(int)
    new_chat_requested = Signal()
    chat_deleted = Signal(int)  # chat_id of deleted chat

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatNavigationPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(340)
        self._project_id: Optional[int] = None
        self._project_name: Optional[str] = None
        self._current_chat_id: Optional[int] = None
        self._section_widgets: dict[str, ChatTopicSection] = {}
        self._search_debounce = QTimer(self)
        self._search_debounce.setSingleShot(True)
        self._search_debounce.timeout.connect(self._load_chats)
        self._setup_ui()
        self._connect_project_context()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Project header
        self._project_header = QFrame()
        self._project_header.setObjectName("chatNavProjectHeader")
        header_layout = QVBoxLayout(self._project_header)
        header_layout.setContentsMargins(12, 10, 12, 10)
        self._project_label = QLabel("Bitte Projekt auswählen")
        self._project_label.setObjectName("chatNavProjectLabel")
        self._project_label.setProperty("projectMode", "false")
        self._project_label.setWordWrap(True)
        header_layout.addWidget(self._project_label)
        layout.addWidget(self._project_header)

        # Search field
        self._search = QLineEdit()
        self._search.setObjectName("chatNavSearch")
        self._search.setPlaceholderText("Titel, Topic oder Inhalt…")
        self._search.textChanged.connect(self._on_search_debounced)
        layout.addWidget(self._search)

        # Lightweight filters (secondary navigation aids)
        self._filter_row = QWidget()
        filter_layout = QHBoxLayout(self._filter_row)
        filter_layout.setContentsMargins(0, 4, 0, 4)
        filter_layout.setSpacing(8)

        self._filter_pinned = QCheckBox("Angeheftet")
        self._filter_pinned.stateChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self._filter_pinned)

        self._filter_archived = QCheckBox("Archiv")
        self._filter_archived.stateChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self._filter_archived)

        self._filter_topic = QComboBox()
        self._filter_topic.setObjectName("chatNavFilterTopic")
        self._filter_topic.setMinimumWidth(90)
        self._filter_topic.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self._filter_topic)

        self._filter_recent = QComboBox()
        self._filter_recent.setObjectName("chatNavFilterRecent")
        self._filter_recent.setMinimumWidth(85)
        self._filter_recent.addItem("Alle", None)
        self._filter_recent.addItem("7 Tage", 7)
        self._filter_recent.addItem("30 Tage", 30)
        self._filter_recent.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self._filter_recent)

        filter_layout.addStretch()
        layout.addWidget(self._filter_row)

        # New Chat button
        self._btn_new = QPushButton("Neuer Chat")
        self._btn_new.setObjectName("chatNavNewChatButton")
        self._btn_new.setIcon(IconManager.get(IconRegistry.ADD, size=16))
        self._btn_new.setEnabled(False)
        self._btn_new.clicked.connect(self._on_new_chat)
        layout.addWidget(self._btn_new)

        # New Topic button
        self._btn_new_topic = QPushButton("Neues Topic")
        self._btn_new_topic.setObjectName("chatNavNewTopicButton")
        self._btn_new_topic.setIcon(IconManager.get(IconRegistry.ADD, size=14))
        self._btn_new_topic.setEnabled(False)
        self._btn_new_topic.clicked.connect(self._on_new_topic)
        layout.addWidget(self._btn_new_topic)

        # Scroll area for sections
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._scroll.setWidget(self._content)
        layout.addWidget(self._scroll, 1)

        # Section placeholders (built on first set_chats)
        self._pinned_section: Optional[ChatTopicSection] = None
        self._topics_sections: list[ChatTopicSection] = []
        self._ungrouped_section: Optional[ChatTopicSection] = None
        self._archived_section: Optional[ChatTopicSection] = None

        self._empty_widget = EmptyStateWidget(
            title="Keine Chats",
            description="Lege einen neuen Chat an.",
            compact=True,
            parent=self,
        )
        self._empty_widget.hide()

    def _refresh_project_label_style(self) -> None:
        """Aktualisiert Stylesheet nach Property-Änderung (projectMode)."""
        try:
            style = self._project_label.style()
            if style:
                style.unpolish(self._project_label)
                style.polish(self._project_label)
        except Exception:
            pass

    def _connect_project_context(self) -> None:
        """Subscribe to project context for project-scoped data binding."""
        try:
            from app.gui.events.project_events import subscribe_project_events
            from app.core.context.project_context_manager import get_project_context_manager
            subscribe_project_events(self._on_project_context_changed)
            mgr = get_project_context_manager()
            pid = mgr.get_active_project_id()
            self._on_project_context_changed({"project_id": pid})
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        project_id = payload.get("project_id")
        if project_id is None:
            self._set_project_ui(None, None)
            return
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            project = get_project_context_manager().get_active_project()
            if project and isinstance(project, dict):
                self._set_project_ui(
                    project.get("project_id"),
                    project.get("name", "Projekt"),
                )
            else:
                self._set_project_ui(None, None)
        except Exception:
            self._set_project_ui(None, None)

    def _set_project_ui(
        self,
        project_id: Optional[int],
        project_name: Optional[str],
    ) -> None:
        self._project_id = project_id
        self._project_name = project_name
        # Clear cached data and selection when project changes – no global chat mixing
        self._current_chat_id = None
        self._cached_pinned = []
        self._cached_topics = []
        self._cached_ungrouped = []
        self._cached_archived = []
        if project_id is not None and project_name:
            self._project_label.setText(project_name)
            self._project_label.setProperty("projectMode", "true")
            self._refresh_project_label_style()
            self._btn_new.setEnabled(True)
            self._btn_new_topic.setEnabled(True)
            self._search.show()
            self._filter_row.show()
            self._filter_pinned.show()
            self._filter_archived.show()
            self._filter_topic.show()
            self._filter_recent.show()
            self._populate_topic_filter()
        else:
            # Global mode: Chat ohne Projekt nutzbar
            self._project_label.setText("Globale Chats")
            self._project_label.setProperty("projectMode", "false")
            self._refresh_project_label_style()
            self._btn_new.setEnabled(True)
            self._btn_new_topic.setEnabled(False)
            self._search.show()
            self._filter_row.show()
            self._filter_pinned.hide()
            self._filter_archived.hide()
            self._filter_topic.hide()
            self._filter_recent.show()
        self._load_chats()

    def set_project(self, project_id: Optional[int], project_name: Optional[str]) -> None:
        """Set project for data binding (alternative to event subscription)."""
        self._set_project_ui(project_id, project_name)

    def set_chats(
        self,
        pinned: Optional[list] = None,
        topics_data: Optional[list] = None,
        ungrouped: Optional[list] = None,
        archived: Optional[list] = None,
    ) -> None:
        """
        Set chat data for all sections.

        pinned: list of chat dicts (id, title, last_activity, preview)
        topics_data: list of (topic_id, topic_name, [chats])
        ungrouped: list of chat dicts
        archived: list of chat dicts
        """
        self._cached_pinned = pinned or []
        self._cached_topics = topics_data or []
        self._cached_ungrouped = ungrouped or []
        self._cached_archived = archived or []
        self._load_chats()

    def _load_chats(self) -> None:
        """Load chats from backend or cached data. Override point for persistence."""
        pinned = getattr(self, "_cached_pinned", [])
        topics_data = getattr(self, "_cached_topics", [])
        ungrouped = getattr(self, "_cached_ungrouped", [])
        archived = getattr(self, "_cached_archived", [])

        # Try backend if no cached data (project or global mode)
        if not any([pinned, topics_data, ungrouped, archived]):
            try:
                from app.services.chat_service import get_chat_service
                svc = get_chat_service()
                filter_text = self._search.text().strip() if self._search.isVisible() else ""
                topic_id = self._filter_topic.currentData() if self._project_id is not None else None
                pinned_only = True if self._filter_pinned.isChecked() else None
                archived_only = True if self._filter_archived.isChecked() else False
                recent_days = self._filter_recent.currentData()
                chats = svc.list_chats_for_project(
                    self._project_id,
                    filter_text,
                    topic_id=topic_id,
                    pinned_only=pinned_only,
                    archived_only=archived_only,
                    recent_days=recent_days,
                )

                # Split by pinned/archived: archived hidden from active, pinned in dedicated section
                archived = [c for c in chats if c.get("archived")]
                active_chats = [c for c in chats if not c.get("archived")]
                pinned = [c for c in active_chats if c.get("pinned")]
                non_pinned = [c for c in active_chats if not c.get("pinned")]
                groups = _group_chats_by_topic(non_pinned)
                topics_data = [(tid, name, chs) for name, tid, chs in groups if name != _UNGROUPED_KEY]
                ungrouped = next((chs for name, tid, chs in groups if name == _UNGROUPED_KEY), [])
            except Exception:
                chats = []
                topics_data = []
                ungrouped = []

        self._render_sections(pinned, topics_data, ungrouped, archived)

    def _render_sections(
        self,
        pinned: list,
        topics_data: list,
        ungrouped: list,
        archived: list,
    ) -> None:
        """Build section widgets from data."""
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._section_widgets.clear()
        self._topics_sections.clear()
        self._pinned_section = None
        self._ungrouped_section = None
        self._archived_section = None

        has_any = bool(pinned or topics_data or ungrouped or archived)
        if not has_any:
            self._content_layout.addWidget(self._empty_widget)
            self._empty_widget.show()
            self._content_layout.addStretch()
            return

        self._empty_widget.hide()

        # Pinned section
        if pinned:
            self._pinned_section = ChatTopicSection(
                "Angeheftet",
                topic_id=None,
                collapsible=False,
                show_add_button=False,
                show_topic_actions=False,
                is_pinned_section=True,
                is_archived_section=False,
                parent=self,
            )
            self._pinned_section.chat_selected.connect(self._on_chat_selected)
            self._pinned_section.chat_context_menu_requested.connect(self._on_chat_context_menu)
            self._pinned_section.set_chats(pinned, self._current_chat_id)
            self._content_layout.addWidget(self._pinned_section)
            self._section_widgets["pinned"] = self._pinned_section

        # Topics sections
        for topic_id, topic_name, chats in topics_data:
            section = ChatTopicSection(
                topic_name,
                topic_id=topic_id,
                collapsible=True,
                show_add_button=True,
                show_topic_actions=True,
                is_pinned_section=False,
                is_archived_section=False,
                parent=self,
            )
            section.chat_selected.connect(self._on_chat_selected)
            section.add_chat_requested.connect(self._on_add_chat_in_topic)
            section.topic_header_menu_requested.connect(self._on_topic_header_menu)
            section.chat_context_menu_requested.connect(self._on_chat_context_menu)
            section.set_chats(chats, self._current_chat_id)
            self._content_layout.addWidget(section)
            self._topics_sections.append(section)
            self._section_widgets[f"topic_{topic_id}"] = section

        # Ungrouped section
        if ungrouped:
            self._ungrouped_section = ChatTopicSection(
                _UNGROUPED_KEY,
                topic_id=None,
                collapsible=True,
                show_add_button=True,
                show_topic_actions=False,
                is_pinned_section=False,
                is_archived_section=False,
                parent=self,
            )
            self._ungrouped_section.chat_selected.connect(self._on_chat_selected)
            self._ungrouped_section.add_chat_requested.connect(self._on_add_chat_in_topic)
            self._ungrouped_section.chat_context_menu_requested.connect(self._on_chat_context_menu)
            self._ungrouped_section.set_chats(ungrouped, self._current_chat_id)
            self._content_layout.addWidget(self._ungrouped_section)
            self._section_widgets["ungrouped"] = self._ungrouped_section

        # Archived section (collapsible, collapsed by default when empty)
        self._archived_section = ChatTopicSection(
            "Archiviert",
            topic_id=None,
            collapsible=True,
            show_add_button=False,
            show_topic_actions=False,
            is_pinned_section=False,
            is_archived_section=True,
            parent=self,
        )
        self._archived_section.chat_selected.connect(self._on_chat_selected)
        self._archived_section.chat_context_menu_requested.connect(self._on_chat_context_menu)
        self._archived_section.set_chats(archived, self._current_chat_id)
        if not archived:
            self._archived_section.set_expanded(False)
        self._content_layout.addWidget(self._archived_section)
        self._section_widgets["archived"] = self._archived_section

        self._content_layout.addStretch()

    def _on_chat_selected(self, chat_id: int) -> None:
        self._current_chat_id = chat_id
        for section in self._section_widgets.values():
            section.set_current_chat(chat_id)
        self.chat_selected.emit(chat_id)

    def _on_new_chat(self) -> None:
        self._on_add_chat_in_topic(None)

    def _on_new_topic(self) -> None:
        if self._project_id is None:
            return
        topic_id = create_topic(self._project_id, self, on_created=lambda _: self.refresh())
        if topic_id is not None:
            self.refresh()

    def _on_topic_header_menu(
        self,
        topic_id: object,
        topic_name: object,
        chat_count: int,
    ) -> None:
        if self._project_id is None:
            return
        menu = build_topic_header_menu(
            topic_id,
            topic_name,
            chat_count,
            self._project_id,
            self,
            on_rename=lambda new_name: self.refresh(),
            on_delete=lambda: self.refresh(),
        )
        menu.exec(QCursor.pos())

    def _on_chat_context_menu(
        self,
        chat_id: int,
        topic_id: Optional[int],
        is_pinned: bool,
        is_archived: bool,
    ) -> None:
        try:
            from app.services.chat_service import get_chat_service
            from app.services.project_service import get_project_service
            chat_svc = get_chat_service()
            info = chat_svc.get_chat_info(chat_id)
            chat_title = info.get("title", "Neuer Chat") if info else "Neuer Chat"
            project_id = self._project_id
            if project_id is None:
                project_id = get_project_service().get_project_of_chat(chat_id)
            if project_id is not None:
                from app.services.topic_service import get_topic_service
                topic_svc = get_topic_service()
                topics = topic_svc.list_topics_for_project(project_id)
            else:
                topics = []
        except Exception:
            chat_title = "Neuer Chat"
            project_id = None
            topics = []
        menu = build_chat_item_context_menu(
            project_id,
            chat_id,
            chat_title,
            topic_id,
            is_pinned,
            is_archived,
            topics,
            self,
            on_action=lambda: self.refresh(),
            on_chat_deleted=lambda cid: self.chat_deleted.emit(cid),
        )
        menu.exec(QCursor.pos())

    def _on_add_chat_in_topic(self, topic_id: Optional[int]) -> None:
        try:
            from app.services.chat_service import get_chat_service
            svc = get_chat_service()
            if self._project_id is not None:
                chat_id = svc.create_chat_in_project(
                    self._project_id, "Neuer Chat", topic_id=topic_id
                )
            else:
                chat_id = svc.create_chat("Neuer Chat")
            self._current_chat_id = chat_id
            self._load_chats()
            self.chat_selected.emit(chat_id)
        except Exception:
            self.new_chat_requested.emit()

    def _on_search_debounced(self) -> None:
        self._search_debounce.stop()
        self._search_debounce.start(250)

    def _on_filter_changed(self) -> None:
        self._load_chats()

    def _populate_topic_filter(self) -> None:
        self._filter_topic.blockSignals(True)
        self._filter_topic.clear()
        self._filter_topic.addItem("Alle Themen", None)
        self._filter_topic.addItem(_UNGROUPED_KEY, -1)
        if self._project_id:
            try:
                from app.services.topic_service import get_topic_service
                for t in get_topic_service().list_topics_for_project(self._project_id):
                    tid = t.get("id")
                    tname = t.get("name", "Topic")
                    if tid is not None:
                        self._filter_topic.addItem(tname, tid)
            except Exception:
                pass
        self._filter_topic.blockSignals(False)

    def set_current_chat(self, chat_id: Optional[int]) -> None:
        """Set active chat without reloading."""
        self._current_chat_id = chat_id
        for section in self._section_widgets.values():
            section.set_current_chat(chat_id)

    def set_current(self, chat_id: Optional[int]) -> None:
        """Alias for set_current_chat (compatibility with ChatWorkspace)."""
        self.set_current_chat(chat_id)

    def get_first_chat_id(self) -> Optional[int]:
        """Return first chat_id from any section (for post-delete selection)."""
        for section in self._section_widgets.values():
            if section and hasattr(section, "_chat_widgets") and section._chat_widgets:
                return next(iter(section._chat_widgets.keys()), None)
        return None

    def contains_chat_id(self, chat_id: int) -> bool:
        """Return True if chat_id exists in the currently loaded chat list."""
        for section in self._section_widgets.values():
            if section and hasattr(section, "_chat_widgets") and chat_id in section._chat_widgets:
                return True
        return False

    def refresh(self) -> None:
        """Reload chat list (e.g. after persistence changes)."""
        self._load_chats()
