"""
QAOperationsView – Operativer Bereich für QA-Verifikation und Artefakte.
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
from app.qa.operations_models import QAOperationsData
from app.resources.styles import get_theme_colors


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


class QAOperationsView(QWidget):
    """QA Operations – Verifikationsstatus, Artefakte, Einstieg in Verifikation."""

    back_requested = Signal()

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.adapter = OperationsAdapter()
        self.data: QAOperationsData | None = None
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
        title = QLabel("QA Operations")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        self.verification_group = QGroupBox("Verifikationsstatus")
        self.verification_group.setObjectName("verificationGroup")
        ver_layout = QVBoxLayout(self.verification_group)
        self.verification_label = QLabel("Lade …")
        self.verification_label.setWordWrap(True)
        ver_layout.addWidget(self.verification_label)
        content_layout.addWidget(self.verification_group)

        self.artifacts_group = QGroupBox("Relevante Artefakte")
        self.artifacts_group.setObjectName("artifactsGroup")
        art_layout = QVBoxLayout(self.artifacts_group)
        self.artifacts_layout = QVBoxLayout()
        art_layout.addLayout(self.artifacts_layout)
        content_layout.addWidget(self.artifacts_group)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def refresh(self):
        self.data = self.adapter.load_qa_operations()
        self._update_ui()

    def _update_ui(self):
        if not self.data:
            self.verification_label.setText("Keine QA-Daten.")
            return

        v = self.data.verification
        lines = [
            f"Letzter Lauf: {v.last_run or '—'}",
            f"Gaps geschlossen: {'Ja' if v.gaps_closed else 'Nein'}",
            f"Orphan Backlog: {v.orphan_count}",
        ]
        if v.verification_steps:
            lines.append("Schritte: " + ", ".join(v.verification_steps))
        self.verification_label.setText("\n".join(lines))

        while self.artifacts_layout.count():
            item = self.artifacts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label, fn in self.data.artifact_links:
            btn = QPushButton(f"Öffnen: {label}")
            btn.clicked.connect(lambda checked=False, f=fn: self._open_file(f))
            self.artifacts_layout.addWidget(btn)

    def _open_file(self, filename: str):
        path = _qa_dir() / filename
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Datei nicht gefunden", f"Datei nicht vorhanden:\n{path}")

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")
        style = f"""
            QGroupBox {{ font-weight: 600; color: {fg}; border: 1px solid {colors.get('top_bar_border', '#505050')}; border-radius: 8px; margin-top: 12px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; color: {muted}; }}
        """
        for g in [self.verification_group, self.artifacts_group]:
            g.setStyleSheet(style)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self._apply_theme()
