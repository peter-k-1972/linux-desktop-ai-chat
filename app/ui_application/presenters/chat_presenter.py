"""
ChatPresenter — Steuerung zwischen Chat-Port und UI (über Sink + Send-Callbacks).

Streaming läuft über ``run_send_async``; Commands für Contract-State über ``handle_command``.
``SendMessageCommand`` plant den Send-Lauf über ``attach_send_pipeline``.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.presenters.chat_send_callbacks import ChatSendCallbacks, ChatSendSession
from app.ui_application.presenters.chat_stream_assembler import append_stream_piece, extract_stream_display
from app.ui_application.view_models.protocols import ChatUiSink
from app.ui_contracts.common.enums import ChatConnectionStatus, ChatStreamPhase, ChatWorkspaceLoadState
from app.ui_contracts.common.events import ChatUiEvent
from app.ui_contracts.workspaces.chat import (
    ChatCommand,
    ChatErrorInfo,
    ChatStatePatch,
    ChatWorkspaceState,
    CreateChatCommand,
    LoadModelsCommand,
    ProjectContextEntry,
    RenameChatCommand,
    SelectChatCommand,
    SendMessageCommand,
    SetChatFilterCommand,
    StopGenerationCommand,
)

if TYPE_CHECKING:
    from app.ui_application.ports.chat_operations_port import ChatOperationsPort


def use_presenter_send_pipeline() -> bool:
    """Standard: Presenter-Pipeline an; Legacy mit LINUX_DESKTOP_CHAT_LEGACY_CHAT_SEND=1."""
    return os.environ.get("LINUX_DESKTOP_CHAT_LEGACY_CHAT_SEND", "").strip() != "1"


class ChatPresenter(BasePresenter):
    def __init__(
        self,
        sink: ChatUiSink,
        port: ChatOperationsPort | None = None,
        *,
        initial_state: ChatWorkspaceState | None = None,
        on_ui_event: Callable[[ChatUiEvent], None] | None = None,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._port = port
        self._state = initial_state or _placeholder_state()
        self._on_ui_event = on_ui_event
        self._schedule_coro: Callable[[Awaitable[Any]], None] | None = None
        self._send_callbacks: ChatSendCallbacks | None = None
        self._send_session_factory: Callable[[], ChatSendSession] | None = None
        self._send_busy_check: Callable[[], bool] | None = None
        self._active_send = False

    @property
    def state(self) -> ChatWorkspaceState:
        return self._state

    @property
    def port(self) -> ChatOperationsPort | None:
        return self._port

    @property
    def is_send_active(self) -> bool:
        return self._active_send

    def attach_send_pipeline(
        self,
        *,
        schedule_coro: Callable[[Awaitable[Any]], None],
        callbacks: ChatSendCallbacks,
        session_factory: Callable[[], ChatSendSession],
        busy_check: Callable[[], bool] | None = None,
    ) -> None:
        """Nach Aufbau der Widgets: SendMessageCommand kann async ``run_send_async`` planen."""
        self._schedule_coro = schedule_coro
        self._send_callbacks = callbacks
        self._send_session_factory = session_factory
        self._send_busy_check = busy_check

    def handle_command(self, command: ChatCommand) -> None:
        if self._port is None:
            self._sink.apply_chat_patch(
                ChatStatePatch(
                    load_state=ChatWorkspaceLoadState.ERROR,
                    error=ChatErrorInfo(
                        code="backend_not_wired",
                        message="ChatOperationsPort ist nicht injiziert.",
                        recoverable=True,
                    ),
                )
            )
            self._emit(ChatUiEvent(kind="error", payload={"command": type(command).__name__}))
            return

        try:
            if isinstance(command, SelectChatCommand):
                self._push_full(self._port.select_chat_state(self._state, command.chat_id))
            elif isinstance(command, CreateChatCommand):
                self._push_full(self._port.create_chat_state(self._state, command.title))
            elif isinstance(command, RenameChatCommand):
                self._push_full(self._port.rename_chat_state(self._state, command.chat_id, command.title))
            elif isinstance(command, StopGenerationCommand):
                self._push_full(self._port.stop_generation_state(self._state))
            elif isinstance(command, SetChatFilterCommand):
                self._push_full(self._port.apply_filter_state(self._state, command.filter_text))
            elif isinstance(command, LoadModelsCommand):
                pass
            elif isinstance(command, SendMessageCommand):
                self._handle_send_message_command(command)
        except Exception as exc:  # noqa: BLE001
            self._sink.apply_chat_patch(
                ChatStatePatch(
                    load_state=ChatWorkspaceLoadState.ERROR,
                    error=ChatErrorInfo(
                        code="presenter_exception",
                        message=str(exc),
                        recoverable=True,
                    ),
                )
            )
            self._emit(
                ChatUiEvent(kind="error", payload={"exception": type(exc).__name__, "msg": str(exc)})
            )

    def _handle_send_message_command(self, command: SendMessageCommand) -> None:
        if (
            self._schedule_coro is None
            or self._send_callbacks is None
            or self._send_session_factory is None
        ):
            self._sink.apply_chat_patch(
                ChatStatePatch(
                    error=ChatErrorInfo(
                        code="send_pipeline_not_attached",
                        message="Send-Pipeline nicht angebunden (attach_send_pipeline).",
                        recoverable=True,
                    ),
                )
            )
            return
        if self._send_busy_check is not None and self._send_busy_check():
            return
        text = (command.text or "").strip()
        if not text:
            return
        model = (command.model_id or "").strip()
        if not model:
            self._sink.apply_chat_patch(
                ChatStatePatch(
                    error=ChatErrorInfo(
                        code="no_model",
                        message="Bitte ein Modell auswählen.",
                        recoverable=True,
                    ),
                )
            )
            return
        session = self._send_session_factory()
        coro = self.run_send_async(
            text=text,
            model=model,
            session=session,
            callbacks=self._send_callbacks,
        )
        self._schedule_coro(coro)

    def refresh_bootstrap(self) -> None:
        if self._port is None:
            self.handle_command(SelectChatCommand(chat_id=None))
            return
        self._push_full(self._port.load_workspace_bootstrap())

    async def run_send_async(
        self,
        *,
        text: str,
        model: str,
        session: ChatSendSession,
        callbacks: ChatSendCallbacks,
    ) -> None:
        """Vollständiger Send + Stream + Persistenz (wie bisheriger Workspace-Code)."""
        self._active_send = True
        try:
            if self._port is None:
                callbacks.show_error_inline("Chat-Port nicht verfügbar.")
                return
            text = (text or "").strip()
            if not text:
                return

            port = self._port
            chat_id = session.chat_id

            if chat_id is None:
                try:
                    pid = port.get_active_project_id()
                    if pid is not None:
                        chat_id = port.create_chat_in_project(pid, "Neuer Chat")
                    else:
                        chat_id = port.create_chat_global("Neuer Chat")
                    session.chat_id = chat_id
                    callbacks.refresh_session_explorer()
                    callbacks.set_session_explorer_current(chat_id)
                    callbacks.refresh_context_bar()
                except Exception as e:
                    callbacks.show_error_inline(f"Chat konnte nicht angelegt werden: {e}")
                    return

            port.save_user_message(chat_id, text)
            try:
                if port.maybe_autotitle_from_first_message(chat_id, text):
                    callbacks.refresh_session_explorer()
            except Exception:
                pass

            callbacks.conversation_add_user(text)
            callbacks.conversation_scroll_bottom()

            self._sink.apply_chat_patch(
                ChatStatePatch(
                    load_state=ChatWorkspaceLoadState.STREAMING,
                    stream_phase=ChatStreamPhase.CONTENT,
                )
            )

            full_content = ""
            provider_done = False
            had_error = False
            completion_status_str = None
            merged_invocation: dict | None = None
            last_error_kind: str | None = None
            last_error_text: str | None = None

            callbacks.details_set_invocation_view(None)

            temp, max_tokens, stream_enabled = port.get_stream_settings()

            try:
                api_messages = port.build_api_messages(chat_id)
                callbacks.conversation_add_placeholder(model)

                async for chunk in port.iter_chat_chunks(
                    model=model,
                    chat_id=chat_id,
                    api_messages=api_messages,
                    temperature=temp,
                    max_tokens=max_tokens,
                    stream=stream_enabled,
                ):
                    merged_invocation = port.merge_invocation_payload(merged_invocation, chunk)
                    ek = port.invocation_error_kind(chunk)
                    if ek:
                        last_error_kind = ek
                    content, _thinking, error, done = extract_stream_display(chunk)
                    if done:
                        provider_done = True
                    if error:
                        had_error = True
                        last_error_text = str(error)
                        full_content = f"Fehler: {error}"
                        callbacks.conversation_update_last_assistant(full_content)
                        callbacks.conversation_scroll_bottom()
                        break
                    if content:
                        full_content = append_stream_piece(full_content, content)
                        callbacks.conversation_update_last_assistant(full_content)
                        callbacks.conversation_scroll_bottom()

                completion_status_str = port.completion_status_for_outcome(
                    full_content,
                    provider_finished_normally=provider_done,
                    had_error=had_error,
                    had_exception=False,
                )

            except asyncio.CancelledError:
                full_content = full_content or "(Abgebrochen)"
                callbacks.conversation_update_last_assistant(full_content)
                callbacks.conversation_scroll_bottom()
                from app.chat.completion_status import CompletionStatus, completion_status_to_db

                completion_status_str = completion_status_to_db(CompletionStatus.INTERRUPTED)
                if merged_invocation is None:
                    merged_invocation = {"outcome": "cancelled"}
            except Exception as e:
                from app.chat.completion_status import CompletionStatus, completion_status_to_db

                full_content = full_content or f"Fehler: {e!s}"
                callbacks.conversation_update_last_assistant(full_content)
                callbacks.conversation_scroll_bottom()
                callbacks.show_error_inline(str(e))
                completion_status_str = completion_status_to_db(CompletionStatus.INTERRUPTED)
                if merged_invocation is None:
                    merged_invocation = {"outcome": "failed"}
            finally:
                try:
                    view = port.build_chat_invocation_view(
                        merged_invocation,
                        last_error_text=last_error_text,
                        last_error_kind=last_error_kind,
                        completion_status_db=completion_status_str,
                        model_name=model,
                    )
                    callbacks.details_set_invocation_view(view)
                except Exception:
                    pass
                if full_content:
                    port.save_assistant_message(
                        chat_id,
                        full_content,
                        model=model,
                        completion_status=completion_status_str,
                    )
                callbacks.conversation_set_last_completion(completion_status_str)
                callbacks.conversation_finalize_streaming()
                self._sink.apply_chat_patch(
                    ChatStatePatch(
                        load_state=ChatWorkspaceLoadState.IDLE,
                        stream_phase=ChatStreamPhase.IDLE,
                    )
                )
                callbacks.refresh_details_panel()
                callbacks.refresh_context_bar()
                callbacks.refresh_inspector()
        finally:
            self._active_send = False
            if callbacks.notify_send_session_completed is not None:
                callbacks.notify_send_session_completed(session)

    def _push_full(self, new_state: ChatWorkspaceState) -> None:
        self._state = new_state
        self._sink.apply_full_state(new_state)

    def _emit(self, event: ChatUiEvent) -> None:
        if self._on_ui_event is not None:
            self._on_ui_event(event)


def _placeholder_state() -> ChatWorkspaceState:
    return ChatWorkspaceState(
        load_state=ChatWorkspaceLoadState.IDLE,
        connection=ChatConnectionStatus.UNKNOWN,
        selected_chat_id=None,
        filter_text="",
        chats=(),
        messages=(),
        models=(),
        default_model_id=None,
        project=ProjectContextEntry(project_id=None, name=None),
        stream_phase=ChatStreamPhase.IDLE,
        streaming_message_index=None,
        error=None,
    )
