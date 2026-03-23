# Layout- & Spacing-Migrationsplan

**Übergeordnete UI-Regeln (Layout, Farbe, Icons, Ownership, Review):** [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md) · [UI_REVIEW_CHECKLIST.md](./UI_REVIEW_CHECKLIST.md)

---

## Pilot-Stand (2026-03)

**Erledigt (siehe `docs/design/PILOT_LAYOUT_REFACTOR_RESULTS.md`):**

- `SettingsDialog` — Dialog-Innen 24px, Block-Abstand 16px, Form 12/8, Button-Leiste, `apply_form_layout_policy`.
- `ProvidersWorkspace` + `providers_panels` — Außen 24px (`SCREEN_PADDING`), zwischen Karten 16px (`CARD_SPACING`), Karten-Innen 16px via `apply_card_inner_layout`; `cc_panel_frame_style` ohne QSS-Padding (kein Doppel-Innenrand).
- **Workbench:** `INSPECTOR_INNER_MARGIN_PX` **10 → 12** in `app/gui/workbench/ui/design_tokens.py`.
- **Hilfsfunktionen:** `apply_dialog_scroll_content_layout`, `apply_dialog_button_bar_layout`, `apply_form_layout_policy`, `apply_card_inner_layout` in `app/gui/shared/layout_constants.py` (Werte aus `design_metrics`).

**Tests:** `tests/unit/gui/test_settings_dialog_layout.py`, `test_providers_workspace_layout.py`, `test_workbench_inspector_layout.py`.

### Pilot Phase 2 (2026-03)

**Erledigt (siehe `docs/design/PILOT_LAYOUT_REFACTOR_PHASE2.md`):**

- **Operations → Projects:** `project_list_panel`, `project_overview_panel`, `project_stats_panel` — `PANEL_PADDING` / `CARD_SPACING` / `SIDEBAR_PADDING`, KPI-Karten 16px Innenrand (Layout-only, QSS `padding:0`), Liste `spacing` 4px, Item `min-height` 32px.
- **Dialog:** `ProjectEditDialog` — gleiches Muster wie Settings-Pilot (`apply_dialog_scroll_content_layout`, `apply_form_layout_policy`, `apply_dialog_button_bar_layout`).
- **Workbench-Header:** `apply_header_profile_margins` + `design_metrics.HEADER_*` — `PanelHeader` (standard), `WorkflowCanvasHeader` (compact), `ContextActionBar` (ultra); `apply_header_layout` delegiert auf **standard**.

**Tests:** `test_projects_workspace_layout.py`, `test_operations_dialog_layout.py`, `test_header_profiles.py`.

### QSS ↔ Python Doppelquellen (2026-03)

**Erledigt (Teil):** Ownership-Dokumente, Audit, kanonische Fälle, `tools/layout_double_source_guard.py`; Chat `modelCombo` ohne Python-Mindesthöhe; Legacy-Sidebar-Größen auf `design_metrics`. Bericht: `QSS_PYTHON_DOUBLE_SOURCE_CLEANUP_REPORT.md`.

**Tests:** `test_qss_python_ownership_rules.py`, `test_layout_double_source_cleanup.py`, `tests/tools/test_layout_double_source_guard.py`.

---

## 1. Harmonisiere zuerst (höchster Nutzen / geringstes Risiko)

1. **`layout_constants` ↔ `design_metrics`** — Pilot: neue `apply_*`-Helfer; weiteres Ausrollen auf weitere Screens.  
2. **Workbench Inspector** — erledigt (12px).  
3. **QSS Magic Padding** in `shell.qss` (6×12, 4×8) → `{{spacing_*}}` Platzhalter.  
4. **Form spacing** — Settings erledigt; **Advanced/Data**-Panels noch ausstehend.

---

## 2. Wo entsteht die meiste Unruhe?

