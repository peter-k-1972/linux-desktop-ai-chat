"""
Testdiagnostik – Dump-Helpers für Debugging bei Testfehlern.

Nutzen: Bei assert-Fehlern in Tests diese Helper aufrufen (oder in
pytest_assertrepr_compare integrieren), um Kontext zu erhalten.

Beispiel:
    def test_xyz(chat_widget):
        result = ...
        if not result:
            print(dump_chat_state(chat_widget))
        assert result
"""

from typing import Any, Optional


def dump_chat_state(widget) -> str:
    """
    Gibt den aktuellen Chat-State eines ChatWidgets als lesbaren String aus.

    Enthält: chat_id, Nachrichtenanzahl, letzte Nachricht, streaming-Status.
    """
    if widget is None:
        return "dump_chat_state: widget is None"
    lines = ["=== Chat State ==="]
    lines.append(f"chat_id: {getattr(widget, 'chat_id', 'N/A')}")
    lines.append(f"_streaming: {getattr(widget, '_streaming', 'N/A')}")
    lines.append(f"current_full_response: {getattr(widget, 'current_full_response', '')[:200]}...")
    if hasattr(widget, "conversation_view") and widget.conversation_view:
        count = widget.conversation_view.message_layout.count()
        lines.append(f"message_layout.count(): {count}")
        if count > 0:
            last = widget.conversation_view.message_layout.itemAt(count - 1)
            if last and last.widget():
                bubble = getattr(last.widget(), "bubble", None)
                if bubble:
                    lines.append(f"last_message: {bubble.text()[:150]}...")
    return "\n".join(lines)


def dump_debug_store(store) -> str:
    """
    Gibt den Inhalt des DebugStore als lesbaren String aus.
    """
    if store is None:
        return "dump_debug_store: store is None"
    lines = ["=== Debug Store ==="]
    try:
        events = store.get_event_history()
        lines.append(f"event_history: {len(events)} events")
        for i, e in enumerate(events[:10]):
            msg = (e.message or "")[:50]
            lines.append(f"  [{i}] {e.event_type.value} | {e.agent_name} | {msg}")
        if hasattr(store, "active_tasks"):
            lines.append(f"active_tasks: {len(store.active_tasks)}")
        if hasattr(store, "model_usage"):
            lines.append(f"model_usage: {len(store.model_usage)} entries")
    except Exception as ex:
        lines.append(f"Error: {ex}")
    return "\n".join(lines)


def dump_recent_events(store, n: int = 5) -> str:
    """
    Gibt die letzten n Events aus dem DebugStore aus.
    """
    if store is None:
        return "dump_recent_events: store is None"
    lines = [f"=== Last {n} Events ==="]
    try:
        events = store.get_event_history()[:n]
        for i, e in enumerate(events):
            msg = (e.message or "")[:80]
            lines.append(f"  {i}: {e.timestamp} | {e.event_type.value} | {e.agent_name} | {msg}")
    except Exception as ex:
        lines.append(f"Error: {ex}")
    return "\n".join(lines)


def dump_agent_context(agent) -> str:
    """
    Gibt den Kontext eines AgentProfile aus.
    """
    if agent is None:
        return "dump_agent_context: agent is None"
    lines = ["=== Agent Context ==="]
    lines.append(f"id: {agent.id}")
    lines.append(f"name: {agent.name}")
    lines.append(f"display_name: {agent.display_name}")
    lines.append(f"system_prompt (first 100): {getattr(agent, 'system_prompt', '')[:100]}...")
    lines.append(f"status: {getattr(agent, 'status', 'N/A')}")
    return "\n".join(lines)


def dump_streaming_state(widget) -> str:
    """
    Gibt den Streaming-Status eines ChatWidgets aus.

    Nützlich bei Async-Tests (z.B. test_shutdown_during_task) wenn
    _streaming nach Abbruch noch True ist.
    """
    if widget is None:
        return "dump_streaming_state: widget is None"
    lines = ["=== Streaming State ==="]
    lines.append(f"_streaming: {getattr(widget, '_streaming', 'N/A')}")
    lines.append(f"_streaming_message_widget: {getattr(widget, '_streaming_message_widget', 'N/A')}")
    lines.append(f"current_full_response (first 100): {str(getattr(widget, 'current_full_response', ''))[:100]}...")
    return "\n".join(lines)


def dump_chunk_state(chunk: Any) -> str:
    """
    Gibt die Struktur eines LLM-Stream-Chunks aus.
    Nützlich bei test_llm_chunk_parsing_failure.
    """
    if chunk is None:
        return "dump_chunk_state: chunk is None"
    lines = ["=== Chunk State ==="]
    lines.append(f"type: {type(chunk).__name__}")
    if isinstance(chunk, dict):
        for k, v in list(chunk.items())[:10]:
            lines.append(f"  {k}: {type(v).__name__}={repr(v)[:80]}")
    return "\n".join(lines)


