# UX Defect List – Behavior-First Manual Testing Simulation

**Version:** 1.3  
**Date:** 2026-03-16  
**Scope:** Simulated manual usage of the new UX architecture – project switching, workspace navigation, Settings, stale state, labels, placeholders, project-scoped data isolation  
**Method:** Application behavior simulation (pytest), code flow trace, and workspace switching exercises

**Full audits:**
- [UX_DEFECTS_BEHAVIOR_AUDIT_2026-03-16.md](UX_DEFECTS_BEHAVIOR_AUDIT_2026-03-16.md) – First audit (D13–D23)
- [UX_DEFECTS_BEHAVIOR_AUDIT_2_2026-03-16.md](UX_DEFECTS_BEHAVIOR_AUDIT_2_2026-03-16.md) – Second deeper audit (D24–D36)
- [UX_DEFECTS_FINAL_KILL_SWEEP_2026-03-16.md](UX_DEFECTS_FINAL_KILL_SWEEP_2026-03-16.md) – **Final pre-release kill sweep** (D37–D39, verified stable areas)

---

## Summary

| Severity | Open | Resolved |
|----------|------|----------|
| Critical | 0 | 1 |
| Major | 3 | 5 |
| Minor | 8 | 3 |

**Status:** D1, D2, D3, D4, D5, D6, D11, D13 resolved. D7, D8, D9, D10, D12, D14–D23 remain open.

---

## Resolved Defects (Verified)

### D1: Settings Breadcrumb Mismatch – Always Reports "Application"

| Field | Value |
|-------|-------|
| **Status** | **Resolved** |
| **Reproduction steps** | 1. Open Settings via Sidebar → Appearance. 2. Navigate to Chat. 3. Open Settings via Command Palette (no workspace_id). |
| **Expected behavior** | Breadcrumb reflects the currently visible Settings category. |
| **Actual behavior (before fix)** | Breadcrumb always showed "Application". |
| **Resolution** | `SettingsScreen.get_current_workspace()` delegates to `SettingsWorkspace.get_current_category()`, which returns the actual category from `_stack.currentIndex()` and `_stack_indices`. `WorkspaceHost.show_area()` uses `widget.get_current_workspace()` when no workspace_id is passed, so breadcrumb displays correctly. |
| **Likely subsystem** | `SettingsScreen`, `SettingsWorkspace`, `WorkspaceHost` |

---

### D2: Chat Does Not Restore Last-Selected Session When Switching Projects Back

| Field | Value |
|-------|-------|
| **Status** | **Resolved** |
| **Reproduction steps** | 1. Select Project A via TopBar. 2. Open Chat, select a chat. 3. Switch to Project B. 4. Switch back to Project A. |
| **Expected behavior** | Chat restores the previously selected chat (or first chat). |
| **Actual behavior (before fix)** | Main area appeared empty until user manually selected a session. |
| **Resolution** | `ChatWorkspace` has `_last_selected_chat_per_project` dict and `_restore_project_selection()`. On `project_context_changed`, it restores last selection or selects first chat. |
| **Likely subsystem** | `ChatWorkspace`, `ChatSessionExplorerPanel` |

---

### D3, D4, D5: No-Project Behavior, Agent Filter, Error Placement

| Field | Value |
|-------|-------|
| **Status** | **Resolved** (see docs/CHAT_GLOBAL_MODE.md) |
| **Resolution** | Chat Global Mode intentional. Agent Tasks project filter implemented. No-project error shown as inline warning over Chat input. |

---

### D11: BreadcrumbManager Missing Settings Categories

| Field | Value |
|-------|-------|
| **Status** | **Resolved** |
| **Resolution** | `WORKSPACE_INFO` in `BreadcrumbManager` includes `settings_project` and `settings_workspace` (lines 48–49). |

---

### D6: Mixed Language in Chat Navigation

