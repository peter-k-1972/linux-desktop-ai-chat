"""
Runtime design-token helpers (metrics + registry).

Visual source of truth remains QSS under ``app/gui/themes/base/`` and
:class:`app.gui.themes.tokens.ThemeTokens`. This package centralizes **numeric**
layout/icon sizes shared with Python code — see ``docs/design/DESIGN_TOKEN_*``.
"""

from app.gui.theme.design_token_registry import DesignTokenRegistry, get_design_token_registry

__all__ = [
    "DesignTokenRegistry",
    "get_design_token_registry",
]
