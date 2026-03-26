"""QAbstractListModel-Zeilen für Project War-Room (Liste, Chats, Workflows, Agenten, Dateien)."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class ProjectSummaryListModel(QAbstractListModel):
    ProjectIdRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    ActivityRole = Qt.ItemDataRole.UserRole + 3
    StatusRole = Qt.ItemDataRole.UserRole + 4
    IsSelectedRole = Qt.ItemDataRole.UserRole + 5

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []
        self._selected: int | None = None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.ProjectIdRole:
            return row["projectId"]
        if role == self.NameRole:
            return row["name"]
        if role == self.ActivityRole:
            return row["activity"]
        if role == self.StatusRole:
            return row["status"]
        if role == self.IsSelectedRole:
            return row["projectId"] == self._selected
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.ProjectIdRole: b"projectId",
            self.NameRole: b"name",
            self.ActivityRole: b"activity",
            self.StatusRole: b"status",
            self.IsSelectedRole: b"isSelected",
        }

    def set_rows(self, rows: list[dict[str, object]], selected_id: int | None) -> None:
        self.beginResetModel()
        self._selected = selected_id
        self._rows = rows
        self.endResetModel()

    def set_selected(self, project_id: int | None) -> None:
        if self._selected == project_id:
            return
        self._selected = project_id
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(max(0, len(self._rows) - 1), 0),
            [self.IsSelectedRole],
        )

    def project_ids(self) -> frozenset[int]:
        return frozenset(int(r["projectId"]) for r in self._rows)


class ProjectChatRowModel(QAbstractListModel):
    ChatIdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    SublineRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.ChatIdRole:
            return row["chatId"]
        if role == self.TitleRole:
            return row["title"]
        if role == self.SublineRole:
            return row["subline"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.ChatIdRole: b"chatId",
            self.TitleRole: b"title",
            self.SublineRole: b"subline",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class ProjectWorkflowRowModel(QAbstractListModel):
    WorkflowIdRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    SublineRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.WorkflowIdRole:
            return row["workflowId"]
        if role == self.NameRole:
            return row["name"]
        if role == self.SublineRole:
            return row["subline"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.WorkflowIdRole: b"workflowId",
            self.NameRole: b"name",
            self.SublineRole: b"subline",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class ProjectAgentRowModel(QAbstractListModel):
    AgentIdRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    SublineRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.AgentIdRole:
            return row["agentId"]
        if role == self.NameRole:
            return row["name"]
        if role == self.SublineRole:
            return row["subline"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.AgentIdRole: b"agentId",
            self.NameRole: b"name",
            self.SublineRole: b"subline",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class ProjectFileRowModel(QAbstractListModel):
    FileIdRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    SublineRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.FileIdRole:
            return row["fileId"]
        if role == self.NameRole:
            return row["name"]
        if role == self.SublineRole:
            return row["subline"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.FileIdRole: b"fileId",
            self.NameRole: b"name",
            self.SublineRole: b"subline",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
