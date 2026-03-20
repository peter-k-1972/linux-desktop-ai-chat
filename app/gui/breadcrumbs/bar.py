"""
BreadcrumbBar – UI-Komponente für Breadcrumb-Anzeige.

Icon > Text > Separator > Text
Minimalistisch, klickbar, theme-kompatibel.
"""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal

from app.gui.breadcrumbs.model import BreadcrumbItem, BreadcrumbAction
from app.gui.icons import IconManager


class BreadcrumbBar(QFrame):
    """
    Zeigt den aktuellen Breadcrumb-Pfad.
    Klickbare Items navigieren.
    """

    navigate_requested = Signal(str, str)  # area_id, workspace_id (workspace_id leer bei Area-Klick)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("breadcrumbBar")
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 8, 12, 8)
        self._layout.setSpacing(4)

    def set_path(self, items: list[BreadcrumbItem]) -> None:
        """Aktualisiert die Anzeige mit dem neuen Pfad."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for i, item in enumerate(items):
            if i > 0:
                sep = QLabel("›")
                sep.setObjectName("breadcrumbSeparator")
                self._layout.addWidget(sep)

            if item.action == BreadcrumbAction.DETAIL:
                lbl = QLabel(item.title)
                lbl.setObjectName("breadcrumbDetail")
                self._layout.addWidget(lbl)
            else:
                btn = QPushButton()
                btn.setObjectName("breadcrumbItem")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                if item.icon:
                    icon = IconManager.get(item.icon, size=16)
                    if not icon.isNull():
                        btn.setIcon(icon)
                btn.setText(item.title)
                btn.setProperty("_area_id", item.area_id or item.id)
                btn.setProperty("_workspace_id", item.id if item.action == BreadcrumbAction.WORKSPACE else "")
                btn.clicked.connect(lambda checked=False, b=btn: self._on_click(b))
                self._layout.addWidget(btn)

        self._layout.addStretch()

    def _on_click(self, btn: QPushButton) -> None:
        """Navigiert bei Klick."""
        area_id = btn.property("_area_id") or ""
        workspace_id = btn.property("_workspace_id") or ""
        if area_id:
            self.navigate_requested.emit(area_id, workspace_id)
