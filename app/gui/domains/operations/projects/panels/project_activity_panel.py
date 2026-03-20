"""
ProjectActivityPanel – Letzte Aktivität im Projekt.

Drei Blöcke: Recent Chats, Recent Sources, Recent Prompts.
Klickbar, öffnet jeweiligen Workspace.
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QGridLayout,
)
from PySide6.QtCore import Qt, Signal

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


def _format_date(ts) -> str:
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


def _make_clickable_row(title: str, ts_str: str, icon_name: str, callback) -> QWidget:
    """Erstellt eine klickbare Zeile."""
    row = QPushButton()
    row.setCursor(Qt.CursorShape.PointingHandCursor)
    row.setFlat(True)
    row.clicked.connect(callback)
    row.setObjectName("activityRow")
    row.setStyleSheet("""
        #activityRow {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 8px 10px;
            text-align: left;
        }
        #activityRow:hover { background: rgba(255, 255, 255, 0.06); }
    """)
    layout = QHBoxLayout(row)
    layout.setContentsMargins(8, 6, 8, 6)
    layout.setSpacing(10)
    icon = IconManager.get(icon_name, size=16)
    icon_lbl = QLabel()
    icon_lbl.setPixmap(icon.pixmap(16, 16))
    layout.addWidget(icon_lbl)
    text_layout = QVBoxLayout()
    text_layout.setSpacing(2)
    lbl = QLabel((title or "Unbenannt")[:50] + ("…" if len(title or "") > 50 else ""))
    lbl.setStyleSheet("font-size: 13px; color: #f1f1f4;")
    text_layout.addWidget(lbl)
    if ts_str:
        ts_lbl = QLabel(ts_str)
        ts_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        text_layout.addWidget(ts_lbl)
    layout.addLayout(text_layout, 1)
    return row


class ProjectActivityPanel(QFrame):
    """Panel mit letzter Projektaktivität in drei Blöcken."""

    chat_clicked = Signal(int)
    prompt_clicked = Signal(int)
    source_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectActivityPanel")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(20)
        scroll.setWidget(self._content)
        layout.addWidget(scroll, 1)

        self._empty_label = QLabel("Keine Aktivität in diesem Projekt.")
        self._empty_label.setStyleSheet("color: #64748b; font-size: 13px; padding: 24px;")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._chats_section = None
        self._sources_section = None
        self._prompts_section = None

        self.setStyleSheet("""
            #projectActivityPanel {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 16px;
            }
        """)

    def set_activity(
        self,
        recent_chats: list,
        recent_prompts: list,
        sources: list,
    ) -> None:
        """Aktualisiert die Aktivitätsblöcke."""
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        has_any = bool(recent_chats or recent_prompts or sources)
        if not has_any:
            self._content_layout.addWidget(self._empty_label)
            return

        self._empty_label.hide()

        if recent_chats:
            section = self._make_section("Letzte Chats", IconRegistry.CHAT)
            self._content_layout.addWidget(section)
            for c in recent_chats[:5]:
                title = c.get("title", "Chat") or "Unbenannt"
                ts = c.get("last_activity") or c.get("created_at")
                chat_id = c.get("id")
                row = _make_clickable_row(
                    title, _format_date(ts), IconRegistry.CHAT,
                    lambda cid=chat_id: self.chat_clicked.emit(cid),
                )
                self._content_layout.addWidget(row)

        if sources:
            section = self._make_section("Quellen / Knowledge", IconRegistry.KNOWLEDGE)
            self._content_layout.addWidget(section)
            for s in sources[:5]:
                name = s.get("name", s.get("path", "Quelle")) if isinstance(s, dict) else str(s)
                path = s.get("path", "") if isinstance(s, dict) else ""
                status = s.get("status", "") if isinstance(s, dict) else ""
                sub = f" · {status}" if status else ""
                row = _make_clickable_row(
                    (name or "Quelle") + sub, "", IconRegistry.KNOWLEDGE,
                    lambda p=path: self.source_clicked.emit(p),
                )
                self._content_layout.addWidget(row)

        if recent_prompts:
            section = self._make_section("Letzte Prompts", IconRegistry.PROMPT_STUDIO)
            self._content_layout.addWidget(section)
            for p in recent_prompts[:5]:
                title = getattr(p, "title", None) or (p.get("title") if isinstance(p, dict) else "Prompt")
                ts = getattr(p, "updated_at", None) or (p.get("updated_at") if isinstance(p, dict) else None)
                pid = getattr(p, "id", None) or (p.get("id") if isinstance(p, dict) else None)
                row = _make_clickable_row(
                    title, _format_date(ts), IconRegistry.PROMPT_STUDIO,
                    lambda prid=pid: self.prompt_clicked.emit(prid),
                )
                self._content_layout.addWidget(row)

    def _make_section(self, title: str, icon_name: str) -> QWidget:
        """Erstellt einen Abschnitts-Header."""
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(8)
        icon = IconManager.get(icon_name, size=16)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(icon.pixmap(16, 16))
        layout.addWidget(icon_lbl)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #94a3b8;")
        layout.addWidget(lbl)
        return w
