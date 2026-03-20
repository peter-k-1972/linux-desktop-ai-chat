#!/usr/bin/env python3
"""
Architecture Graph – Linux Desktop Chat.

Erzeugt aus ARCHITECTURE_MAP.json eine visuelle Architekturkarte als Graphviz-DOT.
Rendert optional SVG und PNG (falls graphviz installiert).

Verwendung:
  python scripts/dev/render_architecture_graph.py
  python scripts/dev/render_architecture_graph.py --no-svg
  python scripts/dev/render_architecture_graph.py --png

Ausgabe:
  docs/04_architecture/ARCHITECTURE_GRAPH.dot (immer)
  docs/04_architecture/ARCHITECTURE_GRAPH.svg (wenn dot verfügbar)
  docs/04_architecture/ARCHITECTURE_GRAPH.png (optional, --png)

Quelle: docs/04_architecture/ARCHITECTURE_MAP.json
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_ARCH = PROJECT_ROOT / "docs" / "04_architecture"
MAP_JSON = DOCS_ARCH / "ARCHITECTURE_MAP.json"
OUTPUT_DOT = DOCS_ARCH / "ARCHITECTURE_GRAPH.dot"
OUTPUT_SVG = DOCS_ARCH / "ARCHITECTURE_GRAPH.svg"
OUTPUT_PNG = DOCS_ARCH / "ARCHITECTURE_GRAPH.png"


def _load_map() -> dict:
    """Lädt ARCHITECTURE_MAP.json."""
    if not MAP_JSON.exists():
        raise FileNotFoundError(
            f"ARCHITECTURE_MAP.json nicht gefunden: {MAP_JSON}. "
            "Bitte zuerst: python scripts/dev/architecture_map.py --json"
        )
    return json.loads(MAP_JSON.read_text(encoding="utf-8"))


def _sanitize_id(s: str) -> str:
    """Erzeugt einen DOT-sicheren Knoten-ID."""
    return s.replace(".", "_").replace("-", "_").replace(" ", "_").replace("/", "_")


def _build_dot(data: dict) -> str:
    """Baut die DOT-Datei aus der Map."""
    lines = [
        "digraph Architecture {",
        "  rankdir=TB;",
        "  splines=ortho;",
        "  nodesep=0.5;",
        "  ranksep=0.6;",
        "  fontname=\"Helvetica\";",
        "  node [fontname=\"Helvetica\", fontsize=10];",
        "  edge [fontname=\"Helvetica\", fontsize=9];",
        "",
        "  /* ========== Hauptlayer ========== */",
        "  subgraph cluster_layers {",
        "    label=\"Hauptlayer\";",
        "    style=filled;",
        "    fillcolor=\"#f8f9fa\";",
        "    penwidth=2;",
        "",
    ]

    layer_ids = {}
    for layer in data.get("layers", []):
        nid = _sanitize_id(f"layer_{layer['name']}")
        layer_ids[layer["name"]] = nid
        lines.append(f'    {nid} [label="{layer["name"]}\\n{layer["path"]}", shape=box, style=filled, fillcolor="#e9ecef"];')

    lines.extend([
        "  }",
        "",
        "  /* ========== Domänen ========== */",
        "  subgraph cluster_domains {",
        "    label=\"Domänen\";",
        "    style=filled;",
        "    fillcolor=\"#f1f3f5\";",
        "    penwidth=1;",
        "",
    ])

    domain_ids = {}
    for domain in data.get("domains", []):
        did = _sanitize_id(f"domain_{domain['name']}")
        domain_ids[domain["name"]] = did
        lines.append(f'    {did} [label="{domain["name"]}", shape=ellipse, style=filled, fillcolor="#dee2e6"];')

    lines.extend([
        "  }",
        "",
        "  /* ========== Entrypoints ========== */",
        "  subgraph cluster_entrypoints {",
        "    label=\"Entrypoints\";",
        "    style=filled;",
        "    fillcolor=\"#e7f5ff\";",
        "    penwidth=1;",
        "",
    ])

    ep_ids = {}
    for ep in data.get("entrypoints", {}).get("canonical", []):
        eid = _sanitize_id(f"ep_{ep['path'].replace('/', '_')}")
        ep_ids[ep["path"]] = eid
        short_cmd = ep["cmd"].replace("python ", "").replace(" ", "_")
        lines.append(f'    {eid} [label="{short_cmd}", shape=invhouse, fillcolor="#74c0fc"];')

    for ep in data.get("entrypoints", {}).get("legacy", []):
        eid = _sanitize_id(f"ep_legacy_{ep['path'].replace('/', '_')}")
        ep_ids[ep["path"]] = eid
        lines.append(f'    {eid} [label="archive/run_legacy_gui", shape=invhouse, fillcolor="#ffc9c9"];')

    lines.extend([
        "  }",
        "",
        "  /* ========== Registries ========== */",
        "  subgraph cluster_registries {",
        "    label=\"Registries\";",
        "    style=filled;",
        "    fillcolor=\"#fff3bf\";",
        "    penwidth=1;",
        "",
    ])

    reg_ids = {}
    for reg in data.get("registries", []):
        rid = _sanitize_id(f"reg_{reg['name'].replace(' ', '_')}")
        reg_ids[reg["name"]] = rid
        lines.append(f'    {rid} [label="{reg["name"]}", shape=component, fillcolor="#ffe066"];')

    lines.extend([
        "  }",
        "",
        "  /* ========== Governance ========== */",
        "  subgraph cluster_governance {",
        "    label=\"Policies / Guards / Drift Radar\";",
        "    style=filled;",
        "    fillcolor=\"#d3f9d8\";",
        "    penwidth=1;",
        "",
    ])

    gov_id = "governance_block"
    blocks = data.get("governance_blocks", [])
    block_count = len(blocks)
    lines.append(f'    {gov_id} [label="{block_count} Governance-Blöcke", shape=note, fillcolor="#b2f2bb"];')

    lines.extend([
        "  }",
        "",
        "  /* ========== Legacy / Transitional ========== */",
        "  subgraph cluster_legacy {",
        "    label=\"Legacy / Transitional\";",
        "    style=filled;",
        "    fillcolor=\"#ffe0e0\";",
        "    penwidth=1;",
        "",
    ])

    leg_id = "legacy_block"
    lt = data.get("legacy_transitional", {})
    temp = ", ".join(lt.get("temporarily_allowed_root", []))
    lines.append(f'    {leg_id} [label="app.main + {temp}", shape=box, style=dashed, fillcolor="#ffc9c9"];')

    lines.extend([
        "  }",
        "",
        "  /* ========== Beziehungen ========== */",
        "",
        "  /* Entrypoints -> GUI */",
    ])

    gui_id = layer_ids.get("GUI", "layer_GUI")
    for ep_path, eid in ep_ids.items():
        if "legacy" not in ep_path:
            lines.append(f"  {eid} -> {gui_id} [label=\"bootstrap\"];")
        else:
            lines.append(f"  {eid} -> {leg_id} [style=dashed, color=\"#c92a2a\"];")

    lines.extend([
        "",
        "  /* Layer-Abhängigkeiten */",
        f"  {layer_ids.get('GUI', 'layer_GUI')} -> {layer_ids.get('Services', 'layer_Services')};",
        f"  {layer_ids.get('GUI', 'layer_GUI')} -> {layer_ids.get('Core', 'layer_Core')};",
        f"  {layer_ids.get('Services', 'layer_Services')} -> {layer_ids.get('Providers', 'layer_Providers')};",
        f"  {layer_ids.get('Services', 'layer_Services')} -> {layer_ids.get('Core', 'layer_Core')};",
        f"  {layer_ids.get('Providers', 'layer_Providers')} -> {layer_ids.get('Core', 'layer_Core')};",
        "",
        "  /* Domänen -> Services/Core */",
    ])

    svc_id = layer_ids.get("Services", "layer_Services")
    core_id = layer_ids.get("Core", "layer_Core")
    for dname in ["agents", "rag", "prompts", "qa"]:
        if dname in domain_ids:
            lines.append(f"  {domain_ids[dname]} -> {svc_id};")
    for dname in ["pipelines"]:
        if dname in domain_ids:
            lines.append(f"  {domain_ids[dname]} -> {svc_id};")
    if "pipelines" not in domain_ids and "pipeline" in str(data.get("services", [])):
        pass  # pipelines als Service, kein Domain-Knoten in JSON
    for dname in ["debug", "metrics"]:
        if dname in domain_ids:
            lines.append(f"  {domain_ids[dname]} -> {core_id} [style=dotted, label=\"observability\"];")
    if "tools" in domain_ids:
        lines.append(f"  {domain_ids['tools']} -> {core_id} [style=dotted, label=\"utility\"];")

    lines.extend([
        "",
        "  /* Registries -> Layer */",
    ])

    if "Model Registry" in reg_ids:
        lines.append(f"  {reg_ids['Model Registry']} -> {core_id};")
    if "Navigation Registry" in reg_ids:
        lines.append(f"  {reg_ids['Navigation Registry']} -> {core_id};")
    if "Screen Registry" in reg_ids:
        lines.append(f"  {reg_ids['Screen Registry']} -> {gui_id};")
    if "Command Registry" in reg_ids:
        lines.append(f"  {reg_ids['Command Registry']} -> {gui_id};")
    if "Agent Registry" in reg_ids:
        lines.append(f"  {reg_ids['Agent Registry']} -> {domain_ids.get('agents', 'domain_agents')};")

    lines.extend([
        "",
        "  /* Governance als Referenz */",
        f"  {gov_id} -> {core_id} [style=dotted, color=\"#2b8a3e\", label=\"guards\"];",
        "",
        "}",
    ])

    return "\n".join(lines)


def _render_dot_to_svg(dot_path: Path, svg_path: Path) -> bool:
    """Rendert DOT zu SVG via graphviz dot."""
    dot_bin = shutil.which("dot")
    if not dot_bin:
        return False
    try:
        result = subprocess.run(
            [dot_bin, "-Tsvg", "-o", str(svg_path), str(dot_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def _render_dot_to_png(dot_path: Path, png_path: Path) -> bool:
    """Rendert DOT zu PNG via graphviz dot."""
    dot_bin = shutil.which("dot")
    if not dot_bin:
        return False
    try:
        result = subprocess.run(
            [dot_bin, "-Tpng", "-o", str(png_path), str(dot_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Architecture Graph Generator – DOT/SVG/PNG aus ARCHITECTURE_MAP.json"
    )
    parser.add_argument(
        "--no-svg",
        action="store_true",
        help="SVG-Rendering überspringen (nur DOT erzeugen)",
    )
    parser.add_argument(
        "--png",
        action="store_true",
        help="Zusätzlich PNG erzeugen",
    )
    args = parser.parse_args()

    DOCS_ARCH.mkdir(parents=True, exist_ok=True)

    try:
        data = _load_map()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    dot_content = _build_dot(data)
    OUTPUT_DOT.write_text(dot_content, encoding="utf-8")
    print(f"Erzeugt: {OUTPUT_DOT}")

    dot_available = shutil.which("dot") is not None
    if not dot_available:
        print(
            "Hinweis: graphviz (dot) nicht gefunden. SVG/PNG werden nicht erzeugt. "
            "DOT-Datei kann mit 'dot -Tsvg -o out.svg ARCHITECTURE_GRAPH.dot' manuell gerendert werden.",
            file=sys.stderr,
        )
        return 0

    if not args.no_svg:
        if _render_dot_to_svg(OUTPUT_DOT, OUTPUT_SVG):
            print(f"Erzeugt: {OUTPUT_SVG}")
        else:
            print("Warnung: SVG-Rendering fehlgeschlagen.", file=sys.stderr)

    if args.png:
        if _render_dot_to_png(OUTPUT_DOT, OUTPUT_PNG):
            print(f"Erzeugt: {OUTPUT_PNG}")
        else:
            print("Warnung: PNG-Rendering fehlgeschlagen.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
