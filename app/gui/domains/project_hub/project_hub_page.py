"""
ProjectHubPage – Overview screen for the active project.

Displays project name, statistics, recent sections, and quick actions.
Reacts to project_context_changed to reload data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
    QGridLayout,
)
from PySide6.QtCore import Qt

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


def _format_date(ts: Any) -> str:
    if ts is None:
        return ""
    try:
        if hasattr(ts, "strftime"):
            return ts.strftime("%d.%m. %H:%M")
        s = str(ts)
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%d.%m. %H:%M")
    except Exception:
        return str(ts)[:16] if ts else ""


def _make_clickable_row(
    title: str, ts_str: str, icon_name: str, callback
) -> QPushButton:
    """Creates a clickable row."""
    row = QPushButton()
    row.setCursor(Qt.CursorShape.PointingHandCursor)
    row.setFlat(True)
    row.clicked.connect(callback)
    row.setObjectName("hubActivityRow")
    row.setStyleSheet("""
        #hubActivityRow {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 8px 10px;
            text-align: left;
        }
        #hubActivityRow:hover { background: rgba(0, 0, 0, 0.05); }
    """)
    layout = QHBoxLayout(row)
    layout.setContentsMargins(8, 6, 8, 6)
    layout.setSpacing(10)
    icon = IconManager.get(icon_name, size=16)
    if icon:
        icon_lbl = QLabel()
        icon_lbl.setPixmap(icon.pixmap(16, 16))
        layout.addWidget(icon_lbl)
    text_layout = QVBoxLayout()
    text_layout.setSpacing(2)
    lbl = QLabel((title or "Unbenannt")[:50] + ("…" if len(title or "") > 50 else ""))
    lbl.setStyleSheet("font-size: 13px;")
    text_layout.addWidget(lbl)
    if ts_str:
        ts_lbl = QLabel(ts_str)
        ts_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        text_layout.addWidget(ts_lbl)
    layout.addLayout(text_layout, 1)
    return row


class ProjectHubPage(QWidget):
    """
    Project Hub – overview of the active project.

    - Project name
    - Statistics: chats, knowledge sources, prompts
    - Sections: Recent Chats, Recent Knowledge, Recent Prompts
    - Quick Actions: + New Chat, + Add Knowledge Source, + Create Prompt, + Create Agent

    Reacts to project_context_changed to reload data.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectHubPage")
        self._project_id: Optional[int] = None
        self._setup_ui()
        self._connect_project_context()
        self._load_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Empty state
        self._empty_label = QLabel("Kein Projekt ausgewählt.\nBitte wählen Sie ein Projekt im Project Switcher.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #64748b; font-size: 15px; padding: 48px;")
        layout.addWidget(self._empty_label)

        # Content container
        self._content = QWidget()
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # Project name
        self._name_label = QLabel()
        self._name_label.setObjectName("projectHubName")
        self._name_label.setStyleSheet("""
            #projectHubName {
                font-size: 24px;
                font-weight: 600;
                color: #0f172a;
            }
        """)
        content_layout.addWidget(self._name_label)

        # Statistics
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        self._stat_chats = self._make_stat_card("Chats", IconRegistry.CHAT)
        self._stat_sources = self._make_stat_card("Knowledge Sources", IconRegistry.KNOWLEDGE)
        self._stat_prompts = self._make_stat_card("Prompts", IconRegistry.PROMPT_STUDIO)
        stats_layout.addWidget(self._stat_chats, 1)
        stats_layout.addWidget(self._stat_sources, 1)
        stats_layout.addWidget(self._stat_prompts, 1)
        content_layout.addLayout(stats_layout)

        # Sections: Recent Chats, Recent Knowledge, Recent Prompts
        sections_layout = QHBoxLayout()
        sections_layout.setSpacing(16)

        self._recent_chats = self._make_section_widget("Recent Chats", IconRegistry.CHAT)
        self._recent_knowledge = self._make_section_widget("Recent Knowledge", IconRegistry.KNOWLEDGE)
        self._recent_prompts = self._make_section_widget("Recent Prompts", IconRegistry.PROMPT_STUDIO)

        sections_layout.addWidget(self._recent_chats, 1)
        sections_layout.addWidget(self._recent_knowledge, 1)
        sections_layout.addWidget(self._recent_prompts, 1)
        content_layout.addLayout(sections_layout)

        # Quick Actions
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #64748b;")
        content_layout.addWidget(actions_label)

        actions_grid = QGridLayout()
        self._btn_new_chat = self._make_action_btn("+ New Chat", IconRegistry.CHAT, self._on_new_chat)
        self._btn_add_source = self._make_action_btn("+ Add Knowledge Source", IconRegistry.KNOWLEDGE, self._on_add_source)
        self._btn_new_prompt = self._make_action_btn("+ Create Prompt", IconRegistry.PROMPT_STUDIO, self._on_new_prompt)
        self._btn_new_agent = self._make_action_btn("+ Create Agent", IconRegistry.AGENTS, self._on_new_agent)
        actions_grid.addWidget(self._btn_new_chat, 0, 0)
        actions_grid.addWidget(self._btn_add_source, 0, 1)
        actions_grid.addWidget(self._btn_new_prompt, 1, 0)
        actions_grid.addWidget(self._btn_new_agent, 1, 1)
        content_layout.addLayout(actions_grid)

        self._content.hide()
        layout.addWidget(self._content, 1)

    def _make_stat_card(self, label: str, icon_name: str) -> QFrame:
        card = QFrame()
        card.setObjectName("hubStatCard")
        card.setStyleSheet("""
            #hubStatCard {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 16px;
            }
        """)
        layout = QHBoxLayout(card)
        layout.setSpacing(10)
        icon = IconManager.get(icon_name, size=20)
        if icon:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(icon.pixmap(20, 20))
            layout.addWidget(icon_lbl)
        inner = QVBoxLayout()
        inner.setSpacing(2)
        value_label = QLabel("0")
        value_label.setStyleSheet("font-size: 20px; font-weight: 600; color: #0f172a;")
        inner.addWidget(value_label)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        inner.addWidget(lbl)
        layout.addLayout(inner, 1)
        card._value_label = value_label
        return card

    def _make_section_widget(self, title: str, icon_name: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("hubSection")
        frame.setStyleSheet("""
            #hubSection {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        icon = IconManager.get(icon_name, size=16)
        if icon:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(icon.pixmap(16, 16))
            header.addWidget(icon_lbl)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b;")
        header.addWidget(lbl)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        content = QWidget()
        frame._items_layout = QVBoxLayout(content)
        frame._items_layout.setContentsMargins(0, 0, 0, 0)
        frame._items_layout.setSpacing(4)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        frame._empty = QLabel("Keine Einträge")
        frame._empty.setStyleSheet("font-size: 12px; color: #94a3b8;")
        frame._items_layout.addWidget(frame._empty)
        return frame

    def _make_action_btn(self, label: str, icon_name: str, callback) -> QPushButton:
        btn = QPushButton(label)
        btn.setIcon(IconManager.get(icon_name, size=18))
        btn.setObjectName("hubQuickAction")
        btn.setStyleSheet("""
            #hubQuickAction {
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 16px;
                color: #334155;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
            }
            #hubQuickAction:hover {
                background: #e2e8f0;
                border-color: #cbd5e1;
            }
        """)
        btn.clicked.connect(callback)
        return btn

    def _connect_project_context(self) -> None:
        """Subscribe to project_context_changed."""
        from app.gui.events.project_events import subscribe_project_events
        subscribe_project_events(self._on_project_context_changed)

    def _on_project_context_changed(self, payload: dict) -> None:
        """Reload data when project changes."""
        self._load_data()

    def _load_data(self) -> None:
        """Load project data from ProjectContextManager."""
        from app.core.context.project_context_manager import get_project_context_manager
        mgr = get_project_context_manager()
        self._project_id = mgr.get_active_project_id()
        project = mgr.get_active_project()

        if not project or not self._project_id:
            self._empty_label.show()
            self._content.hide()
            return

        self._empty_label.hide()
        self._content.show()

        self._name_label.setText(project.get("name", "Projekt"))

        try:
            from app.services.project_service import get_project_service
            svc = get_project_service()
            chat_count = svc.count_chats_of_project(self._project_id)
            source_count = len(svc.get_project_sources(self._project_id))
            prompt_count = svc.count_prompts_of_project(self._project_id)
        except Exception:
            chat_count = 0
            source_count = 0
            prompt_count = 0

        self._stat_chats._value_label.setText(str(chat_count))
        self._stat_sources._value_label.setText(str(source_count))
        self._stat_prompts._value_label.setText(str(prompt_count))

        activity: Dict[str, List] = {}
        try:
            from app.services.project_service import get_project_service
            activity = get_project_service().get_recent_project_activity(
                self._project_id, chat_limit=5, prompt_limit=5
            )
        except Exception:
            pass

        def chat_title_ts(c):
            return (c.get("title", "Chat"), c.get("last_activity") or c.get("created_at"))
        self._populate_section(
            self._recent_chats,
            activity.get("recent_chats", []),
            chat_title_ts,
            lambda c: c.get("id"),
            IconRegistry.CHAT,
            self._on_chat_clicked,
        )
        def source_title(s):
            name = s.get("name", s.get("path", "Source")) if isinstance(s, dict) else str(s)
            return (name, None)
        self._populate_section(
            self._recent_knowledge,
            activity.get("sources", [])[:5],
            source_title,
            lambda s: s.get("path", "") if isinstance(s, dict) else "",
            IconRegistry.KNOWLEDGE,
            self._on_source_clicked,
        )
        def prompt_title_ts(p):
            title = getattr(p, "title", None) or (p.get("title") if isinstance(p, dict) else "Prompt")
            ts = getattr(p, "updated_at", None) or (p.get("updated_at") if isinstance(p, dict) else None)
            return (title, ts)
        self._populate_section(
            self._recent_prompts,
            activity.get("recent_prompts", []),
            prompt_title_ts,
            lambda p: getattr(p, "id", None) or (p.get("id") if isinstance(p, dict) else None),
            IconRegistry.PROMPT_STUDIO,
            self._on_prompt_clicked,
        )

    def _populate_section(
        self,
        section: QFrame,
        items: List,
        title_ts_fn,
        id_fn,
        icon_name: str,
        click_cb,
    ) -> None:
        """Populate a section with items."""
        while section._items_layout.count():
            item = section._items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not items:
            empty = QLabel("Keine Einträge")
            empty.setStyleSheet("font-size: 12px; color: #94a3b8;")
            section._items_layout.addWidget(empty)
            return

        for it in items:
            title, ts = title_ts_fn(it) if callable(title_ts_fn) else (str(it), None)
            item_id = id_fn(it) if callable(id_fn) else None
            row = _make_clickable_row(
                title or "—",
                _format_date(ts) if ts else "",
                icon_name,
                lambda iid=item_id: click_cb(iid),
            )
            section._items_layout.addWidget(row)

    def _find_workspace_host(self) -> Optional[QWidget]:
        """Find WorkspaceHost in parent hierarchy."""
        p = self
        while p:
            if hasattr(p, "show_area") and hasattr(p, "_area_to_index"):
                return p
            p = p.parent() if hasattr(p, "parent") else None
        return None

    def _ensure_project_active(self) -> None:
        """Ensure current project is active in ProjectContextManager."""
        if self._project_id is None:
            return
        from app.core.context.project_context_manager import get_project_context_manager
        if get_project_context_manager().get_active_project_id() != self._project_id:
            get_project_context_manager().set_active_project(self._project_id)

    def _on_chat_clicked(self, chat_id: int) -> None:
        self._ensure_project_active()
        try:
            from app.gui.domains.operations.operations_context import set_pending_context
            set_pending_context({"chat_id": chat_id})
        except Exception:
            pass
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_chat")

    def _on_source_clicked(self, path: str) -> None:
        self._ensure_project_active()
        try:
            from app.gui.domains.operations.operations_context import set_pending_context
            set_pending_context({"source_path": path})
        except Exception:
            pass
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_knowledge")

    def _on_prompt_clicked(self, prompt_id: int) -> None:
        self._ensure_project_active()
        try:
            from app.gui.domains.operations.operations_context import set_pending_context
            set_pending_context({"prompt_id": prompt_id})
        except Exception:
            pass
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_prompt_studio")

    def _on_new_chat(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_chat")

    def _on_add_source(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_knowledge")

    def _on_new_prompt(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_prompt_studio")

    def _on_new_agent(self) -> None:
        self._ensure_project_active()
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea
            host.show_area(NavArea.OPERATIONS, "operations_agent_tasks")
