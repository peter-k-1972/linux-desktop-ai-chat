"""
Kontrast-Hilfen für den Theme-Visualizer (praxisnah, WCAG-orientiert).

Nutzt app.gui.themes.contrast — keine parallele Farblogik.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.gui.themes.canonical_token_ids import ThemeTokenId, flat_key
from app.gui.themes.contrast import contrast_ratio


class ContrastLevel(str, Enum):
    OK = "OK"
    WARN = "schlecht"
    BAD = "kritisch"


@dataclass(frozen=True)
class ContrastPairSpec:
    label: str
    fg_canonical: str
    bg_canonical: str
    minimum: float


# Mindestwerte angelehnt an docs/design/THEME_CONTRAST_RULES.md
DEFAULT_CONTRAST_PAIRS: tuple[ContrastPairSpec, ...] = (
    ContrastPairSpec("fg.primary × bg.surface", ThemeTokenId.FG_PRIMARY, ThemeTokenId.BG_SURFACE, 4.5),
    ContrastPairSpec("fg.primary × bg.app", ThemeTokenId.FG_PRIMARY, ThemeTokenId.BG_APP, 4.5),
    ContrastPairSpec("fg.secondary × bg.surface", ThemeTokenId.FG_SECONDARY, ThemeTokenId.BG_SURFACE, 4.5),
    ContrastPairSpec("fg.muted × bg.surface", ThemeTokenId.FG_MUTED, ThemeTokenId.BG_SURFACE, 4.5),
    ContrastPairSpec("fg.disabled × input.disabled_bg", ThemeTokenId.FG_DISABLED, ThemeTokenId.INPUT_DISABLED_BG, 3.0),
    ContrastPairSpec("fg.link × bg.surface", ThemeTokenId.FG_LINK, ThemeTokenId.BG_SURFACE, 4.5),
    ContrastPairSpec("input.fg × input.bg", ThemeTokenId.INPUT_FG, ThemeTokenId.INPUT_BG, 4.5),
    ContrastPairSpec("input.placeholder × input.bg", ThemeTokenId.INPUT_PLACEHOLDER, ThemeTokenId.INPUT_BG, 4.5),
    ContrastPairSpec("table.header_fg × table.header_bg", ThemeTokenId.TABLE_HEADER_FG, ThemeTokenId.TABLE_HEADER_BG, 4.5),
    ContrastPairSpec(
        "markdown.codeblock_fg × markdown.codeblock_bg",
        ThemeTokenId.MARKDOWN_CODEBLOCK_FG,
        ThemeTokenId.MARKDOWN_CODEBLOCK_BG,
        4.5,
    ),
    ContrastPairSpec("badge.success.fg × badge.success.bg", ThemeTokenId.BADGE_SUCCESS_FG, ThemeTokenId.BADGE_SUCCESS_BG, 4.5),
    ContrastPairSpec("badge.warning.fg × badge.warning.bg", ThemeTokenId.BADGE_WARNING_FG, ThemeTokenId.BADGE_WARNING_BG, 4.5),
    ContrastPairSpec("badge.error.fg × badge.error.bg", ThemeTokenId.BADGE_ERROR_FG, ThemeTokenId.BADGE_ERROR_BG, 4.5),
    ContrastPairSpec("badge.info.fg × badge.info.bg", ThemeTokenId.BADGE_INFO_FG, ThemeTokenId.BADGE_INFO_BG, 4.5),
    ContrastPairSpec("button.primary.fg × button.primary.bg", ThemeTokenId.BUTTON_PRIMARY_FG, ThemeTokenId.BUTTON_PRIMARY_BG, 4.5),
    ContrastPairSpec("chat.user_fg × chat.user_bg", ThemeTokenId.CHAT_USER_FG, ThemeTokenId.CHAT_USER_BG, 4.5),
    ContrastPairSpec("chat.assistant_fg × chat.assistant_bg", ThemeTokenId.CHAT_ASSISTANT_FG, ThemeTokenId.CHAT_ASSISTANT_BG, 4.5),
)


def token_value(tokens: dict[str, str], canonical: str) -> str:
    fk = flat_key(canonical)
    return (tokens.get(fk) or tokens.get(canonical) or "").strip()


def evaluate_pair(tokens: dict[str, str], spec: ContrastPairSpec) -> tuple[float | None, ContrastLevel, str]:
    fg = token_value(tokens, spec.fg_canonical)
    bg = token_value(tokens, spec.bg_canonical)
    if not fg or not bg:
        return None, ContrastLevel.BAD, "fehlender Token"
    try:
        ratio = contrast_ratio(fg, bg)
    except ValueError:
        return None, ContrastLevel.BAD, "ungültige Farbe"
    if ratio + 1e-6 >= spec.minimum:
        return ratio, ContrastLevel.OK, ""
    if ratio >= 3.0:
        return ratio, ContrastLevel.WARN, f"< {spec.minimum:.1f}:1"
    return ratio, ContrastLevel.BAD, f"< {spec.minimum:.1f}:1"


def contrast_hint_for_fg_on_bg(tokens: dict[str, str], fg_canonical: str, bg_canonical: str, minimum: float = 4.5) -> str:
    """Kurzhinweis für Swatch-Zeilen (Text auf Fläche)."""
    fg = token_value(tokens, fg_canonical)
    bg = token_value(tokens, bg_canonical)
    if not fg or not bg:
        return "—"
    try:
        r = contrast_ratio(fg, bg)
    except ValueError:
        return "?"
    if r + 1e-6 >= minimum:
        tag = ContrastLevel.OK.value
    elif r >= 3.0:
        tag = ContrastLevel.WARN.value
    else:
        tag = ContrastLevel.BAD.value
    return f"{r:.1f}:1 {tag}"
