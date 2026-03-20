# Agent UI Architecture Evaluation

**Date:** 2026-03-16  
**Scope:** `app/ui/agents/*` vs `app/gui/domains/control_center/*`  
**Role:** Software Architect

---

## 1. Features Implemented in UI (`app/ui/agents/*`)

### 1.1 Agent Manager (actively used)

| Module | Features |
|--------|----------|
| **agent_manager_panel** | Full HR-style agent management: list + profile, actions (New, Duplicate, Activate, Deactivate, Delete, Use in Chat). Uses `AgentService`, `AgentRegistry`. |
| **AgentManagerDialog** | Dialog wrapper for toolbar/menu. Emits `agent_selected_for_chat`. |
| **agent_list_panel** | Agent list with `set_agents()` (global) or project-scoped `_load_agents()`. Create Agent button. |
| **agent_list_item** | List item widget per agent. |
| **agent_profile_panel** | Profile detail: Avatar, read-only view, edit mode, Performance tab. Uses `AgentProfileForm`. |
| **agent_avatar_widget** | Avatar display/edit. |
| **agent_form_widgets** | `AgentProfileForm`, `AgentCapabilitiesEditor` – form fields for profile editing. |
| **agent_performance_tab** | Performance metrics tab. |

**Entry point:** `main.py` → toolbar → `open_agent_manager()` → `AgentManagerDialog`.

### 1.2 Agent Workspace (dead code – not instantiated)

| Module | Features |
|--------|----------|
| **agent_workspace** | Three-column layout: Nav + stacked content + Inspector. **Never instantiated** in app. |
| **agent_navigation_panel** | Left nav: Agent Library, Runs, Activity, Skills. Project context. |
| **agent_library_panel** | `AgentListPanel` + `AgentEditorPanel`. Project-scoped agents, Create Agent. |
| **agent_editor_panel** | Editor: Name, Model, Prompt, Knowledge Collections, Tools, Memory, Limits. Different from `AgentProfileForm`. |
| **agent_runs_panel** | Agent runs table from `DebugStore` (live polling). Agent, Status, Start, Duration, Result. |
| **agent_activity_panel** | Event stream from `DebugStore`. Model calls, tool calls, steps, errors. Filter by type. |
| **agent_skills_panel** | Tool enable/disable per agent. Agent selector combo, checkboxes for tools. |

**Entry point:** None. `AgentWorkspace` is exported from `__init__.py` but never imported or instantiated elsewhere.

---

## 2. Features Implemented in GUI (`app/gui/domains/control_center/*`)

| Module | Features |
|--------|----------|
| **control_center_screen** | Nav + stacked workspaces. Models, Providers, Agents, Tools, Data Stores. Inspector integration. |
| **control_center_nav** | Left navigation for workspaces. |
| **agents_workspace** | Agent tab in Control Center. Uses `AgentRegistryPanel` + `AgentSummaryPanel`. |
| **agents_panels** | `AgentRegistryPanel`: **Demo data** table (3 hardcoded rows). Selection → Inspector. `AgentSummaryPanel`: Static "Configuration Summary" (hardcoded values). |
| **base_management_workspace** | Base class for workspaces. `setup_inspector()`. |

**Entry point:** `bootstrap.py` → `ControlCenterScreen` → Nav Area `CONTROL_CENTER` (Command Center).

**Data:** No `AgentService` integration. All demo/placeholder data.

---

## 3. Overlap Analysis

| Aspect | UI | GUI |
|--------|----|-----|
| **Concept** | Agent management (HR-style) | Agent management (design/config view) |
| **Data source** | `AgentService`, `AgentRegistry` | Hardcoded demo data |
| **Layout** | List + Profile (splitter) | Table + Summary |
| **CRUD** | Full (create, update, delete, activate, duplicate) | None |
| **Inspector** | AgentWorkspace has `setup_inspector` (unused) | AgentsWorkspace has `setup_inspector` (used) |
| **Entry** | Main toolbar dialog | Control Center tab |

**Overlap:** Both present "agent management" but with different implementations. No shared components. GUI is a placeholder; UI has the real implementation.

---

## 4. Architecture Recommendation

### 4.1 Canonical Implementation

**Treat `app/ui/agents` Agent Manager flow as canonical** for agent CRUD and profile editing. It is the only implementation wired to real data and actively used.

**Treat `app/gui/domains/control_center` Agents tab as the Control Center integration point** – it should host the real agent management UI, not demo data.

### 4.2 Target Architecture

1. **Single agent management implementation** – Use `AgentManagerPanel` (or a shared component) both in:
   - Main toolbar dialog (current behavior)
   - Control Center → Agents tab

