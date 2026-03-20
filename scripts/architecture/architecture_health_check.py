#!/usr/bin/env python3
"""
Architecture Health Check – Linux Desktop Chat.

Schnelle Prüfung des Architekturzustands ohne Volltestlauf.
Bündelt vorhandene Governance-Signale und erzeugt einen Gesamtstatus.

Verwendung:
  python scripts/architecture/architecture_health_check.py
  python scripts/architecture/architecture_health_check.py --json

Ausgabe:
  ARCHITECTURE_HEALTH: OK | WARNING | FAIL
"""

import argparse
import json
import sys
from pathlib import Path

# Projekt-Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_ARCH = PROJECT_ROOT / "docs" / "04_architecture"
TESTS_ARCH = PROJECT_ROOT / "tests" / "architecture"

# Erwartete Governance-Policies (wie Drift-Radar)
EXPECTED_POLICIES = [
    "EVENTBUS_GOVERNANCE_POLICY.md",
    "PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md",
    "REGISTRY_GOVERNANCE_POLICY.md",
    "SERVICE_GOVERNANCE_POLICY.md",
    "STARTUP_GOVERNANCE_POLICY.md",
    "GUI_GOVERNANCE_POLICY.md",
    "FEATURE_GOVERNANCE_POLICY.md",
    "GUI_DOMAIN_DEPENDENCY_POLICY.md",
]

# Kanonische Entrypoints
CANONICAL_ENTRYPOINTS = [
    "run_gui_shell.py",
    "app/__main__.py",
    "main.py",
]

# Mindestanzahl Architektur-Testdateien
MIN_ARCH_TEST_FILES = 8


def _check_baseline() -> tuple[bool, str]:
    """Prüft ob Baseline-Dokument vorhanden."""
    path = DOCS_ARCH / "ARCHITECTURE_BASELINE_2026.md"
    if not path.exists():
        return False, f"Baseline fehlt: {path}"
    return True, "Baseline vorhanden"


def _check_governance_policies() -> tuple[bool, list[str], list[str]]:
    """Prüft ob zentrale Governance-Policies vorhanden sind."""
    missing = []
    present = []
    for name in EXPECTED_POLICIES:
        path = DOCS_ARCH / name
        if path.exists():
            present.append(name)
        else:
            missing.append(name)
    ok = len(missing) == 0
    return ok, present, missing


def _check_arch_guard_config() -> tuple[bool, str]:
    """Prüft ob arch_guard_config importierbar und konsistent ist."""
    path = TESTS_ARCH / "arch_guard_config.py"
    if not path.exists():
        return False, "arch_guard_config.py fehlt"
    try:
        # Import außerhalb des Projektpfads; sys.path anpassen
        import importlib.util
        spec = importlib.util.spec_from_file_location("arch_guard_config", path)
        if spec is None or spec.loader is None:
            return False, "arch_guard_config nicht ladbar"
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        docs_arch = getattr(mod, "DOCS_ARCH", None)
        if docs_arch is None:
            return False, "DOCS_ARCH nicht definiert"
        expected = PROJECT_ROOT / "docs" / "04_architecture"
        if Path(docs_arch) != expected:
            return False, f"DOCS_ARCH zeigt auf {docs_arch}, erwartet {expected}"
        return True, "arch_guard_config konsistent"
    except Exception as e:
        return False, f"arch_guard_config Fehler: {e}"


def _check_entrypoints() -> tuple[bool, list[str], list[str]]:
    """Prüft ob kanonische Entrypoints vorhanden sind."""
    missing = []
    present = []
    for ep in CANONICAL_ENTRYPOINTS:
        path = PROJECT_ROOT / ep
        if path.exists():
            present.append(ep)
        else:
            missing.append(ep)
    ok = len(missing) == 0
    return ok, present, missing


def _check_architecture_tests() -> tuple[bool, int, str]:
    """Prüft ob Architektur-Testdateien vorhanden sind."""
    if not TESTS_ARCH.exists():
        return False, 0, "tests/architecture/ fehlt"
    test_files = [f for f in TESTS_ARCH.glob("test_*.py") if f.name != "__init__.py"]
    count = len(test_files)
    if count < MIN_ARCH_TEST_FILES:
        return False, count, f"Nur {count} Architektur-Tests, mindestens {MIN_ARCH_TEST_FILES} erwartet"
    return True, count, f"{count} Architektur-Testdateien"


