# UX Stabilization Plan – Implementation Log

**Date:** 2026-03-16  
**Status:** Phase 1 & 2 complete

---

## Phase 1 — Critical Architecture Fixes (D24, D9)

### Fixes Applied

| Defect | Fix | Root Cause |
|--------|-----|------------|
| **D24** | WorkspaceHost calls `prepare_for_setup()` and passes `content_token` to screens | Area switch did not use token; async/delayed setup_inspector could complete out of order |
| **D9** | All screens and workspace widgets accept `content_token: int \| None = None` and pass to `set_content()` | Control Center, QA, Runtime screens did not propagate token to workspace widgets |

### Files Modified

**WorkspaceHost:**
- `app/gui/workspace/workspace_host.py` – `_on_current_changed` calls `prepare_for_setup()`, passes `content_token` to `setup_inspector`

**Screens:**
- `app/gui/domains/operations/operations_screen.py`
- `app/gui/domains/control_center/control_center_screen.py`
- `app/gui/domains/qa_governance/qa_governance_screen.py`
- `app/gui/domains/runtime_debug/runtime_debug_screen.py`
- `app/gui/domains/settings/settings_screen.py`
- `app/ui/settings/settings_workspace.py`

**Control Center workspaces:**
- `app/gui/domains/control_center/workspaces/base_management_workspace.py`
- `app/gui/domains/control_center/workspaces/models_workspace.py`
- `app/gui/domains/control_center/workspaces/providers_workspace.py`
- `app/gui/domains/control_center/workspaces/agents_workspace.py`
- `app/gui/domains/control_center/workspaces/tools_workspace.py`
- `app/gui/domains/control_center/workspaces/data_stores_workspace.py`

**QA workspaces:**
- `app/gui/domains/qa_governance/workspaces/base_analysis_workspace.py`
- `app/gui/domains/qa_governance/workspaces/test_inventory_workspace.py`
- `app/gui/domains/qa_governance/workspaces/coverage_map_workspace.py`
- `app/gui/domains/qa_governance/workspaces/incidents_workspace.py`
- `app/gui/domains/qa_governance/workspaces/replay_lab_workspace.py`
- `app/gui/domains/qa_governance/workspaces/gap_analysis_workspace.py`

**Runtime workspaces:**
- `app/gui/domains/runtime_debug/workspaces/base_monitoring_workspace.py`
- `app/gui/domains/runtime_debug/workspaces/eventbus_workspace.py`
- `app/gui/domains/runtime_debug/workspaces/logs_workspace.py`
- `app/gui/domains/runtime_debug/workspaces/metrics_workspace.py`
- `app/gui/domains/runtime_debug/workspaces/llm_calls_workspace.py`
- `app/gui/domains/runtime_debug/workspaces/agent_activity_workspace.py`
- `app/gui/domains/runtime_debug/workspaces/system_graph_workspace.py`

**Settings workspaces:**
- `app/gui/domains/settings/workspaces/base_settings_workspace.py`
- `app/gui/domains/settings/workspaces/appearance_workspace.py`
- `app/gui/domains/settings/workspaces/advanced_workspace.py`
- `app/gui/domains/settings/workspaces/system_workspace.py`
- `app/gui/domains/settings/workspaces/agents_workspace.py`
- `app/gui/domains/settings/workspaces/models_workspace.py`

### Verification

- `tests/behavior/ux_behavior_simulation.py` – 7 passed
- `tests/behavior/ux_regression_tests.py` – 5 passed
- **Total:** 12 tests passed

### Remaining Defects (Phase 1)

None. D24 and D9 resolved.

---

## Phase 2 — Navigation Completeness (D12, D14, D15)

### Fixes Applied

| Defect | Fix | Root Cause |
|--------|-----|------------|
| **D12** | Added `cc_agents` (Agents) to SYSTEM section in sidebar | Sidebar SYSTEM missing Agents entry |
| **D14** | Added `rd_system_graph` (System Graph) to OBSERVABILITY section | Sidebar OBSERVABILITY missing System Graph |
| **D15** | Added Command Palette commands for Knowledge, Prompt Studio, Agent Tasks, Control Center sub-workspaces, System Graph | Command Palette only had area-level nav |

### Files Modified

- `app/gui/navigation/sidebar_config.py` – D12, D14
- `app/gui/commands/bootstrap.py` – D15

### New Command Palette Commands

- `nav.knowledge` – Open Knowledge
- `nav.prompt_studio` – Open Prompt Studio
- `nav.agent_tasks` – Open Agent Tasks
- `nav.cc_models` – Open Models
- `nav.cc_providers` – Open Providers
- `nav.cc_agents` – Open Agents
- `nav.cc_tools` – Open Tools
- `nav.cc_data_stores` – Open Data Stores
- `nav.rd_system_graph` – Open System Graph

### Verification

- All 12 UX behavior/regression tests pass
- Manual: Sidebar shows Agents in SYSTEM, System Graph in OBSERVABILITY
- Manual: Command Palette lists new commands

