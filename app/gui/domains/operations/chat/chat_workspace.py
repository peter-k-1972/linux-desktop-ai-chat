"""
ChatWorkspace – Erster operativer Arbeitsraum.

Session Explorer (links) + Conversation (Mitte) + Input (unten).
Vollständig an Ollama und DatabaseManager angebunden.
"""

import asyncio
from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QTimer

from app.gui.inspector.chat_context_inspector import _format_datetime
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


def _append_stream_piece(full: str, piece: str) -> str:
    """
    Hängt einen Stream-Teil an und entfernt maximales Suffix/Präfix-Overlap.

    Verhindert Duplikate wenn späteres ``message.content`` den bereits über
    ``thinking`` gezeigten Text wiederholt, oder wenn ein Provider kumulative
    statt strikt inkrementelle Blöcke sendet.
    """
    if not piece:
        return full
    if not full:
        return piece
    max_k = min(len(full), len(piece))
    for k in range(max_k, 0, -1):
        if full.endswith(piece[:k]):
            return full + piece[k:]
    return full + piece


def _extract_content(chunk: Dict[str, Any]) -> tuple[str, str, str | None, bool]:
    """
    Extrahiert Anzeige-Text, thinking, error, done aus einem Stream-Chunk.

    Wenn ``message.content`` leer ist, aber ``message.thinking`` nicht, wird
    ``thinking`` als Anzeige-Text verwendet (z. B. Modelle mit getrenntem
    Thinking-Stream).
    """
    if chunk is None or not isinstance(chunk, dict):
        return ("", "", None, False)
    if "error" in chunk:
        return ("", "", chunk.get("error", ""), chunk.get("done", False))
    msg = chunk.get("message") or {}
    raw_c = msg.get("content")
    if raw_c is None:
        raw_c = ""
    if isinstance(raw_c, str):
        content_str = raw_c
    else:
        content_str = str(raw_c)
    th_raw = msg.get("thinking") or ""
    if not isinstance(th_raw, str):
        th_raw = str(th_raw) if th_raw is not None else ""
    thinking = th_raw.strip()
    if content_str.strip():
        out = content_str
    elif thinking:
        out = th_raw
    else:
        out = ""
    done = chunk.get("done", False)
    return (out, thinking, None, done)


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
        self._setup_ui()
        self._connect_signals()
        self._connect_project_context()
        QTimer.singleShot(0, self._defer_load_models)
        QTimer.singleShot(50, self._refresh_context_bar)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._session_explorer = ChatNavigationPanel(self)
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

        self._details_panel = ChatDetailsPanel(self)
        self._details_panel.chat_updated.connect(self._on_details_chat_updated)
        self._details_panel.set_get_model_callback(
            lambda: self._input.get_selected_model() if self._input else ""
        )
        layout.addWidget(self._details_panel)

    def _connect_signals(self):
        self._session_explorer.chat_selected.connect(self._on_session_selected)
        self._session_explorer.chat_deleted.connect(self._on_chat_deleted)
        self._input.send_requested.connect(self._on_send_requested)

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
            from app.core.context.project_context_manager import get_project_context_manager
            mgr = get_project_context_manager()
            mgr.set_active_project(project_id)
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
            from app.services.project_service import get_project_service
            return get_project_service().get_project_of_chat(self._current_chat_id)
        except Exception:
            return None

    def _on_context_bar_menu_requested(self) -> None:
        """Rechtsklick auf Kontextbar → Kontextmenü anzeigen."""
        self._show_context_bar_menu()

    def _show_context_bar_menu(self) -> None:
        """Zeigt Kontextmenü der Kontextbar an."""
        try:
            from app.services.chat_service import get_chat_service
            from app.services.project_service import get_project_service
            from app.services.topic_service import get_topic_service

            chat_svc = get_chat_service()
            proj_svc = get_project_service()
            project_id = self._project_id_for_context()
            chat_id = self._current_chat_id

            chat_title = "Neuer Chat"
            topic_id = None
            is_pinned = False
            is_archived = False
            topics = []
            if chat_id:
                info = chat_svc.get_chat_info(chat_id)
                if info:
                    chat_title = info.get("title", "Neuer Chat")
                    topic_id = info.get("topic_id")
                    is_pinned = bool(info.get("pinned"))
                    is_archived = bool(info.get("archived"))
            if project_id:
                topics = get_topic_service().list_topics_for_project(project_id)

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
            from app.core.context.project_context_manager import get_project_context_manager
            pid = get_project_context_manager().get_active_project_id()
            self._last_selected_chat_per_project[pid] = chat_id
        except Exception:
            pass
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
            from app.services.chat_service import get_chat_service
            from app.gui.breadcrumbs import get_breadcrumb_manager
            svc = get_chat_service()
            info = svc.get_chat_info(chat_id)
            title = info.get("title", "Neuer Chat") if info else "Neuer Chat"
            mgr = get_breadcrumb_manager()
            if mgr:
                mgr.set_path_with_detail(NavArea.OPERATIONS, "operations_chat", title)
        except Exception:
            pass

    def _load_messages(self, chat_id: int) -> None:
        """Lädt Nachrichten für einen Chat."""
        try:
            from app.services.chat_service import get_chat_service
            svc = get_chat_service()
            messages = svc.load_chat(chat_id)
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
            from app.services.infrastructure import get_infrastructure
            from app.services.model_service import get_model_service
            from app.services.unified_model_catalog_service import get_unified_model_catalog_service

            settings = get_infrastructure().settings
            catalog = await get_unified_model_catalog_service().build_catalog_for_chat(settings)
            selectable = [e["selection_id"] for e in catalog if e.get("chat_selectable")]
            default = None
            if selectable:
                default = get_model_service().get_default_chat_model(selectable)
            self._input.set_unified_catalog(catalog, default_selection_id=default)
            if selectable:
                self._input.refresh_model_ancillary_display()
            else:
                self._input.set_status("Kein chat-fähiges Modell – Ollama starten oder Cloud aktivieren.")
        except Exception:
            self._input.set_models([])
            self._input.set_status("Modellliste nicht ladbar")

    def _on_send_requested(self, text: str) -> None:
        """Startet den asynchronen Send-Vorgang."""
        if self._streaming:
            return
        asyncio.create_task(self._run_send(text))

    async def _run_send(self, text: str) -> None:
        """Führt den Chat-Lauf durch."""
        if self._streaming:
            return
        text = (text or "").strip()
        if not text:
            return

        chat_svc = self._get_chat_service()
        if not chat_svc:
            self._show_error("Chat-Service nicht verfügbar.")
            return

        model = self._input.get_selected_model()
        if not model:
            self._show_error("Bitte ein Modell auswählen.")
            return

        if self._current_chat_id is None:
            try:
                from app.core.context.project_context_manager import get_project_context_manager
                mgr = get_project_context_manager()
                pid = mgr.get_active_project_id()
                if pid is not None:
                    self._current_chat_id = chat_svc.create_chat_in_project(
                        pid, "Neuer Chat"
                    )
                else:
                    self._current_chat_id = chat_svc.create_chat("Neuer Chat")
            except Exception as e:
                self._show_error(f"Chat konnte nicht angelegt werden: {e}")
                return
            self._session_explorer.refresh()
            self._session_explorer.set_current(self._current_chat_id)
            self._refresh_context_bar()

        chat_id = self._current_chat_id
        chat_svc.save_message(chat_id, "user", text)
        try:
            info = chat_svc.get_chat_info(chat_id)
            if info and (info.get("title") or "").strip() in ("", "Neuer Chat"):
                title = (text[:50] + "…") if len(text) > 50 else text
                chat_svc.save_chat_title(chat_id, title)
                self._session_explorer.refresh()
        except Exception:
            pass
        self._conversation.add_user_message(text)
        self._conversation.scroll_to_bottom()

        self._streaming = True
        self._input.set_sending(True)

        full_content = ""
        provider_done = False
        had_error = False
        completion_status_str = None
        merged_invocation: Optional[Dict[str, Any]] = None
        last_error_kind: Optional[str] = None
        last_error_text: Optional[str] = None
        self._details_panel.set_last_invocation_view(None)
        self._last_invocation_view = None

        try:
            messages = chat_svc.load_chat(chat_id)
            api_messages = [
                {"role": row[0], "content": row[1]}
                for row in messages
            ]

            self._conversation.add_assistant_placeholder(model=model)

            from app.services.infrastructure import get_infrastructure
            from app.chat.completion_heuristics import assess_completion_heuristic
            from app.chat.completion_status import (
                CompletionStatus,
                completion_status_to_db,
            )

            settings = get_infrastructure().settings
            stream_enabled = getattr(settings, "chat_streaming_enabled", True)
            from app.services.model_invocation_display import (
                error_kind_from_chunk,
                merge_model_invocation_payload,
            )

            async for chunk in chat_svc.chat(
                model=model,
                messages=api_messages,
                chat_id=chat_id,
                temperature=getattr(settings, "temperature", 0.7),
                max_tokens=getattr(settings, "max_tokens", 4096),
                stream=stream_enabled,
            ):
                merged_invocation = merge_model_invocation_payload(merged_invocation, chunk)
                ek = error_kind_from_chunk(chunk)
                if ek:
                    last_error_kind = ek
                content, _, error, done = _extract_content(chunk)
                if done:
                    provider_done = True
                if error:
                    had_error = True
                    last_error_text = str(error)
                    full_content = f"Fehler: {error}"
                    self._conversation.update_last_assistant(full_content)
                    self._conversation.scroll_to_bottom()
                    break
                if content:
                    full_content = _append_stream_piece(full_content, content)
                    self._conversation.update_last_assistant(full_content)
                    self._conversation.scroll_to_bottom()

            status = assess_completion_heuristic(
                full_content,
                provider_finished_normally=provider_done,
                had_error=had_error,
                had_exception=False,
            )
            completion_status_str = completion_status_to_db(status)

        except asyncio.CancelledError:
            full_content = full_content or "(Abgebrochen)"
            self._conversation.update_last_assistant(full_content)
            self._conversation.scroll_to_bottom()
            completion_status_str = completion_status_to_db(CompletionStatus.INTERRUPTED)
            if merged_invocation is None:
                merged_invocation = {"outcome": "cancelled"}
        except Exception as e:
            full_content = full_content or f"Fehler: {e!s}"
            self._conversation.update_last_assistant(full_content)
            self._conversation.scroll_to_bottom()
            QTimer.singleShot(0, lambda: self._show_error(str(e)))
            completion_status_str = completion_status_to_db(CompletionStatus.INTERRUPTED)
            if merged_invocation is None:
                merged_invocation = {"outcome": "failed"}
        finally:
            try:
                from app.services.model_invocation_display import build_chat_invocation_view

                view = build_chat_invocation_view(
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
                chat_svc.save_message(
                    chat_id,
                    "assistant",
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
            from app.core.context.project_context_manager import get_project_context_manager
            from app.services.project_service import get_project_service
            from app.services.chat_service import get_chat_service

            if self._current_chat_id:
                chat_svc = self._get_chat_service()
                if chat_svc:
                    info = chat_svc.get_chat_info(self._current_chat_id)
                    if info:
                        chat_title = info.get("title") or "Neuer Chat"
                        topic_name = info.get("topic_name")
                    proj_id = get_project_service().get_project_of_chat(self._current_chat_id)
                    if proj_id:
                        proj = get_project_service().get_project(proj_id)
                        project_name = proj.get("name") if proj else None
            if project_name is None:
                mgr = get_project_context_manager()
                proj = mgr.get_active_project()
                if proj and isinstance(proj, dict):
                    project_name = proj.get("name")
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
        """Update details panel with active chat metadata."""
        if not self._current_chat_id:
            self._details_panel.clear()
            return
        try:
            chat_svc = self._get_chat_service()
            if not chat_svc:
                self._details_panel.clear()
                return
            info = chat_svc.get_chat_info(self._current_chat_id)
            if not info:
                self._details_panel.clear()
                return
            project_id = None
            project_name = None
            try:
                from app.services.project_service import get_project_service
                project_id = get_project_service().get_project_of_chat(
                    self._current_chat_id
                )
                if project_id:
                    proj = get_project_service().get_project(project_id)
                    project_name = proj.get("name") if proj else None
            except Exception:
                pass
            last_agent = chat_svc.get_last_assistant_agent_for_chat(
                self._current_chat_id
            )
            self._details_panel.update_chat(
                chat_id=self._current_chat_id,
                chat_title=info.get("title", "Neuer Chat"),
                project_id=project_id,
                project_name=project_name,
                topic_id=info.get("topic_id"),
                topic_name=info.get("topic_name"),
                created_at=info.get("created_at"),
                last_activity=info.get("last_activity"),
                last_assistant_agent=last_agent,
                is_pinned=bool(info.get("pinned")),
                is_archived=bool(info.get("archived")),
            )
            if self._last_invocation_view:
                self._details_panel.set_last_invocation_view(self._last_invocation_view)
        except Exception:
            self._details_panel.clear()

    def _get_chat_service(self):
        try:
            from app.services.chat_service import get_chat_service
            return get_chat_service()
        except Exception:
            return None

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
                chat_svc = self._get_chat_service()
                if chat_svc:
                    messages = chat_svc.load_chat(self._current_chat_id)
                    msg_count = len(messages)
                    info = chat_svc.get_chat_info(self._current_chat_id)
                    if info:
                        chat_title = info.get("title", "Neuer Chat")
                        last_activity = _format_datetime(info.get("last_activity"))
                        topic_id = info.get("topic_id")
                        topic_name = info.get("topic_name")
                from app.services.project_service import get_project_service
                proj_id = get_project_service().get_project_of_chat(self._current_chat_id)
                if proj_id:
                    project_id = proj_id
                    proj = get_project_service().get_project(proj_id)
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
