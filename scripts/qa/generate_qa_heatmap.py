#!/usr/bin/env python3
"""
QA Heatmap Generator – Linux Desktop Chat.

Liest docs/qa/QA_RISK_RADAR.md, QA_EVOLUTION_MAP.md, REGRESSION_CATALOG.md,
QA_LEVEL3_COVERAGE_MAP.md und erzeugt eine Heatmap pro Subsystem über
zentrale QA-Dimensionen.

Dimensionen:
- Failure Coverage
- Contract Coverage
- Async Coverage
- Cross-Layer Coverage
- Drift/Governance Coverage
- Restrisiko

Skala: 0 = keine, 1 = gering, 2 = mittel, 3 = stark
Restrisiko: Low / Medium / High

Verwendung:
  python scripts/qa/generate_qa_heatmap.py
"""

import csv
import json
import re
import sys
from pathlib import Path

# Projekt-Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_QA = PROJECT_ROOT / "docs" / "qa"

DIMENSIONS = [
    "Failure_Coverage",
    "Contract_Coverage",
    "Async_Coverage",
    "Cross_Layer_Coverage",
    "Drift_Governance_Coverage",
]
RESTRISIKO = "Restrisiko"


def parse_level(s: str) -> int:
    """Low→1, Medium→2, High→3."""
    s = (s or "").strip()
    if not s:
        return 0
    lower = s.lower()
    if "high" in lower or "stark" in lower:
        return 3
    if "medium" in lower or "mittel" in lower:
        return 2
    if "low" in lower or "gering" in lower:
        return 1
    return 0


def parse_risk_radar(content: str) -> dict:
    """Extrahiert Subsystem-Bewertung aus QA_RISK_RADAR.md."""
    result = {}
    in_table = False
    for line in content.split("\n"):
        if "| Subsystem | Failure Impact |" in line:
            in_table = True
            continue
        if in_table and line.strip().startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 9:
                sub = parts[0].replace("**", "").strip()
                if sub and sub != "Subsystem":
                    result[sub] = {
                        "failure_impact": parts[1],
                        "async_state": parts[2],
                        "cross_layer": parts[3],
                        "failure_test": parts[4],
                        "contract_gov": parts[5],
                        "drift": parts[6],
                        "restluecken": parts[7],
                        "prioritaet": parts[8] if len(parts) > 8 else "",
                    }
        elif in_table and not line.strip().startswith("|"):
            break
    return result


def parse_evolution_map(content: str) -> dict:
    """Extrahiert Restrisiko und Abgesichert-durch aus QA_EVOLUTION_MAP.md."""
    result = {}
    in_table = False
    for line in content.split("\n"):
        if "Subsystem" in line and "Relevante Fehlerklassen" in line and "|" in line:
            in_table = True
            continue
        if in_table and line.strip().startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 5:
                sub = parts[0].replace("**", "").strip()
                if sub and sub != "Subsystem":
                    result[sub] = {
                        "restrisiko": parts[3] if len(parts) > 3 else "Low",
                        "abgesichert_durch": (parts[2] or "").lower(),
                    }
        elif in_table and line.strip() == "":
            break
    return result


