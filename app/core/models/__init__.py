"""
Core models: ModelRole, ModelRegistry, ModelOrchestrator, Router, Escalation.
"""

from app.core.models.roles import (
    ModelRole,
    DEFAULT_ROLE_MODEL_MAP,
    ROLE_DISPLAY_NAMES,
    all_roles,
    get_default_model_for_role,
    get_role_display_name,
)
from app.core.models.registry import ModelEntry, ModelRegistry, get_registry
from app.core.models.router import route_prompt
from app.core.models.escalation_manager import (
    get_escalation_model,
    get_next_escalation_role,
    LOCAL_ESCALATION_MAP,
    CLOUD_ESCALATION_MAP,
)
from app.core.models.orchestrator import ModelOrchestrator

__all__ = [
    "ModelRole",
    "DEFAULT_ROLE_MODEL_MAP",
    "ROLE_DISPLAY_NAMES",
    "all_roles",
    "get_default_model_for_role",
    "get_role_display_name",
    "ModelEntry",
    "ModelRegistry",
    "get_registry",
    "route_prompt",
    "get_escalation_model",
    "get_next_escalation_role",
    "LOCAL_ESCALATION_MAP",
    "CLOUD_ESCALATION_MAP",
    "ModelOrchestrator",
]
