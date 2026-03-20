"""
Theme Loader – lädt QSS-Templates und substituiert Tokens.
"""

import re
from pathlib import Path

from app.gui.themes.definition import ThemeDefinition
from app.utils.paths import get_themes_dir


def _base_qss_path() -> Path:
    """Pfad zum Basis-QSS (assets/themes/base/base.qss)."""
    return get_themes_dir() / "base" / "base.qss"


def _shell_qss_path() -> Path:
    """Pfad zum Shell-QSS (assets/themes/base/shell.qss)."""
    return get_themes_dir() / "base" / "shell.qss"


def _substitute_tokens(text: str, tokens: dict[str, str]) -> str:
    """
    Ersetzt {{token_name}} durch token-Werte.
    Unbekannte Tokens bleiben unverändert.
    """
    def repl(match: re.Match) -> str:
        key = match.group(1)
        return tokens.get(key, match.group(0))

    return re.sub(r"\{\{(\w+)\}\}", repl, text)


def load_stylesheet(theme: ThemeDefinition) -> str:
    """
    Lädt das vollständige Stylesheet für ein Theme.
    Kombiniert base.qss + shell.qss und substituiert Tokens.
    """
    tokens = theme.get_tokens_dict()
    parts: list[str] = []

    base_path = _base_qss_path()
    if base_path.exists():
        base_text = base_path.read_text(encoding="utf-8")
        parts.append(_substitute_tokens(base_text, tokens))

    shell_path = _shell_qss_path()
    if shell_path.exists():
        shell_text = shell_path.read_text(encoding="utf-8")
        parts.append(_substitute_tokens(shell_text, tokens))

    return "\n\n".join(parts) if parts else ""
