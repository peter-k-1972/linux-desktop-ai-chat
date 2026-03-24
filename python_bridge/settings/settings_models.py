"""QAbstractListModel für strukturierte Settings-Zeilen (Archiv / Ledger)."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class SettingsLedgerListModel(QAbstractListModel):
    """Eine Zeile = ein steuerbares Setting mit Metadaten für die UI."""

    KeyRole = Qt.ItemDataRole.UserRole + 1
    LabelRole = Qt.ItemDataRole.UserRole + 2
    ValueRole = Qt.ItemDataRole.UserRole + 3
    KindRole = Qt.ItemDataRole.UserRole + 4
    OptionsRole = Qt.ItemDataRole.UserRole + 5
    DescriptionRole = Qt.ItemDataRole.UserRole + 6

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
        if role == self.KeyRole:
            return row.get("key", "")
        if role == self.LabelRole:
            return row["label"]
        if role == self.ValueRole:
            return row["value"]
        if role == self.KindRole:
            return row["kind"]
        if role == self.OptionsRole:
            return row.get("options", "")
        if role == self.DescriptionRole:
            return row.get("description", "")
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.KeyRole: b"settingKey",
            self.LabelRole: b"label",
            self.ValueRole: b"value",
            self.KindRole: b"kind",
            self.OptionsRole: b"options",
            self.DescriptionRole: b"description",
        }

    def set_rows(self, rows: list[dict[str, str]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
