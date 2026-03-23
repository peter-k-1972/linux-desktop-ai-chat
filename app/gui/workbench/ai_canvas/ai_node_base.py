"""
Runtime node instances placed on the AI canvas graph.

``type_id`` values are registered in :mod:`ai_node_registry`; positions are scene
coordinates until a layout engine exists.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


def new_node_id() -> str:
    return uuid.uuid4().hex[:12]


@dataclass(slots=True)
class AiNodeInstance:
    node_id: str
    type_id: str
    title: str
    x: float
    y: float
