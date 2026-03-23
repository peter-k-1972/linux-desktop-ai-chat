"""
Synchroner Einstiegspunkt für Agent-Ausführung aus Workflows.

Kapselt asyncio + AgentTaskRunner; Tests können einen rein synchronen Stub setzen
(ohne Netzwerk/Modell).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# (agent_id, prompt, model_override) -> dict mit response_text, success, error, …
WorkflowAgentSyncFn = Callable[[str, str, Optional[str]], Dict[str, Any]]

_sync_override: Optional[WorkflowAgentSyncFn] = None


def set_workflow_agent_sync_override(fn: Optional[WorkflowAgentSyncFn]) -> None:
    """Nur für Tests: synchroner Stub statt echtem AgentTaskRunner."""
    global _sync_override
    _sync_override = fn


def run_workflow_agent(
    agent_id: str,
    prompt: str,
    model_override: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Führt einen Agent-Lauf aus und liefert ein JSON-taugliches Dict.

    Raises:
        RuntimeError: bei hartem Laufzeitfehler (Adapter).
    """
    if _sync_override is not None:
        return _sync_override(agent_id, prompt, model_override)

    from app.agents.agent_task_runner import get_agent_task_runner

    runner = get_agent_task_runner()

    async def _run() -> Dict[str, Any]:
        result = await runner.start_agent_task(agent_id, prompt, model_override)
        return {
            "response_text": result.response or "",
            "success": result.success,
            "error": result.error,
            "task_id": result.task_id,
            "metadata": {
                "model": result.model,
                "agent_name": result.agent_name,
                "duration_sec": result.duration_sec,
                **(result.metadata or {}),
            },
        }

    try:
        return asyncio.run(_run())
    except RuntimeError as e:
        if "asyncio.run()" in str(e) and "running event loop" in str(e).lower():
            logger.warning("Event loop aktiv – Workflow-Agent-Override empfohlen: %s", e)
        raise RuntimeError(
            "Agent-Ausführung aus Workflow erfordert asyncio.run oder set_workflow_agent_sync_override (Tests)."
        ) from e
