"""
EmptyStateWidget – wiederverwendbare Komponente für leere und Info-Zustände.

Unterstützt:
- optionales Icon
- Titel
- kurze Erklärung
- optionaler Zusatzhinweis
- visuell ruhige, produktartige Darstellung

Zustandsarten:
- leer / noch keine Daten
- kein Projekt ausgewählt
- Bereich noch nicht ausgebaut
- informativer Hinweis

Theme-verträglich: nutzt ObjectNames für QSS, keine harten Farbcodes.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.shared.layout_constants import (
    EMPTY_STATE_PADDING,
    EMPTY_STATE_PADDING_COMPACT,
    EMPTY_STATE_PADDING_COMPACT_V,
    EMPTY_STATE_SPACING,
    EMPTY_STATE_SPACING_COMPACT,
)


class EmptyStateWidget(QFrame):
    """
    Wiederverwendbare Empty-State-/Info-State-Karte.

    Nicht dramatisch, nicht fehlerhaft, klar und freundlich.
    """

    def __init__(
        self,
        title: str,
        description: str,
        *,
        icon: Optional[str] = None,
        hint: Optional[str] = None,
        compact: bool = False,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._compact = compact
        self.setObjectName("emptyStateWidget")
        if compact:
            self.setProperty("compact", "true")
        self._setup_ui(title, description, icon=icon, hint=hint)

    def _setup_ui(
        self,
        title: str,
        description: str,
        *,
        icon: Optional[str] = None,
        hint: Optional[str] = None,
    ) -> None:
        layout = QVBoxLayout(self)
        if self._compact:
            layout.setContentsMargins(
                EMPTY_STATE_PADDING_COMPACT, EMPTY_STATE_PADDING_COMPACT_V,
                EMPTY_STATE_PADDING_COMPACT, EMPTY_STATE_PADDING_COMPACT_V,
            )
            layout.setSpacing(EMPTY_STATE_SPACING_COMPACT)
        else:
            layout.setContentsMargins(
                EMPTY_STATE_PADDING, EMPTY_STATE_PADDING, EMPTY_STATE_PADDING, EMPTY_STATE_PADDING
            )
            layout.setSpacing(EMPTY_STATE_SPACING)

        if icon and not self._compact:
            try:
                qicon = IconManager.get(icon, size=32)
                if not qicon.isNull():
                    icon_widget = QLabel()
                    icon_widget.setObjectName("emptyStateIcon")
                    icon_widget.setPixmap(qicon.pixmap(32, 32))
                    icon_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(icon_widget)
            except Exception:
                pass

        self._title_label = QLabel(title)
        self._title_label.setObjectName("emptyStateTitle")
        self._title_label.setWordWrap(True)
        self._title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter if self._compact else Qt.AlignmentFlag.AlignLeft
        )
        layout.addWidget(self._title_label)

        self._desc_label = QLabel(description)
        self._desc_label.setObjectName("emptyStateDescription")
        self._desc_label.setWordWrap(True)
        self._desc_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter if self._compact else Qt.AlignmentFlag.AlignLeft
        )
        layout.addWidget(self._desc_label)

        if hint and not self._compact:
            self._hint_label = QLabel(hint)
            self._hint_label.setObjectName("emptyStateHint")
            self._hint_label.setWordWrap(True)
            layout.addWidget(self._hint_label)

        if self._compact:
            layout.insertStretch(0, 1)
            layout.addStretch(1)

    def set_content(
        self,
        title: str,
        description: str,
        *,
        icon: Optional[str] = None,
        hint: Optional[str] = None,
    ) -> None:
        """Aktualisiert Titel, Beschreibung und optionale Felder."""
        self._title_label.setText(title)
        self._desc_label.setText(description)
        if hasattr(self, "_hint_label"):
            if hint:
                self._hint_label.setText(hint)
                self._hint_label.show()
            else:
                self._hint_label.hide()
