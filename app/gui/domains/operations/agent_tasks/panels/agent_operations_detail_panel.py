"""
R2: Read-only Agent-Operations-Detail inkl. Deep Links.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.gui.shared import BasePanel
from app.qa.operations_models import AgentOperationsSummary
from app.gui.navigation.nav_areas import NavArea


def _panel_style() -> str:
    return (
        "background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; "
        "padding: 12px;"
    )


class AgentOperationsDetailPanel(BasePanel):
    """Support-Detail: Konfiguration, Issues, Navigation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentOperationsDetailPanel")
        self.setStyleSheet(_panel_style())
        self._summary: AgentOperationsSummary | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self._title = QLabel("Agent (Betrieb)")
        self._title.setStyleSheet("font-weight: 600; font-size: 14px; color: #1f2937;")
        layout.addWidget(self._title)

        self._body = QLabel("Agent in der Liste auswählen…")
        self._body.setWordWrap(True)
        self._body.setStyleSheet("color: #374151; font-size: 12px;")
        layout.addWidget(self._body)

        row_wf = QHBoxLayout()
        self._btn_workflows = QPushButton("Workflows…")
        self._btn_workflows.setToolTip("Workflows-Workspace mit Projekt-Scope und passender Definition")
        self._btn_workflows.clicked.connect(self._on_workflows)
        row_wf.addWidget(self._btn_workflows)
        row_wf.addStretch()
        layout.addLayout(row_wf)

        row_nav = QHBoxLayout()
        self._btn_betrieb = QPushButton("Störungen…")
        self._btn_betrieb.setToolTip("Betrieb → Störungen")
        self._btn_betrieb.clicked.connect(self._on_betrieb)
        row_nav.addWidget(self._btn_betrieb)
        self._btn_platform = QPushButton("Plattform…")
        self._btn_platform.setToolTip("Betrieb → Plattform-Gesundheit")
        self._btn_platform.clicked.connect(self._on_platform)
        row_nav.addWidget(self._btn_platform)
        self._btn_projects = QPushButton("Projekte…")
        self._btn_projects.setToolTip("Operations → Projekte")
        self._btn_projects.clicked.connect(self._on_projects)
        row_nav.addWidget(self._btn_projects)
        row_nav.addStretch()
        layout.addLayout(row_nav)

        layout.addStretch()

    def set_summary(self, summary: AgentOperationsSummary | None) -> None:
        self._summary = summary
        if not summary:
            self._body.setText("Agent in der Liste auswählen…")
            self._btn_workflows.setEnabled(False)
            return
        lines = [
            f"<b>Slug:</b> {summary.slug or '—'}",
            f"<b>Status:</b> {summary.status or '—'}",
            f"<b>Modell:</b> {summary.assigned_model or '—'}",
            f"<b>Modell-Rolle:</b> {summary.model_role or '—'}",
            f"<b>Cloud erlaubt:</b> {'ja' if summary.cloud_allowed else 'nein'}",
        ]
        if summary.last_activity_source == "metrics" and summary.last_activity_at:
            lines.append(f"<b>Letzte Aktivität (Metrics):</b> {summary.last_activity_at}")
        else:
            lines.append("<b>Letzte Aktivität:</b> unbekannt (keine Metrics-Events)")
        if summary.workflow_definition_ids:
            lines.append(
                f"<b>Workflow-Definitionen mit Agent-Knoten:</b> {len(summary.workflow_definition_ids)}"
            )
        if summary.issues:
            lines.append("<b>Hinweise:</b><ul>" + "".join(f"<li>{i.message}</li>" for i in summary.issues) + "</ul>")
        self._body.setText("<br/>".join(lines))
        self._btn_workflows.setEnabled(bool(summary.workflow_definition_ids))

    def _find_workspace_host(self):
        p = self
        while p:
            if hasattr(p, "show_area") and hasattr(p, "_area_to_index"):
                return p
            p = p.parent() if hasattr(p, "parent") else None
        return None

    def _on_workflows(self) -> None:
        if not self._summary or not self._summary.workflow_definition_ids:
            return
        from app.gui.domains.operations.operations_context import set_pending_context

        wf_id = self._summary.workflow_definition_ids[0]
        set_pending_context(
            {
                "workflow_ops_scope": "project",
                "workflow_ops_select_workflow_id": wf_id,
            }
        )
        host = self._find_workspace_host()
        if host:
            host.show_area(NavArea.OPERATIONS, "operations_workflows")

    def _on_betrieb(self) -> None:
        from app.gui.domains.operations.operations_context import set_pending_context

        set_pending_context({"audit_incidents_tab": "incidents"})
        host = self._find_workspace_host()
        if host:
            host.show_area(NavArea.OPERATIONS, "operations_audit_incidents")

    def _on_platform(self) -> None:
        from app.gui.domains.operations.operations_context import set_pending_context

        set_pending_context({"audit_incidents_tab": "platform"})
        host = self._find_workspace_host()
        if host:
            host.show_area(NavArea.OPERATIONS, "operations_audit_incidents")

    def _on_projects(self) -> None:
        host = self._find_workspace_host()
        if host:
            host.show_area(NavArea.OPERATIONS, "operations_projects")
