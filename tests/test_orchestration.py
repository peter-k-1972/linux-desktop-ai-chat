"""
Tests für Agenten-Orchestrierung: Task, TaskGraph, TaskPlanner, AgentRouter,
DelegationEngine, ExecutionEngine.
"""

import os
import tempfile
import pytest

from app.agents.task import Task, TaskStatus
from app.agents.task_graph import TaskGraph
from app.agents.task_planner import TaskPlanner
from app.agents.agent_router import AgentRouter
from app.agents.delegation_engine import DelegationEngine
from app.agents.execution_engine import ExecutionEngine
from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_registry import AgentRegistry
from app.agents.agent_repository import AgentRepository
from app.agents.departments import Department
from app.agents.seed_agents import _seed_profiles


# --- Task ---


def test_task_creation():
    """Task-Erstellung mit Defaults."""
    t = Task(description="Test-Task")
    assert t.id
    assert t.description == "Test-Task"
    assert t.status == TaskStatus.PENDING
    assert t.assigned_agent is None
    assert t.dependencies == []
    assert t.created_at is not None
    assert t.updated_at is not None


def test_task_serialization():
    """Task to_dict / from_dict."""
    t = Task(
        description="Serial",
        assigned_agent="agent-1",
        status=TaskStatus.COMPLETED,
        output="Done",
        dependencies=["dep-1"],
        priority=10,
    )
    d = t.to_dict()
    t2 = Task.from_dict(d)
    assert t2.description == t.description
    assert t2.assigned_agent == t.assigned_agent
    assert t2.status == t.status
    assert t2.output == t.output
    assert t2.dependencies == t.dependencies
    assert t2.priority == t.priority


def test_task_status_properties():
    """Task Status-Properties."""
    t = Task(description="X")
    assert t.is_pending
    assert not t.is_completed
    t.status = TaskStatus.RUNNING
    assert t.is_running
    t.status = TaskStatus.COMPLETED
    assert t.is_completed
    assert t.is_terminal
    t.status = TaskStatus.FAILED
    assert t.is_failed
    assert t.is_terminal


# --- TaskGraph ---


def test_task_graph_add_and_get():
    """TaskGraph: add_task, get_task, get_all_tasks."""
    g = TaskGraph()
    t1 = Task(description="A")
    t2 = Task(description="B", dependencies=[t1.id])
    g.add_task(t1)
    g.add_task(t2)
    assert g.get_task(t1.id) == t1
    assert g.get_task(t2.id) == t2
    assert len(g.get_all_tasks()) == 2


def test_task_graph_get_ready_tasks():
    """TaskGraph: get_ready_tasks berücksichtigt Dependencies."""
    g = TaskGraph()
    t1 = Task(description="A")
    t2 = Task(description="B", dependencies=[t1.id])
    g.add_task(t1)
    g.add_task(t2)
    ready = g.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].id == t1.id
    g.mark_completed(t1.id, "ok")
    ready2 = g.get_ready_tasks()
    assert len(ready2) == 1
    assert ready2[0].id == t2.id


def test_task_graph_mark_completed_failed():
    """TaskGraph: mark_completed, mark_failed."""
    g = TaskGraph()
    t = Task(description="X")
    g.add_task(t)
    assert g.mark_completed(t.id, "Result")
    assert g.get_task(t.id).status == TaskStatus.COMPLETED
    assert g.get_task(t.id).output == "Result"
    t2 = Task(description="Y")
    g.add_task(t2)
    assert g.mark_failed(t2.id, "Error")
    assert g.get_task(t2.id).status == TaskStatus.FAILED
    assert g.get_task(t2.id).error == "Error"


def test_task_graph_get_next_tasks():
    """TaskGraph: get_next_tasks liefert priorisierte bereite Tasks."""
    g = TaskGraph()
    t1 = Task(description="Low", priority=1)
    t2 = Task(description="High", priority=10)
    g.add_task(t1)
    g.add_task(t2)
    next_tasks = g.get_next_tasks(limit=5)
    assert len(next_tasks) == 2
    assert next_tasks[0].description == "High"
    assert next_tasks[1].description == "Low"


def test_task_graph_is_complete():
    """TaskGraph: is_complete."""
    g = TaskGraph()
    t = Task(description="X")
    g.add_task(t)
    assert not g.is_complete()
    g.mark_completed(t.id)
    assert g.is_complete()


# --- TaskPlanner ---


@pytest.mark.asyncio
async def test_task_planner_heuristic_video():
    """TaskPlanner: Heuristik für Video-Prompt."""
    planner = TaskPlanner(llm_complete_fn=None)
    graph = await planner.plan("Erstelle ein Video über KI-Agenten")
    tasks = graph.get_all_tasks()
    assert len(tasks) >= 4
    descs = [t.description.lower() for t in tasks]
    assert any("recherch" in d or "thema" in d for d in descs)
    assert any("skript" in d or "script" in d for d in descs)
    assert any("video" in d or "render" in d for d in descs)


@pytest.mark.asyncio
async def test_task_planner_heuristic_code():
    """TaskPlanner: Heuristik für Code-Prompt."""
    planner = TaskPlanner(llm_complete_fn=None)
    graph = await planner.plan("Schreibe eine Python-Funktion für Fibonacci")
    tasks = graph.get_all_tasks()
    assert len(tasks) == 1
    assert "code" in tasks[0].description.lower() or "erstellen" in tasks[0].description.lower()


