"""
ChatItemContextMenu – Context menu for chat list items.

Actions: Rename, Move to Topic, Move to Ungruppiert, Pin/Unpin,
Archive/Unarchive, Duplicate, Delete.

Advanced actions only in context menu; default list stays clean.
Delete requires confirmation.
"""

from typing import Callable, Optional

from PySide6.QtWidgets import QMenu, QInputDialog, QMessageBox
from PySide6.QtCore import Qt


def build_chat_item_context_menu(
    project_id: Optional[int],
    chat_id: int,
    chat_title: str,
    current_topic_id: Optional[int],
    is_pinned: bool,
    is_archived: bool,
    topics: list,
    parent_widget,
    on_action: Callable[[], None],
    on_chat_deleted: Optional[Callable[[int], None]] = None,
) -> QMenu:
    """
    Build context menu for a chat item.
    project_id=None: nur Rename und Delete (Chat ohne Projekt).
    """
    menu = QMenu(parent_widget)
    menu.setObjectName("chatItemContextMenu")

    # Rename (immer verfügbar)
    rename_action = menu.addAction("Umbenennen")
    rename_action.triggered.connect(
        lambda: _do_rename(chat_id, chat_title, parent_widget, on_action)
    )

    # Projekt-spezifische Aktionen nur bei project_id
    if project_id is not None:
        menu.addSeparator()

        # Move to Topic (submenu)
        move_sub = menu.addMenu("Zu Topic verschieben")
        move_to_ungrouped = move_sub.addAction("Ungruppiert")
        move_to_ungrouped.setEnabled(current_topic_id is not None)
        move_to_ungrouped.triggered.connect(
            lambda: _do_move_to_topic(project_id, chat_id, None, on_action)
        )
        if topics:
            move_sub.addSeparator()
            for t in topics:
                tid = t.get("id")
                tname = t.get("name", "Topic")
                if tid is None:
                    continue
                action = move_sub.addAction(tname)
                action.setEnabled(tid != current_topic_id)
                action.triggered.connect(
                    lambda checked=False, tid=tid: _do_move_to_topic(
                        project_id, chat_id, tid, on_action
                    )
                )

        # Pin / Unpin
        if is_pinned:
            pin_action = menu.addAction("Lösen")
            pin_action.triggered.connect(
                lambda: _do_pin(project_id, chat_id, False, on_action)
            )
        else:
            pin_action = menu.addAction("Anheften")
            pin_action.setEnabled(not is_archived)
            pin_action.triggered.connect(
                lambda: _do_pin(project_id, chat_id, True, on_action)
            )

        # Archive / Unarchive
        if is_archived:
            archive_action = menu.addAction("Reaktivieren")
            archive_action.triggered.connect(
                lambda: _do_archive(project_id, chat_id, False, on_action)
            )
        else:
            archive_action = menu.addAction("Archivieren")
            archive_action.triggered.connect(
                lambda: _do_archive(project_id, chat_id, True, on_action)
            )

        menu.addSeparator()

        # Duplicate
        dup_action = menu.addAction("Duplizieren")
        dup_action.triggered.connect(
            lambda: _do_duplicate(project_id, chat_id, current_topic_id, on_action)
        )

    menu.addSeparator()

    # Delete (immer verfügbar)
    delete_action = menu.addAction("Löschen…")
    delete_action.triggered.connect(
        lambda cid=chat_id: _do_delete(cid, chat_title, parent_widget, on_action, on_chat_deleted)
    )

    return menu


def _do_rename(
    chat_id: int,
    current_title: str,
    parent_widget,
    on_action: Callable[[], None],
) -> None:
    title, ok = QInputDialog.getText(
        parent_widget,
        "Chat umbenennen",
        "Neuer Titel:",
        text=current_title or "Neuer Chat",
    )
    if not ok or not (title := (title or "").strip()):
        return
    try:
        from app.services.chat_service import get_chat_service
        get_chat_service().save_chat_title(chat_id, title)
        on_action()
    except Exception:
        pass


def _do_move_to_topic(
    project_id: int,
    chat_id: int,
    topic_id: Optional[int],
    on_action: Callable[[], None],
) -> None:
    try:
        from app.services.chat_service import get_chat_service
        get_chat_service().move_chat_to_topic(project_id, chat_id, topic_id)
        on_action()
    except Exception:
        pass


def _do_pin(
    project_id: int,
    chat_id: int,
    pinned: bool,
    on_action: Callable[[], None],
) -> None:
    try:
        from app.services.chat_service import get_chat_service
        get_chat_service().set_chat_pinned(project_id, chat_id, pinned)
        on_action()
    except Exception:
        pass


def _do_archive(
    project_id: int,
    chat_id: int,
    archived: bool,
    on_action: Callable[[], None],
) -> None:
    try:
        from app.services.chat_service import get_chat_service
        get_chat_service().set_chat_archived(project_id, chat_id, archived)
        on_action()
    except Exception:
        pass


def _do_duplicate(
    project_id: int,
    chat_id: int,
    topic_id: Optional[int],
    on_action: Callable[[], None],
) -> None:
    try:
        from app.services.chat_service import get_chat_service
        new_id = get_chat_service().duplicate_chat(chat_id, project_id, topic_id)
        if new_id is not None:
            on_action()
    except Exception:
        pass


