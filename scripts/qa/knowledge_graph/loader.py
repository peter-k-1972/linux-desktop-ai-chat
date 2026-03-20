"""
QA Knowledge Graph – Lader für Input-Artefakte.

Lädt: incidents/index.json, incidents/analytics.json, QA_AUTOPILOT_V3.json,
QA_TEST_STRATEGY.json, REGRESSION_CATALOG.json (oder .md Fallback).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import (
    get_project_root,
    load_json,
    parse_regression_catalog_md,
    _to_relative_source,
)


@dataclass(frozen=False)
class KnowledgeGraphInputs:
    """Input-Daten für den Knowledge Graph."""
    incident_index: dict[str, Any] | None
    analytics: dict[str, Any] | None
    autopilot_v3: dict[str, Any] | None
    test_strategy: dict[str, Any] | None
    regression_catalog: dict[str, Any] | None
    regression_catalog_parsed: dict[str, Any]  # Aus .md geparst falls .json fehlt
    loaded_sources: list[str]


def load_regression_catalog(
    json_path: Path | None,
    md_path: Path | None,
    project_root: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """
    Lädt REGRESSION_CATALOG. Versucht .json, Fallback auf .md-Parsing.
    Gibt (raw_catalog, parsed_structure) zurück.
    """
    catalog = load_json(json_path) if json_path else None
    parsed: dict[str, Any] = {"failure_class_to_domains": {}, "test_domains": []}

    if catalog and isinstance(catalog, dict):
        # JSON-Format: erwarte failure_classes, test_mappings o.ä.
        parsed["failure_class_to_domains"] = catalog.get("failure_class_to_domains", {})
        parsed["test_domains"] = catalog.get("test_domains", [])
        parsed["failure_class_to_tests"] = catalog.get("failure_class_to_tests", {})
    elif md_path and md_path.exists():
        content = md_path.read_text(encoding="utf-8")
        parsed = parse_regression_catalog_md(content)

    return catalog, parsed


def load_knowledge_graph_inputs(
    incident_index_path: Path | None = None,
    analytics_path: Path | None = None,
    autopilot_v3_path: Path | None = None,
    test_strategy_path: Path | None = None,
    regression_catalog_path: Path | None = None,
) -> KnowledgeGraphInputs:
    """Lädt alle Inputs für den Knowledge Graph."""
    project_root = get_project_root()
    docs_qa = project_root / "docs" / "qa"
    inc_dir = docs_qa / "incidents"

    # Default-Pfade
    incident_index_path = incident_index_path or inc_dir / "index.json"
    analytics_path = analytics_path or inc_dir / "analytics.json"
    autopilot_v3_path = autopilot_v3_path or docs_qa / "QA_AUTOPILOT_V3.json"
    test_strategy_path = test_strategy_path or docs_qa / "QA_TEST_STRATEGY.json"
    regression_catalog_path = regression_catalog_path or docs_qa / "REGRESSION_CATALOG.json"
    # Fallback: .md in gleichem Verzeichnis
    regression_md_path = regression_catalog_path.parent / "REGRESSION_CATALOG.md"

    sources: list[str] = []
    incident_index = load_json(incident_index_path)
    if incident_index:
        sources.append(_to_relative_source(incident_index_path, project_root))

    analytics = load_json(analytics_path)
    if analytics:
        sources.append(_to_relative_source(analytics_path, project_root))

    autopilot_v3 = load_json(autopilot_v3_path)
    if autopilot_v3:
        sources.append(_to_relative_source(autopilot_v3_path, project_root))

    test_strategy = load_json(test_strategy_path)
    if test_strategy:
        sources.append(_to_relative_source(test_strategy_path, project_root))

    catalog, catalog_parsed = load_regression_catalog(
        regression_catalog_path, regression_md_path, project_root
    )
    if catalog:
        sources.append(_to_relative_source(regression_catalog_path, project_root))
    elif regression_md_path.exists():
        sources.append(_to_relative_source(regression_md_path, project_root))

    return KnowledgeGraphInputs(
        incident_index=incident_index,
        analytics=analytics,
        autopilot_v3=autopilot_v3,
        test_strategy=test_strategy,
        regression_catalog=catalog,
        regression_catalog_parsed=catalog_parsed,
        loaded_sources=sources,
    )
