# GUI Governance Audit

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Kontext:** Erweitertes GUI-Governance-Testsystem

---

## 1. Übersicht

Audit der zentralen GUI-Wiring-Punkte: Screen Registry, Navigation, Commands, Bootstrap.

---

## 2. Screen Registry

### 2.1 Struktur

| Komponente | Pfad | Rolle |
|------------|------|-------|
| ScreenRegistry | `app/gui/workspace/screen_registry.py` | area_id → Factory, Title |
| Bootstrap | `app/gui/bootstrap.py` | Registriert alle Screens bei Start |
| WorkspaceHost | `app/gui/workspace/workspace_host.py` | Lädt Screens aus Registry, zeigt per area_id |

### 2.2 Bootstrap-Registrierung

| area_id | Screen-Klasse | Titel |
|---------|---------------|-------|
| command_center | DashboardScreen | Kommandozentrale |
| project_hub | ProjectHubScreen | Project Hub |
| operations | OperationsScreen | Operations |
| control_center | ControlCenterScreen | Control Center |
| qa_governance | QAGovernanceScreen | QA & Governance |
| runtime_debug | RuntimeDebugScreen | Runtime / Debug |
| settings | SettingsScreen | Settings |

### 2.3 NavArea-Konsistenz

- **NavArea** (`app/core/navigation/nav_areas.py`): COMMAND_CENTER, PROJECT_HUB, OPERATIONS, CONTROL_CENTER, QA_GOVERNANCE, RUNTIME_DEBUG, SETTINGS
- **Bootstrap** nutzt dieselben NavArea-Konstanten
- **NavArea.all_areas()** enthält kein PROJECT_HUB – **INVESTIGATE** (evtl. bewusst)

### 2.4 Klassifikation

| Thema | Status |
|-------|--------|
| Screen-IDs eindeutig | OK |
| Bootstrap referenziert nur gültige Screens | OK |
| Screen-Klassen importierbar | OK |
| NavArea.all_areas() vs. Bootstrap | INVESTIGATE |

---

## 3. Navigation Registry

### 3.1 Struktur

| Komponente | Pfad | Rolle |
|------------|------|-------|
| Navigation Registry | `app/core/navigation/navigation_registry.py` | Single Source of Truth für Nav-Einträge |
| NavEntry | area, workspace, title, icon | Ein Eintrag |
| Sidebar | `app/gui/navigation/sidebar.py` | Nutzt get_sidebar_sections() |
| SidebarConfig | `app/gui/navigation/sidebar_config.py` | Mappt Registry → NavSection |

### 3.2 NavEntry-Bereiche

- **PROJECT:** project_hub, command_center, operations_projects
- **WORKSPACE:** operations_chat, operations_knowledge, operations_prompt_studio, operations_agent_tasks
- **SYSTEM:** cc_models, cc_providers, cc_agents, cc_tools, cc_data_stores
- **OBSERVABILITY:** rd_introspection, rd_qa_cockpit, rd_qa_observability, rd_eventbus, rd_logs, rd_llm_calls, rd_agent_activity, rd_metrics, rd_system_graph
- **QUALITY:** qa_test_inventory, qa_coverage_map, qa_incidents, qa_replay_lab, qa_gap_analysis
- **SETTINGS:** settings_application, settings_appearance, settings_ai_models, settings_data, settings_privacy, settings_advanced, settings_project, settings_workspace

### 3.3 Navigation Targets vs. Screens

Workspace-IDs aus Registry müssen von den Domain-Screens unterstützt werden:

| Screen | Unterstützte workspace_ids |
|--------|---------------------------|
| OperationsScreen | operations_projects, operations_chat, operations_agent_tasks, operations_knowledge, operations_prompt_studio |
| ControlCenterScreen | cc_models, cc_providers, cc_agents, cc_tools, cc_data_stores |
| RuntimeDebugScreen | rd_introspection, rd_qa_cockpit, rd_qa_observability, rd_eventbus, rd_logs, rd_metrics, rd_llm_calls, rd_agent_activity, rd_system_graph |
| QAGovernanceScreen | qa_test_inventory, qa_coverage_map, qa_gap_analysis, qa_incidents, qa_replay_lab |
| SettingsScreen | settings_application, settings_appearance, settings_ai_models, settings_data, settings_privacy, settings_advanced, settings_project, settings_workspace |

### 3.4 Gefundene Probleme

| Thema | Klassifikation | Details |
|-------|----------------|---------|
| AGENT_ACTIVITY nicht importiert | FIX_NOW | navigation_registry.py nutzte AGENT_ACTIVITY, Import fehlte → **behoben** |
| Tote Targets | OK | Alle Registry-Einträge haben passende Screens |

