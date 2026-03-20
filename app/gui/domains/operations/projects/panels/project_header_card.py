"""
ProjectHeaderCard – Projektkopf für den Project Overview.

Projektname, Beschreibung, letzte Aktivität, Status.
"""

from datetime import datetime
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


def _format_date(ts: str | None) -> str:
    if not ts:
        return "—"
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(ts) if ts else "—"


class ProjectHeaderCard(QFrame):
    """Karte mit Projektkopf: Name, Beschreibung, Metadaten."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectHeaderCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        self._name_label = QLabel()
        self._name_label.setObjectName("projectHeaderName")
        self._name_label.setStyleSheet("""
            #projectHeaderName {
                font-size: 22px;
                font-weight: 600;
                color: #f1f1f4;
                letter-spacing: -0.02em;
            }
        """)
        layout.addWidget(self._name_label)

        self._meta_label = QLabel()
        self._meta_label.setObjectName("projectHeaderMeta")
        self._meta_label.setStyleSheet("""
            #projectHeaderMeta {
                font-size: 12px;
                color: #64748b;
            }
        """)
        layout.addWidget(self._meta_label)

        self._desc_label = QLabel()
        self._desc_label.setWordWrap(True)
        self._desc_label.setObjectName("projectHeaderDesc")
        self._desc_label.setStyleSheet("""
            #projectHeaderDesc {
                font-size: 13px;
                color: #94a3b8;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self._desc_label)

        self.setStyleSheet("""
            #projectHeaderCard {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
        """)

    def set_project(self, project: dict | None) -> None:
        """Aktualisiert den Inhalt."""
        if not project:
            self._name_label.setText("—")
            self._meta_label.setText("")
            self._desc_label.setText("")
            return
        name = project.get("name", "Unbenannt")
        desc = project.get("description", "") or "Keine Beschreibung."
        status = project.get("status", "active")
        created = project.get("created_at")
        updated = project.get("updated_at")
        self._name_label.setText(name)
        self._meta_label.setText(
            f"Erstellt: {_format_date(created)} · Geändert: {_format_date(updated)} · Status: {status}"
        )
        self._desc_label.setText(desc)
