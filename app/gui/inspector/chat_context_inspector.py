"""
ChatContextInspector – Inspector-Inhalt für Chat-Kontext.

Zeigt Chat-Titel, Projekt, Topic, Modell, letzte Aktivität, Nachrichtenanzahl.
Ermöglicht Topic-Zuordnung per Dropdown.
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal


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


class ChatContextInspector(QWidget):
    """Inspector-Widget für Chat-Kontext."""

    topic_changed = Signal(int, object)  # chat_id, topic_id | None

    def __init__(
        self,
        session_id: str = "(keine)",
        chat_id: int | None = None,
        chat_title: str | None = None,
        model: str = "(wird geladen)",
        context_status: str = "Bereit",
        message_count: int = 0,
        project_id: int | None = None,
        project_name: str | None = None,
        topic_id: int | None = None,
        topic_name: str | None = None,
        last_activity: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("chatContextInspector")
        self._session_id = session_id
        self._chat_id = chat_id
        self._chat_title = chat_title or "Neuer Chat"
        self._model = model
        self._context_status = context_status
        self._message_count = message_count
        self._project_id = project_id
        self._project_name = project_name
        self._topic_id = topic_id
        self._topic_name = topic_name
        self._last_activity = last_activity or "—"
        self._topic_combo: QComboBox | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Chat-Titel
        title_group = QGroupBox("Chat")
        title_layout = QVBoxLayout(title_group)
        title_label = QLabel(self._chat_title)
        title_label.setObjectName("inspectorPrimaryValue")
        title_label.setWordWrap(True)
        title_layout.addWidget(title_label)
        layout.addWidget(title_group)

        # Projekt (falls zugeordnet)
        if self._project_name:
            proj_group = QGroupBox("Projekt")
            proj_layout = QVBoxLayout(proj_group)
            proj_label = QLabel(self._project_name)
            proj_label.setWordWrap(True)
            proj_layout.addWidget(proj_label)
            layout.addWidget(proj_group)

        # Topic (mit Zuordnungs-Dropdown)
        topic_group = QGroupBox("Topic")
        topic_layout = QVBoxLayout(topic_group)
        if self._project_id and self._chat_id is not None:
            self._topic_combo = QComboBox()
            self._topic_combo.setObjectName("topicCombo")
            self._populate_topic_combo()
            self._topic_combo.currentIndexChanged.connect(self._on_topic_combo_changed)
            topic_layout.addWidget(self._topic_combo)
        else:
            topic_label = QLabel(self._topic_name or "—")
            topic_layout.addWidget(topic_label)
        layout.addWidget(topic_group)

        # Letzte Aktivität
        activity_group = QGroupBox("Letzte Aktivität")
        activity_layout = QVBoxLayout(activity_group)
        activity_label = QLabel(self._last_activity)
        activity_layout.addWidget(activity_label)
        layout.addWidget(activity_group)

        # Kontext
        context_group = QGroupBox("Session")
        context_layout = QVBoxLayout(context_group)
        context_label = QLabel(self._session_id)
        context_layout.addWidget(context_label)
        layout.addWidget(context_group)

        # Modell
        model_group = QGroupBox("Modell")
        model_layout = QVBoxLayout(model_group)
        model_label = QLabel(self._model)
        model_layout.addWidget(model_label)
        layout.addWidget(model_group)

        # Kontextstatus
        status_group = QGroupBox("Kontextstatus")
        status_layout = QVBoxLayout(status_group)
        status_label = QLabel(self._context_status)
        status_label.setObjectName("panelStatus")
        status_layout.addWidget(status_label)
        layout.addWidget(status_group)

        # Nachrichtenanzahl
        count_group = QGroupBox("Nachrichten")
        count_layout = QVBoxLayout(count_group)
        count_label = QLabel(f"{self._message_count} Nachrichten")
        count_layout.addWidget(count_label)
        layout.addWidget(count_group)

        layout.addStretch()

    def _populate_topic_combo(self) -> None:
        """Füllt das Topic-Dropdown mit Topics des Projekts."""
        if not self._topic_combo or not self._project_id:
            return
        self._topic_combo.blockSignals(True)
        self._topic_combo.clear()
        self._topic_combo.addItem("Ungruppiert", None)
        try:
            from app.services.topic_service import get_topic_service
            topics = get_topic_service().list_topics_for_project(self._project_id)
            for t in topics:
                self._topic_combo.addItem(t.get("name", "Topic"), t.get("id"))
        except Exception:
            pass
        idx = self._topic_combo.findData(self._topic_id)
        if idx >= 0:
            self._topic_combo.setCurrentIndex(idx)
        else:
            self._topic_combo.setCurrentIndex(0)
        self._topic_combo.blockSignals(False)

    def _on_topic_combo_changed(self) -> None:
        """Topic-Zuordnung geändert."""
        if not self._topic_combo or self._chat_id is None or self._project_id is None:
            return
        topic_id = self._topic_combo.currentData()
        try:
            from app.services.chat_service import get_chat_service
            get_chat_service().move_chat_to_topic(self._project_id, self._chat_id, topic_id)
            self.topic_changed.emit(self._chat_id, topic_id)
        except Exception:
            pass
