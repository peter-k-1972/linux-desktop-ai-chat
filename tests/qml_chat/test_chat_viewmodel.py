"""ChatQmlViewModel + Presenter/Port wiring (kein QML-Render)."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from app.ui_contracts import (
    ChatConnectionStatus,
    ChatListEntry,
    ChatStreamPhase,
    ChatWorkspaceLoadState,
    ChatWorkspaceState,
    ProjectContextEntry,
)
from app.ui_application.mappers.chat_mapper import chat_message_from_row
from app.ui_runtime.qml.chat.chat_models import ChatMessageListModel, ChatSessionListModel
from app.ui_runtime.qml.chat.chat_qml_viewmodel import ChatQmlViewModel
from tests.architecture.app_ui_themes_source_root import app_ui_themes_source_root
from tests.unit.ui_application.test_chat_presenter_run_send import FakeChatPort


def _state(**kwargs: Any) -> ChatWorkspaceState:
    base = dict(
        load_state=ChatWorkspaceLoadState.IDLE,
        connection=ChatConnectionStatus.UNKNOWN,
        selected_chat_id=None,
        filter_text="",
        chats=(),
        messages=(),
        models=(),
        default_model_id=None,
        project=ProjectContextEntry(project_id=None, name="P"),
        stream_phase=ChatStreamPhase.IDLE,
        streaming_message_index=None,
        error=None,
    )
    base.update(kwargs)
    return ChatWorkspaceState(**base)


class VmTestPort(FakeChatPort):
    def __init__(self) -> None:
        super().__init__()
        self._entries: list[ChatListEntry] = []
        self._rows: dict[int, list[tuple[Any, ...]]] = {}

    def create_chat_global(self, title: str) -> int:
        cid = 300 + len(self._entries)
        self._entries.append(ChatListEntry(chat_id=cid, title=title))
        self._rows[cid] = []
        return cid

    def list_chat_entries(self, filter_text: str) -> list[ChatListEntry]:
        del filter_text
        return list(self._entries)

    def load_workspace_bootstrap(self) -> ChatWorkspaceState:
        return _state(chats=tuple(self._entries))

    def select_chat_state(self, state: ChatWorkspaceState, chat_id: int | None) -> ChatWorkspaceState:
        if chat_id is not None and not any(e.chat_id == chat_id for e in self._entries):
            return state
        if chat_id is None:
            return replace(state, selected_chat_id=None, messages=())
        rows = self._rows.get(chat_id, [])
        msgs = []
        for i, row in enumerate(rows):
            d: dict[str, Any] = {"role": row[0], "content": row[1] if len(row) > 1 else ""}
            if len(row) > 3 and row[3] is not None:
                d["model"] = row[3]
            msgs.append(chat_message_from_row(d, message_index=i))
        return replace(state, selected_chat_id=chat_id, messages=tuple(msgs))

    def create_chat_state(self, state: ChatWorkspaceState, title: str) -> ChatWorkspaceState:
        cid = self.create_chat_global(title)
        st = replace(state, chats=tuple(self._entries))
        return self.select_chat_state(st, cid)

    def apply_filter_state(self, state: ChatWorkspaceState, filter_text: str) -> ChatWorkspaceState:
        return replace(state, filter_text=filter_text, chats=tuple(self._entries))

    async def load_unified_model_catalog(
        self,
    ) -> tuple[list[dict[str, Any]], str | None]:
        return ([{"selection_id": "m1", "chat_selectable": True}], "m1")


@pytest.fixture
def qapplication():
    from PySide6.QtWidgets import QApplication
    import sys

    return QApplication.instance() or QApplication(sys.argv)


def test_viewmodel_initial_session_and_active(qapplication) -> None:
    port = VmTestPort()
    vm = ChatQmlViewModel(port, schedule_coro=lambda c: None)
    assert vm.activeChatId == -1
    assert vm.sessionModel.rowCount() == 0


def test_viewmodel_select_session(qapplication) -> None:
    port = VmTestPort()
    port._entries = [ChatListEntry(chat_id=5, title="Alpha")]
    port._rows[5] = [("user", "hi"), ("assistant", "yo")]
    vm = ChatQmlViewModel(port, schedule_coro=lambda c: None)
    vm.selectSession(5)
    assert vm.activeChatId == 5
    assert vm.messageModel.rowCount() == 2


def test_viewmodel_invalid_session_ignored(qapplication) -> None:
    port = VmTestPort()
    vm = ChatQmlViewModel(port, schedule_coro=lambda c: None)
    vm.selectSession(999)
    assert vm.activeChatId == -1


def test_viewmodel_context_surface_session_and_counts(qapplication) -> None:
    port = VmTestPort()
    port._entries = [ChatListEntry(chat_id=5, title="Alpha", updated_at_iso="2025-01-15T10:00:00")]
    port._rows[5] = [("user", "a"), ("assistant", "b")]
    vm = ChatQmlViewModel(port, schedule_coro=lambda c: None)
    vm._catalog_entries = [
        {"selection_id": "m1", "display_short": "qwen2.5", "chat_selectable": True, "is_online": False},
    ]
    vm._set_default_model_id("m1")
    vm.selectSession(5)
    assert vm.sessionTitle == "Alpha"
    assert vm.sessionIdCaption == "#5"
    assert "Zuletzt" in vm.sessionActivityLine
    assert vm.activeModel == "qwen2.5"
    assert vm.provider == "local"
    assert vm.messageCount == 2
    vm.apply_runtime_context_hints("semantic")
    assert vm.contextMode == "semantic"


@pytest.mark.asyncio
async def test_viewmodel_send_streams_and_persists(qapplication) -> None:
    import asyncio

    port = VmTestPort()
    port._entries = [ChatListEntry(chat_id=1, title="T")]
    port._rows[1] = []

    def schedule_coro(coro):
        asyncio.get_running_loop().create_task(coro)

    vm = ChatQmlViewModel(port, schedule_coro=schedule_coro)
    vm._set_default_model_id("m1")
    vm.selectSession(1)
    vm.sendMessage("ping")

    for _ in range(100):
        await asyncio.sleep(0.02)
        if port.saved_assistant:
            break
    assert port.saved_user == [(1, "ping")]
    assert port.saved_assistant


def test_message_model_streaming_flags(qapplication) -> None:
    m = ChatMessageListModel()
    m.append_user("u")
    m.append_assistant_placeholder("m1")
    assert m.data(m.index(1, 0), m.IsStreamingRole) is True
    m.update_last_assistant("partial")
    m.finalize_streaming()
    assert m.data(m.index(1, 0), m.IsStreamingRole) is False


def test_session_model_active(qapplication) -> None:
    s = ChatSessionListModel()
    s.set_chats((ChatListEntry(1, "A"), ChatListEntry(2, "B")), 2)
    assert s.data(s.index(1, 0), s.IsActiveRole) is True
    assert s.data(s.index(0, 0), s.IsActiveRole) is False


@pytest.mark.asyncio
async def test_chat_stage_qml_smoke(qapplication, monkeypatch) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    import asyncio
    from pathlib import Path

    from app.ui_runtime.qml.qml_runtime import QmlRuntime
    from app.ui_runtime.theme_loader import load_theme_manifest_from_path

    class SmokePort(VmTestPort):
        async def load_unified_model_catalog(
            self,
        ) -> tuple[list[dict[str, Any]], str | None]:
            return ([{"selection_id": "mdl", "chat_selectable": True}], "mdl")

    port = SmokePort()

    def schedule_coro(coro):
        try:
            asyncio.get_running_loop().create_task(coro)
        except RuntimeError:
            pass

    chat_vm = ChatQmlViewModel(port, schedule_coro=schedule_coro, parent=None)
    chat_vm._set_default_model_id("mdl")

    root = Path(__file__).resolve().parents[2]
    manifest = load_theme_manifest_from_path(
        app_ui_themes_source_root()
        / "builtins"
        / "light_default"
        / "manifest.json"
    )
    rt = QmlRuntime(manifest)
    rt.activate(context={"chat": chat_vm})
    try:
        qml_root = root / "qml"
        stage = qml_root / "domains" / "chat" / "ChatStage.qml"
        from PySide6.QtCore import QUrl
        from PySide6.QtQml import QQmlComponent

        eng = rt._engine
        comp = QQmlComponent(eng, QUrl.fromLocalFile(str(stage.resolve())))
        obj = comp.create(eng.rootContext())
        assert obj is not None, comp.errorString()
    finally:
        rt.deactivate()
