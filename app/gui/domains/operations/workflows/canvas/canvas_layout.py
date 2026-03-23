"""
Deterministische Layout-Hilfen für WorkflowNode.position (ohne Qt).

Nur fehlende oder unvollständige Positionen werden gesetzt.
"""

from __future__ import annotations

from typing import Dict, Tuple

from app.workflows.models.definition import WorkflowDefinition, WorkflowNode

# Raster für automatische Platzierung (Scene-Koordinaten)
GRID_COLS = 4
CELL_W = 200.0
CELL_H = 110.0
MARGIN = 48.0


def _has_xy(pos) -> bool:
    if pos is None or not isinstance(pos, dict):
        return False
    try:
        x = pos.get("x")
        y = pos.get("y")
        return x is not None and y is not None
    except Exception:
        return False


def position_for_grid_index(i: int) -> Dict[str, float]:
    """Deterministische Position für den i-ten Knoten (sortierte Reihenfolge)."""
    col = i % GRID_COLS
    row = i // GRID_COLS
    return {"x": MARGIN + col * CELL_W, "y": MARGIN + row * CELL_H}


def ensure_missing_positions(definition: WorkflowDefinition) -> int:
    """
    Setzt position für alle Knoten ohne gültige x/y (echte Modellmutation).

    Returns:
        Anzahl der Knoten, die in diesem Aufruf neu gesetzt wurden.
        Wiederholter Aufruf auf derselben Definition: 0, sobald alle x/y vorhanden sind.
    """
    ordered = sorted(definition.nodes, key=lambda n: n.node_id)
    changed = 0
    for i, node in enumerate(ordered):
        if _has_xy(node.position):
            continue
        node.position = position_for_grid_index(i)
        changed += 1
    return changed


def positions_dict_for_definition(definition: WorkflowDefinition) -> Dict[str, Tuple[float, float]]:
    """node_id -> (x, y) für Tests / Abgleich."""
    out: Dict[str, Tuple[float, float]] = {}
    for n in definition.nodes:
        if _has_xy(n.position):
            out[n.node_id] = (float(n.position["x"]), float(n.position["y"]))
    return out


def write_position(node: WorkflowNode, x: float, y: float) -> None:
    """Schreibt Scene-Position in den Knoten."""
    node.position = {"x": float(x), "y": float(y)}
