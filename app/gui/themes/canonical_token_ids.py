"""
Kanonical Token-IDs (THEME_TOKEN_SPEC.md) — nur Namen, keine Farbwerte.

API: ThemeTokenId.BG_APP == "color.bg.app"
QSS/Python-Map-Key: Punkt → Unterstrich → "color_bg_app"
"""

from __future__ import annotations


def flat_key(canonical: str) -> str:
    """color.bg.app → color_bg_app"""
    return canonical.replace(".", "_")


class ThemeTokenId:
    """Verbindliche Token-Namen gemäß docs/design/THEME_TOKEN_SPEC.md"""

    # Foundation
    BG_APP = "color.bg.app"
    BG_WINDOW = "color.bg.window"
    BG_PANEL = "color.bg.panel"
    BG_SURFACE = "color.bg.surface"
    BG_SURFACE_ALT = "color.bg.surface_alt"
    BG_SURFACE_ELEVATED = "color.bg.surface_elevated"
    BG_OVERLAY = "color.bg.overlay"

    # Foreground
    FG_PRIMARY = "color.fg.primary"
    FG_SECONDARY = "color.fg.secondary"
    FG_MUTED = "color.fg.muted"
    FG_DISABLED = "color.fg.disabled"
    FG_INVERSE = "color.fg.inverse"
    FG_LINK = "color.fg.link"
    FG_ON_SUCCESS = "color.fg.on_success"
    FG_ON_WARNING = "color.fg.on_warning"
    FG_ON_ERROR = "color.fg.on_error"
    FG_ON_SELECTED = "color.fg.on_selected"

    # Borders
    BORDER_DEFAULT = "color.border.default"
    BORDER_SUBTLE = "color.border.subtle"
    BORDER_STRONG = "color.border.strong"
    BORDER_FOCUS = "color.border.focus"

    # Interaction
    INTERACTION_HOVER = "color.interaction.hover"
    INTERACTION_PRESSED = "color.interaction.pressed"
    INTERACTION_SELECTED = "color.interaction.selected"
    INTERACTION_ACTIVE = "color.interaction.active"
    INTERACTION_FOCUS_RING = "color.interaction.focus_ring"

    # Selection (text)
    SELECTION_BG = "color.selection.bg"
    SELECTION_FG = "color.selection.fg"

    # State
    STATE_ACCENT = "color.state.accent"
    STATE_ACCENT_HOVER = "color.state.accent_hover"
    STATE_ACCENT_PRESSED = "color.state.accent_pressed"
    STATE_ACCENT_MUTED_BG = "color.state.accent_muted_bg"
    STATE_SUCCESS = "color.state.success"
    STATE_WARNING = "color.state.warning"
    STATE_ERROR = "color.state.error"
    STATE_INFO = "color.state.info"

    # Buttons
    BUTTON_PRIMARY_BG = "color.button.primary.bg"
    BUTTON_PRIMARY_FG = "color.button.primary.fg"
    BUTTON_PRIMARY_HOVER = "color.button.primary.hover"
    BUTTON_PRIMARY_PRESSED = "color.button.primary.pressed"
    BUTTON_SECONDARY_BG = "color.button.secondary.bg"
    BUTTON_SECONDARY_FG = "color.button.secondary.fg"
    BUTTON_SECONDARY_BORDER = "color.button.secondary.border"
    BUTTON_SECONDARY_HOVER = "color.button.secondary.hover"
    BUTTON_DISABLED_BG = "color.button.disabled.bg"
    BUTTON_DISABLED_FG = "color.button.disabled.fg"

    # Inputs
    INPUT_BG = "color.input.bg"
    INPUT_FG = "color.input.fg"
    INPUT_PLACEHOLDER = "color.input.placeholder"
    INPUT_BORDER = "color.input.border"
    INPUT_BORDER_FOCUS = "color.input.border_focus"
    INPUT_DISABLED_BG = "color.input.disabled_bg"
    INPUT_DISABLED_FG = "color.input.disabled_fg"

    # Nav
    NAV_BG = "color.nav.bg"
    NAV_FG = "color.nav.fg"
    NAV_HOVER_BG = "color.nav.hover_bg"
    NAV_ACTIVE_BG = "color.nav.active_bg"
    NAV_ACTIVE_FG = "color.nav.active_fg"

    # Tabs
    TAB_BG = "color.tab.bg"
    TAB_FG = "color.tab.fg"
    TAB_ACTIVE_BG = "color.tab.active_bg"
    TAB_ACTIVE_FG = "color.tab.active_fg"
    TAB_INDICATOR = "color.tab.indicator"

    # Tables
    TABLE_BG = "color.table.bg"
    TABLE_FG = "color.table.fg"
    TABLE_HEADER_BG = "color.table.header_bg"
    TABLE_HEADER_FG = "color.table.header_fg"
    TABLE_ROW_ALT_BG = "color.table.row_alt_bg"
    TABLE_GRID = "color.table.grid"
    TABLE_SELECTION_BG = "color.table.selection_bg"
    TABLE_SELECTION_FG = "color.table.selection_fg"

    # Chat
    CHAT_USER_BG = "color.chat.user_bg"
    CHAT_USER_FG = "color.chat.user_fg"
    CHAT_USER_BORDER = "color.chat.user_border"
    CHAT_ASSISTANT_BG = "color.chat.assistant_bg"
    CHAT_ASSISTANT_FG = "color.chat.assistant_fg"
    CHAT_ASSISTANT_BORDER = "color.chat.assistant_border"
    CHAT_SYSTEM_BG = "color.chat.system_bg"
    CHAT_SYSTEM_FG = "color.chat.system_fg"

    # Markdown
    MARKDOWN_BODY = "color.markdown.body"
    MARKDOWN_HEADING = "color.markdown.heading"
    MARKDOWN_LINK = "color.markdown.link"
    MARKDOWN_QUOTE = "color.markdown.quote"
    MARKDOWN_QUOTE_BORDER = "color.markdown.quote_border"
    MARKDOWN_INLINE_CODE_BG = "color.markdown.inline_code_bg"
    MARKDOWN_INLINE_CODE_FG = "color.markdown.inline_code_fg"
    MARKDOWN_CODEBLOCK_BG = "color.markdown.codeblock_bg"
    MARKDOWN_CODEBLOCK_FG = "color.markdown.codeblock_fg"
    MARKDOWN_TABLE_BORDER = "color.markdown.table_border"
    MARKDOWN_TABLE_HEADER_BG = "color.markdown.table_header_bg"
    MARKDOWN_HR = "color.markdown.hr"

    # Syntax / console
    SYNTAX_PLAIN = "color.syntax.plain"
    SYNTAX_KEYWORD = "color.syntax.keyword"
    SYNTAX_STRING = "color.syntax.string"
    SYNTAX_COMMENT = "color.syntax.comment"
    SYNTAX_NUMBER = "color.syntax.number"
    SYNTAX_FUNCTION = "color.syntax.function"
    CONSOLE_INFO = "color.console.info"
    CONSOLE_WARNING = "color.console.warning"
    CONSOLE_ERROR = "color.console.error"
    CONSOLE_SUCCESS = "color.console.success"

    # Badges
    BADGE_SUCCESS_BG = "color.badge.success.bg"
    BADGE_SUCCESS_FG = "color.badge.success.fg"
    BADGE_WARNING_BG = "color.badge.warning.bg"
    BADGE_WARNING_FG = "color.badge.warning.fg"
    BADGE_ERROR_BG = "color.badge.error.bg"
    BADGE_ERROR_FG = "color.badge.error.fg"
    BADGE_INFO_BG = "color.badge.info.bg"
    BADGE_INFO_FG = "color.badge.info.fg"

    # Domain monitoring / QA
    DOMAIN_MONITORING_BG = "color.domain.monitoring.bg"
    DOMAIN_MONITORING_SURFACE = "color.domain.monitoring.surface"
    DOMAIN_MONITORING_BORDER = "color.domain.monitoring.border"
    DOMAIN_MONITORING_TEXT = "color.domain.monitoring.text"
    DOMAIN_MONITORING_MUTED = "color.domain.monitoring.muted"
    DOMAIN_MONITORING_ACCENT = "color.domain.monitoring.accent"
    DOMAIN_MONITORING_ACCENT_BG = "color.domain.monitoring.accent_bg"
    DOMAIN_QA_NAV_SELECTED_BG = "color.domain.qa_nav.selected_bg"
    DOMAIN_QA_NAV_SELECTED_FG = "color.domain.qa_nav.selected_fg"

    # Charts
    CHART_BG = "color.chart.bg"
    CHART_AXIS = "color.chart.axis"
    CHART_GRID = "color.chart.grid"
    CHART_SERIES_1 = "color.chart.series.1"
    CHART_SERIES_2 = "color.chart.series.2"
    CHART_SERIES_3 = "color.chart.series.3"
    CHART_SERIES_OTHER = "color.chart.series.other"

    # Graph / workflow
    GRAPH_NODE_FILL = "color.graph.node.fill"
    GRAPH_NODE_BORDER = "color.graph.node.border"
    GRAPH_NODE_TEXT = "color.graph.node.text"
    GRAPH_NODE_TEXT_MUTED = "color.graph.node.text_muted"
    GRAPH_NODE_SELECTED_BORDER = "color.graph.node.selected_border"
    GRAPH_EDGE = "color.graph.edge"
    GRAPH_NODE_STATUS_COMPLETED_FILL = "color.graph.node.status.completed.fill"
    GRAPH_NODE_STATUS_COMPLETED_BORDER = "color.graph.node.status.completed.border"
    GRAPH_NODE_STATUS_FAILED_FILL = "color.graph.node.status.failed.fill"
    GRAPH_NODE_STATUS_FAILED_BORDER = "color.graph.node.status.failed.border"
    GRAPH_NODE_STATUS_RUNNING_FILL = "color.graph.node.status.running.fill"
    GRAPH_NODE_STATUS_RUNNING_BORDER = "color.graph.node.status.running.border"
    GRAPH_NODE_STATUS_PENDING_FILL = "color.graph.node.status.pending.fill"
    GRAPH_NODE_STATUS_PENDING_BORDER = "color.graph.node.status.pending.border"
    GRAPH_NODE_STATUS_CANCELLED_FILL = "color.graph.node.status.cancelled.fill"
    GRAPH_NODE_STATUS_CANCELLED_BORDER = "color.graph.node.status.cancelled.border"

    # Indicators
    INDICATOR_READY = "color.indicator.ready"
    INDICATOR_RUNNING = "color.indicator.running"
    INDICATOR_FAILED = "color.indicator.failed"
    INDICATOR_INDEXING = "color.indicator.indexing"
    INDICATOR_SYNCING = "color.indicator.syncing"

    # Menu / tooltip
    MENU_BG = "color.menu.bg"
    MENU_FG = "color.menu.fg"
    MENU_HOVER_BG = "color.menu.hover_bg"
    TOOLTIP_BG = "color.tooltip.bg"
    TOOLTIP_FG = "color.tooltip.fg"


def all_canonical_color_token_ids() -> tuple[str, ...]:
    """Alle deklarierten Farb-Token (canonical), für Vollständigkeitstests."""
    return tuple(
        v
        for k, v in vars(ThemeTokenId).items()
        if not k.startswith("_") and isinstance(v, str) and v.startswith("color.")
    )


def all_flat_color_keys() -> frozenset[str]:
    return frozenset(flat_key(c) for c in all_canonical_color_token_ids())
