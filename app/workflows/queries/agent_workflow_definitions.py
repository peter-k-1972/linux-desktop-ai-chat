"""
Welche Workflow-Definitionen referenzieren einen Agenten (agent-Knoten).

Rein lesend; für R2 Deep Links / Einordnung.
"""

from __future__ import annotations

from typing import List

from app.workflows.models.definition import WorkflowDefinition


def definition_references_agent(
    definition: WorkflowDefinition,
    *,
    agent_id: str | None,
    slug: str | None,
) -> bool:
    """True, wenn ein aktivierter agent-Knoten dieselbe agent_id oder agent_slug nutzt."""
    aid = (agent_id or "").strip()
    sl = (slug or "").strip()
    if not aid and not sl:
        return False
    for node in definition.nodes:
        if node.node_type != "agent" or not node.is_enabled:
            continue
        cfg = node.config or {}
        cfg_slug = str(cfg.get("agent_slug") or "").strip()
        cfg_id = str(cfg.get("agent_id") or "").strip()
        if sl and cfg_slug == sl:
            return True
        if aid and cfg_id == aid:
            return True
    return False


def list_workflow_ids_referencing_agent(
    definitions: List[WorkflowDefinition],
    *,
    agent_id: str | None,
    slug: str | None,
) -> List[str]:
    """Stable sortierte workflow_ids (lexikographisch)."""
    out = [
        d.workflow_id
        for d in definitions
        if definition_references_agent(d, agent_id=agent_id, slug=slug)
    ]
    return sorted(set(out))
