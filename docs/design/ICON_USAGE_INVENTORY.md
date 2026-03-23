# Icon Usage Inventory

**Projekt:** Linux Desktop Chat / Obsidian Core  
**Stand:** 2026-03-22 (aktualisiert: Cutover-Bindung) — Kanon: `resources/icons/` + `IconManager` / `icon_registry.get_icon*`.

**Legende:** *semantic_role* = intendierte Bedeutung im UI. *Registry* = ID in `IconRegistry` / `IconManager.get(id)`.

---

## 1. Zentrales Registry-Set (Shell & Domains)

| icon_name (Registry) | file (primär) | usage_locations | semantic_role |
|------------------------|---------------|-----------------|---------------|
| dashboard | `resources/icons/navigation/dashboard.svg` | `nav_mapping` (Kommandozentrale), `bootstrap.py`, `palette_loader` | Hauptbereich Dashboard |
| chat | `…/navigation/chat.svg` | Nav Operations, OPS workspaces, `project_stats_panel`, `project_quick_actions`, `palette_loader` | Chat / Operations |
| control | `…/navigation/control.svg` | Nav Control Center, `system_status_panel` | Steuerung / Control Center |
| shield | `…/navigation/shield.svg` | Nav QA & Governance, `palette_loader` | Governance (Runtime-QA → `qa_runtime`) |
| qa_runtime | `…/monitoring/qa_runtime.svg` | `rd_qa_cockpit`, `rd_qa_observability` | Runtime-QA / Observability |
| activity | `…/navigation/activity.svg` | Nav Runtime/Debug, `top_bar` Status-Aktion | Aktivität / Live |
| gear | `…/navigation/gear.svg` | Nav Settings, `bootstrap` | Einstellungen |
| models | `…/objects/models.svg` | CC, Settings, `palette_loader` | ML-Modelle |
| providers | `…/objects/providers.svg` | CC, `palette_loader` | Anbieter |
| agents | `…/objects/agents.svg` | CC, OPS agent tasks, Settings, `palette_loader`, `project_quick_actions` | Agenten |
| tools | `…/objects/tools.svg` | CC, `palette_loader` | Werkzeuge |
| data_stores | `…/objects/data_stores.svg` | CC Data Stores, `project_stats` „Datei-Links“ | Datenspeicher (Deployment → **deploy**) |
| knowledge | `…/objects/knowledge.svg` | OPS, `palette`, `source_details`, `project_quick_actions`, `project_stats` | Wissensbasis |
| prompt_studio | `…/objects/prompt_studio.svg` | OPS, `palette`, `project_quick_actions`, `project_stats` | Prompt-Editor |
| projects | `…/objects/projects.svg` | OPS projects, `bootstrap`, `palette` | Projekte |
| test_inventory | `…/objects/test_inventory.svg` | QA workspace, `palette` | Testbestand |
| coverage_map | `…/objects/coverage_map.svg` | QA | Coverage |
| gap_analysis | `…/objects/gap_analysis.svg` | QA | Lückenanalyse |
| incidents | `…/objects/incidents.svg` | QA, OPS audit | Vorfälle |
| replay_lab | `…/objects/replay_lab.svg` | QA | Replay |
| appearance | `…/objects/appearance.svg` | Settings, Theme Visualizer, `bootstrap` dev | Erscheinungsbild |
| system | `…/objects/system.svg` | Settings system, RD introspection | System |
| advanced | `…/objects/advanced.svg` | Settings advanced | Erweitert |
| eventbus | `…/monitoring/eventbus.svg` | RD, `nav_mapping` | Event-Bus |
| logs | `…/monitoring/logs.svg` | RD logs, `bootstrap` | Protokolle (Markdown-Demo → **sparkles**) |
| sparkles | `…/ai/sparkles.svg` | `rd_markdown_demo` | Demo / Dekoration |
| metrics | `…/monitoring/metrics.svg` | RD | Metriken |
| llm_calls | `…/monitoring/llm_calls.svg` | RD | LLM-Aufrufe |
| agent_activity | `…/monitoring/agent_activity.svg` | RD | Agent-Aktivität |
| system_graph | `…/monitoring/system_graph.svg` | RD, OPS workflows, Workspace Map, `palette`, `project_quick_actions` | Graph / Workflows |
| add | `…/actions/add.svg` | Chat nav new, projects, Legacy „Neu“ | Hinzufügen |
| pin | `…/actions/pin.svg` | `chat_details_panel` Pin | Anheften |
| open | `…/actions/open.svg` | `source_details_panel` Öffnen | Datei/Quelle öffnen |
| link_out | `…/actions/link_out.svg` | Registry / Aktion `external_link` | Externer Link |
| remove | `…/actions/remove.svg` | knowledge source delete | Entfernen |
| edit | `…/actions/edit.svg` | chat rename, project edit | Bearbeiten |
| refresh | `…/actions/refresh.svg` | knowledge reindex, `bootstrap`, `palette` | Neu laden |
| search | `…/actions/search.svg` | TopBar Command Palette, Hilfe **früher** fälschlich, source open/chunks | Suche |
| filter | `…/actions/filter.svg` | (Registry; wenig direkt) | Filter |
| run | `…/actions/run.svg` | project activate | Ausführen |
| stop | `…/actions/stop.svg` | (Registry) | Stopp |
| save | `…/actions/save.svg` | Registry + assets fallback | Speichern |
| deploy | `…/actions/deploy.svg` | Registry; Mapping „deployment“ → deploy | Deploy / Release |
| help | `…/system/help.svg` | `top_bar` Hilfe | Hilfe |
| info | `…/system/info.svg` | Registry | Information |
| send | `…/system/send.svg` | `chat_composer_widget` (IconManager), Registry | Senden |
| success | `…/states/success.svg` | Status / Canvas (indirekt) | Erfolg |
| warning | `…/states/warning.svg` | Status | Warnung |
| error | `…/states/error.svg` | Status | Fehler |
| running | `…/states/running.svg` | Status | Laufend |
| idle | `…/states/idle.svg` | Status | Leerlauf |
| paused | `…/states/paused.svg` | Status | Pausiert |

