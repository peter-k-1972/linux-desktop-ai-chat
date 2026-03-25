"""
Pytest Fixtures für Linux-Desktop-Chat.

Zentrale Fixtures für Unit-, UI- und Smoke-Tests.
"""

import json
import os

# Single-Instance-Lock deaktivieren während Tests (verhindert Konflikte)
os.environ.setdefault("LINUX_DESKTOP_CHAT_SINGLE_INSTANCE", "0")
# Kein automatisches Default-Projekt „Allgemein“ in pytest (deterministische DB-/Kontexttests)
os.environ.setdefault("LINUX_DESKTOP_CHAT_SKIP_DEFAULT_PROJECT", "1")
# Feature-Registry-Tests: Edition-Maske ohne harte Import-Probes (chromadb …).
# Echte Availability: tests/unit/features/test_dependency_availability.py erzwingt Prüfungen.
os.environ.setdefault("LDC_IGNORE_TECHNICAL_AVAILABILITY", "1")

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_repository import AgentRepository
from app.debug.agent_event import AgentEvent, EventType
from app.prompts.prompt_models import Prompt
from app.rag.models import Document, Chunk
from app.metrics.agent_metrics import AgentMetricEvent, MetricEventType


# --- QApplication (für GUI-Tests) ---

@pytest.fixture(scope="session", autouse=True)
def qapplication():
    """QApplication für GUI-Tests (ChatWidget, Agent HR, Debug Panel)."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# --- Event Loop für PySide6 + qasync ---

@pytest.fixture
def qt_event_loop(qapplication):
    """
    Event Loop mit qasync für PySide6 – damit async UI-Tests funktionieren.

    Nutzen für Tests, die asyncio mit Qt-Widgets kombinieren (z.B. ChatWidget.run_chat).
    """
    try:
        from qasync import QEventLoop
    except ImportError:
        pytest.skip("qasync nicht installiert – pip install qasync")
    loop = QEventLoop(qapplication)
    yield loop
    loop.close()


# --- Test Agent ---

@pytest.fixture
def test_agent():
    """Beispiel-Agentenprofil für Tests."""
    return AgentProfile(
        id="test-agent-001",
        name="Test-Research-Agent",
        display_name="Research Agent (Test)",
        slug="test_research_agent",
        short_description="Agent für Recherche-Tests",
        long_description="Vollständige Beschreibung für Tests",
        department="research",
        role="Researcher",
        status=AgentStatus.ACTIVE.value,
        system_prompt="Du bist ein hilfreicher Recherche-Assistent.",
        capabilities=["research", "analysis"],
        tools=["rag", "web_search"],
        knowledge_spaces=[],
        tags=["test"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        visibility_in_chat=True,
        priority=0,
    )


@pytest.fixture
def test_agent_inactive():
    """Inaktiver Agent für Tests."""
    return AgentProfile(
        id="test-agent-002",
        name="Test-Inactive-Agent",
        display_name="Inactive (Test)",
        slug="test_inactive",
        department="development",
        status=AgentStatus.INACTIVE.value,
        visibility_in_chat=False,
    )


# --- Test Prompt ---

@pytest.fixture
def test_prompt():
    """Beispiel-Prompt für Tests."""
    return Prompt(
        id=1,
        title="Code Review",
        category="code",
        description="Bitte prüfe den Code.",
        content="Analysiere den Code und gib Feedback.",
        tags=["code", "review"],
        prompt_type="user",
        scope="global",
        project_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def test_prompt_empty():
    """Leerer Prompt für Create-Tests."""
    return Prompt.empty()


# --- Test Document ---

@pytest.fixture
def test_document():
    """Beispiel-Dokument für RAG-Tests."""
    return Document(
        id="doc-test-001",
        path="/tmp/test_readme.md",
        content="# Test-Dokument\n\nDies ist Beispielinhalt für RAG-Tests. "
        "Es enthält mehrere Sätze. Absatz zwei mit mehr Text. "
        "Absatz drei für Chunking-Tests. " * 5,
        metadata={"filename": "test_readme.md", "extension": ".md"},
        source_type="file",
    )


@pytest.fixture
def test_document_file(tmp_path):
    """Erstellt eine echte Testdatei und liefert den Document-Loader-Pfad."""
    md = tmp_path / "sample.md"
    md.write_text(
        "# Beispiel\n\nInhalt für Document-Loader-Tests.\n\n"
        "Mehrere Absätze für Chunking.",
        encoding="utf-8",
    )
    return str(md)


# --- Test Chunk ---

@pytest.fixture
def test_chunk():
    """Beispiel-Chunk für RAG-Tests."""
    return Chunk(
        id="chunk-001",
        document_id="doc-001",
        content="Dies ist der Chunk-Inhalt für Kontext-Tests.",
        metadata={"filename": "test.md", "chunk_index": 0, "total_chunks": 1},
        position=0,
    )


# --- Test Task / Event ---

@pytest.fixture
def test_event():
    """Beispiel-AgentEvent für Debug/Metrics-Tests."""
    return AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name="Test-Agent",
        task_id="task-001",
        event_type=EventType.TASK_COMPLETED,
        message="Task abgeschlossen",
        metadata={"agent_id": "agent-001", "duration_sec": 2.5, "critic_score": 0.9},
    )


@pytest.fixture
def test_task_event():
    """Task-Event für Metrics-Tests."""
    return AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name="Research",
        task_id="task-123",
        event_type=EventType.TASK_COMPLETED,
        message="Recherche abgeschlossen",
        metadata={"agent_id": "research-001", "duration_sec": 5.0},
    )


# --- Test Metric Event ---

@pytest.fixture
def test_metric_event():
    """Beispiel AgentMetricEvent für Metrics-Tests."""
    return AgentMetricEvent(
        timestamp=datetime.now(timezone.utc),
        agent_id="agent-001",
        event_type=MetricEventType.TASK_COMPLETED,
        task_id="task-001",
        duration_sec=3.0,
        critic_score=0.85,
        metadata={},
    )


# --- Isolierte Datenbanken für Tests ---

@pytest.fixture
def temp_db_path():
    """Temporärer Pfad für Test-Datenbank (Agents, Prompts, Metrics)."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def agent_repository(temp_db_path):
    """AgentRepository mit temporärer DB."""
    return AgentRepository(db_path=temp_db_path)


@pytest.fixture
def temp_chroma_dir(tmp_path):
    """Temporäres Verzeichnis für ChromaDB (Vector Store)."""
    return str(tmp_path / "chroma_test")


# --- Testdaten-Pfade ---

@pytest.fixture
def sample_documents_dir():
    """Pfad zu den Beispiel-Dokumenten."""
    base = Path(__file__).parent / "data" / "sample_documents"
    return str(base) if base.exists() else None


@pytest.fixture
def sample_prompts_path():
    """Pfad zur Beispiel-Prompts JSON."""
    return Path(__file__).parent / "data" / "sample_prompts.json"


@pytest.fixture
def sample_agents_path():
    """Pfad zur Beispiel-Agenten JSON."""
    return Path(__file__).parent / "data" / "sample_agents.json"


def pytest_sessionfinish(session, exitstatus):
    """Offene aiohttp-Sessions der Infrastruktur vor Prozessende schließen."""
    from app.services import infrastructure as infra_mod

    inst = infra_mod._infrastructure
    if inst is not None:
        infra_mod._close_ollama_client_best_effort(getattr(inst, "_client", None))
