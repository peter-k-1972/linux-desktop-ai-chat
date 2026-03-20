"""
QA Cockpit – Check-Funktionen für Marker, EventType, Regression.

Leichtgewichtig, robust, keine großen Frameworks.
"""

from pathlib import Path

from scripts.qa.qa_paths import ARTIFACTS_DASHBOARDS, GOVERNANCE

# Projekt-Root (scripts/qa/ -> Projekt-Root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"

def _parse_top_risks_from_radar() -> list[tuple[str, str]]:
    """
    Liest Top-3-Risiken aus docs/qa/artifacts/dashboards/QA_RISK_RADAR.md.
    Fallback falls Datei fehlt oder Parsing scheitert.
    """
    radar_path = ARTIFACTS_DASHBOARDS / "QA_RISK_RADAR.md"
    if not radar_path.exists():
        return _TOP_RISKS_FALLBACK
    try:
        content = radar_path.read_text(encoding="utf-8")
        in_table = False
        results = []
        for line in content.splitlines():
            if "## 5. Top-3-Risikobereiche" in line or "## 5. Top-3 Risikobereiche" in line:
                in_table = True
                continue
            if in_table and line.strip().startswith("|") and "---" not in line and "Rang" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4 and parts[1].isdigit():
                    subsys = parts[2].strip("*").strip()
                    risk = parts[3].strip()
                    if subsys and risk:
                        results.append((subsys, risk))
            if in_table and line.strip() == "" and results:
                break
        return results if results else _TOP_RISKS_FALLBACK
    except Exception:
        return _TOP_RISKS_FALLBACK


_TOP_RISKS_FALLBACK = [
    ("RAG", "ChromaDB Netzwerk-Fehler nicht getestet; optional dependency"),
    ("Debug/EventBus", "Drift: Neuer EventType ohne Registry/Timeline"),
    ("Startup/Bootstrap", "Ollama nicht erreichbar nicht getestet; degraded_mode nur RAG"),
]

def get_top_risks() -> list[tuple[str, str]]:
    """Liefert Top-3-Risiken aus Risk Radar (geparst oder Fallback)."""
    return _parse_top_risks_from_radar()


TOP_RISKS = get_top_risks()  # Für Cockpit-Import


# --- Marker-Disziplin ---

DOMAIN_MARKER_MAP = {
    "contracts": "contract",
    "async_behavior": "async_behavior",
    "failure_modes": "failure_mode",
    "cross_layer": "cross_layer",
    "startup": "startup",
    "meta": "contract",  # Meta-Tests nutzen contract
    "chaos": "chaos",
}


def check_marker_discipline() -> list[tuple[str, str, bool]]:
    """
    Prüft: Hat jede Testdatei in spezialisierten Domänen den erwarteten Marker?

    Returns: Liste von (rel_path, expected_marker, has_marker)
    """
    results = []
    for domain, expected_marker in DOMAIN_MARKER_MAP.items():
        domain_path = TESTS_DIR / domain
        if not domain_path.exists():
            continue
        marker_str = f"@pytest.mark.{expected_marker}"
        for py_file in sorted(domain_path.glob("test_*.py")):
            content = py_file.read_text(encoding="utf-8")
            has_marker = marker_str in content
            rel = str(py_file.relative_to(PROJECT_ROOT))
            results.append((rel, expected_marker, has_marker))
    return results


def get_marker_violations() -> list[tuple[str, str]]:
    """Dateien ohne erwarteten Marker."""
    return [
        (rel, marker)
        for rel, marker, has_marker in check_marker_discipline()
        if not has_marker
    ]


# --- EventType-Coverage ---

def check_event_type_coverage() -> dict:
    """
    Prüft EventType-Abdeckung: Registry, Timeline, Drift-Tests.

    Returns: dict mit event_types, registry_ok, timeline_ok, drift_tests_ok
    """
    try:
        from app.debug.agent_event import EventType
        from tests.contracts.event_type_registry import EVENT_TYPE_CONTRACT
    except ImportError as e:
        return {"error": str(e)}

    event_types = [et.name for et in EventType]
    registry_ok = all(et in EVENT_TYPE_CONTRACT for et in EventType)
    registry_missing = [et.name for et in EventType if et not in EVENT_TYPE_CONTRACT]

    # Timeline: event_timeline_view type_map
    try:
        from app.gui.domains.runtime_debug.panels.event_timeline_view import _event_display_text
        from app.debug.agent_event import AgentEvent
        from datetime import datetime, timezone

        timeline_ok = True
        timeline_missing = []
        for et in EventType:
            ev = AgentEvent(agent_name="x", event_type=et, message="")
            text = _event_display_text(ev)
            if not text or not isinstance(text, str):
                timeline_ok = False
                timeline_missing.append(et.name)
    except Exception as e:
        timeline_ok = False
        timeline_missing = [f"Import/Error: {e}"]

    return {
        "event_types": event_types,
        "count": len(event_types),
        "registry_ok": registry_ok,
        "registry_missing": registry_missing,
        "timeline_ok": timeline_ok,
        "timeline_missing": timeline_missing,
    }


# --- Regression-Coverage ---

# Fehlerklassen aus REGRESSION_CATALOG (manuell gepflegt, stabil)
ERROR_CLASSES = [
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
]


def parse_regression_catalog() -> dict[str, list[str]]:
    """
    Liest docs/qa/governance/REGRESSION_CATALOG.md und extrahiert Fehlerklasse -> Domänen/Dateien.

    Returns: {error_class_id: [domain/file, ...]}
    """
    catalog_path = GOVERNANCE / "REGRESSION_CATALOG.md"
    if not catalog_path.exists():
        return {ec: [] for ec in ERROR_CLASSES}

    content = catalog_path.read_text(encoding="utf-8")
    coverage: dict[str, list[str]] = {ec: [] for ec in ERROR_CLASSES}

    in_zuordnung = False
    current_domain = ""
    for line in content.splitlines():
        if "## Zuordnung" in line:
            in_zuordnung = True
        if in_zuordnung and line.strip().startswith("### "):
            # ### failure_modes/ -> failure_modes
            current_domain = line.strip()[4:].rstrip("/").strip()
        if in_zuordnung and "|" in line and "Fehlerklasse" not in line and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                fehlerklasse_raw = parts[3].strip().strip("`")
                if not fehlerklasse_raw or fehlerklasse_raw in ("–", "-"):
                    continue
                datei = parts[1].strip() if len(parts) > 1 else "?"
                ref = f"{current_domain}/{datei}" if current_domain else datei
                for ec_raw in fehlerklasse_raw.split(","):
                    ec = ec_raw.strip().strip("`").split(" ")[0].split("(")[0]
                    if ec in coverage and ref not in coverage[ec]:
                        coverage[ec].append(ref)

    return coverage


def check_regression_coverage() -> dict:
    """
    Prüft Regression-Coverage aus dem Catalog.

    Returns: {covered: [...], partial: [...], open: [...], by_class: {...}}
    """
    coverage = parse_regression_catalog()
    covered = [ec for ec in ERROR_CLASSES if len(coverage.get(ec, [])) >= 1]
    open_classes = [ec for ec in ERROR_CLASSES if len(coverage.get(ec, [])) == 0]

    return {
        "error_classes": ERROR_CLASSES,
        "covered": covered,
        "open": open_classes,
        "by_class": coverage,
        "covered_count": len(covered),
        "open_count": len(open_classes),
        "total": len(ERROR_CLASSES),
    }
