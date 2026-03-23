# Pilot Layout Refactor — Analyse (Phase 0)

## Betroffene Dateien

| Bereich | Dateien |
|---------|---------|
| Settings | `app/gui/domains/settings/settings_dialog.py` |
| CC Providers | `app/gui/domains/control_center/workspaces/providers_workspace.py`, `app/gui/domains/control_center/panels/providers_panels.py` |
| CC Styles | `app/gui/themes/control_center_styles.py` (`cc_panel_frame_style`, `cc_refresh_button_style`) |
| Workbench | `app/gui/workbench/ui/design_tokens.py` (`INSPECTOR_INNER_MARGIN_PX`) |
| Shared | `app/gui/shared/layout_constants.py`, `app/gui/theme/design_metrics.py` |
| Tests | `tests/unit/gui/test_settings_dialog_layout.py`, `test_providers_workspace_layout.py`, `test_workbench_inspector_layout.py` |

## Aktuelle Problemwerte (Ist, vor Pilot)

| Ort | Problem |
|-----|---------|
| `settings_dialog.py` | `layout.setSpacing(20)`, `form.setSpacing(14)` — bricht 4px-Raster und Audit-Ziel 12 |
| | `main_layout` nur unten 12 — ok, aber nicht benannt |
| | `QFormLayout` ohne Label-Alignment / Field-Growth-Policy |
| | `api_key_edit` min width 280 — Magic Number |
| `providers_workspace.py` | `24/16` hardcoded statt `SCREEN_PADDING` / `CARD_SPACING` |
| `providers_panels.py` | `layout.setContentsMargins(16,…)` hardcoded |
| `cc_panel_frame_style` | QSS `padding: 12px` **+** Layout-Margins 16 → **Doppel-Innenabstand** |
| `cc_refresh_button_style` | `6px 12px` hardcoded |
| Workbench Inspector | `INSPECTOR_INNER_MARGIN_PX = 10` vs. Shell 12px |

## Anzuwendende Regeln (`LAYOUT_SYSTEM_RULES.md`)

- Dialog-Innen **24**, Block-Abstand zwischen Form und GroupBoxes **16** (`CARD_SPACING`)
- Form: Zeile **12**, Label↔Feld **8**, Labels rechtsbündig
- Karten-Innen **16**, Workspace-Außen **24**
- Footer-Abstand Dialog: **12** (`DIALOG_FOOTER_TOP_GAP_PX`)
- Kein doppeltes Card-Padding (QSS + Layout)

## Ersetzungen (geplant → umgesetzt)

| Alt | Neu |
|-----|-----|
| 20 / 14 spacing | 16 (VBox) / 12+8 (QFormLayout vertical/horizontal) |
| 24/24 content margins | `apply_dialog_scroll_content_layout` |
| 24,0,24,0 button bar | `apply_dialog_button_bar_layout` |
| 16 panel margins | `apply_card_inner_layout` |
| QSS padding 12 on CC frame | `padding: 0` + nur Layout 16 |
| 10 inspector | 12 |

## Risiken

- **ThemeManager:** `cc_panel_frame_style` / Refresh brauchen aktives Theme — Tests nutzen bestehende Session-`QApplication`.  
- **Async:** `SettingsDialog.load_settings_to_ui` ruft `asyncio.create_task` — Unit-Tests patchen `create_task`.  
- **Visuell:** Entfernen des QSS-Paddings verschiebt Inhalt um ~12px nach außen (kompensiert durch einheitliche 16px Layout — Netto ähnlicher Sichtabstand zur Kante).  
- **Andere CC-Panels:** nutzen weiterhin lokales `_cc_panel_style` mit evtl. eigenem Padding — nur **Providers** nutzen `cc_panel_frame_style`.
