"""Contract-Tests: Chat-DTOs (Qt-frei, serialisierbar)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from app.ui_contracts import (
    ChatConnectionStatus,
    ChatDetailsPanelState,
    ChatListEntry,
    ChatStatePatch,
    ChatStreamPhase,
    ChatTopicOptionEntry,
    ChatWorkspaceLoadState,
    ChatWorkspaceState,
    ProjectContextEntry,
    ProjectListRow,
)
from app.ui_contracts.workspaces.chat import chat_contract_to_json, merge_chat_state


def _minimal_state() -> ChatWorkspaceState:
    return ChatWorkspaceState(
        load_state=ChatWorkspaceLoadState.IDLE,
        connection=ChatConnectionStatus.ONLINE,
        selected_chat_id=3,
        filter_text="",
        chats=(ChatListEntry(chat_id=3, title="A"),),
        messages=(),
        models=(),
        default_model_id="m1",
        project=ProjectContextEntry(project_id=1, name="P"),
        stream_phase=ChatStreamPhase.IDLE,
        streaming_message_index=None,
        error=None,
        details_panel=None,
    )


def test_merge_chat_state_updates_messages_only():
    base = _minimal_state()
    patch = ChatStatePatch(messages=())
    merged = merge_chat_state(base, patch)
    assert merged.messages == ()
    assert merged.selected_chat_id == 3


def test_merge_clear_selected():
    base = _minimal_state()
    merged = merge_chat_state(base, ChatStatePatch(clear_selected_chat=True))
    assert merged.selected_chat_id is None


def test_merge_details_panel():
    det = ChatDetailsPanelState(
        chat_id=3,
        title="Hi",
        project_id=1,
        project_name="P",
        selected_topic_id=None,
        topic_display_name=None,
        topic_options=(ChatTopicOptionEntry(None, "Ungruppiert"),),
        model_label="m",
        last_assistant_agent=None,
        created_at_label="a",
        updated_at_label="b",
        is_pinned=False,
        is_archived=False,
    )
    base = _minimal_state()
    merged = merge_chat_state(base, ChatStatePatch(details_panel=det))
    assert merged.details_panel is det


def test_chat_contract_to_json_roundtrip_shape():
    base = _minimal_state()
    j = chat_contract_to_json(base)
    assert j["load_state"] == "idle"
    assert j["chats"][0]["chat_id"] == 3


def test_project_list_row_json():
    j = chat_contract_to_json(ProjectListRow(project_id=7, name="P"))
    assert j == {"project_id": 7, "name": "P"}
