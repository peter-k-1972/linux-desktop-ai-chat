"""
SubsystemDetailView – Detailansicht für ein Subsystem.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QPushButton,
    QGroupBox,
)
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices

from app.qa.dashboard_adapter import QADashboardAdapter
from app.qa.drilldown_models import SubsystemDetailData
from app.resources.styles import get_theme_colors


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


class SubsystemDetailView(QWidget):
    """Subsystem-Detail: Name, Testanzahl, Domains, Hints, Quick Links."""

    back_requested = Signal()

    def __init__(self, subsystem_name: str, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.subsystem_name = subsystem_name
        self.theme = theme
        self.adapter = QADashboardAdapter()
        self.data: SubsystemDetailData | None = None
        self._init_ui()
        self._apply_theme()
        self.refresh()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        back_btn = QPushButton("← Zurück")
        back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(back_btn)
        header.addStretch()
        self.title_label = QLabel(self.subsystem_name)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(self.title_label)
        header.addStretch()
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        self.status_group = QGroupBox("Status")
        self.status_group.setObjectName("statusGroup")
        status_layout = QVBoxLayout(self.status_group)
        self.status_label = QLabel("—")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        content_layout.addWidget(self.status_group)

        self.domains_group = QGroupBox("Test-Domains")
        self.domains_group.setObjectName("domainsGroup")
        domains_layout = QVBoxLayout(self.domains_group)
        self.domains_label = QLabel("—")
        self.domains_label.setWordWrap(True)
        domains_layout.addWidget(self.domains_label)
        content_layout.addWidget(self.domains_group)

        self.hints_group = QGroupBox("Hinweise")
        self.hints_group.setObjectName("hintsGroup")
        hints_layout = QVBoxLayout(self.hints_group)
        self.hints_label = QLabel("—")
        self.hints_label.setWordWrap(True)
        hints_layout.addWidget(self.hints_label)
        content_layout.addWidget(self.hints_group)

        links_layout = QHBoxLayout()
        for label, fn in [("Gap Report", "PHASE3_GAP_REPORT.md"), ("Coverage Map", "QA_COVERAGE_MAP.json"), ("Test Inventory", "QA_TEST_INVENTORY.json")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked=False, f=fn: self._open_file(f))
            links_layout.addWidget(btn)
        links_layout.addStretch()
        content_layout.addLayout(links_layout)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _open_file(self, filename: str):
        path = _qa_dir() / filename
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Datei nicht gefunden", f"Datei nicht vorhanden:\n{path}")

    def refresh(self):
        self.data = self.adapter.load_subsystem_detail(self.subsystem_name)
        self._update_ui()

    def _update_ui(self):
        if not self.data:
            self.status_label.setText("Keine Daten.")
            return

        d = self.data
        self.title_label.setText(d.name)
        self.status_label.setText(f"Tests: {d.test_count}\nStatus: {d.status}")

        if d.test_domains:
            lines = [f"• {dom}: {cnt}" for dom, cnt in d.test_domains[:15]]
            self.domains_label.setText("\n".join(lines))
        else:
            self.domains_label.setText("Keine Domain-Zuordnung.")

        if d.failure_classes:
            self.domains_label.setText(
                self.domains_label.text() + "\n\nFailure Classes: " + ", ".join(d.failure_classes[:10])
            )

        if d.hints:
            self.hints_label.setText("\n".join(f"• {h}" for h in d.hints))
        else:
            self.hints_label.setText("Keine besonderen Hinweise.")

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")
        style = f"""
            QGroupBox {{ font-weight: 600; color: {fg}; border: 1px solid {colors.get('top_bar_border', '#505050')}; border-radius: 8px; margin-top: 12px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; color: {muted}; }}
        """
        for g in [self.status_group, self.domains_group, self.hints_group]:
            g.setStyleSheet(style)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self._apply_theme()
