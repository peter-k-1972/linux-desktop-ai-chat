#!/usr/bin/env python3
"""
Schreibt das kanonische 24×24-Outline-Icon-Set nach resources/icons/.

Einmal ausführen aus Projektroot:
  python3 tools/generate_canonical_icon_set.py

Style: viewBox 0 0 24 24, stroke 1.5, round caps, currentColor, fill none.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS_ROOT = ROOT / "resources" / "icons"

SVG_HEAD = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="1.5" '
    'stroke-linecap="round" stroke-linejoin="round">'
)
SVG_TAIL = "</svg>\n"

# (category, filename) -> inner markup (paths only, no root svg)
ICONS: list[tuple[str, str, str]] = [
    # --- navigation ---
    (
        "navigation",
        "dashboard.svg",
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    ),
    (
        "navigation",
        "chat.svg",
        '<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5H8l-5 2.5V11.5a8.5 8.5 0 0 1 8.5-8.5h5A8.5 8.5 0 0 1 21 11.5z"/>',
    ),
    (
        "navigation",
        "control.svg",
        '<path d="M4 6h4M14 6h6M4 12h2M10 12h10M6 6v4M16 6v4M4 12v6M12 12v6"/>'
        '<circle cx="10" cy="6" r="2"/><circle cx="8" cy="12" r="2"/><circle cx="16" cy="12" r="2"/>',
    ),
    (
        "navigation",
        "shield.svg",
        '<path d="M12 3 20 7v6c0 5-3.5 9-8 10-4.5-1-8-5-8-10V7l8-4z"/>',
    ),
    (
        "navigation",
        "activity.svg",
        '<path d="M22 12h-4l-3 9L9 3 6 12H2"/>',
    ),
    (
        "navigation",
        "gear.svg",
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41"/>',
    ),
    # --- objects ---
    (
        "objects",
        "agents.svg",
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    ),
    (
        "objects",
        "models.svg",
        '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>'
        '<path d="M3.3 7L12 12l8.7-5"/><path d="M12 22V12"/>',
    ),
    (
        "objects",
        "providers.svg",
        '<path d="M12 22v-5"/><path d="M9 8V2"/><path d="M15 8V2"/><path d="M18 8v5a6 6 0 0 1-12 0V8Z"/>'
        '<rect x="6" y="8" width="12" height="5" rx="1"/>',
    ),
    (
        "objects",
        "tools.svg",
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    ),
    (
        "objects",
        "data_stores.svg",
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M3 5v6c0 1.7 4 3 9 3s9-1.3 9-3V5"/>'
        '<path d="M3 11v6c0 1.7 4 3 9 3s9-1.3 9-3v-6"/>',
    ),
    (
        "objects",
        "knowledge.svg",
        '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
        '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    ),
    (
        "objects",
        "prompt_studio.svg",
        '<path d="M21 15a4 4 0 0 1-4 4H7l-4 4V7a4 4 0 0 1 4-4h10"/>'
        '<path d="M16 3v10"/><path d="M13 6h6"/><path d="M13 10h4"/>',
    ),
    (
        "objects",
        "projects.svg",
        '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    ),
    (
        "objects",
        "test_inventory.svg",
        '<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>'
        '<path d="M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v0a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2z"/>'
        '<path d="M9 12h6"/><path d="M9 16h6"/><path d="M9 8h2"/>',
    ),
    (
        "objects",
        "coverage_map.svg",
        '<polygon points="1 6 8 2 15 6 22 2 22 18 15 22 8 18 1 22 1 6"/>'
        '<line x1="8" y1="2" x2="8" y2="18"/><line x1="15" y1="6" x2="15" y2="22"/>',
    ),
    (
        "objects",
        "gap_analysis.svg",
        '<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 12v8"/><path d="M22 20V8"/>'
        '<path d="M7 14h6"/><path d="M13 10h6"/>',
    ),
    (
        "objects",
        "incidents.svg",
        '<path d="M10.3 3.3a2 2 0 0 1 3.4 0l8.4 14.5a2 2 0 0 1-1.7 3H3.6a2 2 0 0 1-1.7-3z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/><circle cx="12" cy="16" r="1"/>',
    ),
    (
        "objects",
        "replay_lab.svg",
        '<polygon points="7 4 19 12 7 20 7 4"/>'
        '<path d="M3 12a9 9 0 0 1 9-9"/><path d="M3 3v6h6"/>',
    ),
    (
        "objects",
        "appearance.svg",
        '<circle cx="12" cy="12" r="4"/>'
        '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    ),
    (
        "objects",
        "system.svg",
        '<rect x="4" y="4" width="16" height="16" rx="2"/>'
        '<rect x="9" y="9" width="6" height="6"/>'
        '<path d="M9 2v2M15 2v2M9 20v2M15 20v2M20 9h2M20 14h2M2 9h2M2 14h2"/>',
    ),
    (
        "objects",
        "advanced.svg",
        '<path d="M4 21v-7"/><path d="M4 10V3"/><path d="M12 21v-9"/><path d="M12 8V3"/><path d="M20 21v-5"/><path d="M20 12V3"/>'
        '<path d="M2 14h4"/><path d="M10 10h4"/><path d="M18 16h4"/>',
    ),
    # --- actions ---
    ("actions", "add.svg", '<path d="M12 5v14M5 12h14"/>'),
    ("actions", "remove.svg", '<path d="M5 12h14"/>'),
    (
        "actions",
        "edit.svg",
        '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    ),
    (
        "actions",
        "refresh.svg",
        '<path d="M21 12a9 9 0 1 1-3-6.7"/>'
        '<path d="M21 3v6h-6"/>',
    ),
    (
        "actions",
        "search.svg",
        '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    ),
    (
        "actions",
        "filter.svg",
        '<path d="M22 3H2l8 9v9l4 2v-11l8-9z"/>',
    ),
    ("actions", "run.svg", '<polygon points="8 5 19 12 8 19 8 5"/>'),
    ("actions", "stop.svg", '<rect x="6" y="6" width="12" height="12" rx="1"/>'),
    (
        "actions",
        "save.svg",
        '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>'
        '<path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/>',
    ),
    (
        "actions",
        "deploy.svg",
        '<path d="M12 3v9"/>'
        '<path d="m8 7 4-4 4 4"/>'
        '<path d="M5 19a7 7 0 0 1 14 0"/>'
        '<path d="M8 19v2l4 2 4-2v-2"/>',
    ),
    (
        "actions",
        "pin.svg",
        '<path d="M12 17v5"/><path d="M9 10.5a3 3 0 0 1 6 0c0 2.5-3 4.5-3 4.5s-3-2-3-4.5z"/>'
        '<circle cx="12" cy="8" r="2"/>',
    ),
    (
        "actions",
        "open.svg",
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<path d="M14 2v6h6"/><path d="M10 12h8"/><path d="M10 16h5"/>',
    ),
    (
        "actions",
        "link_out.svg",
        '<path d="M18 13v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
        '<path d="M15 3h6v6"/><path d="M10 14 21 3"/>',
    ),
    # --- states ---
    (
        "states",
        "success.svg",
        '<circle cx="12" cy="12" r="10"/>'
        '<path d="m9 12 2 2 4-4"/>',
    ),
    (
        "states",
        "warning.svg",
        '<path d="M10.3 3.3a2 2 0 0 1 3.4 0l8.4 14.5a2 2 0 0 1-1.7 3H3.6a2 2 0 0 1-1.7-3z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/><circle cx="12" cy="17" r="1"/>',
    ),
    (
        "states",
        "error.svg",
        '<circle cx="12" cy="12" r="10"/>'
        '<path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    ),
    (
        "states",
        "running.svg",
        '<path d="M21 12a9 9 0 1 1-6.22-8.55"/>'
        '<path d="M21 3v6h-6"/>',
    ),
    (
        "states",
        "idle.svg",
        '<path d="M12 2a10 10 0 1 0 10 10"/>'
        '<path d="M12 6v6l4 2"/>',
    ),
    (
        "states",
        "paused.svg",
        '<rect x="6" y="5" width="4" height="14" rx="1"/>'
        '<rect x="14" y="5" width="4" height="14" rx="1"/>',
    ),
    # --- monitoring ---
    (
        "monitoring",
        "eventbus.svg",
        '<circle cx="5" cy="12" r="2"/><circle cx="12" cy="7" r="2"/><circle cx="19" cy="12" r="2"/>'
        '<circle cx="12" cy="17" r="2"/>'
        '<path d="M7 11l3-2M14 9l3 2M14 15l3-2M7 13l3 2"/>',
    ),
    (
        "monitoring",
        "logs.svg",
        '<path d="M8 6h12M8 10h12M8 14h8M8 18h10"/>'
        '<rect x="3.5" y="5" width="2.5" height="14" rx="0.5"/>',
    ),
    (
        "monitoring",
        "metrics.svg",
        '<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-6"/><path d="M22 20V8"/>',
    ),
    (
        "monitoring",
        "llm_calls.svg",
        '<path d="M12 2v4"/><path d="M12 18v4"/>'
        '<path d="m4.9 4.9 2.8 2.8"/><path d="m16.3 16.3 2.8 2.8"/>'
        '<path d="M2 12h4"/><path d="M18 12h4"/>'
        '<circle cx="12" cy="12" r="3"/>',
    ),
    (
        "monitoring",
        "agent_activity.svg",
        '<path d="M22 12h-4l-3 7-4-14-3 7H2"/>',
    ),
    (
        "monitoring",
        "system_graph.svg",
        '<circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/>'
        '<circle cx="12" cy="18" r="2"/><circle cx="12" cy="11" r="2"/>'
        '<path d="M7 7.5l3.5 2.5M16 7.5l-3.5 2.5M12 13v3"/>',
    ),
    (
        "monitoring",
        "qa_runtime.svg",
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>'
        '<path d="m4.9 4.9 2.2 2.2M17.1 17.1l2.2 2.2M4.9 19.1l2.2-2.2M17.1 6.9l2.2-2.2"/>',
    ),
    # --- system ---
    (
        "system",
        "help.svg",
        '<circle cx="12" cy="12" r="10"/>'
        '<path d="M9.1 9a3 3 0 1 1 5.8 1c0 2-3 2-3 4"/>'
        '<circle cx="12" cy="17" r="1"/>',
    ),
    (
        "system",
        "info.svg",
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="12" y1="16" x2="12" y2="11"/>'
        '<circle cx="12" cy="8" r="1"/>',
    ),
    (
        "system",
        "send.svg",
        '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    ),
    # --- ai ---
    (
        "ai",
        "sparkles.svg",
        '<path d="M12 3 13.2 6.6 17 8l-3.8 1.4L12 13l-1.2-3.6L7 8l3.8-1.4L12 3z"/>'
        '<path d="M19 15l.5 1.5 1.5.5-1.5.5-.5 1.5-.5-1.5-1.5-.5 1.5-.5.5-1.5z"/>',
    ),
    # --- workflow ---
    (
        "workflow",
        "graph.svg",
        '<circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/>'
        '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>'
        '<path d="M8 6h8M8 18h8M6 8v8M18 8v8"/>',
    ),
    (
        "workflow",
        "pipeline.svg",
        '<rect x="2" y="8" width="5" height="8" rx="1"/>'
        '<rect x="9.5" y="8" width="5" height="8" rx="1"/>'
        '<rect x="17" y="8" width="5" height="8" rx="1"/>'
        '<path d="M7 12h2.5M14.5 12h2.5"/>',
    ),
    # --- data ---
    (
        "data",
        "dataset.svg",
        '<ellipse cx="12" cy="5" rx="8" ry="2.5"/>'
        '<path d="M4 5v4c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5V5"/>'
        '<path d="M4 9v4c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5V9"/>',
    ),
    (
        "data",
        "folder.svg",
        '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h11a2 2 0 0 1 2 2z"/>',
    ),
]


def main() -> int:
    for category, filename, body in ICONS:
        out = ICONS_ROOT / category / filename
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(SVG_HEAD + body + SVG_TAIL, encoding="utf-8")
        print("wrote", out.relative_to(ROOT))
    print(f"Done: {len(ICONS)} icons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
