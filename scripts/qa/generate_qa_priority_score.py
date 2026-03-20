#!/usr/bin/env python3
"""
QA Priority Score Generator – Linux Desktop Chat.

Liest QA_RISK_RADAR.md, QA_HEATMAP.json, QA_EVOLUTION_MAP.md und erzeugt
eine nachvollziehbare QA-Priorisierung pro Subsystem.

Output:
- docs/qa/QA_PRIORITY_SCORE.md
- docs/qa/QA_PRIORITY_SCORE.json

Verwendung:
  python scripts/qa/generate_qa_priority_score.py
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_QA = PROJECT_ROOT / "docs" / "qa"

# Scoring: P1=3, P2=2, P3=1
P_SCORE = {"P1": 3, "P2": 2, "P3": 1}

# Restrisiko/Restlücken: Low=0, Medium=1, High=2
LEVEL_SCORE = {"low": 0, "medium": 1, "high": 2}

# Nächste QA-Schritte (aus Evolution Map, Risk Radar)
NEXT_STEPS = {
    "Agentensystem": "Live-Tests für echte Agent-Ausführung",
    "Startup/Bootstrap": "Init-Reihenfolge Contract",
    "RAG": "Embedding-Service Failure (Ollama Embedding-API)",
    "Provider/Ollama": "Contract für Ollama-Response-Format",
    "Prompt-System": "failure_mode für Prompt-Service",
    "Persistenz/SQLite": "Contract für DB-Schema",
    "Metrics": "Cross-Layer für Metrics unter Failure",
    "Tools": "–",
    "Chat": "–",
    "Debug/EventBus": "Drift-Sentinel bei neuem EventType (bereits vorhanden)",
}


def parse_level(s: str) -> int:
    """Low→0, Medium→1, High→2."""
    s = (s or "").strip().lower()
    if "high" in s:
        return 2
    if "medium" in s or "mittel" in s:
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
                        "prioritaet": parts[8].replace("**", "").strip() if len(parts) > 8 else "",
                        "restluecken": parts[7] if len(parts) > 7 else "Low",
                    }
        elif in_table and not line.strip().startswith("|"):
            break
    return result


def parse_evolution_map(content: str) -> dict:
    """Extrahiert Nächster QA-Hebel aus QA_EVOLUTION_MAP.md."""
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
                hebel = parts[4] if len(parts) > 4 else ""
                if sub and sub != "Subsystem":
                    result[sub] = {"naechster_hebel": hebel}
        elif in_table and line.strip() == "":
            break
    return result


def weak_dimensions(hm: dict) -> list[str]:
    """Liefert Dimensionen mit Wert <= 1."""
    dims = [
        "Failure_Coverage",
        "Contract_Coverage",
        "Async_Coverage",
        "Cross_Layer_Coverage",
        "Drift_Governance_Coverage",
    ]
    labels = {
        "Failure_Coverage": "Failure",
        "Contract_Coverage": "Contract",
        "Async_Coverage": "Async",
        "Cross_Layer_Coverage": "Cross-Layer",
        "Drift_Governance_Coverage": "Drift/Gov",
    }
    return [labels[d] for d in dims if hm.get(d, 0) <= 1]


def build_begruendung(
    sub: str,
    rr: dict,
    hm: dict,
    top3_risks: dict,
) -> str:
    """Baut Begründung aus Risk Radar, Heatmap, Top-3-Risiken."""
    parts = []
    p = rr.get("prioritaet", "")
    if p:
        parts.append(f"Risk Radar {p}")
    weak = weak_dimensions(hm)
    if weak:
        parts.append(f"schwache Abdeckung: {', '.join(weak)}")
    if sub in top3_risks:
        parts.append(top3_risks[sub])
    restluecken = rr.get("restluecken", "")
    if restluecken and "medium" in restluecken.lower() or "high" in restluecken.lower():
        parts.append(f"Restlücken {restluecken}")
    return "; ".join(parts) if parts else "Stabile Abdeckung"


def compute_score(rr: dict, hm: dict) -> tuple[int, str]:
    """
    Berechnet Prioritätsscore.

    Logik:
    - P-Basis: P1=3, P2=2, P3=1
    - Coverage-Gap: (15 - Summe) / 5 → 0..3 (niedrige Abdeckung = höherer Gap)
    - Restrisiko: Low=0, Medium=1, High=2
    - Restlücken: Low=0, Medium=1, High=2

    Score = P + Gap + Restrisiko + Restlücken (höher = dringender)
    """
    p_raw = rr.get("prioritaet", "P3")
    p_val = P_SCORE.get(p_raw.upper(), 1)

    cov_sum = (
        hm.get("Failure_Coverage", 0)
        + hm.get("Contract_Coverage", 0)
        + hm.get("Async_Coverage", 0)
        + hm.get("Cross_Layer_Coverage", 0)
        + hm.get("Drift_Governance_Coverage", 0)
    )
    gap = max(0, min(3, (15 - cov_sum) // 5))

    restrisiko = hm.get("Restrisiko", "Low")
    rest_val = LEVEL_SCORE.get(restrisiko.lower(), 0)

    restluecken = rr.get("restluecken", "Low")
    restl_val = parse_level(restluecken)

    score = p_val + gap + rest_val + restl_val
    p_label = rr.get("prioritaet", "P3")
    return score, f"{p_label}+Gap{gap}+Restr{rest_val}+Restl{restl_val}"


def get_next_step(sub: str, evolution: dict) -> str:
    """Nächster QA-Schritt aus Evolution Map oder Fallback."""
    hebel = evolution.get(sub, {}).get("naechster_hebel", "").strip()
    if hebel and hebel != "–" and hebel != "-":
        return hebel
    return NEXT_STEPS.get(sub, "–")


def main() -> int:
    """Hauptfunktion."""
    risk_path = DOCS_QA / "QA_RISK_RADAR.md"
    heatmap_path = DOCS_QA / "QA_HEATMAP.json"
    evolution_path = DOCS_QA / "QA_EVOLUTION_MAP.md"

    if not risk_path.exists():
        print(f"FEHLER: {risk_path} nicht gefunden.", file=sys.stderr)
        return 1
    if not heatmap_path.exists():
        print(f"FEHLER: {heatmap_path} nicht gefunden.", file=sys.stderr)
        return 1

    risk_content = risk_path.read_text(encoding="utf-8")
    heatmap_data = json.loads(heatmap_path.read_text(encoding="utf-8"))
    evolution = parse_evolution_map(evolution_path.read_text(encoding="utf-8")) if evolution_path.exists() else {}

    risk_radar = parse_risk_radar(risk_content)

    # Top-3-Risiken aus Risk Radar
    top3_risks = {}
    in_top3 = False
    for line in risk_content.split("\n"):
        if "Top-3-Risikobereiche" in line or "Top-3 Risikobereiche" in line:
            in_top3 = True
            continue
        if in_top3 and line.strip().startswith("|") and "---" not in line and "Rang" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4 and parts[1].strip().isdigit():
                sub = parts[2].replace("**", "").strip()
                risk = parts[3].strip()
                if sub and risk:
                    top3_risks[sub] = risk
        if in_top3 and line.strip() == "" and top3_risks:
            break

    # Heatmap als Dict pro Subsystem
    hm_by_sub = {r["Subsystem"]: r for r in heatmap_data.get("heatmap", [])}

    # Scores berechnen
    rows = []
    for hm_row in heatmap_data.get("heatmap", []):
        sub = hm_row["Subsystem"]
        rr = risk_radar.get(sub, {})
        score, score_detail = compute_score(rr, hm_row)
        begruendung = build_begruendung(sub, rr, hm_row, top3_risks)
        next_step = get_next_step(sub, evolution)

        rows.append({
            "Subsystem": sub,
            "Score": score,
            "Prioritaet": rr.get("prioritaet", "P3"),
            "Begruendung": begruendung,
            "Naechster_QA_Schritt": next_step,
            "Score_Detail": score_detail,
        })

    # Nach Score sortieren (höher = zuerst), bei Gleichstand: P1 > P2 > P3
    p_order = {"P1": 0, "P2": 1, "P3": 2}
    rows.sort(key=lambda r: (-r["Score"], p_order.get(r["Prioritaet"], 3), r["Subsystem"]))

    # Top-3 und Top-3 Sprints
    top3 = rows[:3]
    top3_sprints = [
        {"Rang": i, "Subsystem": r["Subsystem"], "Schritt": r["Naechster_QA_Schritt"]}
        for i, r in enumerate(top3, 1)
    ]

    # JSON schreiben
    json_out = {
        "eingabedaten": ["QA_RISK_RADAR.md", "QA_HEATMAP.json", "QA_EVOLUTION_MAP.md"],
        "scoring_logik": {
            "P_Basis": "P1=3, P2=2, P3=1",
            "Coverage_Gap": "(15 - Summe) / 5, max 3",
            "Restrisiko": "Low=0, Medium=1, High=2",
            "Restluecken": "Low=0, Medium=1, High=2",
            "Score": "P + Gap + Restrisiko + Restlücken",
        },
        "scores": rows,
        "top3_prioritaeten": [
            {"Rang": i, "Subsystem": r["Subsystem"], "Score": r["Score"], "Begruendung": r["Begruendung"]}
            for i, r in enumerate(top3, 1)
        ],
        "top3_naechste_sprints": top3_sprints,
    }
    (DOCS_QA / "QA_PRIORITY_SCORE.json").write_text(
        json.dumps(json_out, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Markdown schreiben
    table_lines = [
        "| Subsystem | Score | Priorität | Begründung | Nächster QA-Schritt |",
        "|-----------|-------|-----------|------------|---------------------|",
    ]
    for r in rows:
        table_lines.append(
            f"| {r['Subsystem']} | {r['Score']} | {r['Prioritaet']} | "
            f"{r['Begruendung'][:60]}{'…' if len(r['Begruendung']) > 60 else ''} | "
            f"{r['Naechster_QA_Schritt'][:40]}{'…' if len(r['Naechster_QA_Schritt']) > 40 else ''} |"
        )

    top3_md = "\n".join(
        f"{i}. **{r['Subsystem']}** (Score {r['Score']}): {r['Naechster_QA_Schritt']}"
        for i, r in enumerate(top3, 1)
    )
    sprints_md = "\n".join(
        f"{i}. **{r['Subsystem']}**: {r['Naechster_QA_Schritt']}"
        for i, r in enumerate(rows[:5], 1)
    )

    md_content = f"""# QA Priority Score – Linux Desktop Chat

