"""
QML-facing chat bridge: models + presenter wiring (no logic in QML).

Implements :class:`ChatUiSink`; drives :class:`ChatPresenter` + :class:`ServiceChatPortAdapter`.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from app.ui_application.adapters.service_chat_port_adapter import ServiceChatPortAdapter
from app.ui_application.mappers.chat_details_mapper import format_chat_details_timestamp
from app.ui_application.ports.chat_operations_port import ChatOperationsPort
from app.ui_application.presenters.chat_presenter import ChatPresenter
from app.ui_application.presenters.chat_send_callbacks import ChatSendCallbacks, ChatSendSession
from app.ui_contracts.common.enums import ChatStreamPhase, ChatWorkspaceLoadState
from app.ui_contracts.workspaces.chat import (
    ChatDetailsPanelState,
    ChatStatePatch,
    ChatWorkspaceState,
    CreateChatCommand,
    SelectChatCommand,
    SendMessageCommand,
)
from app.ui_runtime.qml.chat.chat_models import ChatMessageListModel, ChatSessionListModel

logger = logging.getLogger(__name__)


class ChatQmlViewModel(QObject):
    """Root context object ``chat`` for ChatStage.qml."""

    messagesChanged = Signal()
    streamUpdate = Signal()
    sessionChanged = Signal()
    readingTableScrollToEnd = Signal()
    activeChatIdChanged = Signal()
    isStreamingChanged = Signal()
    busyChanged = Signal()
    canSendChanged = Signal()
    defaultModelIdChanged = Signal()
    errorTextChanged = Signal()
    contextSurfaceChanged = Signal()
    statusHintChanged = Signal()

    def __init__(
        self,
        port: ChatOperationsPort,
        schedule_coro: Callable[[Awaitable[Any]], None],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._port = port
        self._schedule_coro = schedule_coro
        self._presenter = ChatPresenter(self, port=port)
        self._session_chat_id: int | None = None
        self._default_model_id: str = ""
        self._error_text: str = ""
        self._status_hint: str = ""
        self._project_name: str = ""
        self._topic_label: str = ""
        self._context_mode_label: str = "—"
        self._session_title: str = ""
        self._session_id_caption: str = ""
        self._session_activity_line: str = ""
        self._active_model: str = ""
        self._provider: str = ""
        self._token_usage_line: str = ""
        self._session_duration_line: str = ""
        self._catalog_entries: list[dict[str, Any]] = []

        self._session_model = ChatSessionListModel(self)
        self._message_model = ChatMessageListModel(self)

        self._attach_pipeline()
        self._presenter.refresh_bootstrap()

    def _attach_pipeline(self) -> None:
        self._presenter.attach_send_pipeline(
            schedule_coro=self._schedule_coro,
            callbacks=ChatSendCallbacks(
                conversation_add_user=self._cb_add_user,
                conversation_scroll_bottom=self._cb_scroll_bottom,
                conversation_add_placeholder=self._cb_add_placeholder,
                conversation_update_last_assistant=self._cb_update_last_assistant,
                conversation_set_last_completion=self._message_model.set_last_completion_label,
                conversation_finalize_streaming=self._cb_finalize_stream,
                input_set_sending=lambda _b: None,
                details_set_invocation_view=lambda _v: None,
                refresh_session_explorer=self._cb_refresh_sessions,
                set_session_explorer_current=self._cb_set_current_chat,
                refresh_context_bar=self._cb_refresh_context,
                refresh_details_panel=self._cb_refresh_context,
                refresh_inspector=lambda: None,
                show_error_inline=self._cb_show_error,
                notify_send_session_completed=self._cb_send_completed,
            ),
            session_factory=self._make_send_session,
            busy_check=lambda: self._presenter.is_send_active,
        )

    def _make_send_session(self) -> ChatSendSession:
        return ChatSendSession(self._session_chat_id)

    def _cb_add_user(self, text: str) -> None:
        self._message_model.append_user(text)
        self.messagesChanged.emit()

    def _cb_scroll_bottom(self) -> None:
        self.readingTableScrollToEnd.emit()

    def _cb_add_placeholder(self, model: str) -> None:
        self._message_model.append_assistant_placeholder(model)
        self.messagesChanged.emit()

    def _cb_update_last_assistant(self, text: str) -> None:
        self._message_model.update_last_assistant(text)
        self.streamUpdate.emit()

    def _cb_finalize_stream(self) -> None:
        self._message_model.finalize_streaming()

    def _cb_refresh_sessions(self) -> None:
        st = self._presenter.state
        try:
            chats = self._port.list_chat_entries(st.filter_text)
            self._session_model.set_chats(tuple(chats), st.selected_chat_id)
        except Exception:
            logger.exception("refresh_session_explorer")
        self.sessionChanged.emit()
        self._sync_context_surface(self._presenter.state)
        self.contextSurfaceChanged.emit()

    def _cb_set_current_chat(self, chat_id: int) -> None:
        self._presenter.handle_command(SelectChatCommand(chat_id=chat_id))

    def _cb_refresh_context(self) -> None:
        self._sync_context_surface(self._presenter.state)
        self.contextSurfaceChanged.emit()

    def _cb_show_error(self, message: str) -> None:
        self._error_text = message
        self.errorTextChanged.emit()

    def _cb_send_completed(self, session: ChatSendSession) -> None:
        self._session_chat_id = session.chat_id

    def start_async_loaders(self) -> None:
        """Call after QML engine + event loop run (model catalog needs asyncio loop)."""
        QTimer.singleShot(0, self._kick_model_load)

    def _kick_model_load(self) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            QTimer.singleShot(50, self._kick_model_load)
            return
        loop.create_task(self._load_models_async())

    def apply_full_state(self, state: ChatWorkspaceState) -> None:
        self._session_chat_id = state.selected_chat_id
        self._session_model.set_chats(state.chats, state.selected_chat_id)
        if state.selected_chat_id is None:
            self._message_model.clear()
        else:
            self._message_model.load_from_entries(state.messages)
        self._sync_context_surface(state)
        self.contextSurfaceChanged.emit()
        if state.error:
            self._error_text = state.error.message
        else:
            self._error_text = ""
        self.errorTextChanged.emit()
        self._apply_load_status(state.load_state, state.stream_phase)
        self._emit_binding_props()
        self.sessionChanged.emit()
        self.messagesChanged.emit()

    def apply_chat_patch(self, patch: ChatStatePatch) -> None:
        if patch.clear_error:
            self._error_text = ""
            self.errorTextChanged.emit()
        if patch.error is not None:
            self._error_text = patch.error.message
            self.errorTextChanged.emit()
        if patch.load_state is not None or patch.stream_phase is not None:
            ls = patch.load_state if patch.load_state is not None else self._presenter.state.load_state
            sp = patch.stream_phase if patch.stream_phase is not None else self._presenter.state.stream_phase
            self._apply_load_status(ls, sp)
        if patch.messages is not None and self._presenter.state.selected_chat_id is not None:
            self._message_model.load_from_entries(patch.messages)
            self.messagesChanged.emit()
        if patch.chats is not None:
            self._session_model.set_chats(patch.chats, self._presenter.state.selected_chat_id)
            self.sessionChanged.emit()
        if patch.project is not None or patch.chats is not None or patch.details_panel is not None:
            self._sync_context_surface(self._presenter.state)
            self.contextSurfaceChanged.emit()
        self._emit_binding_props()

    def _apply_load_status(self, load_state: ChatWorkspaceLoadState, stream_phase: ChatStreamPhase) -> None:
        if load_state == ChatWorkspaceLoadState.STREAMING:
            self._status_hint = "Antwort wird gestreamt …"
        elif load_state == ChatWorkspaceLoadState.LOADING_MESSAGES:
            self._status_hint = "Nachrichten werden geladen …"
        elif load_state == ChatWorkspaceLoadState.ERROR:
            self._status_hint = ""
        else:
            if stream_phase == ChatStreamPhase.IDLE:
                self._status_hint = ""
        self.statusHintChanged.emit()
        self.isStreamingChanged.emit()
        self.busyChanged.emit()
        self.canSendChanged.emit()

    def _emit_binding_props(self) -> None:
        self.activeChatIdChanged.emit()
        self.isStreamingChanged.emit()
        self.busyChanged.emit()
        self.canSendChanged.emit()

    def _activity_line_from_details(self, dp: ChatDetailsPanelState) -> str:
        u = (dp.updated_at_label or "").strip()
        c = (dp.created_at_label or "").strip()
        if u and u != "—":
            return f"Zuletzt · {u}"
        if c and c != "—":
            return f"Erstellt · {c}"
        return ""

    def _sync_context_surface(self, state: ChatWorkspaceState) -> None:
        cid = state.selected_chat_id
        dp = state.details_panel
        if cid is None:
            self._session_title = ""
            self._session_id_caption = ""
            self._session_activity_line = ""
        elif dp is not None and dp.chat_id == cid:
            self._session_title = (dp.title or "").strip()
            self._session_id_caption = f"#{cid}"
            self._session_activity_line = self._activity_line_from_details(dp)
        else:
            entry = next((e for e in state.chats if e.chat_id == cid), None)
            self._session_title = (entry.title if entry else "") or ""
            self._session_id_caption = f"#{cid}"
            iso = entry.updated_at_iso if entry else None
            if iso:
                self._session_activity_line = f"Zuletzt · {format_chat_details_timestamp(iso)}"
            else:
                self._session_activity_line = ""

        pid = state.project.project_id
        pname = (state.project.name or "").strip()
        if pid is not None and pname:
            self._project_name = pname
        else:
            self._project_name = ""

        if dp is not None and cid is not None and dp.chat_id == cid:
            tn = (dp.topic_display_name or "").strip()
            self._topic_label = tn if tn and tn != "—" else ""
        else:
            self._topic_label = ""

    def apply_runtime_context_hints(self, context_mode: str | None) -> None:
        """Optional: set by app shell after infrastructure init (keeps ui_runtime free of app.services)."""
        self._context_mode_label = (str(context_mode).strip() if context_mode else "") or "—"
        self.contextSurfaceChanged.emit()

    async def _load_models_async(self) -> None:
        try:
            catalog, default_selection_id = await self._port.load_unified_model_catalog()
            self._catalog_entries = list(catalog)
            selectable = [e for e in catalog if e.get("chat_selectable")]
            mid = (default_selection_id or "").strip()
            if not mid and selectable:
                mid = str(selectable[0].get("selection_id") or "").strip()
            self._set_default_model_id(mid)
        except Exception:
            logger.exception("load_unified_model_catalog")
            self._catalog_entries = []
            self._set_default_model_id("")

    def _refresh_model_source_labels(self) -> None:
        mid = (self._default_model_id or "").strip()
        if not mid:
            self._active_model = ""
            self._provider = ""
            return
        entry = next((e for e in self._catalog_entries if e.get("selection_id") == mid), None)
        if entry:
            self._active_model = (entry.get("display_short") or mid).strip()
            self._provider = "cloud" if entry.get("is_online") else "local"
        else:
            self._active_model = mid
            self._provider = ""

    def _set_default_model_id(self, value: str) -> None:
        self._default_model_id = value or ""
        self._refresh_model_source_labels()
        self.defaultModelIdChanged.emit()
        self.canSendChanged.emit()
        self.contextSurfaceChanged.emit()

    def _get_message_model(self) -> ChatMessageListModel:
        return self._message_model

    def _get_session_model(self) -> ChatSessionListModel:
        return self._session_model

    def _get_active_chat_id(self) -> int:
        cid = self._presenter.state.selected_chat_id
        return -1 if cid is None else int(cid)

    def _get_is_streaming(self) -> bool:
        return self._presenter.state.load_state == ChatWorkspaceLoadState.STREAMING

    def _get_busy(self) -> bool:
        return self._presenter.is_send_active or self._get_is_streaming()

    def _get_can_send(self) -> bool:
        if self._get_busy():
            return False
        return bool(self._default_model_id.strip())

    def _get_default_model_id(self) -> str:
        return self._default_model_id

    def _get_error_text(self) -> str:
        return self._error_text

    def _get_project_name(self) -> str:
        return self._project_name

    def _get_context_mode_label(self) -> str:
        return self._context_mode_label

    def _get_session_title(self) -> str:
        return self._session_title

    def _get_session_id_caption(self) -> str:
        return self._session_id_caption

    def _get_session_activity_line(self) -> str:
        return self._session_activity_line

    def _get_active_model(self) -> str:
        return self._active_model

    def _get_provider(self) -> str:
        return self._provider

    def _get_topic_name(self) -> str:
        return self._topic_label

    def _get_message_count(self) -> int:
        return self._message_model.rowCount()

    def _get_token_usage_line(self) -> str:
        return self._token_usage_line

    def _get_session_duration_line(self) -> str:
        return self._session_duration_line

    def _get_status_hint(self) -> str:
        return self._status_hint

    messageModel = Property(QObject, _get_message_model, constant=True)
    sessionModel = Property(QObject, _get_session_model, constant=True)
    activeChatId = Property(int, _get_active_chat_id, notify=activeChatIdChanged)
    isStreaming = Property(bool, _get_is_streaming, notify=isStreamingChanged)
    busy = Property(bool, _get_busy, notify=busyChanged)
    canSend = Property(bool, _get_can_send, notify=canSendChanged)
    defaultModelId = Property(str, _get_default_model_id, notify=defaultModelIdChanged)
    errorText = Property(str, _get_error_text, notify=errorTextChanged)
    sessionTitle = Property(str, _get_session_title, notify=contextSurfaceChanged)
    sessionIdCaption = Property(str, _get_session_id_caption, notify=contextSurfaceChanged)
    sessionActivityLine = Property(str, _get_session_activity_line, notify=contextSurfaceChanged)
    activeModel = Property(str, _get_active_model, notify=contextSurfaceChanged)
    provider = Property(str, _get_provider, notify=contextSurfaceChanged)
    contextMode = Property(str, _get_context_mode_label, notify=contextSurfaceChanged)
    projectName = Property(str, _get_project_name, notify=contextSurfaceChanged)
    topicName = Property(str, _get_topic_name, notify=contextSurfaceChanged)
    topicLabel = Property(str, _get_topic_name, notify=contextSurfaceChanged)
    contextModeLabel = Property(str, _get_context_mode_label, notify=contextSurfaceChanged)
    messageCount = Property(int, _get_message_count, notify=messagesChanged)
    tokenUsageLine = Property(str, _get_token_usage_line, notify=contextSurfaceChanged)
    sessionDurationLine = Property(str, _get_session_duration_line, notify=contextSurfaceChanged)
    statusHint = Property(str, _get_status_hint, notify=statusHintChanged)

    @Slot(str)
    def sendMessage(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        mid = self._default_model_id.strip() or None
        self._presenter.handle_command(SendMessageCommand(text=text, model_id=mid))

    @Slot(int)
    def selectSession(self, chat_id: int) -> None:
        cid = None if chat_id < 0 else chat_id
        self._presenter.handle_command(SelectChatCommand(chat_id=cid))

    @Slot()
    def createSession(self) -> None:
        self._presenter.handle_command(CreateChatCommand(title="Neuer Chat"))


def build_chat_qml_viewmodel(
    schedule_coro: Callable[[Awaitable[Any]], None],
    *,
    port: ChatOperationsPort | None = None,
    parent: QObject | None = None,
) -> ChatQmlViewModel:
    """Factory for QML runtime (default port: :class:`ServiceChatPortAdapter`)."""
    p = port or ServiceChatPortAdapter()
    return ChatQmlViewModel(p, schedule_coro, parent=parent)
