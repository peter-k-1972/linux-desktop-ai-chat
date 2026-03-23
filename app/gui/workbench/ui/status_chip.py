"""
Small status / severity labels (console legend, future row badges).
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget


class StatusChip(QLabel):
    """Object name is ``workbenchChip{Kind}`` for QSS (Info, Warning, Error, Success)."""

    def __init__(self, text: str, kind: str = "Info", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        key = kind.strip().lower()
        oid = {
            "info": "workbenchChipInfo",
            "warning": "workbenchChipWarning",
            "error": "workbenchChipError",
            "success": "workbenchChipSuccess",
        }.get(key, "workbenchChipInfo")
        self.setObjectName(oid)
