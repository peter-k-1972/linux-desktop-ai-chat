"""
ProjectInspectorPanel – rechte Spalte im Projects-Workspace (Projektarchiv / Rückenschild).

Beschreibung, Kontextregeln, Standard-Kontextmodus.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
)

from app.gui.shared.layout_constants import PANEL_PADDING, WIDGET_SPACING
from app.gui.theme import design_metrics as dm
from app.projects.models import format_context_rules_narrative, format_default_context_policy_caption


class ProjectInspectorPanel(QFrame):
    """Detailspalte: Archivmetadaten und Kontextkonfiguration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectInspectorPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(400)
        self._setup_ui()
        self.set_project(None)

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        title = QLabel("Projekt-Inspector")
        title.setStyleSheet(
            f"font-weight: 700; font-size: {dm.TEXT_MD_PX}px; color: #1e293b; padding: 0 4px;"
        )
        outer.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("projectInspectorScroll")

        body = QWidget()
        bl = QVBoxLayout(body)
        bl.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        bl.setSpacing(WIDGET_SPACING + 4)

        self._empty = QLabel("Kein Projekt gewählt.")
        self._empty.setWordWrap(True)
        self._empty.setStyleSheet(f"color: #64748b; font-size: {dm.TEXT_SM_PX}px;")
        bl.addWidget(self._empty)

        self._name = QLabel()
        self._name.setWordWrap(True)
        self._name.setStyleSheet(
            f"font-weight: 600; font-size: {dm.TEXT_BASE_PX}px; color: #0f172a;"
        )
        self._name.hide()
        bl.addWidget(self._name)

        self._sec_desc = QLabel("Beschreibung")
        self._sec_desc.setStyleSheet(
            f"font-weight: 600; font-size: {dm.TEXT_XS_PX}px; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em;"
        )
        self._sec_desc.hide()
        bl.addWidget(self._sec_desc)

        self._desc = QLabel()
        self._desc.setWordWrap(True)
        self._desc.setStyleSheet(f"color: #334155; font-size: {dm.TEXT_SM_PX}px; line-height: 1.45;")
        self._desc.hide()
        bl.addWidget(self._desc)

        self._sec_rules = QLabel("Kontextregeln")
        self._sec_rules.setStyleSheet(self._sec_desc.styleSheet())
        self._sec_rules.hide()
        bl.addWidget(self._sec_rules)

        self._rules = QLabel()
        self._rules.setWordWrap(True)
        self._rules.setStyleSheet(self._desc.styleSheet())
        self._rules.hide()
        bl.addWidget(self._rules)

        self._sec_mode = QLabel("Standard-Kontextmodus")
        self._sec_mode.setStyleSheet(self._sec_desc.styleSheet())
        self._sec_mode.hide()
        bl.addWidget(self._sec_mode)

        self._mode = QLabel()
        self._mode.setWordWrap(True)
        self._mode.setStyleSheet(
            f"color: #1e40af; font-size: {dm.TEXT_SM_PX}px; font-weight: 500; line-height: 1.45;"
        )
        self._mode.hide()
        bl.addWidget(self._mode)

        bl.addStretch()
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        self.setStyleSheet(
            f"""
            #projectInspectorPanel {{
                background: #f8fafc;
                border-left: 1px solid #e2e8f0;
            }}
            #projectInspectorScroll {{
                background: transparent;
            }}
            """
        )

    def set_project(self, project: dict | None) -> None:
        if not project:
            self._empty.show()
            self._name.hide()
            self._sec_desc.hide()
            self._desc.hide()
            self._sec_rules.hide()
            self._rules.hide()
            self._sec_mode.hide()
            self._mode.hide()
            return

        self._empty.hide()
        name = (project.get("name") or "Projekt").strip()
        self._name.setText(name)
        self._name.show()

        desc = (project.get("description") or "").strip() or "—"
        self._desc.setText(desc)
        self._sec_desc.show()
        self._desc.show()

        self._rules.setText(format_context_rules_narrative(project))
        self._sec_rules.show()
        self._rules.show()

        self._mode.setText(format_default_context_policy_caption(project))
        self._sec_mode.show()
        self._mode.show()
