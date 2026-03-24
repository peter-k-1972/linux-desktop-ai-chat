"""QAbstractListModel für Workflow-Liste, Graph-Knoten, Kanten und Run-Historie."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class WorkflowSummaryListModel(QAbstractListModel):
    WorkflowIdRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    VersionRole = Qt.ItemDataRole.UserRole + 3
    SublineRole = Qt.ItemDataRole.UserRole + 4
    IsSelectedRole = Qt.ItemDataRole.UserRole + 5

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []
        self._selected: str | None = None

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
        if role == self.VersionRole:
            return row["version"]
        if role == self.SublineRole:
            return row["subline"]
        if role == self.IsSelectedRole:
            return row["workflowId"] == self._selected
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.WorkflowIdRole: b"workflowId",
            self.NameRole: b"name",
            self.VersionRole: b"version",
            self.SublineRole: b"subline",
            self.IsSelectedRole: b"isSelected",
        }

    def set_rows(self, rows: list[dict[str, object]], selected_id: str | None) -> None:
        self.beginResetModel()
        self._selected = selected_id
        self._rows = rows
        self.endResetModel()

    def set_selected(self, workflow_id: str | None) -> None:
        if self._selected == workflow_id:
            return
        self._selected = workflow_id
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(max(0, len(self._rows) - 1), 0),
            [self.IsSelectedRole],
        )


class WorkflowGraphNodeModel(QAbstractListModel):
    NodeIdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    RoleKeyRole = Qt.ItemDataRole.UserRole + 3
    PosXRole = Qt.ItemDataRole.UserRole + 4
    PosYRole = Qt.ItemDataRole.UserRole + 5
    IsSelectedRole = Qt.ItemDataRole.UserRole + 6

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []
        self._selected: str | None = None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.NodeIdRole:
            return row["nodeId"]
        if role == self.TitleRole:
            return row["title"]
        if role == self.RoleKeyRole:
            return row["roleKey"]
        if role == self.PosXRole:
            return row["posX"]
        if role == self.PosYRole:
            return row["posY"]
        if role == self.IsSelectedRole:
            return row["nodeId"] == self._selected
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.NodeIdRole: b"nodeId",
            self.TitleRole: b"title",
            self.RoleKeyRole: b"roleKey",
            self.PosXRole: b"posX",
            self.PosYRole: b"posY",
            self.IsSelectedRole: b"isSelected",
        }

    def set_graph(self, rows: list[dict[str, object]], selected_node: str | None) -> None:
        self.beginResetModel()
        self._selected = selected_node
        self._rows = rows
        self.endResetModel()

    def set_selected(self, node_id: str | None) -> None:
        if self._selected == node_id:
            return
        self._selected = node_id
        if not self._rows:
            return
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(len(self._rows) - 1, 0),
            [self.IsSelectedRole],
        )

    def update_node_pos(self, node_id: str, x: float, y: float) -> None:
        for i, row in enumerate(self._rows):
            if row["nodeId"] == node_id:
                row["posX"] = x
                row["posY"] = y
                idx = self.index(i, 0)
                self.dataChanged.emit(idx, idx, [self.PosXRole, self.PosYRole])
                return


class WorkflowGraphEdgeModel(QAbstractListModel):
    EdgeIdRole = Qt.ItemDataRole.UserRole + 1
    SxRole = Qt.ItemDataRole.UserRole + 2
    SyRole = Qt.ItemDataRole.UserRole + 3
    TxRole = Qt.ItemDataRole.UserRole + 4
    TyRole = Qt.ItemDataRole.UserRole + 5
    FlowKindRole = Qt.ItemDataRole.UserRole + 6

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
        if role == self.EdgeIdRole:
            return row["edgeId"]
        if role == self.SxRole:
            return row["sx"]
        if role == self.SyRole:
            return row["sy"]
        if role == self.TxRole:
            return row["tx"]
        if role == self.TyRole:
            return row["ty"]
        if role == self.FlowKindRole:
            return row["flowKind"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.EdgeIdRole: b"edgeId",
            self.SxRole: b"sx",
            self.SyRole: b"sy",
            self.TxRole: b"tx",
            self.TyRole: b"ty",
            self.FlowKindRole: b"flowKind",
        }

    def set_edges(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class WorkflowRunHistoryModel(QAbstractListModel):
    RunIdRole = Qt.ItemDataRole.UserRole + 1
    StatusRole = Qt.ItemDataRole.UserRole + 2
    DurationRole = Qt.ItemDataRole.UserRole + 3
    StartedRole = Qt.ItemDataRole.UserRole + 4

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
        if role == self.RunIdRole:
            return row["runId"]
        if role == self.StatusRole:
            return row["status"]
        if role == self.DurationRole:
            return row["duration"]
        if role == self.StartedRole:
            return row["started"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.RunIdRole: b"runId",
            self.StatusRole: b"status",
            self.DurationRole: b"duration",
            self.StartedRole: b"started",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
