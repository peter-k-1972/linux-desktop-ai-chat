#!/usr/bin/env python3
"""
QA Dependency Graph Generator – Linux Desktop Chat.

Erzeugt eine visuelle Karte der Subsystem-Abhängigkeiten und Kaskadenpfade.
Wenn Subsystem A fehlschlägt, welche anderen sind mitbetroffen?

Output:
- docs/qa/QA_DEPENDENCY_GRAPH.md
- docs/qa/QA_DEPENDENCY_GRAPH.mmd
- docs/qa/QA_DEPENDENCY_GRAPH.dot

Verwendung:
  python scripts/qa/generate_qa_dependency_graph.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.qa.qa_paths import ARCHITECTURE_GRAPHS

# Subsysteme (aus Risk Radar / Evolution Map)
SUBSYSTEMS = [
    "Chat",
    "Agentensystem",
    "Prompt-System",
    "RAG",
    "Debug/EventBus",
    "Metrics",
    "Startup/Bootstrap",
    "Tools",
    "Provider/Ollama",
    "Persistenz/SQLite",
]

# Abhängigkeiten: (from, to, edge_type, impact)
# A → B bedeutet: A hängt von B ab = wenn B fehlschlägt, ist A mitbetroffen
# Edge-Typen: runtime, startup, observability, persistence, async_state
# Impact: low, medium, high
DEPENDENCIES = [
    # Chat (Kern-UI) hängt von allen Laufzeit-Komponenten ab
    ("Chat", "Provider/Ollama", "runtime", "high"),
    ("Chat", "RAG", "runtime", "medium"),
    ("Chat", "Agentensystem", "runtime", "high"),
    ("Chat", "Prompt-System", "runtime", "high"),
    ("Chat", "Persistenz/SQLite", "persistence", "high"),
    # Agentensystem
    ("Agentensystem", "Provider/Ollama", "runtime", "high"),
    ("Agentensystem", "Prompt-System", "runtime", "high"),
    ("Agentensystem", "Tools", "runtime", "medium"),
    ("Agentensystem", "RAG", "runtime", "medium"),
    # RAG
    ("RAG", "Provider/Ollama", "runtime", "high"),
    ("RAG", "Persistenz/SQLite", "persistence", "medium"),
    # Prompt-System
    ("Prompt-System", "Persistenz/SQLite", "persistence", "high"),
    # Tools
    ("Tools", "Persistenz/SQLite", "persistence", "medium"),
    # Startup
    ("Startup/Bootstrap", "Provider/Ollama", "startup", "high"),
    ("Startup/Bootstrap", "RAG", "startup", "medium"),
    ("Startup/Bootstrap", "Persistenz/SQLite", "startup", "high"),
    # Observability
    ("Debug/EventBus", "Chat", "observability", "low"),
    ("Debug/EventBus", "Agentensystem", "observability", "low"),
    ("Debug/EventBus", "RAG", "observability", "low"),
    ("Metrics", "Debug/EventBus", "observability", "medium"),
    ("Metrics", "Chat", "observability", "low"),
]


def sanitize_id(s: str) -> str:
    """Gültige Node-ID für Mermaid/Graphviz."""
    import re
    return re.sub(r"[^a-zA-Z0-9_]", "_", s).strip("_") or "node"


def get_cascade_paths() -> list[list[str]]:
    """Kritischste Kaskadenpfade: Wenn X fehlschlägt, wer ist betroffen?"""
    # A → B: A hängt von B ab. Wenn B fehlschlägt, ist A betroffen.
    # dependents[B] = alle A mit A → B (die von B abhängen)
    dependents = {}  # to -> [from, ...]
    for fr, to, _, _ in DEPENDENCIES:
        dependents.setdefault(to, []).append(fr)

    def affected_when_fails(source: str, visited: set) -> set:
        """Alle Subsysteme, die betroffen sind wenn source fehlschlägt (transitiv)."""
        if source in visited:
            return set()
        visited.add(source)
        result = {source}
        for dep in dependents.get(source, []):
            result |= affected_when_fails(dep, visited)
        return result

    critical_sources = ["Provider/Ollama", "Persistenz/SQLite", "Startup/Bootstrap"]
    paths = []
    for src in critical_sources:
        all_affected = affected_when_fails(src, set())
        others = sorted(all_affected - {src})
        if others:
            paths.append([src] + others)
        elif src == "Startup/Bootstrap":
            # Startup-Fehler blockiert App-Start → alle indirekt betroffen
            paths.append([src, "(App startet nicht – alle Subsysteme blockiert)"])

    return paths


def get_top3_hebel() -> list[dict]:
    """Top-3 QA-Hebel aus dem Dependency Graph."""
    # Subsysteme mit meisten Abhängigen (höchste Kaskaden-Reichweite)
    dependents = {}
    for fr, to, _, impact in DEPENDENCIES:
        dependents.setdefault(to, []).append((fr, impact))

    # Zähle Abhängige, gewichtet nach Impact
    impact_val = {"high": 3, "medium": 2, "low": 1}
    scores = {}
    for sub in SUBSYSTEMS:
        deps = dependents.get(sub, [])
        score = sum(impact_val.get(i, 1) for _, i in deps)
        scores[sub] = (len(deps), score)

    # Sortiere nach (Anzahl, Impact-Summe)
    ranked = sorted(scores.items(), key=lambda x: (-x[1][0], -x[1][1]))
    top3 = ranked[:3]

    hebel = [
        {
            "subsystem": sub,
            "begruendung": f"{count} Subsysteme hängen von {sub} ab",
            "schritt": _get_hebel_for(sub),
        }
        for sub, (count, _) in top3
    ]
    return hebel


def _get_hebel_for(sub: str) -> str:
    """Empfohlener QA-Schritt für Subsystem."""
    hebel_map = {
        "Provider/Ollama": "Contract für Ollama-Response, degraded_mode ohne Ollama",
        "Persistenz/SQLite": "Failure-Tests für DB-Lock, Schema-Drift",
        "Startup/Bootstrap": "Init-Reihenfolge Contract, degraded_mode",
        "RAG": "Embedding-Service Failure, ChromaDB Netzwerk",
        "Chat": "Cross-Layer-Tests für UI↔Service",
        "Agentensystem": "Live-Tests für Agent-Ausführung",
        "Prompt-System": "failure_mode für Prompt-Service",
        "Debug/EventBus": "Drift-Sentinel bei neuem EventType",
        "Metrics": "Metrics unter Failure",
        "Tools": "Tool-Failure-Sichtbarkeit",
    }
    return hebel_map.get(sub, "–")


def generate_mermaid() -> str:
    """Erzeugt Mermaid flowchart."""
    lines = [
        "flowchart TB",
        "    %% QA Dependency Graph: A → B = A hängt von B ab",
        "    %% Wenn B fehlschlägt, ist A mitbetroffen",
        "",
    ]

    sub_ids = {s: sanitize_id(s) for s in SUBSYSTEMS}
    for s in SUBSYSTEMS:
        lines.append(f'    {sub_ids[s]}["{s}"]')
    lines.append("")

    for fr, to, etype, impact in DEPENDENCIES:
        if fr in sub_ids and to in sub_ids:
            lines.append(f"    {sub_ids[fr]} -->|{etype} {impact}| {sub_ids[to]}")

    return "\n".join(lines)


def generate_dot() -> str:
    """Erzeugt Graphviz DOT."""
    lines = [
        "digraph QA_Dependency {",
        "    rankdir=TB;",
        "    node [shape=box, fontname=\"DejaVu Sans\"];",
        "    edge [fontname=\"DejaVu Sans\", fontsize=9];",
        "",
    ]

    sub_ids = {s: sanitize_id(s) for s in SUBSYSTEMS}
    for s in SUBSYSTEMS:
        lines.append(f'    {sub_ids[s]} [label="{s}"];')
    lines.append("")

    for fr, to, etype, impact in DEPENDENCIES:
        if fr in sub_ids and to in sub_ids:
            lines.append(f'    {sub_ids[fr]} -> {sub_ids[to]} [label="{etype} ({impact})"];')

    lines.append("}")
    return "\n".join(lines)


def generate_md(mermaid: str, top3_paths: list, top3_hebel: list) -> str:
    """Erzeugt QA_DEPENDENCY_GRAPH.md."""
    def path_line(i: int, p: list) -> str:
        if len(p) > 1 and str(p[1]).startswith("("):
            return f"{i}. **{p[0]}** fehlschlägt → {p[1]}"
        return f"{i}. **{p[0]}** fehlschlägt → {', '.join(p[1:])} mitbetroffen"

    paths_md = "\n".join(path_line(i, p) for i, p in enumerate(top3_paths[:3], 1))
    hebel_md = "\n".join(
        f"{i}. **{h['subsystem']}**: {h['schritt']}"
        for i, h in enumerate(top3_hebel, 1)
    )

    deps_by_type = {}
    for fr, to, etype, impact in DEPENDENCIES:
        key = f"{fr} → {to}"
        deps_by_type.setdefault(etype, []).append(f"{key} ({impact})")
    wichtigste = "\n".join(
        f"- **{t}**: " + "; ".join(deps_by_type.get(t, [])[:5])
        for t in ["runtime", "startup", "persistence", "observability"]
    )

    return f"""# QA Dependency Graph – Linux Desktop Chat

