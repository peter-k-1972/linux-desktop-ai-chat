#!/usr/bin/env python3
"""
QA Self-Healing Generator – Linux Desktop Chat.

Erkennt Wartungs- und Driftprobleme in der Testsuite und leitet
sinnvolle QA-Wartungsempfehlungen ab.

Checks:
1. Flaky-Risiko-Heuristik
2. Schwache-Test-Heuristik
3. Fehlerklassen-Streuung über Testdomänen
4. QA-Wartungsempfehlungen

Output:
- docs/qa/QA_SELF_HEALING.md
- docs/qa/QA_SELF_HEALING.json

Verwendung:
  python scripts/qa/generate_qa_self_healing.py
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_QA = PROJECT_ROOT / "docs" / "qa"
TESTS_DIR = PROJECT_ROOT / "tests"

# Flaky-Risiko-Signale (Heuristik: erhöhtes Risiko, keine Behauptung)
FLAKY_SIGNALS = [
    (r"@pytest\.mark\.async_behavior", "async_behavior", "Async/Event-Loop-Sensitivität"),
    (r"@pytest\.mark\.chaos", "chaos", "Fault-Injection, Timing-Szenarien"),
    (r"qtbot\.wait\s*\(", "qtbot_wait", "Event-Wait, Timing-abhängig"),
    (r"asyncio\.sleep\s*\(", "asyncio_sleep", "Delay-basiert"),
    (r"TimeoutProviderStub|DelayedProviderStub", "timeout_delay_stub", "Timeout-/Delay-Szenarien"),
    (r"wait_sec|delay_sec", "timeout_delay_param", "Konfigurierbare Verzögerung"),
    (r"destroy|cleanup|teardown", "lifecycle", "Cleanup-/Destroy-Sensitivität"),
]

# Schwache-Test-Signale (Heuristik: möglicherweise zu weich)
WEAK_SIGNALS = [
    (r"assert\s+\w+\s+is\s+not\s+None\b", "assert_not_none", "Nur Existenzprüfung"),
    (r"assert\s+[^=]+\.count\s*\(\s*\)\s*>=\s*1\b", "count_ge_1", "Nur count >= 1"),
    (r"assert\s+[^=]+\.count\s*\(\s*\)\s*>\s*0\b", "count_gt_0", "Nur count > 0"),
    (r"assert\s+[^=]+\.count\s*\(\s*\)\s*>=\s*\d+", "count_ge_n", "Nur count >= N"),
    (r"assert\s+[^=]+\.isVisible\s*\(\s*\)", "assert_isVisible", "Assert nur isVisible"),
]


# Gültige Fehlerklassen-IDs aus REGRESSION_CATALOG (Definitionstabelle)
VALID_ERROR_CLASSES = {
    "ui_state_drift", "async_race", "late_signal_use_after_destroy",
    "request_context_loss", "rag_silent_failure", "debug_false_truth",
    "startup_ordering", "degraded_mode_failure", "contract_schema_drift",
    "metrics_false_success", "tool_failure_visibility", "optional_dependency_missing",
}


def _parse_regression_catalog(path: Path) -> dict[str, set[str]]:
    """Extrahiert Fehlerklasse → Testdomänen aus REGRESSION_CATALOG.md (nur Zuordnung-Tabellen)."""
    result: dict[str, set[str]] = {}
    if not path.exists():
        return result
    content = path.read_text(encoding="utf-8")
    current_domain = ""
    in_zuordnung = True
    for line in content.split("\n"):
        if "## Historische Bugs" in line or "## Erweiterung" in line:
            in_zuordnung = False
        if line.strip().startswith("### ") and "/" in line:
            part = line.split("### ")[-1].strip().rstrip("/")
            current_domain = part
            in_zuordnung = True
            continue
        if not in_zuordnung or not current_domain:
            continue
        if "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p]
            if len(parts) >= 3:
                fehler = parts[2].strip()
                if fehler and fehler not in ("–", "-", "Fehlerklasse"):
                    for fc in re.split(r"[\s,]+", fehler):
                        fc = fc.split("(")[0].strip().lower()
                        if fc in VALID_ERROR_CLASSES:
                            result.setdefault(fc, set()).add(current_domain)
    return result


def _scan_flaky_risks() -> list[dict]:
    """Scannt Tests auf Flaky-Risiko-Signale."""
    findings: list[dict] = []
    for py_path in TESTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_path) or py_path.name == "__init__.py":
            continue
        rel = py_path.relative_to(PROJECT_ROOT)
        try:
            content = py_path.read_text(encoding="utf-8")
        except Exception:
            continue
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern, signal_id, beschreibung in FLAKY_SIGNALS:
                if re.search(pattern, line):
                    # Test-Funktion finden (rückwärts)
                    test_name = ""
                    for j in range(i - 1, max(-1, i - 40), -1):
                        m = re.search(r"(?:async\s+)?def\s+(test_\w+)\s*\(", lines[j])
                        if m:
                            test_name = m.group(1)
                            break
                    findings.append({
                        "datei": str(rel),
                        "zeile": i,
                        "test": test_name or "?",
                        "signal": signal_id,
                        "beschreibung": beschreibung,
                        "snippet": line.strip()[:80],
                    })
                    break  # Pro Zeile nur ein Signal
    return findings


def _scan_weak_tests() -> list[dict]:
    """Scannt Tests auf schwache Assertion-Muster."""
    findings: list[dict] = []
    for py_path in TESTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_path) or py_path.name == "__init__.py":
            continue
        rel = py_path.relative_to(PROJECT_ROOT)
        try:
            content = py_path.read_text(encoding="utf-8")
        except Exception:
            continue
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern, signal_id, beschreibung in WEAK_SIGNALS:
                if re.search(pattern, line):
                    test_name = ""
                    for j in range(i - 1, max(-1, i - 40), -1):
                        m = re.search(r"(?:async\s+)?def\s+(test_\w+)\s*\(", lines[j])
                        if m:
                            test_name = m.group(1)
                            break
                    findings.append({
                        "datei": str(rel),
                        "zeile": i,
                        "test": test_name or "?",
                        "signal": signal_id,
                        "beschreibung": beschreibung,
                        "snippet": line.strip()[:80],
                    })
                    break
    return findings


def _aggregate_flaky_by_test(findings: list[dict]) -> list[dict]:
    """Aggregiert Flaky-Findings pro Test, priorisiert nach Signal-Anzahl."""
    by_key: dict[str, list[dict]] = {}
    for f in findings:
        # Helper-Dateien ohne Testfunktionen (chaos_fixtures) überspringen
        if "chaos_fixtures.py" in f["datei"]:
            continue
        key = f"{f['datei']}::{f['test']}"
        by_key.setdefault(key, []).append(f)
    result = []
    for key, items in sorted(by_key.items(), key=lambda x: -len(x[1])):
        first = items[0]
        result.append({
            "datei": first["datei"],
            "test": first["test"] if first["test"] != "?" else "(mehrere)",
            "anzahl_signale": len(items),
            "signale": list({i["signal"] for i in items}),
            "beschreibung": "; ".join({i["beschreibung"] for i in items}),
        })
    return sorted(result, key=lambda x: -x["anzahl_signale"])


def _aggregate_weak_by_test(findings: list[dict]) -> list[dict]:
    """Aggregiert schwache-Test-Findings pro Test."""
    by_key: dict[str, list[dict]] = {}
    for f in findings:
        key = f"{f['datei']}::{f['test']}"
        by_key.setdefault(key, []).append(f)
    result = []
    for key, items in by_key.items():
        first = items[0]
        signals = list({i["signal"] for i in items})
        result.append({
            "datei": first["datei"],
            "test": first["test"],
            "anzahl_signale": len(items),
            "signale": signals,
            "beschreibung": "; ".join({i["beschreibung"] for i in items}),
        })
    return sorted(result, key=lambda x: -x["anzahl_signale"])


def _analyze_error_class_spread(catalog: dict[str, set[str]]) -> list[dict]:
    """Findet Fehlerklassen mit geringer Streuung (nur 1 Domäne)."""
    result = []
    for fc, domains in catalog.items():
        if len(domains) <= 1:
            result.append({
                "fehlerklasse": fc,
                "domaenen": sorted(domains),
                "anzahl_domaenen": len(domains),
                "bewertung": "Nur eine Domäne" if len(domains) == 1 else "Keine Domäne",
            })
    return sorted(result, key=lambda x: x["anzahl_domaenen"])


def _build_maintenance_recommendations(
    flaky_agg: list[dict],
    weak_agg: list[dict],
    spread_low: list[dict],
) -> list[dict]:
    """Baut Top-5 Wartungsempfehlungen aus allen Checks."""
    recs: list[dict] = []
    seen: set[str] = set()

    # 1. Flaky-Risiko: Tests mit vielen Signalen
    for f in flaky_agg[:3]:
        rec = {
            "prioritaet": len(recs) + 1,
            "typ": "Flaky-Risiko",
            "ziel": f"{f['datei']}::{f['test']}",
            "empfehlung": f"Flaky-Risiko prüfen: {f['beschreibung']}. Keine automatische Änderung – manuell bewerten.",
        }
        if rec["ziel"] not in seen:
            recs.append(rec)
            seen.add(rec["ziel"])

    # 2. Schwache Tests
    for w in weak_agg[:3]:
        key = f"{w['datei']}::{w['test']}"
        if key not in seen:
            recs.append({
                "prioritaet": len(recs) + 1,
                "typ": "Schwacher Test",
                "ziel": key,
                "empfehlung": f"Assertion prüfen: {w['beschreibung']}. Wirkung statt nur Existenz testen?",
            })
            seen.add(key)

    # 3. Fehlerklassen-Streuung
    for s in spread_low[:2]:
        if s["fehlerklasse"] not in seen:
            recs.append({
                "prioritaet": len(recs) + 1,
                "typ": "Geringe Streuung",
                "ziel": s["fehlerklasse"],
                "empfehlung": f"Fehlerklasse nur in {', '.join(s['domaenen']) or 'keiner'} Domäne abgesichert. Zweite Domäne erwägen.",
            })
            seen.add(s["fehlerklasse"])

    return recs[:5]


def run_generator() -> dict:
    """Führt alle Self-Healing-Checks aus."""
    result: dict = {
        "iteration": 1,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "eingabedaten": [],
        "checks": [],
        "flaky_risiken": [],
        "schwache_tests": [],
        "fehlerklassen_geringe_streuung": [],
        "wartungsempfehlungen": [],
        "empfehlung_iteration2": [],
    }

    # Regression Catalog
    catalog_path = DOCS_QA / "REGRESSION_CATALOG.md"
    if catalog_path.exists():
        result["eingabedaten"].append("REGRESSION_CATALOG.md")
    result["eingabedaten"].append("tests/")
    catalog = _parse_regression_catalog(catalog_path)

    # Checks
    result["checks"] = [
        "Flaky-Risiko-Heuristik: async_behavior, chaos, qtbot.wait, asyncio.sleep, timeout/delay, lifecycle",
        "Schwache-Test-Heuristik: assert is not None, count()>=1, nur isVisible",
        "Fehlerklassen-Streuung: pro Fehlerklasse Anzahl Testdomänen aus REGRESSION_CATALOG",
        "QA-Wartungsempfehlungen: Zusammenführung aus allen Checks, Top-5 priorisiert",
    ]

    # Flaky
    flaky_raw = _scan_flaky_risks()
    flaky_agg = _aggregate_flaky_by_test(flaky_raw)
    result["flaky_risiken"] = flaky_agg[:20]  # Top 20

    # Schwache Tests
    weak_raw = _scan_weak_tests()
    weak_agg = _aggregate_weak_by_test(weak_raw)
    result["schwache_tests"] = weak_agg[:20]

    # Streuung
    spread_low = _analyze_error_class_spread(catalog)
    result["fehlerklassen_geringe_streuung"] = spread_low

    # Wartungsempfehlungen
    result["wartungsempfehlungen"] = _build_maintenance_recommendations(
        flaky_agg, weak_agg, spread_low
    )

    # Iteration 2
    result["empfehlung_iteration2"] = [
        {"prioritaet": 1, "schritt": "AST-basierte Assertion-Analyse", "nutzen": "Schwache Tests präziser erkennen"},
        {"prioritaet": 2, "schritt": "Flaky-Historie aus CI-Logs", "nutzen": "Tatsächlich flaky vs. nur Risiko"},
        {"prioritaet": 3, "schritt": "Autopilot-Integration", "nutzen": "Wartungsempfehlungen in Sprint-Planung"},
    ]

    return result


def write_markdown(data: dict) -> str:
    """Erzeugt QA_SELF_HEALING.md Inhalt."""
    lines = [
        "# QA Self-Healing – Linux Desktop Chat",
        "",
        f"**Iteration:** {data['iteration']}  ",
        f"**Generiert:** {data['generated']}  ",
        "**Zweck:** Wartungs- und Driftprobleme in der Testsuite erkennen, daraus sinnvolle QA-Wartungsempfehlungen ableiten.",
        "",
        "---",
        "",
        "## 1. Zweck",
        "",
        "Der QA Self-Healing-Prozess **erkennt** und **diagnostiziert** – nicht automatisch repariert.",
        "",
        "- Erkennung von Flaky-Risiken",
        "- Erkennung potenziell schwacher Tests",
        "- Analyse der Fehlerklassen-Streuung",
        "- Priorisierte Wartungsempfehlungen",
        "",
        "---",
        "",
        "## 2. Verwendete Checks",
        "",
    ]
    for c in data["checks"]:
        lines.append(f"- {c}")
    lines.extend([
        "",
        "---",
        "",
        "## 3. Auffällige Flaky-Risiken",
        "",
        "*(Heuristik: erhöhtes Risiko, keine Behauptung „dieser Test ist flaky“)*",
        "",
        "| Datei | Test | Signale | Beschreibung |",
        "|-------|------|---------|--------------|",
    ])
    for f in data.get("flaky_risiken", [])[:15]:
        b = f.get("beschreibung", "") or ""
        b_short = b[:50] + ("…" if len(b) > 50 else "")
        lines.append(f"| {f['datei']} | {f['test']} | {f['anzahl_signale']} | {b_short} |")
    lines.extend([
        "",
        "---",
        "",
        "## 4. Potenziell schwache Tests",
        "",
        "*(Nur markieren – keine automatische Änderung)*",
        "",
        "| Datei | Test | Signale | Beschreibung |",
        "|-------|------|---------|--------------|",
    ])
    for w in data.get("schwache_tests", [])[:15]:
        b = w.get("beschreibung", "") or ""
        b_short = b[:50] + ("…" if len(b) > 50 else "")
        lines.append(f"| {w['datei']} | {w['test']} | {w['anzahl_signale']} | {b_short} |")
    lines.extend([
        "",
        "---",
        "",
        "## 5. Fehlerklassen mit geringer Streuung",
        "",
        "*(Nur eine Domäne deckt die Fehlerklasse ab → weniger robust)*",
        "",
        "| Fehlerklasse | Domänen | Bewertung |",
        "|--------------|---------|-----------|",
    ])
    for s in data.get("fehlerklassen_geringe_streuung", []):
        dom = ", ".join(s["domaenen"]) if s["domaenen"] else "–"
        lines.append(f"| {s['fehlerklasse']} | {dom} | {s['bewertung']} |")
    lines.extend([
        "",
        "---",
        "",
        "## 6. Top-5 Wartungsempfehlungen",
        "",
        "| Priorität | Typ | Ziel | Empfehlung |",
        "|-----------|-----|------|------------|",
    ])
    for r in data.get("wartungsempfehlungen", []):
        emp = (r.get("empfehlung", "") or "")[:70] + ("…" if len(r.get("empfehlung", "")) > 70 else "")
        lines.append(f"| {r.get('prioritaet', '?')} | {r.get('typ', '')} | {r.get('ziel', '')} | {emp} |")
    lines.extend([
        "",
        "---",
        "",
        "## 7. Empfehlung für QA Self-Healing Iteration 2",
        "",
        "| Priorität | Schritt | Nutzen |",
        "|-----------|---------|--------|",
    ])
    for e in data.get("empfehlung_iteration2", []):
        lines.append(f"| {e.get('prioritaet', '?')} | {e.get('schritt', '')} | {e.get('nutzen', '')} |")
    lines.extend([
        "",
        "---",
        "",
        "## 8. Verweise",
        "",
        "- [REGRESSION_CATALOG.md](REGRESSION_CATALOG.md)",
        "- [CHAOS_QA_PLAN.md](CHAOS_QA_PLAN.md)",
        "- [QA_AUTOPILOT.md](QA_AUTOPILOT.md)",
        "",
        f"*QA Self-Healing Iteration {data['iteration']} – generiert am {data['generated'].split()[0]}.*",
        "",
    ])
    return "\n".join(lines)


def write_json(data: dict) -> dict:
    """Erzeugt JSON-serialisierbares Dict."""
    return {
        "iteration": data["iteration"],
        "generated": data["generated"],
        "eingabedaten": data["eingabedaten"],
        "checks": data["checks"],
        "flaky_risiken": data["flaky_risiken"],
        "schwache_tests": data["schwache_tests"],
        "fehlerklassen_geringe_streuung": data["fehlerklassen_geringe_streuung"],
        "wartungsempfehlungen": data["wartungsempfehlungen"],
        "empfehlung_iteration2": data["empfehlung_iteration2"],
    }


def main() -> int:
    data = run_generator()
    DOCS_QA.mkdir(parents=True, exist_ok=True)

    md_content = write_markdown(data)
    (DOCS_QA / "QA_SELF_HEALING.md").write_text(md_content, encoding="utf-8")

    json_data = write_json(data)
    (DOCS_QA / "QA_SELF_HEALING.json").write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    flaky = len(data.get("flaky_risiken", []))
    weak = len(data.get("schwache_tests", []))
    spread = len(data.get("fehlerklassen_geringe_streuung", []))
    recs = len(data.get("wartungsempfehlungen", []))

    print("QA Self-Healing – generiert")
    print(f"  Flaky-Risiken: {flaky} | Schwache Tests: {weak} | Geringe Streuung: {spread}")
    print(f"  Wartungsempfehlungen: {recs}")
    print(f"  → docs/qa/QA_SELF_HEALING.md")
    print(f"  → docs/qa/QA_SELF_HEALING.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
