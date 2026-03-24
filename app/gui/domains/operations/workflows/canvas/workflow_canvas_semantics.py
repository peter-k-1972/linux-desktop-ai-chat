"""Bezeichnungen für Prozessdiagramm (Knotenrollen)."""

from __future__ import annotations


def node_role_caption(node_type: str) -> str:
    """Kurzbezeichnung für die Planungstafel (Agent, Prompt, Tool, Modell, …)."""
    t = (node_type or "").strip().lower()
    return {
        "agent": "Agent",
        "prompt_build": "Prompt",
        "tool_call": "Tool",
        "chain_delegate": "Modell",
        "context_load": "Kontext",
        "start": "Start",
        "end": "Ende",
        "noop": "Prozess",
    }.get(t, t or "Knoten")