---

## 4. Command Registry

### 4.1 Zwei Command-Registries

| Registry | Pfad | Nutzer | Populated by |
|----------|------|--------|--------------|
| **gui CommandRegistry** | `app/gui/commands/registry.py` | CommandPaletteDialog (nicht aktiv genutzt) | gui/commands/bootstrap.register_commands |
| **core CommandRegistry** | `app/core/command_registry.py` | CommandPalette (Ctrl+K) | palette_loader.load_all_palette_commands |

### 4.2 Aktive Command Palette

- **CommandPalette** (`app/gui/navigation/command_palette.py`) nutzt **core** CommandRegistry
- **palette_loader** lädt: load_area_commands, load_workspace_graph_command, load_feature_commands, load_help_commands, load_system_commands

### 4.3 Command-IDs (core, aus palette_loader)

- **nav.area.\*** (area-only)
- **feature.open.\*** (aus FEATURE_REGISTRY.md)
- **help.open**, **help.open.\***
- **cmd.rebuild_system_map**, **cmd.rebuild_trace_map**, **cmd.rebuild_feature_registry**, **cmd.reload_providers**, **cmd.run_qa_sweep**
- **nav.workspace_graph**

### 4.4 gui Commands (gui CommandRegistry)

- nav.dashboard, nav.projects, nav.chat, nav.knowledge, nav.prompt_studio, nav.agent_tasks
- nav.control_center, nav.cc_models, nav.cc_providers, nav.cc_agents, nav.cc_tools, nav.cc_data_stores
- nav.qa_governance, nav.runtime_debug, nav.rd_qa_cockpit, nav.rd_qa_observability, nav.rd_system_graph
- nav.settings
- system.help, system.help_context, system.switch_theme, system.reload_theme

**Hinweis:** Die gui CommandRegistry wird von **CommandPaletteDialog** genutzt, die Shell verwendet aber **CommandPalette** (core). → **INVESTIGATE**: Doppelte Registrierung, evtl. Legacy.

### 4.5 Klassifikation

| Thema | Status |
|-------|--------|
| core Command-IDs eindeutig | OK (skip bei Duplikat in palette_loader) |
| gui Command-IDs eindeutig | OK |
| Zwei Registries | INVESTIGATE |
| Command-Ziele auflösbar | OK (callbacks mit workspace_host) |

---

## 5. Bootstrap / Wiring

### 5.1 Ablauf (ShellMainWindow)

1. `register_all_screens()` → ScreenRegistry
2. `workspace_host.register_from_registry()` → Screens erstellen, in WorkspaceHost legen
3. `register_commands(workspace_host)` → gui CommandRegistry
4. `load_all_palette_commands(workspace_host)` → core CommandRegistry
5. `show_area(NavArea.COMMAND_CENTER)` → Initialer Screen

### 5.2 Abhängigkeiten

- Bootstrap → ScreenRegistry, NavArea, alle Domain-Screens
- Shell → Bootstrap, WorkspaceHost, Navigation, Commands, Breadcrumbs
- WorkspaceHost → ScreenRegistry

### 5.3 Klassifikation

| Thema | Status |
|-------|--------|
| Bootstrap-Reihenfolge | OK |
| Keine toten Screen-Referenzen | OK |
| Wiring konsistent | OK |

---

## 6. Breadcrumbs

- **BreadcrumbManager** nutzt `app.core.navigation.navigation_registry` (get_all_entries)
- **WORKSPACE_INFO** wird aus Registry gebaut
- Abhängig von navigation_registry → AGENT_ACTIVITY-Fix relevant

---

## 7. Zusammenfassung der Klassifikationen

| Klassifikation | Anzahl | Themen |
|----------------|--------|--------|
| OK | Mehrheit | Screen Registry, Navigation Targets, Bootstrap |
| FIX_NOW | 1 | AGENT_ACTIVITY Import (behoben) |
| GUARD_NEEDED | 4 | Screen-ID-Duplikate, Nav-Target-Existenz, Command-ID-Duplikate, Bootstrap-Screen-Konsistenz |
| INVESTIGATE | 2 | NavArea.all_areas vs. Bootstrap, Zwei Command-Registries |
| FOLLOW_UP | 0 | - |

---

## 8. Empfohlene Guards

1. **Screen Guards:** Keine doppelten area_ids in Bootstrap; alle registrierten Screens importierbar
2. **Navigation Guards:** Alle NavEntry.area in NavArea; alle workspace_ids von Screens unterstützt
3. **Command Guards:** Keine doppelten Command-IDs in core Registry (nach Load)
4. **Bootstrap Guards:** Bootstrap area_ids = NavArea-Konstanten; alle Screens instanziierbar
