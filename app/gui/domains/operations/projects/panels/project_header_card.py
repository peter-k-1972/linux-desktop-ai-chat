"""
ProjectHeaderCard – Projektkopf für den Project Overview.

Projektname, Beschreibung, letzte Aktivität, Status.
"""

from datetime import datetime
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

from app.projects.controlling import format_budget_display, format_effort_display
from app.projects.lifecycle import lifecycle_label_de
from app.projects.models import format_default_context_policy_caption
from app.ui_contracts.workspaces.projects_overview import ProjectCoreView


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

        self._fach_label = QLabel()
        self._fach_label.setObjectName("projectHeaderFach")
        self._fach_label.setWordWrap(True)
        self._fach_label.setStyleSheet("""
            #projectHeaderFach {
                font-size: 12px;
                color: #a8b4c8;
            }
        """)
        layout.addWidget(self._fach_label)

        self._ctrl_line = QLabel()
        self._ctrl_line.setWordWrap(True)
        self._ctrl_line.setObjectName("projectHeaderControlling")
        self._ctrl_line.setStyleSheet("#projectHeaderControlling { font-size: 11px; color: #64748b; }")
        self._ctrl_line.hide()
        layout.addWidget(self._ctrl_line)

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

        self._policy_label = QLabel()
        self._policy_label.setWordWrap(True)
        self._policy_label.setObjectName("projectHeaderPolicy")
        self._policy_label.setStyleSheet("""
            #projectHeaderPolicy {
                font-size: 12px;
                color: #64748b;
            }
        """)
        layout.addWidget(self._policy_label)

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
            self._fach_label.setText("")
            self._ctrl_line.hide()
            self._meta_label.setText("")
            self._desc_label.setText("")
            self._policy_label.setText("")
            return
        name = project.get("name", "Unbenannt")
        desc = project.get("description", "") or "Keine Beschreibung."
        status = project.get("status", "active")
        created = project.get("created_at")
        updated = project.get("updated_at")
        self._name_label.setText(name)

        lc = lifecycle_label_de(project.get("lifecycle_status"))
        fach_parts = [f"Phase: {lc}"]
        cust = (project.get("customer_name") or "").strip()
        if cust:
            fach_parts.append(f"Kunde: {cust}")
        xref = (project.get("external_reference") or "").strip()
        if xref:
            fach_parts.append(f"Ref.: {xref}")
        icode = (project.get("internal_code") or "").strip()
        if icode:
            fach_parts.append(f"Code: {icode}")
        ps = (project.get("planned_start_date") or "").strip()
        pe = (project.get("planned_end_date") or "").strip()
        if ps or pe:
            plan = f"{ps or '—'} → {pe or '—'}"
            fach_parts.append(f"Plan: {plan}")
        self._fach_label.setText(" · ".join(fach_parts))

        ctrl_parts = []
        bd = format_budget_display(project.get("budget_amount"), project.get("budget_currency"))
        if bd:
            ctrl_parts.append(f"Budget: {bd}")
        eh = format_effort_display(project.get("estimated_effort_hours"))
        if eh:
            ctrl_parts.append(eh)
        if ctrl_parts:
            self._ctrl_line.setText(" · ".join(ctrl_parts))
            self._ctrl_line.show()
        else:
            self._ctrl_line.hide()

        self._meta_label.setText(
            f"Erstellt: {_format_date(created)} · Geändert: {_format_date(updated)} · "
            f"Techn. Status: {status}"
        )
        self._desc_label.setText(desc)
        self._policy_label.setText(
            f"Standard-Kontextpolicy: {format_default_context_policy_caption(project)}"
        )

    def set_overview(
        self,
        core: ProjectCoreView,
        *,
        budget_label: str | None = None,
        effort_label: str | None = None,
    ) -> None:
        self._name_label.setText(core.name or "Projekt")

        fach_parts = [f"Phase: {core.lifecycle_label}"]
        if core.customer_name:
            fach_parts.append(f"Kunde: {core.customer_name}")
        if core.external_reference:
            fach_parts.append(f"Ref.: {core.external_reference}")
        if core.internal_code:
            fach_parts.append(f"Code: {core.internal_code}")
        if core.planned_start_label or core.planned_end_label:
            fach_parts.append(
                f"Plan: {core.planned_start_label or '—'} → {core.planned_end_label or '—'}"
            )
        self._fach_label.setText(" · ".join(fach_parts))

        ctrl_parts: list[str] = []
        if budget_label:
            ctrl_parts.append(f"Budget: {budget_label}")
        if effort_label:
            ctrl_parts.append(f"Aufwandsschätzung: {effort_label}")
        if ctrl_parts:
            self._ctrl_line.setText(" · ".join(ctrl_parts))
            self._ctrl_line.show()
        else:
            self._ctrl_line.hide()

        updated = core.updated_at_label or "—"
        self._meta_label.setText(f"Geändert: {updated} · Techn. Status: {core.status_label}")
        self._desc_label.setText(core.description_display or "—")
        self._policy_label.setText(
            f"Standard-Kontextpolicy: {core.default_context_policy_label or '—'}"
        )
