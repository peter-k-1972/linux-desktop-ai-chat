"""
TopicActions – Lightweight topic UX: create, rename, delete, assign, remove.

Mit ``chat_ops`` (:class:`ChatOperationsPort`) keine direkten Topic-/Chat-Service-Imports;
ohne ``chat_ops`` Legacy-Fallback.
"""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtWidgets import QMenu

from app.ui_application.ports.chat_operations_port import ChatOperationsPort
from app.gui.domains.operations.chat.panels.topic_editor_dialog import (
    TopicCreateDialog,
    TopicRenameDialog,
    TopicDeleteConfirmDialog,
)


def create_topic(
    project_id: int,
    parent_widget=None,
    on_created: Optional[Callable[[int], None]] = None,
    *,
    chat_ops: ChatOperationsPort | None = None,
) -> Optional[int]:
    """
    Show lightweight create dialog and create topic.
    Returns topic_id on success, None on cancel.
    """
    dlg = TopicCreateDialog(parent_widget)
    if dlg.exec() != dlg.DialogCode.Accepted:
        return None
    name = dlg.get_name()
    if not name:
        return None
    try:
        if chat_ops is not None:
            topic_id = chat_ops.create_topic(project_id, name)
        else:
            from app.services.topic_service import get_topic_service

            topic_id = get_topic_service().create_topic(project_id, name)
        if on_created:
            on_created(topic_id)
        return topic_id
    except Exception:
        return None


def rename_topic(
    topic_id: int,
    current_name: str,
    parent_widget=None,
    on_renamed: Optional[Callable[[str], None]] = None,
    *,
    chat_ops: ChatOperationsPort | None = None,
) -> bool:
    """
    Show lightweight rename dialog and update topic.
    Returns True on success.
    """
    dlg = TopicRenameDialog(current_name, parent_widget)
    if dlg.exec() != dlg.DialogCode.Accepted:
        return False
    new_name = dlg.get_name()
    if not new_name or new_name == current_name:
        return False
    try:
        if chat_ops is not None:
            chat_ops.update_topic_name(topic_id, new_name)
        else:
            from app.services.topic_service import get_topic_service

            get_topic_service().update_topic(topic_id, name=new_name)
        if on_renamed:
            on_renamed(new_name)
        return True
    except Exception:
        return False


def delete_topic(
    topic_id: int,
    topic_name: str,
    chat_count: int,
    parent_widget=None,
    on_deleted: Optional[Callable[[], None]] = None,
    *,
    chat_ops: ChatOperationsPort | None = None,
) -> bool:
    """
    Show confirmation dialog and delete topic.
    Chats move to Ungrouped (NOT deleted).
    Returns True on success.
    """
    dlg = TopicDeleteConfirmDialog(topic_name, chat_count, parent_widget)
    if dlg.exec() != dlg.DialogCode.Accepted:
        return False
    try:
        if chat_ops is not None:
            chat_ops.delete_topic_by_id(topic_id)
        else:
            from app.services.topic_service import get_topic_service

            get_topic_service().delete_topic(topic_id)
        if on_deleted:
            on_deleted()
        return True
    except Exception:
        return False


def assign_chat_to_topic(
    project_id: int,
    chat_id: int,
    topic_id: int,
    on_assigned: Optional[Callable[[], None]] = None,
    *,
    chat_ops: ChatOperationsPort | None = None,
) -> bool:
    """Assign chat to topic. Returns True on success."""
    return _move_chat_to_topic_impl(
        project_id, chat_id, topic_id, on_assigned, chat_ops=chat_ops
    )


def remove_chat_from_topic(
    project_id: int,
    chat_id: int,
    on_removed: Optional[Callable[[], None]] = None,
    *,
    chat_ops: ChatOperationsPort | None = None,
) -> bool:
    """Remove chat from topic (move to Ungruppiert). Returns True on success."""
    return _move_chat_to_topic_impl(
        project_id, chat_id, None, on_removed, chat_ops=chat_ops
    )


