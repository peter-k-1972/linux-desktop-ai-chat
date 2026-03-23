"""
Bottom dock: structured log output with theme-aware severity colors.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from app.gui.themes import get_theme_manager
from app.gui.workbench.ui import PanelHeader, StatusChip


class ConsolePanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchConsolePanelRoot")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(
            PanelHeader(
                "Console",
                "Logs, agent runs, and diagnostics. Severity colors follow the active theme.",
                parent=self,
            )
        )

        legend = QWidget(self)
        legend.setObjectName("workbenchConsoleLegend")
        leg_lay = QHBoxLayout(legend)
        leg_lay.setContentsMargins(12, 6, 12, 6)
        leg_lay.setSpacing(10)
        leg_label = QLabel("Severity preview:")
        leg_label.setObjectName("workbenchConsoleLegendLabel")
        leg_lay.addWidget(leg_label)
        for text, kind in (
            ("Info", "info"),
            ("Warning", "warning"),
            ("Error", "error"),
            ("OK", "success"),
        ):
            leg_lay.addWidget(StatusChip(text, kind, parent=legend))
        leg_lay.addStretch(1)
        layout.addWidget(legend)

        self._text = QPlainTextEdit(self)
        self._text.setObjectName("workbenchConsoleLog")
        self._text.setReadOnly(True)
        self._text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self._text, 1)

        self._fmts: dict[str, QTextCharFormat] = {}
        self._rebuild_formats()
        mgr = get_theme_manager()
        mgr.theme_changed.connect(lambda _tid: self._rebuild_formats())

    def _rebuild_formats(self) -> None:
        tok = get_theme_manager().get_tokens()

        def _c(key: str, fallback: str) -> QColor:
            return QColor(tok.get(key, fallback))

        info = QTextCharFormat()
        info.setForeground(_c("color_text", "#1f2937"))

        warn = QTextCharFormat()
        warn.setForeground(_c("color_warning", "#f59e0b"))

        err = QTextCharFormat()
        err.setForeground(_c("color_error", "#ef4444"))

        ok = QTextCharFormat()
        ok.setForeground(_c("color_success", "#10b981"))

        self._fmts = {
            "info": info,
            "warning": warn,
            "error": err,
            "success": ok,
        }

    def log_output(self, text: str) -> None:
        self._append(text + "\n", "info")

    def error_output(self, text: str) -> None:
        self._append(text + "\n", "error")

    def log_warning(self, text: str) -> None:
        self._append(text + "\n", "warning")

    def log_success(self, text: str) -> None:
        self._append(text + "\n", "success")

    def clear(self) -> None:
        self._text.clear()

    def _append(self, text: str, level: str) -> None:
        fmt = self._fmts.get(level, self._fmts["info"])
        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self._text.setTextCursor(cursor)
        self._text.ensureCursorVisible()
