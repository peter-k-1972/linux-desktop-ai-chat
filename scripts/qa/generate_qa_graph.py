#!/usr/bin/env python3
"""
QA Architecture Graph Generator – Linux Desktop Chat.

Liest docs/qa/QA_EVOLUTION_MAP.md, REGRESSION_CATALOG.md, QA_RISK_RADAR.md,
extrahiert Subsysteme, Fehlerklassen und Tests, und erzeugt:

- docs/qa/QA_ARCHITECTURE_GRAPH.mmd  (Mermaid)
- docs/qa/QA_ARCHITECTURE_GRAPH.dot  (Graphviz)
- docs/qa/QA_ARCHITECTURE_GRAPH.md   (Dokumentation mit eingebettetem Graph)

Graph-Struktur: Subsystem → Fehlerklasse → Testdomäne/Tests

Verwendung:
  python scripts/qa/generate_qa_graph.py
"""

import re
import sys
from pathlib import Path

# Projekt-Root (scripts/qa/ -> parent.parent.parent)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
from scripts.qa.qa_paths import ARTIFACTS_DASHBOARDS, GOVERNANCE, ARCHITECTURE_GRAPHS


def parse_evolution_map(content: str) -> dict:
    """Extrahiert aus QA_EVOLUTION_MAP.md: Subsystem → Fehlerklassen, Tests."""
    result = {"subsystems": {}, "error_to_subsystems": {}}

    # Tabelle "Evolution Map pro Subsystem" (Zeilen mit | **X** |)
    # Format: | **Subsystem** | Fehlerklassen | Abgesichert durch | ...
    in_evolution_table = False
    for line in content.split("\n"):
        if "Subsystem" in line and "Relevante Fehlerklassen" in line and "|" in line:
            in_evolution_table = True
            continue
        if in_evolution_table and line.strip().startswith("|") and "---" not in line:
            m = re.match(r"\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|", line)
            if m:
                subsystem = m.group(1).strip()
                fehlerklassen_raw = m.group(2).strip()
                tests_raw = m.group(3).strip()
                if subsystem and subsystem != "Subsystem":
                    fehlerklassen = [
                        x.strip()
                        for x in re.split(r"[,;]|\band\b", fehlerklassen_raw)
                        if x.strip() and not x.strip().startswith("–") and x.strip() != "–"
                    ]
                    # Bereinige Fehlerklassen (nur IDs wie ui_state_drift)
                    fehlerklassen = [f for f in fehlerklassen if re.match(r"^[a-z_]+$", f)]
                    tests = [
                        x.strip()
                        for x in re.split(r"[,;()]|\band\b", tests_raw)
                        if x.strip()
                        and len(x.strip()) > 2
                        and not x.strip().startswith("–")
                        and x.strip() != "Low"
                        and x.strip() != "Medium"
                        and x.strip() != "High"
                    ]
                    result["subsystems"][subsystem] = {
                        "fehlerklassen": fehlerklassen,
                        "tests": tests,
                    }
                    for fk in fehlerklassen:
                        if fk not in result["error_to_subsystems"]:
                            result["error_to_subsystems"][fk] = []
                        if subsystem not in result["error_to_subsystems"][fk]:
                            result["error_to_subsystems"][fk].append(subsystem)
        elif in_evolution_table and line.strip() == "":
            in_evolution_table = False

    return result


def parse_regression_catalog(content: str) -> dict:
    """Extrahiert aus REGRESSION_CATALOG.md: Fehlerklasse → Tests."""
    result = {"error_to_tests": {}, "test_domains": set()}

    # Tabellen unter "Zuordnung: Tests → Fehlerklassen"
    # Format: | datei | test | fehlerklasse |
    # Stopp vor "Historische Bugs" - andere Tabellenstruktur
    current_domain = None
    for line in content.split("\n"):
        if "## Historische Bugs" in line or "## Erweiterung" in line:
            current_domain = None
            continue
        # Domain-Header: ### failure_modes/
        m_domain = re.match(r"^###\s+(.+)/?\s*$", line)
        if m_domain:
            current_domain = m_domain.group(1).strip().rstrip("/")
            continue

        # Tabellenzeile: | test_xyz | test_abc | fehlerklasse |
        # Nur wenn Datei wie test_* aussieht (echte Testdateien)
        if line.strip().startswith("|") and "---" not in line and current_domain:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3:
                datei, test, fehlerklasse = parts[0], parts[1], parts[2]
                # Nur echte Testdateien (test_*.py) - keine Historische-Bugs-Zeilen
                if (
                    datei
                    and datei != "Datei"
                    and test
                    and test != "Test"
                    and datei.startswith("test_")
                ):
                    result["test_domains"].add(current_domain)
                    test_ref = f"{current_domain}/{datei}"
                    if fehlerklasse and fehlerklasse != "–" and fehlerklasse != "-":
                        for fk in [x.strip() for x in fehlerklasse.split(",")]:
                            fk = fk.strip()
                            if fk:
                                if fk not in result["error_to_tests"]:
                                    result["error_to_tests"][fk] = []
                                entry = f"{test_ref}::{test}"
                                if entry not in result["error_to_tests"][fk]:
                                    result["error_to_tests"][fk].append(entry)

    return result


