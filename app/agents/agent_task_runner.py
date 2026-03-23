"""
AgentTaskRunner – Service-Schicht für Agent-Task-Ausführung.

Führt Agent → Prompt → Modell → Antwort aus.
Emittiert Events an den EventBus für DebugStore und GUI.
Keine GUI-Logik.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.agents.agent_profile import AgentProfile
from app.agents.agent_service import get_agent_service
from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import get_event_bus

logger = logging.getLogger(__name__)


@dataclass
class AgentTaskResult:
    """Ergebnis eines Agent-Tasks."""

    task_id: str
    agent_id: str
    agent_name: str
    prompt: str
    response: str
    model: str
    success: bool
    error: Optional[str] = None
    duration_sec: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentTaskRunner:
    """
    Führt Agent-Tasks aus: Agent → Prompt → Modell → Antwort.
    Emittiert Events für DebugStore/AgentActivity.
    """

    def __init__(self):
        self._event_bus = get_event_bus()

    def _emit(self, event: AgentEvent) -> None:
        """Sendet Event an EventBus."""
        self._event_bus.emit(event)

    async def start_agent_task(
        self,
        agent_id: str,
        prompt: str,
        model_override: Optional[str] = None,
    ) -> AgentTaskResult:
        """
        Startet einen Agent-Task: lädt Agent, ruft Modell auf, liefert Ergebnis.
        Emittiert TASK_CREATED, TASK_STARTED, MODEL_CALL, TASK_COMPLETED/TASK_FAILED.
        """
        task_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)

        # Agent laden
        service = get_agent_service()
        agent = service.get(agent_id)
        if not agent:
            err = f"Agent nicht gefunden: {agent_id}"
            self._emit(
                AgentEvent(
                    task_id=task_id,
                    agent_name="",
                    event_type=EventType.TASK_FAILED,
                    message=err,
                    metadata={"agent_id": agent_id, "error": err},
                )
            )
            return AgentTaskResult(
                task_id=task_id,
                agent_id=agent_id,
                agent_name="",
                prompt=prompt,
                response="",
                model="",
                success=False,
                error=err,
            )

        agent_name = agent.effective_display_name

        # TASK_CREATED
        self._emit(
            AgentEvent(
                task_id=task_id,
                agent_name=agent_name,
                event_type=EventType.TASK_CREATED,
                message=prompt[:100] + ("…" if len(prompt) > 100 else ""),
                metadata={"agent_id": agent_id, "description": prompt[:200]},
            )
        )

        # TASK_STARTED
        self._emit(
            AgentEvent(
                task_id=task_id,
                agent_name=agent_name,
                event_type=EventType.TASK_STARTED,
                message="Task gestartet",
                metadata={"agent_id": agent_id},
            )
        )

        # Modell ermitteln
        model = model_override or agent.assigned_model
        if not model:
            try:
                from app.services.model_service import get_model_service
                result = await get_model_service().get_models()
                model = result.data[0] if result.success and result.data else None
            except Exception:
                model = None

        if not model:
            err = "Kein Modell verfügbar – ist Ollama gestartet?"
            self._emit(
                AgentEvent(
                    task_id=task_id,
                    agent_name=agent_name,
                    event_type=EventType.TASK_FAILED,
                    message=err,
                    metadata={"agent_id": agent_id, "error": err},
                )
            )
            return AgentTaskResult(
                task_id=task_id,
                agent_id=agent_id,
                agent_name=agent_name,
                prompt=prompt,
                response="",
                model="",
                success=False,
                error=err,
            )

        # Messages bauen
        messages: List[Dict[str, str]] = []
        if agent.system_prompt:
            messages.append({"role": "system", "content": agent.system_prompt})
        messages.append({"role": "user", "content": prompt})

        full_response = ""
        error_msg: Optional[str] = None

        try:
            from app.services.chat_service import get_chat_service
            chat_svc = get_chat_service()

            from app.persistence.enums import UsageType

            async for chunk in chat_svc.chat(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
                stream=True,
                usage_type=UsageType.AGENT_RUN.value,
            ):
                if chunk and isinstance(chunk, dict):
                    if "error" in chunk:
                        error_msg = chunk.get("error", "Unbekannter Fehler")
                        break
                    msg = chunk.get("message") or {}
                    content = msg.get("content") or ""
                    if content:
                        full_response += content

            duration = (datetime.now(timezone.utc) - start_time).total_seconds()

            if error_msg:
                self._emit(
                    AgentEvent(
                        task_id=task_id,
                        agent_name=agent_name,
                        event_type=EventType.TASK_FAILED,
                        message=error_msg,
                        metadata={"agent_id": agent_id, "error": error_msg, "model": model},
                    )
                )
                return AgentTaskResult(
                    task_id=task_id,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    prompt=prompt,
                    response="",
                    model=model,
                    success=False,
                    error=error_msg,
                    duration_sec=duration,
                )

            # MODEL_CALL (nach Abschluss)
            self._emit(
                AgentEvent(
                    task_id=task_id,
                    agent_name=agent_name,
                    event_type=EventType.MODEL_CALL,
                    message=f"Modellaufruf: {model}",
                    metadata={
                        "model_id": model,
                        "duration_sec": duration,
                        "agent_id": agent_id,
                    },
                )
            )

            # TASK_COMPLETED
            self._emit(
                AgentEvent(
                    task_id=task_id,
                    agent_name=agent_name,
                    event_type=EventType.TASK_COMPLETED,
                    message="Task abgeschlossen",
                    metadata={"agent_id": agent_id, "model": model},
                )
            )

            return AgentTaskResult(
                task_id=task_id,
                agent_id=agent_id,
                agent_name=agent_name,
                prompt=prompt,
                response=full_response,
                model=model,
                success=True,
                duration_sec=duration,
                metadata={"model": model},
            )

        except asyncio.CancelledError:
            err = "Task abgebrochen"
            self._emit(
                AgentEvent(
                    task_id=task_id,
                    agent_name=agent_name,
                    event_type=EventType.TASK_FAILED,
                    message=err,
                    metadata={"agent_id": agent_id, "error": err},
                )
            )
            return AgentTaskResult(
                task_id=task_id,
                agent_id=agent_id,
                agent_name=agent_name,
                prompt=prompt,
                response="",
                model=model,
                success=False,
                error=err,
            )
        except Exception as e:
            err = str(e)
            logger.exception("Agent task failed: %s", e)
            self._emit(
                AgentEvent(
                    task_id=task_id,
                    agent_name=agent_name,
                    event_type=EventType.TASK_FAILED,
                    message=err,
                    metadata={"agent_id": agent_id, "error": err, "model": model},
                )
            )
            return AgentTaskResult(
                task_id=task_id,
                agent_id=agent_id,
                agent_name=agent_name,
                prompt=prompt,
                response="",
                model=model,
                success=False,
                error=err,
            )


_runner: Optional[AgentTaskRunner] = None


def get_agent_task_runner() -> AgentTaskRunner:
    """Liefert den globalen AgentTaskRunner."""
    global _runner
    if _runner is None:
        _runner = AgentTaskRunner()
    return _runner
