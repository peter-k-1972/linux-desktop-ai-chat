"""
Erweitert Legacy-Token-Dicts (ThemeTokens.to_dict + Aliase) um alle Spec-Keys.

Quelle: docs/design/THEME_TOKEN_SPEC.md
Alle Werte werden aus bestehenden Theme-Feldern abgeleitet — keine neuen Farben.
"""

from __future__ import annotations

from app.gui.themes.canonical_token_ids import ThemeTokenId, all_canonical_color_token_ids, flat_key


def _g(d: dict[str, str], key: str, fallback: str = "") -> str:
    v = d.get(key, "")
    return v if v else fallback


def expand_token_dict_to_full_spec(base: dict[str, str]) -> dict[str, str]:
    """
    :param base: Ausgabe von merge_semantic_aliases_for_qss (enthält color_* + Aliase).
    :return: Kopie inkl. aller color_* Spec-Flat-Keys, Legacy-Keys und canonical Duplikate.
    """
    L = dict(base)
    out: dict[str, str] = dict(L)

    def set_both(canonical: str, value: str) -> None:
        fk = flat_key(canonical)
        if value:
            out[fk] = value
            out[canonical] = value

    # --- Foundation (Legacy-Mapping laut Spec) ---
    set_both(ThemeTokenId.BG_APP, _g(L, "color_bg"))
    set_both(ThemeTokenId.BG_WINDOW, _g(L, "color_bg", _g(L, "color_bg_surface")))
    set_both(ThemeTokenId.BG_PANEL, _g(L, "color_nav_bg"))
    set_both(ThemeTokenId.BG_SURFACE, _g(L, "color_bg_surface"))
    set_both(ThemeTokenId.BG_SURFACE_ALT, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.BG_SURFACE_ELEVATED, _g(L, "color_bg_elevated"))
    set_both(ThemeTokenId.BG_OVERLAY, _g(L, "color_bg"))

    # --- Foreground ---
    set_both(ThemeTokenId.FG_PRIMARY, _g(L, "color_text"))
    set_both(ThemeTokenId.FG_SECONDARY, _g(L, "color_text_secondary"))
    set_both(ThemeTokenId.FG_MUTED, _g(L, "color_text_muted"))
    set_both(ThemeTokenId.FG_DISABLED, _g(L, "color_text_disabled"))
    set_both(ThemeTokenId.FG_INVERSE, _g(L, "color_text_inverse"))
    set_both(ThemeTokenId.FG_LINK, _g(L, "color_accent"))
    set_both(ThemeTokenId.FG_ON_SUCCESS, _g(L, "color_text_inverse", _g(L, "color_text")))
    set_both(ThemeTokenId.FG_ON_WARNING, _g(L, "color_text", _g(L, "color_text_inverse")))
    set_both(ThemeTokenId.FG_ON_ERROR, _g(L, "color_text_inverse", _g(L, "color_text")))
    set_both(ThemeTokenId.FG_ON_SELECTED, _g(L, "color_fg_on_selected", _g(L, "color_nav_selected_fg")))

    # Borders: legacy color_border = subtle; medium = default per migration note
    set_both(ThemeTokenId.BORDER_DEFAULT, _g(L, "color_border_medium", _g(L, "color_border")))
    set_both(ThemeTokenId.BORDER_SUBTLE, _g(L, "color_border"))
    set_both(ThemeTokenId.BORDER_STRONG, _g(L, "color_border_strong"))
    set_both(ThemeTokenId.BORDER_FOCUS, _g(L, "color_focus_ring", _g(L, "color_accent")))

    # Interaction
    set_both(ThemeTokenId.INTERACTION_HOVER, _g(L, "color_bg_hover"))
    set_both(ThemeTokenId.INTERACTION_PRESSED, _g(L, "color_border"))
    set_both(ThemeTokenId.INTERACTION_SELECTED, _g(L, "color_bg_selected"))
    set_both(ThemeTokenId.INTERACTION_ACTIVE, _g(L, "color_bg_selected"))
    set_both(ThemeTokenId.INTERACTION_FOCUS_RING, _g(L, "color_focus_ring"))

    # Text selection
    set_both(ThemeTokenId.SELECTION_BG, _g(L, "color_accent", _g(L, "color_bg_selected")))
    set_both(ThemeTokenId.SELECTION_FG, _g(L, "color_text_inverse", _g(L, "color_text")))

    # State
    set_both(ThemeTokenId.STATE_ACCENT, _g(L, "color_accent"))
    set_both(ThemeTokenId.STATE_ACCENT_HOVER, _g(L, "color_accent_hover"))
    set_both(ThemeTokenId.STATE_ACCENT_PRESSED, _g(L, "color_accent"))
    set_both(ThemeTokenId.STATE_ACCENT_MUTED_BG, _g(L, "color_accent_bg"))
    set_both(ThemeTokenId.STATE_SUCCESS, _g(L, "color_success"))
    set_both(ThemeTokenId.STATE_WARNING, _g(L, "color_warning"))
    set_both(ThemeTokenId.STATE_ERROR, _g(L, "color_error"))
    set_both(ThemeTokenId.STATE_INFO, _g(L, "color_info"))

    # Buttons
    set_both(ThemeTokenId.BUTTON_PRIMARY_BG, _g(L, "color_accent"))
    set_both(ThemeTokenId.BUTTON_PRIMARY_FG, _g(L, "color_text_inverse"))
    set_both(ThemeTokenId.BUTTON_PRIMARY_HOVER, _g(L, "color_accent_hover"))
    set_both(ThemeTokenId.BUTTON_PRIMARY_PRESSED, _g(L, "color_accent"))
    set_both(ThemeTokenId.BUTTON_SECONDARY_BG, _g(L, "color_bg_surface"))
    set_both(ThemeTokenId.BUTTON_SECONDARY_FG, _g(L, "color_text"))
    bd = out.get(flat_key(ThemeTokenId.BORDER_DEFAULT), "")
    set_both(ThemeTokenId.BUTTON_SECONDARY_BORDER, bd or _g(L, "color_border"))
    set_both(ThemeTokenId.BUTTON_SECONDARY_HOVER, _g(L, "color_bg_hover"))
    set_both(ThemeTokenId.BUTTON_DISABLED_BG, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.BUTTON_DISABLED_FG, _g(L, "color_text_disabled"))

    # Inputs
    set_both(ThemeTokenId.INPUT_BG, _g(L, "color_bg_input"))
    set_both(ThemeTokenId.INPUT_FG, _g(L, "color_text"))
    set_both(ThemeTokenId.INPUT_PLACEHOLDER, _g(L, "color_text_muted"))
    set_both(ThemeTokenId.INPUT_BORDER, out.get(flat_key(ThemeTokenId.BORDER_DEFAULT), _g(L, "color_border")))
    set_both(ThemeTokenId.INPUT_BORDER_FOCUS, out.get(flat_key(ThemeTokenId.BORDER_FOCUS), _g(L, "color_focus_ring")))
    set_both(ThemeTokenId.INPUT_DISABLED_BG, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.INPUT_DISABLED_FG, _g(L, "color_text_disabled"))

    # Nav (Shell)
    set_both(ThemeTokenId.NAV_BG, _g(L, "color_nav_bg"))
    set_both(ThemeTokenId.NAV_FG, _g(L, "color_text"))
    set_both(ThemeTokenId.NAV_HOVER_BG, _g(L, "color_bg_hover"))
    set_both(ThemeTokenId.NAV_ACTIVE_BG, _g(L, "color_nav_selected_bg", _g(L, "color_bg_selected")))
    set_both(ThemeTokenId.NAV_ACTIVE_FG, _g(L, "color_nav_selected_fg"))

    # Tabs
    set_both(ThemeTokenId.TAB_BG, _g(L, "color_bg", _g(L, "color_nav_bg")))
    set_both(ThemeTokenId.TAB_FG, _g(L, "color_text_muted"))
    set_both(ThemeTokenId.TAB_ACTIVE_BG, _g(L, "color_bg_surface"))
    set_both(ThemeTokenId.TAB_ACTIVE_FG, _g(L, "color_text"))
    # Tab indicator: neutral edge by default (accent reduction); override in theme if needed.
    set_both(
        ThemeTokenId.TAB_INDICATOR,
        _g(L, "color_border_medium", _g(L, "color_border_strong", _g(L, "color_accent"))),
    )

    # Tables
    set_both(ThemeTokenId.TABLE_BG, _g(L, "color_bg_surface"))
    set_both(ThemeTokenId.TABLE_FG, _g(L, "color_text"))
    set_both(ThemeTokenId.TABLE_HEADER_BG, _g(L, "color_bg_elevated"))
    set_both(ThemeTokenId.TABLE_HEADER_FG, _g(L, "color_text_secondary"))
    set_both(ThemeTokenId.TABLE_ROW_ALT_BG, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.TABLE_GRID, out.get(flat_key(ThemeTokenId.BORDER_SUBTLE), _g(L, "color_border")))
    set_both(
        ThemeTokenId.TABLE_SELECTION_BG,
        out.get(flat_key(ThemeTokenId.SELECTION_BG), _g(L, "color_bg_selected")),
    )
    set_both(
        ThemeTokenId.TABLE_SELECTION_FG,
        out.get(flat_key(ThemeTokenId.SELECTION_FG), _g(L, "color_text")),
    )

    # Chat bubbles (kein Redesign: aus Accent/Surface ableiten)
    set_both(ThemeTokenId.CHAT_USER_BG, _g(L, "color_accent"))
    set_both(ThemeTokenId.CHAT_USER_FG, _g(L, "color_text_inverse"))
    set_both(ThemeTokenId.CHAT_USER_BORDER, out.get(flat_key(ThemeTokenId.BORDER_SUBTLE), _g(L, "color_border")))
    set_both(ThemeTokenId.CHAT_ASSISTANT_BG, _g(L, "color_bg_surface"))
    set_both(ThemeTokenId.CHAT_ASSISTANT_FG, _g(L, "color_text"))
    set_both(ThemeTokenId.CHAT_ASSISTANT_BORDER, out.get(flat_key(ThemeTokenId.BORDER_SUBTLE), _g(L, "color_border")))
    set_both(ThemeTokenId.CHAT_SYSTEM_BG, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.CHAT_SYSTEM_FG, _g(L, "color_text_muted"))

    # Markdown
    set_both(ThemeTokenId.MARKDOWN_BODY, _g(L, "color_text"))
    set_both(ThemeTokenId.MARKDOWN_HEADING, _g(L, "color_text"))
    set_both(ThemeTokenId.MARKDOWN_LINK, _g(L, "color_accent"))
    set_both(ThemeTokenId.MARKDOWN_QUOTE, _g(L, "color_text_secondary"))
    set_both(ThemeTokenId.MARKDOWN_QUOTE_BORDER, out.get(flat_key(ThemeTokenId.BORDER_STRONG), _g(L, "color_border_strong")))
    set_both(ThemeTokenId.MARKDOWN_INLINE_CODE_BG, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.MARKDOWN_INLINE_CODE_FG, _g(L, "color_text"))
    set_both(ThemeTokenId.MARKDOWN_CODEBLOCK_BG, _g(L, "color_bg_muted", _g(L, "color_bg_input")))
    set_both(ThemeTokenId.MARKDOWN_CODEBLOCK_FG, _g(L, "color_text"))
    set_both(ThemeTokenId.MARKDOWN_TABLE_BORDER, out.get(flat_key(ThemeTokenId.BORDER_DEFAULT), _g(L, "color_border")))
    set_both(ThemeTokenId.MARKDOWN_TABLE_HEADER_BG, out.get(flat_key(ThemeTokenId.TABLE_HEADER_BG)))
    set_both(ThemeTokenId.MARKDOWN_HR, out.get(flat_key(ThemeTokenId.BORDER_SUBTLE)))

    # Syntax / console (bestehende Keys)
    set_both(ThemeTokenId.SYNTAX_PLAIN, _g(L, "color_text"))
    set_both(ThemeTokenId.SYNTAX_KEYWORD, _g(L, "color_accent"))
    set_both(ThemeTokenId.SYNTAX_STRING, _g(L, "color_success"))
    set_both(ThemeTokenId.SYNTAX_COMMENT, _g(L, "color_text_muted"))
    set_both(ThemeTokenId.SYNTAX_NUMBER, _g(L, "color_warning"))
    set_both(ThemeTokenId.SYNTAX_FUNCTION, _g(L, "color_info"))
    set_both(ThemeTokenId.CONSOLE_INFO, _g(L, "color_console_info"))
    set_both(ThemeTokenId.CONSOLE_WARNING, _g(L, "color_console_warning"))
    set_both(ThemeTokenId.CONSOLE_ERROR, _g(L, "color_console_error"))
    set_both(ThemeTokenId.CONSOLE_SUCCESS, _g(L, "color_console_success"))

    # Badges (tinted surfaces aus vorhandenen Flächen)
    set_both(ThemeTokenId.BADGE_SUCCESS_BG, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.BADGE_SUCCESS_FG, _g(L, "color_success"))
    set_both(ThemeTokenId.BADGE_WARNING_BG, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.BADGE_WARNING_FG, _g(L, "color_warning"))
    set_both(ThemeTokenId.BADGE_ERROR_BG, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.BADGE_ERROR_FG, _g(L, "color_error"))
    set_both(ThemeTokenId.BADGE_INFO_BG, _g(L, "color_accent_bg"))
    set_both(ThemeTokenId.BADGE_INFO_FG, _g(L, "color_accent"))

    # Domain (Legacy-Namen beibehalten + Spec-Flat)
    set_both(ThemeTokenId.DOMAIN_MONITORING_BG, _g(L, "color_monitoring_bg"))
    set_both(ThemeTokenId.DOMAIN_MONITORING_SURFACE, _g(L, "color_monitoring_surface"))
    set_both(ThemeTokenId.DOMAIN_MONITORING_BORDER, _g(L, "color_monitoring_border"))
    set_both(ThemeTokenId.DOMAIN_MONITORING_TEXT, _g(L, "color_monitoring_text"))
    set_both(ThemeTokenId.DOMAIN_MONITORING_MUTED, _g(L, "color_monitoring_muted"))
    set_both(ThemeTokenId.DOMAIN_MONITORING_ACCENT, _g(L, "color_monitoring_accent"))
    set_both(ThemeTokenId.DOMAIN_MONITORING_ACCENT_BG, _g(L, "color_monitoring_accent_bg"))
    set_both(ThemeTokenId.DOMAIN_QA_NAV_SELECTED_BG, _g(L, "color_qa_nav_selected_bg"))
    set_both(ThemeTokenId.DOMAIN_QA_NAV_SELECTED_FG, _g(L, "color_qa_nav_selected_fg"))

    # Charts
    set_both(ThemeTokenId.CHART_BG, out.get(flat_key(ThemeTokenId.DOMAIN_MONITORING_BG), _g(L, "color_bg")))
    set_both(ThemeTokenId.CHART_AXIS, _g(L, "color_text_muted"))
    set_both(ThemeTokenId.CHART_GRID, out.get(flat_key(ThemeTokenId.BORDER_SUBTLE)))
    set_both(ThemeTokenId.CHART_SERIES_1, _g(L, "color_info"))
    set_both(ThemeTokenId.CHART_SERIES_2, _g(L, "color_warning"))
    set_both(ThemeTokenId.CHART_SERIES_3, _g(L, "color_accent"))
    set_both(ThemeTokenId.CHART_SERIES_OTHER, _g(L, "color_text_secondary"))

    # Workflow graph (Ist-Farben semantisch abbilden, ohne neue Hex)
    set_both(ThemeTokenId.GRAPH_NODE_FILL, _g(L, "color_bg_surface"))
    set_both(ThemeTokenId.GRAPH_NODE_BORDER, out.get(flat_key(ThemeTokenId.BORDER_DEFAULT)))
    set_both(ThemeTokenId.GRAPH_NODE_TEXT, _g(L, "color_text"))
    set_both(ThemeTokenId.GRAPH_NODE_TEXT_MUTED, _g(L, "color_text_muted"))
    set_both(ThemeTokenId.GRAPH_NODE_SELECTED_BORDER, _g(L, "color_accent"))
    set_both(ThemeTokenId.GRAPH_EDGE, _g(L, "color_border_strong", _g(L, "color_text_muted")))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_COMPLETED_FILL, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_COMPLETED_BORDER, _g(L, "color_success"))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_FAILED_FILL, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_FAILED_BORDER, _g(L, "color_error"))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_RUNNING_FILL, _g(L, "color_accent_bg"))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_RUNNING_BORDER, _g(L, "color_accent"))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_PENDING_FILL, _g(L, "color_bg_surface"))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_PENDING_BORDER, _g(L, "color_text_muted"))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_CANCELLED_FILL, _g(L, "color_bg_muted"))
    set_both(ThemeTokenId.GRAPH_NODE_STATUS_CANCELLED_BORDER, _g(L, "color_warning"))

    # Indicators (Workbench tabs)
    set_both(ThemeTokenId.INDICATOR_READY, _g(L, "color_text_muted"))
    set_both(ThemeTokenId.INDICATOR_RUNNING, _g(L, "color_info"))
    set_both(ThemeTokenId.INDICATOR_FAILED, _g(L, "color_error"))
    set_both(ThemeTokenId.INDICATOR_INDEXING, _g(L, "color_warning"))
    set_both(ThemeTokenId.INDICATOR_SYNCING, _g(L, "color_accent"))

    # Menu / tooltip
    set_both(ThemeTokenId.MENU_BG, _g(L, "color_bg_elevated", _g(L, "color_bg_surface")))
    set_both(ThemeTokenId.MENU_FG, _g(L, "color_text"))
    set_both(ThemeTokenId.MENU_HOVER_BG, _g(L, "color_bg_hover"))
    set_both(ThemeTokenId.TOOLTIP_BG, _g(L, "color_bg_elevated"))
    set_both(ThemeTokenId.TOOLTIP_FG, _g(L, "color_text"))

    # Sicherstellen: kein leerer Spec-Key — Fallback nur aus anderen Theme-Feldern
    fallback = _g(L, "color_text", _g(L, "color_bg_surface", _g(L, "color_bg")))
    for c in all_canonical_color_token_ids():
        fk = flat_key(c)
        if not (out.get(fk) or "").strip():
            set_both(c, fallback)

    return out


def assert_all_spec_tokens_present(d: dict[str, str]) -> list[str]:
    """Liefert fehlende oder leere Spec-Flat-Keys."""
    missing: list[str] = []
    for c in all_canonical_color_token_ids():
        fk = flat_key(c)
        if fk not in d or not (d.get(fk) or "").strip():
            missing.append(fk)
    return missing
