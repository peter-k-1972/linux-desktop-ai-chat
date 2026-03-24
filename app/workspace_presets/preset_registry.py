"""
Zentrale Workspace-Preset-Registry (codebasiert, Slice 1).

Kein Overlay, keine Persistenz, kein Relaunch — nur registrierte Produktobjekte.
"""

from __future__ import annotations

from typing import Final

from app.application_release_info import APP_RELEASE_VERSION

from app.workspace_presets.preset_models import PresetReleaseStatus, WorkspacePreset
from app.workspace_presets.preset_validation import assert_registered_presets_valid

# Kanonische Preset-IDs (Smoke / QA)
PRESET_ID_CHAT_FOCUS: Final[str] = "chat_focus"
PRESET_ID_WORKFLOW_STUDIO: Final[str] = "workflow_studio"
PRESET_ID_PROJECT_COMMAND_CENTER: Final[str] = "project_command_center"
PRESET_ID_AGENT_OPERATIONS: Final[str] = "agent_operations"
PRESET_ID_RESCUE_MINIMAL: Final[str] = "rescue_minimal"

_CANONICAL_PRESET_IDS: Final[tuple[str, ...]] = (
    PRESET_ID_CHAT_FOCUS,
    PRESET_ID_WORKFLOW_STUDIO,
    PRESET_ID_PROJECT_COMMAND_CENTER,
    PRESET_ID_AGENT_OPERATIONS,
    PRESET_ID_RESCUE_MINIMAL,
)

# Kompatibilität: aktuelle App-Release-Zeile als untere Schranke (Slice 1 — grob).
_DEFAULT_COMPAT: Final[tuple[str, ...]] = (APP_RELEASE_VERSION,)


REGISTERED_PRESETS_BY_ID: dict[str, WorkspacePreset] = {
    PRESET_ID_CHAT_FOCUS: WorkspacePreset(
        preset_id=PRESET_ID_CHAT_FOCUS,
        display_name="Chat Focus",
        description="Chat-first workspace: standard widget shell, light theme, Chat operations workspace.",
        gui_id="default_widget_gui",
        theme_id="light_default",
        start_domain="operations_chat",
        layout_mode="chat_focused",
        context_profile="chat_focus",
        overlay_mode="standard",
        rescue_bias="none",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=_DEFAULT_COMPAT,
        tags=("workspace", "chat"),
    ),
    PRESET_ID_WORKFLOW_STUDIO: WorkspacePreset(
        preset_id=PRESET_ID_WORKFLOW_STUDIO,
        display_name="Workflow Studio",
        description="Workflow editor and runs: widget shell, workbench theme, Workflows workspace.",
        gui_id="default_widget_gui",
        theme_id="workbench",
        start_domain="operations_workflows",
        layout_mode="operations_split",
        context_profile="operations_heavy",
        overlay_mode="standard",
        rescue_bias="none",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=_DEFAULT_COMPAT,
        tags=("workspace", "workflows"),
    ),
    PRESET_ID_PROJECT_COMMAND_CENTER: WorkspacePreset(
        preset_id=PRESET_ID_PROJECT_COMMAND_CENTER,
        display_name="Project Command Center",
        description="Projects and system overview entry: widget shell, dark theme, Command Center nav entry.",
        gui_id="default_widget_gui",
        theme_id="dark_default",
        start_domain="command_center",
        layout_mode="default",
        context_profile="balanced",
        overlay_mode="standard",
        rescue_bias="none",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=_DEFAULT_COMPAT,
        tags=("workspace", "projects", "command_center"),
    ),
    PRESET_ID_AGENT_OPERATIONS: WorkspacePreset(
        preset_id=PRESET_ID_AGENT_OPERATIONS,
        display_name="Agent Operations",
        description="Agent Tasks operations workspace with emphasis on agent tooling.",
        gui_id="default_widget_gui",
        theme_id="dark_default",
        start_domain="operations_agent_tasks",
        layout_mode="operations_split",
        context_profile="operations_heavy",
        overlay_mode="diagnostics_friendly",
        rescue_bias="none",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=_DEFAULT_COMPAT,
        tags=("workspace", "agents"),
    ),
    PRESET_ID_RESCUE_MINIMAL: WorkspacePreset(
        preset_id=PRESET_ID_RESCUE_MINIMAL,
        display_name="Rescue Minimal",
        description="Conservative shell for support: widget GUI, light theme, Settings root; recovery-oriented context (Slice 1: declarative only).",
        gui_id="default_widget_gui",
        theme_id="light_default",
        start_domain="settings",
        layout_mode="default",
        context_profile="rescue_oriented",
        overlay_mode="minimal_hints",
        rescue_bias="prefer_recovery_visible",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=_DEFAULT_COMPAT,
        tags=("rescue", "support", "minimal"),
    ),
}

assert_registered_presets_valid(REGISTERED_PRESETS_BY_ID)


def get_workspace_preset(preset_id: str) -> WorkspacePreset:
    """Liefert ein Preset oder wirft KeyError."""
    key = (preset_id or "").strip()
    if key not in REGISTERED_PRESETS_BY_ID:
        raise KeyError(f"Unknown workspace preset_id: {preset_id!r}")
    return REGISTERED_PRESETS_BY_ID[key]


def list_workspace_preset_ids() -> tuple[str, ...]:
    """Alle registrierten ``preset_id`` (sortiert)."""
    return tuple(sorted(REGISTERED_PRESETS_BY_ID.keys()))


def list_workspace_presets() -> tuple[WorkspacePreset, ...]:
    """Alle Presets, sortiert nach ``preset_id``."""
    return tuple(REGISTERED_PRESETS_BY_ID[k] for k in sorted(REGISTERED_PRESETS_BY_ID))


def list_approved_workspace_presets() -> tuple[WorkspacePreset, ...]:
    """Presets mit ``release_status == approved`` (für spätere Standard-Auswahl-UI)."""
    return tuple(
        p for p in list_workspace_presets() if p.release_status == PresetReleaseStatus.APPROVED
    )


def get_default_workspace_preset_id() -> str:
    """
    Produkt-Default-Preset-ID (Slice 1: konservativ ``chat_focus``).

    Später: aus Settings / Policy — hier nur kanonischer Einstieg.
    """
    return PRESET_ID_CHAT_FOCUS


def canonical_workspace_preset_ids() -> tuple[str, ...]:
    """Die in Slice 1 definierten kanonischen Preset-IDs."""
    return _CANONICAL_PRESET_IDS
