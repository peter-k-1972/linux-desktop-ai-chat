"""
ThemeDefinition – Manifest und Tokens eines Themes.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.gui.themes.tokens import ThemeTokens


@dataclass
class ThemeDefinition:
    """
    Vollständige Definition eines Themes.
    id: Eindeutige Kennung (z.B. light_default, dark_default)
    name: Anzeigename
    tokens: Design-Tokens
    extends: Optional, ID eines Basis-Themes
    """

    id: str
    name: str
    tokens: ThemeTokens
    extends: str | None = None
    _path: Path | None = None

    @property
    def path(self) -> Path | None:
        """Pfad zum Theme-Verzeichnis."""
        return self._path

    def get_tokens_dict(self) -> dict[str, str]:
        """
        Flaches Token-Dict für QSS-Substitution inkl. Legacy-Aliase und
        vollständiger Spec-Keys (THEME_TOKEN_SPEC.md).
        """
        from app.gui.themes.palette_resolve import merge_semantic_aliases_for_qss
        from app.gui.themes.resolved_spec_tokens import expand_token_dict_to_full_spec

        return expand_token_dict_to_full_spec(merge_semantic_aliases_for_qss(self.tokens))