def _move_chat_to_topic_impl(
    project_id: int,
    chat_id: int,
    topic_id: int | None,
    on_done: Optional[Callable[[], None]] = None,
    *,
    chat_ops: ChatOperationsPort | None = None,
) -> bool:
    try:
        if chat_ops is not None:
            chat_ops.move_chat_to_topic(project_id, chat_id, topic_id)
        else:
            from app.services.chat_service import get_chat_service

            get_chat_service().move_chat_to_topic(project_id, chat_id, topic_id)
        if on_done:
            on_done()
        return True
    except Exception:
        return False


def build_topic_header_menu(
    topic_id: int,
    topic_name: str,
    chat_count: int,
    project_id: int,
    parent_widget,
    on_rename: Callable[[str], None],
    on_delete: Callable[[], None],
    *,
    chat_ops: ChatOperationsPort | None = None,
) -> QMenu:
    """
    Build context menu for topic section header: Rename, Delete.
    """
    menu = QMenu(parent_widget)
    menu.setObjectName("topicHeaderMenu")

    rename_action = menu.addAction("Umbenennen")
    rename_action.triggered.connect(
        lambda: _do_rename(topic_id, topic_name, parent_widget, on_rename, chat_ops)
    )

    delete_action = menu.addAction("Löschen…")
    delete_action.triggered.connect(
        lambda: _do_delete(
            topic_id, topic_name, chat_count, parent_widget, on_delete, chat_ops
        )
    )

    return menu


def build_chat_topic_menu(
    project_id: int,
    chat_id: int,
    current_topic_id: Optional[int],
    topics: list,
    parent_widget,
    on_moved: Callable[[], None],
    *,
    chat_ops: ChatOperationsPort | None = None,
) -> QMenu:
    """
    Build context menu for chat item: Move to topic / Remove from topic.
    topics: list of dicts with id, name
    """
    menu = QMenu(parent_widget)
    menu.setObjectName("chatTopicMenu")

    remove_action = menu.addAction("Zu Ungruppiert verschieben")
    remove_action.setEnabled(current_topic_id is not None)
    remove_action.triggered.connect(
        lambda: _do_remove(project_id, chat_id, on_moved, chat_ops)
    )

    if topics:
        menu.addSeparator()
        for t in topics:
            tid = t.get("id")
            tname = t.get("name", "Topic")
            if tid is None:
                continue
            action = menu.addAction(tname)
            action.setEnabled(tid != current_topic_id)
            action.triggered.connect(
                lambda checked=False, tid=tid: _do_assign(
                    project_id, chat_id, tid, on_moved, chat_ops
                )
            )

    return menu


def _do_rename(
    topic_id: int,
    topic_name: str,
    parent_widget,
    on_renamed: Callable[[str], None],
    chat_ops: ChatOperationsPort | None,
) -> None:
    def _cb(new_name: str) -> None:
        on_renamed(new_name)

    rename_topic(topic_id, topic_name, parent_widget, _cb, chat_ops=chat_ops)


def _do_delete(
    topic_id: int,
    topic_name: str,
    chat_count: int,
    parent_widget,
    on_deleted: Callable[[], None],
    chat_ops: ChatOperationsPort | None,
) -> None:
    delete_topic(
        topic_id, topic_name, chat_count, parent_widget, on_deleted, chat_ops=chat_ops
    )


def _do_remove(
    project_id: int,
    chat_id: int,
    on_moved: Callable[[], None],
    chat_ops: ChatOperationsPort | None,
) -> None:
    remove_chat_from_topic(project_id, chat_id, on_moved, chat_ops=chat_ops)


def _do_assign(
    project_id: int,
    chat_id: int,
    topic_id: int,
    on_moved: Callable[[], None],
    chat_ops: ChatOperationsPort | None,
) -> None:
    assign_chat_to_topic(project_id, chat_id, topic_id, on_moved, chat_ops=chat_ops)
