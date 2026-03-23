# Layout Pilot Refactor — Phase 2 Abschlussbericht

## 1. Executive Summary

Phase 2 überträgt das Layoutsystem auf **Operations → Projects** (Liste, Overview, KPI-Stats), den **ProjectEditDialog** und die **Workbench-Header-Chrome** (Panel, Workflow, Context-Bar). Zentrale Erweiterung: **`apply_header_profile_margins`** und **`HEADER_*_MARGINS`** in `design_metrics`. **11 neue Unit-Tests** decken Header-Profile, Projects-Panels und den Dialog ab. **`NewProjectDialog`** bleibt bewusst unverändert (Follow-up).

## 2. Betroffene Dateien

- `app/gui/theme/design_metrics.py`
- `app/gui/shared/layout_constants.py`
- `app/gui/domains/operations/projects/panels/project_list_panel.py`
- `app/gui/domains/operations/projects/panels/project_overview_panel.py`
- `app/gui/domains/operations/projects/panels/project_stats_panel.py`
- `app/gui/domains/operations/projects/dialogs/project_edit_dialog.py`
- `app/gui/workbench/ui/panel_header.py`
- `app/gui/workbench/ui/context_action_bar.py`
- `app/gui/workbench/workflows/workflow_header.py`
- `docs/design/PROJECTS_LAYOUT_REFACTOR_NOTES.md`
- `docs/design/LAYOUT_SPACING_MIGRATION_PLAN.md`
- `docs/design/PILOT_LAYOUT_REFACTOR_PHASE2.md`
- `tests/unit/gui/test_projects_workspace_layout.py`
- `tests/unit/gui/test_operations_dialog_layout.py`
- `tests/unit/gui/test_header_profiles.py`

## 3. Alte Werte → neue Werte (Auszug)

| Ort | Vorher | Nachher |
|-----|--------|---------|
| Liste: VBox spacing | 8 | `WIDGET_SPACING` (12) |
| Liste: `QListWidget` spacing | 2 | `SPACE_XS_PX` (4) |
| Liste: Item padding / min-height | 10×12, kein min-height | 8×12, **32px** min-height |
| Overview: outer spacing | 20 | `CARD_SPACING` (16) zwischen Blöcken |
| Overview: Monitoring/Control QSS padding | 14px | `CARD_PADDING_PX` (16), `padding:0` nur für Stats-Karten + Layout |
| Stats: KPI layout margins | 14,12 | `apply_card_inner_layout` (16) |
| Stats: outer spacing | 10 | `WIDGET_SPACING` (12) |
| ProjectEditDialog | `QFormLayout(self)` | `QVBoxLayout` + Body + Button-Zeile + Form-Policy |
| PanelHeader margins | 12,10,12,**8** | **standard** 12,10,12,10 |
| Workflow header | 12,8,12,8 (ok) | `apply_header_profile_margins(..., "compact")` |
| Context bar | 8,6,8,6 (ok) | `apply_header_profile_margins(..., "ultra")` |

## 4. Header-Profile (implementiert)

| Profil | Konstante | Komponente |
|--------|-----------|------------|
| standard | `HEADER_STANDARD_MARGINS` (12,10,12,10) | `PanelHeader` |
| compact | `HEADER_COMPACT_MARGINS` (12,8,12,8) | `WorkflowCanvasHeader` |
| ultra | `HEADER_ULTRA_MARGINS` (8,6,8,6) | `ContextActionBar` |

API: `apply_header_profile_margins(layout, "standard"|"compact"|"ultra")`.  
`apply_header_layout` ruft **standard** auf (Rückwärtskompatibilität).

## 5. Form-Layouts (ProjectEditDialog)

- `apply_form_layout_policy`: vertikal **12**, horizontal **8**, rechtsbündige Labels.
- Inhalt in `apply_dialog_scroll_content_layout` (24px Rand, 16px Block-Spacing im Body-VBox).
- `QDialogButtonBox` in eigener Zeile mit `apply_dialog_button_bar_layout` + `addStretch`.

## 6. Entfernte / ersetzte Magic Numbers

- 14 (KPI / Overview-Frames) → 16 oder Layout-only.
- 10 (Stats-Spacing, früher List-Padding) → 12 / 8 je Kontext.
- 2 (Listen-Spacing) → 4.
- 8 (PanelHeader unten) → 10 (Standardprofil).
- Viele feste px in Projects-QSS durch `design_metrics`-Interpolation (ohne Farb-Redesign).

Verbleibend: **farbige** RGBA-Styles in Overview (bewusster Dark-Hub-Look) — separater Theme-Schritt.

## 7. Teststatus

```text
pytest tests/unit/gui/test_header_profiles.py \
       tests/unit/gui/test_projects_workspace_layout.py \
       tests/unit/gui/test_operations_dialog_layout.py
```

→ **11 passed** (lokal verifiziert).

## 8. Nächste Migrations-Kandidaten

1. `NewProjectDialog` in `projects_workspace.py` — gleiches Dialog-Muster wie `ProjectEditDialog`.
2. `project_activity_panel` / `project_quick_actions_panel` — auf `CARD_SPACING` / `WIDGET_SPACING` prüfen.
3. Weitere Operations-Workspaces (Knowledge, Agent Tasks) mit **Panel 20 / Gap 16 / Compact 12**.
4. `shell.qss` Magic-Padding (globaler kleiner PR).

---

## Fragen A–C

**A. Funktioniert das Layoutsystem stabil über mehrere Domains?**  
**Ja** — gleiche Helfer für **Settings**, **CC Providers**, **Projects**, **Workbench-Header** und **ProjectEditDialog**; Werte stammen durchgängig aus `design_metrics` + `layout_constants`.

**B. Sind Header-Profile ausreichend abstrahiert?**  
**Ja** für die drei bestehenden Chrome-Typen. Falls später z. B. „dense sidebar title“ nötig wird, entweder viertes Profil oder Wiederverwendung von **compact** mit Dokumentation.

**C. Können weitere Operations-Workspaces schematisch migriert werden?**  
**Ja** — Schema: äußerer Rand `PANEL_PADDING` oder `WORKSPACE_PADDING`, Spalten `SIDEBAR_PADDING`, vertikale Sektionen `CARD_SPACING`, Karten `apply_card_inner_layout` + QSS `padding:0` auf dem Rahmen.
