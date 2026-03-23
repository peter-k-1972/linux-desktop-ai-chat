# Pilot Layout Refactor — Phase 2

## Migrierte Screens / Komponenten

| Bereich | Dateien |
|---------|---------|
| Projects Liste | `app/gui/domains/operations/projects/panels/project_list_panel.py` |
| Projects Overview | `app/gui/domains/operations/projects/panels/project_overview_panel.py` |
| KPI Stats | `app/gui/domains/operations/projects/panels/project_stats_panel.py` |
| Projekt bearbeiten | `app/gui/domains/operations/projects/dialogs/project_edit_dialog.py` |
| Workbench Header | `panel_header.py`, `workflow_header.py`, `context_action_bar.py` |
| Shared | `layout_constants.py` (`apply_header_profile_margins`, `HeaderProfile`), `design_metrics.py` (`HEADER_*_MARGINS`, `LIST_ITEM_MIN_HEIGHT_PX`) |

## Bestätigte Regeln

- **Workspace-Listen-Spalte:** Compact **12** (`SIDEBAR_PADDING`), vertikaler Block-Abstand **12** (`WIDGET_SPACING`).
- **Overview-Hauptfläche:** **20** (`PANEL_PADDING`), vertikale Sektions-Abstände **16** (`CARD_SPACING`).
- **KPI-Karten:** **16** Innenrand nur per `QLayout` + Rahmen-QSS `padding:0` (kein Doppel-Padding).
- **Listen:** `QListWidget` **spacing 4**; Items **min-height 32** (`LIST_ITEM_MIN_HEIGHT_PX`).
- **Dialoge:** 24 / 16 / 12-8 Form / Button-Zeile wie Pilot 1.
- **Header:** drei Profile aus **einer** Quelle (`design_metrics`).

## Anpassungen / Abweichungen vom ersten Entwurf

- **PanelHeader** unten: von 8px auf **10px** angeglichen (**standard** = 12,10,12,10) — bewusst.
- **Stat-Card:** früher QSS-Padding + Layout — jetzt nur Layout 16px.
- **Overview-Aktionsbuttons:** Padding **12×16** (`SPACE_MD` × `SPACE_LG`) statt 10×18.
- **`NewProjectDialog`** (`projects_workspace.py`): **nicht** umgebaut — nächster kleiner Schritt empfohlen.

## Stabile Muster für weitere Migration

1. **Operations linke Spalte:** `SIDEBAR_PADDING` + `WIDGET_SPACING` + `design_metrics` in Item-QSS.
2. **Operations Haupt-Content:** `PANEL_PADDING` + `CARD_SPACING`.
3. **Karten mit QSS-Rahmen:** `padding:0` im Selector + `apply_card_inner_layout`.
4. **Modale Dialoge mit vielen Zeilen:** `QVBoxLayout` → Body mit `apply_dialog_scroll_content_layout` → `QFormLayout` + `apply_form_layout_policy` → `apply_dialog_button_bar_layout`.
5. **Chrome-Zeilen:** `apply_header_profile_margins(layout, "standard"|"compact"|"ultra")`.

## Referenz-Dokumente

- `docs/design/PROJECTS_LAYOUT_REFACTOR_NOTES.md` (Phase-0-Ist)
- `docs/design/LAYOUT_SYSTEM_RULES.md`
- `LAYOUT_PILOT_REFACTOR_PHASE2_REPORT.md` (Abschluss)
