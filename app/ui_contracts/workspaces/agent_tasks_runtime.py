"""
Agent Tasks — schmaler Runtime-Start (Batch 6).

Nur Start-Task-Ergebnis, kein vollständiges Laufzeitmodell.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StartAgentTaskCommand:
    agent_id: str
    prompt: str


@dataclass(frozen=True, slots=True)
class StartAgentTaskResultDto:
    task_id: str
    agent_id: str
    agent_name: str
    prompt: str
    response: str
    model: str
    success: bool
    error: str | None = None
    duration_sec: float = 0.0
