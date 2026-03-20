#!/usr/bin/env python3
"""
QA Autopilot Generator – Linux Desktop Chat.

Liest QA_PRIORITY_SCORE.json, QA_HEATMAP.json, QA_EVOLUTION_MAP.md,
QA_STABILITY_INDEX.json und erzeugt automatische QA-Sprint-Empfehlungen.

Output:
- docs/qa/QA_AUTOPILOT.md
- docs/qa/QA_AUTOPILOT.json

Verwendung:
  python scripts/qa/generate_qa_autopilot.py
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.qa.qa_paths import ARTIFACTS_JSON, ARTIFACTS_DASHBOARDS, ARCHITECTURE_GRAPHS

# Heatmap-Dimension → Testart
DIM_TO_TESTART = {
    "Failure_Coverage": "failure_mode",
    "Contract_Coverage": "contract",
    "Async_Coverage": "async_behavior",
    "Cross_Layer_Coverage": "cross_layer",
    "Drift_Governance_Coverage": "drift_governance",
}

DIM_LABELS = {
    "Failure_Coverage": "Failure-Mode-Tests",
    "Contract_Coverage": "Contract-Tests",
    "Async_Coverage": "Async-Behavior-Tests",
    "Cross_Layer_Coverage": "Cross-Layer-Tests",
    "Drift_Governance_Coverage": "Drift/Governance-Tests",
}


def _parse_evolution_map(path: Path) -> dict[str, str]:
    """Extrahiert Subsystem → Nächster QA-Hebel aus QA_EVOLUTION_MAP.md."""
    result: dict[str, str] = {}
    if not path.exists():
        return result
    content = path.read_text(encoding="utf-8")
    in_table = False
    for line in content.split("\n"):
        if "| Subsystem | Relevante Fehlerklassen |" in line:
            in_table = True
            continue
        if in_table:
            if not line.strip() or not line.strip().startswith("|"):
                break
            if "---" in line:
                continue
            parts = [p.strip() for p in line.split("|") if p]
            if len(parts) >= 5:
                sub = parts[0].replace("**", "").strip()
                hebel = parts[4].strip() if len(parts) > 4 else ""
                if sub and hebel and hebel != "–" and hebel != "-":
                    result[sub] = hebel
    return result


def _parse_dependency_hebel(path: Path) -> list[dict]:
    """Extrahiert Top QA-Hebel aus QA_DEPENDENCY_GRAPH.md Sektion 6."""
    result: list[dict] = []
    if not path.exists():
        return result
    content = path.read_text(encoding="utf-8")
    in_section = False
    for line in content.split("\n"):
        if "## 6. Top-3 QA-Hebel" in line:
            in_section = True
            continue
        if in_section:
            if line.strip().startswith("## "):
                break
            m = re.match(r"^\d+\.\s+\*\*(.+?)\*\*:\s*(.+)", line.strip())
            if m:
                result.append({"subsystem": m.group(1), "schritt": m.group(2).strip()})
    return result


def _get_heatmap_weakest(heatmap_row: dict) -> tuple[str, str] | None:
    """Findet schwächste Dimension (Wert 1) und gibt (dim_key, testart_label) zurück."""
    weakest = None
    for dim, testart in DIM_TO_TESTART.items():
        val = heatmap_row.get(dim)
        if isinstance(val, (int, float)) and val == 1:
            weakest = (dim, DIM_LABELS.get(dim, testart))
            break  # Erste gefundene
    return weakest


def _get_all_weak_dimensions(heatmap_row: dict) -> list[str]:
    """Gibt alle Dimensionen mit Wert 1 zurück (für Begründung)."""
    weak = []
    for dim in DIM_TO_TESTART:
        val = heatmap_row.get(dim)
        if isinstance(val, (int, float)) and val == 1:
            weak.append(DIM_LABELS.get(dim, dim))
    return weak


def _subsystem_in_belastungsfaktoren(subsystem: str, belastungsfaktoren: list[str]) -> bool:
    """Prüft ob Subsystem in Stability-Index-Belastungsfaktoren erwähnt wird."""
    sub_clean = subsystem.replace("/", "/")
    for bf in belastungsfaktoren:
        if subsystem in bf or sub_clean in bf:
            return True
    return False


def run_generator() -> dict:
    """Liest Artefakte, erzeugt Autopilot-Empfehlungen."""
    result: dict = {
        "iteration": 1,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "eingabedaten": [],
        "entscheidungslogik": [],
        "empfohlener_sprint": {},
        "top3_alternativen": [],
        "kandidaten": [],
        "stability_index_einordnung": "",
        "empfehlung_iteration2": [],
    }

    # 1. Priority Score
    priority_path = ARTIFACTS_JSON / "QA_PRIORITY_SCORE.json"
    scores_by_sub: dict[str, dict] = {}
    top3_sprints: list[dict] = []

    if priority_path.exists():
        result["eingabedaten"].append("QA_PRIORITY_SCORE.json")
        try:
            data = json.loads(priority_path.read_text(encoding="utf-8"))
            for s in data.get("scores", []):
                sub = s.get("Subsystem", "")
                if sub:
                    scores_by_sub[sub] = {
                        "score": s.get("Score", 0),
                        "prioritaet": s.get("Prioritaet", ""),
                        "naechster_schritt": s.get("Naechster_QA_Schritt", "–"),
                        "begruendung": s.get("Begruendung", ""),
                    }
            top3_sprints = data.get("top3_naechste_sprints", [])
        except (json.JSONDecodeError, KeyError):
            pass

    # 2. Heatmap
    heatmap_path = ARTIFACTS_JSON / "QA_HEATMAP.json"
    heatmap_by_sub: dict[str, dict] = {}

    if heatmap_path.exists():
        result["eingabedaten"].append("QA_HEATMAP.json")
        try:
            data = json.loads(heatmap_path.read_text(encoding="utf-8"))
            for row in data.get("heatmap", []):
                sub = row.get("Subsystem", "")
                if sub:
                    heatmap_by_sub[sub] = row
        except (json.JSONDecodeError, KeyError):
            pass

    # 3. Evolution Map
    evolution_path = ARTIFACTS_DASHBOARDS / "QA_EVOLUTION_MAP.md"
    evolution_hebel: dict[str, str] = _parse_evolution_map(evolution_path)
    if evolution_path.exists():
        result["eingabedaten"].append("QA_EVOLUTION_MAP.md")

    # 4. Stability Index
    stability_path = ARTIFACTS_JSON / "QA_STABILITY_INDEX.json"
    stability_index = 0
    stability_klasse = ""
    belastungsfaktoren: list[str] = []

    if stability_path.exists():
        result["eingabedaten"].append("QA_STABILITY_INDEX.json")
        try:
            data = json.loads(stability_path.read_text(encoding="utf-8"))
            stability_index = data.get("index", 0)
            stability_klasse = data.get("stabilitaetsklasse", "")
            belastungsfaktoren = data.get("belastungsfaktoren", [])
        except (json.JSONDecodeError, KeyError):
            pass

    # 5. Dependency Graph (optional)
    dep_path = ARCHITECTURE_GRAPHS / "QA_DEPENDENCY_GRAPH.md"
    dep_hebel: list[dict] = _parse_dependency_hebel(dep_path)
    if dep_path.exists():
        result["eingabedaten"].append("QA_DEPENDENCY_GRAPH.md")

    # Kandidaten bauen: alle Subsysteme aus Priority Score, sortiert nach Score (absteigend)
    all_subs = list(scores_by_sub.keys()) if scores_by_sub else list(heatmap_by_sub.keys())
    if not all_subs and heatmap_by_sub:
        all_subs = list(heatmap_by_sub.keys())

    # Sortierung: Priority Score absteigend, dann Heatmap Weak Spots absteigend
    def sort_key(sub: str) -> tuple:
        sc = scores_by_sub.get(sub, {})
        score = sc.get("score", 0)
        hm = heatmap_by_sub.get(sub, {})
        weak_count = sum(1 for k in DIM_TO_TESTART if isinstance(hm.get(k), (int, float)) and hm.get(k) == 1)
        in_bf = 1 if _subsystem_in_belastungsfaktoren(sub, belastungsfaktoren) else 0
        return (-score, -weak_count, -in_bf)

    all_subs.sort(key=sort_key)

    kandidaten = []
    for i, sub in enumerate(all_subs):
        sc = scores_by_sub.get(sub, {})
        hm = heatmap_by_sub.get(sub, {})

        # Nächster Schritt: Priority Score hat Vorrang, sonst Evolution Map
        schritt = sc.get("naechster_schritt", "–")
        if not schritt or schritt in ("–", "-"):
            schritt = evolution_hebel.get(sub, "–")

        # Fehlende Testart aus Heatmap
        weak_dims = _get_all_weak_dimensions(hm)
        weakest = _get_heatmap_weakest(hm)
        if weakest:
            empfohlene_testart = weakest[1]
        elif weak_dims:
            empfohlene_testart = weak_dims[0]
        else:
            empfohlene_testart = "–"

        # Grund: aus Priority Score Begründung + Heatmap
        grund_teile = []
        if sc.get("begruendung"):
            grund_teile.append(sc["begruendung"][:120] + ("…" if len(sc.get("begruendung", "")) > 120 else ""))
        if weak_dims:
            grund_teile.append(f"Schwache Abdeckung: {', '.join(weak_dims)}")
        if _subsystem_in_belastungsfaktoren(sub, belastungsfaktoren):
            grund_teile.append("Stabilitäts-Belastungsfaktor")
        grund = "; ".join(grund_teile) if grund_teile else "Priorität aus Risk Radar"

        kandidaten.append({
            "subsystem": sub,
            "prioritaetswert": sc.get("score", 0),
            "grund": grund,
            "empfohlene_testart": empfohlene_testart,
            "empfohlener_schritt": schritt,
            "heatmap_weak_spots": len(weak_dims),
        })

    result["kandidaten"] = kandidaten

    # Empfohlener nächster Sprint: erster Kandidat mit konkretem Schritt
    empfohlener = {}
    for k in kandidaten:
        if k["empfohlener_schritt"] and k["empfohlener_schritt"] not in ("–", "-"):
            empfohlener = {
                "subsystem": k["subsystem"],
                "grund": k["grund"],
                "empfohlene_testart": k["empfohlene_testart"],
                "schritt": k["empfohlener_schritt"],
            }
            break
    if not empfohlener and top3_sprints:
        first = top3_sprints[0]
        sub = first.get("Subsystem", "")
        schritt = first.get("Schritt", "–")
        for k in kandidaten:
            if k["subsystem"] == sub:
                empfohlener = {
                    "subsystem": sub,
                    "grund": k["grund"],
                    "empfohlene_testart": k["empfohlene_testart"],
                    "schritt": schritt,
                }
                break
    if not empfohlener and kandidaten:
        empfohlener = {
            "subsystem": kandidaten[0]["subsystem"],
            "grund": kandidaten[0]["grund"],
            "empfohlene_testart": kandidaten[0]["empfohlene_testart"],
            "schritt": kandidaten[0]["empfohlener_schritt"] or "–",
        }

    result["empfohlener_sprint"] = empfohlener

    # Top-3 Alternativen: nächste 3 mit konkretem Schritt, außer dem empfohlenen
    alternativen = []
    for k in kandidaten:
        if k["subsystem"] == empfohlener.get("subsystem"):
            continue
        if k["empfohlener_schritt"] and k["empfohlener_schritt"] not in ("–", "-"):
            alternativen.append({
                "subsystem": k["subsystem"],
                "grund": k["grund"],
                "empfohlene_testart": k["empfohlene_testart"],
                "schritt": k["empfohlener_schritt"],
            })
        if len(alternativen) >= 3:
            break
    if len(alternativen) < 3:
        seen = {a["subsystem"] for a in alternativen}
        for k in kandidaten:
            if k["subsystem"] == empfohlener.get("subsystem") or k["subsystem"] in seen:
                continue
            alternativen.append({
                "subsystem": k["subsystem"],
                "grund": k["grund"],
                "empfohlene_testart": k["empfohlene_testart"],
                "schritt": k["empfohlener_schritt"] or "–",
            })
            seen.add(k["subsystem"])
            if len(alternativen) >= 3:
                break

    result["top3_alternativen"] = alternativen[:3]

    # Entscheidungslogik
    result["entscheidungslogik"] = [
        "1. Priority Score als primäre Sortierung (höher = dringender)",
        "2. Heatmap Weak Spots als Tiebreaker (mehr Schwachstellen = höhere Priorität)",
        "3. Stabilitäts-Belastungsfaktoren: Subsysteme darin werden hervorgehoben",
        "4. Fehlende Testart: Dimension mit Wert 1 in der Heatmap → entsprechende Testart",
        "5. Nächster Schritt: aus Priority Score (Naechster_QA_Schritt), sonst Evolution Map (Nächster QA-Hebel)",
    ]

    # Stability Index Einordnung
    result["stability_index_einordnung"] = (
        f"Aktueller Stability Index: {stability_index} ({stability_klasse}). "
        "Der empfohlene Sprint adressiert einen der wichtigsten Belastungsfaktoren. "
        "Nach Umsetzung: Index-Verbesserung durch Reduktion von Priority Score und/oder Heatmap Weak Spots möglich."
    )

    # Empfehlung Iteration 2
    result["empfehlung_iteration2"] = [
        {"prioritaet": 1, "schritt": "Dependency Graph Kaskadenwirkung einbeziehen", "nutzen": "Kritische Ketten priorisieren"},
        {"prioritaet": 2, "schritt": "Risk Radar Restrisiko direkt nutzen", "nutzen": "High/Medium als Abzug"},
        {"prioritaet": 3, "schritt": "Autopilot-Output in CI/GitHub Action", "nutzen": "Sprint-Empfehlung bei jedem Run"},
    ]

    return result


def write_markdown(data: dict) -> str:
    """Erzeugt QA_AUTOPILOT.md Inhalt."""
    lines = [
        "# QA Autopilot – Linux Desktop Chat",
        "",
        f"**Iteration:** {data['iteration']}  ",
        f"**Generiert:** {data['generated']}  ",
        "**Zweck:** Aus QA-Artefakten automatisch ableiten, welcher QA-Sprint als Nächstes den höchsten Nutzen bringt.",
        "",
        "---",
        "",
        "## 1. Zweck",
        "",
        "Der QA Autopilot kombiniert:",
        "",
        "- **Priority Score** – Risikopriorisierung pro Subsystem",
        "- **Heatmap** – Abdeckungsdefizite (welche Testart fehlt?)",
        "- **Evolution Map** – nächster QA-Hebel pro Subsystem",
        "- **Stability Index** – Belastungsfaktoren",
        "",
        "Er liefert pro Kandidat: Grund, empfohlene Testart, empfohlenen Schritt.",
        "",
        "---",
        "",
        "## 2. Entscheidungslogik",
        "",
    ]
    for el in data["entscheidungslogik"]:
        lines.append(f"- {el}")
    lines.extend([
        "",
        "---",
        "",
        "## 3. Empfohlener nächster QA-Sprint",
        "",
        "| Subsystem | Grund | Testart | Schritt |",
        "|------------|-------|---------|---------|",
    ])
    emp = data.get("empfohlener_sprint", {})
    if emp:
        grund = emp.get("grund", "") or ""
        grund_short = grund[:80] + ("…" if len(grund) > 80 else "")
        lines.append(
            f"| **{emp.get('subsystem', '?')}** | {grund_short} | "
            f"{emp.get('empfohlene_testart', '–')} | {emp.get('schritt', '–')} |"
        )
    lines.extend([
        "",
        "---",
        "",
        "## 4. Top-3 alternative QA-Sprints",
        "",
        "| Rang | Subsystem | Grund | Testart | Schritt |",
        "|------|-----------|-------|---------|---------|",
    ])
    for i, alt in enumerate(data.get("top3_alternativen", [])[:3], 1):
        grund = (alt.get("grund", "") or "")[:60] + ("…" if len(alt.get("grund", "")) > 60 else "")
        lines.append(f"| {i} | {alt.get('subsystem', '?')} | {grund} | {alt.get('empfohlene_testart', '–')} | {alt.get('schritt', '–')} |")
    lines.extend([
        "",
        "---",
        "",
        "## 5. Alle Kandidaten (mit Begründung)",
        "",
        "| Subsystem | Priorität | Grund | Empfohlene Testart | Empfohlener Schritt |",
        "|-----------|-----------|-------|-------------------|---------------------|",
    ])
    for k in data.get("kandidaten", []):
        g = k.get("grund", "") or ""
        grund = g[:70] + ("…" if len(g) > 70 else "")
        lines.append(
            f"| {k.get('subsystem', '?')} | {k.get('prioritaetswert', '?')} | {grund} | "
            f"{k.get('empfohlene_testart', '–')} | {k.get('empfohlener_schritt', '–')} |"
        )
    lines.extend([
        "",
        "---",
        "",
        "## 6. Einordnung zum Stability Index",
        "",
        data.get("stability_index_einordnung", ""),
        "",
        "---",
        "",
        "## 7. Empfehlung für QA Autopilot Iteration 2",
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
        "- [QA_PRIORITY_SCORE.json](QA_PRIORITY_SCORE.json)",
        "- [QA_HEATMAP.json](QA_HEATMAP.json)",
        "- [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md)",
        "- [QA_STABILITY_INDEX.json](QA_STABILITY_INDEX.json)",
        "- [QA_DEPENDENCY_GRAPH.md](QA_DEPENDENCY_GRAPH.md)",
        "",
        f"*QA Autopilot Iteration {data['iteration']} – generiert am {data['generated'].split()[0]}.*",
        "",
    ])
    return "\n".join(lines)


def write_json(data: dict) -> dict:
    """Erzeugt JSON-serialisierbares Dict."""
    return {
        "iteration": data["iteration"],
        "generated": data["generated"],
        "eingabedaten": data["eingabedaten"],
        "entscheidungslogik": data["entscheidungslogik"],
        "empfohlener_sprint": data["empfohlener_sprint"],
        "top3_alternativen": data["top3_alternativen"],
        "kandidaten": data["kandidaten"],
        "stability_index_einordnung": data["stability_index_einordnung"],
        "empfehlung_iteration2": data["empfehlung_iteration2"],
    }


def main() -> int:
    data = run_generator()
    DOCS_QA.mkdir(parents=True, exist_ok=True)

    md_content = write_markdown(data)
    ARTIFACTS_DASHBOARDS.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_JSON.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DASHBOARDS / "QA_AUTOPILOT.md").write_text(md_content, encoding="utf-8")

    json_data = write_json(data)
    (ARTIFACTS_JSON / "QA_AUTOPILOT.json").write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    emp = data.get("empfohlener_sprint", {})
    print("QA Autopilot – generiert")
    print(f"  Empfohlener Sprint: {emp.get('subsystem', '?')} → {emp.get('schritt', '–')}")
    print(f"  Testart: {emp.get('empfohlene_testart', '–')}")
    print(f"  Alternativen: {len(data.get('top3_alternativen', []))}")
    print(f"  → docs/qa/QA_AUTOPILOT.md")
    print(f"  → docs/qa/QA_AUTOPILOT.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
