# UX Defect List – Manual Testing Simulation

**Version:** 1.0  
**Date:** 2026-03-16  
**Scope:** Simulated manual usage of the new UX architecture – project switching, workspace navigation, Settings, stale state, labels, placeholders, project-scoped data isolation  
**Method:** Codebase trace and flow analysis (no live GUI interaction)

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 2 |
| Major | 6 |
| Minor | 5 |

---

## Critical Defects

### D1: Dual Project Context Systems Not Synchronized

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Operations → Projects. 2. Select a project from the list. 3. Click "Als aktives Projekt setzen". 4. Navigate to Chat, Knowledge, Prompt Studio, or Agents. |
| **Expected behavior** | All workspaces show data for the newly activated project. |
| **Actual behavior** | Chat, Knowledge, Prompt Studio, and Agents still show data for the previous project (or "Bitte Projekt auswählen" if none was set via TopBar). |
| **Severity** | Critical |
| **Likely subsystem** | Project context (`ProjectContextManager` vs `ActiveProjectContext`) |

**Root cause:** Two independent project context systems exist:

- **ProjectContextManager** (core) – used by TopBar ProjectSwitcher, Chat, Knowledge, Prompt Studio, Agents; emits `project_context_changed`
- **ActiveProjectContext** (context) – used by ProjectsWorkspace, ProjectOverviewPanel, BreadcrumbManager; emits `active_project_changed`

"Als aktives Projekt setzen" in ProjectsWorkspace updates only `ActiveProjectContext`. It never calls `ProjectContextManager.set_active_project()`. Workspaces that depend on `project_context_changed` therefore do not react.

---

### D2: Project Switcher (TopBar) Does Not Update Projects List

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Operations → Projects. 2. Note the selected project. 3. Use TopBar Project Switcher to select a different project. 4. Observe the Projects list. |
| **Expected behavior** | Projects list selection and overview update to the newly selected project. |
| **Actual behavior** | Projects list and overview remain on the previously selected project. |
| **Severity** | Critical |
| **Likely subsystem** | Project context (`ProjectContextManager` vs `ActiveProjectContext`) |

**Root cause:** TopBar ProjectSwitcher calls `ProjectContextManager.set_active_project(project_id)` only. It never updates `ActiveProjectContext`. ProjectsWorkspace subscribes to `ActiveProjectContext.active_project_changed`, so it never receives the change.

---

## Major Defects

### D3: Repeated Project Switching Can Leave Stale Chat Content

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Select Project A via TopBar. 2. Open Chat, select a chat, send a message. 3. Switch to Project B via TopBar. 4. Switch back to Project A. 5. Observe Chat workspace. |
| **Expected behavior** | Chat shows Project A’s sessions and the correct conversation. |
| **Actual behavior** | ChatWorkspace clears on project change (`_on_project_context_changed` clears conversation and details). When switching back, the session list is refreshed, but if the user had a chat open and switches quickly, the previously selected chat may not be reselected; the main area can appear empty until the user picks a session again. |
| **Severity** | Major |
| **Likely subsystem** | Chat workspace, project context propagation |

**Note:** Clearing on project change is correct. The defect is that no "last selected chat per project" is restored when returning, so the user must reselect a chat manually.

---

### D4: Opening Chat / Knowledge / Prompt Studio / Agents in Different Orders Without Project

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Start app (no project selected). 2. Open Chat → Knowledge → Prompt Studio → Agents in any order. |
| **Expected behavior** | Each workspace shows a clear empty state: "Bitte Projekt auswählen" or equivalent, with disabled create actions. |
| **Actual behavior** | Chat, Knowledge, Prompt Studio, and Agents all show "Bitte Projekt auswählen" and disable creation. Agent Tasks workspace uses `list_agents()` without project filter in `AgentRegistryPanel`; it may show global agents even when no project is active. |
| **Severity** | Major |
| **Likely subsystem** | Agent Tasks workspace, AgentRegistryPanel |

**Note:** Agent Tasks subscribes to `project_context_changed` but `AgentRegistryPanel` and `AgentTaskPanel` may not strictly filter by project when none is set.

---

### D5: Settings Navigation and Back – Breadcrumb/Selection Mismatch

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Settings → Application. 2. Open Settings → Appearance. 3. Use Sidebar to go to Operations → Chat. 4. Use Sidebar to return to Settings. |
| **Expected behavior** | Settings opens with the last viewed category (e.g. Appearance) selected. |
| **Actual behavior** | `SettingsScreen.get_current_workspace()` always returns `"settings_application"`. Breadcrumbs may show "Application" even when the user was on Appearance. Sidebar selection may not match the visible Settings category. |
| **Severity** | Major |
| **Likely subsystem** | Settings screen, breadcrumb manager |

---

### D6: Inconsistent Labels – Operations Nav vs Sidebar vs UX Spec

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Compare Operations sub-nav labels with global Sidebar labels. 2. Compare with UX_CONCEPT.md. |
| **Expected behavior** | Consistent naming: e.g. "Agent Tasks" in Operations and "Agents" in Sidebar should map clearly to the same concept. |
| **Actual behavior** | Operations nav: "Projekte", "Chat", "Agent Tasks", "Knowledge / RAG", "Prompt Studio". Sidebar WORKSPACE: "Projects", "Chat", "Knowledge", "Prompt Studio", "Agents". Mixed EN/DE: "Projekte" vs "Projects", "Agent Tasks" vs "Agents". UX spec: "Agent Tasks" under Operations; Control Center has "Agents" (design). Sidebar has "Agents" under WORKSPACE (unclear if Tasks or design). |
| **Severity** | Major |
| **Likely subsystem** | Navigation, sidebar config, operations nav |

