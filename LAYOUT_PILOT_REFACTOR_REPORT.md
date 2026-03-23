# Layout Pilot Refactor — Abschlussbericht

## 1. Executive Summary

Ein **gezielter Pilot** harmonisiert **SettingsDialog**, **Control Center → Providers Workspace** (inkl. Panel-QSS) und die **Workbench-Inspector-Innenmargin** mit dem kanonischen Raster aus `LAYOUT_SYSTEM_RULES.md`. Zentrale **`apply_*`-Helfer** in `layout_constants.py` kapseln Werte aus `design_metrics.py`. Zehn neue/gezielte **Unit-Tests** prüfen Margin/Spacing/Policy; der volle Ordner `tests/unit/gui/` enthält **einen bestehenden Fehler** im Theme-Visualizer-Test (Singleton), nicht Teil dieses Pilots.

## 2. Betroffene Dateien

- `app/gui/shared/layout_constants.py`
- `app/gui/theme/design_metrics.py`
- `app/gui/domains/settings/settings_dialog.py`
- `app/gui/domains/control_center/workspaces/providers_workspace.py`
- `app/gui/domains/control_center/panels/providers_panels.py`
- `app/gui/themes/control_center_styles.py`
- `app/gui/workbench/ui/design_tokens.py`
- `tests/unit/gui/test_settings_dialog_layout.py`
- `tests/unit/gui/test_providers_workspace_layout.py`
- `tests/unit/gui/test_workbench_inspector_layout.py`
- `docs/design/LAYOUT_SPACING_MIGRATION_PLAN.md`
- `docs/design/LAYOUT_SYSTEM_RULES.md`
- `docs/design/PILOT_LAYOUT_REFACTOR_NOTES.md`
- `docs/design/PILOT_LAYOUT_REFACTOR_RESULTS.md`

## 3. Alte Werte → neue Werte

| Bereich | Alt | Neu |
|---------|-----|-----|
| Settings: VBox spacing | 20 | 16 (`CARD_SPACING`) |
| Settings: Form | `setSpacing(14)` | vertical 12 / horizontal 8 (`apply_form_layout_policy`) |
| Settings: Scroll-Inhalt margins | 24 (literal) | `apply_dialog_scroll_content_layout` → `DIALOG_PADDING_PX` |
| Settings: Button-Leiste | margins 24,0,24,0 spacing 12 | `apply_dialog_button_bar_layout` |
| Settings: Footer-Gap | 12 (literal) | `DIALOG_FOOTER_TOP_GAP_PX` |
| Settings: API-Key min width | 280 | `WIDE_LINE_EDIT_MIN_WIDTH_PX` |
| Providers workspace | margins/spacing 24/16 literals | `SCREEN_PADDING` / `CARD_SPACING` |
| Provider panels inner | `16` literals | `apply_card_inner_layout` |
| `cc_panel_frame_style` | padding 12px | padding 0 |
| `cc_refresh_button_style` | 6px 12px, 6px radius, 12px font | `PADDING_COMPACT_*`, `RADIUS_SM_PX`, `TEXT_SM_PX` |
| Workbench inspector | 10px inner | 12px (`INSPECTOR_INNER_MARGIN_PX`) |

## 4. Angewandte Regeln (real im Code)

- Dialog-Innen **24px**; Abstand Scroll-Bereich → Button-Zeile **12px**; Block-Abstand im Scroll **16px**.
- Form **12px** Zeilen, **8px** Label↔Feld, **rechtsbündige** Labels, wachsende Felder.
- Workspace-Außen **24px** (`SCREEN_PADDING` = gleicher Zahlenwert wie Dialog-Padding).
- Karten-Innen **16px** nur über Layout (kein zusätzliches QSS-Padding auf dem CC-Frame für Providers).
- Zwischen Widgets in Provider-Karten **12px** (`WIDGET_SPACING`).

## 5. Entfernte / reduzierte Magic Numbers

- 20, 14 (Settings spacing)
- 24, 16, 12 (teilweise durch benannte Konstanten/Helfer ersetzt)
- 280 (API-Key-Breite)
- 12 (QSS padding auf CC-Frame)
- 6, 12 in Refresh-QSS (durch Metriken)
- 10 → 12 Inspector

Verbleibend bewusst: **36px** feste Breite für den Prompt-„…“-Button (kompakter Browse-Button).

## 6. Form-Policy

**Funktionsfähig** für alle drei `QFormLayout`s im Settings-Dialog (Hauptform, API-Key-Gruppe, Prompt-Gruppe).  
**Einschränkung:** Mindestlabelbreite **120px** ist in `design_metrics` dokumentiert, aber **nicht** automatisch auf alle `QLabel`-Widgets angewendet — bei extrem langen Labels ggf. nachschärfen.

## 7. Teststatus

| Suite | Ergebnis |
|-------|----------|
| `pytest tests/unit/gui/test_settings_dialog_layout.py tests/unit/gui/test_providers_workspace_layout.py tests/unit/gui/test_workbench_inspector_layout.py` | **10 passed** |
| `pytest tests/unit/gui/` gesamt | **1 failed** (`test_theme_visualizer_integration.py::test_launcher_single_instance_and_reopen` — vorbestehende Singleton-Leiche) |

## 8. Offene Restrisiken

- Nur **Providers** nutzen das neue `cc_panel_frame_style` (padding 0); andere CC-Dateien mit `_cc_panel_style` bleiben uneinheitlich.
- **Visuelle Regression:** Karten wirken minimal anders (ein Innenabstandspfad statt QSS+Layout-Doppelung).
- **SettingsDialog** weiterhin **Legacy-Modal**; eingebettete Shell-Settings nicht in diesem Pilot angefasst.

## 9. Empfohlene nächste Refactor-Kandidaten

1. CC **Models** / **Tools** — `_cc_panel_style` mit gleichem Muster wie Providers.  
2. **data_settings_panel** / **advanced_settings_panel** — `apply_form_layout_policy`.  
3. **QSS shell.qss** Magic Padding (gesonderter kleiner PR).

---

## Fragen A–C

**A. Ist der Settings Dialog jetzt ein kanonischer Referenzdialog?**  
**Ja**, als **erster** Referenz für modale Dialoge mit Scroll + Form + GroupBoxes + Button-Leiste; eingebettete Settings-Seiten sollten nachziehen.

**B. Ist der Providers Workspace jetzt ein kanonischer Referenz-Workspace?**  
**Ja** für **CC-Management-Workspaces** mit gestapelten Karten: Außen 24 / zwischen Karten 16 / Karten-Innen 16 / Rahmen ohne QSS-Padding.

**C. Reicht die Policy für weitere Dialoge/Panels?**  
**Größtenteils ja** — für komplexe Dialoge mit variabler Label-Länge ist **Nachschärfung** sinnvoll (explizite Label-Mindestbreite oder `QGridLayout`). Die Helfer sind bewusst klein gehalten und erweiterbar.
