"""
ChatWorkspace – Erster operativer Arbeitsraum.

Session Explorer (links) + Conversation (Mitte) + Input (unten).
Vollständig an Ollama und DatabaseManager angebunden.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QTimer

from app.chat.stream_consume import (
    ChatStreamConsumeContext,
    ChatStreamConsumeHooks,
    consume_chat_model_stream,
)
from app.chat.stream_pipeline_trace import trace_persist_assistant
from app.ui_application.adapters.service_chat_port_adapter import ServiceChatPortAdapter
from app.ui_application.mappers.chat_details_mapper import format_chat_details_timestamp
from app.ui_application.mappers.chat_mapper import conversation_rows_from_message_entries
from app.ui_application.presenters.chat_presenter import ChatPresenter, use_presenter_send_pipeline
from app.ui_application.presenters.chat_send_callbacks import ChatSendCallbacks, ChatSendSession
from app.chat.final_assistant_message import final_assistant_message_for_persistence
from app.ui_application.presenters.chat_stream_assembler import append_stream_piece, extract_stream_display
from app.ui_contracts.common.enums import ChatStreamPhase, ChatWorkspaceLoadState
from app.ui_application.mappers.chat_details_mapper import build_chat_details_panel_state
from app.ui_contracts.workspaces.chat import (
    ChatStatePatch,
    ChatWorkspaceState,
    SelectChatCommand,
    SendMessageCommand,
    empty_chat_details_panel_state,
)

from app.gui.navigation.nav_areas import NavArea
from app.gui.domains.operations.chat.panels.chat_navigation_panel import ChatNavigationPanel
from app.gui.domains.operations.chat.panels.chat_details_panel import ChatDetailsPanel
from app.gui.domains.operations.chat.panels import (
    ChatConversationPanel,
    ChatInputPanel,
)
from app.gui.domains.operations.chat.panels.chat_context_bar import ChatContextBar
from app.gui.domains.operations.chat.panels.chat_item_context_menu import (
    build_context_bar_context_menu,
)
from PySide6.QtGui import QCursor


class ChatWorkspaceChatSink:
    """Spiegelt Contract-State/Patches auf Widgets (keine Fachlogik)."""

    __slots__ = ("_ws",)

    def __init__(self) -> None:
        self._ws: ChatWorkspace | None = None

    def bind(self, workspace: ChatWorkspace) -> None:
        self._ws = workspace

    def apply_full_state(self, state: ChatWorkspaceState) -> None:
        ws = self._ws
        if ws is None:
            return
        if state.error:
            ws._input.set_error(state.error.message)
        else:
            ws._input.set_error("")
        self._apply_load_and_stream_flags(ws, state.load_state, state.stream_phase)
        ws._current_chat_id = state.selected_chat_id
        ws._session_explorer.set_current_chat(state.selected_chat_id)
        if state.selected_chat_id is None:
            ws._conversation.clear()
        else:
            rows = conversation_rows_from_message_entries(state.messages)
            ws._conversation.load_messages(rows)
            ws._conversation.scroll_to_bottom()
        ws._refresh_context_bar()
        if state.details_panel is not None:
            ws._details_panel.apply_details_state(state.details_panel)

    def apply_chat_patch(self, patch: ChatStatePatch) -> None:
        ws = self._ws
        if ws is None:
            return
        if patch.clear_error:
            ws._input.set_error("")
        if patch.error is not None:
            ws._input.set_error(patch.error.message)
        if patch.load_state is not None or patch.stream_phase is not None:
            ls = patch.load_state if patch.load_state is not None else ChatWorkspaceLoadState.IDLE
            sp = patch.stream_phase if patch.stream_phase is not None else ChatStreamPhase.IDLE
            self._apply_load_and_stream_flags(ws, ls, sp)
        if patch.messages is not None and ws._current_chat_id is not None:
            rows = conversation_rows_from_message_entries(patch.messages)
            ws._conversation.load_messages(rows)
            ws._conversation.scroll_to_bottom()
        if patch.details_panel is not None:
            ws._details_panel.apply_details_state(patch.details_panel)

    @staticmethod
    def _apply_load_and_stream_flags(ws: ChatWorkspace, load_state: ChatWorkspaceLoadState, stream_phase: ChatStreamPhase) -> None:
        if load_state == ChatWorkspaceLoadState.STREAMING:
            ws._streaming = True
            ws._input.set_sending(True)
            ws._input.set_status("Antwort wird gestreamt…")
        elif load_state == ChatWorkspaceLoadState.LOADING_MESSAGES:
            ws._streaming = False
            ws._input.set_sending(False)
            ws._input.set_status("Nachrichten werden geladen…")
        elif load_state == ChatWorkspaceLoadState.ERROR:
            ws._streaming = False
            ws._input.set_sending(False)
            ws._input.set_status("")
        else:
            if stream_phase == ChatStreamPhase.IDLE:
                ws._streaming = False
                ws._input.set_sending(False)
                ws._input.set_status("")


class ChatWorkspace(QWidget):
    """Chat-Arbeitsraum mit Session Explorer, Conversation und Input."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatWorkspace")
        self._current_chat_id: int | None = None
        self._last_selected_chat_per_project: dict[int | None, int] = {}
        self._inspector_host = None
        self._streaming = False
        self._last_invocation_view: Optional[dict] = None
        self._chat_port = ServiceChatPortAdapter()
        self._chat_sink = ChatWorkspaceChatSink()
        self._chat_presenter = ChatPresenter(self._chat_sink, port=self._chat_port)
        self._setup_ui()
        self._chat_sink.bind(self)
        self._connect_signals()
        self._attach_chat_presenter_send_pipeline()
        self._connect_project_context()
        QTimer.singleShot(0, self._defer_load_models)
        QTimer.singleShot(50, self._refresh_context_bar)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._session_explorer = ChatNavigationPanel(
            self, nav_data=self._chat_port, chat_actions=self._chat_port
        )
        layout.addWidget(self._session_explorer)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)

        self._context_bar = ChatContextBar(self)
        self._connect_context_bar()
        center_layout.addWidget(self._context_bar)

        self._conversation = ChatConversationPanel(self)
        center_layout.addWidget(self._conversation, 1)

        self._input = ChatInputPanel(self)
        center_layout.addWidget(self._input)

        layout.addWidget(center, 1)

        self._details_panel = ChatDetailsPanel(self, details_ops=self._chat_port)
        self._details_panel.chat_updated.connect(self._on_details_chat_updated)
        layout.addWidget(self._details_panel)

    def _connect_signals(self):
        self._session_explorer.chat_selected.connect(self._on_session_selected)
        self._session_explorer.chat_deleted.connect(self._on_chat_deleted)
        self._input.send_requested.connect(self._on_send_requested)

    def _attach_chat_presenter_send_pipeline(self) -> None:
        self._chat_presenter.attach_send_pipeline(
            schedule_coro=lambda c: asyncio.create_task(c),
            callbacks=ChatSendCallbacks(
                conversation_add_user=self._conversation.add_user_message,
                conversation_scroll_bottom=self._conversation.scroll_to_bottom,
                conversation_add_placeholder=lambda m: self._conversation.add_assistant_placeholder(
                    model=m
                ),
                conversation_update_last_assistant=self._conversation.update_last_assistant,
                conversation_set_last_completion=self._conversation.set_last_assistant_completion_status,
                conversation_finalize_streaming=self._conversation.finalize_streaming,
                input_set_sending=lambda _b: None,
                details_set_invocation_view=self._set_invocation_view_from_presenter,
                refresh_session_explorer=self._session_explorer.refresh,
                set_session_explorer_current=self._session_explorer.set_current,
                refresh_context_bar=self._refresh_context_bar,
                refresh_details_panel=self._refresh_details_panel,
                refresh_inspector=self._refresh_inspector,
                show_error_inline=self._show_error,
                notify_send_session_completed=self._on_send_session_completed,
            ),
            session_factory=lambda: ChatSendSession(self._current_chat_id),
            busy_check=lambda: self._chat_presenter.is_send_active,
        )

    def _connect_context_bar(self) -> None:
        """Verbinde Kontextbar-Signale mit Aktionen."""
        self._context_bar.project_clicked.connect(self._on_context_bar_project_clicked)
        self._context_bar.chat_clicked.connect(self._on_context_bar_chat_clicked)
        self._context_bar.topic_clicked.connect(self._on_context_bar_topic_clicked)
        self._context_bar.context_menu_requested.connect(
            self._on_context_bar_menu_requested
        )

    def _on_context_bar_project_clicked(self) -> None:
        """Projekt-Label geklickt → ProjectSwitcherDialog öffnen."""
        try:
            from app.gui.project_switcher.project_switcher_dialog import (
                ProjectSwitcherDialog,
            )
            dlg = ProjectSwitcherDialog(self)
            dlg.project_selected.connect(self._on_project_switcher_selected)
            dlg.exec()
        except Exception:
            pass

    def _on_project_switcher_selected(self, project_id: object) -> None:
        """Projekt aus Switcher-Dialog ausgewählt."""
        try:
            self._chat_port.set_active_project_selection(project_id)
        except Exception:
            pass

    def _on_context_bar_chat_clicked(self) -> None:
        """Chat-Label geklickt → Umbenennen-Dialog."""
        if not self._current_chat_id:
            return
        self._details_panel._on_rename()

    def _on_context_bar_topic_clicked(self) -> None:
        """Topic-Label geklickt → Topic-Combo im Details-Panel fokussieren oder Dialog."""
        if not self._current_chat_id or not self._project_id_for_context():
            return
        self._details_panel.set_expanded(True)
        self._details_panel._topic_combo.showPopup()

    def _project_id_for_context(self) -> int | None:
        """Projekt-ID des aktuellen Chats für Kontext-Aktionen."""
        if not self._current_chat_id:
            return None
        try:
            return self._chat_port.project_id_for_chat(self._current_chat_id)
        except Exception:
            return None

    def _on_context_bar_menu_requested(self) -> None:
        """Rechtsklick auf Kontextbar → Kontextmenü anzeigen."""
        self._show_context_bar_menu()

    def _show_context_bar_menu(self) -> None:
        """Zeigt Kontextmenü der Kontextbar an."""
        try:
            project_id = self._project_id_for_context()
            chat_id = self._current_chat_id

            chat_title = "Neuer Chat"
            topic_id = None
            is_pinned = False
            is_archived = False
            topics = []
            if chat_id:
                info = self._chat_port.get_chat_info(chat_id)
                if info:
                    chat_title = info.get("title", "Neuer Chat")
                    topic_id = info.get("topic_id")
                    is_pinned = bool(info.get("pinned"))
                    is_archived = bool(info.get("archived"))
            if project_id:
                topics = self._chat_port.list_topic_rows_for_project(project_id)

            menu = build_context_bar_context_menu(
                chat_id=chat_id,
                project_id=project_id,
                chat_title=chat_title,
                current_topic_id=topic_id,
                is_pinned=is_pinned,
                is_archived=is_archived,
                topics=topics,
                parent_widget=self,
                on_action=self._on_details_chat_updated,
                on_project_switch_requested=lambda: self._on_context_bar_project_clicked(),
                on_new_chat_requested=lambda: self._session_explorer._on_new_chat(),
                on_chat_deleted=lambda cid: self._on_chat_deleted(cid),
                chat_ops=self._chat_port,
            )
            menu.exec(QCursor.pos())
        except Exception:
            pass

    def _connect_project_context(self) -> None:
        """Subscribe to project_context_changed – reload only active project's chats."""
        try:
            from app.gui.events.project_events import subscribe_project_events
            subscribe_project_events(self._on_project_context_changed)
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        """Project changed – clear workspace; restore last selection for new project."""
        new_project_id = payload.get("project_id")
        self._current_chat_id = None
        try:
            self._chat_presenter.handle_command(SelectChatCommand(chat_id=None))
        except Exception:
            pass
        self._session_explorer.set_current(None)
        self._conversation.clear()
        self._details_panel.clear()
        self._refresh_inspector()
        self._restore_project_selection(new_project_id)

    def _restore_project_selection(self, project_id: int | None) -> None:
        """Restore last selected chat for project, or select first if available."""
        last_chat_id = self._last_selected_chat_per_project.get(project_id)
        if last_chat_id is not None and self._session_explorer.contains_chat_id(last_chat_id):
            self._session_explorer.set_current(last_chat_id)
            self._on_session_selected(last_chat_id)
            return
        first_id = self._session_explorer.get_first_chat_id()
        if first_id is not None:
            self._session_explorer.set_current(first_id)
            self._on_session_selected(first_id)
        else:
            self._refresh_context_bar()

    def _on_session_selected(self, chat_id: int):
        self._last_invocation_view = None
        self._current_chat_id = chat_id
        try:
            pid = self._chat_port.get_active_project_id()
            self._last_selected_chat_per_project[pid] = chat_id
        except Exception:
            pass
        try:
            self._chat_presenter.handle_command(SelectChatCommand(chat_id=chat_id))
        except Exception:
            self._load_messages(chat_id)
        self._refresh_details_panel()
        self._refresh_context_bar()
        self._refresh_inspector()
        self._update_breadcrumb_detail(chat_id)

    def _on_chat_deleted(self, chat_id: int) -> None:
        """Clear workspace if the deleted chat was active; select first remaining."""
        if self._current_chat_id != chat_id:
            return
        self._current_chat_id = None
        self._conversation.clear()
        self._details_panel.clear()
        self._refresh_inspector()
        first_id = self._session_explorer.get_first_chat_id()
        if first_id is not None:
            self._session_explorer.set_current(first_id)
            self._on_session_selected(first_id)
        else:
            self._refresh_context_bar()

    def _update_breadcrumb_detail(self, chat_id: int) -> None:
        """Aktualisiert Breadcrumb auf Project / Chat / Session-Titel."""
        try:
            from app.gui.breadcrumbs import get_breadcrumb_manager
            info = self._chat_port.get_chat_info(chat_id)
            title = info.get("title", "Neuer Chat") if info else "Neuer Chat"
            mgr = get_breadcrumb_manager()
            if mgr:
                mgr.set_path_with_detail(NavArea.OPERATIONS, "operations_chat", title)
        except Exception:
            pass

    def _load_messages(self, chat_id: int) -> None:
        """Lädt Nachrichten für einen Chat."""
        try:
            messages = self._chat_port.load_conversation_rows(chat_id)
            self._conversation.load_messages(messages)
            self._conversation.scroll_to_bottom()
        except Exception:
            self._conversation.clear()

    def _defer_load_models(self) -> None:
        """Deferriert Modell-Load bis Event-Loop läuft."""
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._load_models_coro())
        except RuntimeError:
            QTimer.singleShot(100, self._defer_load_models)

    async def _load_models_coro(self) -> None:
        """Lädt Unified-Katalog (Registry, Ollama, lokale Assets) für die Modell-Combo."""
        try:
            catalog, default = await self._chat_port.load_unified_model_catalog()
            selectable = [e["selection_id"] for e in catalog if e.get("chat_selectable")]
            self._input.set_unified_catalog(catalog, default_selection_id=default)
            if selectable:
                self._input.refresh_model_ancillary_display()
            else:
                self._input.set_status("Kein chat-fähiges Modell – Ollama starten oder Cloud aktivieren.")
        except Exception:
            self._input.set_models([])
            self._input.set_status("Modellliste nicht ladbar")

    def _on_send_requested(self, text: str) -> None:
        """Startet Send: standardmaessig ChatPresenter; deprecated siehe ``use_presenter_send_pipeline``."""
        if use_presenter_send_pipeline():
            if self._chat_presenter.is_send_active:
                return
            self._chat_presenter.handle_command(
                SendMessageCommand(text=text, model_id=self._input.get_selected_model() or None)
            )
            return
        if self._streaming:
            return
        asyncio.create_task(self._run_send_legacy(text))

    def _set_invocation_view_from_presenter(self, view: object) -> None:
        self._last_invocation_view = view if isinstance(view, dict) else None
        self._details_panel.set_last_invocation_view(view)

    def _on_send_session_completed(self, session: ChatSendSession) -> None:
        self._current_chat_id = session.chat_id

    async def _run_send_legacy(self, text: str) -> None:
        """
        Deprecated Workspace-Sendeinstieg (nur bei ``LINUX_DESKTOP_CHAT_LEGACY_CHAT_SEND=1``).

        Gleiche Port-/Consume-Finalisierung wie Presenter, aber ohne Butler und ohne Streaming-Patches
        am Contract-State; siehe ``docs/04_architecture/CHAT_SEGMENT_CLOSEOUT.md``.
        """
        if self._streaming:
            return
        text = (text or "").strip()
        if not text:
            return

        port = self._chat_port

        model = self._input.get_selected_model()
        if not model:
            self._show_error("Bitte ein Modell auswählen.")
            return

        if self._current_chat_id is None:
            try:
                pid = port.get_active_project_id()
                if pid is not None:
                    self._current_chat_id = port.create_chat_in_project(pid, "Neuer Chat")
                else:
                    self._current_chat_id = port.create_chat_global("Neuer Chat")
            except Exception as e:
                self._show_error(f"Chat konnte nicht angelegt werden: {e}")
                return
            self._session_explorer.refresh()
            self._session_explorer.set_current(self._current_chat_id)
            self._refresh_context_bar()

        chat_id = self._current_chat_id
        port.save_user_message(chat_id, text)
        try:
            if port.maybe_autotitle_from_first_message(chat_id, text):
                self._session_explorer.refresh()
        except Exception:
            pass
        self._conversation.add_user_message(text)
        self._conversation.scroll_to_bottom()

        self._streaming = True
        self._input.set_sending(True)

        ctx = ChatStreamConsumeContext()
        full_content = ""
        provider_done = False
        had_error = False
        completion_status_str = None
        merged_invocation: Optional[Dict[str, Any]] = None
        last_error_kind: Optional[str] = None
        last_error_text: Optional[str] = None
        self._details_panel.set_last_invocation_view(None)
        self._last_invocation_view = None

        from app.chat.completion_status import CompletionStatus, completion_status_to_db

        try:
            api_messages = port.build_api_messages(chat_id)

            self._conversation.add_assistant_placeholder(model=model)

            temp, max_tokens, stream_enabled = port.get_stream_settings()

            await consume_chat_model_stream(
                ctx,
                chunk_source=port.iter_chat_chunks(
                    model=model,
                    chat_id=chat_id,
                    api_messages=api_messages,
                    temperature=temp,
                    max_tokens=max_tokens,
                    stream=stream_enabled,
                ),
                merge_invocation=port.merge_invocation_payload,
                invocation_error_kind=port.invocation_error_kind,
                completion_status_for_outcome=port.completion_status_for_outcome,
                hooks=ChatStreamConsumeHooks(
                    update_assistant_text=self._conversation.update_last_assistant,
                    scroll_bottom=self._conversation.scroll_to_bottom,
                ),
            )
            full_content = ctx.full_content
            merged_invocation = ctx.merged_invocation
            last_error_kind = ctx.last_error_kind
            last_error_text = ctx.last_error_text
            provider_done = ctx.provider_done
            had_error = ctx.had_error
            completion_status_str = ctx.completion_status_str

        except asyncio.CancelledError:
            full_content = (
                full_content
                or final_assistant_message_for_persistence(ctx.accumulator)
                or "(Abgebrochen)"
            )
            self._conversation.update_last_assistant(full_content)
            self._conversation.scroll_to_bottom()
            completion_status_str = completion_status_to_db(CompletionStatus.INTERRUPTED)
            if merged_invocation is None:
                merged_invocation = {"outcome": "cancelled"}
        except Exception as e:
            full_content = (
                full_content
                or final_assistant_message_for_persistence(ctx.accumulator)
                or f"Fehler: {e!s}"
            )
            self._conversation.update_last_assistant(full_content)
            self._conversation.scroll_to_bottom()
            QTimer.singleShot(0, lambda: self._show_error(str(e)))
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
                self._last_invocation_view = view
                self._details_panel.set_last_invocation_view(view)
            except Exception:
                pass
            if full_content:
                trace_persist_assistant(
                    chat_id=chat_id,
                    text_len=len(full_content),
                    text_preview=full_content,
                )
                port.save_assistant_message(
                    chat_id,
                    full_content,
                    model=model,
                    completion_status=completion_status_str,
                )
            self._conversation.set_last_assistant_completion_status(completion_status_str)
            self._conversation.finalize_streaming()
            self._streaming = False
            self._input.set_sending(False)
            self._refresh_details_panel()
            self._refresh_context_bar()
            self._refresh_inspector()

    def _show_error(self, msg: str) -> None:
        """Zeigt eine Fehlermeldung als Inline-Warnung über dem Chat-Input (nicht als AI-Nachricht)."""
        if self._input:
            self._input.set_error(msg)

    def _on_inspector_topic_changed(self, chat_id: int, topic_id: object) -> None:
        """Topic im Inspector geändert → Chat-Liste aktualisieren."""
        self._session_explorer.refresh()

    def _on_details_chat_updated(self) -> None:
        """Details panel action (rename, pin, etc.) → refresh list and inspector."""
        self._session_explorer.refresh()
        self._refresh_context_bar()
        self._refresh_inspector()

    def _refresh_context_bar(self) -> None:
        """Aktualisiert die Kontextleiste mit Projekt, Chat, Topic."""
        project_name = None
        chat_title = None
        topic_name = None

        try:
            if self._current_chat_id:
                info = self._chat_port.get_chat_info(self._current_chat_id)
                if info:
                    chat_title = info.get("title") or "Neuer Chat"
                    topic_name = info.get("topic_name")
                proj_id = self._chat_port.project_id_for_chat(self._current_chat_id)
                if proj_id is not None:
                    proj = self._chat_port.get_project_record(proj_id)
                    project_name = proj.get("name") if proj else None
            if project_name is None:
                prec = self._chat_port.get_active_project_record()
                if prec:
                    project_name = prec.get("name")
                if project_name is None:
                    project_name = "Globale Chats"
        except Exception:
            project_name = "—"
            chat_title = "—" if not chat_title else chat_title

        self._context_bar.set_context(
            project_name=project_name,
            chat_title=chat_title,
            topic_name=topic_name,
        )

    def _refresh_details_panel(self) -> None:
        """Update details panel with active chat metadata (Contract-DTO über Sink)."""
        try:
            model_label = (
                (self._input.get_selected_model() or None) if self._input else None
            )
            st = build_chat_details_panel_state(
                self._chat_port,
                self._current_chat_id,
                model_label=model_label,
            )
            if st is None:
                st = empty_chat_details_panel_state()
            self._chat_sink.apply_chat_patch(ChatStatePatch(details_panel=st))
            if not self._current_chat_id:
                self._details_panel.set_last_invocation_view(None)
                self._last_invocation_view = None
            elif self._last_invocation_view:
                self._details_panel.set_last_invocation_view(self._last_invocation_view)
        except Exception:
            self._details_panel.clear()

    def open_with_context(self, ctx: dict) -> None:
        """Öffnet einen Chat aus Project-Hub-Kontext. ctx: {chat_id: int}."""
        chat_id = ctx.get("chat_id")
        if chat_id is not None:
            self._session_explorer.refresh()
            self._session_explorer.set_current(chat_id)
            self._on_session_selected(chat_id)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Wird von WorkspaceHost aufgerufen. Setzt Chat-Kontext im Inspector."""
        self._inspector_host = inspector_host
        self._inspector_content_token = content_token
        self._refresh_inspector()

    def _refresh_inspector(self) -> None:
        """Aktualisiert den Inspector mit aktuellem Kontext."""
        if not self._inspector_host:
            return
        from app.gui.inspector.chat_context_inspector import ChatContextInspector

        model = self._input.get_selected_model() if self._input else None
        model_str = model or "(kein Modell)"
        session_str = str(self._current_chat_id) if self._current_chat_id else "(neu)"
        status = "Wird gesendet…" if self._streaming else "Bereit"

        msg_count = 0
        project_id = None
        project_name = None
        topic_id = None
        topic_name = None
        chat_title = None
        last_activity = None
        if self._current_chat_id:
            try:
                messages = self._chat_port.load_conversation_rows(self._current_chat_id)
                msg_count = len(messages)
                info = self._chat_port.get_chat_info(self._current_chat_id)
                if info:
                    chat_title = info.get("title", "Neuer Chat")
                    last_activity = format_chat_details_timestamp(info.get("last_activity"))
                    topic_id = info.get("topic_id")
                    topic_name = info.get("topic_name")
                proj_id = self._chat_port.project_id_for_chat(self._current_chat_id)
                if proj_id:
                    project_id = proj_id
                    proj = self._chat_port.get_project_record(proj_id)
                    project_name = proj.get("name") if proj else None
            except Exception:
                pass

        chat_inspector = ChatContextInspector(
            session_id=session_str,
            chat_id=self._current_chat_id,
            chat_title=chat_title or "Neuer Chat",
            model=model_str,
            context_status=status,
            message_count=msg_count,
            project_id=project_id,
            project_name=project_name,
            topic_id=topic_id,
            topic_name=topic_name,
            last_activity=last_activity or "—",
            chat_ops=self._chat_port,
        )
        chat_inspector.topic_changed.connect(self._on_inspector_topic_changed)

        from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget
        from app.gui.domains.debug import ContextInspectionPanel

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(chat_inspector)
        try:
            from app.context.debug.context_debug_flag import is_context_debug_enabled
            if is_context_debug_enabled():
                inspection_panel = ContextInspectionPanel()
                inspection_panel.set_chat_id(self._current_chat_id)
                container_layout.addWidget(inspection_panel, 1)
        except Exception:
            pass

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        scroll.setWidget(container)

        token = getattr(self, "_inspector_content_token", None)
        self._inspector_host.set_content(scroll, content_token=token)


def _extract_content(chunk: object) -> tuple[str, str, str | None, bool]:
    """Tests/Legacy: (display_piece, thinking_stripped, error, done) ohne StreamPieceSource."""
    out, th, err, done, _src = extract_stream_display(chunk if isinstance(chunk, dict) else None)
    return out, th, err, done


_append_stream_piece = append_stream_piece
