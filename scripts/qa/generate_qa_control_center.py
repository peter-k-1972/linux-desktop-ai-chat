#!/usr/bin/env python3
"""
QA Control Center Generator – Linux Desktop Chat.

Integriert alle QA-Artefakte in eine operative Steuerungsansicht.
Keine neue Analyse – Verdichtung und Integration.

Output:
- docs/qa/QA_CONTROL_CENTER.md
- docs/qa/QA_CONTROL_CENTER.json

Verwendung:
  python scripts/qa/generate_qa_control_center.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_QA = PROJECT_ROOT / "docs" / "qa"


def _load_json(path: Path) -> dict | None:
    """Lädt JSON-Datei oder gibt None zurück."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _collect_data() -> dict:
    """Sammelt Daten aus allen relevanten QA-Artefakten."""
    data: dict = {"sources": {}, "errors": []}

    # QA_STATUS.json
    status = _load_json(DOCS_QA / "QA_STATUS.json")
    data["sources"]["QA_STATUS"] = status
    if not status:
        data["errors"].append("QA_STATUS.json nicht gefunden oder ungültig")

    # QA_STABILITY_INDEX.json
    stability = _load_json(DOCS_QA / "QA_STABILITY_INDEX.json")
    data["sources"]["QA_STABILITY_INDEX"] = stability

    # QA_PRIORITY_SCORE.json
    priority = _load_json(DOCS_QA / "QA_PRIORITY_SCORE.json")
    data["sources"]["QA_PRIORITY_SCORE"] = priority

    # QA_AUTOPILOT.json
    autopilot = _load_json(DOCS_QA / "QA_AUTOPILOT.json")
    data["sources"]["QA_AUTOPILOT"] = autopilot

    # QA_SELF_HEALING.json
    self_healing = _load_json(DOCS_QA / "QA_SELF_HEALING.json")
    data["sources"]["QA_SELF_HEALING"] = self_healing

    # QA_ANOMALY_DETECTION.json
    anomaly = _load_json(DOCS_QA / "QA_ANOMALY_DETECTION.json")
    data["sources"]["QA_ANOMALY_DETECTION"] = anomaly

    # QA_HEATMAP.json
    heatmap = _load_json(DOCS_QA / "QA_HEATMAP.json")
    data["sources"]["QA_HEATMAP"] = heatmap

    return data


def _build_gesamtstatus(data: dict) -> dict:
    """Baut Gesamtstatus aus Status, Stability, Governance."""
    status = data["sources"].get("QA_STATUS") or {}
    stability = data["sources"].get("QA_STABILITY_INDEX") or {}

    test_count = status.get("test_count", -1)
    regression = status.get("regression", {})
    event_type = status.get("event_type", {})

    governance_parts = []
    if not status.get("marker_violations"):
        governance_parts.append("Marker-Disziplin OK")
    else:
        governance_parts.append(f"Marker: {len(status['marker_violations'])} Verletzungen")

    cov = regression.get("covered_count", 0)
    total = regression.get("total", cov + regression.get("open_count", 0)) or 12
    governance_parts.append(f"Regression {cov}/{total}")

    reg_ok = event_type.get("registry_ok", False)
    tl_ok = event_type.get("timeline_ok", False)
    if reg_ok and tl_ok:
        governance_parts.append("EventType OK")
    else:
        governance_parts.append("EventType: Lücken")

    return {
        "test_anzahl": test_count if test_count >= 0 else "?",
        "stability_index": stability.get("index", "?"),
        "stabilitaetsklasse": stability.get("stabilitaetsklasse", "?"),
        "governance": "; ".join(governance_parts),
    }


