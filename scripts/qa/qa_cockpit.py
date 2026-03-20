#!/usr/bin/env python3
"""
QA Cockpit – aktives QA-Radar für Linux Desktop Chat.

Generiert docs/qa/artifacts/dashboards/QA_STATUS.md mit:
- Testzahlen
- Marker-Disziplin
- EventType-Coverage
- Regression-Coverage
- Warnungen / offene Governance-Lücken

Verwendung:
  python scripts/qa/qa_cockpit.py
  python scripts/qa/qa_cockpit.py --json   # Zusätzlich QA_STATUS.json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Projekt-Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.qa.qa_paths import DOCS_QA, ARTIFACTS_DASHBOARDS, ARTIFACTS_JSON


def _run_pytest_count() -> tuple[int, int]:
    """Führt pytest --collect-only aus und zählt Tests (ohne live/slow)."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "-m", "not live and not slow"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        out = result.stdout + result.stderr
        # pytest -q zeigt "XXX items" oder "XXX tests"
        for line in out.splitlines():
            if " item" in line or " test" in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p.isdigit() and i > 0 and "item" in line.lower() or "test" in line.lower():
                        return int(p), 0
                # Fallback: erste Zahl
                for p in parts:
                    if p.isdigit():
                        return int(p), 0
    except Exception as e:
        return -1, 0
    return -1, 0


def _count_tests_simple() -> int:
    """Zählt Tests via pytest --collect-only (Summe der pro-Datei-Zahlen)."""
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "-m", "not live and not slow"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=90,
        )
        total = 0
        for line in (r.stdout + r.stderr).splitlines():
            # Format: "tests/foo/test_bar.py: 5"
            if ":" in line:
                part = line.rsplit(":", 1)[-1].strip()
                if part.isdigit():
                    total += int(part)
        return total if total > 0 else -1
    except Exception:
        pass
    return -1


