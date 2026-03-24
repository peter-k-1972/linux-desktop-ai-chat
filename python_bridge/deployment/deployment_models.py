"""QAbstractListModel types for Deployment (Druckerei) QML."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class ReleaseListModel(QAbstractListModel):
    ReleaseIdRole = Qt.ItemDataRole.UserRole + 1
    DisplayNameRole = Qt.ItemDataRole.UserRole + 2
    VersionLabelRole = Qt.ItemDataRole.UserRole + 3
    LifecycleRole = Qt.ItemDataRole.UserRole + 4
    ArtifactKindRole = Qt.ItemDataRole.UserRole + 5
    ArtifactRefRole = Qt.ItemDataRole.UserRole + 6
    IsSelectedRole = Qt.ItemDataRole.UserRole + 7

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, str]] = []
        self._selected_id: str | None = None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.ReleaseIdRole:
            return row["releaseId"]
        if role == self.DisplayNameRole:
            return row["displayName"]
        if role == self.VersionLabelRole:
            return row["versionLabel"]
        if role == self.LifecycleRole:
            return row["lifecycle"]
        if role == self.ArtifactKindRole:
            return row["artifactKind"]
        if role == self.ArtifactRefRole:
            return row["artifactRef"]
        if role == self.IsSelectedRole:
            return row["releaseId"] == self._selected_id
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.ReleaseIdRole: b"releaseId",
            self.DisplayNameRole: b"displayName",
            self.VersionLabelRole: b"versionLabel",
            self.LifecycleRole: b"lifecycle",
            self.ArtifactKindRole: b"artifactKind",
            self.ArtifactRefRole: b"artifactRef",
            self.IsSelectedRole: b"isSelected",
        }

    def set_releases(self, rows: list[dict[str, str]], selected_id: str | None) -> None:
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


class BuildStepListModel(QAbstractListModel):
    StepIdRole = Qt.ItemDataRole.UserRole + 1
    LabelRole = Qt.ItemDataRole.UserRole + 2
    StateRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, str]] = [
            {"stepId": "build", "label": "Build", "state": "idle"},
            {"stepId": "validate", "label": "Validate", "state": "idle"},
            {"stepId": "package", "label": "Package", "state": "idle"},
            {"stepId": "publish", "label": "Publish", "state": "idle"},
        ]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.StepIdRole:
            return row["stepId"]
        if role == self.LabelRole:
            return row["label"]
        if role == self.StateRole:
            return row["state"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.StepIdRole: b"stepId",
            self.LabelRole: b"label",
            self.StateRole: b"state",
        }

    def reset_steps(self) -> None:
        for r in self._rows:
            r["state"] = "idle"
        top = self.index(0, 0)
        bottom = self.index(len(self._rows) - 1, 0)
        self.dataChanged.emit(top, bottom, [self.StateRole])

    def set_step_state(self, index: int, state: str) -> None:
        if not (0 <= index < len(self._rows)):
            return
        self._rows[index]["state"] = state
        idx = self.index(index, 0)
        self.dataChanged.emit(idx, idx, [self.StateRole])

    def set_all_done(self) -> None:
        for i in range(len(self._rows)):
            self._rows[i]["state"] = "done"
        top = self.index(0, 0)
        bottom = self.index(len(self._rows) - 1, 0)
        self.dataChanged.emit(top, bottom, [self.StateRole])


class ArtifactListModel(QAbstractListModel):
    ArtifactIdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    SubtitleRole = Qt.ItemDataRole.UserRole + 3
    ReleaseIdRole = Qt.ItemDataRole.UserRole + 4

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
        if role == self.ArtifactIdRole:
            return row["artifactId"]
        if role == self.TitleRole:
            return row["title"]
        if role == self.SubtitleRole:
            return row["subtitle"]
        if role == self.ReleaseIdRole:
            return row["releaseId"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.ArtifactIdRole: b"artifactId",
            self.TitleRole: b"title",
            self.SubtitleRole: b"subtitle",
            self.ReleaseIdRole: b"releaseId",
        }

    def set_rows(self, rows: list[dict[str, str]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class BuildLogListModel(QAbstractListModel):
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

    def prepend(self, message: str, time_label: str) -> None:
        self.beginInsertRows(QModelIndex(), 0, 0)
        self._rows.insert(0, {"message": message, "timeLabel": time_label})
        self._rows = self._rows[:200]
        self.endInsertRows()
