"""
Runtime / Debug — Farben und QSS aus ThemeManager (Domain Monitoring + State).

Vermeidet harte Hex-Werte in Panels; bleibt konsistent mit shell.qss (color_monitoring_*).
"""

from __future__ import annotations

from app.gui.themes.canonical_token_ids import ThemeTokenId
from app.gui.themes.manager import get_theme_manager


def _c(tid: str) -> str:
    v = get_theme_manager().color(tid)
    if v:
        return v
    # Minimal fallback wenn Theme noch nicht initialisiert
    return "#64748b"


def rd_panel_qss(*, padding_px: int = 12, border_radius: int = 8) -> str:
    bg = _c(ThemeTokenId.DOMAIN_MONITORING_BG)
    bd = _c(ThemeTokenId.DOMAIN_MONITORING_BORDER)
    return (
        f"background: {bg}; border: 1px solid {bd}; border-radius: {border_radius}px; "
        f"padding: {padding_px}px;"
    )


def rd_scroll_area_qss(*, transparent: bool = False) -> str:
    if transparent:
        return "QScrollArea { background: transparent; }"
    bg = _c(ThemeTokenId.DOMAIN_MONITORING_BG)
    return f"QScrollArea {{ background: {bg}; border: none; }}"


def rd_section_title_qss(*, font_size_px: int = 13) -> str:
    return (
        f"font-weight: 600; font-size: {font_size_px}px; "
        f"color: {_c(ThemeTokenId.DOMAIN_MONITORING_MUTED)};"
    )


def rd_page_title_qss(*, font_size_px: int = 18) -> str:
    return (
        f"font-weight: 600; font-size: {font_size_px}px; "
        f"color: {_c(ThemeTokenId.DOMAIN_MONITORING_MUTED)};"
    )


def rd_body_secondary_qss(*, font_size_px: int = 11) -> str:
    return f"color: {_c(ThemeTokenId.DOMAIN_MONITORING_MUTED)}; font-size: {font_size_px}px;"


def rd_control_qss(*, font_size_px: int = 12, radius: int = 6) -> str:
    """ComboBox, QLineEdit in Monitoring-Kontext."""
    surf = _c(ThemeTokenId.DOMAIN_MONITORING_SURFACE)
    fg = _c(ThemeTokenId.DOMAIN_MONITORING_TEXT)
    bd = _c(ThemeTokenId.DOMAIN_MONITORING_BORDER)
    return (
        f"background: {surf}; color: {fg}; border: 1px solid {bd}; "
        f"border-radius: {radius}px; padding: 6px 12px; font-size: {font_size_px}px;"
    )


def rd_monospace_table_qss(*, font_size_px: int = 11) -> str:
    bg = _c(ThemeTokenId.DOMAIN_MONITORING_BG)
    fg = _c(ThemeTokenId.DOMAIN_MONITORING_TEXT)
    grid = _c(ThemeTokenId.DOMAIN_MONITORING_BORDER)
    sel = _c(ThemeTokenId.DOMAIN_MONITORING_SURFACE)
    return (
        f"QTableWidget {{ background: {bg}; color: {fg}; border: none; "
        f"gridline-color: {grid}; font-family: monospace; font-size: {font_size_px}px; }}"
        f"QTableWidget::item:selected {{ background: {sel}; }}"
    )


def rd_monospace_list_qss(*, font_size_px: int = 11) -> str:
    bg = _c(ThemeTokenId.DOMAIN_MONITORING_BG)
    fg = _c(ThemeTokenId.DOMAIN_MONITORING_TEXT)
    sel = _c(ThemeTokenId.DOMAIN_MONITORING_SURFACE)
    return (
        f"QListWidget {{ background: {bg}; color: {fg}; border: none; "
        f"font-family: monospace; font-size: {font_size_px}px; }}"
        f"QListWidget::item:selected {{ background: {sel}; }}"
    )


def rd_detail_text_edit_qss() -> str:
    surf = _c(ThemeTokenId.DOMAIN_MONITORING_SURFACE)
    fg = _c(ThemeTokenId.DOMAIN_MONITORING_TEXT)
    return (
        f"QTextEdit {{ background: {surf}; color: {fg}; border: none; "
        f"font-family: monospace; font-size: 12px; padding: 8px; border-radius: 6px; }}"
    )


def rd_metric_value_colors() -> tuple[str, ...]:
    """Reihenfolge für KPI-Karten — aus semantischen Tokens, nicht Regenbogen-Hex."""
    return (
        _c(ThemeTokenId.DOMAIN_MONITORING_ACCENT),
        _c(ThemeTokenId.CHART_SERIES_3),
        _c(ThemeTokenId.INDICATOR_RUNNING),
        _c(ThemeTokenId.STATE_SUCCESS),
        _c(ThemeTokenId.STATE_ERROR),
        _c(ThemeTokenId.DOMAIN_MONITORING_MUTED),
    )


def rd_metric_refresh_colors(*, has_error_line: bool) -> tuple[str, ...]:
    """Farben für die sechs KPI-Werte nach Refresh (Slot 4 = Letzter Fehler)."""
    cols = list(rd_metric_value_colors())
    cols[4] = _c(ThemeTokenId.STATE_ERROR) if has_error_line else _c(ThemeTokenId.DOMAIN_MONITORING_MUTED)
    cols[5] = _c(ThemeTokenId.DOMAIN_MONITORING_MUTED)
    return tuple(cols)


