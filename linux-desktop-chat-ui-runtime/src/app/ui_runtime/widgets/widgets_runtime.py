"""
PySide6-Widgets-Runtime — wendet deklarative Theme-Daten an, ohne Services.

Phase 1: Kein Ersatz für ``ThemeManager``; ``stylesheet_hook`` erlaubt die bestehende
Integration (z. B. ``app.setStyleSheet``) von außen, damit die produktive GUI unverändert bleibt.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.ui_runtime.base_runtime import BaseRuntime
from app.ui_runtime.manifest_models import ThemeManifest


class WidgetsRuntime(BaseRuntime):
    """Liest Design-Pack (QSS-Fragmente) und ruft optional einen Hook auf."""

    def __init__(
        self,
        manifest: ThemeManifest,
        *,
        stylesheet_hook: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(manifest)
        self._stylesheet_hook = stylesheet_hook
        self._last_qss: str | None = None

    def activate(self, context: dict[str, Any] | None = None) -> None:
        del context  # reserviert für Shell-/Font-Overrides
        qss = self._merge_qss_fragments()
        self._last_qss = qss
        if self._stylesheet_hook and qss:
            self._stylesheet_hook(qss)

    def deactivate(self) -> None:
        if self._stylesheet_hook and self._last_qss:
            self._stylesheet_hook("")
        self._last_qss = None

    def _merge_qss_fragments(self) -> str:
        design = self.manifest.packs.get("design") or {}
        paths = design.get("qss") or []
        if not isinstance(paths, list):
            return ""
        chunks: list[str] = []
        for rel in paths:
            if not isinstance(rel, str):
                continue
            resolved = self.manifest.resolve_pack_path(rel)
            if resolved is None or not resolved.is_file():
                continue
            try:
                chunks.append(resolved.read_text(encoding="utf-8"))
            except OSError:
                continue
        return "\n\n".join(chunks)

    def layout_pack_path(self) -> Path | None:
        """Pfad zum Layout-Pack-Einstieg (JSON), falls vorhanden."""
        layout = self.manifest.packs.get("layout") or {}
        entry = layout.get("entry")
        if not isinstance(entry, str):
            return None
        return self.manifest.resolve_pack_path(entry)
