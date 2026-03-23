"""
ChatWidget – Haupt-Chat-Bereich mit Conversation, Composer und Side-Panel.
"""

import asyncio
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QTimer
from qasync import asyncSlot

from app.gui.domains.operations.chat.panels.conversation_view import ConversationView
from app.gui.domains.operations.chat.panels.chat_composer_widget import ChatComposerWidget
from app.gui.domains.operations.chat.panels.chat_header_widget import ChatHeaderWidget
from app.gui.domains.operations.chat.panels.chat_side_panel import ChatSidePanel
from app.tools import FileSystemTools
from app.utils.paths import DEFAULT_LEGACY_ICONS_PATH_STR
from app.core.commands.chat_commands import parse_slash_command
from app.core.models.roles import ModelRole
from app.core.models.orchestrator import ModelOrchestrator
from app.agents.agent_registry import get_agent_registry
from app.agents.agent_profile import AgentProfile
from app.core.llm import OutputPipeline
from app.rag.service import RAGService
from app.debug.emitter import emit_event
from app.debug.agent_event import EventType
from app.agents.research_service import create_research_agent
from app.agents.orchestration_service import create_orchestration_service
from app.core.llm.llm_complete import complete


# --- Module-level helpers (used by tests) ---

def is_placeholder_or_invalid_assistant_message(text: str) -> bool:
    """Prüft, ob der Text ein Platzhalter oder ungültiger Assistant-Text ist."""
    if text is None:
        return True
    s = (text or "").strip()
    if not s:
        return True
    if s == "...":
        return True
    if "(Kein Inhalt von Ollama erhalten)" in s:
        return True
    if "(Ollama hat keinen finalen Antworttext geliefert)" in s:
        return True
    if "(Ollama hat keinen Stream zurückgeliefert)" in s:
        return True
    if "Thinking-Daten" in s and "keinen finalen Antworttext" in s:
        return True
    return False


def _create_default_pipeline():
    """Erstellt eine Pipeline mit Standardeinstellungen (für Tests/Backward-Compat)."""
    return OutputPipeline(
        strip_html=True,
        preserve_markdown=True,
        retry_without_thinking=True,
        max_retries=1,
    )


def finalize_stream_response(
    content: str,
    thinking_chunks: List[str],
    done: bool,
) -> str:
    """
    Ermittelt den finalen Antworttext aus Content und Thinking-Chunks.
    Delegiert an die Output-Pipeline für einheitliche Verarbeitung.
    - Content hat Vorrang; wenn vorhanden, wird er bereinigt und zurückgegeben.
    - Nur Thinking: Fallback-Text.
    - done ohne Content: Platzhalter.
    - Kein Stream: anderer Platzhalter.
    """
    pipeline = _create_default_pipeline()
    result = pipeline.process(
        raw_content=content,
        thinking_chunks=thinking_chunks,
        done=done,
        retry_count=0,
    )
    return result.display_text()


def _extract_chunk_parts(chunk: Optional[Dict[str, Any]]) -> Tuple[str, str, Optional[str]]:
    """
    Extrahiert content, thinking und error aus einem Stream-Chunk.
    Returns: (content, thinking, error)
    Content wird nicht gestrippt, um exakte Konkatenation zu erhalten.
    Defensiv: Ungültige Chunk-Formen (None, Nicht-Dict, message nicht Dict) → leere Rückgabe.
    """
    if chunk is None or not isinstance(chunk, dict):
        return ("", "", None)
    if "error" in chunk:
        return ("", "", chunk.get("error", ""))
    msg = chunk.get("message")
    if msg is None or not isinstance(msg, dict):
        msg = {}
    content = msg.get("content") or ""
    thinking = (msg.get("thinking") or "").strip()
    return (content, thinking, None)


# --- Tool call pattern ---
_TOOL_CALL_PATTERN = re.compile(
    r'<tool_call\s+name="([^"]+)"\s*/>',
    re.IGNORECASE | re.DOTALL,
)


