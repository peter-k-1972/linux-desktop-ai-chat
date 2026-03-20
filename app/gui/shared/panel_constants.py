"""
Panel-Konstanten – Breiten und Layout-Werte für Studio-Panels.

Wird von Chat-Side-Panel, Model-Settings-Panel und Prompt-Manager-Panel genutzt.
Domain-übergreifend in shared, um Cross-Domain-Imports zu vermeiden.
"""

from PySide6.QtGui import QFont, QFontMetrics


def _calc_prompts_panel_widths():
    font = QFont()
    font.setPixelSize(14)
    fm = QFontMetrics(font)
    padding = 18 * 2
    preview_text = "x" * 80
    list_item_width = fm.horizontalAdvance(preview_text)
    longest_label = max(
        fm.horizontalAdvance("Beschreibung"),
        fm.horizontalAdvance("Tags (kommagetrennt)"),
        fm.horizontalAdvance("instruction"),
        400,
    )
    width_content = max(list_item_width, longest_label) + 48
    btn1 = fm.horizontalAdvance("In Chat übernehmen") + padding
    btn2 = fm.horizontalAdvance("Als Systemprompt") + padding
    btn3 = fm.horizontalAdvance("In Composer einfügen") + padding
    width_three_buttons = btn1 + btn2 + btn3 + 16
    return width_content + 24, width_three_buttons + 24


_cached_widths = None


def _get_prompts_panel_widths():
    global _cached_widths
    if _cached_widths is None:
        try:
            from PySide6.QtWidgets import QApplication

            if QApplication.instance():
                w_content, w_buttons = _calc_prompts_panel_widths()
                fixed = max(w_content, w_buttons)
                btn_fit = (fixed - 16) // 3 if w_content > w_buttons else None
                _cached_widths = (fixed, btn_fit)
            else:
                _cached_widths = (600, 194)
        except Exception:
            _cached_widths = (600, 194)
    return _cached_widths


def _PROMPTS_PANEL_FIXED_WIDTH() -> int:
    """Feste Breite für Prompts-Panel (Chat-Side-Panel, Model-Settings)."""
    return _get_prompts_panel_widths()[0]


def _BUTTON_WIDTH_IF_FIT() -> int | None:
    """Button-Breite für drei Buttons nebeneinander (Prompt-Manager)."""
    return _get_prompts_panel_widths()[1]
