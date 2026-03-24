"""
Workspace Preset — Produktobjekt (Slice 1: Modell nur, keine Aktivierung).

Presets sind keine GUIs und keine Themes; sie referenzieren ``gui_id`` / ``theme_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final


class PresetReleaseStatus(StrEnum):
    """Governance-Status (Produkt/QA, nicht rein kosmetisch)."""

    DRAFT = "draft"
    CANDIDATE = "candidate"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


# Erlaubte Token — Slice 1: explizite Mengen, später erweiterbar.
LAYOUT_MODES: Final[frozenset[str]] = frozenset(
    {
        "default",
        "chat_focused",
        "operations_split",
        "presentation",
    }
)

CONTEXT_PROFILES: Final[frozenset[str]] = frozenset(
    {
        "balanced",
        "chat_focus",
        "operations_heavy",
        "deployment_focus",
        "rescue_oriented",
    }
)

OVERLAY_MODES: Final[frozenset[str]] = frozenset(
    {
        "standard",
        "minimal_hints",
        "diagnostics_friendly",
    }
)

RESCUE_BIAS: Final[frozenset[str]] = frozenset(
    {
        "none",
        "prefer_minimal_ui",
        "prefer_recovery_visible",
    }
)

DEFAULT_LAYOUT_MODE: Final[str] = "default"
DEFAULT_CONTEXT_PROFILE: Final[str] = "balanced"
DEFAULT_OVERLAY_MODE: Final[str] = "standard"
DEFAULT_RESCUE_BIAS: Final[str] = "none"


@dataclass(frozen=True, slots=True)
class WorkspacePreset:
    """
    Deklarativer Arbeitsmodus — Orchestrierung auf Produktebene.

    Pflichtfelder sind zum Start konsistent zu halten; optionale Felder haben Defaults.
    """

    preset_id: str
    display_name: str
    description: str
    gui_id: str
    theme_id: str
    start_domain: str
    requires_restart: bool
    release_status: PresetReleaseStatus
    compatible_app_versions: tuple[str, ...]
    layout_mode: str = DEFAULT_LAYOUT_MODE
    context_profile: str = DEFAULT_CONTEXT_PROFILE
    overlay_mode: str = DEFAULT_OVERLAY_MODE
    rescue_bias: str = DEFAULT_RESCUE_BIAS
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        pid = (self.preset_id or "").strip()
        if not pid:
            raise ValueError("preset_id must be non-empty")
        object.__setattr__(self, "preset_id", pid)
