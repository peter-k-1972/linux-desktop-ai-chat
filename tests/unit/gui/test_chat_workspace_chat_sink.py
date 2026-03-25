"""ChatWorkspaceChatSink spiegelt Contract-State/Patches auf Mock-Widgets (ohne Qt-Workspace)."""

from __future__ import annotations

from types import SimpleNamespace

from app.gui.domains.operations.chat.chat_workspace import ChatWorkspaceChatSink
from app.ui_contracts import (
    ChatConnectionStatus,
    ChatDetailsPanelState,
    ChatErrorInfo,
    ChatMessageEntry,
    ChatStatePatch,
    ChatStreamPhase,
    ChatTopicOptionEntry,
    ChatWorkspaceLoadState,
    ChatWorkspaceState,
    ProjectContextEntry,
)


def _base_state(**overrides) -> ChatWorkspaceState:
    base = dict(
        load_state=ChatWorkspaceLoadState.IDLE,
        connection=ChatConnectionStatus.UNKNOWN,
        selected_chat_id=None,
        filter_text="",
        chats=(),
        messages=(),
        models=(),
        default_model_id=None,
        project=ProjectContextEntry(None, None),
        stream_phase=ChatStreamPhase.IDLE,
        streaming_message_index=None,
        error=None,
        details_panel=None,
    )
    base.update(overrides)
    return ChatWorkspaceState(**base)


def _mock_workspace():
    inp = SimpleNamespace(
        error="",
        sending=False,
        status="",
        set_error=lambda s: setattr(inp, "error", s),
        set_sending=lambda b: setattr(inp, "sending", b),
        set_status=lambda s: setattr(inp, "status", s),
    )
    conv = SimpleNamespace(
        rows=None,
        cleared=False,
        clear=lambda: setattr(conv, "cleared", True),
        load_messages=lambda r: setattr(conv, "rows", list(r)),
        scroll_to_bottom=lambda: None,
    )
    nav = SimpleNamespace(current=None, set_current_chat=lambda cid: setattr(nav, "current", cid))
    details = SimpleNamespace(last_state=None, apply_details_state=lambda s: setattr(details, "last_state", s))
    ws = SimpleNamespace(
        _input=inp,
        _conversation=conv,
        _session_explorer=nav,
        _details_panel=details,
        _current_chat_id=None,
        _streaming=False,
        _refresh_context_bar=lambda: setattr(ws, "bar_refreshed", True),
    )
    ws.bar_refreshed = False
    return ws


def test_apply_full_state_error_and_messages():
    sink = ChatWorkspaceChatSink()
    ws = _mock_workspace()
    sink.bind(ws)
    msg = ChatMessageEntry(
        message_index=0,
        role="user",
        content="hi",
        thinking_text=None,
        model_label=None,
        created_at_iso=None,
    )
    state = _base_state(
        selected_chat_id=7,
        messages=(msg,),
        error=ChatErrorInfo(code="x", message="oops", recoverable=True),
    )
    sink.apply_full_state(state)
    assert ws._input.error == "oops"
    assert ws._current_chat_id == 7
    assert ws._session_explorer.current == 7
    assert ws._conversation.rows == [("user", "hi")]
    assert ws.bar_refreshed is True


def test_apply_full_state_clears_conversation_when_no_selection():
    sink = ChatWorkspaceChatSink()
    ws = _mock_workspace()
    sink.bind(ws)
    sink.apply_full_state(_base_state(selected_chat_id=None))
    assert ws._conversation.cleared is True


def test_apply_chat_patch_streaming_and_error():
    sink = ChatWorkspaceChatSink()
    ws = _mock_workspace()
    ws._current_chat_id = 1
    sink.bind(ws)
    sink.apply_chat_patch(
        ChatStatePatch(
            load_state=ChatWorkspaceLoadState.STREAMING,
            stream_phase=ChatStreamPhase.CONTENT,
        )
    )
    assert ws._streaming is True
    assert ws._input.sending is True
    assert "gestreamt" in ws._input.status

    sink.apply_chat_patch(
        ChatStatePatch(clear_error=True, error=ChatErrorInfo(code="e", message="bad", recoverable=True))
    )
    assert ws._input.error == "bad"


def test_apply_full_state_details_panel():
    sink = ChatWorkspaceChatSink()
    ws = _mock_workspace()
    sink.bind(ws)
    det = ChatDetailsPanelState(
        chat_id=1,
        title="T",
        project_id=2,
        project_name="P",
        selected_topic_id=None,
        topic_display_name=None,
        topic_options=(ChatTopicOptionEntry(None, "Ungruppiert"),),
        model_label="m",
        last_assistant_agent=None,
        created_at_label="—",
        updated_at_label="—",
        is_pinned=False,
        is_archived=False,
    )
    sink.apply_full_state(_base_state(details_panel=det))
    assert ws._details_panel.last_state is det


def test_apply_chat_patch_details_panel():
    sink = ChatWorkspaceChatSink()
    ws = _mock_workspace()
    sink.bind(ws)
    det = ChatDetailsPanelState(
        chat_id=9,
        title="X",
        project_id=None,
        project_name=None,
        selected_topic_id=None,
        topic_display_name=None,
        topic_options=(ChatTopicOptionEntry(None, "Ungruppiert"),),
        model_label=None,
        last_assistant_agent=None,
        created_at_label="—",
        updated_at_label="—",
        is_pinned=True,
        is_archived=False,
    )
    sink.apply_chat_patch(ChatStatePatch(details_panel=det))
    assert ws._details_panel.last_state is det


def test_apply_chat_patch_messages_only_when_chat_selected():
    sink = ChatWorkspaceChatSink()
    ws = _mock_workspace()
    ws._current_chat_id = None
    sink.bind(ws)
    msg = ChatMessageEntry(0, "assistant", "a", None, None, None)
    sink.apply_chat_patch(ChatStatePatch(messages=(msg,)))
    assert ws._conversation.rows is None

    ws._current_chat_id = 3
    sink.apply_chat_patch(ChatStatePatch(messages=(msg,)))
    assert ws._conversation.rows == [("assistant", "a")]
