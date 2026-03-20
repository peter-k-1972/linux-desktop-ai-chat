#!/usr/bin/env python3
"""
QA Incident Replay – Registry Builder.

Erzeugt docs/qa/incidents/index.json aus allen Incident-Verzeichnissen.

Aggregiert:
- incident.yaml (Pflicht)
- replay.yaml (optional)
- bindings.json (optional)

Robust: Fehlende optionale Dateien erzeugen nur WARNINGS, kein Abbruch.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Projekt-Root: scripts/qa/incidents/ -> Projekt-Root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_INCIDENTS_DIR = _PROJECT_ROOT / "docs" / "qa" / "incidents"
_INDEX_PATH = _INCIDENTS_DIR / "index.json"

# Warnungsklassen
MISSING_REPLAY = "MISSING_REPLAY"
MISSING_BINDING = "MISSING_BINDING"
UNKNOWN_STATUS = "UNKNOWN_STATUS"
UNKNOWN_FAILURE_CLASS = "UNKNOWN_FAILURE_CLASS"
UNKNOWN_SEVERITY = "UNKNOWN_SEVERITY"
UNKNOWN_SUBSYSTEM = "UNKNOWN_SUBSYSTEM"
PARSE_ERROR = "PARSE_ERROR"
SKIPPED_DIR = "SKIPPED_DIR"

# Allowed Values (für Warnungen)
INCIDENT_STATUS_VALUES = {
    "new", "triaged", "classified", "replay_defined", "replay_verified",
    "bound_to_regression", "closed", "invalid", "duplicate", "archived",
}
FAILURE_CLASS_VALUES = {
    "ui_state_drift", "async_race", "late_signal_use_after_destroy",
    "request_context_loss", "rag_silent_failure", "debug_false_truth",
    "startup_ordering", "degraded_mode_failure", "contract_schema_drift",
    "metrics_false_success", "tool_failure_visibility", "optional_dependency_missing",
}
SEVERITY_VALUES = {"blocker", "critical", "high", "medium", "low", "cosmetic"}
SUBSYSTEM_VALUES = {
    "Chat", "Agentensystem", "Prompt-System", "RAG", "Debug/EventBus",
    "Metrics", "Startup/Bootstrap", "Tools", "Provider/Ollama", "Persistenz/SQLite",
}

# Incident-Verzeichnis-Pattern: INC-YYYYMMDD-NNN, INC-YYYY-NNNN_slug, etc.
INC_DIR_PATTERN = re.compile(
    r"^INC-\d{8}-\d{3}(?:_[a-zA-Z0-9_-]+)?$|^INC-\d{4}-\d{4}(?:_[a-zA-Z0-9_-]+)?$",
    re.IGNORECASE,
)


def _load_yaml(path: Path) -> dict | None:
    """Lädt YAML-Datei."""
    try:
        import yaml
    except ImportError:
        return None
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_json(path: Path) -> dict | None:
    """Lädt JSON-Datei."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _extract_slug(dir_name: str, incident_id: str) -> str:
    """Extrahiert Slug aus Verzeichnisnamen (INC-20260315-001_slug -> slug)."""
    if "_" in dir_name and dir_name.lower().startswith(incident_id.lower() + "_"):
        return dir_name[len(incident_id) + 1 :].strip()
    return ""


def _incident_is_open(status: str) -> bool:
    return status in {"new", "triaged", "classified", "replay_defined", "replay_verified"}


def _incident_is_classified(status: str) -> bool:
    return status in {"classified", "replay_defined", "replay_verified", "bound_to_regression", "closed"}


def _incident_has_replay_defined(status: str) -> bool:
    return status in {"replay_defined", "replay_verified", "bound_to_regression", "closed"}


def _incident_has_replay_verified(status: str) -> bool:
    return status in {"replay_verified", "bound_to_regression", "closed"}


def _incident_is_bound_to_regression(status: str) -> bool:
    return status in {"bound_to_regression", "closed"}