def _build_top_risiken(data: dict) -> list[dict]:
    """Top-Risiken aus Risk Radar / Priority Score."""
    status = data["sources"].get("QA_STATUS") or {}
    priority = data["sources"].get("QA_PRIORITY_SCORE") or {}

    risks = status.get("top_risks", [])
    if risks:
        return [{"subsystem": r.get("subsystem", "?"), "risk": r.get("risk", "?")} for r in risks]

    top3 = priority.get("top3_prioritaeten", [])
    return [
        {
            "subsystem": t.get("Subsystem", "?"),
            "risk": t.get("Begruendung", "?")[:80] + ("…" if len(t.get("Begruendung", "")) > 80 else ""),
        }
        for t in top3[:3]
    ]


def _build_naechster_sprint(data: dict) -> dict:
    """Nächster QA-Sprint aus Autopilot."""
    autopilot = data["sources"].get("QA_AUTOPILOT") or {}
    emp = autopilot.get("empfohlener_sprint", {})
    return {
        "subsystem": emp.get("subsystem", "–"),
        "schritt": emp.get("schritt", "–"),
        "testart": emp.get("empfohlene_testart", "–"),
    }


def _build_warnsignale(data: dict) -> list[dict]:
    """Aktuelle Warnsignale aus Anomaly Detection."""
    anomaly = data["sources"].get("QA_ANOMALY_DETECTION") or {}
    warns = anomaly.get("warnsignale", [])
    return [{"typ": w.get("typ", "beobachtung"), "text": w.get("text", "?")} for w in warns]


def _build_wartungsbedarf(data: dict) -> list[dict]:
    """QA-Wartungsbedarf aus Self-Healing."""
    sh = data["sources"].get("QA_SELF_HEALING") or {}
    emp = sh.get("wartungsempfehlungen", [])
    return [
        {
            "prioritaet": e.get("prioritaet", 0),
            "typ": e.get("typ", "?"),
            "ziel": e.get("ziel", "?"),
            "empfehlung": e.get("empfehlung", "?")[:100] + ("…" if len(e.get("empfehlung", "")) > 100 else ""),
        }
        for e in emp[:5]
    ]


def _build_stabilisatoren(data: dict) -> list[str]:
    """Top-Stabilisatoren aus Stability Index und Governance."""
    stability = data["sources"].get("QA_STABILITY_INDEX") or {}
    status = data["sources"].get("QA_STATUS") or {}

    stabilisatoren = stability.get("stabilisatoren", [])

    if not stabilisatoren:
        # Fallback aus Status
        parts = []
        if not status.get("marker_violations"):
            parts.append("Marker-Disziplin")
        reg = status.get("regression", {})
        if reg.get("open_count", 1) == 0:
            parts.append("Regression 12/12")
        if status.get("event_type", {}).get("registry_ok"):
            parts.append("EventType-Registry")
        return parts if parts else ["Governance-Grundlagen"]

    return stabilisatoren


def _build_top5_empfehlungen(data: dict) -> list[dict]:
    """Top-5 operative Empfehlungen – konsolidiert aus allen Artefakten."""
    recommendations = []

    # 1. Nächster Sprint (Autopilot)
    autopilot = data["sources"].get("QA_AUTOPILOT") or {}
    emp = autopilot.get("empfohlener_sprint", {})
    if emp.get("subsystem"):
        recommendations.append({
            "rang": 1,
            "massnahme": f"Nächster QA-Sprint: {emp.get('subsystem')} – {emp.get('schritt', '–')}",
            "quelle": "QA_AUTOPILOT",
        })

    # 2. Top-Risiko adressieren
    risks = _build_top_risiken(data)
    if risks:
        r = risks[0]
        risk_text = r.get("risk", "")
        risk_short = risk_text[:60] + "…" if len(risk_text) > 60 else risk_text
        recommendations.append({
            "rang": 2,
            "massnahme": f"Top-Risiko beobachten: {r.get('subsystem')} – {risk_short}",
            "quelle": "QA_RISK_RADAR",
        })

    # 3. Warnsignale
    anomaly = data["sources"].get("QA_ANOMALY_DETECTION") or {}
    warns = anomaly.get("warnsignale", [])
    if warns:
        w = warns[0]
        recommendations.append({
            "rang": 3,
            "massnahme": f"Warnsignal: {w.get('text', '?')}",
            "quelle": "QA_ANOMALY_DETECTION",
        })

    # 4. Wartung (Self-Healing Top-1)
    sh = data["sources"].get("QA_SELF_HEALING") or {}
    emp_list = sh.get("wartungsempfehlungen", [])
    if emp_list:
        e = emp_list[0]
        recommendations.append({
            "rang": 4,
            "massnahme": f"Wartung: {e.get('ziel', '?').split('::')[-1]} – {e.get('typ', '?')} prüfen",
            "quelle": "QA_SELF_HEALING",
        })

    # 5. Subsysteme NICHT priorisieren (niedriges Risiko)
    priority = data["sources"].get("QA_PRIORITY_SCORE") or {}
    scores = priority.get("scores", [])
    low_priority = [s for s in scores if s.get("Prioritaet") == "P3" and s.get("Score", 99) <= 1]
    if low_priority:
        subs = ", ".join(s.get("Subsystem", "?") for s in low_priority[:3])
        recommendations.append({
            "rang": 5,
            "massnahme": f"Nicht priorisieren (Risiko niedrig): {subs}",
            "quelle": "QA_PRIORITY_SCORE",
        })

    return recommendations[:5]


