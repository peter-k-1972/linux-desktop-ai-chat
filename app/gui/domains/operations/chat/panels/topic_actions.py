"""
TopicActions – Lightweight topic UX: create, rename, delete, assign, remove.

Topics are flat. Deleting a topic moves its chats to Ungrouped (chats are NOT deleted).
"""

from typing import Callable, Optional

from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt

from app.gui.domains.operations.chat.panels.topic_editor_dialog import (
    TopicCreateDialog,
    TopicRenameDialog,
    TopicDeleteConfirmDialog,
)


def create_topic(
    project_id: int,
    parent_widget=None,
    on_created: Optional[Callable[[int], None]] = None,
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
) -> bool:
    """Assign chat to topic. Returns True on success."""
    try:
        from app.services.chat_service import get_chat_service
        get_chat_service().move_chat_to_topic(project_id, chat_id, topic_id)
        if on_assigned:
            on_assigned()
        return True
    except Exception:
        return False


def remove_chat_from_topic(
    project_id: int,
    chat_id: int,
    on_removed: Optional[Callable[[], None]] = None,
) -> bool:
    """Remove chat from topic (move to Ungruppiert). Returns True on success."""
    return assign_chat_to_topic(project_id, chat_id, None, on_removed)


def build_topic_header_menu(
    topic_id: int,
    topic_name: str,
    chat_count: int,
    project_id: int,
    parent_widget,
    on_rename: Callable[[str], None],
    on_delete: Callable[[], None],
) -> QMenu:
    """
    Build context menu for topic section header: Rename, Delete.
    """
    menu = QMenu(parent_widget)
    menu.setObjectName("topicHeaderMenu")

    rename_action = menu.addAction("Umbenennen")
    rename_action.triggered.connect(
        lambda: _do_rename(topic_id, topic_name, parent_widget, on_rename)
    )

    delete_action = menu.addAction("Löschen…")
    delete_action.triggered.connect(
        lambda: _do_delete(topic_id, topic_name, chat_count, parent_widget, on_delete)
    )

    return menu


def build_chat_topic_menu(
    project_id: int,
    chat_id: int,
    current_topic_id: Optional[int],
    topics: list,
    parent_widget,
    on_moved: Callable[[], None],
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
        lambda: _do_remove(project_id, chat_id, on_moved)
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
                lambda checked=False, tid=tid: _do_assign(project_id, chat_id, tid, on_moved)
            )

    return menu


def _do_rename(
    topic_id: int,
    topic_name: str,
    parent_widget,
    on_renamed: Callable[[str], None],
) -> None:
    def _cb(new_name: str) -> None:
        on_renamed(new_name)

    rename_topic(topic_id, topic_name, parent_widget, _cb)


def _do_delete(
    topic_id: int,
    topic_name: str,
    chat_count: int,
    parent_widget,
    on_deleted: Callable[[], None],
) -> None:
    delete_topic(topic_id, topic_name, chat_count, parent_widget, on_deleted)


def _do_remove(
    project_id: int,
    chat_id: int,
    on_moved: Callable[[], None],
) -> None:
    remove_chat_from_topic(project_id, chat_id, on_moved)


def _do_assign(
    project_id: int,
    chat_id: int,
    topic_id: int,
    on_moved: Callable[[], None],
) -> None:
    assign_chat_to_topic(project_id, chat_id, topic_id, on_moved)
