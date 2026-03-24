"""QAbstractListModel exposing domain id + label for QML NavRail."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class DomainNavModel(QAbstractListModel):
    DomainIdRole = Qt.ItemDataRole.UserRole + 1
    LabelRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, entries: list[tuple[str, str]], parent=None) -> None:
        super().__init__(parent)
        self._rows = [{"domainId": i, "label": lbl} for i, lbl in entries]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.DomainIdRole:
            return row["domainId"]
        if role == self.LabelRole:
            return row["label"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.DomainIdRole: b"domainId",
            self.LabelRole: b"label",
        }
