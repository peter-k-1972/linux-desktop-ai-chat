"""
Agentenfarm — deklarative Vorbereitungsschicht (ohne Orchestrierung / ohne DB).

Konsumenten: ``from app.agents.farm import get_agent_farm_catalog, AgentFarmCatalog``.
"""

from app.agents.farm.loader import (
    AgentFarmCatalog,
    default_catalog_path,
    load_agent_farm_catalog,
    load_agent_farm_catalog_from_path,
    reset_agent_farm_catalog_cache,
)
from app.agents.farm.models import (
    ActivationState,
    AgentFarmRoleDefinition,
    FarmRoleKind,
    ScopeLevel,
)

get_agent_farm_catalog = load_agent_farm_catalog

__all__ = [
    "ActivationState",
    "AgentFarmCatalog",
    "AgentFarmRoleDefinition",
    "FarmRoleKind",
    "ScopeLevel",
    "default_catalog_path",
    "get_agent_farm_catalog",
    "load_agent_farm_catalog",
    "load_agent_farm_catalog_from_path",
    "reset_agent_farm_catalog_cache",
]