def _build_operative_fragen(data: dict) -> dict:
    """Beantwortet die 5 operativen Fragen."""
    autopilot = data["sources"].get("QA_AUTOPILOT") or {}
    anomaly = data["sources"].get("QA_ANOMALY_DETECTION") or {}
    sh = data["sources"].get("QA_SELF_HEALING") or {}
    priority = data["sources"].get("QA_PRIORITY_SCORE") or {}

    emp = autopilot.get("empfohlener_sprint", {})
    sprint_text = f"{emp.get('subsystem', '–')}: {emp.get('schritt', '–')}" if emp.get("subsystem") else "–"

    warns = [w.get("text", "?") for w in anomaly.get("warnsignale", [])]

    weak_tests = [e.get("ziel", "?") for e in sh.get("wartungsempfehlungen", []) if e.get("typ") == "Schwacher Test"][:3]
    if not weak_tests:
        weak_tests = [e.get("ziel", "?") for e in sh.get("wartungsempfehlungen", [])][:3]

    # P3 mit Score 1 = nicht priorisieren
    nicht_priorisieren = [
        s.get("Subsystem", "?")
        for s in priority.get("scores", [])
        if s.get("Prioritaet") == "P3" and s.get("Score", 99) <= 1
    ]

    # Niedriges Risiko
    niedrig_risiko = [
        s.get("Subsystem", "?")
        for s in priority.get("scores", [])
        if s.get("Prioritaet") == "P3" and s.get("Score", 99) <= 2
    ]

    return {
        "naechster_qa_sprint": sprint_text,
        "warnsignale_beobachten": warns,
        "schwache_tests_naechstes_haerten": weak_tests,
        "subsysteme_nicht_priorisieren": nicht_priorisieren[:5],
        "risiko_niedrig_keine_aktion": list(dict.fromkeys(niedrig_risiko))[:5],
    }