**Generiert:** `python scripts/qa/generate_qa_dependency_graph.py`  
**Zweck:** Karte der Subsystem-Abhängigkeiten und Kaskadenpfade.

---

## 1. Zweck

Der Dependency Graph zeigt:

- **Abhängigkeiten:** Welches Subsystem hängt von welchem ab?
- **Kaskaden:** Wenn A fehlschlägt, welche anderen sind mitbetroffen?
- **QA-Hebel:** Welche Subsysteme haben die größte Kaskaden-Reichweite?

---

## 2. Leselogik

| Pfeil | Bedeutung |
|-------|-----------|
| **A → B** | A hängt von B ab |
| **Wenn B fehlschlägt** | A ist mitbetroffen |

| Kanten-Typ | Bedeutung |
|------------|-----------|
| runtime | Laufzeit-Abhängigkeit (LLM, RAG, Agent) |
| startup | Startreihenfolge, Bootstrap |
| persistence | Datenbank, Chroma, SQLite |
| observability | Debug, Metrics, EventBus |

| Impact | Bedeutung |
|--------|-----------|
| high | Kritisch – Fehler blockiert oder beeinträchtigt stark |
| medium | Deutlich spürbar |
| low | Geringe Auswirkung |

---

## 3. Mermaid-Graph

```mermaid
{mermaid}
```