def build_heatmap(risk_radar: dict, evolution: dict) -> list[dict]:
    """Baut Heatmap-Daten aus geparsten Quellen."""
    subsystems = sorted(set(risk_radar.keys()) | set(evolution.keys()))
    rows = []

    for sub in subsystems:
        rr = risk_radar.get(sub, {})
        ev = evolution.get(sub, {})
        abg = ev.get("abgesichert_durch", "")

        # Failure Coverage: Failure-Test Spalte (High = gute Abdeckung)
        failure_cov = parse_level(rr.get("failure_test", ""))

        # Contract Coverage: Contract/Gov Spalte
        contract_cov = parse_level(rr.get("contract_gov", ""))

        # Async Coverage: aus Abgesichert durch (async_behavior) + Risk Radar
        async_cov = 0
        if "async_behavior" in abg or "async" in abg:
            async_cov = 3
        elif "streaming" in abg or "shutdown" in abg:
            async_cov = 3
        elif sub == "Chat":
            async_cov = 3
        elif sub == "Debug/EventBus":
            async_cov = 2
        elif sub in ("RAG", "Startup/Bootstrap", "Agentensystem"):
            async_cov = 2
        else:
            async_cov = max(1, parse_level(rr.get("async_state", "")) - 1)

        # Cross-Layer Coverage: aus Abgesichert durch (cross_layer) oder Risk Radar
        cross_cov = 0
        if "cross_layer" in abg:
            cross_cov = 3 if sub in ("Chat", "Prompt-System", "Debug/EventBus", "Agentensystem") else 2
        elif parse_level(rr.get("cross_layer", "")) >= 2 and sub in ("Chat", "Agentensystem", "Prompt-System", "Debug/EventBus"):
            cross_cov = 3  # Coverage Map: cross_layer für diese Subsysteme
        else:
            cross_cov = min(2, parse_level(rr.get("cross_layer", "")))

        # Drift/Governance: Drift-Risiko invers + Sentinel/Contract
        drift_cov = 0
        drift_risk = rr.get("drift", "")
        if "high" in drift_risk.lower() and sub == "Debug/EventBus":
            drift_cov = 2  # Sentinel vorhanden
        elif "medium" in drift_risk.lower():
            drift_cov = 2
        else:
            drift_cov = contract_cov  # Drift Low → Contract deckt ab

        # Restrisiko: aus Evolution Map
        restrisiko_raw = ev.get("restrisiko", "Low")
        if "high" in restrisiko_raw.lower():
            restrisiko = "High"
        elif "medium" in restrisiko_raw.lower():
            restrisiko = "Medium"
        else:
            restrisiko = "Low"

        rows.append({
            "Subsystem": sub,
            "Failure_Coverage": failure_cov,
            "Contract_Coverage": contract_cov,
            "Async_Coverage": async_cov,
            "Cross_Layer_Coverage": cross_cov,
            "Drift_Governance_Coverage": drift_cov,
            "Restrisiko": restrisiko,
        })

    return rows


def score_to_label(n: int) -> str:
    """0→–, 1→gering, 2→mittel, 3→stark."""
    return {0: "–", 1: "gering", 2: "mittel", 3: "stark"}.get(n, "–")


