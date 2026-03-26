"""QAbstractListModel-Zeilen für OperationsReadViewModel."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class AuditEventRowModel(QAbstractListModel):
    EventDbIdRole = Qt.ItemDataRole.UserRole + 1
    OccurredAtRole = Qt.ItemDataRole.UserRole + 2
    EventTypeRole = Qt.ItemDataRole.UserRole + 3
    SummaryRole = Qt.ItemDataRole.UserRole + 4
    ProjectIdRole = Qt.ItemDataRole.UserRole + 5
    WorkflowIdRole = Qt.ItemDataRole.UserRole + 6
    RunIdRole = Qt.ItemDataRole.UserRole + 7

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
        if role == self.EventDbIdRole:
            return row["eventDbId"]
        if role == self.OccurredAtRole:
            return row["occurredAt"]
        if role == self.EventTypeRole:
            return row["eventType"]
        if role == self.SummaryRole:
            return row["summary"]
        if role == self.ProjectIdRole:
            return row["projectId"]
        if role == self.WorkflowIdRole:
            return row["workflowId"]
        if role == self.RunIdRole:
            return row["runId"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.EventDbIdRole: b"eventDbId",
            self.OccurredAtRole: b"occurredAt",
            self.EventTypeRole: b"eventType",
            self.SummaryRole: b"summary",
            self.ProjectIdRole: b"projectId",
            self.WorkflowIdRole: b"workflowId",
            self.RunIdRole: b"runId",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class RuntimeIncidentRowModel(QAbstractListModel):
    IncidentIdRole = Qt.ItemDataRole.UserRole + 1
    LastSeenRole = Qt.ItemDataRole.UserRole + 2
    StatusRole = Qt.ItemDataRole.UserRole + 3
    SeverityRole = Qt.ItemDataRole.UserRole + 4
    TitleRole = Qt.ItemDataRole.UserRole + 5
    WorkflowIdRole = Qt.ItemDataRole.UserRole + 6
    RunIdRole = Qt.ItemDataRole.UserRole + 7
    CountRole = Qt.ItemDataRole.UserRole + 8

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
        if role == self.IncidentIdRole:
            return row["incidentId"]
        if role == self.LastSeenRole:
            return row["lastSeenAt"]
        if role == self.StatusRole:
            return row["status"]
        if role == self.SeverityRole:
            return row["severity"]
        if role == self.TitleRole:
            return row["title"]
        if role == self.WorkflowIdRole:
            return row["workflowId"]
        if role == self.RunIdRole:
            return row["runId"]
        if role == self.CountRole:
            return row["occurrenceCount"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.IncidentIdRole: b"incidentId",
            self.LastSeenRole: b"lastSeenAt",
            self.StatusRole: b"status",
            self.SeverityRole: b"severity",
            self.TitleRole: b"title",
            self.WorkflowIdRole: b"workflowId",
            self.RunIdRole: b"runId",
            self.CountRole: b"occurrenceCount",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class QaIndexIncidentRowModel(QAbstractListModel):
    IncidentIdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    StatusRole = Qt.ItemDataRole.UserRole + 3
    SeverityRole = Qt.ItemDataRole.UserRole + 4
    SubsystemRole = Qt.ItemDataRole.UserRole + 5
    BindingTextRole = Qt.ItemDataRole.UserRole + 6

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
        if role == self.IncidentIdRole:
            return row["incidentId"]
        if role == self.TitleRole:
            return row["title"]
        if role == self.StatusRole:
            return row["status"]
        if role == self.SeverityRole:
            return row["severity"]
        if role == self.SubsystemRole:
            return row["subsystem"]
        if role == self.BindingTextRole:
            return row["bindingText"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.IncidentIdRole: b"incidentId",
            self.TitleRole: b"title",
            self.StatusRole: b"status",
            self.SeverityRole: b"severity",
            self.SubsystemRole: b"subsystem",
            self.BindingTextRole: b"bindingText",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class AuditFollowupRowModel(QAbstractListModel):
    CategoryRole = Qt.ItemDataRole.UserRole + 1
    SourceRole = Qt.ItemDataRole.UserRole + 2
    DescriptionRole = Qt.ItemDataRole.UserRole + 3
    LocationRole = Qt.ItemDataRole.UserRole + 4

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
        if role == self.CategoryRole:
            return row["category"]
        if role == self.SourceRole:
            return row["source"]
        if role == self.DescriptionRole:
            return row["description"]
        if role == self.LocationRole:
            return row["location"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.CategoryRole: b"category",
            self.SourceRole: b"source",
            self.DescriptionRole: b"description",
            self.LocationRole: b"location",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class PlatformCheckRowModel(QAbstractListModel):
    CheckIdRole = Qt.ItemDataRole.UserRole + 1
    SeverityRole = Qt.ItemDataRole.UserRole + 2
    TitleRole = Qt.ItemDataRole.UserRole + 3
    DetailRole = Qt.ItemDataRole.UserRole + 4

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
        if role == self.CheckIdRole:
            return row["checkId"]
        if role == self.SeverityRole:
            return row["severity"]
        if role == self.TitleRole:
            return row["title"]
        if role == self.DetailRole:
            return row["detail"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.CheckIdRole: b"checkId",
            self.SeverityRole: b"severity",
            self.TitleRole: b"title",
            self.DetailRole: b"detail",
        }

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
