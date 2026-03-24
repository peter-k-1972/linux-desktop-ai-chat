"""
Chat-Details-Panel: Contract-DTO aus Port-Lesevorgängen (keine Qt, keine Widgets).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from app.ui_contracts.workspaces.chat import (
    ChatDetailsPanelState,
    ChatTopicOptionEntry,
    empty_chat_details_panel_state,
)

if TYPE_CHECKING:
    from app.ui_application.ports.chat_operations_port import ChatOperationsPort


def format_chat_details_timestamp(ts: Any) -> str:
    """Gleiche Anzeigelogik wie zuvor im Details-Panel (dd.mm.yyyy HH:MM)."""
    if ts is None:
        return "—"
    try:
        if hasattr(ts, "strftime"):
            return ts.strftime("%d.%m.%Y %H:%M")
        s = str(ts)
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(ts)[:16] if ts else "—"


def build_chat_details_panel_state(
    port: ChatOperationsPort,
    chat_id: int | None,
    *,
    model_label: str | None,
) -> ChatDetailsPanelState | None:
    """
    Liefert None, wenn chat_id gesetzt ist aber keine Chat-Infos existieren (Panel leeren).
    Bei chat_id None explizit ``empty_chat_details_panel_state`` vom Aufrufer nutzen.
    """
    if chat_id is None:
        return empty_chat_details_panel_state()
    info = port.get_chat_info(chat_id)
    if not info:
        return None
    project_id: int | None = None
    project_name: str | None = None
    try:
        project_id = port.project_id_for_chat(chat_id)
        if project_id:
            proj = port.get_project_record(project_id)
            project_name = proj.get("name") if proj else None
    except Exception:
        pass
    topic_options: list[ChatTopicOptionEntry] = [
        ChatTopicOptionEntry(None, "Ungruppiert"),
    ]
    if project_id:
        try:
            for t in port.list_topic_rows_for_project(project_id):
                tid = t.get("id")
                tname = t.get("name", "Topic")
                if tid is not None:
                    topic_options.append(ChatTopicOptionEntry(int(tid), str(tname)))
        except Exception:
            pass
    last_agent = port.get_last_assistant_agent_for_chat(chat_id)
    tid_sel = info.get("topic_id")
    if tid_sel is not None:
        try:
            tid_sel = int(tid_sel)
        except (TypeError, ValueError):
            tid_sel = None
    return ChatDetailsPanelState(
        chat_id=chat_id,
        title=str(info.get("title") or "Neuer Chat"),
        project_id=project_id,
        project_name=project_name,
        selected_topic_id=tid_sel,
        topic_display_name=(str(info.get("topic_name")) if info.get("topic_name") else None),
        topic_options=tuple(topic_options),
        model_label=model_label,
        last_assistant_agent=last_agent,
        created_at_label=format_chat_details_timestamp(info.get("created_at")),
        updated_at_label=format_chat_details_timestamp(info.get("last_activity")),
        is_pinned=bool(info.get("pinned")),
        is_archived=bool(info.get("archived")),
    )