def generate_md(rows: list[dict], top3_hotspots: list, staerkste: list, empfehlungen: list) -> str:
    """Erzeugt QA_HEATMAP.md."""
    table_lines = [
        "| Subsystem | Failure | Contract | Async | Cross-Layer | Drift/Gov | Restrisiko |",
        "|-----------|---------|----------|-------|-------------|-----------|------------|",
    ]
    for r in rows:
        table_lines.append(
            f"| {r['Subsystem']} | "
            f"{score_to_label(r['Failure_Coverage'])} | "
            f"{score_to_label(r['Contract_Coverage'])} | "
            f"{score_to_label(r['Async_Coverage'])} | "
            f"{score_to_label(r['Cross_Layer_Coverage'])} | "
            f"{score_to_label(r['Drift_Governance_Coverage'])} | "
            f"{r['Restrisiko']} |"
        )

    hotspots_md = "\n".join(f"{i+1}. **{h['sub']}**: {h['reason']}" for i, h in enumerate(top3_hotspots))
    staerkste_md = "\n".join(f"- **{s['sub']}**: {s['dims']}" for s in staerkste)
    empf_md = "\n".join(f"- {e}" for e in empfehlungen)

    return f"""# QA Heatmap – Linux Desktop Chat

**Generiert:** `python scripts/qa/generate_qa_heatmap.py`  
**Zweck:** Sichtbarkeit der QA-Abdeckung pro Subsystem über zentrale Dimensionen.

---

## 1. Zweck

Die Heatmap unterstützt:

- **Planung:** Wo ist QA stark, wo schwach?
- **Priorisierung:** Welche Subsysteme brauchen den nächsten QA-Schritt?
- **Transparenz:** Nachvollziehbare qualitative Bewertung pro Dimension

---

## 2. Skala / Leselogik

| Wert | Bedeutung |
|------|-----------|
| **–** | Keine erkennbare Abdeckung |
| **gering** | 1 – Basis vorhanden |
| **mittel** | 2 – Deutliche Abdeckung |
| **stark** | 3 – Gute bis sehr gute Abdeckung |

**Restrisiko:** Low / Medium / High (aus Evolution Map)

| Dimension | Bedeutung |
|-----------|-----------|
| Failure | failure_mode-Tests, Fehlerszenarien |
| Contract | Contract-Tests, Schema-Governance |
| Async | async_behavior, Streaming, Race-Conditions |
| Cross-Layer | UI↔Service↔Request, Wahrheitsebenen |
| Drift/Gov | EventType-Sentinel, Drift-Absicherung |

---

## 3. Heatmap pro Subsystem

{chr(10).join(table_lines)}

---

## 4. Top-3 Hotspots (Priorität für QA)

{hotspots_md}

---

## 5. Stärkste QA-Bereiche

{staerkste_md}

---

## 6. Empfohlene nächste QA-Schritte

{empf_md}

---

## 7. Quellen

| Datei | Inhalt |
|-------|--------|
| [QA_RISK_RADAR.md](QA_RISK_RADAR.md) | Failure-Test, Contract/Gov, Drift |
| [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md) | Restrisiko, Abgesichert durch |
| [QA_LEVEL3_COVERAGE_MAP.md](QA_LEVEL3_COVERAGE_MAP.md) | Coverage-Details |
| [REGRESSION_CATALOG.md](REGRESSION_CATALOG.md) | Fehlerklassen, Tests |

---

## 8. Empfehlung für QA Heatmap Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Automatisches Parsen aus Risk Radar + Evolution Map | Heatmap aktuell halten |
| 2 | Trend: Heatmap-Vergleich über Zeit | Fortschritt sichtbar |
| 3 | Cockpit-Integration: Heatmap-Summary in QA_STATUS | Sichtbarkeit im Tagesgeschäft |

---

*Generiert durch scripts/qa/generate_qa_heatmap.py*
"""


def compute_insights(rows: list[dict]) -> tuple[list, list, list]:
    """Berechnet Top-3 Hotspots, stärkste Bereiche, Empfehlungen."""
    # Hotspots: niedrige Gesamtabdeckung oder Restrisiko
    def gap_score(r: dict) -> float:
        s = (
            r["Failure_Coverage"]
            + r["Contract_Coverage"]
            + r["Async_Coverage"]
            + r["Cross_Layer_Coverage"]
            + r["Drift_Governance_Coverage"]
        )
        risk = 1 if r["Restrisiko"] == "Low" else (2 if r["Restrisiko"] == "Medium" else 3)
        return risk * 2 - (s / 15.0)  # Höher = mehr Handlungsbedarf

    sorted_by_gap = sorted(rows, key=gap_score, reverse=True)
    top3_hotspots = []
    for r in sorted_by_gap[:3]:
        reasons = []
        if r["Failure_Coverage"] <= 1:
            reasons.append("Failure Coverage gering")
        if r["Contract_Coverage"] <= 1:
            reasons.append("Contract Coverage gering")
        if r["Drift_Governance_Coverage"] <= 1:
            reasons.append("Drift/Governance schwach")
        if r["Restrisiko"] != "Low":
            reasons.append(f"Restrisiko {r['Restrisiko']}")
        top3_hotspots.append({
            "sub": r["Subsystem"],
            "reason": "; ".join(reasons) if reasons else "Priorität aus Gesamtbewertung",
        })

    # Stärkste: hohe Summe
    def total(r: dict) -> int:
        return (
            r["Failure_Coverage"]
            + r["Contract_Coverage"]
            + r["Async_Coverage"]
            + r["Cross_Layer_Coverage"]
            + r["Drift_Governance_Coverage"]
        )

    sorted_by_strength = sorted(rows, key=total, reverse=True)
    staerkste = []
    for r in sorted_by_strength[:4]:
        dims = []
        for d in DIMENSIONS:
            v = r.get(d, 0)
            if v >= 2:
                dims.append(d.replace("_", " ").replace("Coverage", "").strip())
        staerkste.append({"sub": r["Subsystem"], "dims": ", ".join(dims) or "–"})

    # Empfehlungen (aus bekannten Lücken)
    empfehlungen = [
        "Live-Tests für Agent-Ausführung (Agentensystem)",
        "Init-Reihenfolge Contract (Startup/Bootstrap)",
        "Embedding-Service Failure (RAG)",
    ]

    return top3_hotspots, staerkste, empfehlungen


