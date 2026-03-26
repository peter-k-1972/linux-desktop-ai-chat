"""QAbstractListModel for shell navigation lists (top areas, workspaces)."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class DomainNavModel(QAbstractListModel):
    """Primary (top-level) areas: roles ``areaId``, ``label`` (legacy alias ``domainId`` = areaId)."""

    DomainIdRole = Qt.ItemDataRole.UserRole + 1
    LabelRole = Qt.ItemDataRole.UserRole + 2
    AreaIdRole = DomainIdRole

    def __init__(self, entries: list[tuple[str, str]], parent=None) -> None:
        super().__init__(parent)
        self._rows = [{"areaId": i, "label": lbl} for i, lbl in entries]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role in (self.DomainIdRole, self.AreaIdRole):
            return row["areaId"]
        if role == self.LabelRole:
            return row["label"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.DomainIdRole: b"domainId",
            self.AreaIdRole: b"areaId",
            self.LabelRole: b"label",
        }

    def set_entries(self, entries: list[tuple[str, str]]) -> None:
        """Replace rows (e.g. when switching top area)."""
        self.beginResetModel()
        self._rows = [{"areaId": i, "label": lbl} for i, lbl in entries]
        self.endResetModel()


class WorkspaceNavModel(QAbstractListModel):
    """Operations (or future) sub-workspaces: ``workspaceId``, ``label``."""

    WorkspaceIdRole = Qt.ItemDataRole.UserRole + 1
    LabelRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, entries: list[tuple[str, str]], parent=None) -> None:
        super().__init__(parent)
        self._rows = [{"workspaceId": i, "label": lbl} for i, lbl in entries]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.WorkspaceIdRole:
            return row["workspaceId"]
        if role == self.LabelRole:
            return row["label"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.WorkspaceIdRole: b"workspaceId",
            self.LabelRole: b"label",
        }

    def set_entries(self, entries: list[tuple[str, str]]) -> None:
        self.beginResetModel()
        self._rows = [{"workspaceId": i, "label": lbl} for i, lbl in entries]
        self.endResetModel()
