"""JSON-Import/Export für WorkflowDefinition (schema_version erhalten)."""

from __future__ import annotations

import json
from typing import Any, Dict

from app.workflows.models.definition import WorkflowDefinition


def definition_to_json(definition: WorkflowDefinition, *, indent: int | None = 2) -> str:
    """Serialisiert Definition nach JSON (UTF-8, stabile Dict-Reihenfolge via sort_keys bei indent=None)."""
    data = definition.to_dict()
    kwargs: Dict[str, Any] = {"ensure_ascii": False}
    if indent is not None:
        kwargs["indent"] = indent
        kwargs["sort_keys"] = True
    else:
        kwargs["separators"] = (",", ":")
        kwargs["sort_keys"] = True
    return json.dumps(data, **kwargs)


def definition_from_json(text: str) -> WorkflowDefinition:
    """Parst JSON zu WorkflowDefinition; unbekannte Felder in metadata werden nicht automatisch übernommen."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Workflow-JSON muss ein Objekt sein.")
    return WorkflowDefinition.from_dict(data)


def definition_to_dict(definition: WorkflowDefinition) -> Dict[str, Any]:
    """Flaches Dict (z. B. für Snapshots)."""
    return definition.to_dict()


def definition_from_dict(data: Dict[str, Any]) -> WorkflowDefinition:
    """Dict zu Definition."""
    return WorkflowDefinition.from_dict(data)