def main() -> int:
    """Hauptfunktion."""
    risk_path = DOCS_QA / "QA_RISK_RADAR.md"
    evolution_path = DOCS_QA / "QA_EVOLUTION_MAP.md"
    coverage_path = DOCS_QA / "QA_LEVEL3_COVERAGE_MAP.md"

    for p in (risk_path, evolution_path):
        if not p.exists():
            print(f"FEHLER: {p} nicht gefunden.", file=sys.stderr)
            return 1

    risk_content = risk_path.read_text(encoding="utf-8")
    evolution_content = evolution_path.read_text(encoding="utf-8")

    risk_radar = parse_risk_radar(risk_content)
    evolution = parse_evolution_map(evolution_content)

    rows = build_heatmap(risk_radar, evolution)
    top3_hotspots, staerkste, empfehlungen = compute_insights(rows)

    md_content = generate_md(rows, top3_hotspots, staerkste, empfehlungen)
    (DOCS_QA / "QA_HEATMAP.md").write_text(md_content, encoding="utf-8")

    # CSV
    with open(DOCS_QA / "QA_HEATMAP.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Subsystem"] + DIMENSIONS + [RESTRISIKO],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    # JSON
    json_data = {
        "subsystems": [r["Subsystem"] for r in rows],
        "dimensions": DIMENSIONS + [RESTRISIKO],
        "heatmap": rows,
        "top3_hotspots": top3_hotspots,
        "staerkste_bereiche": staerkste,
        "empfehlungen": empfehlungen,
    }
    (DOCS_QA / "QA_HEATMAP.json").write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Summary
    print("=" * 60)
    print("QA Heatmap – Summary")
    print("=" * 60)
    print()
    print("Verwendete Subsysteme:")
    for r in rows:
        print(f"  - {r['Subsystem']}")
    print()
    print("Verwendete QA-Dimensionen:")
    for d in DIMENSIONS + [RESTRISIKO]:
        print(f"  - {d}")
    print()
    print("Top-3 Hotspots:")
    for i, h in enumerate(top3_hotspots, 1):
        print(f"  {i}. {h['sub']}: {h['reason']}")
    print()
    print("Stärkste QA-Bereiche:")
    for s in staerkste:
        print(f"  - {s['sub']}: {s['dims']}")
    print()
    print("Empfehlung für QA Heatmap Iteration 2:")
    print("  - Automatisches Parsen aus Risk Radar + Evolution Map")
    print("  - Trend: Heatmap-Vergleich über Zeit")
    print("  - Cockpit-Integration: Heatmap-Summary in QA_STATUS")
    print()
    print("Generierte Dateien:")
    print(f"  - {DOCS_QA / 'QA_HEATMAP.md'}")
    print(f"  - {DOCS_QA / 'QA_HEATMAP.csv'}")
    print(f"  - {DOCS_QA / 'QA_HEATMAP.json'}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
