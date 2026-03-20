#!/usr/bin/env python3
"""
Architecture Map Contract Validator – Linux Desktop Chat.

Prüft die Architecture Map gegen den tatsächlichen Projektzustand.
Die Map wird zum lebenden Architekturvertrag.

Verwendung:
  python scripts/dev/validate_architecture_map.py
  python scripts/dev/validate_architecture_map.py --json

Quelle: docs/04_architecture/ARCHITECTURE_MAP.json
Ausgabe: Terminal-Zusammenfassung, optional JSON-Bericht
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_ARCH = PROJECT_ROOT / "docs" / "04_architecture"
MAP_JSON = DOCS_ARCH / "ARCHITECTURE_MAP.json"


@dataclass
class CheckResult:
    """Ergebnis einer Einzelprüfung."""
    category: str
    item: str
    ok: bool
    message: str = ""


@dataclass
class ValidationReport:
    """Gesamtbericht der Validierung."""
    ok: bool
    total: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    results: list[CheckResult] = field(default_factory=list)

    def add(self, result: CheckResult) -> None:
        self.results.append(result)
        self.total += 1
        if result.ok:
            self.passed += 1
        else:
            self.failed += 1

    def add_warning(self, result: CheckResult) -> None:
        self.results.append(result)
        self.total += 1
        self.warnings += 1


def _load_map() -> dict:
    """Lädt ARCHITECTURE_MAP.json."""
    if not MAP_JSON.exists():
        raise FileNotFoundError(
            f"ARCHITECTURE_MAP.json nicht gefunden: {MAP_JSON}. "
            "Bitte zuerst: python scripts/dev/architecture_map.py --json"
        )
    return json.loads(MAP_JSON.read_text(encoding="utf-8"))


def _resolve_registry_paths(path_str: str) -> list[Path]:
    """Löst kombinierte Registry-Pfade (z.B. 'a, b') in existenzprüfbare Pfade auf."""
    candidates: list[Path] = []
    for part in path_str.split(","):
        part = part.strip()
        if not part:
            continue
        if part.startswith("app/"):
            base = PROJECT_ROOT / part
        elif part.startswith("gui/"):
            base = PROJECT_ROOT / "app" / part
        elif "/" in part:
            base = PROJECT_ROOT / part
        else:
            base = PROJECT_ROOT / "app" / "gui" / "commands" / part
        candidates.append(base)
        if not base.suffix:
            candidates.append(base.with_suffix(".py"))
    return candidates


def _check_registry_path(path_str: str) -> tuple[bool, str]:
    """Prüft ob mindestens ein aufgelöster Registry-Pfad existiert."""
    candidates = _resolve_registry_paths(path_str)
    for c in candidates:
        if c.exists():
            return True, f"OK: {c.relative_to(PROJECT_ROOT)}"
    return False, f"Keiner gefunden für: {path_str}"


def validate_layers(data: dict, report: ValidationReport) -> None:
    """A: Layer-Pfade existieren."""
    for layer in data.get("layers", []):
        path = PROJECT_ROOT / layer["path"].rstrip("/")
        ok = path.is_dir()
        report.add(CheckResult(
            "layers",
            layer["name"],
            ok,
            f"{layer['path']} {'existiert' if ok else 'fehlt'}"
        ))


def validate_domains(data: dict, report: ValidationReport) -> None:
    """B: Domain-Pfade existieren."""
    for domain in data.get("domains", []):
        path = PROJECT_ROOT / domain["path"].rstrip("/")
        ok = path.is_dir()
        report.add(CheckResult(
            "domains",
            domain["name"],
            ok,
            f"{domain['path']} {'existiert' if ok else 'fehlt'}"
        ))


def validate_entrypoints(data: dict, report: ValidationReport) -> None:
    """C: Entrypoint-Pfade existieren."""
    for ep in data.get("entrypoints", {}).get("canonical", []):
        path = PROJECT_ROOT / ep["path"]
        ok = path.exists()
        report.add(CheckResult(
            "entrypoints",
            ep["path"],
            ok,
            f"{ep['path']} {'existiert' if ok else 'fehlt'}"
        ))
    for ep in data.get("entrypoints", {}).get("legacy", []):
        path = PROJECT_ROOT / ep["path"]
        ok = path.exists()
        report.add(CheckResult(
            "entrypoints_legacy",
            ep["path"],
            ok,
            f"{ep['path']} {'existiert' if ok else 'fehlt'}"
        ))


def validate_registries(data: dict, report: ValidationReport) -> None:
    """D: Registry-Pfade existieren (robust bei kombinierten Angaben)."""
    for reg in data.get("registries", []):
        path_str = reg.get("path", "")
        ok, msg = _check_registry_path(path_str)
        report.add(CheckResult(
            "registries",
            reg["name"],
            ok,
            msg
        ))


def validate_services(data: dict, report: ValidationReport) -> None:
    """E: Referenzierte Services existieren als Modul."""
    for name in data.get("services", []):
        path = PROJECT_ROOT / "app" / "services" / f"{name}.py"
        ok = path.is_file()
        report.add(CheckResult(
            "services",
            name,
            ok,
            f"app/services/{name}.py {'existiert' if ok else 'fehlt'}"
        ))


def validate_governance(data: dict, report: ValidationReport) -> None:
    """F: Policy-Dateien und Tests existieren."""
    for block in data.get("governance_blocks", []):
        policy = block.get("policy", "")
        test_name = block.get("test", "")

        policy_path = DOCS_ARCH / policy if not policy.startswith("/") else Path(policy)
        if not policy_path.exists() and not policy.endswith(".md"):
            policy_path = DOCS_ARCH / f"{policy}.md"
        policy_ok = policy_path.exists()

        test_path = PROJECT_ROOT / "tests" / "architecture" / f"{test_name}.py"
        test_ok = test_path.exists()

        report.add(CheckResult(
            "governance",
            block["block"],
            policy_ok and test_ok,
            f"policy={policy_ok}, test={test_ok}"
        ))


def validate_legacy_transitional(data: dict, report: ValidationReport) -> None:
    """G: Legacy-/Übergangspfade sind plausibel."""
    lt = data.get("legacy_transitional", {})
    temp = lt.get("temporarily_allowed_root", [])
    for f in temp:
        path = PROJECT_ROOT / "app" / f
        ok = path.is_file()
        report.add(CheckResult(
            "legacy_transitional",
            f"app/{f}",
            ok,
            f"{'existiert' if ok else 'fehlt'} (temporär erlaubt)"
        ))
    archive_legacy = PROJECT_ROOT / "archive" / "run_legacy_gui.py"
    report.add(CheckResult(
        "legacy_transitional",
        "archive/run_legacy_gui.py",
        archive_legacy.exists(),
        "Legacy-Entrypoint"
    ))


def validate_map_not_empty(data: dict, report: ValidationReport) -> None:
    """H: Map ist nicht veraltet oder leer."""
    has_layers = len(data.get("layers", [])) >= 4
    has_domains = len(data.get("domains", [])) >= 5
    has_entrypoints = bool(data.get("entrypoints", {}).get("canonical"))
    has_governance = len(data.get("governance_blocks", [])) >= 5
    ok = has_layers and has_domains and has_entrypoints and has_governance
    report.add(CheckResult(
        "map_structure",
        "map_not_trivial",
        ok,
        f"layers={len(data.get('layers', []))}, domains={len(data.get('domains', []))}, "
        f"entrypoints={len(data.get('entrypoints', {}).get('canonical', []))}, "
        f"governance={len(data.get('governance_blocks', []))}"
    ))


def run_validation(data: dict) -> ValidationReport:
    """Führt alle Prüfungen aus."""
    report = ValidationReport(ok=True)
    validate_layers(data, report)
    validate_domains(data, report)
    validate_entrypoints(data, report)
    validate_registries(data, report)
    validate_services(data, report)
    validate_governance(data, report)
    validate_legacy_transitional(data, report)
    validate_map_not_empty(data, report)
    report.ok = report.failed == 0
    return report


def _print_report(report: ValidationReport) -> None:
    """Gibt lesbare Terminal-Zusammenfassung aus."""
    failed = [r for r in report.results if not r.ok]
    if failed:
        print("FAIL – Architecture Map Contract Validierung")
        print("=" * 50)
        for r in failed:
            print(f"  [{r.category}] {r.item}: {r.message}")
        print()
    print(f"Ergebnis: {'OK' if report.ok else 'FAIL'}")
    print(f"  Bestanden: {report.passed}/{report.total}")
    if report.failed:
        print(f"  Fehlgeschlagen: {report.failed}")
    if report.warnings:
        print(f"  Warnungen: {report.warnings}")


def _to_json(report: ValidationReport) -> dict:
    """Serialisiert den Bericht als JSON."""
    return {
        "ok": report.ok,
        "total": report.total,
        "passed": report.passed,
        "failed": report.failed,
        "warnings": report.warnings,
        "results": [
            {
                "category": r.category,
                "item": r.item,
                "ok": r.ok,
                "message": r.message,
            }
            for r in report.results
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Architecture Map Contract Validator – prüft Map gegen Projektzustand"
    )
    parser.add_argument("--json", action="store_true", help="JSON-Bericht ausgeben")
    parser.add_argument("--map", type=Path, default=None, help="Alternativer Map-Pfad (für Tests)")
    args = parser.parse_args()

    global MAP_JSON
    if args.map is not None:
        MAP_JSON = args.map

    try:
        data = _load_map()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    report = run_validation(data)

    if args.json:
        out = _to_json(report)
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        _print_report(report)

    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