2. **Remove dead code** – `AgentWorkspace` and its dependent panels are never reached. Either remove or migrate valuable features (Runs, Activity, Skills) into Control Center as separate tabs/panels.

3. **Replace demo data** – `AgentRegistryPanel` and `AgentSummaryPanel` should be replaced or wired to `AgentService` / `AgentRegistry`.

---

## 5. Migration Plan

### Phase 1: Unify Control Center Agents Tab

| Step | Action |
|------|--------|
| 1.1 | Replace `AgentsWorkspace` content with `AgentManagerPanel` (or embed it in a scroll area). |
| 1.2 | Ensure `AgentManagerPanel` works in Control Center layout (inspector, theme). |
| 1.3 | Remove `AgentRegistryPanel` and `AgentSummaryPanel` demo implementations. |

### Phase 2: Remove Dead Code (AgentWorkspace)

| Step | Action |
|------|--------|
| 2.1 | Remove `agent_workspace.py` (never instantiated). |
| 2.2 | Remove `agent_navigation_panel.py` (only used by AgentWorkspace). |
| 2.3 | Remove `agent_library_panel.py` (only used by AgentWorkspace). |
| 2.4 | Remove `agent_editor_panel.py` (only used by AgentLibraryPanel). |
| 2.5 | Decide: Remove or migrate `agent_runs_panel`, `agent_activity_panel`, `agent_skills_panel` (see Phase 3). |

### Phase 3: Optional – Migrate Valuable Features

| Step | Action |
|------|--------|
| 3.1 | If Runs/Activity/Skills are desired in Control Center: add them as sub-tabs or panels within `AgentsWorkspace`, reusing `AgentRunsPanel`, `AgentActivityPanel`, `AgentSkillsPanel`. |
| 3.2 | If not: remove these panels. |

---

## 6. Modules to Keep

| Module | Reason |
|--------|--------|
| `agent_manager_panel` | Main entry point, full CRUD, used by main.py. |
| `agent_list_panel` | Used by AgentManagerPanel. Supports global and project-scoped. |
| `agent_list_item` | Used by AgentListPanel. |
| `agent_profile_panel` | Used by AgentManagerPanel. |
| `agent_avatar_widget` | Used by AgentProfilePanel. |
| `agent_form_widgets` | Used by AgentProfilePanel. |
| `agent_performance_tab` | Used by AgentProfilePanel. |
| `control_center_screen` | Control Center host. |
| `control_center_nav` | Control Center navigation. |
| `agents_workspace` | Control Center Agents tab (content to be replaced). |
| `base_management_workspace` | Base for all Control Center workspaces. |

**Conditional keep (if Phase 3):**

| Module | Reason |
|--------|--------|
| `agent_runs_panel` | Live agent runs from DebugStore. |
| `agent_activity_panel` | Event stream for monitoring. |
| `agent_skills_panel` | Tool configuration per agent. |

---

## 7. Modules to Remove

| Module | Reason |
|--------|--------|
| `agent_workspace` | Never instantiated. Dead code. |
| `agent_navigation_panel` | Only used by AgentWorkspace. |
| `agent_library_panel` | Only used by AgentWorkspace. |
| `agent_editor_panel` | Only used by AgentLibraryPanel. |
| `agents_panels.AgentRegistryPanel` | Demo data. Replace with real implementation. |
| `agents_panels.AgentSummaryPanel` | Static demo. Replace with real implementation. |

**Conditional remove (if Phase 3 not done):**

| Module | Reason |
|--------|--------|
| `agent_runs_panel` | Only used by AgentWorkspace. |
| `agent_activity_panel` | Only used by AgentWorkspace. |
| `agent_skills_panel` | Only used by AgentWorkspace. |

---

## 8. Summary

| Output | Result |
|--------|--------|
| **Architecture recommendation** | Single canonical agent management: `AgentManagerPanel`. Control Center Agents tab hosts it. Remove `AgentWorkspace` (dead). |
| **Migration plan** | Phase 1: Replace Control Center Agents content with `AgentManagerPanel`. Phase 2: Remove AgentWorkspace and dependent panels. Phase 3 (optional): Migrate Runs/Activity/Skills into Control Center. |
| **Modules to keep** | `agent_manager_panel`, `agent_list_panel`, `agent_list_item`, `agent_profile_panel`, `agent_avatar_widget`, `agent_form_widgets`, `agent_performance_tab`, Control Center screen/nav/workspace/base. |
| **Modules to remove** | `agent_workspace`, `agent_navigation_panel`, `agent_library_panel`, `agent_editor_panel`, demo `AgentRegistryPanel`/`AgentSummaryPanel`; optionally `agent_runs_panel`, `agent_activity_panel`, `agent_skills_panel` if not migrated. |
