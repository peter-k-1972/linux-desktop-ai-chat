"""
ChatDetailsPanel – Collapsible right-side panel for active chat metadata and quick actions.

User-facing productivity panel. Metadata clearly grouped.
Main chat area remains primary.
"""

from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QScrollArea,
    QGroupBox,
    QComboBox,
    QInputDialog,
)
from PySide6.QtCore import Qt, Signal

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


def _format_datetime(ts) -> str:
    if ts is None:
        return "—"
    try:
        if hasattr(ts, "strftime"):
            return ts.strftime("%d.%m.%Y %H:%M")
        s = str(ts)
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(ts)[:16] if ts else "—"


class ChatDetailsPanel(QFrame):
    """
    Collapsible right-side panel showing active chat metadata and quick actions.

    Metadata: title, project, topic, model, agent (aus letzter Assistant-Nachricht),
    created at, updated at.
    Quick actions: rename, move to topic, pin/unpin, archive/unarchive.
    """

    chat_updated = Signal()  # Emitted when any action changes the chat

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatDetailsPanel")
        self.setMinimumWidth(200)
        self.setMaximumWidth(320)
        self._expanded = True
        self._chat_id: Optional[int] = None
        self._project_id: Optional[int] = None
        self._topic_id: Optional[int] = None
        self._is_pinned = False
        self._is_archived = False
        self._get_model = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Collapsible header
        self._header = QFrame()
        self._header.setObjectName("chatDetailsHeader")
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(12, 10, 12, 10)
        self._collapse_icon = QLabel("◀")
        self._collapse_icon.setStyleSheet("font-size: 11px; color: #64748b;")
        header_layout.addWidget(self._collapse_icon)
        self._header_label = QLabel("Chat-Details")
        self._header_label.setStyleSheet(
            "font-size: 13px; font-weight: 600; color: #374151;"
        )
        header_layout.addWidget(self._header_label)
        header_layout.addStretch()
        self._header.setStyleSheet("""
            #chatDetailsHeader {
                background: #f8fafc;
                border-left: 1px solid #e2e8f0;
            }
            #chatDetailsHeader:hover { background: #f1f5f9; }
        """)
        self._header.mousePressEvent = self._on_header_clicked
        layout.addWidget(self._header)

        # Content (scrollable)
        self._content = QWidget()
        self._content.setObjectName("chatDetailsContent")
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        # Metadata group
        self._meta_group = QGroupBox("Metadaten")
        self._meta_group.setStyleSheet(
            "QGroupBox { font-weight: 600; color: #475569; font-size: 11px; }"
        )
        meta_layout = QVBoxLayout(self._meta_group)
        meta_layout.setSpacing(6)

        self._title_label = QLabel("—")
        self._title_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #1f2937;")
        self._title_label.setWordWrap(True)
        meta_layout.addWidget(self._title_label)

        self._project_label = QLabel("Projekt: —")
        self._project_label.setStyleSheet("font-size: 12px; color: #64748b;")
        self._project_label.setWordWrap(True)
        meta_layout.addWidget(self._project_label)

        self._topic_combo = QComboBox()
        self._topic_combo.setObjectName("detailsTopicCombo")
        self._topic_combo.setStyleSheet("""
            #detailsTopicCombo {
                padding: 6px 10px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 12px;
            }
        """)
        self._topic_combo.currentIndexChanged.connect(self._on_topic_changed)
        meta_layout.addWidget(self._topic_combo)

        self._model_label = QLabel("Modell: —")
        self._model_label.setStyleSheet("font-size: 12px; color: #64748b;")
        meta_layout.addWidget(self._model_label)

        self._agent_label = QLabel("Agent: —")
        self._agent_label.setStyleSheet("font-size: 12px; color: #64748b;")
        meta_layout.addWidget(self._agent_label)

        self._created_label = QLabel("Erstellt: —")
        self._created_label.setStyleSheet("font-size: 12px; color: #64748b;")
        meta_layout.addWidget(self._created_label)

        self._updated_label = QLabel("Aktualisiert: —")
        self._updated_label.setStyleSheet("font-size: 12px; color: #64748b;")
        meta_layout.addWidget(self._updated_label)

        content_layout.addWidget(self._meta_group)

        self._invocation_group = QGroupBox("Letzter Modellaufruf")
        self._invocation_group.setStyleSheet(
            "QGroupBox { font-weight: 600; color: #475569; font-size: 11px; }"
        )
        inv_layout = QVBoxLayout(self._invocation_group)
        inv_layout.setSpacing(6)
        self._invocation_title = QLabel("—")
        self._invocation_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #1f2937;")
        self._invocation_title.setWordWrap(True)
        inv_layout.addWidget(self._invocation_title)
        self._invocation_status = QLabel("")
        self._invocation_status.setStyleSheet("font-size: 12px; color: #64748b;")
        self._invocation_status.setWordWrap(True)
        inv_layout.addWidget(self._invocation_status)
        self._invocation_details = QLabel("")
        self._invocation_details.setStyleSheet("font-size: 11px; color: #475569;")
        self._invocation_details.setWordWrap(True)
        inv_layout.addWidget(self._invocation_details)
        content_layout.addWidget(self._invocation_group)

        # Quick actions group
        self._actions_group = QGroupBox("Aktionen")
        self._actions_group.setStyleSheet(
            "QGroupBox { font-weight: 600; color: #475569; font-size: 11px; }"
        )
        actions_layout = QVBoxLayout(self._actions_group)
        actions_layout.setSpacing(6)

        self._btn_rename = QPushButton("Umbenennen")
        self._btn_rename.setIcon(IconManager.get(IconRegistry.EDIT, size=14))
        self._style_action_btn(self._btn_rename)
        self._btn_rename.clicked.connect(self._on_rename)
        actions_layout.addWidget(self._btn_rename)

        self._btn_pin = QPushButton("Anheften")
        self._btn_pin.setIcon(IconManager.get(IconRegistry.PIN, size=14))
        self._style_action_btn(self._btn_pin)
        self._btn_pin.clicked.connect(self._on_toggle_pin)
        actions_layout.addWidget(self._btn_pin)

        self._btn_archive = QPushButton("Archivieren")
        self._style_action_btn(self._btn_archive)
        self._btn_archive.clicked.connect(self._on_toggle_archive)
        actions_layout.addWidget(self._btn_archive)

        content_layout.addWidget(self._actions_group)
        content_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(self._content)
        layout.addWidget(scroll, 1)

        self.setStyleSheet("""
            #chatDetailsPanel {
                background: #ffffff;
                border-left: 1px solid #e2e8f0;
            }
        """)

    def _style_action_btn(self, btn: QPushButton) -> None:
        btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover { background: #e2e8f0; }
            QPushButton:disabled { background: #f8fafc; color: #94a3b8; }
        """)

    def _on_header_clicked(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_expanded()

    def toggle_expanded(self) -> None:
        self._expanded = not self._expanded
        self._content.setVisible(self._expanded)
        self._header_label.setVisible(self._expanded)
        self._collapse_icon.setText("◀" if self._expanded else "▶")
        if self._expanded:
            self.setMaximumWidth(320)
            self.setMinimumWidth(200)
        else:
            self.setMaximumWidth(40)
            self.setMinimumWidth(40)

    def set_expanded(self, expanded: bool) -> None:
        if self._expanded != expanded:
            self.toggle_expanded()

    def set_get_model_callback(self, callback) -> None:
        """Set callback to get current model name: () -> str."""
        self._get_model = callback

    def update_chat(
        self,
        chat_id: Optional[int],
        chat_title: str,
        project_id: Optional[int],
        project_name: Optional[str],
        topic_id: Optional[int],
        topic_name: Optional[str],
        created_at,
        last_activity,
        *,
        last_assistant_agent: Optional[str] = None,
        is_pinned: bool = False,
        is_archived: bool = False,
    ) -> None:
        """Update panel with active chat data."""
        self._chat_id = chat_id
        self._project_id = project_id
        self._topic_id = topic_id
        self._is_pinned = is_pinned
        self._is_archived = is_archived

        has_chat = chat_id is not None
        self._meta_group.setEnabled(has_chat)
        self._actions_group.setEnabled(has_chat)

        self._title_label.setText(chat_title or "—")
        self._project_label.setText(f"Projekt: {project_name or '—'}")
        model = (self._get_model() or "—") if self._get_model else "—"
        self._model_label.setText(f"Modell: {model}")
        if not has_chat:
            self._agent_label.setText("Agent: —")
            self._agent_label.setToolTip("")
        elif last_assistant_agent:
            self._agent_label.setText(f"Agent (letzte Antwort): {last_assistant_agent}")
            self._agent_label.setToolTip("")
        else:
            self._agent_label.setText("Agent: nicht vermerkt")
            self._agent_label.setToolTip(
                "Wird nur angezeigt, wenn eine Assistant-Nachricht mit gespeicherter "
                "Agentenkennung existiert (z. B. Agent Tasks). Im normalen Modell-Chat "
                "bleibt dieses Feld leer."
            )
        self._created_label.setText(f"Erstellt: {_format_datetime(created_at)}")
        self._updated_label.setText(f"Aktualisiert: {_format_datetime(last_activity)}")

        # Topic combo
        self._topic_combo.blockSignals(True)
        self._topic_combo.clear()
        self._topic_combo.addItem("Ungruppiert", None)
        if project_id and has_chat:
            try:
                from app.services.topic_service import get_topic_service
                for t in get_topic_service().list_topics_for_project(project_id):
                    tid = t.get("id")
                    tname = t.get("name", "Topic")
                    if tid is not None:
                        self._topic_combo.addItem(tname, tid)
            except Exception:
                pass
        idx = self._topic_combo.findData(topic_id)
        self._topic_combo.setCurrentIndex(max(0, idx))
        self._topic_combo.blockSignals(False)

        # Pin/Archive buttons
        self._btn_pin.setText("Lösen" if is_pinned else "Anheften")
        self._btn_pin.setEnabled(not is_archived)
        self._btn_archive.setText("Reaktivieren" if is_archived else "Archivieren")

    def _on_topic_changed(self) -> None:
        if self._chat_id is None or self._project_id is None:
            return
        topic_id = self._topic_combo.currentData()
        try:
            from app.services.chat_service import get_chat_service
            get_chat_service().move_chat_to_topic(
                self._project_id, self._chat_id, topic_id
            )
            self._topic_id = topic_id
            self.chat_updated.emit()
        except Exception:
            pass

    def _on_rename(self) -> None:
        if self._chat_id is None:
            return
        current = self._title_label.text()
        if current == "—":
            current = "Neuer Chat"
        title, ok = QInputDialog.getText(
            self, "Chat umbenennen", "Neuer Titel:", text=current
        )
        if not ok or not (title := (title or "").strip()):
            return
        try:
            from app.services.chat_service import get_chat_service
            get_chat_service().save_chat_title(self._chat_id, title)
            self._title_label.setText(title)
            self.chat_updated.emit()
        except Exception:
            pass

    def _on_toggle_pin(self) -> None:
        if self._chat_id is None or self._project_id is None:
            return
        try:
            from app.services.chat_service import get_chat_service
            get_chat_service().set_chat_pinned(
                self._project_id, self._chat_id, not self._is_pinned
            )
            self._is_pinned = not self._is_pinned
            self.chat_updated.emit()
        except Exception:
            pass

    def _on_toggle_archive(self) -> None:
        if self._chat_id is None or self._project_id is None:
            return
        try:
            from app.services.chat_service import get_chat_service
            get_chat_service().set_chat_archived(
                self._project_id, self._chat_id, not self._is_archived
            )
            self._is_archived = not self._is_archived
            self.chat_updated.emit()
        except Exception:
            pass

    def clear(self) -> None:
        """Clear panel when no chat selected."""
        self.update_chat(
            None, "—", None, "—", None, "—",
            None, None,
            last_assistant_agent=None,
            is_pinned=False, is_archived=False,
        )
        self.set_last_invocation_view(None)

    def set_last_invocation_view(self, view: Optional[dict]) -> None:
        """
        Strukturierte Anzeige aus app.services.model_invocation_display.build_chat_invocation_view.
        view: None leert die Gruppe.
        """
        if not view:
            self._invocation_title.setText("—")
            self._invocation_status.setText("")
            self._invocation_details.setText("")
            self._invocation_title.setStyleSheet(
                "font-size: 12px; font-weight: 600; color: #1f2937;"
            )
            return
        title = view.get("title") or "Letzter Modellaufruf"
        status = view.get("status_line") or ""
        lines = view.get("detail_lines") or []
        hint = (view.get("style_hint") or "neutral").lower()

        self._invocation_title.setText(title)
        self._invocation_status.setText(status)
        self._invocation_details.setText("\n".join(str(x) for x in lines if x))

        base_title = "font-size: 12px; font-weight: 600; color: #1f2937;"
        base_status = "font-size: 12px; color: #64748b;"
        if hint == "warn":
            base_title = "font-size: 12px; font-weight: 600; color: #b45309;"
            base_status = "font-size: 12px; color: #b45309;"
        elif hint == "block":
            base_title = "font-size: 12px; font-weight: 600; color: #991b1b;"
            base_status = "font-size: 12px; color: #991b1b;"
        elif hint in ("error",):
            base_title = "font-size: 12px; font-weight: 600; color: #b91c1c;"
            base_status = "font-size: 12px; color: #b91c1c;"
        elif hint == "cancel":
            base_title = "font-size: 12px; font-weight: 600; color: #6b21a8;"
            base_status = "font-size: 12px; color: #6b21a8;"
        elif hint == "ok":
            base_title = "font-size: 12px; font-weight: 600; color: #166534;"
            base_status = "font-size: 12px; color: #166534;"
        self._invocation_title.setStyleSheet(base_title)
        self._invocation_status.setStyleSheet(base_status)
