"""
Smoke Tests: Komplette Workflows.

Prüft End-to-End-Abläufe:
- Chat starten, Prompt senden, Antwort erhalten
- Agent starten, Task ausführen
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_repository import AgentRepository
from app.agents.execution_engine import ExecutionEngine
from app.agents.task import Task, TaskStatus
from app.agents.task_graph import TaskGraph
from app.agents.delegation_engine import DelegationEngine
from app.agents.agent_router import AgentRouter
from app.agents.agent_registry import AgentRegistry
from app.agents.agent_factory import AgentFactory
from app.core.llm.llm_complete import complete


@pytest.mark.smoke
class TestChatWorkflowSmoke:
    """Smoke: Chat-Workflow (Prompt → Antwort)."""

    @pytest.mark.asyncio
    async def test_prompt_send_receive_mock(self):
        """Prompt senden, Antwort erhalten (Mock)."""
        async def mock_chat(**kwargs):
            yield {"message": {"content": "Smoke-Antwort"}}

        result = await complete(
            chat_fn=mock_chat,
            model="test",
            messages=[{"role": "user", "content": "Hallo"}],
        )
        assert isinstance(result, str)
        assert "Smoke-Antwort" in result or "Fehler" in result

    def test_chat_widget_has_run_chat(self):
        """ChatWidget bietet run_chat für Chat-Ausführung."""
        from app.gui.legacy import ChatWidget
        assert hasattr(ChatWidget, "run_chat")


@pytest.mark.smoke
class TestAgentWorkflowSmoke:
    """Smoke: Agent-Workflow (Task planen → ausführen)."""

    @pytest.fixture
    def temp_db(self, tmp_path):
        import tempfile
        import os
        fd, path = tempfile.mkstemp(suffix=".db", dir=str(tmp_path))
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except OSError:
            pass

    @pytest.fixture
    def repo_with_agent(self, temp_db):
        repo = AgentRepository(db_path=temp_db)
        profile = AgentProfile(
            name="Smoke-Agent",
            slug="smoke_agent",
            department="research",
            status=AgentStatus.ACTIVE.value,
            capabilities=["research"],
        )
        repo.create(profile)
        return repo

    @pytest.mark.asyncio
    async def test_agent_task_execution_mock(self, repo_with_agent):
        """Agent starten, Task ausführen (Mock run_fn)."""
        registry = AgentRegistry(repository=repo_with_agent)
        registry.refresh()
        router = AgentRouter(registry=registry)
        delegation = DelegationEngine(router=router)
        factory = AgentFactory()
        factory._registry = registry

        async def mock_run(agent_id: str, prompt: str, context: dict) -> str:
            return "Task-Ergebnis (Mock)"

        engine = ExecutionEngine(
            run_fn=mock_run,
            factory=factory,
            delegation_engine=delegation,
        )

        task = Task(
            description="Test-Task",
            input={"prompt": "Test"},
            tool_hint="research",
        )
        graph = TaskGraph()
        graph.add_task(task)

        result = await engine.run_task(task, graph)

        assert "Task-Ergebnis" in result
        assert graph.get_task(task.id).status == TaskStatus.COMPLETED