| Field | Value |
|-------|-------|
| **Status** | **Resolved** |
| **Reproduction steps** | 1. Open Chat with a project selected. 2. Inspect section labels and filter checkboxes. |
| **Resolution** | `ChatNavigationPanel` uses "Ungruppiert", "Angeheftet", "Archiv" (all DE). `tests/behavior/ux_regression_tests.py::test_chat_navigation_language_consistency` passes. |
| **Likely subsystem** | `ChatNavigationPanel`, `ChatTopicSection` |

---

### D13: Crash When Switching to Prompt Studio

| Field | Value |
|-------|-------|
| **Status** | **Resolved** |
| **Reproduction steps** | 1. Start application. 2. Open Operations → Prompt Studio. |
| **Actual behavior (before fix)** | `TypeError: PromptStudioWorkspace.setup_inspector() got an unexpected keyword argument 'content_token'`. |
| **Resolution** | `app.ui.prompts.PromptStudioWorkspace.setup_inspector` now accepts `content_token: int | None = None` and passes it to `inspector_host.set_content()`. |
| **Likely subsystem** | `app.ui.prompts.prompt_studio_workspace`, `OperationsScreen` |

---

## Open Defects

### D12: Sidebar SYSTEM Section Missing Agents (NEW)

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Sidebar. 2. Expand SYSTEM section. 3. Compare with UX spec (Control Center: Models, Providers, **Agents**, Tools, Data Stores). |
| **Expected behavior** | Sidebar SYSTEM lists all five Control Center workspaces including Agents. |
| **Actual behavior** | Sidebar lists only Models, Providers, Tools, Data Stores. Users cannot reach Agents (cc_agents) via one-click from Sidebar; must open Control Center first, then select Agents from sub-nav. |
| **Severity** | Major |
| **Likely subsystem** | `sidebar_config.py` |

---

### D7: Breadcrumb vs Sidebar/Operations Nav – Label Inconsistency

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Operations → Agent Tasks. 2. Inspect Breadcrumb. 3. Compare with Sidebar and Operations Nav. |
| **Expected behavior** | Consistent labels across Breadcrumb, Sidebar, and Operations Nav. |
| **Actual behavior** | Breadcrumb shows "Agents" for operations_agent_tasks; Sidebar and Operations Nav show "Agent Tasks". Breadcrumb shows "Project Overview" (EN) for operations_projects; Sidebar and Operations Nav show "Projekte" (DE). Mixed EN/DE. |
| **Severity** | Minor |
| **Likely subsystem** | `BreadcrumbManager.WORKSPACE_INFO`, `sidebar_config.py`, `OperationsNav` |

---

### D8: Settings Project/Workspace Categories – Placeholder Content

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Settings → Project. 2. Open Settings → Workspace. |
| **Expected behavior** | Functional settings or clear "Not yet available" message. |
| **Actual behavior** | Project: "Projektspezifische Einstellungen" + "Dieser Bereich wird in einer zukünftigen Version erweitert." Workspace: "Workspace-spezifische Einstellungen" + same message. Acceptable for initial release. |
| **Severity** | Minor |
| **Likely subsystem** | `ProjectCategory`, `WorkspaceCategory` |

---

### D9: Inspector May Show Stale Content on Rapid Workspace Switching

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Chat, select a chat (Inspector shows session details). 2. Quickly switch to Knowledge, then to Prompt Studio. |
| **Expected behavior** | Inspector always shows content for the current workspace. |
| **Actual behavior** | `OperationsScreen._on_workspace_changed` calls `prepare_for_setup` and passes `content_token` – stale content guarded. `ControlCenterScreen._on_workspace_changed` does NOT use `prepare_for_setup` or `content_token`. Rapid switching in Control Center (Models → Providers → Agents) has higher risk of stale inspector. |
| **Severity** | Minor |
| **Likely subsystem** | `OperationsScreen`, `ControlCenterScreen`, `InspectorHost`, workspace `setup_inspector` |

---

### D10: Project Hub vs Projects vs Dashboard – Overlapping Entry Points

