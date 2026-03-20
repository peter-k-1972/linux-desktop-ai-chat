"""
CommandCenterView – Kommandozentrale / Operations Center.

Phase B+C: Stack-Navigation mit Drilldown in QA, Subsysteme, Runtime, Governance, Operations.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QStackedWidget,
    QScrollArea,
    QFrame,
    QLabel,
    QPushButton,
    QGroupBox,
)
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices

from app.qa.dashboard_adapter import QADashboardAdapter, DashboardData
from app.resources.styles import get_theme_colors
from app.gui.domains.command_center.qa_drilldown_view import QADrilldownView
from app.gui.domains.command_center.subsystem_detail_view import SubsystemDetailView
from app.gui.domains.command_center.runtime_debug_view import RuntimeDebugView
from app.gui.domains.command_center.governance_view import GovernanceView
from app.gui.domains.command_center.qa_operations_view import QAOperationsView
from app.gui.domains.command_center.incident_operations_view import IncidentOperationsView
from app.gui.domains.command_center.review_operations_view import ReviewOperationsView
from app.gui.domains.command_center.audit_operations_view import AuditOperationsView


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


class _StatusCard(QFrame):
    """Einzelne Executive Status Card."""

    def __init__(self, title: str, value: str | int, subtitle: str = "", theme: str = "dark"):
        super().__init__()
        self.setObjectName("statusCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("statusCardTitle")
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("statusCardValue")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("statusCardSubtitle")
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        if subtitle:
            layout.addWidget(self.subtitle_label)
        self._theme = theme

    def set_value(self, value: str | int, subtitle: str = ""):
        self.value_label.setText(str(value))
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle))

    def apply_style(self, colors: dict):
        bg = "#2a2a2a" if self._theme == "dark" else "#f8f8f8"
        border = colors.get("top_bar_border", "#505050")
        fg = colors.get("fg", "#e8e8e8")
        self.setStyleSheet(f"""
            QFrame#statusCard {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QLabel#statusCardTitle {{
                color: {colors.get('muted', '#a0a0a0')};
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            QLabel#statusCardValue {{
                color: {fg};
                font-size: 20px;
                font-weight: 700;
            }}
            QLabel#statusCardSubtitle {{
                color: {colors.get('muted', '#a0a0a0')};
                font-size: 10px;
            }}
        """)


class _SubsystemCard(QPushButton):
    """Klickbare Subsystem-Karte."""

    def __init__(self, name: str, test_count: int, theme: str = "dark"):
        super().__init__(f"{name}\n{test_count} Tests")
        self.subsystem_name = name
        self.setObjectName("subsystemCard")
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton#subsystemCard {
                text-align: left;
                padding: 10px;
                border: 1px solid #505050;
                border-radius: 8px;
                background-color: #2a2a2a;
            }
            QPushButton#subsystemCard:hover {
                background-color: #353535;
                border-color: #606060;
            }
        """)