| Prio | Bereich | Warum |
|------|---------|-------|
| 1 | **Chat** (`conversation_view.py`, `input_panel.py`, `chat_composer_widget.py`) | **Erledigt (2026-03):** `design_metrics.CHAT_*`, max. Spalte 800px, Composer elastisch, Buttons 32/40 — siehe `CHAT_LAYOUT_POLICY.md`, `CHAT_LAYOUT_REFACTOR_REPORT.md` |
| 2 | **Shell-Workspace-Wechsel** | 8/12/16/24/32 zwischen Areas ohne Host-Absicherung |
| 3 | **Dashboard** | 32px Rand + 20/24 Grid — fühlt sich „anders“ an als Operations |
| 4 | **Context Action Bar vs. PanelHeader** | Phase 2: Profile vereinheitlicht — weiter beobachten |

---

## 3. Magic Numbers zuerst ersetzen (konkret)

| Datei / Stelle | Wert | Ersatz |
|-----------------|------|--------|
| `conversation_view.py` | 1200 min/max width | **erledigt:** `CHAT_CONTENT_MAX_WIDTH_PX` 800, min 0 |
| `conversation_view.py` | 32,40,28 margins/spacing | **erledigt:** `PANEL_PADDING_PX` + `SPACE_LG_PX` |
| `chat_composer_widget.py` | 1000 container | **erledigt:** elastisch, gleiche max wie Content-Spalte |
| `input_panel.py` | 48 button height | **erledigt:** Prompt 32, Send 40 (`CHAT_PRIMARY_SEND_HEIGHT_PX`) |
| `dashboard_screen.py` | 32 margins | **24** oder **20** je Zielbild |
| `project_stats_panel.py` | 14,12 margins | **16** oder **12** nach Card-Regel |
| `settings_dialog.py` | spacing 20, form 14 | **erledigt** — 16 (Blöcke) / 12+8 (Form) |
| `legacy/*` | diverse | deprecate oder hinter Feature-Flag |

---

## 4. Tokenisierung (QSS + Python)

| Wert-Typ | Mechanismus |
|----------|-------------|
| Panel/Card/Dialog padding | `ThemeTokens` erweitern oder ausschließlich `design_metrics` in Python; QSS bleibt `{{panel_padding}}` etc. |
| Header-Profile | drei neue Platzhalter oder eine QSS-Klasse `.headerStandard` / `.headerCompact` |
| Button/Input-Höhe | `min-height: {{control_height_md}}` in QSS; Python `setFixedHeight` entfernen wo möglich |
| Listen-Zeilenhöhe | ein Token `size_list_row_md` für QSS |

---

## 5. Regression vermeiden

- **Pro PR ein Bereich** (z. B. nur Chat oder nur Settings).  
- **Light + Dark** visuell prüfen (Ränder betreffen oft nur Layout, nicht Farbe).  
- **Mindestfenster 1000×700** testen — besonders nach Entfernen der 1200px-Regel.  
- Screenshot-Checkliste: Shell-Ops-Chat, CC-Providers, Workbench-Explorer+Inspector, Settings-Dialog, Dashboard.

---

## 6. Pilot-Screens (in dieser Reihenfolge)

1. **Settings Dialog** — begrenzte Fläche, hohe Sichtbarkeit, klare Form-Struktur.  
2. **Control Center — Providers Workspace** — typisches 24+16 Muster, repräsentativ.  
3. **Operations — Project List + Overview** — zwei Dichten in einem Flow.  
4. **Workbench — InspectorPanel** — kleine Konstantenänderung, großer Wirkungsgrad.  
5. **Chat — ConversationView + Input** — **erledigt** (siehe `CHAT_LAYOUT_REFACTOR_NOTES.md`, `test_chat_layout_refactor.py`).

---

## 7. Abhängigkeiten

- Theme-/Token-Pipeline muss neue Platzhalter aufnehmen (`loader.py` bleibt kompatibel).  
- Keine Pflicht, Farben anzufassen — Layout zuerst.

---

*Gesamtüberblick:* [LAYOUT_SPACING_AUDIT_REPORT.md](../../LAYOUT_SPACING_AUDIT_REPORT.md)
