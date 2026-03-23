# GUI Feature Coverage Review (Phase 1)

**Legende Status:** **A** vollständig GUI-verfügbar · **B** teilweise · **C** nur indirekt/versteckt · **D** Backend/CLI · **E** dokumentiert/erwartet, GUI nicht oder nur anderswo  

**Standard-Produktpfad:** `main.py` / `python -m app` → `run_gui_shell.py` → `ShellMainWindow` (`app/gui/shell/main_window.py`).

---

## Kernprodukt & Operations

| Feature / Modul | Soll-Herkunft | GUI-Einstieg | Status | Bewertung | Lücke / Problem | Priorität |
|-----------------|---------------|--------------|--------|-----------|-----------------|-----------|
| Chat (Sessions, Senden, Streaming) | README, `docs/FEATURES/*` | Sidebar **WORKSPACE → Chat**, Command Palette `nav.chat` | **A** | Produktkern unter `operations/chat/` | — | — |
| Projekte (CRUD, aktives Projekt) | README | **WORKSPACE → Projekte**, TopBar Project Switcher | **A** | `ProjectsWorkspace`, Dialoge unter `operations/projects/` | — | — |
| Knowledge / RAG | README, `help/operations/knowledge_overview.md` | **WORKSPACE → Knowledge** | **B** | Hauptflows vorhanden; Index-/Retrieval-Teilpanels mit Platzhalter-Texten | `index_overview_panel.py`, `retrieval_status_panel.py` (laut `docs/PLACEHOLDER_INVENTORY.md`) | Mittel |
| Prompt Studio | README | **WORKSPACE → Prompt Studio** | **B** | Editor/Listen produktiv; Vorschau-Panel stub | `preview_panel.py` „(Platzhalter)“ | Mittel |
| Workflows (DAG, Runs) | README | **WORKSPACE → Workflows** | **A** | `workflow_workspace.py`, Canvas, Run-Historie (Architektur laut Code) | ComfyUI/Media-Pipeline-Schritte: Backend-Platzhalter-Executors (`app/pipelines/executors/placeholder_executors.py`) | Mittel–Hoch (wenn Media-Workflows versprochen) |
| Deployment (Releases, Rollouts) | README | **WORKSPACE → Deployment** | **A** | `DeploymentWorkspace`, Panels/Dialoge | Kein „automatisches externes Deployment“ (README) — Erwartung klären | Niedrig |
| Betrieb (Audit, Incidents, Checks) | README, Nav „Betrieb“ | **WORKSPACE → Betrieb** | **A** | `AuditIncidentsWorkspace` | Semantische Nähe zu QA-„Incidents“ — siehe Phase 3 | Mittel |
| Agent Tasks | README | **WORKSPACE → Agent Tasks** | **B** | Registry/Flows; Status/Queue-Platzhalter | `status_panel.py`, `queue_panel.py` | Mittel |

---

## Control Center (SYSTEM)

| Feature / Modul | Soll-Herkunft | GUI-Einstieg | Status | Bewertung | Lücke / Problem | Priorität |
|-----------------|---------------|--------------|--------|-----------|-----------------|-----------|
| Models | Nav, README | **SYSTEM → Models** | **A** | `ModelsWorkspace` | — | — |
| Providers | Nav | **SYSTEM → Providers** | **A** | `ProvidersWorkspace` | — | — |
| Agents (Profile, CRUD) | README, Help | **SYSTEM → Agents** | **A** | `AgentManagerPanel` in `agents_workspace.py` (nicht Demo-`agents_panels.py`) | Tote Demo-Datei `agents_panels.py` verwirrt Leser von alter Doku | Mittel (Wartung) |
| Tools (Übersicht) | README (Live-Snapshot) | **SYSTEM → Tools** | **A** | `ToolRegistryPanel.refresh()` → `build_tool_snapshot_rows()` | Keine Plugin-Registry — README korrekt; Erwartung „externe Tools“ sonst falsch | Niedrig |
| Data Stores | README (Live-Snapshot) | **SYSTEM → Data Stores** | **A** | `build_data_store_rows()`, Health-Summary | — | — |

---

## Kommandozentrale vs. QA-Depth

