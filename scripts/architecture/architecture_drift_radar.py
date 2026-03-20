#!/usr/bin/env python3
"""
Architecture Drift Radar – Linux Desktop Chat.

Konsolidiert Architektur-Governance-Signale aus pytest und erzeugt
strukturierte JSON- und Markdown-Reports.

Verwendung:
  python scripts/architecture/architecture_drift_radar.py
  python scripts/architecture/architecture_drift_radar.py --json-only

Ausgabe:
  docs/04_architecture/ARCHITECTURE_DRIFT_RADAR.json
  docs/04_architecture/ARCHITECTURE_DRIFT_RADAR_STATUS.md
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Projekt-Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Kanonischer Pfad: docs/04_architecture (siehe DOCS_ARCHITECTURE_PATH_DECISION.md)
DOCS_ARCH = PROJECT_ROOT / "docs" / "04_architecture"
DRIFT_RADAR_STATUS_MD = DOCS_ARCH / "ARCHITECTURE_DRIFT_RADAR_STATUS.md"
TESTS_ARCH = PROJECT_ROOT / "tests" / "architecture"

# Mapping: Test-Datei-Pattern → Drift-Kategorie
TEST_TO_DRIFT_CATEGORY = {
    "test_app_package_guards": ["layer_drift", "entrypoint_drift"],
    "test_gui_governance_guards": ["layer_drift"],
    "test_gui_domain_dependency_guards": ["gui_domain_drift"],
    "test_service_governance_guards": ["layer_drift"],
    "test_startup_governance_guards": ["startup_drift", "entrypoint_drift"],
    "test_registry_governance_guards": ["registry_drift"],
    "test_provider_orchestrator_governance_guards": ["provider_drift", "hardcoding_drift"],
    "test_eventbus_governance_guards": ["event_drift"],
    "test_feature_governance_guards": ["feature_drift"],
}

# Erwartete Governance-Domänen (Policy)
EXPECTED_GOVERNANCE_DOMAINS = frozenset({
    "app_package", "gui", "services", "startup", "registry",
    "provider", "eventbus", "feature",
})

# Erwartete Drift-Kategorien (Policy)
EXPECTED_DRIFT_CATEGORIES = frozenset({
    "layer_drift", "startup_drift", "registry_drift", "provider_drift",
    "event_drift", "entrypoint_drift", "hardcoding_drift", "gui_domain_drift",
    "feature_drift",
})


def _run_pytest() -> tuple[int, str]:
    """Führt pytest tests/architecture -m architecture aus. Returns (exit_code, stdout)."""
    cmd = [
        sys.executable, "-m", "pytest",
        str(TESTS_ARCH),
        "-m", "architecture",
        "--tb=no", "-rA",
    ]
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.returncode, result.stdout + result.stderr


def _parse_pytest_output(stdout: str) -> list[dict]:
    """Parst pytest -rA Ausgabe. Returns Liste von {nodeid, outcome}."""
    results = []
    # Format: "PASSED tests/architecture/test_foo.py::test_bar" (short test summary)
    pattern = re.compile(
        r"^(PASSED|FAILED|SKIPPED|ERROR)\s+(tests/architecture/[^\s]+)$",
        re.MULTILINE,
    )
    for m in pattern.finditer(stdout):
        results.append({
            "nodeid": m.group(2),
            "outcome": m.group(1).lower(),
        })
    return results


def _test_to_categories(nodeid: str) -> list[str]:
    """Mappt Test-NodeID auf Drift-Kategorien."""
    # nodeid: tests/architecture/test_foo.py::test_bar
    parts = nodeid.split("/")
    if len(parts) < 3:
        return []
    filename = parts[-1].split("::")[0]  # test_foo.py
    stem = filename.replace(".py", "")   # test_foo
    return list(TEST_TO_DRIFT_CATEGORY.get(stem, []))


def _check_governance_files() -> dict:
    """Prüft Existenz zentraler Governance-Dateien."""
    expected = [
        ("arch_guard_config", TESTS_ARCH / "arch_guard_config.py"),
        ("policy_eventbus", DOCS_ARCH / "EVENTBUS_GOVERNANCE_POLICY.md"),
        ("policy_provider", DOCS_ARCH / "PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md"),
        ("policy_registry", DOCS_ARCH / "REGISTRY_GOVERNANCE_POLICY.md"),
        ("policy_service", DOCS_ARCH / "SERVICE_GOVERNANCE_POLICY.md"),
        ("policy_startup", DOCS_ARCH / "STARTUP_GOVERNANCE_POLICY.md"),
        ("policy_gui", DOCS_ARCH / "GUI_GOVERNANCE_POLICY.md"),
        ("policy_feature", DOCS_ARCH / "FEATURE_GOVERNANCE_POLICY.md"),
    ]
    status = {}
    for key, path in expected:
        status[key] = path.exists()
    return status


def _build_report(exit_code: int, test_results: list[dict]) -> dict:
    """Erstellt den konsolidierten Radar-Report."""
    passed = sum(1 for r in test_results if r["outcome"] == "passed")
    failed = sum(1 for r in test_results if r["outcome"] == "failed")
    skipped = sum(1 for r in test_results if r["outcome"] == "skipped")
    errors = sum(1 for r in test_results if r["outcome"] == "error")

    # Drift-Kategorien aggregieren
    drift_categories = {cat: {"passed": 0, "failed": 0, "tests": []} for cat in EXPECTED_DRIFT_CATEGORIES}
    failures = []

    for r in test_results:
        cats = _test_to_categories(r["nodeid"])
        for cat in cats:
            if cat in drift_categories:
                if r["outcome"] == "passed":
                    drift_categories[cat]["passed"] += 1
                elif r["outcome"] == "failed":
                    drift_categories[cat]["failed"] += 1
                drift_categories[cat]["tests"].append({
                    "nodeid": r["nodeid"],
                    "outcome": r["outcome"],
                })
        if r["outcome"] == "failed":
            failures.append(r["nodeid"])

    for cat, data in drift_categories.items():
        data["status"] = "ok" if data["failed"] == 0 else "drift"

    governance_files = _check_governance_files()
    missing_governance = [k for k, v in governance_files.items() if not v]

    return {
        "version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_tests": len(test_results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "status": "ok" if failed == 0 and errors == 0 else "drift",
            "pytest_exit_code": exit_code,
        },
        "drift_categories": {
            k: {
                "status": v["status"],
                "passed": v["passed"],
                "failed": v["failed"],
            }
            for k, v in drift_categories.items()
        },
        "failures": failures,
        "governance_files": governance_files,
        "missing_governance": missing_governance,
    }


def _write_json_report(report: dict) -> Path:
    """Schreibt JSON-Report."""
    path = DOCS_ARCH / "ARCHITECTURE_DRIFT_RADAR.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def _write_markdown_report(report: dict) -> Path:
    """Schreibt Markdown-Status-Report."""
    path = DRIFT_RADAR_STATUS_MD
    lines = [
        "# Architecture Drift Radar – Status",
        "",
        f"**Erzeugt:** {report['timestamp']}",
        "",
        "## 1. Zusammenfassung",
        "",
        f"- **Status:** {report['summary']['status'].upper()}",
        f"- **Tests:** {report['summary']['passed']} bestanden, {report['summary']['failed']} fehlgeschlagen",
        f"- **Gesamt:** {report['summary']['total_tests']}",
        "",
        "## 2. Drift-Kategorien",
        "",
        "| Kategorie | Status | Passed | Failed |",
        "|-----------|--------|--------|--------|",
    ]
    for cat, data in report["drift_categories"].items():
        lines.append(f"| {cat} | {data['status']} | {data['passed']} | {data['failed']} |")

    lines.extend([
        "",
        "## 3. Fehlgeschlagene Tests",
        "",
    ])
    if report["failures"]:
        for f in report["failures"]:
            lines.append(f"- `{f}`")
    else:
        lines.append("Keine.")

    lines.extend([
        "",
        "## 4. Governance-Dateien",
        "",
    ])
    if report.get("missing_governance"):
        lines.append("Fehlend: " + ", ".join(report["missing_governance"]))
    else:
        lines.append("Alle erwarteten Governance-Dateien vorhanden.")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Architecture Drift Radar")
    parser.add_argument("--json-only", action="store_true", help="Nur JSON ausgeben, kein Markdown")
    args = parser.parse_args()

    exit_code, stdout = _run_pytest()
    test_results = _parse_pytest_output(stdout)
    report = _build_report(exit_code, test_results)

    _write_json_report(report)
    if not args.json_only:
        _write_markdown_report(report)

    status = report["summary"]["status"]
    print(f"Architecture Drift Radar: {status.upper()}")
    print(f"  Tests: {report['summary']['passed']} passed, {report['summary']['failed']} failed")
    if report["failures"]:
        for f in report["failures"]:
            print(f"  FAILED: {f}")

    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