def _extract_incident(
    incident_dir: Path,
    incident: dict,
    replay: dict | None,
    bindings: dict | None,
    warnings: list[dict],
) -> dict:
    """Extrahiert Registry-Felder aus incident, replay, bindings."""
    identity = incident.get("identity") or {}
    classification = incident.get("classification") or {}
    environment = incident.get("environment") or {}
    behavior = incident.get("behavior") or {}
    detection = incident.get("detection") or {}
    qa = incident.get("qa") or {}
    analysis = incident.get("analysis") or {}

    incident_id = identity.get("id") or ""
    status = qa.get("status") or ""
    severity = classification.get("severity") or ""
    failure_class = classification.get("failure_class") or ""
    subsystem = classification.get("subsystem") or ""

    # Warnungen für unbekannte Werte
    if status and status not in INCIDENT_STATUS_VALUES:
        warnings.append({"code": UNKNOWN_STATUS, "incident_id": incident_id, "message": f"status '{status}' unbekannt"})
    if failure_class and failure_class not in FAILURE_CLASS_VALUES:
        warnings.append({"code": UNKNOWN_FAILURE_CLASS, "incident_id": incident_id, "message": f"failure_class '{failure_class}' unbekannt"})
    if severity and severity not in SEVERITY_VALUES:
        warnings.append({"code": UNKNOWN_SEVERITY, "incident_id": incident_id, "message": f"severity '{severity}' unbekannt"})
    if subsystem and subsystem not in SUBSYSTEM_VALUES:
        warnings.append({"code": UNKNOWN_SUBSYSTEM, "incident_id": incident_id, "message": f"subsystem '{subsystem}' unbekannt"})

    # Komponente aus affected_components
    affected = analysis.get("affected_components") or []
    component = affected[0] if affected else None

    # regression_required: severity >= medium und kein regression_test
    regression_test = qa.get("regression_test") or (bindings and (bindings.get("regression_catalog") or {}).get("regression_test"))
    reg_required = severity in ("blocker", "critical", "high", "medium") and not bool(regression_test and str(regression_test).strip())

    # replay_status
    replay_status = None
    if replay:
        replay_status = (replay.get("verification") or {}).get("status")

    # binding_status
    binding_status = None
    if bindings:
        binding_status = (bindings.get("status") or {}).get("binding_status")

    # risk_tags: classification.tags + bindings risk_dimensions
    risk_tags = list(classification.get("tags") or [])
    if bindings:
        dims = (bindings.get("risk_radar") or {}).get("risk_dimensions") or []
        risk_tags.extend(d for d in dims if d and d not in risk_tags)

    # autopilot_eligible
    autopilot_eligible = False
    if bindings:
        autopilot_eligible = bool((bindings.get("autopilot") or {}).get("sprint_candidate"))

    # catalog_candidate: replay vorhanden, aber kein regression_test
    catalog_candidate = bool(replay) and not bool(regression_test and str(regression_test).strip()) and status not in ("closed", "invalid", "duplicate", "archived")

    # first_seen_version, last_seen_version (optional in incident)
    first_seen = environment.get("first_seen_version") or incident.get("first_seen_version")
    last_seen = environment.get("last_seen_version") or incident.get("last_seen_version")

    slug = _extract_slug(incident_dir.name, incident_id)

    return {
        "incident_id": incident_id,
        "slug": slug,
        "title": identity.get("title") or "",
        "status": status,
        "severity": severity,
        "priority": classification.get("priority") or "",
        "subsystem": subsystem,
        "component": component,
        "runtime_layer": environment.get("runtime_layer") or "",
        "failure_class": failure_class,
        "reproducibility": behavior.get("reproducibility") or "",
        "regression_required": reg_required,
        "replay_status": replay_status,
        "binding_status": binding_status,
        "detected_at": detection.get("when") or "",
        "first_seen_version": first_seen,
        "last_seen_version": last_seen,
        "risk_tags": risk_tags,
        "autopilot_eligible": autopilot_eligible,
        "catalog_candidate": catalog_candidate,
    }


def _build_clusters(incidents: list[dict]) -> dict[str, dict[str, int]]:
    """Baut Cluster-Mappings für failure_class, subsystem, runtime_layer."""
    clusters: dict[str, dict[str, int]] = {
        "failure_class": {},
        "subsystem": {},
        "runtime_layer": {},
    }
    for inc in incidents:
        fc = inc.get("failure_class") or ""
        if fc:
            clusters["failure_class"][fc] = clusters["failure_class"].get(fc, 0) + 1
        ss = inc.get("subsystem") or ""
        if ss:
            clusters["subsystem"][ss] = clusters["subsystem"].get(ss, 0) + 1
        rl = inc.get("runtime_layer") or ""
        if rl:
            clusters["runtime_layer"][rl] = clusters["runtime_layer"].get(rl, 0) + 1
    return clusters