---

## 4. Wichtigste Abhängigkeiten

{wichtigste}

---

## 5. Kritischste Kaskadenpfade

{paths_md}

---

## 6. Top-3 QA-Hebel aus dem Dependency Graph

{hebel_md}

---

## 7. Quellen

| Quelle | Inhalt |
|--------|--------|
| [QA_RISK_RADAR.md](QA_RISK_RADAR.md) | Subsystem-Liste |
| [docs/architecture.md](../architecture.md) | Datenfluss |
| Risk Radar Begründungen | Cross-Layer, Abhängigkeiten |

---

## 8. Empfehlung für QA Dependency Graph Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Automatisches Parsen aus Architektur-Docs | Graph aktuell halten |
| 2 | Impact-Scores pro Kaskadenpfad | Priorisierung verfeinern |
| 3 | Verknüpfung mit QA_PRIORITY_SCORE | Abhängigkeiten in Priorisierung einbeziehen |

---

*Generiert durch scripts/qa/generate_qa_dependency_graph.py*
"""


def main() -> int:
    """Hauptfunktion."""
    top3_paths = get_cascade_paths()
    top3_hebel = get_top3_hebel()

    mermaid = generate_mermaid()
    dot = generate_dot()
    md_content = generate_md(mermaid, top3_paths, top3_hebel)

    ARCHITECTURE_GRAPHS.mkdir(parents=True, exist_ok=True)
    (ARCHITECTURE_GRAPHS / "QA_DEPENDENCY_GRAPH.mmd").write_text(mermaid, encoding="utf-8")
    (ARCHITECTURE_GRAPHS / "QA_DEPENDENCY_GRAPH.dot").write_text(dot, encoding="utf-8")
    (ARCHITECTURE_GRAPHS / "QA_DEPENDENCY_GRAPH.md").write_text(md_content, encoding="utf-8")

    print("=" * 60)
    print("QA Dependency Graph – Summary")
    print("=" * 60)
    print()
    print("Verwendete Subsysteme:")
    for s in SUBSYSTEMS:
        print(f"  - {s}")
    print()
    print("Wichtigste Abhängigkeiten (Auszug):")
    for fr, to, etype, impact in DEPENDENCIES[:10]:
        print(f"  {fr} → {to} ({etype}, {impact})")
    print("  ...")
    print()
    print("Top-3 Kaskadenpfade:")
    for i, p in enumerate(top3_paths[:3], 1):
        if len(p) > 1 and str(p[1]).startswith("("):
            print(f"  {i}. {p[0]} fehlschlägt → {p[1]}")
        else:
            print(f"  {i}. {p[0]} fehlschlägt → {len(p)-1} Subsysteme betroffen")
    print()
    print("Top-3 QA-Hebel:")
    for h in top3_hebel:
        print(f"  - {h['subsystem']}: {h['schritt']}")
    print()
    print("Generierte Dateien:")
    print(f"  - {ARCHITECTURE_GRAPHS / 'QA_DEPENDENCY_GRAPH.md'}")
    print(f"  - {ARCHITECTURE_GRAPHS / 'QA_DEPENDENCY_GRAPH.mmd'}")
    print(f"  - {ARCHITECTURE_GRAPHS / 'QA_DEPENDENCY_GRAPH.dot'}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