def rd_status_color_for_label(status: str) -> str:
    s = (status or "").lower()
    if s in ("running", "active", "started"):
        return _c(ThemeTokenId.CHART_SERIES_3)
    if s in ("completed", "success", "ok", "healthy", "selected", "finished"):
        return _c(ThemeTokenId.STATE_SUCCESS)
    if s in ("failed", "error", "critical"):
        return _c(ThemeTokenId.STATE_ERROR)
    if s in ("idle", "pending"):
        return _c(ThemeTokenId.DOMAIN_MONITORING_MUTED)
    return _c(ThemeTokenId.DOMAIN_MONITORING_MUTED)


def rd_node_card_qss(*, border_color: str, border_radius: int = 8) -> str:
    surf = _c(ThemeTokenId.DOMAIN_MONITORING_SURFACE)
    return (
        f"background: {surf}; border: 1px solid {border_color}; border-radius: {border_radius}px; "
        "padding: 12px;"
    )


def rd_card_title_qss() -> str:
    return (
        f"color: {_c(ThemeTokenId.DOMAIN_MONITORING_TEXT)}; font-weight: 600; font-size: 12px;"
    )


def rd_card_status_qss(color: str) -> str:
    return f"color: {color}; font-size: 11px;"


def rd_list_item_muted_qss() -> str:
    """QColor name for setForeground on items."""
    return _c(ThemeTokenId.DOMAIN_MONITORING_MUTED)


def rd_kpi_inner_card_qss(*, border_radius: int = 6) -> str:
    """Metrik-Kachel innerhalb eines Monitoring-Panels."""
    surf = _c(ThemeTokenId.DOMAIN_MONITORING_SURFACE)
    bd = _c(ThemeTokenId.DOMAIN_MONITORING_BORDER)
    return (
        f"background: {surf}; border: 1px solid {bd}; border-radius: {border_radius}px; "
        "padding: 12px;"
    )


def rd_kpi_caption_qss(*, font_size_px: int = 11) -> str:
    return f"color: {_c(ThemeTokenId.DOMAIN_MONITORING_MUTED)}; font-size: {font_size_px}px;"


def rd_kpi_value_qss(*, color: str, font_size_px: int = 20) -> str:
    return (
        f"color: {color}; font-weight: 600; font-size: {font_size_px}px; font-family: monospace;"
    )


def rd_embedded_row_frame_qss(*, padding_px: int = 8, radius: int = 6) -> str:
    """Zeilen/Timeline in Monitoring — ersetzt frühere rgba(255,255,255,…)-Flächen."""
    surf = _c(ThemeTokenId.DOMAIN_MONITORING_SURFACE)
    bd = _c(ThemeTokenId.DOMAIN_MONITORING_BORDER)
    return (
        f"background: {surf}; border-radius: {radius}px; padding: {padding_px}px; "
        f"border: 1px solid {bd};"
    )


def rd_label_line_qss(*, font_size_px: int = 11, muted: bool = False) -> str:
    tid = ThemeTokenId.DOMAIN_MONITORING_MUTED if muted else ThemeTokenId.DOMAIN_MONITORING_TEXT
    return f"font-size: {font_size_px}px; color: {_c(tid)};"


def rd_bold_title_qss(*, font_size_px: int = 13) -> str:
    return f"font-weight: bold; font-size: {font_size_px}px; color: {_c(ThemeTokenId.DOMAIN_MONITORING_TEXT)};"


def rd_monospace_line_qss(*, font_size_px: int = 11) -> str:
    fg = _c(ThemeTokenId.DOMAIN_MONITORING_TEXT)
    return f"font-size: {font_size_px}px; font-family: monospace; color: {fg};"


def rd_graph_ok_border_color() -> str:
    """Einheitliche „OK“-Kante für System-Graph-Knoten."""
    return _c(ThemeTokenId.DOMAIN_MONITORING_ACCENT)


def rd_task_status_color(status: str) -> str:
    """Task-/Tool-Status für Text oder linke Akzentkante."""
    s = (status or "").lower()
    if s == "pending":
        return _c(ThemeTokenId.DOMAIN_MONITORING_MUTED)
    if s in ("running", "started", "active"):
        return _c(ThemeTokenId.INDICATOR_RUNNING)
    if s in ("completed", "success", "ok"):
        return _c(ThemeTokenId.STATE_SUCCESS)
    if s in ("failed", "error"):
        return _c(ThemeTokenId.STATE_ERROR)
    return _c(ThemeTokenId.DOMAIN_MONITORING_MUTED)


def rd_task_row_frame_qss(*, left_accent_color: str, padding_px: int = 6) -> str:
    """Task-Zeile mit farbigem linken Rand."""
    surf = _c(ThemeTokenId.DOMAIN_MONITORING_SURFACE)
    return (
        f"background: {surf}; border-radius: 6px; padding: {padding_px}px; "
        f"border: none; border-left: 3px solid {left_accent_color};"
    )