---

### D7: Empty or Placeholder Views in Workspaces

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Knowledge → Settings section. 2. Open Prompt Studio → Settings section. 3. Open Agent workspace (if using ui/agents) → Settings section. |
| **Expected behavior** | Either a functional settings UI or a clear "Not yet available" message. |
| **Actual behavior** | Knowledge Settings: `KnowledgeContentPlaceholder` – "Content panel – implement section-specific UI here." Prompt Studio Settings: "Prompt Studio Einstellungen. (Coming soon)". Agent Settings: "Agent-Workspace-Einstellungen." (placeholder). |
| **Severity** | Major |
| **Likely subsystem** | Knowledge, Prompt Studio, Agent workspaces |

---

### D8: Project-Scoped Data Visibility When Switching Projects

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Select Project A. 2. Open Chat, create Chat X. 3. Open Knowledge, add Source S. 4. Open Prompt Studio, create Prompt P. 5. Switch to Project B via TopBar. 6. Check Chat, Knowledge, Prompt Studio. |
| **Expected behavior** | Each workspace shows only Project B’s data (or empty if none). No data from Project A. |
| **Actual behavior** | Chat, Knowledge, Prompt Studio subscribe to `project_context_changed` and reload. Data is project-scoped via `project_id` filters. No cross-project leakage observed in the code paths. |
| **Severity** | Major (verification) |
| **Likely subsystem** | Chat, Knowledge, Prompt Studio, project context |

**Note:** This is a verification item. Code analysis suggests correct isolation. Manual testing should confirm there is no brief flash of wrong data or race conditions during project switch.

---

## Minor Defects

### D9: Mixed Language in Chat Navigation

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Chat. 2. Inspect section labels. |
| **Expected behavior** | Consistent language (all DE or all EN). |
| **Actual behavior** | "Ungrouped" (EN), "Archiviert", "Angeheftet" (DE). |
| **Severity** | Minor |
| **Likely subsystem** | Chat navigation panel |

---

### D10: Settings Category Mismatch – Legacy vs New IDs

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Navigate to Settings via Command Palette or direct workspace_id. 2. Use legacy IDs like `settings_system`, `settings_models`. |
| **Expected behavior** | Correct category is shown. |
| **Actual behavior** | `SettingsScreen` maps `settings_system` → `settings_application`, `settings_models` → `settings_ai_models`. Works, but legacy IDs suggest older structure; mapping could be documented or removed. |
| **Severity** | Minor |
| **Likely subsystem** | Settings screen |

---

### D11: Project Hub vs Projects – Overlapping Entry Points

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Sidebar PROJECT section. 2. Compare "Project Hub", "Dashboard", "Projects". |
| **Expected behavior** | Clear distinction between project overview, dashboard, and project list. |
| **Actual behavior** | Project Hub (standalone), Dashboard (Command Center), Projects (Operations) overlap in purpose. Naming and roles are unclear. |
| **Severity** | Minor |
| **Likely subsystem** | Navigation, sidebar config |

---

### D12: Inspector Not Cleared When Switching Workspaces Quickly

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Chat, select a chat (Inspector shows session details). 2. Quickly switch to Knowledge, then to Prompt Studio. |
| **Expected behavior** | Inspector always shows content for the current workspace. |
| **Actual behavior** | `OperationsScreen._on_workspace_changed` calls `setup_inspector` on the new workspace. If the workspace has no inspector or fails, `inspector_host.clear_content()` may not be called in all paths. Inspector could briefly show stale content. |
| **Severity** | Minor |
| **Likely subsystem** | Inspector host, operations screen |

---

### D13: Create Flow Without Project – Error Message Placement

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Ensure no project is selected. 2. Open Chat. 3. Type a message and send. |
| **Expected behavior** | Clear message that a project must be selected first. |
| **Actual behavior** | `_show_error("Bitte zuerst ein Projekt auswählen.")` displays the message in the conversation area as an assistant message. It is easy to miss and looks like a normal reply. |
| **Severity** | Minor |
| **Likely subsystem** | Chat workspace, input validation |

---

## Test Scenarios Covered

| Scenario | Result |
|----------|--------|
| Switching projects repeatedly (TopBar) | D2: Projects list does not update |
| Switching projects repeatedly (Projects list) | D1: Chat/Knowledge/Prompt/Agents do not update |
| Opening Chat / Knowledge / Prompt Studio / Agents in different orders | D4: Agent Tasks may show global agents without project |
| Creating and selecting items | D1, D2 affect creation context; D13 affects error display |
| Navigating to Settings and back | D5: Breadcrumb/selection mismatch |
| Stale UI state | D3, D12 |
| Inconsistent labels | D6, D9, D11 |
| Empty or placeholder views | D7 |
| Project-scoped data isolation | D8: Appears correct; manual verification recommended |

---

## Recommended Fix Priority

1. **Critical:** Synchronize `ProjectContextManager` and `ActiveProjectContext` (D1, D2).
2. **Major:** Restore last-selected item per project when switching back (D3); fix Settings breadcrumb/selection (D5); replace or remove placeholder views (D7); align labels (D6).
3. **Minor:** Standardize language (D9); clarify Project Hub vs Projects (D11); improve "no project" error display (D13).

---

*This document records defects identified through codebase analysis. Manual GUI testing is recommended to confirm and refine these findings.*