def _check_drift_radar_artifacts() -> tuple[str, str]:
    """
    Liest Drift-Radar-JSON falls vorhanden.
    Returns: ("ok"|"drift"|"missing", message)
    """
    path = DOCS_ARCH / "ARCHITECTURE_DRIFT_RADAR.json"
    if not path.exists():
        return "missing", "Drift-Radar-JSON nicht vorhanden (führe architecture_drift_radar.py aus)"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        summary = data.get("summary", {})
        status = summary.get("status", "unknown")
        if status == "ok":
            return "ok", "Drift-Radar: OK"
        if status == "drift":
            failed = summary.get("failed", 0)
            return "drift", f"Drift-Radar: {failed} fehlgeschlagene Tests"
        return "unknown", f"Drift-Radar-Status: {status}"
    except Exception as e:
        return "error", f"Drift-Radar-JSON lesbar: {e}"


def _check_docs_path_consistency() -> tuple[bool, str]:
    """Prüft ob docs/04_architecture existiert und Policies enthält."""
    if not DOCS_ARCH.exists():
        return False, f"docs/04_architecture fehlt: {DOCS_ARCH}"
    policy_count = sum(1 for p in EXPECTED_POLICIES if (DOCS_ARCH / p).exists())
    if policy_count == 0:
        return False, "Keine Governance-Policies in docs/04_architecture"
    return True, f"docs/04_architecture konsistent ({policy_count} Policies)"


def run_health_check() -> dict:
    """Führt alle Checks aus und liefert strukturiertes Ergebnis."""
    results = {}
    failures = []
    warnings = []

    # 1. Baseline
    ok, msg = _check_baseline()
    results["baseline"] = {"ok": ok, "message": msg}
    if not ok:
        failures.append(msg)

    # 2. Governance-Policies
    ok, present, missing = _check_governance_policies()
    results["governance_policies"] = {
        "ok": ok,
        "present": len(present),
        "missing": missing,
        "message": f"{len(present)}/{len(EXPECTED_POLICIES)} Policies" + (
            f", fehlend: {missing}" if missing else ""
        ),
    }
    if not ok:
        failures.append(f"Policies fehlen: {missing}")

    # 3. arch_guard_config
    ok, msg = _check_arch_guard_config()
    results["arch_guard_config"] = {"ok": ok, "message": msg}
    if not ok:
        failures.append(msg)

    # 4. Entrypoints
    ok, present, missing = _check_entrypoints()
    results["entrypoints"] = {
        "ok": ok,
        "present": present,
        "missing": missing,
        "message": f"{len(present)}/{len(CANONICAL_ENTRYPOINTS)} Entrypoints" + (
            f", fehlend: {missing}" if missing else ""
        ),
    }
    if not ok:
        failures.append(f"Entrypoints fehlen: {missing}")

    # 5. Architektur-Tests
    ok, count, msg = _check_architecture_tests()
    results["architecture_tests"] = {"ok": ok, "count": count, "message": msg}
    if not ok:
        failures.append(msg)

    # 6. docs-Pfad
    ok, msg = _check_docs_path_consistency()
    results["docs_path"] = {"ok": ok, "message": msg}
    if not ok:
        failures.append(msg)

    # 7. Drift-Radar (optional, nicht kritisch für FAIL)
    drift_status, drift_msg = _check_drift_radar_artifacts()
    results["drift_radar"] = {"status": drift_status, "message": drift_msg}
    if drift_status == "drift":
        warnings.append(drift_msg)
    elif drift_status == "missing":
        warnings.append(drift_msg)

    # Gesamtstatus
    if failures:
        overall = "FAIL"
    elif warnings:
        overall = "WARNING"
    else:
        overall = "OK"

    return {
        "overall": overall,
        "results": results,
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Architecture Health Check")
    parser.add_argument("--json", action="store_true", help="JSON-Ausgabe")
    args = parser.parse_args()

    report = run_health_check()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"ARCHITECTURE_HEALTH: {report['overall']}")
        print()
        for key, data in report["results"].items():
            status = "✓" if data.get("ok", data.get("status") == "ok") else "✗"
            msg = data.get("message", str(data))
            print(f"  {status} {key}: {msg}")
        if report["failures"]:
            print()
            print("Failures:")
            for f in report["failures"]:
                print(f"  - {f}")
        if report["warnings"]:
            print()
            print("Warnings:")
            for w in report["warnings"]:
                print(f"  - {w}")

    exit_codes = {"OK": 0, "WARNING": 1, "FAIL": 2}
    return exit_codes.get(report["overall"], 2)


if __name__ == "__main__":
    sys.exit(main())
