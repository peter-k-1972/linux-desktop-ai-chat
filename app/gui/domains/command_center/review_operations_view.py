"""
ReviewOperationsView – Arbeitsbereich für review_candidate / Orphan Backlog.
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

from app.qa.operations_adapter import OperationsAdapter
from app.qa.operations_models import ReviewOperationsData
from app.resources.styles import get_theme_colors


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


class ReviewOperationsView(QWidget):
    """Review Operations – Orphan Backlog, Review-Batches."""

    back_requested = Signal()

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.adapter = OperationsAdapter()
        self.data: ReviewOperationsData | None = None
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
        title = QLabel("Review Operations")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        self.backlog_group = QGroupBox("Orphan Review Backlog")
        self.backlog_group.setObjectName("backlogGroup")
        bl_layout = QVBoxLayout(self.backlog_group)
        self.backlog_label = QLabel("—")
        self.backlog_label.setWordWrap(True)
        bl_layout.addWidget(self.backlog_label)
        content_layout.addWidget(self.backlog_group)

        self.batches_group = QGroupBox("Review-Batches")
        self.batches_group.setObjectName("batchesGroup")
        batch_layout = QVBoxLayout(self.batches_group)
        self.batches_label = QLabel("—")
        self.batches_label.setWordWrap(True)
        batch_layout.addWidget(self.batches_label)
        content_layout.addWidget(self.batches_group)

        links_layout = QHBoxLayout()
        for label, fn in [("Gap Report", "PHASE3_GAP_REPORT.md"), ("Orphan Governance", "PHASE3_ORPHAN_REVIEW_GOVERNANCE.md")]:
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
        self.data = self.adapter.load_review_operations()
        self._update_ui()

    def _update_ui(self):
        if not self.data:
            self.backlog_label.setText("Keine Review-Daten.")
            return

        d = self.data
        self.backlog_label.setText(
            f"Orphan Backlog: {d.orphan_count} Tests\n"
            f"Treat as: {d.treat_as}\n\n"
            "Diese Tests haben keine catalog_bound-Zuordnung und sind als Review-Kandidaten markiert."
        )

        if d.batches:
            lines = []
            for b in d.batches:
                lines.append(f"• {b.label}: {b.count} ({b.treat_as})")
                if b.description:
                    lines.append(f"  {b.description}")
            self.batches_label.setText("\n".join(lines))
        else:
            self.batches_label.setText("Keine Batches.")

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")
        style = f"""
            QGroupBox {{ font-weight: 600; color: {fg}; border: 1px solid {colors.get('top_bar_border', '#505050')}; border-radius: 8px; margin-top: 12px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; color: {muted}; }}
        """
        for g in [self.backlog_group, self.batches_group]:
            g.setStyleSheet(style)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self._apply_theme()
