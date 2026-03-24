"""Adapter: :class:`QmlAgentRosterPort` → :func:`app.agents.agent_registry.get_agent_registry`."""

from __future__ import annotations

from app.agents.agent_profile import AgentProfile


class ServiceQmlAgentRosterAdapter:
    def refresh_registry(self) -> None:
        from app.agents.agent_registry import get_agent_registry

        get_agent_registry().refresh()

    def list_all_profiles(self) -> list[AgentProfile]:
        from app.agents.agent_registry import get_agent_registry

        return get_agent_registry().list_all()

    def get_profile(self, agent_id: str) -> AgentProfile | None:
        from app.agents.agent_registry import get_agent_registry

        try:
            return get_agent_registry().get(agent_id)
        except Exception:
            return None
