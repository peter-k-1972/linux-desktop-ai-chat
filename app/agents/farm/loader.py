"""
Lädt und validiert den Agentenfarm-Katalog aus JSON.

Keine Datenbank, keine GUI — nur verfügbare, geprüfte Definitionen für spätere Nutzung.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from app.agents.farm.models import (
    ActivationState,
    AgentFarmRoleDefinition,
    FarmRoleKind,
    ScopeLevel,
)

_DEFAULT_CATALOG_PATH = Path(__file__).resolve().parent / "default_catalog.json"

_SCOPE_VALUES = {e.value for e in ScopeLevel}
_KIND_VALUES = {e.value for e in FarmRoleKind}
_ACTIVATION_VALUES = {e.value for e in ActivationState}


@dataclass(frozen=True)
class AgentFarmCatalog:
    """Gebündelter Katalog inkl. Index."""

    schema_version: int
    catalog_id: str
    description: str
    roles: Tuple[AgentFarmRoleDefinition, ...]

    def by_role_id(self) -> Dict[str, AgentFarmRoleDefinition]:
        return {r.agent_role_id: r for r in self.roles}


_catalog_cache: Optional[AgentFarmCatalog] = None
_catalog_path_used: Optional[Path] = None


def _require_str(d: Mapping[str, Any], key: str, *, ctx: str) -> str:
    v = d.get(key)
    if v is None or not isinstance(v, str) or not str(v).strip():
        raise ValueError(f"{ctx}: Feld {key!r} muss ein nicht-leerer String sein")
    return str(v).strip()


def _optional_str(d: Mapping[str, Any], key: str) -> Optional[str]:
    v = d.get(key)
    if v is None:
        return None
    if not isinstance(v, str):
        raise ValueError(f"Feld {key!r} muss ein String oder null sein")
    s = v.strip()
    return s if s else None


def _str_list(d: Mapping[str, Any], key: str, *, ctx: str) -> Tuple[str, ...]:
    v = d.get(key)
    if v is None:
        return ()
    if not isinstance(v, list):
        raise ValueError(f"{ctx}: {key!r} muss eine Liste von Strings sein")
    out: List[str] = []
    for i, item in enumerate(v):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{ctx}: {key!r}[{i}] muss ein nicht-leerer String sein")
        out.append(item.strip())
    return tuple(out)


def _parse_role(raw: Mapping[str, Any], index: int) -> AgentFarmRoleDefinition:
    ctx = f"roles[{index}]"
    agent_role_id = _require_str(raw, "agent_role_id", ctx=ctx)
    sl_raw = _require_str(raw, "scope_level", ctx=ctx)
    if sl_raw not in _SCOPE_VALUES:
        raise ValueError(f"{ctx}: ungültige scope_level {sl_raw!r}, erlaubt: {sorted(_SCOPE_VALUES)}")
    scope_level = ScopeLevel(sl_raw)

    fk_raw = _require_str(raw, "farm_role_kind", ctx=ctx)
    if fk_raw not in _KIND_VALUES:
        raise ValueError(f"{ctx}: ungültige farm_role_kind {fk_raw!r}, erlaubt: {sorted(_KIND_VALUES)}")
    farm_role_kind = FarmRoleKind(fk_raw)

    display_name = _require_str(raw, "display_name", ctx=ctx)
    functional_role = _require_str(raw, "functional_role", ctx=ctx)
    responsibility_scope = _require_str(raw, "responsibility_scope", ctx=ctx)

    input_types = _str_list(raw, "input_types", ctx=ctx)
    output_types = _str_list(raw, "output_types", ctx=ctx)
    allowed_workflow_ids = _str_list(raw, "allowed_workflow_ids", ctx=ctx)

    esc = _optional_str(raw, "escalation_target_role_id")

    act_raw = _require_str(raw, "activation", ctx=ctx)
    if act_raw not in _ACTIVATION_VALUES:
        raise ValueError(f"{ctx}: ungültige activation {act_raw!r}, erlaubt: {sorted(_ACTIVATION_VALUES)}")
    activation = ActivationState(act_raw)

    iv = raw.get("is_standard")
    if not isinstance(iv, bool):
        raise ValueError(f"{ctx}: is_standard muss ein Boolean sein")

    allowed_keys = {
        "agent_role_id",
        "scope_level",
        "farm_role_kind",
        "display_name",
        "functional_role",
        "responsibility_scope",
        "input_types",
        "output_types",
        "allowed_workflow_ids",
        "escalation_target_role_id",
        "activation",
        "is_standard",
    }
    extra = set(raw.keys()) - allowed_keys
    if extra:
        raise ValueError(f"{ctx}: unbekannte Schlüssel: {sorted(extra)}")

    return AgentFarmRoleDefinition(
        agent_role_id=agent_role_id,
        scope_level=scope_level,
        farm_role_kind=farm_role_kind,
        display_name=display_name,
        functional_role=functional_role,
        responsibility_scope=responsibility_scope,
        input_types=input_types,
        output_types=output_types,
        allowed_workflow_ids=allowed_workflow_ids,
        escalation_target_role_id=esc,
        activation=activation,
        is_standard=iv,
    )


def load_agent_farm_catalog_from_path(path: Path) -> AgentFarmCatalog:
    """Lädt und validiert einen Katalog von der angegebenen Datei."""
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Katalog-Root muss ein JSON-Objekt sein")

    sv = data.get("schema_version")
    if not isinstance(sv, int) or sv < 1:
        raise ValueError("schema_version muss eine positive Ganzzahl sein")

    catalog_id = _require_str(data, "catalog_id", ctx="root")
    description = data.get("description")
    if description is None:
        description = ""
    if not isinstance(description, str):
        raise ValueError("description muss ein String sein")

    roles_raw = data.get("roles")
    if not isinstance(roles_raw, list):
        raise ValueError("roles muss eine Liste sein")

    root_keys = {"schema_version", "catalog_id", "description", "roles"}
    extra_root = set(data.keys()) - root_keys
    if extra_root:
        raise ValueError(f"Unbekannte Root-Schlüssel: {sorted(extra_root)}")

    seen_ids: set[str] = set()
    roles: List[AgentFarmRoleDefinition] = []
    for i, item in enumerate(roles_raw):
        if not isinstance(item, dict):
            raise ValueError(f"roles[{i}] muss ein Objekt sein")
        role = _parse_role(item, i)
        if role.agent_role_id in seen_ids:
            raise ValueError(f"doppelte agent_role_id: {role.agent_role_id!r}")
        seen_ids.add(role.agent_role_id)
        roles.append(role)

    return AgentFarmCatalog(
        schema_version=sv,
        catalog_id=catalog_id,
        description=description.strip(),
        roles=tuple(roles),
    )


def load_agent_farm_catalog(*, catalog_path: Optional[Path] = None) -> AgentFarmCatalog:
    """
    Lazy geladener Standard-Katalog (Singleton pro Prozess).

    Args:
        catalog_path: Optionaler Pfad; Standard ist ``default_catalog.json`` neben diesem Modul.
    """
    global _catalog_cache, _catalog_path_used
    path = Path(catalog_path) if catalog_path is not None else _DEFAULT_CATALOG_PATH
    if _catalog_cache is not None and _catalog_path_used == path:
        return _catalog_cache
    cat = load_agent_farm_catalog_from_path(path)
    _catalog_cache = cat
    _catalog_path_used = path.resolve()
    return _catalog_cache


def reset_agent_farm_catalog_cache() -> None:
    """Nur für Tests: Singleton zurücksetzen."""
    global _catalog_cache, _catalog_path_used
    _catalog_cache = None
    _catalog_path_used = None


def default_catalog_path() -> Path:
    """Pfad zur mitgelieferten Standard-Datei."""
    return _DEFAULT_CATALOG_PATH
