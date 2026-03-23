# Layout & Spacing Inventory

**Zweck:** Systematische Bestandsaufnahme von Layout-API-Nutzung (Python + QSS) für die modulare Shell- und Workbench-GUI.  
**Stand:** Code-Scan `app/gui/**/*.py`, `app/gui/themes/base/*.qss`.  
**Format:** `type | value | location | component | note | conflict_status`

**Legende `conflict_status`:** `aligned` — passt zur intendierten Skala; `drift` — abweichender Zahlenwert; `split` — zwei gültige Systeme (z. B. Shell vs. Workbench); `qss_python` — QSS und Python setzen dieselbe Dimension unkoordiniert; `legacy` — veraltete Struktur.

---

## A) `setContentsMargins` — häufige Muster (aggregiert)

| type | value | location | component | note | conflict_status |
|------|-------|----------|-----------|------|-----------------|
| margins | 0,0,0,0 | `shell/main_window.py` central_layout; `workbench/main_workbench.py` _central_lay; viele `*_screen.py`, Router-Hosts, Splitter-Roots | Shell central stack, Workbench canvas column, Domain roots | Null-Margin-Pattern für zusammenhängende Flächen | aligned |
| margins | 8,12,8,12 | `navigation/sidebar.py` | Haupt-Sidebar-Inhalt | Asymmetrisch vertikal vs. horizontal | drift |
| margins | 12,10,12,10 | `chat_navigation_panel.py` header_layout; `chat_details_panel.py` header; `workbench/ui/panel_header.py`; `command_center_view.py` | Chat-Nav-Header, Workbench PanelHeader, Command-Center-Kopf | Header-Dichte konsistent **innerhalb** dieser Gruppe | aligned |
| margins | 12,12,12,12 | `chat_navigation_panel.py`; `project_list_panel.py`; `model_inspector.py`; `project_context_inspector.py`; `workflow_inspector_panel.py`; `markdown_demo_panel.py` | Chat-Nav, Projektliste, Inspektoren | „Standard 12“-Raster | aligned |
| margins | 16,16,16,16 | `providers_panels.py` (×3); `tools_workspace` inner; `data_stores_workspace` inner; viele CC/Operations-Panels | Control-Center-Workspaces, Form-Panels | Häufigstes Panel-Innenmaß außerhalb `apply_panel_layout` | drift |
| margins | 16,20,16,16 | `source_details_panel.py`; `settings_workspace.py` | Knowledge-Details, Settings-äußerer Rand | Oben +4px vs. symmetrisch 16 | drift |
| margins | 24,24,24,24 | `settings_dialog.py` layout; `*_workspace.py` (CC, Introspection, …); `canvas_base.py` | Settings-Dialog-Inhalt, CC-Workspace-Wrapper, Canvas-Base | „Luftiges“ 24er-Raster | split |
| margins | 24,16,24,24 | `chat_composer_widget.py` wrapper_layout | Chat-Composer äußerer Wrapper | Unten +8 vs. symmetrisch | drift |
| margins | 16,12,12,12 | `chat_composer_widget.py` inner layout | Composer-Zeilen | Rechts/unten reduziert | drift |
| margins | 14,12,14,12 | `project_stats_panel.py` | KPI-Karte | Ungewöhnliches 14 horizontal | drift |
| margins | 20,20,20,20 | `conversation_panel.py` _content_layout; `project_overview_panel.py` | Chat-Konversations-Inhalt, Projekt-Overview | Kollidiert mit `PANEL_PADDING=20` aber **ohne** zentrale Konstante im Code | qss_python |
| margins | 32,40,32,40 | `conversation_view.py` message_layout | Chat-Nachrichtenspalte | Sehr luftig; fest mit 1200px Breite gekoppelt | drift |
| margins | 32,32,32,32 | `dashboard_screen.py` | Dashboard-äußerer Rand | Maximaler Shell-Content-Padding-Wert im Sample | drift |
| margins | 24,28,24,28 | `workbench/ui/empty_state.py` | Workbench EmptyState | Von `EMPTY_STATE_*` abweichend (28 vertikal) | drift |
| margins | 20,20,20,16 | `workbench/command_palette/command_palette_dialog.py` | Command Palette (Workbench) | Unten −4px vs. symmetrisch | drift |
| margins | 12,8,12,8 | `workbench/workflows/workflow_header.py`; `workflow_builder_canvas.py` sl; `workbench/ui/context_action_bar.py` 8,6,8,6 | Workflow/Context-Leisten | Unterschiedliche vertikale Kompaktheit 6 vs. 8 | drift |
| margins | 8,8,8,8 | `operations/audit_incidents_workspace.py`; `workflow_*_panel.py` (mehrere) | Incident-Audit, Workflow-Editor/Liste | Kompaktes 8er-Raster | aligned |
| margins | 0,0,0,12 | `navigation/workspace_graph.py` (mehrere Stellen); `settings_dialog.py` main_layout | Workspace-Graph-Footer-Bereich, Settings unterer Abstand | Spezielle „nur unten“-Einrückung | drift |
| margins | 0,8,0,0 | `agent_tasks_workspace.py` betrieb/tasks Spalten | Agent-Tasks-Split | Nur top margin | drift |

