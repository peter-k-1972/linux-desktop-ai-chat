"""QAbstractListModel types for Agents domain QML."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class AgentRosterListModel(QAbstractListModel):
    AgentIdRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    RoleRole = Qt.ItemDataRole.UserRole + 3
    ModelRole = Qt.ItemDataRole.UserRole + 4
    StatusRole = Qt.ItemDataRole.UserRole + 5
    IsSelectedRole = Qt.ItemDataRole.UserRole + 6

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []
        self._selected_id: str | None = None

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
        if role == self.RoleRole:
            return row["role"]
        if role == self.ModelRole:
            return row["assignedModel"]
        if role == self.StatusRole:
            return row["status"]
        if role == self.IsSelectedRole:
            return row["agentId"] == self._selected_id
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.AgentIdRole: b"agentId",
            self.NameRole: b"name",
            self.RoleRole: b"role",
            self.ModelRole: b"assignedModel",
            self.StatusRole: b"status",
            self.IsSelectedRole: b"isSelected",
        }

    def set_agents(self, rows: list[dict[str, object]], selected_id: str | None) -> None:
        self.beginResetModel()
        self._selected_id = selected_id
        self._rows = rows
        self.endResetModel()

    def update_selection(self, selected_id: str | None) -> None:
        if self._selected_id == selected_id:
            return
        self._selected_id = selected_id
        if not self._rows:
            return
        top = self.index(0, 0)
        bottom = self.index(len(self._rows) - 1, 0)
        self.dataChanged.emit(top, bottom, [self.IsSelectedRole])


class AgentTaskListModel(QAbstractListModel):
    TaskIdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    StateRole = Qt.ItemDataRole.UserRole + 3
    AgentLabelRole = Qt.ItemDataRole.UserRole + 4
    TimeLabelRole = Qt.ItemDataRole.UserRole + 5

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
        if role == self.TaskIdRole:
            return row["taskId"]
        if role == self.TitleRole:
            return row["title"]
        if role == self.StateRole:
            return row["state"]
        if role == self.AgentLabelRole:
            return row["agentLabel"]
        if role == self.TimeLabelRole:
            return row["timeLabel"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.TaskIdRole: b"taskId",
            self.TitleRole: b"title",
            self.StateRole: b"state",
            self.AgentLabelRole: b"agentLabel",
            self.TimeLabelRole: b"timeLabel",
        }

    def set_rows(self, rows: list[dict[str, str]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class ActivityFeedListModel(QAbstractListModel):
    MessageRole = Qt.ItemDataRole.UserRole + 1
    TimeLabelRole = Qt.ItemDataRole.UserRole + 2

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
        if role == self.MessageRole:
            return row["message"]
        if role == self.TimeLabelRole:
            return row["timeLabel"]
        return None

    def roleNames(self):  # noqa: N802
        return {self.MessageRole: b"message", self.TimeLabelRole: b"timeLabel"}

    def set_rows(self, rows: list[dict[str, str]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