def _build_metrics(incidents: list[dict]) -> dict[str, int]:
    """Baut Metriken."""
    metrics = {
        "open_incidents": 0,
        "classified_incidents": 0,
        "replay_defined": 0,
        "replay_verified": 0,
        "bound_to_regression": 0,
    }
    for inc in incidents:
        status = inc.get("status") or ""
        if _incident_is_open(status):
            metrics["open_incidents"] += 1
        if _incident_is_classified(status):
            metrics["classified_incidents"] += 1
        if _incident_has_replay_defined(status):
            metrics["replay_defined"] += 1
        if _incident_has_replay_verified(status):
            metrics["replay_verified"] += 1
        if _incident_is_bound_to_regression(status):
            metrics["bound_to_regression"] += 1
    return metrics


def _build_registry(incidents_dir: Path) -> dict:
    """Baut die vollständige Registry."""
    warnings: list[dict] = []
    incidents: list[dict] = []

    if not incidents_dir.exists():
        return {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "incident_count": 0,
            "incidents": [],
            "clusters": {"failure_class": {}, "subsystem": {}, "runtime_layer": {}},
            "metrics": {"open_incidents": 0, "classified_incidents": 0, "replay_defined": 0, "replay_verified": 0, "bound_to_regression": 0},
            "warnings": [{"code": PARSE_ERROR, "incident_id": "", "message": f"Incidents-Verzeichnis nicht gefunden: {incidents_dir}"}],
        }

    # Verzeichnisse scannen (exkl. templates, _schema)
    skip_names = {"templates", "_schema", "index.json"}
    subdirs = sorted(
        d for d in incidents_dir.iterdir()
        if d.is_dir() and d.name not in skip_names and INC_DIR_PATTERN.match(d.name)
    )

    for incident_dir in subdirs:
        incident_path = incident_dir / "incident.yaml"
        replay_path = incident_dir / "replay.yaml"
        bindings_path = incident_dir / "bindings.json"

        if not incident_path.exists():
            warnings.append({"code": SKIPPED_DIR, "incident_id": incident_dir.name, "message": f"incident.yaml fehlt in {incident_dir.name}"})
            continue

        incident = _load_yaml(incident_path)
        if not incident:
            warnings.append({"code": PARSE_ERROR, "incident_id": incident_dir.name, "message": f"incident.yaml konnte nicht geladen werden: {incident_dir.name}"})
            continue

        incident_id = (incident.get("identity") or {}).get("id") or incident_dir.name

        replay = _load_yaml(replay_path) if replay_path.exists() else None
        bindings = _load_json(bindings_path) if bindings_path.exists() else None

        # Optionale Dateien: Warnung wenn erwartet
        status = (incident.get("qa") or {}).get("status") or ""
        if status in ("replay_defined", "replay_verified", "bound_to_regression", "closed") and not replay:
            warnings.append({"code": MISSING_REPLAY, "incident_id": incident_id, "message": "replay.yaml fehlt"})
        if status in ("bound_to_regression", "closed") and not bindings:
            warnings.append({"code": MISSING_BINDING, "incident_id": incident_id, "message": "bindings.json fehlt"})

        entry = _extract_incident(incident_dir, incident, replay, bindings, warnings)
        incidents.append(entry)

    clusters = _build_clusters(incidents)
    metrics = _build_metrics(incidents)

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "incident_count": len(incidents),
        "incidents": incidents,
        "clusters": clusters,
        "metrics": metrics,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Erzeugt docs/qa/incidents/index.json aus allen Incident-Verzeichnissen.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=_INDEX_PATH,
        help=f"Pfad zur index.json (default: {_INDEX_PATH})",
    )
    parser.add_argument(
        "-i", "--incidents-dir",
        type=Path,
        default=_INCIDENTS_DIR,
        help=f"Pfad zum Incidents-Verzeichnis (default: {_INCIDENTS_DIR})",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Keine Ausgabe außer Fehlern",
    )
    args = parser.parse_args()

    incidents_dir = args.incidents_dir
    if not incidents_dir.is_absolute():
        incidents_dir = (Path.cwd() / incidents_dir).resolve()

    registry = _build_registry(incidents_dir)

    output_path = args.output
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")

    if not args.quiet:
        print(f"Registry erzeugt: {output_path}")
        print(f"  Incidents: {registry['incident_count']}")
        print(f"  Metriken: open={registry['metrics']['open_incidents']}, classified={registry['metrics']['classified_incidents']}")
        if registry['warnings']:
            print(f"  Warnungen: {len(registry['warnings'])}")
            for w in registry["warnings"][:5]:
                print(f"    [{w['code']}] {w['incident_id']}: {w['message']}")
            if len(registry["warnings"]) > 5:
                print(f"    ... und {len(registry['warnings']) - 5} weitere")

    return 0


if __name__ == "__main__":
    sys.exit(main())
