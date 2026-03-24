"""
Reine Abbildungen Service-/Persistenz-naher Strukturen → ui_contracts.

Hinweis: Keys sind defensiv, weil Legacy-Pfade noch dict-lastig sind.
"""

from __future__ import annotations

from typing import Any, Literal, Mapping

from app.ui_contracts.workspaces.chat import ChatListEntry, ChatMessageEntry


def _normalize_role(role_raw: str) -> Literal["user", "assistant", "system", "tool"]:
    if role_raw == "assistant":
        return "assistant"
    if role_raw == "system":
        return "system"
    if role_raw == "tool":
        return "tool"
    return "user"


def chat_list_entry_from_mapping(row: Mapping[str, Any]) -> ChatListEntry:
    cid = int(row.get("id") or row.get("chat_id") or 0)
    title = str(row.get("title") or "")
    pid = row.get("project_id")
    project_id = int(pid) if pid is not None else None
    return ChatListEntry(
        chat_id=cid,
        title=title,
        project_id=project_id,
        updated_at_iso=(str(row["updated_at_iso"]) if row.get("updated_at_iso") else None),
        is_archived=bool(row.get("is_archived", False)),
    )


def conversation_rows_from_message_entries(
    entries: tuple[ChatMessageEntry, ...] | list[ChatMessageEntry],
) -> list[tuple[Any, ...]]:
    """Konvertiert Contract-Nachrichten in Tupel für ``ChatConversationPanel.load_messages``."""
    rows: list[tuple[Any, ...]] = []
    for e in entries:
        row: tuple[Any, ...] = (e.role, e.content)
        if e.model_label:
            row = (e.role, e.content, None, e.model_label)
        rows.append(row)
    return rows


def chat_message_from_row(
    row: Mapping[str, Any],
    *,
    message_index: int,
) -> ChatMessageEntry:
    role = _normalize_role(str(row.get("role") or "user"))
    return ChatMessageEntry(
        message_index=message_index,
        role=role,
        content=str(row.get("content") or ""),
        thinking_text=(str(row["thinking"]) if row.get("thinking") else None),
        model_label=(str(row["model"]) if row.get("model") else None),
        created_at_iso=(str(row["created_at_iso"]) if row.get("created_at_iso") else None),
    )
