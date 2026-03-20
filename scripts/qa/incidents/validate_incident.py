#!/usr/bin/env python3
"""
QA Incident Replay – Validator für incident.yaml, replay.yaml, bindings.json.

Validiert:
- Schema (JSON Schema)
- Lifecycle (Statusübergänge)
- Konsistenz zwischen Dateien

Output: OK | WARN | ERROR
Exit-Codes: 0=OK, 1=WARN, 2=ERROR

Fehlerklassen:
- SCHEMA_ERROR, MISSING_FIELD, INVALID_STATUS_TRANSITION
- CONSISTENCY_ERROR, UNKNOWN_VALUE, FILE_MISSING
- LIFECYCLE_VIOLATION, PATTERN_VIOLATION
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Projekt-Root: scripts/qa/incidents/ -> Projekt-Root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SCHEMA_DIR = _PROJECT_ROOT / "docs" / "qa" / "incidents" / "_schema"

# Fehlerklassen
SCHEMA_ERROR = "SCHEMA_ERROR"
MISSING_FIELD = "MISSING_FIELD"
INVALID_STATUS_TRANSITION = "INVALID_STATUS_TRANSITION"
CONSISTENCY_ERROR = "CONSISTENCY_ERROR"
UNKNOWN_VALUE = "UNKNOWN_VALUE"
FILE_MISSING = "FILE_MISSING"
LIFECYCLE_VIOLATION = "LIFECYCLE_VIOLATION"
PATTERN_VIOLATION = "PATTERN_VIOLATION"

# Erlaubte Incident-Statusübergänge (von -> [nach])
INCIDENT_TRANSITIONS: dict[str, list[str]] = {
    "new": ["triaged", "invalid", "duplicate"],
    "triaged": ["classified", "invalid", "duplicate"],
    "classified": ["replay_defined", "invalid", "duplicate", "archived"],
    "replay_defined": ["replay_verified", "invalid", "duplicate", "archived"],
    "replay_verified": ["bound_to_regression", "invalid", "duplicate", "archived"],
    "bound_to_regression": ["closed", "archived"],
    "closed": ["archived"],
    "invalid": ["archived"],
    "duplicate": ["archived"],
    "archived": [],
}

# Allowed Values
INCIDENT_STATUS_VALUES = list(INCIDENT_TRANSITIONS.keys())
SEVERITY_VALUES = ["blocker", "critical", "high", "medium", "low", "cosmetic"]
PRIORITY_VALUES = ["P0", "P1", "P2", "P3"]
FAILURE_CLASS_VALUES = [
    "ui_state_drift", "async_race", "late_signal_use_after_destroy",
    "request_context_loss", "rag_silent_failure", "debug_false_truth",
    "startup_ordering", "degraded_mode_failure", "contract_schema_drift",
    "metrics_false_success", "tool_failure_visibility", "optional_dependency_missing",
]
REPRODUCIBILITY_VALUES = ["always", "intermittent", "once", "unknown", "requires_specific_state"]
RUNTIME_LAYER_VALUES = [
    "ui", "service", "persistence", "integration", "startup",
    "observability", "cross_layer", "other",
]
REPLAY_STATUS_VALUES = ["draft", "validated", "test_bound", "guarded", "obsolete"]
BINDING_STATUS_VALUES = ["proposed", "validated", "catalog_bound", "rejected", "archived"]


@dataclass
class ValidationIssue:
    """Einzelne Validierungsmeldung."""

    code: str
    message: str
    path: str | None = None
    is_error: bool = True


@dataclass
class ValidationResult:
    """Gesamtergebnis der Validierung."""

    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def add_error(self, code: str, message: str, path: str | None = None) -> None:
        self.errors.append(ValidationIssue(code=code, message=message, path=path, is_error=True))

    def add_warning(self, code: str, message: str, path: str | None = None) -> None:
        self.warnings.append(ValidationIssue(code=code, message=message, path=path, is_error=False))

    def output_status(self) -> str:
        if self.has_errors:
            return "ERROR"
        if self.has_warnings:
            return "WARN"
        return "OK"

    def exit_code(self) -> int:
        if self.has_errors:
            return 2
        if self.has_warnings:
            return 1
        return 0


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


def _validate_incident_schema(incident: dict, result: ValidationResult) -> None:
    """Schema-Validierung incident.yaml via jsonschema."""
    try:
        import jsonschema
        import yaml
    except ImportError:
        result.add_warning(SCHEMA_ERROR, "jsonschema oder pyyaml nicht installiert – Schema-Skip")
        return

    schema_path = _SCHEMA_DIR / "incident.schema.yaml"
    if not schema_path.exists():
        result.add_warning(SCHEMA_ERROR, f"Schema nicht gefunden: {schema_path}")
        return

    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    if not schema:
        return

    try:
        jsonschema.validate(instance=incident, schema=schema)
    except jsonschema.ValidationError as e:
        path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else None
        result.add_error(SCHEMA_ERROR, str(e.message), path=path)


def _validate_replay_schema(replay: dict, result: ValidationResult) -> None:
    """Schema-Validierung replay.yaml via jsonschema."""
    try:
        import jsonschema
        import yaml
    except ImportError:
        result.add_warning(SCHEMA_ERROR, "jsonschema oder pyyaml nicht installiert – Schema-Skip")
        return

    schema_path = _SCHEMA_DIR / "replay.schema.yaml"
    if not schema_path.exists():
        result.add_warning(SCHEMA_ERROR, f"Schema nicht gefunden: {schema_path}")
        return

    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    if not schema:
        return

    try:
        jsonschema.validate(instance=replay, schema=schema)
    except jsonschema.ValidationError as e:
        path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else None
        result.add_error(SCHEMA_ERROR, str(e.message), path=path)


def _validate_bindings_schema(bindings: dict, result: ValidationResult) -> None:
    """Schema-Validierung bindings.json via jsonschema."""
    try:
        import jsonschema
    except ImportError:
        result.add_warning(SCHEMA_ERROR, "jsonschema nicht installiert – Schema-Skip")
        return

    schema_path = _SCHEMA_DIR / "bindings.schema.json"
    if not schema_path.exists():
        result.add_warning(SCHEMA_ERROR, f"Schema nicht gefunden: {schema_path}")
        return

    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        jsonschema.validate(instance=bindings, schema=schema)
    except jsonschema.ValidationError as e:
        path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else None
        result.add_error(SCHEMA_ERROR, str(e.message), path=path)


def _validate_incident_lifecycle(
    incident: dict,
    result: ValidationResult,
    *,
    previous_status: str | None = None,
) -> None:
    """Lifecycle-Validierung: Pflichtfelder je Status, Statusübergänge."""
    qa = incident.get("qa") or {}
    status = qa.get("status")
    if not status:
        result.add_error(MISSING_FIELD, "qa.status fehlt", path="qa.status")
        return

    if status not in INCIDENT_STATUS_VALUES:
        result.add_error(UNKNOWN_VALUE, f"qa.status '{status}' nicht erlaubt", path="qa.status")
        return

    # Pflichtfelder je Status
    if status == "duplicate":
        dup = qa.get("duplicate_of")
        if not dup or not dup.strip():
            result.add_error(LIFECYCLE_VIOLATION, "status=duplicate erfordert qa.duplicate_of (INC-xxx)")
    elif status in ("invalid", "archived"):
        reason = qa.get("status_reason")
        if not reason or not str(reason).strip():
            result.add_warning(LIFECYCLE_VIOLATION, f"status={status} sollte qa.status_reason oder notes.md haben")
    elif status == "closed":
        res = incident.get("resolution") or {}
        if not res.get("fix") or not res.get("verified"):
            result.add_warning(LIFECYCLE_VIOLATION, "status=closed sollte resolution.fix und resolution.verified haben")
    elif status == "triaged":
        cls = incident.get("classification") or {}
        if not cls.get("severity") or not cls.get("priority"):
            result.add_error(MISSING_FIELD, "status=triaged erfordert classification.severity und priority")
    elif status == "classified":
        cls = incident.get("classification") or {}
        if not cls.get("failure_class") or not cls.get("subsystem"):
            result.add_error(MISSING_FIELD, "status=classified erfordert classification.failure_class und subsystem")

    # Statusübergang prüfen (status_history oder CLI-Argument previous_status)
    prev = previous_status
    if not prev:
        status_history = qa.get("status_history") or []
        if status_history:
            last = status_history[-1]
            prev = last if isinstance(last, str) else (last.get("status") if isinstance(last, dict) else None)
    if prev and prev in INCIDENT_TRANSITIONS:
        _validate_status_transition(prev, status, result)

    # Allowed Values für classification
    cls = incident.get("classification") or {}
    if cls.get("severity") and cls["severity"] not in SEVERITY_VALUES:
        result.add_error(UNKNOWN_VALUE, f"severity '{cls['severity']}' nicht erlaubt", path="classification.severity")
    if cls.get("priority") and cls["priority"] not in PRIORITY_VALUES:
        result.add_error(UNKNOWN_VALUE, f"priority '{cls['priority']}' nicht erlaubt", path="classification.priority")
    if cls.get("failure_class") and cls["failure_class"] not in FAILURE_CLASS_VALUES:
        result.add_error(UNKNOWN_VALUE, f"failure_class '{cls['failure_class']}' nicht erlaubt", path="classification.failure_class")
    if incident.get("behavior", {}).get("reproducibility") and incident["behavior"]["reproducibility"] not in REPRODUCIBILITY_VALUES:
        result.add_error(UNKNOWN_VALUE, f"reproducibility nicht erlaubt", path="behavior.reproducibility")
    env = incident.get("environment") or {}
    if env.get("runtime_layer") and env["runtime_layer"] not in RUNTIME_LAYER_VALUES:
        result.add_error(UNKNOWN_VALUE, f"runtime_layer '{env['runtime_layer']}' nicht erlaubt", path="environment.runtime_layer")


def _validate_replay_lifecycle(replay: dict, result: ValidationResult) -> None:
    """Lifecycle-Validierung replay.yaml."""
    ver = replay.get("verification") or {}
    status = ver.get("status")
    if not status:
        result.add_error(MISSING_FIELD, "verification.status fehlt", path="verification.status")
        return
    if status not in REPLAY_STATUS_VALUES:
        result.add_error(UNKNOWN_VALUE, f"verification.status '{status}' nicht erlaubt", path="verification.status")


def _validate_bindings_lifecycle(bindings: dict, result: ValidationResult) -> None:
    """Lifecycle-Validierung bindings.json."""
    status_obj = bindings.get("status") or {}
    bs = status_obj.get("binding_status")
    if not bs:
        result.add_error(MISSING_FIELD, "status.binding_status fehlt", path="status.binding_status")
        return
    if bs not in BINDING_STATUS_VALUES:
        result.add_error(UNKNOWN_VALUE, f"binding_status '{bs}' nicht erlaubt", path="status.binding_status")


def _validate_consistency(
    incident: dict | None,
    replay: dict | None,
    bindings: dict | None,
    incident_dir: Path,
    result: ValidationResult,
    *,
    project_root: Path | None = None,
) -> None:
    """Konsistenz zwischen incident.yaml, replay.yaml, bindings.json."""
    if not incident:
        return

    inc_id = (incident.get("identity") or {}).get("id")
    qa_status = (incident.get("qa") or {}).get("status")
    qa_replay_id = (incident.get("qa") or {}).get("replay_id")
    cls = incident.get("classification") or {}
    severity = cls.get("severity")

    # C3: replay_defined erfordert replay.yaml
    if qa_status == "replay_defined":
        replay_path = incident_dir / "replay.yaml"
        if not replay_path.exists() or not replay:
            result.add_error(FILE_MISSING, "status=replay_defined erfordert replay.yaml")
        elif replay:
            rep_inc_id = (replay.get("identity") or {}).get("incident_id")
            if inc_id and rep_inc_id and inc_id != rep_inc_id:
                result.add_error(CONSISTENCY_ERROR, f"incident_id stimmt nicht: incident={inc_id} vs replay={rep_inc_id}")

    # C4: replay_verified erfordert replay verification.status = validated
    if qa_status == "replay_verified" and replay:
        rep_status = (replay.get("verification") or {}).get("status")
        if rep_status != "validated":
            result.add_error(CONSISTENCY_ERROR, f"status=replay_verified erfordert replay verification.status=validated, ist: {rep_status}")

    # C7, C8: bound_to_regression erfordert bindings.json mit regression_test
    if qa_status == "bound_to_regression":
        bindings_path = incident_dir / "bindings.json"
        if not bindings_path.exists() or not bindings:
            result.add_error(FILE_MISSING, "status=bound_to_regression erfordert bindings.json")
        elif bindings:
            reg_test = (bindings.get("regression_catalog") or {}).get("regression_test")
            if not reg_test or not str(reg_test).strip():
                result.add_error(LIFECYCLE_VIOLATION, "status=bound_to_regression erfordert regression_catalog.regression_test")

    # C1, C6: incident_id überall identisch
    if replay and inc_id:
        rep_inc_id = (replay.get("identity") or {}).get("incident_id")
        if rep_inc_id and inc_id != rep_inc_id:
            result.add_error(CONSISTENCY_ERROR, f"incident_id inkonsistent: incident={inc_id} vs replay={rep_inc_id}")
    if bindings and inc_id:
        bind_inc_id = (bindings.get("identity") or {}).get("incident_id")
        if bind_inc_id and inc_id != bind_inc_id:
            result.add_error(CONSISTENCY_ERROR, f"incident_id inkonsistent: incident={inc_id} vs bindings={bind_inc_id}")

    # C2: qa.replay_id = replay identity.id
    if replay and qa_replay_id:
        rep_id = (replay.get("identity") or {}).get("id")
        if rep_id and qa_replay_id != rep_id:
            result.add_error(CONSISTENCY_ERROR, f"replay_id inkonsistent: qa.replay_id={qa_replay_id} vs replay.id={rep_id}")

    # C9: failure_class übereinstimmend
    if bindings and cls.get("failure_class"):
        bind_fc = (bindings.get("regression_catalog") or {}).get("failure_class")
        if bind_fc and cls["failure_class"] != bind_fc:
            result.add_error(CONSISTENCY_ERROR, f"failure_class inkonsistent: incident={cls['failure_class']} vs bindings={bind_fc}")

    # C10: severity blocker/critical -> control_center sichtbar
    if severity in ("blocker", "critical") and bindings:
        cc = bindings.get("control_center") or {}
        if cc.get("included") is False:
            result.add_warning(CONSISTENCY_ERROR, "severity blocker/critical sollte im Control Center sichtbar sein (control_center.included=true)")

    # C11: binding_status catalog_bound nur bei bound_to_regression oder closed
    if bindings:
        bs = (bindings.get("status") or {}).get("binding_status")
        if bs == "catalog_bound" and qa_status not in ("bound_to_regression", "closed"):
            result.add_error(CONSISTENCY_ERROR, f"binding_status=catalog_bound nur bei incident status bound_to_regression/closed, ist: {qa_status}")

    # C14: regression_test bei catalog_bound muss auf existierenden Test verweisen
    if bindings and (bindings.get("status") or {}).get("binding_status") == "catalog_bound":
        reg_test = (bindings.get("regression_catalog") or {}).get("regression_test")
        if reg_test and project_root:
            # Test-Pfad kann tests/foo.py::test_bar oder tests/foo.py sein
            test_path = str(reg_test).split("::")[0].strip()
            full_path = project_root / test_path
            if not full_path.exists():
                result.add_warning(FILE_MISSING, f"regression_test verweist auf nicht existierende Datei: {test_path}")


def _validate_status_transition(previous_status: str, current_status: str, result: ValidationResult) -> None:
    """Prüft ob der Statusübergang previous_status → current_status erlaubt ist."""
    if previous_status not in INCIDENT_TRANSITIONS:
        return
    allowed = INCIDENT_TRANSITIONS[previous_status]
    if current_status not in allowed:
        result.add_error(
            INVALID_STATUS_TRANSITION,
            f"Ungültiger Übergang: {previous_status} → {current_status}. Erlaubt: {allowed}",
        )


def validate_incident_dir(
    incident_dir: Path,
    *,
    previous_status: str | None = None,
) -> ValidationResult:
    """
    Validiert ein Incident-Verzeichnis (incident.yaml, replay.yaml, bindings.json).

    Args:
        incident_dir: Pfad zum Incident-Verzeichnis (z.B. docs/qa/incidents/INC-20260315-001)
        previous_status: Optional vorheriger Status für Übergangsvalidierung (z.B. aus Git)

    Returns:
        ValidationResult mit errors und warnings
    """
    result = ValidationResult()
    incident_dir = Path(incident_dir).resolve()

    incident_path = incident_dir / "incident.yaml"
    replay_path = incident_dir / "replay.yaml"
    bindings_path = incident_dir / "bindings.json"

    if not incident_path.exists():
        result.add_error(FILE_MISSING, f"incident.yaml nicht gefunden: {incident_path}")
        return result

    incident = _load_yaml(incident_path)
    if not incident:
        result.add_error(SCHEMA_ERROR, "incident.yaml konnte nicht geladen werden")
        return result

    replay = _load_yaml(replay_path) if replay_path.exists() else None
    bindings = _load_json(bindings_path) if bindings_path.exists() else None

    # Schema-Validierung
    _validate_incident_schema(incident, result)
    if replay:
        _validate_replay_schema(replay, result)
    if bindings:
        _validate_bindings_schema(bindings, result)

    # Lifecycle
    _validate_incident_lifecycle(incident, result, previous_status=previous_status)
    if replay:
        _validate_replay_lifecycle(replay, result)
    if bindings:
        _validate_bindings_lifecycle(bindings, result)

    # Konsistenz
    _validate_consistency(incident, replay, bindings, incident_dir, result, project_root=_PROJECT_ROOT)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validiert incident.yaml, replay.yaml, bindings.json eines QA Incidents."
    )
    parser.add_argument(
        "incident_dir",
        type=Path,
        help="Pfad zum Incident-Verzeichnis (z.B. docs/qa/incidents/INC-20260315-001)",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Nur Status ausgeben, keine Details",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Alle Meldungen ausgeben",
    )
    parser.add_argument(
        "--from-status",
        type=str,
        metavar="STATUS",
        help="Vorheriger Status für Übergangsvalidierung (z.B. aus Git-Diff)",
    )
    args = parser.parse_args()

    incident_dir = args.incident_dir
    if not incident_dir.is_absolute():
        incident_dir = (Path.cwd() / incident_dir).resolve()

    if not incident_dir.is_dir():
        print(f"ERROR: Verzeichnis nicht gefunden: {incident_dir}", file=sys.stderr)
        return 2

    result = validate_incident_dir(incident_dir, previous_status=args.from_status)
    status = result.output_status()

    if not args.quiet:
        for e in result.errors:
            print(f"ERROR [{e.code}]: {e.message}" + (f" (path: {e.path})" if e.path else ""), file=sys.stderr)
        for w in result.warnings:
            if args.verbose:
                print(f"WARN  [{w.code}]: {w.message}" + (f" (path: {w.path})" if w.path else ""), file=sys.stderr)

    print(status)
    return result.exit_code()


if __name__ == "__main__":
    sys.exit(main())
