# Agents UI Architecture Audit

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Rolle:** Senior Software Architect  
**Referenz:** APP_UI_TO_GUI_TRANSITION_PLAN.md, APP_MOVE_MATRIX.md, docs/qa/architecture/AGENT_UI_ARCHITECTURE_EVALUATION.md

---

## 1. Executive Summary

The Agents UI domain has **two parallel implementations** with different purposes and data sources:

| Implementation | Location | Purpose | Data | Entry Point |
|----------------|----------|---------|------|-------------|
| **Agent Manager flow** | `app/ui/agents/` | HR-style agent CRUD, profile editing | AgentService, AgentRegistry | main.py toolbar → AgentManagerDialog |
| **Control Center Agents** | `app/gui/domains/control_center/` | Design/config view | **Demo data only** | Control Center → cc_agents tab |

**Key finding:** `AgentWorkspace` (ui) and its dependent panels (Library, Runs, Activity, Skills) are **never instantiated** in the app. Only `AgentManagerPanel` and its sub-panels are actively used.

**Recommendation:** **Strategy C (Hybrid)** – Move the Agent Manager flow into `gui/domains/control_center/agents_ui/`, replace demo content in Control Center, and remove or archive the dead AgentWorkspace branch.

---

## 2. GUI Feature Inventory

### 2.1 Control Center Structure

| File | Role | Features |
|------|------|----------|
| `control_center_screen.py` | Screen host | Nav + stacked workspaces, Inspector delegation |
| `control_center_nav.py` | Left nav | Workspace selection (Models, Providers, Agents, Tools, Data Stores) |
| `workspaces/agents_workspace.py` | Agents tab | AgentsWorkspace – AgentRegistryPanel + AgentSummaryPanel |
| `panels/agents_panels.py` | Panels | AgentRegistryPanel (demo table), AgentSummaryPanel (static summary) |
| `workspaces/base_management_workspace.py` | Base | setup_inspector(), Inspector integration |

### 2.2 AgentsWorkspace Features

| Feature | Implementation | Data |
|---------|----------------|------|
| Agent list | AgentRegistryPanel – QTableWidget | 3 hardcoded rows |
| Agent details | AgentSummaryPanel | Static "Research Agent", "Web Search, File Read, Code Exec" |
| Inspector | setup_inspector() | Updates on row selection |
| CRUD | None | — |
| Project scope | None | — |

**Conclusion:** GUI Agents tab is a **placeholder** with demo data. No AgentService integration.

---

## 3. UI Feature Inventory

### 3.1 Agent Manager Flow (actively used)

| File | Role | Features | Imported by |
|------|------|----------|-------------|
| `agent_manager_panel.py` | Main panel | List + Profile, actions (New, Duplicate, Activate, Deactivate, Delete, Use in Chat) | main.py (via AgentManagerDialog) |
| `agent_list_panel.py` | Agent list | set_agents(), project-scoped _load_agents(), Create Agent | AgentManagerPanel, AgentLibraryPanel |
| `agent_list_item.py` | List item | Per-agent widget | AgentListPanel |
| `agent_profile_panel.py` | Profile view | Avatar, read-only/edit mode, Performance tab | AgentManagerPanel |
| `agent_avatar_widget.py` | Avatar | Display/edit | AgentProfilePanel |
| `agent_form_widgets.py` | Forms | AgentProfileForm, AgentCapabilitiesEditor | AgentProfilePanel |
| `agent_performance_tab.py` | Metrics | Performance tab content | AgentProfilePanel |

**Entry point:** main.py → toolbar → `open_agent_manager()` → AgentManagerDialog.

### 3.2 Agent Workspace Flow (dead code – never instantiated)