def parse_risk_radar(content: str) -> list:
    """Extrahiert aus QA_RISK_RADAR.md: Subsystem-Liste zur Validierung."""
    subsystems = []
    in_table = False
    for line in content.split("\n"):
        if "| Subsystem | Failure Impact |" in line:
            in_table = True
            continue
        if in_table and line.strip().startswith("|") and "---" not in line:
            m = re.match(r"\|\s*\*\*([^*]+)\*\*\s*\|", line)
            if m:
                subsystems.append(m.group(1).strip())
        elif in_table and line.strip() == "":
            break
    return subsystems


def build_graph_data(evolution: dict, regression: dict, risk_subsystems: list) -> dict:
    """Baut die Graph-Daten: Subsystem → Fehlerklasse → Tests."""
    edges_seen = set()
    graph = {
        "subsystems": set(),
        "error_classes": set(),
        "tests": set(),
        "edges": [],  # (from, to, type: "sub_err" | "err_test")
    }

    def add_edge(from_n: str, to_n: str, etype: str) -> None:
        key = (from_n, to_n, etype)
        if key not in edges_seen:
            edges_seen.add(key)
            graph["edges"].append((from_n, to_n, etype))

    # Subsysteme aus Evolution Map (oder Risk Radar falls leer)
    for sub in evolution["subsystems"]:
        graph["subsystems"].add(sub)
    for sub in risk_subsystems:
        graph["subsystems"].add(sub)

    # Fehlerklassen und Kanten aus Evolution Map
    for subsystem, data in evolution["subsystems"].items():
        for fk in data["fehlerklassen"]:
            graph["error_classes"].add(fk)
            add_edge(subsystem, fk, "sub_err")

    # Tests aus Regression Catalog
    for fk, tests in regression["error_to_tests"].items():
        graph["error_classes"].add(fk)
        for t in tests:
            # Test-Node: kurzer Name (domain/file oder domain/file::test)
            node = t.split("::")[0] if "::" in t else t
            graph["tests"].add(node)
            add_edge(fk, node, "err_test")

    # Fehlerklassen aus Evolution Map, die keine Tests in Regression haben
    for fk in graph["error_classes"]:
        if fk not in regression["error_to_tests"]:
            # Prüfe ob Subsystem-Tests aus Evolution Map existieren
            for sub, data in evolution["subsystems"].items():
                if fk in data["fehlerklassen"] and data["tests"]:
                    for t in data["tests"]:
                        graph["tests"].add(t)
                        add_edge(fk, t, "err_test")

    return graph


