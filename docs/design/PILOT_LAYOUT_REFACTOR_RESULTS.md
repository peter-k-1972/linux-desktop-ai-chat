# Pilot Layout Refactor — Ergebnisse

## Umgesetzt

1. **`layout_constants.py`**
   - Aliase `DIALOG_CONTENT_PADDING`, `CARD_INNER_PADDING` (aus `design_metrics`).
   - `apply_dialog_scroll_content_layout` — Scroll-Inhalt 24px Rand, vertikaler Block-Abstand 16px (`CARD_SPACING`).
   - `apply_dialog_button_bar_layout` — horizontal 24px, `spacing` 12px.
   - `apply_form_layout_policy` — QFormLayout: vertical 12, horizontal 8, rechtsbündige Labels, `AllNonFixedFieldsGrow`.
   - `apply_card_inner_layout` — 16px Innenrand für Karten-Panel-Inhalt.

2. **`design_metrics.py`**
   - `FORM_LABEL_MIN_WIDTH_DESKTOP_PX`, `WIDE_LINE_EDIT_MIN_WIDTH_PX`, `DIALOG_FOOTER_TOP_GAP_PX`.

3. **`settings_dialog.py`**
   - Kanonische Helfer; `settingsDialogContent` objectName für Tests.
   - Nested `QFormLayout`s (API-Key, Prompt) mit gleicher Policy.
   - `WIDGET_SPACING` auf horizontalen Zeilen (Key, Status, Verzeichnis).

4. **`providers_workspace.py`**
   - `SCREEN_PADDING` / `CARD_SPACING`; `objectName` `providersWorkspaceRoot` (überschreibt Basis-`cc_providersWorkspace` für klare Test-ID).

5. **`providers_panels.py`**
   - `apply_card_inner_layout` + `WIDGET_SPACING` (12) zwischen vertikalen Elementen und in der Titelzeile.

6. **`control_center_styles.py`**
   - `cc_panel_frame_style`: `padding: 0` — ein Innenabstandspfad (Python 16px).
   - `cc_refresh_button_style`: kompaktes Padding/Radius/Schrift aus `design_metrics`.

7. **`design_tokens.py` (Workbench)**
   - `INSPECTOR_INNER_MARGIN_PX`: 10 → **12** (Shell-Parität).

## Harmonisierte Werte (Kurz)

| Kontext | Vorher | Nachher |
|---------|--------|---------|
| Settings VBox spacing | 20 | 16 (`CARD_SPACING`) |
| Settings Form | spacing 14 | vertical 12 / horizontal 8 |
| Settings API min width | 280 literal | `WIDE_LINE_EDIT_MIN_WIDTH_PX` |
| Settings main bottom | 12 literal | `DIALOG_FOOTER_TOP_GAP_PX` |
| Providers workspace | 24/16 literals | `SCREEN_PADDING` / `CARD_SPACING` |
| Provider cards inner | 16 literal | `apply_card_inner_layout` → `CARD_PADDING_PX` |
| CC frame QSS padding | 12px | 0px |
| Inspector inner | 10 | 12 |

## Bewährte Regeln

- **Eine Quelle für Zahlen:** `design_metrics` + dünne `apply_*`-API in `layout_constants`.
- **Kein Doppel-Padding:** Rahmen per QSS, Inhalt per `QLayout` margins.
- **Form-Policy zentral:** ein Aufruf pro `QFormLayout`.

## Offen / nächste Schritte

- **Eingebettete Settings** (Kategorien in Shell) und **`advanced_settings_panel` / `data_settings_panel`** — gleiche `apply_form_layout_policy`.
- **CC `models_panels` / `tools_panels`:** `_cc_panel_style` auf Modell „padding 0 + apply_card_inner_layout“ angleichen.
- **Label min width 120:** in Qt nicht global für QFormLayout — bei langen deutschen Labels gezielt `QLabel.setMinimumWidth` prüfen.
- **`tests/unit/gui/test_theme_visualizer_integration.py`** — schlägt bei vollem `tests/unit/gui/`-Lauf fehl (Singleton `_instance`); **nicht** durch diesen Pilot verursacht.

## Empfohlener nächster Pilot

1. **Control Center — Models Workspace** (größte Nutzung von `_cc_panel_style`).  
2. **Settings-Kategorie-Panels** (eingebettet, nicht modal).