| Feature / Modul | Soll-Herkunft | GUI-Einstieg | Status | Bewertung | Lücke / Problem | Priorität |
|-----------------|---------------|--------------|--------|-----------|-----------------|-----------|
| Dashboard (4 Karten) | Shell-Start | **PROJECT → Systemübersicht** (`DashboardScreen`) | **B** | `SystemStatusPanel` live (Ollama, DB); `QAStatusPanel`/`IncidentsPanel` via `QADashboardAdapter`; `ActiveWorkPanel` bewusst ohne Live-Aggregation | Kein eingebetteter **vollständiger** Stack wie `CommandCenterView` (QA-Drilldown, Subsystem-Detail, Ops-Views) | **Hoch** |
| CommandCenterView (QA-Stack, Drilldowns) | `COMMAND_CENTER_ARCHITECTURE.md`, Tests | **Nicht** im Standard-Shell; nur Legacy `app/main.py` → `CommandCenterView` | **C** / **D** (für Standardnutzer effektiv **fehlend**) | Implementiert und getestet (`tests/ui/test_command_center_dashboard.py`), aber **abgekoppelt** vom produktiven Shell-Einstieg | Produktversprechen „eine Kommandozentrale“ vs. zwei Welten (Shell-Dashboard vs. Legacy-Stack) | **Hoch** |
| QA Test Inventory | Nav | **QUALITY → Test Inventory** | **A** | `TestInventoryWorkspace` | — | — |
| Coverage / Gaps / Incidents / Replay | Nav | **QUALITY → …** | **A**–**B** | Workspaces registriert; Replay mit Service (`replay_lab_workspace.py`) | Tiefe vs. CLI-Repro (`app/cli/`) — siehe Phase 2 | Mittel |
| QA Cockpit / QA Observability | Nav **OBSERVABILITY** | Runtime → QA Cockpit / QA Observability | **B** | Parallele QA-Oberflächen zur **QUALITY**-Sektion | Doppelte Einstiege, unklare Rollentrennung für Nutzer | Mittel–Hoch |

---

## Runtime / Debug / Devtools

| Feature / Modul | Soll-Herkunft | GUI-Einstieg | Status | Bewertung | Lücke / Problem | Priorität |
|-----------------|---------------|--------------|--------|-----------|-----------------|-----------|
| Introspection | Nav | **OBSERVABILITY → Introspection** | **A** | Live-Diagnostik | — | — |
| EventBus / Logs / Metrics / LLM Calls / Agent Activity / System Graph | Nav | jeweilige Einträge | **B** | Präsent; Tiefe ohne Session nicht verifiziert | Monitoring-Erwartung vs. Implementierungsdetail | Niedrig–Mittel |
| Markdown Demo | `runtime_debug_screen.py` | Runtime-Subnav **Markdown Demo** | **B** | Absichtlich QA/Dev | Nicht in `navigation_registry.py` Sidebar-Liste — nur Subnav + Palette `nav.rd_markdown_demo` | Niedrig (Kennzeichnung) |
| Theme Visualizer | `docs/devtools/THEME_VISUALIZER.md` | Runtime-Subnav (wenn Env) | **C** | `is_theme_visualizer_available()` | Kein Sidebar-Eintrag in zentraler Registry | Niedrig (Dev-only) |

---

## Settings

| Feature / Modul | Soll-Herkunft | GUI-Einstieg | Status | Bewertung | Lücke / Problem | Priorität |
|-----------------|---------------|--------------|--------|-----------|-----------------|-----------|
| Application, Appearance, AI/Models, Data, Privacy, Advanced | Nav **SETTINGS** | jeweilige Kategorie | **A** | `settings_workspace.py` + Kategorien | — | — |
| Project / Workspace (Settings) | Nav | **SETTINGS → Project / Workspace** | **B** | Sichtbare Kategorien | `ProjectCategory` / `WorkspaceCategory` Empty States („zukünftige Version“) laut `PLACEHOLDER_INVENTORY.md` | Mittel |
| Settings-Dialog (modal) | Legacy/alt | `settings_dialog.py` | **C** | existiert | Nicht fokussierter Shell-Hauptpfad | Niedrig |

---

## Hilfe, Suche, Import/Export

| Feature / Modul | Soll-Herkunft | GUI-Einstieg | Status | Bewertung | Lücke / Problem | Priorität |
|-----------------|---------------|--------------|--------|-----------|-----------------|-----------|
| Kontext-Hilfe (F1) | TopBar | **Hilfe**-Aktion | **A** | `HelpWindow`, Topics, Guided Tours | — | — |
| Semantische Doku-Suche | Help | Tab „Semantische Doku-Suche“ in `HelpWindow` | **B** | `DocSearchPanel` + Service | Abhängig von Index/Chroma — Fehlerpfad für Nutzer unklar ohne Live-Test | Mittel |
| Slash-Commands / Chat-Hilfe | Chat | im Chat-Workspace | **A** (implizit) | nicht jede Zeile verifiziert | — | — |

---

## Recovery / Admin / Governance

| Thema | GUI-Einstieg | Status | Anmerkung |
|-------|--------------|--------|-----------|
| Fehlgeschlagene Workflow-Läufe | Betrieb + QA-Bereiche | **B** | Mehrere Einstiege |
| Reindex / Rescan / Cleanup RAG | Vermutlich Settings + Knowledge | **B**–**C** | Nicht jede Operation als eigener sichtbarer Wizard verifiziert — gezielt im Code nachziehen bei Umsetzungsplan |
| Vollständiger Test-/Coverage-Lauf | — | **D** | `pytest`/CI |

---

*Ende GUI_FEATURE_COVERAGE_REVIEW.md*
