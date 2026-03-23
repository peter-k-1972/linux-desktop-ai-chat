# GUI

## Verwandte Themen

- [Chat](../chat/README.md) · [Settings](../settings/README.md) · [Provider](../providers/README.md) · [RAG](../rag/README.md)  
- [Architektur – Schichten](../../../docs/ARCHITECTURE.md#1-schichtenmodell) · [Systemkarte](../../../docs/00_map_of_the_system.md)

## 1. Fachsicht

Die **GUI** ist die **PySide6-Shell** der Anwendung: Hauptfenster, Bereichsumschaltung, Workspaces je Screen, **Navigation** (Sidebar, Breadcrumbs, Command Palette), **Inspector** (rechts), **Monitors** (unten) und domänenspezifische **Panels**. Zentraler Code unter **`app/gui/`** (nicht `app/ui/` — dieses Verzeichnis existiert im aktuellen Tree nicht, vgl. `docs/DOC_GAP_ANALYSIS.md`).

## 2. Rollenmatrix

| Rolle | Nutzung |
|-------|---------|
| **Fachanwender** | Bedienung aller Screens und Workspaces. |
| **Admin** | Kein separates Admin-UI; Konfiguration über Settings. |
| **Entwickler** | `app/gui/bootstrap.py`, Domains, WorkspaceHost, Inspector, Tests `tests/ui/`. |
| **Business** | Produktoberfläche „Linux Desktop Chat“. |

## 3. Prozesssicht

```
ShellMainWindow (app/gui/shell/)
        │
        ├── NavigationSidebar → NavArea wechseln
        │
        ├── WorkspaceHost → Screen aus ScreenRegistry
        │
        ├── InspectorHost (rechts)
        │
        └── Monitors (unten, app/gui/monitors/)
```

**Screen-Registrierung** beim Start: `register_all_screens()` in `app/gui/bootstrap.py` — mappt jede `NavArea`-ID auf genau eine Screen-Klasse:

| `NavArea` (Konstante) | Screen-Klasse | Anzeigename (Registry-Titel) |
|----------------------|---------------|------------------------------|
| `command_center` | `DashboardScreen` | Kommandozentrale |
| `project_hub` | `ProjectHubScreen` | Project Hub |
| `operations` | `OperationsScreen` | Operations |
| `control_center` | `ControlCenterScreen` | Control Center |
| `qa_governance` | `QAGovernanceScreen` | QA & Governance |
| `runtime_debug` | `RuntimeDebugScreen` | Runtime / Debug |
| `settings` | `SettingsScreen` | Settings |

Definition der Konstanten: `app/core/navigation/nav_areas.py`.

## 4. Interaktionssicht

### 4.1 Navigation

- **Sidebar / Bereiche:** `app/gui/navigation/` (`NavigationSidebar`, `nav_areas`).
- **Command Palette:** `app/gui/navigation/command_palette.py` — Befehle aus `app/gui/commands/` (`CommandRegistry`).
- **Breadcrumbs:** `app/gui/breadcrumbs/` (Paket; von Screens bei Workspace-Wechsel angesprochen).

### 4.2 Workspaces (eingebettete Hauptfläche je Screen)

**Operations** (`operations_screen.py`) — IDs:

| Workspace-ID | Klasse |
|--------------|--------|
| `operations_projects` | `ProjectsWorkspace` |
| `operations_chat` | `ChatWorkspace` |
| `operations_agent_tasks` | `AgentTasksWorkspace` |
| `operations_knowledge` | `KnowledgeWorkspace` |
| `operations_prompt_studio` | `PromptStudioWorkspace` |

Standard nach Start des Stacks: `operations_projects` (`set_current` in `_setup_ui`).

**Control Center** (`control_center_screen.py`):

| Workspace-ID | Klasse |
|--------------|--------|
| `cc_models` | `ModelsWorkspace` |
| `cc_providers` | `ProvidersWorkspace` |
| `cc_agents` | `AgentsWorkspace` |
| `cc_tools` | `ToolsWorkspace` |
| `cc_data_stores` | `DataStoresWorkspace` |

Standard: `cc_models`.

**QA & Governance** (`qa_governance_screen.py`):

| Workspace-ID | Klasse |
|--------------|--------|
| `qa_test_inventory` | `TestInventoryWorkspace` |
| `qa_coverage_map` | `CoverageMapWorkspace` |
| `qa_gap_analysis` | `GapAnalysisWorkspace` |
| `qa_incidents` | `IncidentsWorkspace` |
| `qa_replay_lab` | `ReplayLabWorkspace` |

Standard: `qa_test_inventory`.

**Runtime / Debug** (`runtime_debug_screen.py`):

| Workspace-ID | Klasse |
|--------------|--------|
| `rd_introspection` | `IntrospectionWorkspace` |
| `rd_qa_cockpit` | `QACockpitWorkspace` |
| `rd_qa_observability` | `QAObservabilityWorkspace` |
| `rd_eventbus` | `EventBusWorkspace` |
| `rd_logs` | `LogsWorkspace` |
| `rd_metrics` | `MetricsWorkspace` |
| `rd_llm_calls` | `LLMCallsWorkspace` |
| `rd_agent_activity` | `AgentActivityWorkspace` |
| `rd_system_graph` | `SystemGraphWorkspace` |

Standard: `rd_introspection`.

**Settings** — acht Kategorien über `SettingsWorkspace` (siehe Modul **settings**), nicht als `QStackedWidget`-Liste in einem separaten `*Screen` wie oben, sondern über `settings_workspace.py` + `SettingsNavigation`.

### 4.3 Panels

**Panels** sind komponentenweise UI-Teile innerhalb von Workspaces (z. B. unter `app/gui/domains/operations/chat/panels/` — `ChatConversationPanel`, `ChatInputPanel`, `ChatContextBar`, `chat_navigation_panel`, …). Es gibt keine einzelne zentrale „Panel-Registry“-Datei; die Einbindung erfolgt über die jeweilige `*Workspace`-Klasse.

### 4.4 Inspector & Backends

- **Inspector:** `app/gui/inspector/` — z. B. `ChatContextInspector` für Chat-Kontext.
- **ChatBackend / KnowledgeBackend:** `app/gui/chat_backend.py`, `app/gui/knowledge_backend.py` — Anbindung an Services.

## 5. Fehler- / Eskalationssicht

| Problem | Ursache |
|---------|---------|
| Screen leer nach Navigation | Factory fehlt in `register_all_screens` oder Exception in Screen-`__init__`. |
| Inspector zeigt alten Inhalt | `prepare_for_setup` / `content_token` in `OperationsScreen`/`RuntimeDebugScreen` (Kommentar D9). |
| Falscher Workspace aktiv | `show_workspace` nicht aufgerufen; Breadcrumb-Drift. |

## 6. Wissenssicht

| Begriff | Ort |
|---------|-----|
| `WorkspaceHost` | `app/gui/workspace/workspace_host.py` |
| `ScreenRegistry` | `app/gui/workspace/screen_registry.py` |
| `register_all_screens` | `app/gui/bootstrap.py` |
| `NavArea` | `app/core/navigation/nav_areas.py` |
| `BaseScreen` | `app/gui/shared/base_screen.py` |

## 7. Perspektivwechsel

| Perspektive | Fokus |
|-------------|--------|
| **User** | Sidebar-Struktur wie in `docs/00_map_of_the_system.md` §4. |
| **Admin** | — |
| **Dev** | Keine Suche unter `app/ui/`; GUI-Code nur unter `app/gui/`. |