def generate() -> tuple[dict, str]:
    """Generiert Control-Center-Daten und Markdown."""
    data = _collect_data()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    gesamtstatus = _build_gesamtstatus(data)
    top_risiken = _build_top_risiken(data)
    naechster_sprint = _build_naechster_sprint(data)
    warnsignale = _build_warnsignale(data)
    wartungsbedarf = _build_wartungsbedarf(data)
    stabilisatoren = _build_stabilisatoren(data)
    top5_empfehlungen = _build_top5_empfehlungen(data)
    operative_fragen = _build_operative_fragen(data)

    output = {
        "iteration": 1,
        "generated": now,
        "gesamtstatus": gesamtstatus,
        "top_risiken": top_risiken,
        "naechster_qa_sprint": naechster_sprint,
        "warnsignale": warnsignale,
        "qa_wartungsbedarf": wartungsbedarf,
        "top_stabilisatoren": stabilisatoren,
        "top5_operative_empfehlungen": top5_empfehlungen,
        "operative_fragen": operative_fragen,
        "eingabedaten": [
            "QA_STATUS.json",
            "QA_STABILITY_INDEX.json",
            "QA_PRIORITY_SCORE.json",
            "QA_AUTOPILOT.json",
            "QA_SELF_HEALING.json",
            "QA_ANOMALY_DETECTION.json",
            "QA_HEATMAP.json",
        ],
        "empfehlung_iteration2": [
            {"prioritaet": 1, "schritt": "Dependency Graph Kaskaden einbeziehen", "nutzen": "Kritische Ketten priorisieren"},
            {"prioritaet": 2, "schritt": "History-Vergleich für Anomalie-Drift", "nutzen": "Echte Drift-Erkennung"},
            {"prioritaet": 3, "schritt": "CI-Integration: Control Center bei jedem Run", "nutzen": "Sichtbarkeit im Tagesgeschäft"},
        ],
    }

    # Markdown
    lines = [
        "# QA Control Center – Linux Desktop Chat",
        "",
        f"**Generiert:** {now}  ",
        "**Quelle:** `python scripts/qa/generate_qa_control_center.py`",
        "",
        "---",
        "",
        "## 1. Gesamtstatus",
        "",
        "| Metrik | Wert |",
        "|--------|------|",
        f"| Tests (ohne live/slow) | {gesamtstatus['test_anzahl']} |",
        f"| Stability Index | {gesamtstatus['stability_index']} |",
        f"| Stabilitätsklasse | {gesamtstatus['stabilitaetsklasse']} |",
        f"| Governance | {gesamtstatus['governance']} |",
        "",
        "---",
        "",
        "## 2. Top-Risiken",
        "",
        "| Rang | Subsystem | Risiko |",
        "|------|-----------|--------|",
    ]
    for i, r in enumerate(top_risiken, 1):
        lines.append(f"| {i} | **{r['subsystem']}** | {r['risk']} |")
    lines.extend([
        "",
        "→ Details: [QA_RISK_RADAR.md](QA_RISK_RADAR.md), [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md)",
        "",
        "---",
        "",
        "## 3. Nächster QA-Sprint",
        "",
        f"| Subsystem | Schritt | Testart |",
        f"|-----------|---------|---------|",
        f"| **{naechster_sprint['subsystem']}** | {naechster_sprint['schritt']} | {naechster_sprint['testart']} |",
        "",
        "→ Details: [QA_AUTOPILOT.md](QA_AUTOPILOT.md)",
        "",
        "---",
        "",
        "## 4. Aktuelle Warnsignale",
        "",
    ])
    if warnsignale:
        for w in warnsignale:
            lines.append(f"- {w['text']}")
        lines.append("")
    else:
        lines.append("- Keine aktiven Warnsignale.")
        lines.append("")
    lines.extend([
        "→ Details: [QA_ANOMALY_DETECTION.md](QA_ANOMALY_DETECTION.md)",
        "",
        "---",
        "",
        "## 5. QA-Wartungsbedarf",
        "",
    ])
    if wartungsbedarf:
        for w in wartungsbedarf:
            lines.append(f"- **P{w['prioritaet']}** ({w['typ']}): `{w['ziel']}`")
        lines.append("")
    else:
        lines.append("- Keine dringenden Wartungsempfehlungen.")
        lines.append("")
    lines.extend([
        "→ Details: [QA_SELF_HEALING.md](QA_SELF_HEALING.md)",
        "",
        "---",
        "",
        "## 6. Top-Stabilisatoren",
        "",
    ])
    for s in stabilisatoren:
        lines.append(f"- {s}")
    lines.extend([
        "",
        "---",
        "",
        "## 7. Top-5 operative Empfehlungen",
        "",
        "| Rang | Maßnahme | Quelle |",
        "|------|----------|--------|",
    ])
    for e in top5_empfehlungen:
        lines.append(f"| {e['rang']} | {e['massnahme']} | {e['quelle']} |")
    lines.extend([
        "",
        "---",
        "",
        "## 8. Operative Fragen (Antworten)",
        "",
        "| Frage | Antwort |",
        "|-------|--------|",
        f"| Was sollte im nächsten QA-Sprint passieren? | {operative_fragen['naechster_qa_sprint']} |",
        f"| Welche Warnsignale beobachten? | {', '.join(operative_fragen['warnsignale_beobachten'][:3]) or '–'} |",
        f"| Welche schwachen Tests als Nächstes härten? | {', '.join(operative_fragen['schwache_tests_naechstes_haerten'][:2]) or '–'} |",
        f"| Welche Subsysteme NICHT priorisieren? | {', '.join(operative_fragen['subsysteme_nicht_priorisieren']) or '–'} |",
        f"| Wo Risiko niedrig genug für Pause? | {', '.join(operative_fragen['risiko_niedrig_keine_aktion'][:3]) or '–'} |",
        "",
        "---",
        "",
        "## 9. Verweise",
        "",
        "- [QA_STATUS.md](QA_STATUS.md) – Testübersicht, Governance",
        "- [QA_STABILITY_INDEX.md](QA_STABILITY_INDEX.md) – Stabilitätskennzahl",
        "- [QA_RISK_RADAR.md](QA_RISK_RADAR.md) – Risikoübersicht",
        "- [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md) – Priorisierung",
        "- [QA_AUTOPILOT.md](QA_AUTOPILOT.md) – Sprint-Empfehlung",
        "- [QA_SELF_HEALING.md](QA_SELF_HEALING.md) – Wartung",
        "- [QA_ANOMALY_DETECTION.md](QA_ANOMALY_DETECTION.md) – Warnsignale",
        "- [QA_INCIDENT_REPLAY_ARCHITECTURE.md](QA_INCIDENT_REPLAY_ARCHITECTURE.md) – Incident → Replay → Guard",
        "- [QA_INCIDENT_REPLAY_INTEGRATION.md](QA_INCIDENT_REPLAY_INTEGRATION.md) – Integrationsarchitektur (Incidents, KPIs, Warnsignale)",
        "",
        "### Generator",
        "",
        "```bash",
        "python3 scripts/qa/generate_qa_control_center.py",
        "```",
        "",
        "### Empfehlung Iteration 2",
        "",
        "1. Dependency Graph Kaskaden einbeziehen",
        "2. History-Vergleich für Anomalie-Drift",
        "3. CI-Integration: Control Center bei jedem Run",
        "",
        f"*Generiert am {now}.*",
        "",
    ])

    md_content = "\n".join(lines)
    return output, md_content


def main() -> int:
    output, md_content = generate()

    DOCS_QA.mkdir(parents=True, exist_ok=True)
    (DOCS_QA / "QA_CONTROL_CENTER.json").write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    (DOCS_QA / "QA_CONTROL_CENTER.md").write_text(md_content, encoding="utf-8")

    # Kurze Summary in stdout
    gs = output["gesamtstatus"]
    print("QA Control Center – Summary")
    print("=" * 40)
    print(f"  Stability Index: {gs['stability_index']} ({gs['stabilitaetsklasse']})")
    print(f"  Tests: {gs['test_anzahl']}")
    print(f"  Nächster Sprint: {output['naechster_qa_sprint']['subsystem']} → {output['naechster_qa_sprint']['schritt']}")
    print(f"  Warnsignale: {len(output['warnsignale'])}")
    print(f"  Top-Risiko: {output['top_risiken'][0]['subsystem'] if output['top_risiken'] else '–'}")
    print("=" * 40)
    print("  → docs/qa/QA_CONTROL_CENTER.md")
    print("  → docs/qa/QA_CONTROL_CENTER.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