def run_cockpit(json_output: bool = False) -> str:
    """Führt alle Checks aus und generiert QA_STATUS.md."""
    sys.path.insert(0, str(PROJECT_ROOT))

    from scripts.qa.checks import (
        check_marker_discipline,
        get_marker_violations,
        check_event_type_coverage,
        check_regression_coverage,
        TOP_RISKS,
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    test_count = _count_tests_simple()

    # Marker-Disziplin
    marker_results = check_marker_discipline()
    violations = get_marker_violations()

    # EventType
    et_coverage = check_event_type_coverage()

    # Regression
    reg_coverage = check_regression_coverage()

    # Control Center Kurzfassung (falls vorhanden)
    control_center_summary = None
    cc_path = ARTIFACTS_JSON / "QA_CONTROL_CENTER.json"
    if cc_path.exists():
        try:
            cc = json.loads(cc_path.read_text(encoding="utf-8"))
            gs = cc.get("gesamtstatus", {})
            sprint = cc.get("naechster_qa_sprint", {})
            warns = cc.get("warnsignale", [])
            risks = cc.get("top_risiken", [])
            control_center_summary = {
                "stability_index": gs.get("stability_index", "?"),
                "next_sprint": f"{sprint.get('subsystem', '–')}: {sprint.get('schritt', '–')}",
                "active_warnings": len(warns),
                "top_risks": [r.get("subsystem", "?") for r in risks[:3]],
            }
        except (json.JSONDecodeError, KeyError):
            pass

    # Build Markdown
    lines = [
        "# QA Status – Linux Desktop Chat",
        "",
        f"**Generiert:** {now}  ",
        f"**Quelle:** `python scripts/qa/qa_cockpit.py`",
        "",
    ]
    if control_center_summary:
        next_short = control_center_summary["next_sprint"]
        if len(next_short) > 40:
            next_short = next_short[:40] + "…"
        lines.extend([
            "**→ [QA Control Center](QA_CONTROL_CENTER.md)** – integrierte Steuerungsansicht",
            "",
            f"| Stability Index | Next QA Sprint | Active Warnings | Top Risks |",
            f"|-----------------|----------------|-----------------|-----------|",
            f"| {control_center_summary['stability_index']} | {next_short} | {control_center_summary['active_warnings']} | {', '.join(control_center_summary['top_risks'])} |",
            "",
        ])
    lines.extend([
        "---",
        "",
        "## 1. Testübersicht",
        "",
        f"| Metrik | Wert |",
        f"|--------|------|",
        f"| Tests (ohne live/slow) | {test_count if test_count >= 0 else '?'} |",
        f"| Marker-Disziplin geprüft | {len(marker_results)} Dateien |",
        f"| Fehlerklassen (Regression) | {reg_coverage['total']} gesamt |",
        "",
        "---",
        "",
        "## 2. Marker-Disziplin",
        "",
    ])

    if violations:
        lines.extend([
            "⚠️ **Warnung:** Folgende Dateien haben keinen erwarteten Marker:",
            "",
        ])
        for rel, marker in violations:
            lines.append(f"- `{rel}` → erwartet: `@pytest.mark.{marker}`")
        lines.extend(["", ""])
    else:
        lines.extend([
            "✅ Alle spezialisierten Testdomänen nutzen die erwarteten Marker.",
            "",
            "| Domäne | Erwarteter Marker | Dateien |",
            "|--------|-------------------|---------|",
        ])
        by_domain: dict[str, list] = {}
        for rel, marker, has_marker in marker_results:
            domain = rel.split("/")[1] if "/" in rel else "?"
            by_domain.setdefault(domain, []).append((rel, has_marker))
        for domain, items in sorted(by_domain.items()):
            ok = sum(1 for _, h in items if h)
            total = len(items)
            marker = next((m for d, m in [
                ("chaos", "chaos"),
                ("contracts", "contract"),
                ("async_behavior", "async_behavior"),
                ("failure_modes", "failure_mode"),
                ("cross_layer", "cross_layer"),
                ("startup", "startup"),
                ("meta", "contract"),
            ] if d == domain), "?")
            lines.append(f"| {domain} | `{marker}` | {ok}/{total} ✅ |")
        lines.append("")

    # EventType
    lines.extend([
        "---",
        "",
        "## 3. EventType-Coverage",
        "",
    ])
    if "error" in et_coverage:
        lines.append(f"⚠️ Fehler: {et_coverage['error']}")
    else:
        et = et_coverage.get("event_types", [])
        reg_ok = et_coverage.get("registry_ok", False)
        tl_ok = et_coverage.get("timeline_ok", False)
        lines.append(f"| Check | Status |")
        lines.append(f"|-------|--------|")
        lines.append(f"| EventTypes (Anzahl) | {len(et)} |")
        lines.append(f"| Registry (event_type_registry.py) | {'✅' if reg_ok else '❌'} |")
        lines.append(f"| Timeline (event_timeline_view) | {'✅' if tl_ok else '❌'} |")
        if et_coverage.get("registry_missing"):
            lines.append(f"| Fehlend in Registry | {', '.join(et_coverage['registry_missing'])} |")
        if et_coverage.get("timeline_missing"):
            lines.append(f"| Fehlend in Timeline | {', '.join(et_coverage['timeline_missing'])} |")
        lines.append("")

    # Regression
    lines.extend([
        "---",
        "",
        "## 4. Regression-Coverage",
        "",
        f"| Metrik | Wert |",
        f"|--------|------|",
        f"| Abgedeckt | {reg_coverage['covered_count']}/{reg_coverage['total']} |",
        f"| Offen | {reg_coverage['open_count']} |",
        "",
    ])
    if reg_coverage["open"]:
        lines.extend([
            "**Offene Fehlerklassen (kein Test im Catalog):**",
            "",
        ])
        for ec in reg_coverage["open"]:
            lines.append(f"- `{ec}`")
        lines.append("")
    lines.append("")

    # QA Stability Index (falls vorhanden)
    stability_path = ARTIFACTS_JSON / "QA_STABILITY_INDEX.json"
    stability_line = None
    if stability_path.exists():
        try:
            stab = json.loads(stability_path.read_text(encoding="utf-8"))
            idx = stab.get("index", "?")
            klasse = stab.get("stabilitaetsklasse", "?")
            stability_line = f"- [QA_STABILITY_INDEX.md](QA_STABILITY_INDEX.md) – Stabilitätsindex **{idx}** ({klasse})"
        except (json.JSONDecodeError, KeyError):
            pass

    # Top-3 Risiken (aus Risk Radar)
    lines.extend([
        "---",
        "",
        "## 5. Top-3 Risiken (Risk Radar)",
        "",
        "| Rang | Subsystem | Hauptrisiko |",
        "|------|-----------|-------------|",
    ])
    for i, (subsys, risk) in enumerate(TOP_RISKS, 1):
        lines.append(f"| {i} | **{subsys}** | {risk} |")
    lines.extend([
        "",
        "→ Details: [QA_RISK_RADAR.md](QA_RISK_RADAR.md)",
        "",
    ])
    # Top-3 nächste QA-Sprints (aus Priority Score, falls vorhanden)
    priority_path = ARTIFACTS_JSON / "QA_PRIORITY_SCORE.json"
    if priority_path.exists():
        try:
            priority_data = json.loads(priority_path.read_text(encoding="utf-8"))
            sprints = priority_data.get("top3_naechste_sprints", [])
            if sprints:
                lines.extend(["", "**Top-3 nächste QA-Sprints:**", ""])
                for s in sprints:
                    lines.append(f"- **{s.get('Subsystem', '?')}**: {s.get('Schritt', '–')}")
                lines.append("")
                lines.append("→ Details: [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md)")
                lines.append("")
        except Exception:
            pass

    # Next QA Sprint Recommendation (aus Autopilot, falls vorhanden)
    autopilot_path = ARTIFACTS_JSON / "QA_AUTOPILOT.json"
    if autopilot_path.exists():
        try:
            ap_data = json.loads(autopilot_path.read_text(encoding="utf-8"))
            emp = ap_data.get("empfohlener_sprint", {})
            if emp.get("subsystem"):
                lines.extend([
                    "",
                    "**Next QA Sprint Recommendation (Autopilot):**",
                    "",
                    f"- **{emp.get('subsystem', '?')}** → {emp.get('schritt', '–')}",
                    f"- Testart: {emp.get('empfohlene_testart', '–')}",
                    "",
                    "→ Details: [QA_AUTOPILOT.md](QA_AUTOPILOT.md)",
                    "",
                ])
        except Exception:
            pass

    lines.extend([
        "---",
        "",
        "## 6. Empfohlene Kommandos",
        "",
        "```bash",
        "# Standard-CI (ohne live/slow)",
        'pytest -m "not live and not slow"',
        "",
        "# Meta-Tests (Drift-Check)",
        "pytest tests/meta/ -v",
        "",
        "# QA-Cockpit ausführen",
        "python scripts/qa/qa_cockpit.py",
        "```",
        "",
        "---",
        "",
        "## 7. Verweise",
        "",
    ])
    if stability_line:
        lines.append(stability_line)
    lines.extend([
        "- [QA_CONTROL_CENTER.md](QA_CONTROL_CENTER.md) – **Steuerungsboard** (Stability, Risiken, Sprint, Warnsignale)",
        "- [QA_RISK_RADAR.md](QA_RISK_RADAR.md) – Priorisierte Risikoübersicht",
        "- [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md) – QA-Priorisierung (Score + nächste Schritte)",
        "- [QA_AUTOPILOT.md](QA_AUTOPILOT.md) – Sprint-Empfehlung aus QA-Artefakten",
        "- [QA_SELF_HEALING.md](QA_SELF_HEALING.md) – QA-Wartungsempfehlungen, Flaky-/Schwache-Test-Heuristik",
        "- [QA_ANOMALY_DETECTION.md](QA_ANOMALY_DETECTION.md) – Anomalie-Erkennung, Warnsignale",
        "- [QA_DEPENDENCY_GRAPH.md](../../architecture/graphs/QA_DEPENDENCY_GRAPH.md) – Subsystem-Abhängigkeiten, Kaskadenpfade",
        "- [CHAOS_QA_PLAN.md](../../plans/CHAOS_QA_PLAN.md) – Chaos-Tests, Fault-Injection",
        "- [QA_HEATMAP.md](QA_HEATMAP.md) – QA-Abdeckung pro Subsystem (Heatmap)",
        "- [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md) – Subsystem ↔ Fehlerklasse ↔ Tests",
        "- [QA_LEVEL3_COVERAGE_MAP.md](QA_LEVEL3_COVERAGE_MAP.md) – Risk-based Coverage",
        "- [REGRESSION_CATALOG.md](../../governance/REGRESSION_CATALOG.md) – Fehlerklassen",
        "- [TEST_GOVERNANCE_RULES.md](../../governance/TEST_GOVERNANCE_RULES.md) – Testpflichten",
        "- [CI_TEST_LEVELS.md](../../governance/CI_TEST_LEVELS.md) – CI-Stufung",
        "",
        f"*Generiert am {now}.*",
        "",
    ])

    md_content = "\n".join(lines)

    # Write QA_STATUS.md
    ARTIFACTS_DASHBOARDS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DASHBOARDS / "QA_STATUS.md").write_text(md_content, encoding="utf-8")

    # Optional JSON
    if json_output:
        ARTIFACTS_JSON.mkdir(parents=True, exist_ok=True)
        data = {
            "generated": now,
            "test_count": test_count,
            "marker_violations": [{"file": f, "expected_marker": m} for f, m in violations],
            "event_type": et_coverage,
            "regression": {
                "covered": reg_coverage["covered"],
                "open": reg_coverage["open"],
                "covered_count": reg_coverage["covered_count"],
                "open_count": reg_coverage["open_count"],
            },
            "top_risks": [{"subsystem": s, "risk": r} for s, r in TOP_RISKS],
        }
        (ARTIFACTS_JSON / "QA_STATUS.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    return md_content


def main():
    parser = argparse.ArgumentParser(description="QA Cockpit – aktives QA-Radar")
    parser.add_argument("--json", action="store_true", help="Zusätzlich QA_STATUS.json erzeugen")
    args = parser.parse_args()
    content = run_cockpit(json_output=args.json)
    print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