class CommandCenterView(QWidget):
    """
    Kommandozentrale – Control Center mit Stack-Navigation.
    """

    back_to_chat_requested = Signal()

    IDX_OVERVIEW = 0
    IDX_QA_DRILLDOWN = 1
    IDX_SUBSYSTEM = 2
    IDX_RUNTIME = 3
    IDX_GOVERNANCE = 4
    IDX_QA_OPS = 5
    IDX_INCIDENT_OPS = 6
    IDX_REVIEW_OPS = 7
    IDX_AUDIT_OPS = 8

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.adapter = QADashboardAdapter()
        self.data: DashboardData | None = None
        self._subsystem_detail_view: SubsystemDetailView | None = None
        self.init_ui()
        self.apply_theme()
        self.refresh()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()

        # Overview
        overview = QWidget()
        ov_layout = QVBoxLayout(overview)
        ov_layout.setContentsMargins(16, 16, 16, 16)
        ov_layout.setSpacing(16)

        header = QHBoxLayout()
        self.back_btn = QPushButton("← Zurück zum Chat")
        self.back_btn.setObjectName("backToChatBtn")
        self.back_btn.clicked.connect(self.back_to_chat_requested.emit)
        header.addWidget(self.back_btn)
        header.addStretch()
        title = QLabel("Kommandozentrale")
        title.setObjectName("commandCenterTitle")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        ov_layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)

        # Guided Workflow Entry (Phase C)
        workflow_group = QGroupBox("Guided Workflow Entry")
        workflow_group.setObjectName("workflowGroup")
        workflow_layout = QHBoxLayout(workflow_group)
        for label, target in [
            ("Orphan Review öffnen", "review_ops"),
            ("QA Verification prüfen", "qa_ops"),
            ("Incident-Status prüfen", "incident_ops"),
            ("Audit Follow-up öffnen", "audit_ops"),
        ]:
            btn = QPushButton(label)
            btn.setToolTip(f"Öffnet: {label}")
            btn.clicked.connect(lambda checked=False, t=target: self._show_operations(t))
            workflow_layout.addWidget(btn)
        workflow_layout.addStretch()
        content_layout.addWidget(workflow_group)

        # Operations Center (Phase C)
        ops_group = QGroupBox("Operations Center")
        ops_group.setObjectName("opsGroup")
        ops_layout = QGridLayout(ops_group)
        for i, (label, target) in enumerate([
            ("QA Operations", "qa_ops"),
            ("Incident Operations", "incident_ops"),
            ("Review Operations", "review_ops"),
            ("Audit / Technical Debt", "audit_ops"),
        ]):
            btn = QPushButton(label + " →")
            btn.clicked.connect(lambda checked=False, t=target: self._show_operations(t))
            ops_layout.addWidget(btn, i // 2, i % 2)
        content_layout.addWidget(ops_group)

        # 1. Executive Status Cards
        cards_group = QGroupBox("Executive Status")
        cards_group.setObjectName("executiveGroup")
        cards_layout = QGridLayout(cards_group)
        self.card_tests = _StatusCard("Tests im Inventar", "—", theme=self.theme)
        self.card_gaps = _StatusCard("Priorisierte Gaps", "—", theme=self.theme)
        self.card_orphan = _StatusCard("Orphan Backlog", "—", theme=self.theme)
        self.card_health = _StatusCard("QA-Gesundheit", "—", theme=self.theme)
        cards_layout.addWidget(self.card_tests, 0, 0)
        cards_layout.addWidget(self.card_gaps, 0, 1)
        cards_layout.addWidget(self.card_orphan, 0, 2)
        cards_layout.addWidget(self.card_health, 0, 3)
        content_layout.addWidget(cards_group)

        # 2. QA Health – mit Drilldown-Button
        health_group = QGroupBox("QA Health – Coverage")
        health_group.setObjectName("healthGroup")
        health_layout = QVBoxLayout(health_group)
        self.health_label = QLabel("Lade …")
        self.health_label.setWordWrap(True)
        health_layout.addWidget(self.health_label)
        qa_drilldown_btn = QPushButton("QA Drilldown →")
        qa_drilldown_btn.setToolTip("Detailansicht: Gaps, Coverage, Orphan Backlog")
        qa_drilldown_btn.clicked.connect(self._show_qa_drilldown)
        health_layout.addWidget(qa_drilldown_btn)
        content_layout.addWidget(health_group)

        # 3. Gap-Warnungen
        gap_group = QGroupBox("Gap-Report Hinweise")
        gap_group.setObjectName("gapGroup")
        gap_layout = QVBoxLayout(gap_group)
        self.gap_label = QLabel("—")
        self.gap_label.setWordWrap(True)
        gap_layout.addWidget(self.gap_label)
        content_layout.addWidget(gap_group)

        # 4. Subsystem-Übersicht (klickbar)
        sub_group = QGroupBox("Subsystem-Übersicht")
        sub_group.setObjectName("subsystemGroup")
        self.sub_layout = QGridLayout(sub_group)
        content_layout.addWidget(sub_group)

        # 5. Runtime / Debug
        runtime_group = QGroupBox("Runtime / Debug")
        runtime_group.setObjectName("runtimeGroup")
        runtime_layout = QVBoxLayout(runtime_group)
        runtime_layout.addWidget(QLabel("Debug-Panel (Aktivität, Timeline, Task-Graph) im Chat-Sidepanel."))
        runtime_btn = QPushButton("Zum Chat (Debug-Panel)")
        runtime_btn.clicked.connect(self._show_runtime)
        runtime_layout.addWidget(runtime_btn)
        content_layout.addWidget(runtime_group)

        # 6. Governance
        gov_group = QGroupBox("Governance / Freeze-Zonen")
        gov_group.setObjectName("govGroup")
        gov_layout = QVBoxLayout(gov_group)
        gov_layout.addWidget(QLabel("Orientierung: QA-Kern, aktive Entwicklung, experimentell."))
        gov_btn = QPushButton("Governance anzeigen →")
        gov_btn.clicked.connect(self._show_governance)
        gov_layout.addWidget(gov_btn)
        content_layout.addWidget(gov_group)

        # 7. Next Actions
        actions_group = QGroupBox("Nächste Schritte")
        actions_group.setObjectName("actionsGroup")
        actions_layout = QVBoxLayout(actions_group)
        self.actions_label = QLabel("—")
        self.actions_label.setWordWrap(True)
        actions_layout.addWidget(self.actions_label)
        content_layout.addWidget(actions_group)

        # 8. Quick Links
        links_group = QGroupBox("Quick Links")
        links_group.setObjectName("linksGroup")
        links_layout = QHBoxLayout(links_group)
        for label, fn in [("Gap Report", "PHASE3_GAP_REPORT.md"), ("Coverage Map", "QA_COVERAGE_MAP.json"), ("Test Inventory", "QA_TEST_INVENTORY.json")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked=False, f=fn: self._open_file(f))
            links_layout.addWidget(btn)
        links_layout.addStretch()
        content_layout.addWidget(links_group)

        content_layout.addStretch()
        scroll.setWidget(content)
        ov_layout.addWidget(scroll)

        self.stack.addWidget(overview)

        # QA Drilldown
        self.qa_drilldown_view = QADrilldownView(theme=self.theme)
        self.qa_drilldown_view.back_requested.connect(self._show_overview)
        self.stack.addWidget(self.qa_drilldown_view)

        # Subsystem Detail (placeholder, wird bei Bedarf befüllt)
        self._subsystem_detail_view = SubsystemDetailView("Chat", theme=self.theme)
        self._subsystem_detail_view.back_requested.connect(self._show_overview)
        self.stack.addWidget(self._subsystem_detail_view)

        # Runtime Debug
        self.runtime_view = RuntimeDebugView(theme=self.theme)
        self.runtime_view.back_requested.connect(self._show_overview)
        self.runtime_view.go_to_chat_requested.connect(self.back_to_chat_requested.emit)
        self.stack.addWidget(self.runtime_view)

        # Governance
        self.governance_view = GovernanceView(theme=self.theme)
        self.governance_view.back_requested.connect(self._show_overview)
        self.stack.addWidget(self.governance_view)

        # Operations Views (Phase C)
        self.qa_ops_view = QAOperationsView(theme=self.theme)
        self.qa_ops_view.back_requested.connect(self._show_overview)
        self.stack.addWidget(self.qa_ops_view)

        self.incident_ops_view = IncidentOperationsView(theme=self.theme)
        self.incident_ops_view.back_requested.connect(self._show_overview)
        self.stack.addWidget(self.incident_ops_view)

        self.review_ops_view = ReviewOperationsView(theme=self.theme)
        self.review_ops_view.back_requested.connect(self._show_overview)
        self.stack.addWidget(self.review_ops_view)

        self.audit_ops_view = AuditOperationsView(theme=self.theme)
        self.audit_ops_view.back_requested.connect(self._show_overview)
        self.stack.addWidget(self.audit_ops_view)

        layout.addWidget(self.stack)

    def _show_overview(self):
        self.stack.setCurrentIndex(self.IDX_OVERVIEW)

    def _show_qa_drilldown(self):
        self.qa_drilldown_view.refresh()
        self.stack.setCurrentIndex(self.IDX_QA_DRILLDOWN)

    def _show_subsystem(self, name: str):
        self._subsystem_detail_view.subsystem_name = name
        self._subsystem_detail_view.refresh()
        self.stack.setCurrentIndex(self.IDX_SUBSYSTEM)

    def _show_runtime(self):
        self.stack.setCurrentIndex(self.IDX_RUNTIME)

    def _show_governance(self):
        self.governance_view.refresh()
        self.stack.setCurrentIndex(self.IDX_GOVERNANCE)

    def _show_operations(self, target: str):
        if target == "qa_ops":
            self.qa_ops_view.refresh()
            self.stack.setCurrentIndex(self.IDX_QA_OPS)
        elif target == "incident_ops":
            self.incident_ops_view.refresh()
            self.stack.setCurrentIndex(self.IDX_INCIDENT_OPS)
        elif target == "review_ops":
            self.review_ops_view.refresh()
            self.stack.setCurrentIndex(self.IDX_REVIEW_OPS)
        elif target == "audit_ops":
            self.audit_ops_view.refresh()
            self.stack.setCurrentIndex(self.IDX_AUDIT_OPS)

    def _on_debug_clicked(self):
        self.back_to_chat_requested.emit()

    def _open_file(self, filename: str):
        path = _qa_dir() / filename
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Datei nicht gefunden", f"Datei nicht vorhanden:\n{path}")

    def refresh(self):
        self.data = self.adapter.load()
        self._update_cards()
        self._update_health()
        self._update_gaps()
        self._update_subsystems()
        self._update_actions()

    def _update_cards(self):
        if not self.data:
            return
        ex = self.data.executive
        self.card_tests.set_value(ex.test_count)
        self.card_gaps.set_value(ex.prioritized_gaps)
        self.card_orphan.set_value(ex.orphan_backlog)
        health_text = {"ok": "✓ OK", "warning": "⚠ Warnung", "unknown": "—"}.get(
            ex.qa_health, ex.qa_health
        )
        self.card_health.set_value(health_text, ex.last_verification or "")

    def _update_health(self):
        if not self.data:
            self.health_label.setText("Keine QA-Daten verfügbar.")
            return
        lines = []
        for ax in self.data.coverage_axes:
            strength = ax.strength
            gap = f" ({ax.gap_count} Gaps)" if ax.gap_count else ""
            lines.append(f"• {ax.axis}: {strength}{gap}")
        self.health_label.setText("\n".join(lines) if lines else "Keine Coverage-Daten.")

    def _update_gaps(self):
        if not self.data:
            self.gap_label.setText("—")
            return
        if not self.data.gap_warnings:
            self.gap_label.setText("Keine Warnungen.")
        else:
            self.gap_label.setText("\n".join(f"• {w}" for w in self.data.gap_warnings))

    def _update_subsystems(self):
        while self.sub_layout.count():
            item = self.sub_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.data:
            self.sub_layout.addWidget(QLabel("Keine Subsystem-Daten."), 0, 0)
            return

        idx = 0
        for sub in self.data.subsystems:
            if sub.test_count == 0 and sub.name == "unknown":
                continue
            card = _SubsystemCard(sub.name, sub.test_count, theme=self.theme)
            card.clicked.connect(lambda checked=False, n=sub.name: self._show_subsystem(n))
            self.sub_layout.addWidget(card, idx // 3, idx % 3)
            idx += 1

    def _update_actions(self):
        if not self.data:
            self.actions_label.setText("—")
            return
        self.actions_label.setText("\n".join(f"• {a}" for a in self.data.next_actions))

    def apply_theme(self):
        colors = get_theme_colors(self.theme)
        self.card_tests.apply_style(colors)
        self.card_gaps.apply_style(colors)
        self.card_orphan.apply_style(colors)
        self.card_health.apply_style(colors)

        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")
        group_style = f"""
            QGroupBox {{
                font-weight: 600;
                color: {fg};
                border: 1px solid {colors.get('top_bar_border', '#505050')};
                border-radius: 8px;
                margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: {muted};
            }}
        """
        for name in ["executiveGroup", "workflowGroup", "opsGroup", "healthGroup", "gapGroup", "subsystemGroup", "runtimeGroup", "govGroup", "actionsGroup", "linksGroup"]:
            w = self.findChild(QGroupBox, name)
            if w:
                w.setStyleSheet(group_style)

        self.qa_drilldown_view.refresh_theme(self.theme)
        self._subsystem_detail_view.refresh_theme(self.theme)
        self.runtime_view.refresh_theme(self.theme)
        self.governance_view.refresh_theme(self.theme)
        self.qa_ops_view.refresh_theme(self.theme)
        self.incident_ops_view.refresh_theme(self.theme)
        self.review_ops_view.refresh_theme(self.theme)
        self.audit_ops_view.refresh_theme(self.theme)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self.apply_theme()
