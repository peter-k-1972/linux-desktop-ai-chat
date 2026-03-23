"""
IconRegistry – semantische Icon-Namen und Pfad-Mapping.

Single Source of Truth für alle Icon-IDs und ihre Zuordnung zu SVG-Dateien.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class IconEntry:
    """Eintrag für ein Icon: Name, Kategorie, Dateiname."""

    name: str
    category: str
    filename: str

    @property
    def path(self) -> Path:
        """Relativer Pfad zur SVG-Datei."""
        return Path(self.category) / self.filename


class IconRegistry:
    """
    Registry aller verfügbaren Icons.
    Kategorien: navigation, panels, actions, status, runtime
    """

    # --- Navigation (Hauptbereiche) ---
    DASHBOARD = "dashboard"
    CHAT = "chat"
    CONTROL = "control"
    SHIELD = "shield"
    ACTIVITY = "activity"
    GEAR = "gear"

    # --- Panels / Workspaces ---
    AGENTS = "agents"
    MODELS = "models"
    PROVIDERS = "providers"
    TOOLS = "tools"
    DATA_STORES = "data_stores"
    KNOWLEDGE = "knowledge"
    PROMPT_STUDIO = "prompt_studio"
    PROJECTS = "projects"
    TEST_INVENTORY = "test_inventory"
    COVERAGE_MAP = "coverage_map"
    GAP_ANALYSIS = "gap_analysis"
    INCIDENTS = "incidents"
    REPLAY_LAB = "replay_lab"
    APPEARANCE = "appearance"
    SYSTEM = "system"
    ADVANCED = "advanced"
    EVENTBUS = "eventbus"
    LOGS = "logs"
    METRICS = "metrics"
    LLM_CALLS = "llm_calls"
    AGENT_ACTIVITY = "agent_activity"
    SYSTEM_GRAPH = "system_graph"

    # --- Actions ---
    ADD = "add"
    REMOVE = "remove"
    EDIT = "edit"
    REFRESH = "refresh"
    SEARCH = "search"
    FILTER = "filter"
    RUN = "run"
    STOP = "stop"
    SAVE = "save"
    DEPLOY = "deploy"
    PIN = "pin"
    OPEN = "open"
    LINK_OUT = "link_out"

    # --- System / Meta ---
    HELP = "help"
    INFO = "info"
    SEND = "send"

    # --- Status ---
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    RUNNING = "running"
    IDLE = "idle"
    PAUSED = "paused"

    # --- Runtime QA (Observability) — getrennt von Governance-Shield ---
    QA_RUNTIME = "qa_runtime"

    # --- AI / Demo ---
    SPARKLES = "sparkles"

    # --- Workflow / Data (Erweiterung) ---
    GRAPH = "graph"
    PIPELINE = "pipeline"
    DATASET = "dataset"
    FOLDER = "folder"

    _ENTRIES: list[IconEntry] = [
        # Navigation
        IconEntry(DASHBOARD, "navigation", "dashboard.svg"),
        IconEntry(CHAT, "navigation", "chat.svg"),
        IconEntry(CONTROL, "navigation", "control.svg"),
        IconEntry(SHIELD, "navigation", "shield.svg"),
        IconEntry(ACTIVITY, "navigation", "activity.svg"),
        IconEntry(GEAR, "navigation", "gear.svg"),
        # Panels
        IconEntry(AGENTS, "panels", "agents.svg"),
        IconEntry(MODELS, "panels", "models.svg"),
        IconEntry(PROVIDERS, "panels", "providers.svg"),
        IconEntry(TOOLS, "panels", "tools.svg"),
        IconEntry(DATA_STORES, "panels", "data_stores.svg"),
        IconEntry(KNOWLEDGE, "panels", "knowledge.svg"),
        IconEntry(PROMPT_STUDIO, "panels", "prompt_studio.svg"),
        IconEntry(PROJECTS, "panels", "projects.svg"),
        IconEntry(TEST_INVENTORY, "panels", "test_inventory.svg"),
        IconEntry(COVERAGE_MAP, "panels", "coverage_map.svg"),
        IconEntry(GAP_ANALYSIS, "panels", "gap_analysis.svg"),
        IconEntry(INCIDENTS, "panels", "incidents.svg"),
        IconEntry(REPLAY_LAB, "panels", "replay_lab.svg"),
        IconEntry(APPEARANCE, "panels", "appearance.svg"),
        IconEntry(SYSTEM, "panels", "system.svg"),
        IconEntry(ADVANCED, "panels", "advanced.svg"),
        IconEntry(EVENTBUS, "runtime", "eventbus.svg"),
        IconEntry(LOGS, "runtime", "logs.svg"),
        IconEntry(METRICS, "runtime", "metrics.svg"),
        IconEntry(LLM_CALLS, "runtime", "llm_calls.svg"),
        IconEntry(AGENT_ACTIVITY, "runtime", "agent_activity.svg"),
        IconEntry(SYSTEM_GRAPH, "runtime", "system_graph.svg"),
        IconEntry(QA_RUNTIME, "runtime", "qa_runtime.svg"),
        # Actions
        IconEntry(ADD, "actions", "add.svg"),
        IconEntry(REMOVE, "actions", "remove.svg"),
        IconEntry(EDIT, "actions", "edit.svg"),
        IconEntry(REFRESH, "actions", "refresh.svg"),
        IconEntry(SEARCH, "actions", "search.svg"),
        IconEntry(FILTER, "actions", "filter.svg"),
        IconEntry(RUN, "actions", "run.svg"),
        IconEntry(STOP, "actions", "stop.svg"),
        IconEntry(SAVE, "actions", "save.svg"),
        IconEntry(DEPLOY, "actions", "deploy.svg"),
        IconEntry(PIN, "actions", "pin.svg"),
        IconEntry(OPEN, "actions", "open.svg"),
        IconEntry(LINK_OUT, "actions", "link_out.svg"),
        IconEntry(SPARKLES, "ai", "sparkles.svg"),
        IconEntry(GRAPH, "workflow", "graph.svg"),
        IconEntry(PIPELINE, "workflow", "pipeline.svg"),
        IconEntry(DATASET, "data", "dataset.svg"),
        IconEntry(FOLDER, "data", "folder.svg"),
        IconEntry(HELP, "system", "help.svg"),
        IconEntry(INFO, "system", "info.svg"),
        IconEntry(SEND, "system", "send.svg"),
        # Status
        IconEntry(SUCCESS, "status", "success.svg"),
        IconEntry(WARNING, "status", "warning.svg"),
        IconEntry(ERROR, "status", "error.svg"),
        IconEntry(RUNNING, "status", "running.svg"),
        IconEntry(IDLE, "status", "idle.svg"),
        IconEntry(PAUSED, "status", "paused.svg"),
    ]

    _BY_NAME: dict[str, IconEntry] = {}

    @classmethod
    def _ensure_index(cls) -> None:
        if not cls._BY_NAME:
            for e in cls._ENTRIES:
                cls._BY_NAME[e.name] = e

    @classmethod
    def get_path(cls, name: str) -> Path | None:
        """Liefert den relativen Pfad für ein Icon, oder None."""
        cls._ensure_index()
        entry = cls._BY_NAME.get(name)
        return entry.path if entry else None

    @classmethod
    def all_names(cls) -> list[str]:
        """Alle registrierten Icon-Namen."""
        cls._ensure_index()
        return list(cls._BY_NAME.keys())

    @classmethod
    def iter_entries(cls) -> Iterator[IconEntry]:
        """Iteriert über alle Icon-Einträge."""
        yield from cls._ENTRIES
