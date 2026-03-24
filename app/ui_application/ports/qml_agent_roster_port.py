"""
QML Agents-Domäne — Zugriff auf den Agent-Registry-Roster (ohne direkten Registry-Import im ViewModel).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.agents.agent_profile import AgentProfile


@runtime_checkable
class QmlAgentRosterPort(Protocol):
    def refresh_registry(self) -> None:
        ...

    def list_all_profiles(self) -> list[AgentProfile]:
        ...

    def get_profile(self, agent_id: str) -> AgentProfile | None:
        ...