def dump_rag_state(service) -> str:
    """
    Gibt den RAG-Service-Status aus.
    Nützlich bei Chroma/RAG-Failure-Tests.
    """
    if service is None:
        return "dump_rag_state: service is None"
    lines = ["=== RAG State ==="]
    lines.append(f"_manager: {getattr(service, '_manager', 'N/A')}")
    lines.append(f"_pipeline: {getattr(service, '_pipeline', 'N/A')}")
    return "\n".join(lines)


def dump_prompt_context(prompt) -> str:
    """
    Gibt den Kontext eines Prompt-Objekts aus.
    """
    if prompt is None:
        return "dump_prompt_context: prompt is None"
    lines = ["=== Prompt Context ==="]
    lines.append(f"id: {prompt.id}")
    lines.append(f"title: {prompt.title}")
    lines.append(f"category: {prompt.category}")
    lines.append(f"content (first 100): {getattr(prompt, 'content', '')[:100]}...")
    return "\n".join(lines)


def dump_prompt_request_state(widget, messages: Optional[list] = None) -> str:
    """
    Dump für Cross-Layer Prompt Truth: UI-State vs. Request-Messages.

    Nützlich wenn UI sagt "Prompt angewendet", aber Request andere/stale Daten hat.
    """
    lines = ["=== Prompt Request State ==="]
    if widget:
        lines.append(f"chat_id: {getattr(widget, 'chat_id', 'N/A')}")
        cv = getattr(widget, 'conversation_view', None)
        if cv and hasattr(cv, 'message_layout'):
            count = cv.message_layout.count()
            lines.append(f"conversation_view messages: {count}")
            for i in range(min(count, 5)):
                item = cv.message_layout.itemAt(i)
                if item and item.widget():
                    w = item.widget()
                    role = getattr(w, 'role', '?')
                    bubble = getattr(w, 'bubble', None)
                    text = (bubble.text() if bubble else '')[:60]
                    lines.append(f"  [{i}] role={role} text={text}...")
    if messages is not None:
        lines.append(f"request messages: {len(messages)}")
        for i, m in enumerate(messages[:5]):
            role = m.get('role', '?')
            content = (m.get('content', '') or '')[:80]
            lines.append(f"  [{i}] role={role} content={content}...")
    return "\n".join(lines)


def dump_debug_failure_state(store, events: Optional[list] = None) -> str:
    """
    Dump für Debug Truth: Store vs. View/Timeline.

    Nützlich wenn Failure-Events im Store sind, aber nicht in der View erscheinen.
    """
    lines = ["=== Debug Failure State ==="]
    if store:
        try:
            history = store.get_event_history()
            lines.append(f"store event_history: {len(history)} events")
            for i, e in enumerate(history[-5:]):
                msg = (getattr(e, 'message', '') or '')[:60]
                et = getattr(e, 'event_type', e)
                if hasattr(et, 'value'):
                    et = et.value
                lines.append(f"  [{i}] {et} | {msg}...")
        except Exception as ex:
            lines.append(f"store error: {ex}")
    if events is not None:
        lines.append(f"view/timeline events: {len(events)}")
        for i, e in enumerate(events[-5:]):
            lines.append(f"  [{i}] {e}")
    return "\n".join(lines)


def dump_startup_mode_state(app_or_main_window) -> str:
    """
    Dump für Startup in Degraded Mode: App-Status bei fehlenden optionalen Deps.
    """
    lines = ["=== Startup Mode State ==="]
    if app_or_main_window is None:
        return "dump_startup_mode_state: app/main_window is None"
    lines.append(f"type: {type(app_or_main_window).__name__}")
    lines.append(f"visible: {getattr(app_or_main_window, 'isVisible', lambda: 'N/A')()}")
    if hasattr(app_or_main_window, 'centralWidget'):
        cw = app_or_main_window.centralWidget()
        lines.append(f"centralWidget: {type(cw).__name__ if cw else 'None'}")
    return "\n".join(lines)


def dump_metrics_state(store_or_service, failed: Optional[bool] = None, agent_id: str = "unknown") -> str:
    """
    Dump für Metrics unter Failure: completed vs. failed, Konsistenz.
    """
    lines = ["=== Metrics State ==="]
    if store_or_service is None:
        return "dump_metrics_state: store/service is None"
    try:
        from app.metrics.agent_metrics import TimeRange
        if hasattr(store_or_service, 'get_aggregated_metrics'):
            agg = store_or_service.get_aggregated_metrics(agent_id, TimeRange.ALL)
            lines.append(f"aggregated_metrics: {len(agg)} buckets")
            for m in agg[:3]:
                lines.append(f"  completed={m.tasks_completed} failed={m.tasks_failed}")
        if hasattr(store_or_service, 'get_agent_statistics'):
            stats = store_or_service.get_agent_statistics(agent_id, TimeRange.ALL)
            lines.append(f"stats: completed={stats.tasks_completed} failed={stats.tasks_failed}")
        if hasattr(store_or_service, 'get_events'):
            ev = store_or_service.get_events(agent_id, TimeRange.ALL)
            lines.append(f"events: {len(ev)}")
            for e in ev[-3:]:
                lines.append(f"  {e.event_type.value}")
    except Exception as ex:
        lines.append(f"error: {ex}")
    if failed is not None:
        lines.append(f"expected failed state: {failed}")
    return "\n".join(lines)