| Field | Value |
|-------|-------|
| **Reproduction steps** | 1. Open Sidebar PROJECT section. 2. Compare "Project Hub", "Dashboard", "Projects". |
| **Expected behavior** | Clear distinction between project overview, dashboard, and project list. |
| **Actual behavior** | Project Hub (standalone), Dashboard (Command Center), Projects (Operations) overlap in purpose. Naming and roles could be clearer. |
| **Severity** | Minor |
| **Likely subsystem** | Navigation, `sidebar_config.py` |

---

## Verification Items (No Defect Observed)

### V1: Project-Scoped Data Isolation

| Field | Value |
|-------|-------|
| **Scenario** | 1. Select Project A. 2. Create Chat X, Knowledge Source S, Prompt P. 3. Switch to Project B. 4. Check Chat, Knowledge, Prompt Studio. |
| **Expected** | Each workspace shows only Project B's data (or empty). |
| **Result** | Chat, Knowledge, Prompt Studio subscribe to `project_context_changed` and reload. Data is project-scoped via `project_id` filters. No cross-project leakage observed in code paths. **Manual testing recommended** to confirm no brief flash of wrong data or race conditions. |

---

### V2: Project Context Sync (TopBar ↔ Projects Workspace)

| Field | Value |
|-------|-------|
| **Scenario** | 1. Set project via TopBar Switcher. 2. Set project via Operations → Projects → "Als aktiv setzen". |
| **Expected** | Both paths update all workspaces and breadcrumbs. |
| **Result** | `ProjectsWorkspace._on_set_active` calls `ProjectContextManager.set_active_project()`, which syncs to `ActiveProjectContext`. TopBar uses `ProjectContextManager`. Both paths should work. **Verified in code.** |

---

### V3: Workspace Switching in Different Orders

| Field | Value |
|-------|-------|
| **Scenario** | 1. Open Chat → Knowledge → Prompt Studio → Agents → Settings → Chat. 2. Reverse: Agents → Prompt Studio → Knowledge → Chat. |
| **Expected** | No crash. Inspector updates for current workspace. |
| **Result** | `tests/behavior/ux_behavior_simulation.py::test_workspace_switch_order_no_crash` passes. No crash observed. |

---

### V4: Application Startup

| Field | Value |
|-------|-------|
| **Scenario** | Run `python main.py` or `python run_gui_shell.py`. |
| **Expected** | Application starts, main window visible, all areas reachable. |
| **Result** | Application starts successfully. Qt D-Bus portal warning (Connection already associated) is non-fatal. |

---

## Test Scenarios Covered

| Scenario | Result |
|----------|--------|
| Switching projects repeatedly (TopBar) | V2: Sync verified |
| Switching projects repeatedly (Projects list) | V2: Sync verified |
| Opening Chat / Knowledge / Prompt Studio / Agents in different orders | V3: No crash |
| Creating and selecting items | D2: Restore logic implemented |
| Navigating to Settings and back | D1: Breadcrumb correct |
| Stale UI state | D9: Control Center at higher risk |
| Inconsistent labels | D6 resolved; D7, D10 open |
| Empty or placeholder views | D8 |
| Project-scoped data isolation | V1 |
| Sidebar navigation completeness | D12: Agents missing from SYSTEM |

---

## Recommended Fix Priority

1. **Major:** Add Agents to Sidebar SYSTEM section (D12). Users cannot reach Agent Design (Control Center) via one-click from Sidebar.
2. **Minor:** Align Breadcrumb labels with Sidebar/Operations (D7). Clarify Project Hub vs Projects vs Dashboard (D10).
3. **Control Center:** Add `prepare_for_setup` and `content_token` to `ControlCenterScreen._on_workspace_changed` (D9).
4. **Documentation:** D8, D9 are acceptable for initial release; document for completeness.

---

## Test Artifacts

- `tests/behavior/ux_behavior_simulation.py` – Programmatic simulation of user flows (project switch, Settings breadcrumb, workspace order, label checks).
- `tests/smoke/test_shell_gui.py` – Smoke tests for ShellMainWindow and all areas.

---

*This document records defects identified through behavior simulation, code flow analysis, and workspace switching exercises. Manual GUI testing is recommended to confirm and refine these findings.*
