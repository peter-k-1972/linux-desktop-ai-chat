"""
LLM Complete – synchrone Vollantwort für Agenten und Knowledge-Extraktion.

Sammelt Stream-Chunks oder nutzt non-streaming API.
"""

import time
from typing import Any, Dict, List, Optional

try:
    from app.debug.emitter import emit_event
    from app.debug.agent_event import EventType
    _DEBUG_AVAILABLE = True
except ImportError:
    _DEBUG_AVAILABLE = False


async def complete(
    chat_fn,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 4096,
    think: Any = None,
) -> str:
    """
    Holt eine vollständige LLM-Antwort (nicht gestreamt).

    Args:
        chat_fn: Callable die chat(model_id=..., messages=..., stream=...) unterstützt.
                 Oder chat(model=..., ...). Muss AsyncGenerator yielden.
        model: Modell-ID
        messages: Chat-Nachrichten
        temperature: Temperatur
        max_tokens: Max Tokens
        think: Thinking-Parameter (optional)

    Returns:
        Vollständiger Antworttext
    """
    content_parts = []
    thinking_parts = []
    start_time = time.perf_counter()

    try:
        # Orchestrator nutzt model_id, Provider nutzt model
        stream = chat_fn(
            model_id=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            think=think,
        )
        if hasattr(stream, "__anext__"):
            async for chunk in stream:
                if "error" in chunk:
                    return f"Fehler: {chunk.get('error', 'Unbekannt')}"
                msg = chunk.get("message") or {}
                if msg.get("content"):
                    content_parts.append(msg["content"])
                if msg.get("thinking"):
                    thinking_parts.append(msg["thinking"])
            result = "".join(content_parts) or ("".join(thinking_parts) if thinking_parts else "")
            if _DEBUG_AVAILABLE:
                emit_event(
                    EventType.MODEL_CALL,
                    agent_name="",
                    message=model,
                    metadata={
                        "model_id": model,
                        "duration_sec": time.perf_counter() - start_time,
                    },
                )
            return result
    except TypeError:
        # Fallback: Provider mit model= statt model_id=
        stream = chat_fn(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            think=think,
        )
        if hasattr(stream, "__anext__"):
            async for chunk in stream:
                if "error" in chunk:
                    return f"Fehler: {chunk.get('error', 'Unbekannt')}"
                msg = chunk.get("message") or {}
                if msg.get("content"):
                    content_parts.append(msg["content"])
            result = "".join(content_parts)
            if _DEBUG_AVAILABLE:
                emit_event(
                    EventType.MODEL_CALL,
                    agent_name="",
                    message=model,
                    metadata={
                        "model_id": model,
                        "duration_sec": time.perf_counter() - start_time,
                    },
                )
            return result
    except Exception as e:
        if _DEBUG_AVAILABLE:
            emit_event(
                EventType.MODEL_CALL,
                agent_name="",
                message=model,
                metadata={
                    "model_id": model,
                    "duration_sec": time.perf_counter() - start_time,
                    "error": str(e),
                },
            )
        return f"Fehler: {e}"