@pytest.mark.asyncio
async def test_task_planner_heuristic_default():
    """TaskPlanner: Fallback für generischen Prompt."""
    planner = TaskPlanner(llm_complete_fn=None)
    graph = await planner.plan("Was ist die Hauptstadt von Frankreich?")
    tasks = graph.get_all_tasks()
    assert len(tasks) >= 1
    assert "frankreich" in tasks[0].description.lower() or len(tasks[0].description) > 0


@pytest.mark.asyncio
async def test_task_planner_with_mock_llm():
    """TaskPlanner: LLM-Planung mit Mock."""
    async def mock_llm(model_id, messages):
        return "1. Thema recherchieren (research)\n2. Skript schreiben (code)\n3. Video rendern (video)"

    planner = TaskPlanner(llm_complete_fn=mock_llm)
    graph = await planner.plan("Video über X")
    tasks = graph.get_all_tasks()
    assert len(tasks) == 3
    assert tasks[0].tool_hint == "research"
    assert tasks[1].dependencies == [tasks[0].id]
    assert tasks[2].dependencies == [tasks[1].id]


# --- AgentRouter (benötigt Registry mit Agenten) ---


@pytest.fixture
def registry_with_agents():
    """Registry mit geseedeten Agenten."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    repo = AgentRepository(db_path=path)
    for p in _seed_profiles():
        try:
            repo.create(p)
        except Exception:
            pass
    reg = AgentRegistry(repository=repo)
    reg.refresh()
    yield reg
    try:
        os.unlink(path)
    except OSError:
        pass


def test_agent_router_by_tool_hint(registry_with_agents):
    """AgentRouter: Routing über tool_hint."""
    router = AgentRouter(registry=registry_with_agents)
    t = Task(description="Recherche", tool_hint="research")
    profile = router.route(t)
    assert profile is not None
    assert "research" in profile.department.lower() or "research" in profile.slug.lower()


def test_agent_router_by_description(registry_with_agents):
    """AgentRouter: Routing über Beschreibung."""
    router = AgentRouter(registry=registry_with_agents)
    t = Task(description="Code schreiben und debuggen")
    profile = router.route(t)
    assert profile is not None
    assert "code" in profile.department.lower() or "code" in profile.slug.lower()


def test_agent_router_fallback(registry_with_agents):
    """AgentRouter: Fallback auf General Assistant."""
    router = AgentRouter(registry=registry_with_agents)
    t = Task(description="Unbekannte Aufgabe xyz123")
    profile = router.route(t)
    assert profile is not None


# --- DelegationEngine ---


def test_delegation_assign_agent(registry_with_agents):
    """DelegationEngine: assign_agent setzt assigned_agent."""
    router = AgentRouter(registry=registry_with_agents)
    engine = DelegationEngine(router=router)
    t = Task(description="Recherche durchführen", tool_hint="research")
    profile = engine.assign_agent(t)
    assert profile is not None
    assert t.assigned_agent is not None
    assert t.assigned_agent in (profile.id, profile.slug)


def test_delegation_dispatch_task(registry_with_agents):
    """DelegationEngine: dispatch_task markiert Task als running."""
    router = AgentRouter(registry=registry_with_agents)
    engine = DelegationEngine(router=router)
    g = TaskGraph()
    t = Task(description="Code", tool_hint="code")
    g.add_task(t)
    profile = engine.dispatch_task(t, g)
    assert profile is not None
    assert g.get_task(t.id).status == TaskStatus.RUNNING


# --- ExecutionEngine ---


@pytest.mark.asyncio
async def test_execution_engine_run_task(registry_with_agents):
    """ExecutionEngine: run_task mit Mock run_fn."""
    async def mock_run(agent_id, prompt, context):
        return f"Result for {prompt[:20]}"

    exec_engine = ExecutionEngine(run_fn=mock_run)
    router = AgentRouter(registry=registry_with_agents)
    exec_engine._delegation = DelegationEngine(router=router)

    g = TaskGraph()
    t = Task(description="Test", tool_hint="research")
    g.add_task(t)

    result = await exec_engine.run_task(t, g)
    assert "Result" in result
    assert g.get_task(t.id).status == TaskStatus.COMPLETED
    assert g.get_task(t.id).output is not None


@pytest.mark.asyncio
async def test_execution_engine_run_graph(registry_with_agents):
    """ExecutionEngine: run_graph führt mehrere Tasks aus."""
    async def mock_run(agent_id, prompt, context):
        return f"Done: {prompt[:30]}"

    exec_engine = ExecutionEngine(run_fn=mock_run)
    router = AgentRouter(registry=registry_with_agents)
    exec_engine._delegation = DelegationEngine(router=router)

    g = TaskGraph()
    t1 = Task(description="First")
    t2 = Task(description="Second", dependencies=[t1.id])
    g.add_task(t1)
    g.add_task(t2)

    result = await exec_engine.run_graph(g)
    assert "Done" in result
    assert g.is_complete()
    assert g.get_task(t1.id).status == TaskStatus.COMPLETED
    assert g.get_task(t2.id).status == TaskStatus.COMPLETED
