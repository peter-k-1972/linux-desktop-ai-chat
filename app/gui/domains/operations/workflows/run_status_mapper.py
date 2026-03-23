"""
Reine Zuordnung Workflow-Definition ↔ NodeRun-Status für Canvas und Tests.

Keine Qt-Abhängigkeit; Status kommt ausschließlich aus NodeRun-Daten.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from app.workflows.models.run import NodeRun
from app.workflows.status import NodeRunStatus


def latest_node_run_by_node_id(node_runs: List[NodeRun]) -> Dict[str, NodeRun]:
    """Letzter NodeRun pro node_id (Reihenfolge: spätere Listeneinträge überschreiben)."""
    out: Dict[str, NodeRun] = {}
    for nr in node_runs:
        out[nr.node_id] = nr
    return out


def canvas_status_by_node_id(
    definition_node_ids: List[str],
    node_runs: List[NodeRun],
) -> Dict[str, Optional[NodeRunStatus]]:
    """
    Für jeden Knoten der Definition: Status aus dem Run, oder None wenn kein NodeRun existiert
    (Knoten im Lauf nicht erreicht / nicht protokolliert).
    """
    by_nid = latest_node_run_by_node_id(node_runs)
    return {nid: (by_nid[nid].status if nid in by_nid else None) for nid in definition_node_ids}


def find_node_run_for_node(node_runs: List[NodeRun], node_id: str) -> Optional[NodeRun]:
    """Letzter NodeRun zu node_id."""
    by_nid = latest_node_run_by_node_id(node_runs)
    return by_nid.get(node_id)
