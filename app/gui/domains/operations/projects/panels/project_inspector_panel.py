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

from app.gui.domains.operations.projects.project_inspector_sink import ProjectInspectorSink
from app.gui.shared.layout_constants import PANEL_PADDING, WIDGET_SPACING
from app.gui.theme import design_metrics as dm
from app.ui_application.adapters.service_projects_overview_read_adapter import (
    ServiceProjectsOverviewReadAdapter,
)
from app.ui_application.presenters.project_inspector_presenter import ProjectInspectorPresenter
from app.ui_application.ports.projects_overview_read_port import ProjectsOverviewReadPort
from app.ui_contracts.workspaces.projects_overview import ProjectInspectorState


class ProjectInspectorPanel(QFrame):
    """Detailspalte: Archivmetadaten und Kontextkonfiguration."""

    def __init__(
        self,
        parent=None,
        *,
        read_port: ProjectsOverviewReadPort | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("projectInspectorPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(400)
        self._setup_ui()
        self._sink = ProjectInspectorSink(self)
        self._presenter = ProjectInspectorPresenter(
            sink=self._sink,
            read_port=read_port or ServiceProjectsOverviewReadAdapter(),
        )
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
        self._presenter.set_project(project)

    def refresh(self) -> None:
        self._presenter.refresh()

    def apply_inspector_loading(self) -> None:
        self.apply_inspector_empty("Projekt-Inspector wird geladen…")

    def apply_inspector_empty(self, message: str | None = None) -> None:
        self._empty.setText(message or "Kein Projekt gewählt.")
        self._empty.show()
        self._name.hide()
        self._sec_desc.hide()
        self._desc.hide()
        self._sec_rules.hide()
        self._rules.hide()
        self._sec_mode.hide()
        self._mode.hide()

    def apply_inspector_error(self, message: str | None = None) -> None:
        self.apply_inspector_empty(message or "Projekt-Inspector konnte nicht geladen werden.")

    def apply_inspector_state(self, state: ProjectInspectorState) -> None:
        self._empty.hide()
        self._name.setText(state.title or "Projekt")
        self._name.show()
        self._desc.setText(state.description_display or "—")
        self._sec_desc.show()
        self._desc.show()
        self._rules.setText(state.context_rules_narrative or "—")
        self._sec_rules.show()
        self._rules.show()
        self._mode.setText(state.context_policy_caption or "—")
        self._sec_mode.show()
        self._mode.show()
