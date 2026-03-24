"""
Laufzeit für Theme-Manifeste und UI-Runtimes (Widgets / QML).

- Lädt und validiert Theme-Manifeste (keine Businesslogik).
- Stellt Runtime-Adapter bereit; Anbindung an ``app.gui.themes`` erfolgt schrittweise von außen.

Exports werden lazy geladen (PEP 562), damit z. B. ``panel_wiring`` ohne ``jsonschema``-Pfad
importierbar bleibt, solange Theme-Symbole nicht angefasst werden.
"""

from __future__ import annotations

import importlib
from typing import Any

__all__ = [
    "PresenterBinding",
    "UICommandDispatcher",
    "UnregisteredCommandError",
    "ThemeManifest",
    "ThemePackRegistry",
    "default_builtin_registry",
    "load_theme_manifest_from_path",
    "validate_manifest_dict",
    "wire_panel",
    "wire_panel_with_presenters",
]

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "UICommandDispatcher": ("app.ui_runtime.command_dispatcher", "UICommandDispatcher"),
    "UnregisteredCommandError": ("app.ui_runtime.command_dispatcher", "UnregisteredCommandError"),
    "ThemeManifest": ("app.ui_runtime.manifest_models", "ThemeManifest"),
    "validate_manifest_dict": ("app.ui_runtime.manifest_models", "validate_manifest_dict"),
    "load_theme_manifest_from_path": ("app.ui_runtime.theme_loader", "load_theme_manifest_from_path"),
    "ThemePackRegistry": ("app.ui_runtime.theme_registry", "ThemePackRegistry"),
    "default_builtin_registry": ("app.ui_runtime.theme_registry", "default_builtin_registry"),
    "PresenterBinding": ("app.ui_runtime.panel_wiring", "PresenterBinding"),
    "wire_panel": ("app.ui_runtime.panel_wiring", "wire_panel"),
    "wire_panel_with_presenters": ("app.ui_runtime.panel_wiring", "wire_panel_with_presenters"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_EXPORTS:
        module_name, attr = _LAZY_EXPORTS[name]
        module = importlib.import_module(module_name)
        return getattr(module, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