def sanitize_id(s: str) -> str:
    """Erzeugt gültige Node-ID für Mermaid/Graphviz."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", s).strip("_") or "node"


def generate_mermaid(graph: dict) -> str:
    """Erzeugt Mermaid flowchart."""
    lines = ["flowchart TB", "    %% QA Architecture: Subsystem → Fehlerklasse → Tests", ""]

    sub_ids = {}
    err_ids = {}
    test_ids = {}

    for i, s in enumerate(sorted(graph["subsystems"])):
        sid = f"sub_{sanitize_id(s)}"
        sub_ids[s] = sid
    for i, e in enumerate(sorted(graph["error_classes"])):
        eid = f"err_{sanitize_id(e)}"
        err_ids[e] = eid
    for i, t in enumerate(sorted(graph["tests"])):
        tid = f"test_{sanitize_id(t)[:40]}"
        test_ids[t] = tid

    lines.append("    subgraph Subsysteme")
    for s in sorted(graph["subsystems"]):
        lines.append(f'        {sub_ids[s]}["{s}"]')
    lines.append("    end")
    lines.append("")
    lines.append("    subgraph Fehlerklassen")
    for e in sorted(graph["error_classes"]):
        lines.append(f'        {err_ids[e]}["{e}"]')
    lines.append("    end")
    lines.append("")
    lines.append("    subgraph Testdomaenen")
    for t in sorted(graph["tests"]):
        label = t.replace('"', "'")[:50]
        lines.append(f'        {test_ids[t]}["{label}"]')
    lines.append("    end")
    lines.append("")

    for from_n, to_n, etype in graph["edges"]:
        if etype == "sub_err" and from_n in sub_ids and to_n in err_ids:
            lines.append(f"    {sub_ids[from_n]} --> {err_ids[to_n]}")
        elif etype == "err_test" and from_n in err_ids and to_n in test_ids:
            lines.append(f"    {err_ids[from_n]} --> {test_ids[to_n]}")

    return "\n".join(lines)


def generate_dot(graph: dict) -> str:
    """Erzeugt Graphviz DOT."""
    lines = [
        "digraph QA_Architecture {",
        "    rankdir=TB;",
        "    node [shape=box, fontname=\"DejaVu Sans\"];",
        "    edge [fontname=\"DejaVu Sans\", fontsize=10];",
        "",
        "    /* Subsysteme */",
    ]

    for s in sorted(graph["subsystems"]):
        nid = sanitize_id(f"sub_{s}")
        lines.append(f'    {nid} [label="{s}", style=filled, fillcolor=lightblue];')
    lines.append("")
    lines.append("    /* Fehlerklassen */")
    for e in sorted(graph["error_classes"]):
        nid = sanitize_id(f"err_{e}")
        lines.append(f'    {nid} [label="{e}", style=filled, fillcolor=lightyellow];')
    lines.append("")
    lines.append("    /* Testdomänen / Tests */")
    for t in sorted(graph["tests"]):
        nid = sanitize_id(f"test_{t}")[:50]
        label = t.replace('"', '\\"')[:60]
        lines.append(f'    {nid} [label="{label}", style=filled, fillcolor=lightgreen];')
    lines.append("")

    for from_n, to_n, etype in graph["edges"]:
        if etype == "sub_err":
            fid = sanitize_id(f"sub_{from_n}")
            tid = sanitize_id(f"err_{to_n}")
            if fid and tid:
                lines.append(f"    {fid} -> {tid};")
        elif etype == "err_test":
            fid = sanitize_id(f"err_{from_n}")
            tid = sanitize_id(f"test_{to_n}")[:50]
            if fid and tid:
                lines.append(f"    {fid} -> {tid};")

    lines.append("}")
    return "\n".join(lines)


def analyze_anomalies(graph: dict) -> list[str]:
    """Erkennt Auffälligkeiten im QA-Netzwerk."""
    anomalies = []
    err_ohne_test = [
        e
        for e in graph["error_classes"]
        if not any(ed[0] == e and ed[2] == "err_test" for ed in graph["edges"])
    ]
    if err_ohne_test:
        anomalies.append(f"Fehlerklassen ohne direkten Test: {', '.join(err_ohne_test)}")
    sub_ohne_err = [
        s
        for s in graph["subsystems"]
        if not any(ed[0] == s and ed[2] == "sub_err" for ed in graph["edges"])
    ]
    if sub_ohne_err:
        anomalies.append(
            f"Subsysteme ohne zugeordnete Fehlerklasse: {', '.join(sub_ohne_err)}"
        )
    if not anomalies:
        anomalies.append("Keine offensichtlichen Lücken erkannt.")
    return anomalies


def generate_md_doc(graph: dict, mermaid_content: str) -> str:
    """Erzeugt QA_ARCHITECTURE_GRAPH.md Dokumentation."""
    return f"""# QA Architecture Graph – Linux Desktop Chat

**Generiert:** `python scripts/qa/generate_qa_graph.py`  
**Zweck:** Visuelle Darstellung der QA-Struktur: Subsystem → Fehlerklasse → Testdomäne/Tests.

---

## 1. Zweck

Die QA-Architekturkarte zeigt:

- **Subsysteme** (aus Risk Radar / Evolution Map)
- **Fehlerklassen** (aus Regression Catalog)
- **Testdomänen und Tests** (aus Regression Catalog, Evolution Map)

Damit wird sichtbar, welche Tests welche Fehlerklassen abdecken und welche Subsysteme davon profitieren.

---

## 2. Leselogik

| Element | Bedeutung |
|---------|-----------|
| **Subsystem** | Architektur-Baustein (Chat, RAG, Agentensystem, …) |
| **Fehlerklasse** | Kategorisierter Fehlertyp (ui_state_drift, rag_silent_failure, …) |
| **Test/Testdomäne** | Konkrete Testdatei oder -domäne (failure_modes/test_chroma_unreachable, …) |

**Richtung:** Subsystem → Fehlerklasse → Test

- Ein Subsystem ist von mehreren Fehlerklassen betroffen.
- Eine Fehlerklasse wird durch einen oder mehrere Tests abgedeckt.

---

## 3. Mermaid Graph

```mermaid
{mermaid_content}
```

---

## 4. Graphviz-Erzeugung

Die Datei `QA_ARCHITECTURE_GRAPH.dot` kann mit Graphviz gerendert werden:

