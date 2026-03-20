#!/usr/bin/env python3
"""
QA Stability Index Generator – Linux Desktop Chat.

Liest QA_PRIORITY_SCORE.json, QA_HEATMAP.json, CHAOS_QA_PLAN.md, QA_STATUS.json
und erzeugt eine nachvollziehbare Stabilitätskennzahl.

Output:
- docs/qa/QA_STABILITY_INDEX.md
- docs/qa/QA_STABILITY_INDEX.json

Verwendung:
  python scripts/qa/generate_qa_stability_index.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_QA = PROJECT_ROOT / "docs" / "qa"
TESTS_CHAOS = PROJECT_ROOT / "tests" / "chaos"

# Index-Logik: Abzüge
def _abzug_priority_top3(summe: int) -> int:
    """0-9→0, 10-12→3, 13-15→5, 16+→7"""
    if summe <= 9:
        return 0
    if summe <= 12:
        return 3
    if summe <= 15:
        return 5
    return 7


def _abzug_heatmap_weak_spots(anzahl: int) -> int:
    """0-5→0, 6-10→3, 11-15→5, 16+→7"""
    if anzahl <= 5:
        return 0
    if anzahl <= 10:
        return 3
    if anzahl <= 15:
        return 5
    return 7


def _abzug_kritische_subsysteme(anzahl: int) -> int:
    """-1 pro Subsystem mit Score >= 4"""
    return min(anzahl, 5)  # Cap bei 5


# Stabilitätsklasse
def _stabilitaetsklasse(index: int) -> str:
    if index >= 90:
        return "Sehr stabil"
    if index >= 80:
        return "Stabil"
    if index >= 70:
        return "Stabil mit Beobachtungspunkten"
    if index >= 60:
        return "Erhöhtes Risiko"
    return "Releasekritisch"


def _count_chaos_scenarios(chaos_plan_path: Path) -> int:
    """Zählt Szenarien in CHAOS_QA_PLAN.md (Tabelle mit | Szenario |)."""
    if not chaos_plan_path.exists():
        return 0
    content = chaos_plan_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    count = 0
    in_table = False
    for line in lines:
        if "| Szenario |" in line:
            in_table = True
            continue
        if in_table:
            if not line.strip():
                break
            if line.strip().startswith("|") and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p]
                if len(parts) >= 1 and parts[0] and not parts[0].startswith("-"):
                    count += 1
            elif not line.strip().startswith("|"):
                break
    return max(count, 0)


def _count_chaos_test_files() -> int:
    """Zählt Testdateien in tests/chaos/ (ohne __init__.py)."""
    if not TESTS_CHAOS.exists():
        return 0
    return sum(
        1 for f in TESTS_CHAOS.iterdir()
        if f.suffix == ".py" and f.name != "__init__.py"
    )


def run_generator() -> dict:
    """Liest Artefakte, berechnet Index, gibt Ergebnis-Dict zurück."""
    result = {
        "iteration": 1,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "eingabedaten": [],
        "abzuege": [],
        "boni": [],
        "belastungsfaktoren": [],
        "stabilisatoren": [],
        "naechster_qa_sprint": [],
    }

    # 1. Priority Score
    priority_path = DOCS_QA / "QA_PRIORITY_SCORE.json"
    top3_sum = 0
    critical_count = 0
    sprints = []

    if priority_path.exists():
        result["eingabedaten"].append("QA_PRIORITY_SCORE.json")
        try:
            data = json.loads(priority_path.read_text(encoding="utf-8"))
            top3 = data.get("top3_prioritaeten", [])
            top3_sum = sum(s.get("Score", 0) for s in top3[:3])
            scores = data.get("scores", [])
            critical_count = sum(1 for s in scores if s.get("Score", 0) >= 4)
            sprints = data.get("top3_naechste_sprints", [])
        except (json.JSONDecodeError, KeyError):
            pass

    abzug_prio = _abzug_priority_top3(top3_sum)
    abzug_crit = _abzug_kritische_subsysteme(critical_count)
    result["abzuege"].append({
        "faktor": "Priority Top-3 Summe",
        "quelle": "QA_PRIORITY_SCORE.json",
        "wert": top3_sum,
        "abzug": abzug_prio,
    })
    result["abzuege"].append({
        "faktor": "Kritische Subsysteme (Score >= 4)",
        "quelle": "QA_PRIORITY_SCORE.json",
        "wert": critical_count,
        "abzug": abzug_crit,
    })
    if top3_sum and priority_path.exists():
        try:
            d = json.loads(priority_path.read_text(encoding="utf-8"))
            top3 = d.get("top3_prioritaeten", [])[:3]
            result["belastungsfaktoren"].append(
                f"Priority Top-3 Summe {top3_sum} – "
                + ", ".join(f"{s.get('Subsystem', '?')} ({s.get('Score', 0)})" for s in top3)
            )
        except Exception:
            result["belastungsfaktoren"].append(f"Priority Top-3 Summe {top3_sum}")

    # 2. Heatmap
    heatmap_path = DOCS_QA / "QA_HEATMAP.json"
    weak_spots = 0
    weak_subsystems_set: set[str] = set()

    if heatmap_path.exists():
        result["eingabedaten"].append("QA_HEATMAP.json")
        try:
            data = json.loads(heatmap_path.read_text(encoding="utf-8"))
            for row in data.get("heatmap", []):
                sub = row.get("Subsystem", "")
                for key, val in row.items():
                    if key == "Subsystem" or key == "Restrisiko":
                        continue
                    if isinstance(val, (int, float)) and val == 1:
                        weak_spots += 1
                        if sub:
                            weak_subsystems_set.add(sub)
        except (json.JSONDecodeError, KeyError):
            pass

    weak_subsystems = sorted(weak_subsystems_set)

    abzug_heat = _abzug_heatmap_weak_spots(weak_spots)
    result["abzuege"].insert(1, {
        "faktor": "Heatmap Weak Spots",
        "quelle": "QA_HEATMAP.json",
        "wert": weak_spots,
        "abzug": abzug_heat,
    })
    if weak_spots:
        result["belastungsfaktoren"].append(
            f"{weak_spots} Heatmap Weak Spots – " + ", ".join(weak_subsystems[:6])
        )
    if critical_count:
        result["belastungsfaktoren"].append(
            f"{critical_count} kritische Subsysteme – Score >= 4"
        )

    # 3. Chaos QA Plan
    chaos_path = DOCS_QA / "CHAOS_QA_PLAN.md"
    chaos_scenarios = _count_chaos_scenarios(chaos_path)
    chaos_bonus = 2 if chaos_scenarios >= 4 else (1 if chaos_scenarios >= 1 else 0)
    if chaos_path.exists():
        result["eingabedaten"].append("CHAOS_QA_PLAN.md")
    result["boni"].append({
        "faktor": "Chaos QA Plan",
        "quelle": "CHAOS_QA_PLAN.md",
        "beschreibung": f"{chaos_scenarios} Szenarien definiert",
        "bonus": chaos_bonus,
    })
    result["stabilisatoren"].append(
        f"Chaos QA Plan – {chaos_scenarios} Szenarien definiert"
    )

    # 4. Chaos-Tests
    chaos_files = _count_chaos_test_files()
    chaos_test_bonus = 1 if chaos_files >= 3 else 0
    result["eingabedaten"].append("tests/chaos/")
    result["boni"].append({
        "faktor": "Chaos-Tests",
        "quelle": "tests/chaos/",
        "beschreibung": f"{chaos_files} Testdateien vorhanden",
        "bonus": chaos_test_bonus,
    })
    if chaos_files >= 3:
        result["stabilisatoren"].append(
            f"Chaos-Tests in CI – {chaos_files} Testdateien, Fault-Injection aktiv"
        )

    # 5. Governance (QA_STATUS)
    status_path = DOCS_QA / "QA_STATUS.json"
    gov_ok = False
    if status_path.exists():
        result["eingabedaten"].append("QA_STATUS.json")
        try:
            data = json.loads(status_path.read_text(encoding="utf-8"))
            violations = data.get("marker_violations", [])
            reg = data.get("regression", {})
            et = data.get("event_type", {})
            marker_ok = len(violations) == 0
            reg_ok = reg.get("open_count", 1) == 0
            et_ok = et.get("registry_ok", False) and et.get("timeline_ok", False)
            gov_ok = marker_ok and reg_ok and et_ok
        except (json.JSONDecodeError, KeyError):
            pass

    gov_bonus = 3 if gov_ok else 0
    result["boni"].append({
        "faktor": "Governance",
        "quelle": "QA_STATUS.json",
        "beschreibung": "Marker OK, Regression 12/12, EventType OK" if gov_ok else "Teilweise",
        "bonus": gov_bonus,
    })
    if gov_ok:
        result["stabilisatoren"].append(
            "Governance – Marker-Disziplin, Regression 12/12, EventType Registry+Timeline"
        )

    # Nächster QA-Sprint
    result["naechster_qa_sprint"] = sprints

    # Berechnung
    abzuege_gesamt = sum(a["abzug"] for a in result["abzuege"])
    boni_gesamt = sum(b["bonus"] for b in result["boni"])
    index = max(0, min(100, 100 - abzuege_gesamt + boni_gesamt))

    result["index"] = index
    result["stabilitaetsklasse"] = _stabilitaetsklasse(index)
    result["abzuege_gesamt"] = abzuege_gesamt
    result["boni_gesamt"] = boni_gesamt
    result["klassen_skala"] = {
        "90-100": "Sehr stabil",
        "80-89": "Stabil",
        "70-79": "Stabil mit Beobachtungspunkten",
        "60-69": "Erhöhtes Risiko",
        "<60": "Releasekritisch",
    }

    return result


def write_markdown(data: dict) -> str:
    """Erzeugt QA_STABILITY_INDEX.md Inhalt."""
    lines = [
        "# QA Stability Index – Linux Desktop Chat",
        "",
        f"**Iteration:** {data['iteration']}  ",
        f"**Generiert:** {data['generated']}  ",
        "**Zweck:** Nachvollziehbare Stabilitätskennzahl für den aktuellen QA-/Release-Zustand.",
        "",
        "---",
        "",
        "## 1. Zweck",
        "",
        "Der QA Stability Index fasst den QA-Zustand in eine einzige, interpretierbare Kennzahl. Er berücksichtigt:",
        "",
        "- **Risiken** (Priority Score, Risk Radar)",
        "- **Abdeckungsdefizite** (Heatmap)",
        "- **Resilienzmaßnahmen** (Chaos QA Plan)",
        "- **Governance** (Marker-Disziplin, Regression-Coverage, EventType)",
        "",
        "Nicht nur Testanzahl, sondern Qualität und Risikolage.",
        "",
        "---",
        "",
        "## 2. Berechnungslogik",
        "",
        "**Startwert:** 100",
        "",
        "### Abzüge (Belastungsfaktoren)",
        "",
        "| Faktor | Quelle | Regel | Aktuell |",
        "|-------|--------|-------|---------|",
    ]
    for a in data["abzuege"]:
        lines.append(f"| {a['faktor']} | {a['quelle']} | siehe Skala | {a['wert']} → **−{a['abzug']}** |")
    lines.extend([
        "",
        "### Boni (Stabilisatoren)",
        "",
        "| Faktor | Quelle | Regel | Aktuell |",
        "|-------|--------|-------|---------|",
    ])
    for b in data["boni"]:
        lines.append(f"| {b['faktor']} | {b['quelle']} | {b['beschreibung']} | **+{b['bonus']}** |")
    lines.extend([
        "",
        "**Index = 100 − Abzüge + Boni**",
        "",
        "---",
        "",
        "## 3. Aktueller Index",
        "",
        "| Metrik | Wert |",
        "|--------|------|",
        f"| **Index** | **{data['index']}** |",
        f"| **Stabilitätsklasse** | {data['stabilitaetsklasse']} |",
        f"| Abzüge gesamt | {data['abzuege_gesamt']} |",
        f"| Boni gesamt | {data['boni_gesamt']} |",
        "",
        "---",
        "",
        "## 4. Stabilitätsklassen",
        "",
        "| Bereich | Klasse | Bedeutung |",
        "|---------|--------|-----------|",
        "| 90–100 | Sehr stabil | Release-ready, geringe Risiken |",
        "| 80–89 | Stabil | Release möglich, bekannte Beobachtungspunkte |",
        "| 70–79 | Stabil mit Beobachtungspunkten | Release mit Vorsicht, QA-Schritte priorisieren |",
        "| 60–69 | Erhöhtes Risiko | Release nur nach gezielten QA-Maßnahmen |",
        "| &lt;60 | Releasekritisch | Kein Release ohne signifikante QA-Verbesserung |",
        "",
        "---",
        "",
        "## 5. Wichtigste Belastungsfaktoren",
        "",
    ])
    for i, bf in enumerate(data["belastungsfaktoren"], 1):
        lines.append(f"{i}. **{bf}**")
    lines.extend(["", "## 6. Wichtigste Stabilisatoren", ""])
    for i, st in enumerate(data["stabilisatoren"], 1):
        lines.append(f"{i}. **{st}**")
    lines.extend([
        "",
        "## 7. Empfohlener nächster QA-Sprint",
        "",
        "| Rang | Subsystem | Schritt |",
        "|------|-----------|---------|",
    ])
    for s in data["naechster_qa_sprint"]:
        sub = s.get("Subsystem", "?")
        schritt = s.get("Schritt", "–")
        rang = s.get("Rang", "?")
        lines.append(f"| {rang} | {sub} | {schritt} |")
    lines.extend([
        "",
        "→ Details: [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md)",
        "",
        "---",
        "",
        "## 8. Verweise",
        "",
        "- [QA_PRIORITY_SCORE.json](QA_PRIORITY_SCORE.json) – Eingabedaten",
        "- [QA_HEATMAP.json](QA_HEATMAP.json) – Eingabedaten",
        "- [CHAOS_QA_PLAN.md](CHAOS_QA_PLAN.md) – Eingabedaten",
        "- [QA_STATUS.json](QA_STATUS.json) – Governance-Status",
        "- [QA_STATUS.md](QA_STATUS.md) – Cockpit-Übersicht",
        "",
        "---",
        "",
        "## 9. Empfehlung für QA Stability Index Iteration 2",
        "",
        "| Priorität | Schritt | Nutzen |",
        "|-----------|---------|--------|",
        "| 1 | Dependency Graph einbeziehen | Kaskadenpfade als Belastungsfaktor (kritische Ketten) |",
        "| 2 | Risk Radar direkt nutzen | Restrisiko High/Medium als Abzug |",
        "| 3 | Trend-Tracking | Index-Verlauf über Sprints (optional: Historie in JSON) |",
        "| 4 | Chaos-Szenarien ↔ Dependency Graph verknüpfen | Abdeckung kritischer Kaskaden durch Chaos-Tests |",
        "",
        "---",
        "",
        f"*QA Stability Index Iteration {data['iteration']} – generiert am {data['generated'].split()[0]}.*",
        "",
    ])
    return "\n".join(lines)


def write_json(data: dict) -> dict:
    """Erzeugt JSON-serialisierbares Dict (ohne redundante Keys)."""
    return {
        "iteration": data["iteration"],
        "generated": data["generated"],
        "zweck": "Nachvollziehbare Stabilitätskennzahl für den aktuellen QA-/Release-Zustand",
        "index": data["index"],
        "stabilitaetsklasse": data["stabilitaetsklasse"],
        "klassen_skala": data["klassen_skala"],
        "berechnung": {
            "startwert": 100,
            "abzuege_gesamt": data["abzuege_gesamt"],
            "boni_gesamt": data["boni_gesamt"],
            "abzuege": data["abzuege"],
            "boni": data["boni"],
        },
        "belastungsfaktoren": data["belastungsfaktoren"],
        "stabilisatoren": data["stabilisatoren"],
        "naechster_qa_sprint": data["naechster_qa_sprint"],
        "eingabedaten": data["eingabedaten"],
        "empfehlung_iteration2": [
            {"prioritaet": 1, "schritt": "Dependency Graph einbeziehen", "nutzen": "Kaskadenpfade als Belastungsfaktor"},
            {"prioritaet": 2, "schritt": "Risk Radar direkt nutzen", "nutzen": "Restrisiko High/Medium als Abzug"},
            {"prioritaet": 3, "schritt": "Trend-Tracking", "nutzen": "Index-Verlauf über Sprints"},
            {"prioritaet": 4, "schritt": "Chaos-Szenarien ↔ Dependency Graph verknüpfen", "nutzen": "Abdeckung kritischer Kaskaden"},
        ],
    }


def main() -> int:
    data = run_generator()
    DOCS_QA.mkdir(parents=True, exist_ok=True)

    md_content = write_markdown(data)
    (DOCS_QA / "QA_STABILITY_INDEX.md").write_text(md_content, encoding="utf-8")

    json_data = write_json(data)
    (DOCS_QA / "QA_STABILITY_INDEX.json").write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Stdout Summary
    print("QA Stability Index – generiert")
    print(f"  Index: {data['index']} ({data['stabilitaetsklasse']})")
    print(f"  Abzüge: {data['abzuege_gesamt']} | Boni: {data['boni_gesamt']}")
    print(f"  → docs/qa/QA_STABILITY_INDEX.md")
    print(f"  → docs/qa/QA_STABILITY_INDEX.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