def build_context_bar_context_menu(
    chat_id: Optional[int],
    project_id: Optional[int],
    chat_title: str,
    current_topic_id: Optional[int],
    is_pinned: bool,
    is_archived: bool,
    topics: list,
    parent_widget,
    on_action: Callable[[], None],
    on_project_switch_requested: Callable[[], None],
    on_new_chat_requested: Callable[[], None],
    on_chat_deleted: Optional[Callable[[int], None]] = None,
) -> "QMenu":
    """
    Kontextmenü für die ChatContextBar (Rechtsklick).
    Enthält: Projekt wechseln, Chat umbenennen, Topic, Neuer Chat, Chat verschieben,
    sowie Pin/Archive/Duplicate/Delete wenn Chat ausgewählt.
    """
    from PySide6.QtWidgets import QMenu

    menu = QMenu(parent_widget)
    menu.setObjectName("chatContextBarMenu")

    # Projekt wechseln (immer)
    switch_action = menu.addAction("Projekt wechseln…")
    switch_action.triggered.connect(on_project_switch_requested)

    menu.addSeparator()

    if chat_id is not None:
        # Chat umbenennen
        rename_action = menu.addAction("Chat umbenennen")
        rename_action.triggered.connect(
            lambda: _do_rename(chat_id, chat_title, parent_widget, on_action)
        )

        if project_id is not None:
            menu.addSeparator()
            move_sub = menu.addMenu("Zu Topic verschieben")
            move_to_ungrouped = move_sub.addAction("Ungruppiert")
            move_to_ungrouped.setEnabled(current_topic_id is not None)
            move_to_ungrouped.triggered.connect(
                lambda: _do_move_to_topic(project_id, chat_id, None, on_action)
            )
            if topics:
                move_sub.addSeparator()
                for t in topics:
                    tid = t.get("id")
                    tname = t.get("name", "Topic")
                    if tid is None:
                        continue
                    action = move_sub.addAction(tname)
                    action.setEnabled(tid != current_topic_id)
                    action.triggered.connect(
                        lambda checked=False, tid=tid: _do_move_to_topic(
                            project_id, chat_id, tid, on_action
                        )
                    )

            menu.addSeparator()
            if is_pinned:
                pin_action = menu.addAction("Lösen")
                pin_action.triggered.connect(
                    lambda: _do_pin(project_id, chat_id, False, on_action)
                )
            else:
                pin_action = menu.addAction("Anheften")
                pin_action.setEnabled(not is_archived)
                pin_action.triggered.connect(
                    lambda: _do_pin(project_id, chat_id, True, on_action)
                )
            if is_archived:
                archive_action = menu.addAction("Reaktivieren")
                archive_action.triggered.connect(
                    lambda: _do_archive(project_id, chat_id, False, on_action)
                )
            else:
                archive_action = menu.addAction("Archivieren")
                archive_action.triggered.connect(
                    lambda: _do_archive(project_id, chat_id, True, on_action)
                )
            menu.addSeparator()
            dup_action = menu.addAction("Duplizieren")
            dup_action.triggered.connect(
                lambda: _do_duplicate(project_id, chat_id, current_topic_id, on_action)
            )

        menu.addSeparator()
        move_project_sub = menu.addMenu(
            "Chat verschieben zu…" if project_id is not None else "Chat zu Projekt hinzufügen…"
        )
        _populate_move_to_project_menu(move_project_sub, chat_id, project_id, on_action)

        menu.addSeparator()
        delete_action = menu.addAction("Löschen…")
        delete_action.triggered.connect(
            lambda cid=chat_id: _do_delete(
                cid, chat_title, parent_widget, on_action, on_chat_deleted
            )
        )
    else:
        # Kein Chat ausgewählt – nur Neuer Chat
        new_action = menu.addAction("Neuer Chat")
        new_action.triggered.connect(on_new_chat_requested)

    return menu


def _populate_move_to_project_menu(
    submenu: "QMenu",
    chat_id: int,
    current_project_id: Optional[int],
    on_action: Callable[[], None],
) -> None:
    """Füllt Submenu mit anderen Projekten zum Verschieben."""
    try:
        from app.services.project_service import get_project_service

        svc = get_project_service()
        projects = svc.list_projects()
        has_any = False
        for p in projects:
            pid = p.get("project_id")
            pname = p.get("name", "Projekt")
            if pid is None or pid == current_project_id:
                continue
            has_any = True
            action = submenu.addAction(pname)
            action.triggered.connect(
                lambda checked=False, pid=pid: _do_move_chat_to_project(
                    chat_id, pid, on_action
                )
            )
        if not has_any:
            submenu.addAction("Keine anderen Projekte").setEnabled(False)
    except Exception:
        submenu.addAction("Fehler beim Laden").setEnabled(False)


def _do_move_chat_to_project(
    chat_id: int,
    target_project_id: int,
    on_action: Callable[[], None],
) -> None:
    """Verschiebt Chat zu anderem Projekt."""
    try:
        from app.services.project_service import get_project_service
        from app.core.context.project_context_manager import get_project_context_manager

        svc = get_project_service()
        svc.move_chat_to_project(chat_id, target_project_id)
        # Aktives Projekt wechseln, damit Nutzer den Chat weiter sieht
        mgr = get_project_context_manager()
        mgr.set_active_project(target_project_id)
        on_action()
    except Exception:
        pass


def _do_delete(
    chat_id: int,
    chat_title: str,
    parent_widget,
    on_action: Callable[[], None],
    on_chat_deleted: Optional[Callable[[int], None]] = None,
) -> None:
    if not isinstance(chat_id, int) or chat_id <= 0:
        return
    reply = QMessageBox.question(
        parent_widget,
        "Chat löschen",
        f"Chat „{chat_title or 'Neuer Chat'}“ wirklich löschen?\n\n"
        "Alle Nachrichten werden unwiderruflich entfernt.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    if reply != QMessageBox.StandardButton.Yes:
        return
    try:
        from app.services.chat_service import get_chat_service
        get_chat_service().delete_chat(chat_id)
        on_action()
        if on_chat_deleted:
            on_chat_deleted(chat_id)
    except Exception:
        pass