*Weitere Dateien mit `setContentsMargins`:* siehe Repository-Grep; über **80** Vorkommen — obige Tabelle deckt die **dominanten Wertklassen** und riskantesten Sonderfälle ab.

---

## B) `setSpacing` / Listen-Spacing

| type | value | location | component | note | conflict_status |
|------|-------|----------|-----------|------|-----------------|
| spacing | 0 | Viele Host-Layouts, Splitter-Roots | Kein Zwischenraum zwischen Chrome und Content | Absicht für Dock/Tab | aligned |
| spacing | 2 | `navigation/sidebar.py` _list_widget; `project_list_panel.py` _list; `knowledge_sources_panel.py` | Nav- und Projektlisten | Sehr dicht | aligned |
| spacing | 4 | `breadcrumb/bar.py`; Runtime/Operations-Nav layout; `sidebar.py` inner | Breadcrumb, Domain-Navs | Feines Raster | aligned |
| spacing | 6 | `chat_details_panel.py` meta/invocation/actions; `markdown_widgets.py`; `workflow_run_panel.py` | Form-Metablocks | Nicht auf 4px-Raster | drift |
| spacing | 8 | Sehr häufig (Settings, Dashboard-Panels, Knowledge, …) | Standard-Zwischenraum | Passt zu `MARGIN_SM` | aligned |
| spacing | 10 | `project_stats_panel.py`; `chat_navigation_panel.py`; `doc_search_panel.py` root; `legacy/sidebar_widget.py` | Mischung aus 8 und 12 | **10px nicht** in `layout_constants` | drift |
| spacing | 12 | Inspektoren, Chat-Details content, viele Form-Rows | Zweit-häufigster Wert | Entspricht `WIDGET_SPACING` / `spacing_md` | aligned |
| spacing | 14 | `settings_dialog.py` form | QFormLayout-Zeilendistanz | Einzigartig im Sample | drift |
| spacing | 16 | CC-Workspaces, Introspection, Conversation content, Dashboard grid | „Section gap“ | Nahe `CARD_SPACING` aber nicht identisch überall | split |
| spacing | 20 | `settings_dialog.py` layout; `project_overview_panel.py`; `command_center_view.py` content | Dialog-Sektionen, Overview | Über `SECTION_SPACING` (24) verstreut | drift |
| spacing | 24 | `workspace_graph.py` content_layout; `dashboard_screen.py` layout | Workspace-Graph, Dashboard | Entspricht `SECTION_SPACING` / `SCREEN_SPACING` | aligned |

---

## C) `setFixed*` / `setMinimum*` / `setMaximum*` (Auswahl)

| type | value | location | component | note | conflict_status |
|------|-------|----------|-----------|------|-----------------|
| min_width | 1000 | `main_workbench.py`, `shell/main_window.py` | Fenster-Minimum | Einheitlich Shell/Workbench | aligned |
| min_width | 1200 | `conversation_view.py` message_container **+** max_width 1200 | Chat-Spalte | Erzwingt horizontales Scrollen auf <1200px Fenster — schwerwiegendes UX-Risiko | drift |
| min_width | 1000 | `chat_composer_widget.py` container | Composer (fixe Breite) | Hardcoded Layout-Breite | drift |
| min_height | 48 | `input_panel.py` prompt + send buttons | Chat-Eingabe | Über typische 32px-Control-Höhe | qss_python |
| min/max width | 180–220 | `operations_nav.py`, `runtime_debug_nav.py`, `control_center_nav.py`, `qa_governance_nav.py` | Domain-Sidebars | Einheitliche Nav-Breitenklasse | aligned |
| min/max width | 260–340 | `chat_navigation_panel.py`, `prompt_list_panel.py`, `library_panel.py`, `knowledge_source_explorer_panel.py` | Chat/Prompt/Knowledge-Spalten | Zweite Sidebar-Klasse | split |
| min_width | 240 | `shell/layout_constants.py` NAV_SIDEBAR_WIDTH default; Explorer-Dock | Shell-Nav vs. Workbench Explorer | Workbench nutzt gleiche Konstante-Datei-**Namenskollision** möglich — `shell/layout_constants` vs `shared/layout_constants` | split |
| min_height | 200 | `shell/layout_constants.py` BOTTOM_PANEL_HEIGHT | Bottom dock | Global | aligned |
| min_width | 420 | `settings_dialog.py` | Settings | Dialog-Minimum | aligned |

