#!/usr/bin/env python3
"""
QA Anomaly Detection – Linux Desktop Chat.

Erkennt ungewöhnliche Veränderungen im QA-System durch heuristische
Vergleiche mit Baseline/History.

Anomalie-Klassen:
1. Stability Drift
2. Priority Shift
3. Flaky Cluster Growth
4. Weak Test Growth
5. Fehlerklassen-Konzentration

Output:
- docs/qa/QA_ANOMALY_DETECTION.md
- docs/qa/QA_ANOMALY_DETECTION.json
- docs/qa/QA_STABILITY_HISTORY.json (Baseline/History)

Verwendung:
  python scripts/qa/generate_qa_anomaly_detection.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_QA = PROJECT_ROOT / "docs" / "qa"

HISTORY_PATH = DOCS_QA / "QA_STABILITY_HISTORY.json"
MAX_HISTORY_ENTRIES = 20

# Anomalie-Klassen
ANOMALIE_KLASSEN = [
    {
        "id": "stability_drift",
        "name": "Stability Drift",
        "beschreibung": "Stability Index oder Stabilitätsklasse hat sich verschlechtert",
        "schwellen": {"index_drop": 5, "klassen_downgrade": True},
    },
    {
        "id": "priority_shift",
        "name": "Priority Shift",
        "beschreibung": "Top-Prioritäten oder kritische Subsysteme haben sich verschoben",
        "schwellen": {"top3_change": True, "critical_count_increase": 1},
    },
    {
        "id": "flaky_cluster_growth",
        "name": "Flaky Cluster Growth",
        "beschreibung": "Anzahl Flaky-Risiko-Tests ist gestiegen",
        "schwellen": {"growth": 3, "absolute_warn": 15},
    },
    {
        "id": "weak_test_growth",
        "name": "Weak Test Growth",
        "beschreibung": "Anzahl potenziell schwacher Tests ist gestiegen",
        "schwellen": {"growth": 3, "absolute_warn": 20},
    },
    {
        "id": "fehlerklassen_konzentration",
        "name": "Fehlerklassen-Konzentration",
        "beschreibung": "Mehr Fehlerklassen nur in einer Domäne abgesichert",
        "schwellen": {"growth": 2, "absolute_warn": 8},
    },
]


def _load_history() -> dict:
    """Lädt History oder gibt leeres Dict zurück."""
    if not HISTORY_PATH.exists():
        return {"entries": [], "baseline": None}
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, KeyError):
        return {"entries": [], "baseline": None}


def _save_history(history: dict) -> None:
    """Speichert History."""
    DOCS_QA.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def _build_snapshot() -> dict:
    """Baut aktuellen Snapshot aus QA-Artefakten."""
    snapshot = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "stability_index": None,
        "stabilitaetsklasse": None,
        "priority_top3_sum": None,
        "critical_subsystems": [],
        "flaky_count": 0,
        "weak_count": 0,
        "fehlerklassen_single_domain": 0,
        "heatmap_weak_spots": None,
    }

    # Stability Index
    stab_path = DOCS_QA / "QA_STABILITY_INDEX.json"
    if stab_path.exists():
        try:
            data = json.loads(stab_path.read_text(encoding="utf-8"))
            snapshot["stability_index"] = data.get("index")
            snapshot["stabilitaetsklasse"] = data.get("stabilitaetsklasse")
            abz = data.get("berechnung", {}).get("abzuege", [])
            for a in abz:
                if "Heatmap" in a.get("faktor", ""):
                    snapshot["heatmap_weak_spots"] = a.get("wert")
                    break
        except (json.JSONDecodeError, KeyError):
            pass

    # Priority Score
    prio_path = DOCS_QA / "QA_PRIORITY_SCORE.json"
    if prio_path.exists():
        try:
            data = json.loads(prio_path.read_text(encoding="utf-8"))
            top3 = data.get("top3_prioritaeten", [])
            snapshot["priority_top3_sum"] = sum(s.get("Score", 0) for s in top3[:3])
            scores = data.get("scores", [])
            snapshot["critical_subsystems"] = [s.get("Subsystem") for s in scores if s.get("Score", 0) >= 4]
        except (json.JSONDecodeError, KeyError):
            pass

    # Self-Healing
    sh_path = DOCS_QA / "QA_SELF_HEALING.json"
    if sh_path.exists():
        try:
            data = json.loads(sh_path.read_text(encoding="utf-8"))
            snapshot["flaky_count"] = len(data.get("flaky_risiken", []))
            snapshot["weak_count"] = len(data.get("schwache_tests", []))
            snapshot["fehlerklassen_single_domain"] = len(data.get("fehlerklassen_geringe_streuung", []))
        except (json.JSONDecodeError, KeyError):
            pass

    return snapshot


def _detect_anomalies(current: dict, baseline: dict | None) -> list[dict]:
    """Erkennt Anomalien durch Vergleich mit Baseline."""
    anomalies: list[dict] = []

    if not baseline:
        return anomalies

    # 1. Stability Drift
    idx_curr = current.get("stability_index")
    idx_base = baseline.get("stability_index")
    if idx_curr is not None and idx_base is not None:
        drop = idx_base - idx_curr
        if drop >= 5:
            anomalies.append({
                "klasse": "stability_drift",
                "name": "Stability Drift",
                "schwere": "mittel",
                "beschreibung": f"Stability Index von {idx_base} auf {idx_curr} gefallen (−{drop})",
                "reaktion": "Belastungsfaktoren prüfen, QA-Sprint priorisieren",
            })
        elif drop >= 2:
            anomalies.append({
                "klasse": "stability_drift",
                "name": "Stability Drift",
                "schwere": "niedrig",
                "beschreibung": f"Stability Index leicht gefallen: {idx_base} → {idx_curr}",
                "reaktion": "Beobachten, nächsten Sprint prüfen",
            })

    # 2. Priority Shift
    crit_curr = set(current.get("critical_subsystems", []))
    crit_base = set(baseline.get("critical_subsystems", []))
    if crit_curr != crit_base:
        new = crit_curr - crit_base
        if new:
            anomalies.append({
                "klasse": "priority_shift",
                "name": "Priority Shift",
                "schwere": "mittel" if len(new) >= 2 else "niedrig",
                "beschreibung": f"Neue kritische Subsysteme (Score≥4): {', '.join(new)}",
                "reaktion": "Risk Radar und Autopilot prüfen",
            })

    # 3. Flaky Cluster Growth
    flaky_curr = current.get("flaky_count", 0)
    flaky_base = baseline.get("flaky_count", 0)
    growth = flaky_curr - flaky_base
    if growth >= 3:
        anomalies.append({
            "klasse": "flaky_cluster_growth",
            "name": "Flaky Cluster Growth",
            "schwere": "mittel" if growth >= 5 else "niedrig",
            "beschreibung": f"Flaky-Risiko-Tests von {flaky_base} auf {flaky_curr} (+{growth})",
            "reaktion": "Self-Healing-Report prüfen, neue async/chaos-Tests bewerten",
        })
    elif flaky_curr >= 15:
        anomalies.append({
            "klasse": "flaky_cluster_growth",
            "name": "Flaky Cluster Growth",
            "schwere": "niedrig",
            "beschreibung": f"Flaky-Risiko-Cluster groß: {flaky_curr} Tests",
            "reaktion": "Regelmäßig Self-Healing prüfen",
        })

    # 4. Weak Test Growth
    weak_curr = current.get("weak_count", 0)
    weak_base = baseline.get("weak_count", 0)
    growth = weak_curr - weak_base
    if growth >= 3:
        anomalies.append({
            "klasse": "weak_test_growth",
            "name": "Weak Test Growth",
            "schwere": "mittel" if growth >= 5 else "niedrig",
            "beschreibung": f"Schwache Tests von {weak_base} auf {weak_curr} (+{growth})",
            "reaktion": "Assertion-Qualität prüfen, Wirkung statt Existenz testen",
        })
    elif weak_curr >= 20:
        anomalies.append({
            "klasse": "weak_test_growth",
            "name": "Weak Test Growth",
            "schwere": "niedrig",
            "beschreibung": f"Viele potenziell schwache Tests: {weak_curr}",
            "reaktion": "Self-Healing Top-5 abarbeiten",
        })

    # 5. Fehlerklassen-Konzentration
    fc_curr = current.get("fehlerklassen_single_domain", 0)
    fc_base = baseline.get("fehlerklassen_single_domain", 0)
    growth = fc_curr - fc_base
    if growth >= 2:
        anomalies.append({
            "klasse": "fehlerklassen_konzentration",
            "name": "Fehlerklassen-Konzentration",
            "schwere": "niedrig",
            "beschreibung": f"Mehr Fehlerklassen nur in 1 Domäne: {fc_base} → {fc_curr}",
            "reaktion": "Regression Catalog: Zweite Domäne für betroffene Klassen erwägen",
        })
    elif fc_curr >= 8:
        anomalies.append({
            "klasse": "fehlerklassen_konzentration",
            "name": "Fehlerklassen-Konzentration",
            "schwere": "niedrig",
            "beschreibung": f"{fc_curr} Fehlerklassen nur in einer Domäne abgesichert",
            "reaktion": "Streuung verbessern für robustere Abdeckung",
        })

    return anomalies


def _get_warnsignale(current: dict, baseline: dict | None) -> list[dict]:
    """Erzeugt Warnsignale aus aktuellen Schwellen (ohne History-Vergleich)."""
    signals: list[dict] = []

    idx = current.get("stability_index")
    if idx is not None:
        if idx < 60:
            signals.append({"typ": "kritisch", "text": f"Stability Index {idx} – releasekritisch"})
        elif idx < 70:
            signals.append({"typ": "warnung", "text": f"Stability Index {idx} – erhöhtes Risiko"})
        elif idx < 80:
            signals.append({"typ": "beobachtung", "text": f"Stability Index {idx} – Beobachtungspunkte"})

    if current.get("flaky_count", 0) >= 15:
        signals.append({"typ": "beobachtung", "text": f"{current['flaky_count']} Flaky-Risiko-Tests – Cluster prüfen"})
    if current.get("weak_count", 0) >= 20:
        signals.append({"typ": "beobachtung", "text": f"{current['weak_count']} potenziell schwache Tests"})
    if current.get("fehlerklassen_single_domain", 0) >= 8:
        signals.append({"typ": "beobachtung", "text": f"{current['fehlerklassen_single_domain']} Fehlerklassen nur in 1 Domäne"})

    return signals


def _get_qa_reaktionen(anomalies: list[dict], warnsignale: list[dict]) -> list[str]:
    """Leitet empfohlene QA-Reaktionen ab."""
    reaktionen: list[str] = []
    seen: set[str] = set()

    for a in anomalies:
        r = a.get("reaktion", "")
        if r and r not in seen:
            reaktionen.append(r)
            seen.add(r)

    if any(s.get("typ") == "kritisch" for s in warnsignale):
        reaktionen.insert(0, "Sofort: Stability-Index und Belastungsfaktoren analysieren")
    if any(s.get("typ") == "warnung" for s in warnsignale):
        if "Sofort" not in str(reaktionen):
            reaktionen.insert(0, "Nächster Sprint: QA-Prioritäten anpassen")

    if not reaktionen:
        reaktionen.append("Keine Anomalien – Baseline beibehalten, regelmäßig erneut prüfen")

    return reaktionen[:5]


def run_generator() -> dict:
    """Führt Anomalie-Erkennung aus."""
    result: dict = {
        "iteration": 1,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "eingabedaten": [],
        "anomalie_klassen": ANOMALIE_KLASSEN,
        "heuristiken": [],
        "baseline_aufgebaut": False,
        "anomalien": [],
        "warnsignale": [],
        "qa_reaktionen": [],
        "aktueller_snapshot": {},
        "empfehlung_iteration2": [],
    }

    # Snapshot bauen
    current = _build_snapshot()
    result["aktueller_snapshot"] = current
    result["eingabedaten"] = [
        "QA_STABILITY_INDEX.json",
        "QA_PRIORITY_SCORE.json",
        "QA_SELF_HEALING.json",
    ]

    # Heuristiken
    result["heuristiken"] = [
        "Stability Drift: Index-Differenz ≥5 = mittel, ≥2 = niedrig",
        "Priority Shift: Änderung der kritischen Subsysteme (Score≥4)",
        "Flaky Cluster Growth: +3 Tests = Anomalie, ≥15 absolut = Beobachtung",
        "Weak Test Growth: +3 Tests = Anomalie, ≥20 absolut = Beobachtung",
        "Fehlerklassen-Konzentration: +2 single-domain = Anomalie, ≥8 absolut = Beobachtung",
    ]

    # History laden / Baseline
    history = _load_history()
    baseline = history.get("baseline")

    if not baseline:
        # Erste Ausführung: Baseline anlegen
        baseline = current.copy()
        history["baseline"] = baseline
        history["entries"] = [{"timestamp": baseline["timestamp"], "snapshot": baseline}]
        _save_history(history)
        result["baseline_aufgebaut"] = True
        result["anomalien"] = []
    else:
        # Vergleich mit Baseline
        result["anomalien"] = _detect_anomalies(current, baseline)
        # History erweitern (optional: neuesten Snapshot anhängen)
        entries = history.get("entries", [])
        entries.append({"timestamp": current["timestamp"], "snapshot": current})
        history["entries"] = entries[-MAX_HISTORY_ENTRIES:]
        _save_history(history)

    # Warnsignale (immer, auch ohne History)
    result["warnsignale"] = _get_warnsignale(current, baseline)

    # QA-Reaktionen
    result["qa_reaktionen"] = _get_qa_reaktionen(result["anomalien"], result["warnsignale"])

    # Iteration 2
    result["empfehlung_iteration2"] = [
        {"prioritaet": 1, "schritt": "History-Vergleich über mehrere Sprints", "nutzen": "Echte Drift-Erkennung"},
        {"prioritaet": 2, "schritt": "Schwellen konfigurierbar machen", "nutzen": "Projekt-spezifische Anpassung"},
        {"prioritaet": 3, "schritt": "Cockpit-Integration: Anomalie-Badge", "nutzen": "Sichtbarkeit im Tagesgeschäft"},
    ]

    return result


def write_markdown(data: dict) -> str:
    """Erzeugt QA_ANOMALY_DETECTION.md Inhalt."""
    lines = [
        "# QA Anomaly Detection – Linux Desktop Chat",
        "",
        f"**Iteration:** {data['iteration']}  ",
        f"**Generiert:** {data['generated']}  ",
        "**Zweck:** Ungewöhnliche Veränderungen im QA-System heuristisch erkennbar machen.",
        "",
        "---",
        "",
        "## 1. Zweck",
        "",
        "Keine AI/ML, keine komplexe Statistik. Robuste heuristische Erkennung von QA-Anomalien:",
        "",
        "- Stability Drift",
        "- Priority Shift",
        "- Flaky Cluster Growth",
        "- Weak Test Growth",
        "- Fehlerklassen-Konzentration",
        "",
        "---",
        "",
        "## 2. Verwendete Heuristiken",
        "",
    ]
    for h in data.get("heuristiken", []):
        lines.append(f"- {h}")
    lines.extend([
        "",
        "---",
        "",
        "## 3. Anomalie-Klassen",
        "",
        "| ID | Name | Beschreibung |",
        "|----|------|--------------|",
    ])
    for k in data.get("anomalie_klassen", []):
        lines.append(f"| {k.get('id', '')} | {k.get('name', '')} | {k.get('beschreibung', '')} |")
    lines.extend([
        "",
        "---",
        "",
        "## 4. Erkannte Anomalien",
        "",
    ])
    if data.get("baseline_aufgebaut"):
        lines.extend([
            "**Baseline aufgebaut.** Erste Ausführung – noch keine Historie zum Vergleich.",
            "",
            "Aktueller Snapshot wurde als Baseline gespeichert. Bei der nächsten Ausführung",
            "werden Abweichungen erkannt.",
            "",
        ])
    else:
        anomalies = data.get("anomalien", [])
        if anomalies:
            lines.extend([
                "| Klasse | Schwere | Beschreibung | Reaktion |",
                "|--------|---------|--------------|----------|",
            ])
            for a in anomalies:
                lines.append(f"| {a.get('name', '')} | {a.get('schwere', '')} | {a.get('beschreibung', '')} | {a.get('reaktion', '')} |")
        else:
            lines.append("Keine Anomalien erkannt.")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 5. Aktuelle Warnsignale",
        "",
    ])
    signals = data.get("warnsignale", [])
    if signals:
        lines.extend(["| Typ | Text |", "|-----|------|"])
        for s in signals:
            lines.append(f"| {s.get('typ', '')} | {s.get('text', '')} |")
    else:
        lines.append("Keine Warnsignale.")
    lines.extend([
        "",
        "---",
        "",
        "## 6. Empfohlene QA-Reaktion",
        "",
    ])
    for i, r in enumerate(data.get("qa_reaktionen", []), 1):
        lines.append(f"{i}. {r}")
    lines.extend([
        "",
        "---",
        "",
        "## 7. Aktueller Snapshot (Baseline-Vergleich)",
        "",
        "| Metrik | Wert |",
        "|--------|------|",
    ])
    snap = data.get("aktueller_snapshot", {})
    for key, label in [
        ("stability_index", "Stability Index"),
        ("stabilitaetsklasse", "Stabilitätsklasse"),
        ("priority_top3_sum", "Priority Top-3 Summe"),
        ("flaky_count", "Flaky-Risiko-Tests"),
        ("weak_count", "Schwache Tests"),
        ("fehlerklassen_single_domain", "Fehlerklassen (nur 1 Domäne)"),
    ]:
        val = snap.get(key)
        lines.append(f"| {label} | {val if val is not None else '–'} |")
    lines.extend([
        "",
        "---",
        "",
        "## 8. Empfehlung für QA Anomaly Detection Iteration 2",
        "",
        "| Priorität | Schritt | Nutzen |",
        "|-----------|---------|--------|",
    ])
    for e in data.get("empfehlung_iteration2", []):
        lines.append(f"| {e.get('prioritaet', '')} | {e.get('schritt', '')} | {e.get('nutzen', '')} |")
    lines.extend([
        "",
        "---",
        "",
        "## 9. Verweise",
        "",
        "- [QA_STABILITY_INDEX.json](QA_STABILITY_INDEX.json)",
        "- [QA_SELF_HEALING.json](QA_SELF_HEALING.json)",
        "- [QA_STABILITY_HISTORY.json](QA_STABILITY_HISTORY.json)",
        "",
        f"*QA Anomaly Detection Iteration {data['iteration']} – generiert am {data['generated'].split()[0]}.*",
        "",
    ])
    return "\n".join(lines)


def write_json(data: dict) -> dict:
    """Erzeugt JSON-serialisierbares Dict."""
    return {
        "iteration": data["iteration"],
        "generated": data["generated"],
        "eingabedaten": data["eingabedaten"],
        "anomalie_klassen": data["anomalie_klassen"],
        "heuristiken": data["heuristiken"],
        "baseline_aufgebaut": data["baseline_aufgebaut"],
        "anomalien": data["anomalien"],
        "warnsignale": data["warnsignale"],
        "qa_reaktionen": data["qa_reaktionen"],
        "aktueller_snapshot": data["aktueller_snapshot"],
        "empfehlung_iteration2": data["empfehlung_iteration2"],
    }


def main() -> int:
    data = run_generator()
    DOCS_QA.mkdir(parents=True, exist_ok=True)

    md_content = write_markdown(data)
    (DOCS_QA / "QA_ANOMALY_DETECTION.md").write_text(md_content, encoding="utf-8")

    json_data = write_json(data)
    (DOCS_QA / "QA_ANOMALY_DETECTION.json").write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    baseline = " (Baseline aufgebaut)" if data.get("baseline_aufgebaut") else ""
    anom = len(data.get("anomalien", []))
    warn = len(data.get("warnsignale", []))

    print("QA Anomaly Detection – generiert")
    print(f"  Anomalien: {anom} | Warnsignale: {warn}{baseline}")
    print(f"  → docs/qa/QA_ANOMALY_DETECTION.md")
    print(f"  → docs/qa/QA_ANOMALY_DETECTION.json")
    if data.get("baseline_aufgebaut"):
        print(f"  → docs/qa/QA_STABILITY_HISTORY.json (Baseline)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