def _parse_tool_calls(text: str) -> List[Tuple[str, str]]:
    """
    Parst <tool_call name="..."/> aus dem Text.
    Returns: [(name, full_match), ...]
    """
    results = []
    for m in _TOOL_CALL_PATTERN.finditer(text):
        results.append((m.group(1), m.group(0)))
    return results


class ChatWidget(QWidget):
    """
    Haupt-Chat-Widget: Conversation, Composer, Header, optional Side-Panel.
    """

    update_chat_signal = Signal(str, bool)  # (text, is_final)

    def __init__(
        self,
        client,
        settings,
        db,
        orchestrator: Optional[ModelOrchestrator] = None,
        rag_service: Optional[RAGService] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.client = client
        self.settings = settings
        self.db = db
        self.orchestrator = orchestrator
        self.rag_service = rag_service
        self.chat_id: Optional[int] = None
        self.temperature = getattr(settings, "temperature", 0.7)
        self.max_tokens = getattr(settings, "max_tokens", 4096)
        self._current_model = getattr(settings, "model", "llama2")
        self.tools: Optional[FileSystemTools] = None
        self.current_full_response = ""
        self._streaming = False
        self._streaming_message_widget = None
        self._streaming_content_buffer = ""
        self._streaming_thinking_chunks: List[str] = []

        self._pipeline = self._create_pipeline()

        self.init_ui()
        self._apply_routing_settings()
        QTimer.singleShot(0, self.load_models)

    def init_ui(self):
        self.setObjectName("chatWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = ChatHeaderWidget(theme=self.settings.theme, parent=self)
        layout.addWidget(self.header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("chatMainSplitter")

        # Linke Seite: Conversation + Composer
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.conversation_view = ConversationView(theme=self.settings.theme, parent=self)
        left_layout.addWidget(self.conversation_view, 1)

        self.composer = ChatComposerWidget(
            icons_path=getattr(self.settings, "icons_path", DEFAULT_LEGACY_ICONS_PATH_STR),
            parent=self,
        )
        self.composer.send_requested.connect(self._on_send)
        left_layout.addWidget(self.composer)

        splitter.addWidget(left)

        # Rechte Seite: Side-Panel
        self.side_panel = ChatSidePanel(
            settings=self.settings,
            orchestrator=self.orchestrator,
            theme=self.settings.theme,
            parent=self,
        )
        self.side_panel.settings_changed.connect(self._on_settings_changed)
        self.side_panel.prompt_apply_requested.connect(self._on_prompt_apply)
        self.side_panel.prompt_as_system_requested.connect(self._on_prompt_as_system)
        self.side_panel.prompt_to_composer_requested.connect(self._on_prompt_to_composer)
        splitter.addWidget(self.side_panel)

        layout.addWidget(splitter)

        self.update_chat_signal.connect(self._on_update_chat_slot)

        # Header-Checkboxen mit Settings synchronisieren
        self.header.rag_check.stateChanged.connect(self._on_rag_toggled)
        self.header.self_improving_check.stateChanged.connect(self._on_self_improving_toggled)

    def _on_rag_toggled(self, state):
        """RAG-Toggle aus Header in Settings übernehmen."""
        if hasattr(self.settings, "rag_enabled"):
            self.settings.rag_enabled = state == Qt.Checked
            self.settings.save()

    def _on_self_improving_toggled(self, state):
        """Self-Improving-Toggle aus Header in Settings übernehmen."""
        if hasattr(self.settings, "self_improving_enabled"):
            self.settings.self_improving_enabled = state == Qt.Checked
            self.settings.save()

    def _on_role_change(self, role: ModelRole):
        """Rolle im Header-Combo setzen."""
        if self.header and self.header.role_combo:
            idx = self.header.role_combo.findData(role)
            if idx >= 0:
                self.header.role_combo.setCurrentIndex(idx)

    async def _run_research_agent(self, user_text: str):
        """Führt den Research Agent aus (Planner → RAG → LLM → Critic)."""
        self._streaming = True
        self.current_full_response = ""
        self._streaming_message_widget = self.add_message("assistant", "Research läuft…", save_to_db=False)

        try:
            async def rag_ctx(q: str, top_k: int = 5):
                return await self.rag_service.get_context(
                    q, space=getattr(self.settings, "rag_space", "default"), top_k=top_k
                )

            agent = create_research_agent(
                self.orchestrator.chat,
                rag_ctx,
                planner_model="qwen2.5:latest",
                research_model="gpt-oss:latest",
                critic_model="mistral:latest",
            )
            response = await agent.run(user_text, rag_top_k=getattr(self.settings, "rag_top_k", 5))
            self.current_full_response = response or "(Keine Antwort)"
            self.update_chat_signal.emit(self.current_full_response, True)
            self.db.save_message(self.chat_id, "assistant", self.current_full_response)
            await self._maybe_self_improve(self.current_full_response)
        except Exception as e:
            err = f"Research Fehler: {e}"
            self.current_full_response = err
            self.update_chat_signal.emit(err, True)
            self.db.save_message(self.chat_id, "assistant", err)
        finally:
            self._streaming = False
            if self._streaming_message_widget:
                self._streaming_message_widget.bubble.setText(self.current_full_response)
                self._streaming_message_widget = None

    async def _run_delegation_flow(self, user_text: str):
        """Führt die Agenten-Orchestrierung aus: Planner → Task Graph → Delegation → Execution."""
        self._streaming = True
        self.current_full_response = ""
        self._streaming_message_widget = self.add_message(
            "assistant", "Delegation: Planung läuft…", save_to_db=False
        )

        try:
            orch = create_orchestration_service(self.orchestrator.chat)
            graph = await orch.plan(user_text)

            async def run_fn(agent_id: str, prompt: str, context: Dict[str, Any]) -> str:
                registry = get_agent_registry()
                profile = registry.get(agent_id) or registry.get_by_slug(agent_id)
                if not profile:
                    return f"Fehler: Agent {agent_id} nicht gefunden"
                model = profile.assigned_model or getattr(self.settings, "model", "qwen2.5:latest")
                messages = []
                if profile.system_prompt:
                    messages.append({"role": "system", "content": profile.system_prompt})
                messages.append({"role": "user", "content": prompt})
                return await complete(
                    self.orchestrator.chat,
                    model,
                    messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )

            def on_progress(task, status: str):
                if self._streaming_message_widget:
                    label = f"{task.description[:40]}…" if len(task.description) > 40 else task.description
                    self._streaming_message_widget.bubble.setText(f"[{status}] {label}")

            result = await orch.run(graph, run_fn=run_fn, on_task_progress=on_progress)
            self.current_full_response = result or "(Keine Antwort)"
            self.update_chat_signal.emit(self.current_full_response, True)
            self.db.save_message(self.chat_id, "assistant", self.current_full_response)
            await self._maybe_self_improve(self.current_full_response)
        except Exception as e:
            err = f"Delegation Fehler: {e}"
            self.current_full_response = err
            self.update_chat_signal.emit(err, True)
            self.db.save_message(self.chat_id, "assistant", err)
        finally:
            self._streaming = False
            if self._streaming_message_widget:
                self._streaming_message_widget.bubble.setText(self.current_full_response)
                self._streaming_message_widget = None

    async def _maybe_self_improve(self, answer: str):
        """Self-Improving: extrahiert Wissen aus Antwort und speichert (wenn aktiviert)."""
        if not getattr(self.settings, "self_improving_enabled", False) or not self.rag_service:
            return
        chat_fn = self.orchestrator.chat if self.orchestrator else self.client.chat

        async def llm_complete(model_id, messages):
            return await complete(chat_fn, model_id, messages)

        updater = self.rag_service.get_knowledge_updater(llm_complete, self_improving_enabled=True)
        if updater:
            try:
                source = f"chat_{self.chat_id}" if self.chat_id else "llm_answer"
                await updater.process_llm_answer(answer, source=source)
            except Exception:
                pass

    def _on_settings_changed(self):
        self._apply_routing_settings()
        self.set_current_model(self.settings.model)
        self.temperature = self.settings.temperature
        self.max_tokens = self.settings.max_tokens

    def _on_prompt_apply(self, prompt):
        if prompt and prompt.content:
            self.add_message("system", prompt.content)

    def _on_prompt_as_system(self, prompt):
        if prompt and prompt.content:
            self.add_message("system", prompt.content)

    def _on_prompt_to_composer(self, prompt):
        if prompt and prompt.content:
            self.composer.append_text(prompt.content)

    def _on_update_chat_slot(self, text: str, is_final: bool):
        """Qt-Slot für update_chat_signal; ruft on_update_chat auf."""
        self.on_update_chat(text, is_final)

    def on_update_chat(self, text: str, is_final: bool):
        """
        Wird bei jedem Stream-Update aufgerufen.
        Überschreibbar von Subklassen (z.B. CapturingChatWidget für Tests).
        Standard: aktualisiert die letzte Assistant-Nachricht oder fügt eine hinzu.
        Defensiv: RuntimeError bei zerstörtem Widget (spätes Signal) wird abgefangen.
        """
        try:
            if is_final and self._streaming_message_widget:
                self._streaming_message_widget.bubble.setText(text)
                self._streaming_message_widget = None
            elif not self._streaming_message_widget and self.conversation_view.message_layout.count() > 0:
                last = self.conversation_view.message_layout.itemAt(
                    self.conversation_view.message_layout.count() - 1
                )
                if last and last.widget():
                    w = last.widget()
                    if getattr(w, "role", None) == "assistant":
                        w.bubble.setText(text)
                        if is_final:
                            self._streaming_message_widget = None
        except RuntimeError:
            # Widget bereits zerstört (spätes Signal nach deleteLater)
            pass

    def _safe_emit_update(self, text: str, is_final: bool) -> None:
        """Emittiert update_chat_signal; ignoriert RuntimeError wenn Widget zerstört."""
        try:
            self.update_chat_signal.emit(text, is_final)
        except RuntimeError:
            pass

    def add_message(
        self,
        role: str,
        content: str,
        timestamp=None,
        avatar_path=None,
        save_to_db: bool = True,
    ):
        """Fügt eine Nachricht zur Conversation hinzu und speichert sie optional in der DB."""
        if save_to_db and self.chat_id and role in ("user", "assistant", "system"):
            self.db.save_message(self.chat_id, role, content)
        return self.conversation_view.add_message(role, content, timestamp, avatar_path)

    def clear_chat(self):
        """Löscht die Anzeige und setzt chat_id zurück."""
        self.conversation_view.clear()
        self.chat_id = None
        self.current_full_response = ""

    def load_history(self):
        """Lädt die Chat-Historie aus der DB und zeigt sie an."""
        self.conversation_view.clear()
        if not self.chat_id:
            return
        rows = self.db.load_chat(self.chat_id)
        for row in rows:
            role, content, timestamp = row[0], row[1], row[2]
            c = content if content is not None else ""
            self.conversation_view.add_message(role, c, timestamp)

    def load_models(self):
        """Lädt verfügbare Modelle und befüllt die Combos."""
        async def _load():
            if self.orchestrator:
                await self.orchestrator.refresh_available_models()
            try:
                from app.services.unified_model_catalog_service import get_unified_model_catalog_service

                u = get_unified_model_catalog_service()
                cat = await u.build_catalog_for_chat(self.settings)
                model_names = [e["selection_id"] for e in cat if e.get("chat_selectable")]
                if self.side_panel:
                    self.side_panel.set_model_list(u.build_role_panel_entries(cat))
            except Exception:
                model_names = []
                models = []
                if self.orchestrator:
                    reg = self.orchestrator._registry
                    for e in reg._models.values():
                        if e.enabled:
                            models.append(
                                {
                                    "name": e.id,
                                    "model": e.id,
                                    "id": e.id,
                                    "display": getattr(e, "display_name", e.id),
                                    "cloud": getattr(e, "source_type", "local") == "cloud",
                                }
                            )
                else:
                    try:
                        raw = await self.client.get_models()
                        for m in raw:
                            name = m.get("name") or m.get("model", "")
                            if name:
                                models.append(
                                    {
                                        "name": name,
                                        "model": name,
                                        "id": name,
                                        "display": name,
                                        "cloud": False,
                                    }
                                )
                    except Exception:
                        pass
                model_names = [
                    m.get("name") or m.get("model", "") for m in models if m.get("name") or m.get("model")
                ]
                if self.side_panel:
                    self.side_panel.set_model_list(models)
            self.header.model_combo.clear()
            self.header.model_combo.addItems(model_names)
            self.set_current_model(self._current_model)
            self._load_agents()

        asyncio.create_task(_load())

    def _load_agents(self):
        """Befüllt die Agent-Combo mit aktiven Agenten."""
        try:
            from app.agents.seed_agents import ensure_seed_agents
            ensure_seed_agents()
            registry = get_agent_registry()
            registry.refresh()
            agents = registry.list_active()
            self.header.agent_combo.clear()
            self.header.agent_combo.addItem("Standard (kein Agent)", None)
            for a in agents:
                self.header.agent_combo.addItem(a.effective_display_name, a.id)
        except Exception:
            self.header.agent_combo.clear()
            self.header.agent_combo.addItem("Standard (kein Agent)", None)

    def set_current_model(self, model_id: str):
        """Setzt das aktuelle Modell in der UI."""
        self._current_model = model_id or self.settings.model
        idx = self.header.model_combo.findText(self._current_model)
        if idx >= 0:
            self.header.model_combo.setCurrentIndex(idx)
        else:
            self.header.model_combo.setCurrentText(self._current_model)

    def _apply_routing_settings(self):
        """Überträgt Routing-Settings in die Header-Controls."""
        self.header.auto_routing_check.setChecked(
            getattr(self.settings, "auto_routing", True)
        )
        self.header.cloud_check.setChecked(
            getattr(self.settings, "cloud_escalation", False)
        )
        self.header.overkill_btn.setChecked(
            getattr(self.settings, "overkill_mode", False)
        )
        self.header.web_search_check.setChecked(
            getattr(self.settings, "web_search", False)
        )
        self.header.rag_check.setChecked(
            getattr(self.settings, "rag_enabled", False)
        )
        self.header.self_improving_check.setChecked(
            getattr(self.settings, "self_improving_enabled", False)
        )
        idx = self.header.think_mode_combo.findText(
            getattr(self.settings, "think_mode", "auto")
        )
        if idx >= 0:
            self.header.think_mode_combo.setCurrentIndex(idx)

    def refresh_theme(self):
        """Aktualisiert Theme für alle Child-Widgets."""
        theme = getattr(self.settings, "theme", "dark")
        self.conversation_view.set_theme(theme)
        self.header.refresh_theme(theme)
        if self.side_panel:
            self.side_panel.refresh_theme(theme)

    def refresh_prompt_backend(self):
        """Aktualisiert das Prompt-Backend nach Einstellungsänderung."""
        if self.side_panel and hasattr(self.side_panel, "prompt_panel"):
            svc = getattr(self.side_panel.prompt_panel, "service", None)
            if svc and hasattr(svc, "refresh_backend"):
                svc.refresh_backend(
                    storage_type=getattr(self.settings, "prompt_storage_type", "database"),
                    db_path="chat_history.db",
                    directory=getattr(self.settings, "prompt_directory", ""),
                )

    def set_icons(self):
        """Aktualisiert Icons (z.B. Senden-Button)."""
        self.composer.icons_path = getattr(self.settings, "icons_path", DEFAULT_LEGACY_ICONS_PATH_STR)
        self.composer.set_icons()

    def _get_active_agent(self) -> Optional[AgentProfile]:
        """Liefert den aktuell ausgewählten Agenten, falls einer gewählt ist."""
        if not self.header or not self.header.agent_combo:
            return None
        agent_id = self.header.agent_combo.currentData()
        if not agent_id:
            return None
        registry = get_agent_registry()
        return registry.get(agent_id)

    def _build_messages_for_api(self, user_text: str) -> List[Dict[str, str]]:
        """Baut die Nachrichtenliste für die API aus Historie + neuer User-Nachricht."""
        messages: List[Dict[str, str]] = []
        agent = self._get_active_agent()
        if agent and agent.system_prompt:
            messages.append({"role": "system", "content": agent.system_prompt})
        if self.chat_id:
            rows = self.db.load_chat(self.chat_id)
            for row in rows:
                role, content = row[0], row[1]
                c = (content or "").strip() if content is not None else ""
                if role == "assistant" and is_placeholder_or_invalid_assistant_message(c):
                    continue
                if not c and role == "assistant":
                    continue
                messages.append({"role": role, "content": c})
        messages.append({"role": "user", "content": user_text})
        return messages

    def _create_pipeline(self) -> OutputPipeline:
        """Erstellt die Output-Pipeline aus den Settings."""
        return OutputPipeline(
            strip_html=getattr(self.settings, "strip_html", True),
            preserve_markdown=getattr(self.settings, "preserve_markdown", True),
            retry_without_thinking=getattr(self.settings, "retry_without_thinking", True),
            max_retries=getattr(self.settings, "max_retries", 1),
        )

    def _get_think_param(self, force_think: Optional[bool] = None) -> Any:
        if force_think is not None:
            return force_think
        mode = getattr(self.settings, "think_mode", "auto")
        if mode == "off":
            return False
        if mode in ("low", "medium", "high"):
            return mode
        return None

    def _resolve_model_and_role_for_prompt(self, user_text: str) -> tuple[str, ModelRole]:
        """Ermittelt Modell und Rolle für den Prompt."""
        force_role = None
        force_model = None
        agent = self._get_active_agent()
        if agent:
            if agent.assigned_model_role:
                try:
                    force_role = ModelRole(agent.assigned_model_role)
                except ValueError:
                    pass
            if agent.assigned_model:
                force_model = agent.assigned_model
        if not force_role and self.header and self.header.role_combo.currentData() is not None:
            force_role = self.header.role_combo.currentData()
        if not force_model:
            force_model = getattr(self.settings, "model", None)
        if self.orchestrator:
            role, model_id = self.orchestrator.select_model_for_prompt(
                user_text,
                force_role=force_role,
                force_model=force_model,
                auto_routing=getattr(self.settings, "auto_routing", True) if not agent else False,
                cloud_enabled=getattr(self.settings, "cloud_escalation", False),
                cloud_via_local=getattr(self.settings, "cloud_via_local", False),
                overkill_mode=getattr(self.settings, "overkill_mode", False),
            )
            if model_id:
                return model_id, role
        return self._current_model or self.settings.model, force_role or ModelRole.DEFAULT

    @asyncSlot()
    async def _on_send(self):
        text = self.composer.get_text()
        if not text.strip():
            return
        result = parse_slash_command(
            text,
            on_role_change=self._on_role_change,
            on_auto_routing_change=lambda v: setattr(self.settings, "auto_routing", v),
            on_cloud_change=lambda v: setattr(self.settings, "cloud_escalation", v),
            on_overkill_change=lambda v: setattr(self.settings, "overkill_mode", v),
        )
        if result.consumed and not result.remaining_text:
            if result.message:
                self.add_message("system", result.message)
            if result.role is not None:
                self._on_role_change(result.role)
            self.composer.clear_input()
            return
        if result.role is not None:
            self._on_role_change(result.role)
        user_text = result.remaining_text or text
        self.composer.clear_input()

        if result.use_delegation and user_text and self.orchestrator:
            await self._run_delegation_flow(user_text)
        else:
            await self.run_chat(user_text)

    async def run_chat(self, user_text: str, retry_count: int = 0, force_think: Optional[bool] = None):
        """Führt einen Chat-Lauf durch: Nachricht speichern, streamen, anzeigen."""
        if self._streaming:
            return
        if not self.chat_id:
            self.chat_id = self.db.create_chat("Neuer Chat")

        if self.tools is None:
            roots = self.db.list_workspace_roots_for_chat(self.chat_id)
            paths = [p for p, _ in roots] if roots else []
            self.tools = FileSystemTools(paths) if paths else None

        if retry_count == 0:
            self.db.save_message(self.chat_id, "user", user_text)
            self.add_message("user", user_text)

        model_id, role = self._resolve_model_and_role_for_prompt(user_text)

        # Research Agent: eigener Pfad (kein Streaming)
        if role == ModelRole.RESEARCH and self.orchestrator and self.rag_service:
            await self._run_research_agent(user_text)
            return

        # RAG: Query mit Kontext erweitern, falls aktiviert
        text_for_llm = user_text
        if self.rag_service and getattr(self.settings, "rag_enabled", False):
            text_for_llm, _ = await self.rag_service.augment_if_enabled(
                user_text,
                enabled=True,
                space=getattr(self.settings, "rag_space", "default"),
                top_k=getattr(self.settings, "rag_top_k", 5),
            )
        messages = self._build_messages_for_api(text_for_llm)

        self._streaming = True
        self.current_full_response = ""
        self._streaming_content_buffer = ""
        self._streaming_thinking_chunks = []

        if retry_count == 0:
            self._streaming_message_widget = self.add_message(
                "assistant", "...", save_to_db=False
            )
        else:
            last = self.conversation_view.message_layout.itemAt(
                self.conversation_view.message_layout.count() - 1
            )
            self._streaming_message_widget = last.widget() if last and last.widget() else None
            if self._streaming_message_widget:
                self._streaming_message_widget.bubble.setText("...")

        think_param = self._get_think_param(force_think)
        stream_enabled = getattr(self.settings, "chat_streaming_enabled", True)
        chat_source = self.orchestrator if self.orchestrator else self.client
        if self.orchestrator:
            kwargs = dict(
                model_id=model_id,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=stream_enabled,
                think=think_param,
                cloud_via_local=getattr(self.settings, "cloud_via_local", False),
            )
        else:
            kwargs = dict(
                model=model_id,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=stream_enabled,
                think=think_param,
            )

        try:
            stream_start = time.perf_counter()
            stream = chat_source.chat(**kwargs)
            if asyncio.iscoroutine(stream):
                stream = await stream
            had_error = False
            async for chunk in stream:
                content, thinking, error = _extract_chunk_parts(chunk)
                if error:
                    self.current_full_response = f"Ollama Fehler: {error}"
                    self._safe_emit_update(self.current_full_response, True)
                    self.db.save_message(self.chat_id, "assistant", self.current_full_response)
                    had_error = True
                    break
                if thinking:
                    self._streaming_thinking_chunks.append(thinking)
                if content:
                    self._streaming_content_buffer += content
                    self._safe_emit_update(self._streaming_content_buffer, chunk.get("done", False))

            if not had_error:
                try:
                    agent = self._get_active_agent()
                except RuntimeError:
                    agent = None
                meta = {
                    "model_id": model_id,
                    "duration_sec": time.perf_counter() - stream_start,
                }
                if agent and agent.id:
                    meta["agent_id"] = agent.id
                emit_event(
                    EventType.MODEL_CALL,
                    agent_name=(agent.effective_display_name if agent else "Chat"),
                    message=model_id,
                    metadata=meta,
                )
                done = True
                pipeline_result = self._pipeline.process(
                    raw_content=self._streaming_content_buffer,
                    thinking_chunks=self._streaming_thinking_chunks,
                    done=done,
                    retry_count=retry_count,
                    retry_used=retry_count > 0,
                    fallback_used=False,
                )

                if pipeline_result.should_retry_without_thinking:
                    self._streaming = False
                    self._streaming_message_widget = None
                    await self.run_chat(user_text, retry_count=retry_count + 1, force_think=False)
                    return

                self.current_full_response = pipeline_result.display_text()

                if not is_placeholder_or_invalid_assistant_message(self.current_full_response):
                    self.db.save_message(self.chat_id, "assistant", self.current_full_response)
                    await self._maybe_self_improve(self.current_full_response)

                self.current_full_response = self.handle_tool_calls(self.current_full_response)
                self._safe_emit_update(self.current_full_response, True)

        except Exception as e:
            try:
                agent = self._get_active_agent()
            except RuntimeError:
                agent = None
            meta = {
                "model_id": model_id,
                "duration_sec": time.perf_counter() - stream_start,
                "error": str(e),
            }
            if agent and agent.id:
                meta["agent_id"] = agent.id
            emit_event(
                EventType.MODEL_CALL,
                agent_name=agent.effective_display_name if agent else "Chat",
                message=model_id,
                metadata=meta,
            )
            err_text = f"Fehler: {e}"
            self.current_full_response = err_text
            self._safe_emit_update(err_text, True)
            self.db.save_message(self.chat_id, "assistant", err_text)
        finally:
            self._streaming = False
            try:
                if self._streaming_message_widget:
                    self._streaming_message_widget.bubble.setText(self.current_full_response)
                    self._streaming_message_widget = None
            except RuntimeError:
                self._streaming_message_widget = None

    def handle_tool_calls(self, text: str) -> str:
        """
        Parst <tool_call name="..."/> im Text, führt Tools aus und ersetzt die Tags.
        """
        if not self.tools:
            return text
        tool_calls = _parse_tool_calls(text)
        if not tool_calls:
            return text
        result_parts = []
        last_end = 0
        for name, full_match in tool_calls:
            start = text.find(full_match, last_end)
            if start < 0:
                continue
            result_parts.append(text[last_end:start])
            try:
                emit_event(
                    EventType.TOOL_EXECUTION,
                    agent_name="Chat",
                    message=name,
                    metadata={"tool_name": name, "status": "started"},
                )
                if name == "list_dir":
                    out = self.tools.list_dir(".")
                elif name == "read_file":
                    out = "(read_file erfordert Parameter)"
                elif name == "write_file":
                    out = "(write_file erfordert Parameter)"
                elif name == "execute_command":
                    out = "(execute_command erfordert Bestätigung)"
                else:
                    out = f"(Unbekanntes Tool: {name})"
                emit_event(
                    EventType.TOOL_EXECUTION,
                    agent_name="Chat",
                    message=name,
                    metadata={"tool_name": name, "status": "completed"},
                )
            except Exception as e:
                emit_event(
                    EventType.TOOL_EXECUTION,
                    agent_name="Chat",
                    message=name,
                    metadata={"tool_name": name, "status": "failed", "error": str(e)},
                )
                out = f"Fehler: {e}"
            result_parts.append(f"\n[Tool {name}]: {out}\n")
            last_end = start + len(full_match)
        result_parts.append(text[last_end:])
        return "".join(result_parts)