| File | Role | Features | Imported by |
|------|------|----------|-------------|
| `agent_workspace.py` | Workspace | 3-column: Nav + stacked content + Inspector | **None** |
| `agent_navigation_panel.py` | Left nav | Agent Library, Runs, Activity, Skills | agent_workspace |
| `agent_library_panel.py` | Library section | AgentListPanel + AgentEditorPanel | agent_workspace |
| `agent_editor_panel.py` | Editor | Name, Model, Prompt, Knowledge, Tools, Memory, Limits | agent_library_panel |
| `agent_runs_panel.py` | Runs table | DebugStore polling, agent/status/start/duration | agent_workspace |
| `agent_activity_panel.py` | Activity stream | DebugStore events, model/tool calls | agent_workspace |
| `agent_skills_panel.py` | Skills config | Tool enable/disable per agent | agent_workspace |

**Entry point:** None. AgentWorkspace is exported but never imported or instantiated.

---

## 4. Feature Comparison Matrix

| Functional Area | GUI | UI (Manager) | UI (Workspace) |
|-----------------|-----|--------------|----------------|
| **Registry / list** | Demo table | AgentListPanel (real) | AgentListPanel (same) |
| **Profile / summary** | Static summary | AgentProfilePanel (full) | — |
| **Editor / form** | None | AgentProfileForm | AgentEditorPanel (different fields) |
| **Skills** | None | — | AgentSkillsPanel |
| **Runs / execution** | None | — | AgentRunsPanel |
| **Activity** | None | — | AgentActivityPanel |
| **Manager dialog** | None | AgentManagerDialog | — |
| **Navigation** | ControlCenterNav | — | AgentNavigationPanel |
| **Data source** | Hardcoded | AgentService | AgentService, DebugStore |

### Overlap Analysis

| Aspect | GUI | UI Manager | UI Workspace |
|--------|-----|------------|--------------|
| Concept | Design/config view | HR-style CRUD | Full agent management |
| Data | Demo | AgentService | AgentService, DebugStore |
| Layout | Table + Summary | List + Profile | Nav + stacked + Inspector |
| CRUD | No | Yes | Yes (via Library) |
| Inspector | Yes (used) | No | Yes (unused) |

---

## 5. Target Architecture Decision

### Chosen Strategy: **C (Hybrid)**

**Justification:**

1. **Agent Manager is canonical** – Only implementation wired to real data. Used by main.py.
2. **Control Center needs real content** – Replace demo with AgentManagerPanel (or equivalent).
3. **AgentWorkspace is dead** – Remove or archive. Its panels (Runs, Activity, Skills) have value but are unreachable; migrate only if desired.
4. **No big-bang** – Phased migration: first unify Control Center, then clean up dead code.

### Target Tree

```
app/gui/domains/control_center/
├── control_center_screen.py
├── control_center_nav.py
├── workspaces/
│   ├── agents_workspace.py      # Hosts AgentManagerPanel (or agents_ui content)
│   ├── ...
├── panels/
│   ├── agents_panels.py         # Replace with real implementation or remove
│   └── ...
└── agents_ui/                   # NEW: Migrated from ui/agents
    ├── __init__.py
    ├── agent_manager_panel.py
    ├── agent_list_panel.py
    ├── agent_list_item.py
    ├── agent_profile_panel.py
    ├── agent_avatar_widget.py
    ├── agent_form_widgets.py
    ├── agent_performance_tab.py
    └── (optional, Phase 3)
        ├── agent_runs_panel.py
        ├── agent_activity_panel.py
        └── agent_skills_panel.py
```

**Post-migration:** `app/ui/agents/` becomes minimal re-exports from `app.gui.domains.control_center.agents_ui`.

---

## 6. File-by-File Classification

