"""QAbstractListModel types for Prompt Studio QML."""

from __future__ import annotations

import re
from datetime import datetime

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

_VAR_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def extract_variable_names(text: str) -> list[str]:
    if not text:
        return []
    seen: list[str] = []
    for m in _VAR_PATTERN.finditer(text):
        name = m.group(1)
        if name not in seen:
            seen.append(name)
    return seen


def format_variables_line(text: str) -> str:
    names = extract_variable_names(text)
    return ", ".join(names) if names else ""


class PromptShelfListModel(QAbstractListModel):
    PromptIdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    CategoryRole = Qt.ItemDataRole.UserRole + 3
    TagsLineRole = Qt.ItemDataRole.UserRole + 4
    IsSelectedRole = Qt.ItemDataRole.UserRole + 5

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []
        self._selected_id: int | None = None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.PromptIdRole:
            return row["promptId"]
        if role == self.TitleRole:
            return row["title"]
        if role == self.CategoryRole:
            return row["category"]
        if role == self.TagsLineRole:
            return row["tagsLine"]
        if role == self.IsSelectedRole:
            return row["promptId"] == self._selected_id
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.PromptIdRole: b"promptId",
            self.TitleRole: b"title",
            self.CategoryRole: b"category",
            self.TagsLineRole: b"tagsLine",
            self.IsSelectedRole: b"isSelected",
        }

    def set_prompts(self, rows: list[dict[str, object]], selected_id: int | None) -> None:
        self.beginResetModel()
        self._selected_id = selected_id
        self._rows = rows
        self.endResetModel()

    def update_selection(self, selected_id: int | None) -> None:
        if self._selected_id == selected_id:
            return
        self._selected_id = selected_id
        if not self._rows:
            return
        top = self.index(0, 0)
        bottom = self.index(len(self._rows) - 1, 0)
        self.dataChanged.emit(top, bottom, [self.IsSelectedRole])


class VariantListModel(QAbstractListModel):
    VersionRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    SubtitleRole = Qt.ItemDataRole.UserRole + 3
    ContentRole = Qt.ItemDataRole.UserRole + 4

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, str]] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.VersionRole:
            return row["version"]
        if role == self.TitleRole:
            return row["title"]
        if role == self.SubtitleRole:
            return row["subtitle"]
        if role == self.ContentRole:
            return row["content"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.VersionRole: b"version",
            self.TitleRole: b"title",
            self.SubtitleRole: b"subtitle",
            self.ContentRole: b"content",
        }

    def set_versions(self, items: list[dict]) -> None:
        self.beginResetModel()
        rows: list[dict[str, str]] = []
        for it in items:
            ver = it.get("version", "")
            title = str(it.get("title") or "")
            body = str(it.get("content") or "")
            created = it.get("created_at")
            sub = ""
            if isinstance(created, datetime):
                sub = created.strftime("%Y-%m-%d %H:%M")
            elif created:
                sub = str(created)
            rows.append({"version": str(ver), "title": title, "subtitle": sub, "content": body})
        self._rows = rows
        self.endResetModel()