**Generiert:** `python scripts/qa/generate_qa_priority_score.py`  
**Zweck:** Automatische, nachvollziehbare QA-Priorisierung aus Risk Radar + Heatmap.

---

## 1. Zweck

Der Priority Score unterstützt:

- **Sprintplanung:** Welche Subsysteme zuerst absichern?
- **Transparenz:** Nachvollziehbare Begründung pro Subsystem
- **Nächste Schritte:** Konkrete QA-Hebel für den nächsten Sprint

---

## 2. Scoring-Logik

| Komponente | Bedeutung |
|------------|-----------|
| **P-Basis** | Risk Radar Priorität: P1=3, P2=2, P3=1 |
| **Coverage-Gap** | (15 − Summe der 5 Heatmap-Dimensionen) / 5, max 3 |
| **Restrisiko** | Low=0, Medium=1, High=2 |
| **Restlücken** | Low=0, Medium=1, High=2 |

**Score = P + Coverage-Gap + Restrisiko + Restlücken**

Höherer Score = höhere QA-Priorität.

---

## 3. Tabelle pro Subsystem

{chr(10).join(table_lines)}

---

## 4. Top-3 nächste QA-Sprints

{top3_md}

---

## 5. Empfohlene nächste QA-Schritte (Top-5)

{sprints_md}

