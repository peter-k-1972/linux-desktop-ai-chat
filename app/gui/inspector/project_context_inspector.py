"""
ProjectContextInspector – Inspector-Inhalt für Projekt-Kontext.

Fachliche Stammdaten, technischer Status, Standard-Kontextpolicy, Inhaltszahlen.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
)

from app.projects.lifecycle import lifecycle_label_de


class ProjectContextInspector(QWidget):
    """Inspector-Widget für Projekt-Kontext."""

    def __init__(
        self,
        project_name: str = "(kein Projekt)",
        description: str = "—",
        status: str = "active",
        policy_caption: str = "—",
        chat_count: int = 0,
        source_count: int = 0,
        prompt_count: int = 0,
        workflow_count: int = 0,
        file_link_count: int = 0,
        customer_name: Optional[str] = None,
        external_reference: Optional[str] = None,
        internal_code: Optional[str] = None,
        lifecycle_status: str = "active",
        planned_start_date: Optional[str] = None,
        planned_end_date: Optional[str] = None,
        controlling_budget_line: Optional[str] = None,
        controlling_effort_line: Optional[str] = None,
        controlling_next_milestone: Optional[str] = None,
        controlling_milestone_counts: Optional[str] = None,
        monitoring_text: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("projectContextInspector")
        self._project_name = project_name
        self._description = description
        self._status = status
        self._policy_caption = policy_caption
        self._chat_count = chat_count
        self._source_count = source_count
        self._prompt_count = prompt_count
        self._workflow_count = workflow_count
        self._file_link_count = file_link_count
        self._customer_name = customer_name
        self._external_reference = external_reference
        self._internal_code = internal_code
        self._lifecycle_status = lifecycle_status
        self._planned_start_date = planned_start_date
        self._planned_end_date = planned_end_date
        self._controlling_budget_line = controlling_budget_line
        self._controlling_effort_line = controlling_effort_line
        self._controlling_next_milestone = controlling_next_milestone
        self._controlling_milestone_counts = controlling_milestone_counts
        self._monitoring_text = monitoring_text
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        proj_group = QGroupBox("Projekt")
        proj_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        proj_layout = QVBoxLayout(proj_group)
        name_label = QLabel(self._project_name)
        name_label.setStyleSheet("color: #1f2937; font-size: 14px; font-weight: 500;")
        name_label.setWordWrap(True)
        proj_layout.addWidget(name_label)
        layout.addWidget(proj_group)

        lc_group = QGroupBox("Projektphase")
        lc_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        lc_layout = QVBoxLayout(lc_group)
        lc_lbl = QLabel(lifecycle_label_de(self._lifecycle_status))
        lc_lbl.setStyleSheet("color: #1e40af; font-size: 12px;")
        lc_layout.addWidget(lc_lbl)
        layout.addWidget(lc_group)

        auftrag_group = QGroupBox("Auftrag")
        auftrag_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        auftrag_layout = QVBoxLayout(auftrag_group)
        lines = []
        if (self._customer_name or "").strip():
            lines.append(f"Kunde: {self._customer_name.strip()}")
        if (self._external_reference or "").strip():
            lines.append(f"Externe Referenz: {self._external_reference.strip()}")
        if (self._internal_code or "").strip():
            lines.append(f"Interner Code: {self._internal_code.strip()}")
        ps = (self._planned_start_date or "").strip()
        pe = (self._planned_end_date or "").strip()
        if ps:
            lines.append(f"Geplanter Start: {ps}")
        if pe:
            lines.append(f"Geplantes Ende: {pe}")
        if lines:
            for t in lines:
                lab = QLabel(t)
                lab.setWordWrap(True)
                lab.setStyleSheet("color: #6b7280; font-size: 12px;")
                auftrag_layout.addWidget(lab)
        else:
            em = QLabel("—")
            em.setStyleSheet("color: #9ca3af; font-size: 12px;")
            auftrag_layout.addWidget(em)
        layout.addWidget(auftrag_group)

        ctrl_group = QGroupBox("Controlling")
        ctrl_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        ctrl_layout = QVBoxLayout(ctrl_group)
        has_ctrl = False
        if (self._controlling_budget_line or "").strip():
            lb = QLabel(self._controlling_budget_line.strip())
            lb.setWordWrap(True)
            lb.setStyleSheet("color: #6b7280; font-size: 12px;")
            ctrl_layout.addWidget(lb)
            has_ctrl = True
        if (self._controlling_effort_line or "").strip():
            lb = QLabel(self._controlling_effort_line.strip())
            lb.setWordWrap(True)
            lb.setStyleSheet("color: #6b7280; font-size: 12px;")
            ctrl_layout.addWidget(lb)
            has_ctrl = True
        nm = (self._controlling_next_milestone or "").strip()
        if nm:
            lb = QLabel(f"Nächster Meilenstein: {nm}")
            lb.setWordWrap(True)
            lb.setStyleSheet("color: #6b7280; font-size: 12px;")
            ctrl_layout.addWidget(lb)
            has_ctrl = True
        mc = (self._controlling_milestone_counts or "").strip()
        if mc:
            lb = QLabel(mc)
            lb.setWordWrap(True)
            lb.setStyleSheet("color: #6b7280; font-size: 12px;")
            ctrl_layout.addWidget(lb)
            has_ctrl = True
        if not has_ctrl:
            em = QLabel("—")
            em.setStyleSheet("color: #9ca3af; font-size: 12px;")
            ctrl_layout.addWidget(em)
        layout.addWidget(ctrl_group)

        mon_group = QGroupBox("Betrieb / Monitoring")
        mon_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        mon_layout = QVBoxLayout(mon_group)
        mt = (self._monitoring_text or "").strip()
        if mt:
            mon_label = QLabel(mt)
            mon_label.setWordWrap(True)
            mon_label.setStyleSheet("color: #6b7280; font-size: 12px; line-height: 1.45;")
            mon_layout.addWidget(mon_label)
        else:
            em = QLabel("—")
            em.setStyleSheet("color: #9ca3af; font-size: 12px;")
            mon_layout.addWidget(em)
        layout.addWidget(mon_group)

        desc_group = QGroupBox("Beschreibung")
        desc_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        desc_layout = QVBoxLayout(desc_group)
        desc_label = QLabel(self._description)
        desc_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        desc_label.setWordWrap(True)
        desc_layout.addWidget(desc_label)
        layout.addWidget(desc_group)

        status_group = QGroupBox("Technischer Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        status_layout = QVBoxLayout(status_group)
        status_label = QLabel(self._status)
        status_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        status_layout.addWidget(status_label)
        layout.addWidget(status_group)

        pol_group = QGroupBox("Standard-Kontextpolicy")
        pol_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        pol_layout = QVBoxLayout(pol_group)
        pol_label = QLabel(self._policy_caption)
        pol_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        pol_label.setWordWrap(True)
        pol_layout.addWidget(pol_label)
        layout.addWidget(pol_group)

        content_group = QGroupBox("Inhalte")
        content_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        content_layout = QVBoxLayout(content_group)
        content_label = QLabel(
            f"Chats: {self._chat_count} · Knowledge-Quellen: {self._source_count} · "
            f"Prompts: {self._prompt_count} · Workflows (Projekt): {self._workflow_count} · "
            f"Datei-Links (DB): {self._file_link_count}"
        )
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        content_layout.addWidget(content_label)
        layout.addWidget(content_group)

        layout.addStretch()
