"""
GUI Capability Descriptor — produktseitige Deklaration unterstützter Bereiche.

Capabilities beschreiben die GUI-/Produktintegration (keine Theme-Dekoration).
Siehe ``docs/architecture/GUI_REGISTRY.md``.

Hinweis: Das **Global Overlay** ist eine **Produktfunktion** (installiert durch
``run_gui_shell`` / ``run_qml_shell``), keine GUI-Capability — daher kein
``supports_global_overlay``-Feld mehr.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

# Bekannte Capability-Attributnamen (für ``gui_supports`` / externe Checks).
KNOWN_GUI_CAPABILITY_NAMES: Final[tuple[str, ...]] = (
    "supports_chat",
    "supports_projects",
    "supports_workflows",
    "supports_prompts",
    "supports_agents",
    "supports_deployment",
    "supports_settings",
    "supports_theme_switching",
    "supports_command_palette",
    "supports_safe_mode_actions",
)


@dataclass(frozen=True, slots=True)
class GuiCapabilities:
    supports_chat: bool
    supports_projects: bool
    supports_workflows: bool
    supports_prompts: bool
    supports_agents: bool
    supports_deployment: bool
    supports_settings: bool
    supports_theme_switching: bool
    supports_command_palette: bool
    supports_safe_mode_actions: bool


# Kanonische Capability-Sätze (Governance). Bei neuer GUI: Eintrag + Registry-Zeile.
CAPABILITIES_DEFAULT_WIDGET_GUI: Final[GuiCapabilities] = GuiCapabilities(
    supports_chat=True,
    supports_projects=True,
    supports_workflows=True,
    supports_prompts=True,
    supports_agents=True,
    supports_deployment=True,
    supports_settings=True,
    supports_theme_switching=True,
    supports_command_palette=True,
    supports_safe_mode_actions=False,
)

CAPABILITIES_LIBRARY_QML_GUI: Final[GuiCapabilities] = GuiCapabilities(
    supports_chat=True,
    supports_projects=True,
    supports_workflows=True,
    supports_prompts=True,
    supports_agents=True,
    supports_deployment=True,
    supports_settings=True,
    supports_theme_switching=False,
    supports_command_palette=False,
    supports_safe_mode_actions=False,
)

CANONICAL_GUI_CAPABILITIES: Final[dict[str, GuiCapabilities]] = {
    "default_widget_gui": CAPABILITIES_DEFAULT_WIDGET_GUI,
    "library_qml_gui": CAPABILITIES_LIBRARY_QML_GUI,
}


def gui_supports(gui_id: str, capability: str) -> bool:
    """
    Prüft eine Capability anhand der registrierten Deskriptoren.

    Args:
        gui_id: Kanonische ``gui_id``.
        capability: Attributname, z. B. ``supports_workflows``.

    Raises:
        KeyError: Unbekannte ``gui_id``.
        ValueError: Unbekannter Capability-Name.
    """
    if capability not in KNOWN_GUI_CAPABILITY_NAMES:
        raise ValueError(f"Unknown GUI capability: {capability!r}")
    from app.gui_registry import get_gui_descriptor

    caps = get_gui_descriptor(gui_id).capabilities
    return bool(getattr(caps, capability))


def get_capabilities_for_gui_id(gui_id: str) -> GuiCapabilities:
    """Liefert den Capability-Satz der registrierten GUI."""
    from app.gui_registry import get_gui_descriptor

    return get_gui_descriptor(gui_id).capabilities


def validate_registered_gui_capabilities(registry: Mapping[str, object]) -> None:
    """
    Stellt sicher, dass jede GUI mit kanonischem Satz exakt übereinstimmt.

    Raises:
        ValueError: Abweichung oder fehlendes ``capabilities`` am Deskriptor.
    """
    for gui_id, desc in registry.items():
        expected = CANONICAL_GUI_CAPABILITIES.get(gui_id)
        if expected is None:
            continue
        caps = getattr(desc, "capabilities", None)
        if caps is None:
            raise ValueError(f"GuiDescriptor for {gui_id!r} missing capabilities")
        if caps != expected:
            raise ValueError(
                f"Capabilities drift for {gui_id!r}: registry has {caps!r}, "
                f"canonical is {expected!r}"
            )