---

## D) Splitter, Stretch, Spacing-Widgets

| type | value | location | component | note | conflict_status |
|------|-------|----------|-----------|------|-----------------|
| QSplitter | Horizontal/Vertical | `workflow_workspace.py`, `prompt_studio_workspace.py`, `settings_workspace.py`, `markdown_demo_panel.py`, `releases_panel.py`, … | Multi-Pane Workspaces | Domänen-spezifische Größen — keine globale `setSizes`-Policy sichtbar | split |
| addStretch | 1 | Häufig in Header-Zeilen, Paletten, Dashboard | Drückt Aktionen nach rechts/unten | Idiomatisch Qt | aligned |
| addSpacing | 12 | `source_details_panel.py` | Vertikaler Abstand vor Aktionen | Einzelwert | drift |

---

## E) QSS (`app/gui/themes/base/*.qss`) — Padding / Margin / Min-Höhe

| type | value | location | component | note | conflict_status |
|------|-------|----------|-----------|------|-----------------|
| padding | `spacing_md` × `spacing_lg` | `shell.qss` #topBar; `base.qss` QPushButton, QLineEdit | TopBar, Standard-Buttons | Konsistent mit Token | aligned |
| padding | 6px 12px | `shell.qss` #projectSwitcherButton | Project Switcher | Entspricht kompakt-Preset, nicht als `{{token}}` | qss_python |
| padding | 4px 8px | `shell.qss` #breadcrumbItem | Breadcrumbs | Micro-Padding | qss_python |
| padding | `panel_padding` (20px) | `base.qss` #basePanel; `shell.qss` bottom pane | Karten, Bottom-Tabs | Gleich `ThemeTokens.panel_padding` | aligned |
| min-height | 32px | `base.qss` QComboBox | Combos | Gleich `CONTROL_HEIGHT` in `shared/layout_constants` | aligned |
| min-height | 26px / 28px / 32px | `workbench.qss` Explorer / Node-Library / Palette | Workbench-Listen | Drei Stufen | drift |
| margin | 2px / 4px | diverse QSS | Tabs, Scrollbar | Feintuning | qss_python |

---

## F) `QFormLayout` / Form-Ausrichtung

| type | value | location | component | note | conflict_status |
|------|-------|----------|-----------|------|-----------------|
| QFormLayout | (default alignment) | `settings_dialog.py`, `ai_models_settings_panel.py`, `data_settings_panel.py`, `advanced_settings_panel.py`, `projects_workspace.py`, `workflow_create_dialog.py`, `agent_form_widgets.py`, … | Settings + Operations-Dialoge | Keine durchgängige `setLabelAlignment`/`setHorizontalSpacing`-Policy im Sample | drift |

---

## G) Zentrale Konstanten-Module (Referenz)

| type | value | location | component | note | conflict_status |
|------|-------|----------|-----------|------|-----------------|
| const | PANEL_PADDING=20, WIDGET_SPACING=12, … | `app/gui/shared/layout_constants.py` | `apply_panel_layout`, … | Sollte mit `app/gui/theme/design_metrics.py` zusammenlaufen | split |
| const | NAV_SIDEBAR_WIDTH=240, INSPECTOR_WIDTH=280, … | `app/gui/shell/layout_constants.py` | `docking_config`, Shell, Workbench-Docks | Separater Pfad von `shared/layout_constants` | split |

---

*Nächste Auswertung:* [COMPONENT_DENSITY_ANALYSIS.md](./COMPONENT_DENSITY_ANALYSIS.md), [SIZE_RHYTHM_AUDIT.md](./SIZE_RHYTHM_AUDIT.md).
