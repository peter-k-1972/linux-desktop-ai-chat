"""
QA Coverage Map – Loader.

Lädt Input-Artefakte für den Coverage-Map-Generator.
Read-only; keine Mutation der Quelldateien.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

LOG = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


def load_json(path: Path) -> dict[str, Any] | None:
    """Lädt JSON-Datei. Gibt None bei Fehler oder fehlender Datei."""
    if not path.exists():
        LOG.debug("Datei nicht gefunden: %s", path)
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        LOG.warning("Konnte %s nicht laden: %s", path, e)
        return None


def _artifacts_json(qa_dir: Path) -> Path:
    return qa_dir / "artifacts" / "json"


def load_inventory(qa_dir: Path | None = None) -> dict[str, Any]:
    """
    Lädt QA_TEST_INVENTORY.json.
    Pflicht-Input – wirft bei Fehler.
    """
    qa_dir = qa_dir or _default_qa_dir()
    path = _artifacts_json(qa_dir) / "QA_TEST_INVENTORY.json"
    data = load_json(path)
    if data is None:
        raise FileNotFoundError(f"QA_TEST_INVENTORY.json nicht gefunden oder ungültig: {path}")
    return data


def load_test_strategy(qa_dir: Path | None = None) -> dict[str, Any] | None:
    """Lädt QA_TEST_STRATEGY.json. Optional."""
    qa_dir = qa_dir or _default_qa_dir()
    return load_json(_artifacts_json(qa_dir) / "QA_TEST_STRATEGY.json")


def load_knowledge_graph(qa_dir: Path | None = None) -> dict[str, Any] | None:
    """Lädt QA_KNOWLEDGE_GRAPH.json. Optional."""
    qa_dir = qa_dir or _default_qa_dir()
    return load_json(_artifacts_json(qa_dir) / "QA_KNOWLEDGE_GRAPH.json")


def load_autopilot_v3(qa_dir: Path | None = None) -> dict[str, Any] | None:
    """Lädt QA_AUTOPILOT_V3.json. Optional."""
    qa_dir = qa_dir or _default_qa_dir()
    return load_json(_artifacts_json(qa_dir) / "QA_AUTOPILOT_V3.json")


def load_incidents_index(qa_dir: Path | None = None) -> dict[str, Any] | None:
    """Lädt incidents/index.json. Optional."""
    qa_dir = qa_dir or _default_qa_dir()
    return load_json(qa_dir / "incidents" / "index.json")


def load_incidents_analytics(qa_dir: Path | None = None) -> dict[str, Any] | None:
    """Lädt incidents/analytics.json. Optional."""
    qa_dir = qa_dir or _default_qa_dir()
    return load_json(qa_dir / "incidents" / "analytics.json")


def load_bindings_by_incident(qa_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """
    Lädt alle bindings.json aus incidents/*/.
    Returns: {incident_id: bindings_dict}
    rejected/archived werden ignoriert.
    """
    qa_dir = qa_dir or _default_qa_dir()
    incidents_dir = qa_dir / "incidents"
    result: dict[str, dict[str, Any]] = {}
    if not incidents_dir.exists():
        return result
    for inc_dir in incidents_dir.iterdir():
        if not inc_dir.is_dir() or inc_dir.name.startswith("_"):
            continue
        bindings_path = inc_dir / "bindings.json"
        if not bindings_path.exists():
            continue
        data = load_json(bindings_path)
        if data is None:
            continue
        status = (data.get("status") or {}).get("binding_status", "")
        if status in ("rejected", "archived"):
            continue
        incident_id = (data.get("identity") or {}).get("incident_id") or inc_dir.name.split("_")[0]
        result[incident_id] = data
    return result


def load_all_inputs(qa_dir: Path | None = None) -> dict[str, Any]:
    """
    Lädt alle Inputs für den Coverage-Map-Generator.
    Returns dict mit: inventory, test_strategy, knowledge_graph, autopilot_v3,
    incidents_index, incidents_analytics, bindings_by_incident, input_sources.
    """
    qa_dir = qa_dir or _default_qa_dir()
    inventory = load_inventory(qa_dir)
    test_strategy = load_test_strategy(qa_dir)
    knowledge_graph = load_knowledge_graph(qa_dir)
    autopilot_v3 = load_autopilot_v3(qa_dir)
    incidents_index = load_incidents_index(qa_dir)
    incidents_analytics = load_incidents_analytics(qa_dir)
    bindings_by_incident = load_bindings_by_incident(qa_dir)

    input_sources: list[str] = ["docs/qa/artifacts/json/QA_TEST_INVENTORY.json"]
    if test_strategy:
        input_sources.append("docs/qa/artifacts/json/QA_TEST_STRATEGY.json")
    if knowledge_graph:
        input_sources.append("docs/qa/artifacts/json/QA_KNOWLEDGE_GRAPH.json")
    if autopilot_v3:
        input_sources.append("docs/qa/artifacts/json/QA_AUTOPILOT_V3.json")
    if incidents_index:
        input_sources.append("docs/qa/incidents/index.json")
    if incidents_analytics:
        input_sources.append("docs/qa/incidents/analytics.json")
    if bindings_by_incident:
        input_sources.append("docs/qa/incidents/*/bindings.json")

    return {
        "inventory": inventory,
        "test_strategy": test_strategy or {},
        "knowledge_graph": knowledge_graph or {},
        "autopilot_v3": autopilot_v3 or {},
        "incidents_index": incidents_index or {},
        "incidents_analytics": incidents_analytics or {},
        "bindings_by_incident": bindings_by_incident,
        "input_sources": sorted(set(input_sources)),
    }
