"""
Registry für Theme-Manifeste (Verzeichnis-basiert, kein dynamisches Code-Loading).

Phase 1: Registrierung expliziter Roots (z. B. ``app/ui_themes/builtins``).
"""

from __future__ import annotations

from pathlib import Path

from app.ui_runtime.manifest_models import ThemeManifest
from app.ui_runtime.theme_loader import load_theme_manifest_from_path


class ThemePackRegistry:
    """Lädt und indexiert Theme-Manifeste unter konfigurierbaren Wurzeln."""

    def __init__(self) -> None:
        self._by_id: dict[str, ThemeManifest] = {}
        self._roots: list[Path] = []

    def register_root(self, root: Path) -> None:
        root = root.resolve()
        if root in self._roots:
            return
        self._roots.append(root)
        if not root.is_dir():
            return
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            mf = child / "manifest.json"
            if not mf.is_file():
                continue
            try:
                manifest = load_theme_manifest_from_path(mf)
            except Exception:
                continue
            self._by_id[manifest.theme_id] = manifest

    def get(self, theme_id: str) -> ThemeManifest | None:
        return self._by_id.get(theme_id)

    def list_theme_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_id))


def default_builtin_registry() -> ThemePackRegistry:
    """Builtin-Themes relativ zu diesem Paket (``app/ui_themes/builtins``)."""
    here = Path(__file__).resolve()
    app_root = here.parent.parent
    reg = ThemePackRegistry()
    reg.register_root(app_root / "ui_themes" / "builtins")
    return reg
