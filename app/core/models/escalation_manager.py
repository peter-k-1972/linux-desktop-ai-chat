"""
Eskalationslogik für den Desktop-Chat.

Steuert den Wechsel zu stärkeren Modellen bei Bedarf.
"""

from typing import Optional, Set

from app.core.models.roles import ModelRole
from app.core.models.registry import ModelRegistry, get_registry


# Eskalationspfade: aktuelle Rolle -> nächste Eskalationsstufe
LOCAL_ESCALATION_MAP = {
    ModelRole.FAST: ModelRole.DEFAULT,
    ModelRole.DEFAULT: ModelRole.THINK,
    ModelRole.CHAT: ModelRole.DEFAULT,
    ModelRole.CODE: ModelRole.THINK,  # komplexer Code -> THINK
    ModelRole.THINK: None,  # THINK ist lokal maximal
}

# Cloud-Eskalation: wenn Cloud aktiv
CLOUD_ESCALATION_MAP = {
    ModelRole.THINK: ModelRole.OVERKILL,
    ModelRole.CODE: ModelRole.OVERKILL,  # oder qwen3-coder, aber OVERKILL als generische Cloud-Stufe
    ModelRole.DEFAULT: ModelRole.OVERKILL,
}


def get_next_escalation_role(
    current_role: ModelRole,
    cloud_enabled: bool = False,
    from_code: bool = False,
) -> Optional[ModelRole]:
    """
    Liefert die nächste Eskalationsrolle.

    Args:
        current_role: Aktuelle Rolle
        cloud_enabled: Cloud-Eskalation erlaubt
        from_code: Eskalation kam von CODE (optional: qwen3-coder statt OVERKILL)

    Returns:
        Nächste Rolle oder None, wenn keine Eskalation möglich
    """
    if cloud_enabled:
        next_role = CLOUD_ESCALATION_MAP.get(current_role)
        if next_role is not None:
            return next_role
        # Fallback: lokale Eskalation
    return LOCAL_ESCALATION_MAP.get(current_role)


def get_escalation_model(
    from_role: ModelRole,
    registry: Optional[ModelRegistry] = None,
    available_local: Optional[Set[str]] = None,
    available_cloud: Optional[Set[str]] = None,
    cloud_enabled: bool = False,
) -> Optional[str]:
    """
    Liefert die Modell-ID für die nächste Eskalationsstufe.

    Returns:
        Modell-ID oder None, wenn keine Eskalation verfügbar
    """
    reg = registry or get_registry()
    next_role = get_next_escalation_role(from_role, cloud_enabled=cloud_enabled)
    if next_role is None:
        return None
    return reg.get_best_model_for_role(
        next_role,
        available_local=available_local,
        available_cloud=available_cloud,
        prefer_local=not cloud_enabled,
        cloud_enabled=cloud_enabled,
    )