**Ladereihenfolge:** `IconManager` liest zuerst `resources/icons/…` (via `icon_registry.get_resource_svg_path`), dann `assets/icons/svg/{category}/{file}` gemäß `IconRegistry.get_path`.

---

## 2. Legacy / Duplikat-Pfade

| icon_name | file | usage_locations | Stand Cutover |
|-----------|------|-----------------|---------------|
| QRC `:/icons/*` | `app/resources/icons/` | ~~`legacy/sidebar_widget`~~, ~~`project_chat_list_widget`~~ | **Ersetzt** durch `IconManager` + `IconRegistry` |
| Toolbar-Pfade | `settings.icons_path` + `*.svg` | ~~`app/main.py` `init_toolbar`~~ | **Ersetzt** durch `IconManager` |
| Flache Assets | `assets/icons/*.svg` | ggf. Altstarts, `settings.icons_path` | weiterhin möglich, **nicht** für neue UI; Composer nutzt keinen Pfad mehr für Send |

**Hinweis:** QRC-Modul kann für andere Ressourcen bestehen bleiben; dokumentierte Widgets laden UI-Icons nicht mehr per `:/icons/`.

**Duplikat-Ordner:** `assets/icons/actions/` und `assets/icons/svg/actions/` (gleiche Basenames); `runtime/` vs `svg/runtime/` — siehe Konfliktbericht.

---

## 3. Sonstige Symbolreferenzen

| Quelle | Typ | Hinweis |
|--------|-----|---------|
| `workspace_graph.py` | `IconManager.get(icon_name)` | Nutzt Registry-Namen aus Graph-Knoten |
| `runtime_debug_nav.py` | `IconManager.get(..., color_token=…)` | Workspace-IDs → Namen aus Mapping |
| `operations_nav.py`, `navigation/sidebar.py` (implizit) | Liste + Icons | `get_workspace_icon` / area icons |
| `empty_state_widget.py` | dynamisch | Registry-String aus Aufrufer |
| `canvas_tabs.py` | `QIcon` komponiert | Status-Badge auf Tab-Icon |

---

*Vollständige Dateiliste SVG im Repo: `glob **/*.svg` (91 Treffer inkl. Doku-Grafiken). Produkt-UI: obige Pfade + `docs/*.svg` ausschließen für reine App-Assets.*
