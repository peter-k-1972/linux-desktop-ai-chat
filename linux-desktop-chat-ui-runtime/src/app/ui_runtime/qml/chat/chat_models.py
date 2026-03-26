"""QAbstractListModel implementations for QML Chat (roles only, no business logic)."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from app.ui_contracts.workspaces.chat import ChatListEntry, ChatMessageEntry


class ChatSessionListModel(QAbstractListModel):
    ChatIdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    IsActiveRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []
        self._active_id: int | None = None

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
        if role == self.IsActiveRole:
            return row["chatId"] == self._active_id
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.ChatIdRole: b"chatId",
            self.TitleRole: b"title",
            self.IsActiveRole: b"isActive",
        }

    def set_chats(self, chats: tuple[ChatListEntry, ...], active_id: int | None) -> None:
        self.beginResetModel()
        self._active_id = active_id
        self._rows = [
            {"chatId": e.chat_id, "title": e.title or f"Chat {e.chat_id}"} for e in chats
        ]
        self.endResetModel()

    def update_active(self, active_id: int | None) -> None:
        if self._active_id == active_id:
            return
        self._active_id = active_id
        if not self._rows:
            return
        top = self.index(0, 0)
        bottom = self.index(len(self._rows) - 1, 0)
        self.dataChanged.emit(top, bottom, [self.IsActiveRole])


class ChatMessageListModel(QAbstractListModel):
    RoleRole = Qt.ItemDataRole.UserRole + 1
    ContentRole = Qt.ItemDataRole.UserRole + 2
    ModelLabelRole = Qt.ItemDataRole.UserRole + 3
    IsStreamingRole = Qt.ItemDataRole.UserRole + 4

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, object]] = []
        self._streaming_index: int | None = None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.RoleRole:
            return row["role"]
        if role == self.ContentRole:
            return row["content"]
        if role == self.ModelLabelRole:
            return row.get("modelLabel") or ""
        if role == self.IsStreamingRole:
            return bool(row.get("isStreaming", False))
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.RoleRole: b"role",
            self.ContentRole: b"content",
            self.ModelLabelRole: b"modelLabel",
            self.IsStreamingRole: b"isStreaming",
        }

    def load_from_entries(self, entries: tuple[ChatMessageEntry, ...]) -> None:
        self.beginResetModel()
        self._streaming_index = None
        self._rows = [
            {
                "role": e.role,
                "content": e.content,
                "modelLabel": e.model_label or "",
                "isStreaming": False,
            }
            for e in entries
        ]
        self.endResetModel()

    def clear(self) -> None:
        self.beginResetModel()
        self._rows = []
        self._streaming_index = None
        self.endResetModel()

    def append_user(self, text: str) -> None:
        row = len(self._rows)
        self.beginInsertRows(QModelIndex(), row, row)
        self._rows.append(
            {
                "role": "user",
                "content": text,
                "modelLabel": "",
                "isStreaming": False,
            }
        )
        self.endInsertRows()

    def append_assistant_placeholder(self, model: str) -> None:
        row = len(self._rows)
        self.beginInsertRows(QModelIndex(), row, row)
        self._rows.append(
            {
                "role": "assistant",
                "content": "",
                "modelLabel": model,
                "isStreaming": True,
            }
        )
        self._streaming_index = row
        self.endInsertRows()

    def update_last_assistant(self, text: str) -> None:
        """Live-Bubble: nur sichtbarer Assistententext (Content-Kanal), nicht Reasoning/Thinking."""
        if self._streaming_index is None or not (0 <= self._streaming_index < len(self._rows)):
            return
        idx = self._streaming_index
        self._rows[idx]["content"] = text
        ix = self.index(idx, 0)
        self.dataChanged.emit(ix, ix, [self.ContentRole])

    def finalize_streaming(self) -> None:
        if self._streaming_index is None or not (0 <= self._streaming_index < len(self._rows)):
            self._streaming_index = None
            return
        idx = self._streaming_index
        self._rows[idx]["isStreaming"] = False
        ix = self.index(idx, 0)
        self.dataChanged.emit(ix, ix, [self.IsStreamingRole])
        self._streaming_index = None

    def set_last_completion_label(self, status: str | None) -> None:
        del status
