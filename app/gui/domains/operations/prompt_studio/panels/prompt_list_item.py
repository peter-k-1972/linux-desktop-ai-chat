"""
PromptListItem – Single prompt entry in the Prompts list.

Shows: name, last updated date, number of versions.
Optional: scope badge (project/global).
Merged from ui/prompts and gui panels.
"""

from typing import Any, Optional

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


def _format_date(dt: Any) -> str:
    """Format date for display (e.g. 16.03.2025)."""
    if not dt:
        return "—"
    try:
        if hasattr(dt, "strftime"):
            return dt.strftime("%d.%m.%Y")
        s = str(dt)
        if "T" in s:
            from datetime import datetime
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return d.strftime("%d.%m.%Y")
        return s[:10] if len(s) >= 10 else s
    except (ValueError, TypeError):
        return "—"


def _get_version_count(prompt: Any, version_count: Optional[int] = None) -> int:
    """Get number of versions for a prompt. Minimum 1 if prompt exists."""
    if prompt is None:
        return 0
    if version_count is not None and version_count > 0:
        return version_count
    return max(version_count or 0, 1)  # At least 1 for existing prompts


class PromptListItem(QFrame):
    """Single prompt entry: name, last updated date, number of versions."""

    def __init__(
        self,
        prompt: Any,
        active: bool = False,
        version_count: Optional[int] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.prompt = prompt
        self._active = active
        self._version_count = version_count
        self.setObjectName("promptListItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        row = QHBoxLayout()
        row.setSpacing(8)

        name = QLabel(self.prompt.title or "Unbenannt")
        name.setObjectName("promptItemName")
        name.setStyleSheet("font-weight: 600; font-size: 13px; color: #1f2937;")
        name.setWordWrap(True)
        row.addWidget(name, 1)

        scope = getattr(self.prompt, "scope", "global")
        project_id = getattr(self.prompt, "project_id", None)
        is_project = scope == "project" and project_id is not None
        badge = QLabel("Projekt" if is_project else "Global")
        badge.setObjectName("promptItemBadge")
        badge.setStyleSheet(
            "#promptItemBadge { font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; "
            + ("background: #dbeafe; color: #1d4ed8;" if is_project else "background: #f3f4f6; color: #6b7280;")
            + " }"
        )
        row.addWidget(badge)
        layout.addLayout(row)

        meta = QHBoxLayout()
        meta.setSpacing(12)
        last_updated = getattr(self.prompt, "updated_at", None) or getattr(
            self.prompt, "created_at", None
        )
        updated_label = QLabel(_format_date(last_updated))
        updated_label.setObjectName("promptItemUpdated")
        updated_label.setStyleSheet("font-size: 11px; color: #64748b;")
        meta.addWidget(updated_label)
        vc = _get_version_count(self.prompt, self._version_count)
        versions_text = f"{vc} Version" if vc == 1 else f"{vc} Versionen"
        versions_label = QLabel(versions_text)
        versions_label.setObjectName("promptItemVersions")
        versions_label.setStyleSheet("font-size: 11px; color: #64748b;")
        meta.addWidget(versions_label)
        meta.addStretch()
        layout.addLayout(meta)

    def _apply_style(self) -> None:
        if self._active:
            self.setStyleSheet("""
                #promptListItem {
                    background: #eff6ff;
                    border: 1px solid #bfdbfe;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                #promptListItem {
                    background: #ffffff;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                }
                #promptListItem:hover {
                    background: #f9fafb;
                    border-color: #d1d5db;
                }
            """)

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_style()


# Alias for library_panel compatibility
PromptListItemWidget = PromptListItem