```bash
# PNG
dot -Tpng docs/qa/QA_ARCHITECTURE_GRAPH.dot -o docs/qa/QA_ARCHITECTURE_GRAPH.png

# SVG
dot -Tsvg docs/qa/QA_ARCHITECTURE_GRAPH.dot -o docs/qa/QA_ARCHITECTURE_GRAPH.svg

# PDF
dot -Tpdf docs/qa/QA_ARCHITECTURE_GRAPH.dot -o docs/qa/QA_ARCHITECTURE_GRAPH.pdf
```

**Hinweis:** Bei vielen Knoten kann das Layout groß werden. Alternativ `fdp` oder `sfdp` statt `dot` für andere Layout-Algorithmen verwenden.

---

## 5. Auffälligkeiten im QA-Netzwerk

{{ANOMALIES}}

---

## 6. Quellen

| Datei | Inhalt |
|-------|--------|
| [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md) | Subsystem ↔ Fehlerklasse ↔ Abgesichert durch |
| [REGRESSION_CATALOG.md](REGRESSION_CATALOG.md) | Tests → Fehlerklassen |
| [QA_RISK_RADAR.md](QA_RISK_RADAR.md) | Subsystem-Liste, Prioritäten |

---

*Generiert am {{DATE}} durch scripts/qa/generate_qa_graph.py*
"""


def main() -> int:
    """Hauptfunktion: Liest QA-Docs, generiert Graph-Dateien, gibt Summary aus."""
    from datetime import datetime, timezone

    evolution_path = ARTIFACTS_DASHBOARDS / "QA_EVOLUTION_MAP.md"
    regression_path = GOVERNANCE / "REGRESSION_CATALOG.md"
    risk_path = ARTIFACTS_DASHBOARDS / "QA_RISK_RADAR.md"

    if not evolution_path.exists():
        print(f"FEHLER: {evolution_path} nicht gefunden.", file=sys.stderr)
        return 1
    if not regression_path.exists():
        print(f"FEHLER: {regression_path} nicht gefunden.", file=sys.stderr)
        return 1
    if not risk_path.exists():
        print(f"FEHLER: {risk_path} nicht gefunden.", file=sys.stderr)
        return 1

    evolution_content = evolution_path.read_text(encoding="utf-8")
    regression_content = regression_path.read_text(encoding="utf-8")
    risk_content = risk_path.read_text(encoding="utf-8")

    evolution = parse_evolution_map(evolution_content)
    regression = parse_regression_catalog(regression_content)
    risk_subsystems = parse_risk_radar(risk_content)

    graph = build_graph_data(evolution, regression, risk_subsystems)

    mermaid = generate_mermaid(graph)
    dot = generate_dot(graph)
    anomalies = analyze_anomalies(graph)
    anomalies_text = "\n".join(f"- {a}" for a in anomalies)
    md_doc = (
        generate_md_doc(graph, mermaid)
        .replace("{DATE}", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
        .replace("{ANOMALIES}", anomalies_text)
    )

    ARCHITECTURE_GRAPHS.mkdir(parents=True, exist_ok=True)
    (ARCHITECTURE_GRAPHS / "QA_ARCHITECTURE_GRAPH.mmd").write_text(mermaid, encoding="utf-8")
    (ARCHITECTURE_GRAPHS / "QA_ARCHITECTURE_GRAPH.dot").write_text(dot, encoding="utf-8")
    (ARCHITECTURE_GRAPHS / "QA_ARCHITECTURE_GRAPH.md").write_text(md_doc, encoding="utf-8")

    # Summary
    print("=" * 60)
    print("QA Architecture Graph – Summary")
    print("=" * 60)
    print()
    print("Erkannte Subsysteme:")
    for s in sorted(graph["subsystems"]):
        print(f"  - {s}")
    print()
    print("Erkannte Fehlerklassen:")
    for e in sorted(graph["error_classes"]):
        print(f"  - {e}")
    print()
    print("Erkannte Tests / Testdomänen:")
    for t in sorted(graph["tests"]):
        print(f"  - {t}")
    print()
    print("Statistik:")
    print(f"  Subsysteme:     {len(graph['subsystems'])}")
    print(f"  Fehlerklassen:  {len(graph['error_classes'])}")
    print(f"  Tests/Domänen:  {len(graph['tests'])}")
    print(f"  Kanten:         {len(graph['edges'])}")
    print()
    print("Generierte Dateien:")
    print(f"  - {ARCHITECTURE_GRAPHS / 'QA_ARCHITECTURE_GRAPH.mmd'}")
    print(f"  - {ARCHITECTURE_GRAPHS / 'QA_ARCHITECTURE_GRAPH.dot'}")
    print(f"  - {ARCHITECTURE_GRAPHS / 'QA_ARCHITECTURE_GRAPH.md'}")
    print()

    # Auffälligkeiten
    print("Auffälligkeiten im QA-Netzwerk:")
    for a in anomalies:
        print(f"  - {a}")
    print()
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
