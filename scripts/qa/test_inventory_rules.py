"""
QA Test Inventory – Mapping-Regeln.

Ableitungslogik für test_type, test_domain, subsystem, guard_type, failure_class.
Entspricht QA_TEST_INVENTORY_MAPPING_RULES.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Marker-Priorität für test_type (höchste zuerst)
MARKER_PRIORITY = [
    "regression",
    "contract",
    "failure_mode",
    "chaos",
    "async_behavior",
    "cross_layer",
    "state_consistency",
    "startup",
    "golden_path",
    "integration",
    "smoke",
    "live",
    "ui",
    "unit",
]

# Technische Marker (keine test_type-Kandidaten)
TECHNICAL_MARKERS = {"asyncio", "slow", "fast", "full"}

# Subsystem-Heuristik: (pattern, subsystem) – Reihenfolge wichtig (spezifisch zuerst)
SUBSYSTEM_PATTERNS = [
    (r"rag|chroma|embedding|retrieval", "RAG"),
    (r"ollama|llm|model_router|provider", "Provider/Ollama"),
    (r"debug|event_bus|event_store|event_type", "Debug/EventBus"),
    (r"prompt", "Prompt-System"),
    (r"agent", "Agentensystem"),
    (r"chat|chatwidget|composer", "Chat"),
    (r"metrics", "Metrics"),
    (r"sqlite|db_|persistence", "Persistenz/SQLite"),
    (r"tool|tools", "Tools"),
    (r"startup|app_starts|main_window", "Startup/Bootstrap"),
]

# test_type -> guard_type (nur wo belastbar)
GUARD_TYPE_MAP = {
    "failure_mode": "failure_replay_guard",
    "chaos": "failure_replay_guard",
    "contract": "event_contract_guard",
    "startup": "startup_degradation_guard",
}

VALID_FAILURE_CLASSES = {
    "ui_state_drift",
    "async_race",
    "late_signal_use_after_destroy",
    "request_context_loss",
    "rag_silent_failure",
    "debug_false_truth",
    "startup_ordering",
    "degraded_mode_failure",
    "contract_schema_drift",
    "metrics_false_success",
    "tool_failure_visibility",
    "optional_dependency_missing",
}


def derive_test_domain(file_path: str) -> str:
    """
    test_domain aus Pfad: tests/<domain>/...
    tests/qa/autopilot_v3/ -> qa
    tests/test_foo.py -> root (Datei direkt unter tests/)
    """
    path = Path(file_path)
    parts = path.parts
    if "tests" not in parts:
        return "root"
    idx = parts.index("tests")
    if idx + 1 >= len(parts):
        return "root"
    next_part = parts[idx + 1]
    if next_part.endswith(".py"):
        return "root"
    if next_part == "qa" and idx + 2 < len(parts):
        return "qa"
    return next_part


def derive_test_type(markers: list[str], test_domain: str) -> tuple[str, str]:
    """
    test_type aus Marker-Priorität, Fallback test_domain.
    Returns (test_type, inference_source).
    """
    for m in MARKER_PRIORITY:
        if m in markers:
            return m, "discovered"
    if test_domain in MARKER_PRIORITY:
        return test_domain, "inferred"
    if test_domain in ("root", "helpers"):
        return "unknown", "inferred"
    return test_domain if test_domain else "unknown", "inferred"


def derive_subsystem(file_path: str, test_name: str) -> tuple[str | None, str]:
    """
    subsystem aus Dateiname/Testname (Heuristik).
    Returns (subsystem, inference_source).
    """
    combined = f"{Path(file_path).stem} {test_name}".lower()
    for pattern, subsystem in SUBSYSTEM_PATTERNS:
        if re.search(pattern, combined):
            return subsystem, "inferred"
    return None, "unknown"


def derive_guard_types(test_type: str) -> list[str]:
    """guard_types aus test_type – nur wo Regel existiert."""
    gt = GUARD_TYPE_MAP.get(test_type)
    return [gt] if gt else []


def derive_execution_mode(markers: list[str]) -> str:
    """execution_mode: sync, async, live, slow."""
    if "live" in markers:
        return "live"
    if "asyncio" in markers:
        return "async"
    if "slow" in markers:
        return "slow"
    return "sync"


def requires_manual_review(
    test_domain: str,
    test_type: str,
    subsystem: str | None,
    file_path: str,
    test_name: str,
) -> bool:
    """
    manual_review_required wenn:
    - test_domain = root
    - test_domain = helpers
    - test_domain = unit und generischer Name
    - subsystem unknown und test_domain nicht qa
    """
    if test_domain in ("root", "helpers"):
        return True
    if test_domain == "unit":
        # Generische Namen
        generic = re.match(r"^test_(parse|validate|run|execute|foo|bar)$", test_name)
        if generic:
            return True
    return False


def parse_regression_catalog(content: str) -> dict[tuple[str, str], dict[str, list[str]]]:
    """
    Parst REGRESSION_CATALOG.md Tabelle.
    Key: (domain, datei_ohne_py), Value: dict test_name -> [failure_classes]
    Catalog nutzt Dateiname ohne .py und domain aus ### domain/
    """
    result: dict[tuple[str, str], dict[str, list[str]]] = {}
    current_domain: str | None = None

    for line in content.split("\n"):
        if "## Historische Bugs" in line or "## Erweiterung" in line:
            current_domain = None
            continue
        m_domain = re.match(r"^###\s+(.+)/?\s*$", line)
        if m_domain:
            current_domain = m_domain.group(1).strip().rstrip("/")
            continue

        if line.strip().startswith("|") and "---" not in line and current_domain:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3:
                datei, test, fehlerklasse = parts[0], parts[1], parts[2]
                if (
                    datei
                    and datei != "Datei"
                    and test
                    and test != "Test"
                    and datei.startswith("test_")
                ):
                    if fehlerklasse and fehlerklasse not in ("–", "-"):
                        for fk in [x.strip() for x in fehlerklasse.split(",")]:
                            fk = fk.strip()
                            if " (" in fk:
                                fk = fk.split(" (")[0].strip()
                            if fk and re.match(r"^[a-z_]+$", fk) and fk in VALID_FAILURE_CLASSES:
                                key = (current_domain, datei)
                                if key not in result:
                                    result[key] = {}
                                if test not in result[key]:
                                    result[key][test] = []
                                if fk not in result[key][test]:
                                    result[key][test].append(fk)
                    else:
                        key = (current_domain, datei)
                        if key not in result:
                            result[key] = {}
                        result[key][test] = []

    # Flatten to (domain, datei) -> {test: [classes]}
    return result


def lookup_failure_classes(
    catalog: dict[tuple[str, str], dict[str, list[str]]],
    test_domain: str,
    file_stem: str,
    test_name: str,
) -> tuple[list[str], str]:
    """
    Lookup failure_class aus Catalog.
    Unterstützt test_extract_chunk_parts_* als Wildcard.
    Returns (failure_classes, inference_source).
    """
    key = (test_domain, file_stem)
    if key not in catalog:
        return [], "unknown"

    tests_map = catalog[key]
    if test_name in tests_map:
        classes = tests_map[test_name]
        return list(classes) if classes else [], "catalog_bound"

    for pattern_test, classes in tests_map.items():
        if "*" in pattern_test:
            regex = pattern_test.replace("*", r".*")
            if re.match(regex, test_name):
                return list(classes) if classes else [], "catalog_bound"

    return [], "unknown"