---

## 6. Quellen

| Datei | Inhalt |
|-------|--------|
| [QA_RISK_RADAR.md](QA_RISK_RADAR.md) | Priorität, Restlücken |
| [QA_HEATMAP.json](QA_HEATMAP.json) | Coverage pro Dimension |
| [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md) | Nächster QA-Hebel |

---

## 7. Empfehlung für QA Priority Scoring Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Gewichtung der Dimensionen konfigurierbar | Flexiblere Priorisierung |
| 2 | Trend: Score-Verlauf über Zeit | Fortschritt sichtbar |
| 3 | Cockpit-Integration: Top-3 in QA_STATUS | Sichtbarkeit im Tagesgeschäft |

---

*Generiert durch scripts/qa/generate_qa_priority_score.py*
"""
    (DOCS_QA / "QA_PRIORITY_SCORE.md").write_text(md_content, encoding="utf-8")

    # Summary
    print("=" * 60)
    print("QA Priority Score – Summary")
    print("=" * 60)
    print()
    print("Verwendete Eingabedaten:")
    for f in json_out["eingabedaten"]:
        print(f"  - {f}")
    print()
    print("Scoring-Logik:")
    for k, v in json_out["scoring_logik"].items():
        print(f"  - {k}: {v}")
    print()
    print("Top-3 Prioritäten:")
    for r in top3:
        print(f"  {r['Score']} | {r['Subsystem']}: {r['Begruendung'][:50]}…")
    print()
    print("Top-3 nächste QA-Sprints:")
    for r in top3_sprints:
        print(f"  {r['Rang']}. {r['Subsystem']}: {r['Schritt']}")
    print()
    print("Generierte Dateien:")
    print(f"  - {DOCS_QA / 'QA_PRIORITY_SCORE.md'}")
    print(f"  - {DOCS_QA / 'QA_PRIORITY_SCORE.json'}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