### Remaining Defects (Phase 2)

None. D12, D14, D15 resolved.

---

## Verification Checklist (Post Phase 1 & 2)

- [x] Workspace switching – no crash
- [x] Inspector updates – token prevents stale content
- [x] Project switching – unchanged
- [x] Command palette navigation – new commands reach all workspaces
- [x] Sidebar navigation – Agents, System Graph visible

---

---

## Phase 3 — Inspector State (D27)

### Fixes Applied

| Defect | Fix |
|--------|-----|
| **D27** | Agents Inspector bound to table selection; AgentRegistryPanel emits `agent_selected`; AgentsWorkspace updates Inspector on row selection |

### Files Modified

- `app/gui/domains/control_center/panels/agents_panels.py` – `agent_selected` signal, `_on_selection_changed`
- `app/gui/domains/control_center/workspaces/agents_workspace.py` – `_refresh_inspector`, `_on_agent_selected`, connect to panel

---

## Phase 4 — UX Consistency (D37, D7, D21, D26)

### Fixes Applied

| Defect | Fix |
|--------|-----|
| **D37** | Knowledge source list items: context menu (Löschen, Neu indexieren) |
| **D7** | Breadcrumb WORKSPACE_INFO: "Project Overview" → "Projekte", "Agents" → "Agent Tasks" |
| **D21** | "Active Project" → "Aktives Projekt" |
| **D26** | "Demo-Daten" label on Agents, Tools, Data Stores panels |

### Files Modified

- `app/gui/domains/operations/knowledge/panels/source_list_item.py`
- `app/gui/breadcrumbs/manager.py`
- `app/gui/domains/control_center/panels/agents_panels.py`, `tools_panels.py`, `data_stores_panels.py`

---

## Phase 5 — Theme Cleanup (D34, D35, D36, D23)

### Fixes Applied

| Defect | Fix |
|--------|-----|
| **D35, D23** | Removed inline `setStyleSheet` from Control Center, QA workspace hosts – use shell.qss tokens |
| **D36** | Removed inline `_sidebar_stylesheet()` from sidebar – use shell.qss tokens |
| **D34** | Workspace hosts and sidebar now use theme tokens via global stylesheet |

### Files Modified

- `app/gui/domains/control_center/control_center_screen.py`
- `app/gui/domains/qa_governance/qa_governance_screen.py`
- `app/gui/domains/runtime_debug/runtime_debug_screen.py`
- `app/gui/navigation/sidebar.py`
- `app/gui/themes/base/shell.qss` – added #navSectionHeader, #navItemList token-based rules

---

## Phase 6 — Additional Tests

### Tests Added

- `test_command_palette_navigation` – nav.knowledge, nav.prompt_studio, nav.agent_tasks, nav.cc_agents, nav.rd_system_graph
- `test_area_switch_inspector_no_stale` – rapid Operations → Control Center → Settings → QA → Runtime switching with InspectorHost

### Files Modified

- `tests/behavior/ux_behavior_simulation.py`

---

---

## Phase 7 — Language Consistency + Test Fix (D28–D33, D20)

### Fixes Applied

| Defect | Fix |
|--------|-----|
| **test_project_switch_chat_restoration** | Call `set_project_service(None)` before/after infra so ProjectService uses correct DB |
| **D29** | "Enter your note text..." → "Notiztext eingeben..." |
| **D28** | Agent editor panel: placeholders and labels unified to German |
| **D30** | Advanced category/workspace: titles to German |
| **D32** | Dock title "Inspector" → "Inspektor" |
| **D33** | Bottom Panel tabs: "Metrics" → "Metriken", "Agent Activity" → "Agent-Aktivität", "LLM Trace" → "LLM-Trace" |
| **D20** | Command Palette: all titles to German ("Chat öffnen", "Knowledge öffnen", etc.) |

### Files Modified

- `tests/behavior/ux_behavior_simulation.py`
- `app/ui/knowledge/source_list_panel.py`
- `app/ui/agents/agent_editor_panel.py`
- `app/gui/domains/settings/workspaces/advanced_workspace.py`
- `app/ui/settings/categories/advanced_category.py`
- `app/gui/shell/docking_config.py`
- `app/gui/monitors/bottom_panel_host.py`
- `app/gui/commands/bootstrap.py`

---

## Phase 8 — Tab Order + Inspector Dock (D38, D39)

### Fixes Applied

| Defect | Fix |
|--------|-----|
| **D38** | Command Palette: explicit `setTabOrder(search, list)`, `StrongFocus` on search and list |
| **D39** | Skip `setup_inspector` when Inspector not visible; on dock `visibilityChanged` → `refresh_inspector_for_current()` |

### Files Modified

- `app/gui/commands/palette.py` – setTabOrder, StrongFocus
- `app/gui/workspace/workspace_host.py` – isVisible() check, `refresh_inspector_for_current()`
- `app/gui/shell/main_window.py` – `_inspector_dock`, `visibilityChanged` → refresh

---

## Remaining Defects

None. All planned UX stabilization items addressed.