| ui/agents File | Status | Reason | Target Path | Risk |
|----------------|--------|--------|-------------|------|
| agent_manager_panel.py | **move_now** (Phase 1) | Main entry, full CRUD, used by main.py | gui/.../agents_ui/agent_manager_panel.py | medium |
| agent_list_panel.py | **move_now** | Used by AgentManagerPanel | gui/.../agents_ui/agent_list_panel.py | medium |
| agent_list_item.py | **move_now** | Used by AgentListPanel | gui/.../agents_ui/agent_list_item.py | low |
| agent_profile_panel.py | **move_now** | Used by AgentManagerPanel | gui/.../agents_ui/agent_profile_panel.py | medium |
| agent_avatar_widget.py | **move_now** | Used by AgentProfilePanel | gui/.../agents_ui/agent_avatar_widget.py | low |
| agent_form_widgets.py | **move_now** | Used by AgentProfilePanel | gui/.../agents_ui/agent_form_widgets.py | low |
| agent_performance_tab.py | **move_now** | Used by AgentProfilePanel | gui/.../agents_ui/agent_performance_tab.py | low |
| agent_workspace.py | **remove_later** | Never instantiated | — | low |
| agent_navigation_panel.py | **remove_later** | Only used by AgentWorkspace | — | low |
| agent_library_panel.py | **remove_later** | Only used by AgentWorkspace | — | low |
| agent_editor_panel.py | **manual_review** | Different from AgentProfileForm; only used by AgentLibraryPanel | — | — |
| agent_runs_panel.py | **manual_review** | Valuable (DebugStore); migrate to Control Center? | gui/.../agents_ui/ (Phase 3) | — |
| agent_activity_panel.py | **manual_review** | Valuable (event stream); migrate? | gui/.../agents_ui/ (Phase 3) | — |
| agent_skills_panel.py | **manual_review** | Tool config; migrate? | gui/.../agents_ui/ (Phase 3) | — |

---

## 7. Proposed Migration Phases

### Phase 1: Unify Control Center Agents Tab (Priority)

| Step | Action | Risk |
|------|--------|------|
| 1.1 | Create `gui/domains/control_center/agents_ui/` | low |
| 1.2 | Move Agent Manager flow (7 files) to agents_ui | medium |
| 1.3 | Replace AgentsWorkspace content with AgentManagerPanel | medium |
| 1.4 | Update main.py to import from gui (or keep ui re-export) | low |
| 1.5 | Remove AgentRegistryPanel/AgentSummaryPanel demo | low |

### Phase 2: Remove Dead Code

| Step | Action | Risk |
|------|--------|------|
| 2.1 | Remove agent_workspace.py | low |
| 2.2 | Remove agent_navigation_panel.py | low |
| 2.3 | Remove agent_library_panel.py | low |
| 2.4 | Remove agent_editor_panel.py (or merge into AgentProfileForm) | manual_review |

### Phase 3: Optional – Migrate Runs/Activity/Skills

| Step | Action | Risk |
|------|--------|------|
| 3.1 | Move agent_runs_panel, agent_activity_panel, agent_skills_panel to agents_ui | medium |
| 3.2 | Add sub-tabs or panels in AgentsWorkspace for Runs/Activity/Skills | medium |

---

## 8. Risks

| Risk | Mitigation |
|------|------------|
| AgentListPanel API (theme param) | Tests fail: AgentListPanel doesn't accept theme. Fix in Phase 1. |
| AgentManagerDialog vs Panel | Dialog wrapper in agent_manager_panel; ensure both work. |
| Inspector integration | AgentManagerPanel has no setup_inspector; AgentsWorkspace does. May need adapter. |
| Test dependencies | 4 test files import ui.agents; update to gui path in Phase 1. |

---

## 9. Manual Review Points

1. **AgentEditorPanel vs AgentProfileForm** – Different field sets. AgentEditorPanel: Name, Model, Prompt, Knowledge, Tools, Memory, Limits. AgentProfileForm: different structure. Decide: merge, keep both, or drop AgentEditorPanel.
2. **Runs/Activity/Skills** – Migrate to Control Center as sub-tabs, or remove. Depends on product roadmap.
3. **AgentManagerDialog** – Standalone dialog vs embedded in Control Center. Both use cases (toolbar + tab) should work.

---

## 10. Summary

| Output | Result |
|--------|--------|
| **Strategy** | C (Hybrid) |
| **Target tree** | `gui/domains/control_center/agents_ui/` with Agent Manager flow |
| **Move now** | 7 files (manager, list, item, profile, avatar, form, performance) |
| **Remove later** | 3 files (workspace, nav, library) |
| **Manual review** | 4 files (editor, runs, activity, skills) |
| **Next sprint** | Phase 1: Create agents_ui, move Agent Manager flow, replace Control Center content |
