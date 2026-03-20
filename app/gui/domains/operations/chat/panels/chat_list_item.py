"""
ChatListItem – Einzelner Chat-Eintrag in der projektbezogenen Chat-Liste.

Zeigt Titel, letzte Aktivität, aktiven Zustand, optional Preview.
"""

from datetime import datetime, timedelta
from typing import Optional

from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal


def _format_relative_time(ts) -> str:
    """Formatiert Timestamp relativ: vor X Min, heute, gestern, etc."""
    if ts is None:
        return ""
    try:
        if hasattr(ts, "date"):
            dt = ts
        else:
            s = str(ts)
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        now = datetime.now()
        if dt.tzinfo:
            now = datetime.now(dt.tzinfo)
        delta = now - dt
        if delta < timedelta(minutes=1):
            return "gerade eben"
        if delta < timedelta(hours=1):
            m = int(delta.total_seconds() / 60)
            return f"vor {m} Min"
        if delta < timedelta(hours=24) and dt.date() == now.date():
            h = int(delta.total_seconds() / 3600)
            return f"vor {h} Std"
        if dt.date() == (now - timedelta(days=1)).date():
            return "gestern"
        if delta < timedelta(days=7):
            return f"vor {delta.days} Tagen"
        return dt.strftime("%d.%m.")
    except Exception:
        return ""


# Alias für Kompatibilität mit ChatTopicSection und ui.chat
format_relative_time = _format_relative_time


class ChatListItemWidget(QFrame):
    """Klickbarer Chat-Eintrag mit Titel, Zeit und optionalem Preview."""

    context_menu_requested = Signal(int)  # chat_id

    def __init__(
        self,
        chat_id: int,
        title: str,
        last_activity: str,
        active: bool,
        parent=None,
        preview: Optional[str] = None,
    ):
        super().__init__(parent)
        self.setObjectName("chatListItem")
        self._chat_id = chat_id
        self._active = active
        self._setup_ui(title, last_activity, preview)

    def _setup_ui(self, title: str, time_str: str, preview: Optional[str] = None):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        self._title = QLabel((title or "Neuer Chat")[:60] + ("…" if len(title or "") > 60 else ""))
        self._title.setObjectName("chatItemTitle")
        self._title.setStyleSheet("font-size: 13px; font-weight: 500; color: #1f2937;")
        self._title.setWordWrap(True)
        layout.addWidget(self._title)

        if time_str:
            self._time = QLabel(time_str)
            self._time.setObjectName("chatItemTime")
            self._time.setStyleSheet("font-size: 11px; color: #64748b;")
            layout.addWidget(self._time)

        if preview and (preview := preview.strip()):
            preview_text = (preview[:80] + "…") if len(preview) > 80 else preview
            self._preview = QLabel(preview_text)
            self._preview.setObjectName("chatItemPreview")
            self._preview.setStyleSheet("font-size: 11px; color: #94a3b8;")
            self._preview.setWordWrap(True)
            layout.addWidget(self._preview)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            #chatListItem {
                background: transparent;
                border-radius: 8px;
                border: none;
            }
            #chatListItem:hover {
                background: #f1f5f9;
            }
            #chatListItem[active="true"] {
                background: #dbeafe;
                border-left: 3px solid #2563eb;
            }
            #chatListItem[active="true"] #chatItemTitle {
                color: #1e40af;
            }
        """)
        self.setProperty("active", self._active)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_active(self, active: bool) -> None:
        self._active = active
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def chat_id(self) -> int:
        return self._chat_id

    def contextMenuEvent(self, event) -> None:
        self.context_menu_requested.emit(self._chat_id)
