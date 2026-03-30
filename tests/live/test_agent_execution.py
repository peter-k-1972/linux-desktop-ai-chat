"""
Live Tests: Agent Execution.

Testet echte Agent-Ausführung mit Ollama.
Task planen → Agent zuweisen → LLM aufrufen → Ergebnis.
"""

import pytest

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_repository import AgentRepository
from app.agents.agent_registry import AgentRegistry
from app.agents.agent_router import AgentRouter
from app.agents.execution_engine import ExecutionEngine
from app.agents.task import Task, TaskStatus
from app.agents.task_graph import TaskGraph
from app.agents.delegation_engine import DelegationEngine
from app.agents.agent_factory import AgentFactory
from app.core.models.orchestrator import ModelOrchestrator
from app.core.llm.llm_complete import complete


def _ollama_available() -> bool:
    import asyncio

    from app.providers.ollama_client import OllamaClient

    client = OllamaClient()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        info = loop.run_until_complete(client.get_debug_info())
        return info.get("online", False)
    except Exception:
        return False
    finally:
        try:
            loop.run_until_complete(client.close())
        except Exception:
            pass
        loop.close()


@pytest.fixture(scope="module")
def ollama_available():
    if not _ollama_available():
        pytest.skip("Ollama nicht erreichbar – Agent Live-Test übersprungen")


@pytest.fixture
def temp_db_path(tmp_path):
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
def agent_repo_with_research_agent(temp_db_path):
    """Repository mit Research-Agent für Live-Tests."""
    repo = AgentRepository(db_path=temp_db_path)
    profile = AgentProfile(
        name="Live-Research-Agent",
        display_name="Research (Live)",
        slug="live_research",
        department="research",
        status=AgentStatus.ACTIVE.value,
        capabilities=["research", "analysis"],
        tools=["rag"],
        system_prompt="Du bist ein prägnanter Assistent. Antworte kurz.",
    )
    repo.create(profile)
    return repo


@pytest.mark.live
@pytest.mark.slow
class TestAgentExecutionLive:
    """Echte Agent-Ausführung mit Ollama."""

    @pytest.mark.asyncio
    async def test_execution_engine_run_task(
        self, agent_repo_with_research_agent, ollama_available, temp_db_path
    ):
        """ExecutionEngine führt Task mit echtem LLM aus."""
        from app.providers import CloudOllamaProvider, LocalOllamaProvider

        orchestrator = ModelOrchestrator(
            local_provider=LocalOllamaProvider(),
            cloud_provider=CloudOllamaProvider(),
        )
        await orchestrator.refresh_available_models()
        models = list(orchestrator._available_local) or ["llama3.2:latest", "qwen2.5:latest"]
        model_id = models[0] if models else "llama3.2:latest"

        async def run_fn(agent_id: str, prompt: str, context: dict) -> str:
            messages = [
                {"role": "system", "content": "Antworte in einem kurzen Satz."},
                {"role": "user", "content": prompt},
            ]
            return await complete(
                orchestrator.chat,
                model_id,
                messages,
                temperature=0,
                max_tokens=50,
            )

        registry = AgentRegistry(repository=agent_repo_with_research_agent)
        registry.refresh()
        router = AgentRouter(registry=registry)
        delegation = DelegationEngine(router=router)
        factory = AgentFactory()
        factory._registry = registry

        engine = ExecutionEngine(
            run_fn=run_fn,
            factory=factory,
            delegation_engine=delegation,
        )

        task = Task(
            description="Sage nur: Test erfolgreich",
            input={"prompt": "Antworte ausschließlich mit: Test erfolgreich"},
            tool_hint="research",
        )
        graph = TaskGraph()
        graph.add_task(task)

        result = await engine.run_task(task, graph)
        assert result is not None
        assert "Fehler" not in result or "erfolgreich" in result.lower()
        assert graph.get_task(task.id).status == TaskStatus.COMPLETED

        await orchestrator.close()
