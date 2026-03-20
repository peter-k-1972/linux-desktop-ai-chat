# UX Defect Report – Comprehensive Behavior-First Audit

**Version:** 1.0  
**Date:** 2026-03-16  
**Scope:** Full exploratory UX and behavior audit of Linux Desktop Chat  
**Method:** Application behavior simulation (pytest), observed crash reproduction, code flow trace for UI structure, workspace switching exercises  
**Reference:** [UX_DEFECTS_BEHAVIOR_TEST.md](UX_DEFECTS_BEHAVIOR_TEST.md) (prior defects D1–D12)

---

## Executive Summary

This audit identified **1 Critical** (resolved), **3 Major**, **8 Minor**, and **4 Cosmetic** defects. The most severe finding was a **crash when switching to Prompt Studio** due to a `setup_inspector` signature mismatch — **fixed** by adding `content_token` support to `app.ui.prompts.PromptStudioWorkspace`. Several navigation gaps, label inconsistencies, and placeholder panels remain open.

---

## Summary Table

| Severity | Count | Resolved |
|----------|-------|----------|
| Critical | 1 | 1 |
| Major | 3 | 0 |
| Minor | 8 | 0 |
| Cosmetic / UX Polish | 4 | 0 |

| Defect Type | Count |
|-------------|-------|
| Bug | 2 |
| Regression | 0 |
| Unimplemented widget | 0 |
| Placeholder | 4 |
| UX inconsistency | 6 |
| Project-context issue | 0 |
| Visual/layout issue | 2 |
| Navigation gap | 2 |

---

## Critical Defects

### D13: Crash When Switching to Prompt Studio (TypeError) — RESOLVED

| Field | Value |
|-------|-------|
| **Defect ID** | D13 |
| **Title** | Crash when switching Operations → Prompt Studio |
| **Status** | **Resolved** |
| **Reproduction steps** | 1. Start application (`python main.py`). 2. Open Operations (e.g. via Sidebar → Chat). 3. Click "Prompt Studio" in Operations sub-nav. |
| **Expected behavior** | Prompt Studio workspace loads; Inspector updates for Prompt Studio context. |
| **Actual behavior (before fix)** | Application crashed with `TypeError: PromptStudioWorkspace.setup_inspector() got an unexpected keyword argument 'content_token'`. |
| **Resolution** | `app.ui.prompts.PromptStudioWorkspace.setup_inspector` now accepts `content_token: int | None = None` and passes it to `inspector_host.set_content()`. |
| **Severity** | Critical |
| **Confidence** | High |
| **Likely subsystem** | `OperationsScreen`, `app.ui.prompts.PromptStudioWorkspace` |
| **Type** | Bug |

---

## Major Defects

### D12: Sidebar SYSTEM Section Missing Agents (Existing)

| Field | Value |
|-------|-------|
| **Defect ID** | D12 |
| **Title** | Sidebar SYSTEM section missing Agents |
| **Reproduction steps** | 1. Open Sidebar. 2. Expand SYSTEM section. 3. Compare with UX spec (Control Center: Models, Providers, **Agents**, Tools, Data Stores). |
| **Expected behavior** | Sidebar SYSTEM lists all five Control Center workspaces including Agents. |
| **Actual behavior** | Sidebar lists only Models, Providers, Tools, Data Stores. Users cannot reach Agents (cc_agents) via one-click from Sidebar; must open Control Center first, then select Agents from sub-nav. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `sidebar_config.py` |
| **Type** | Navigation gap |

---

### D14: Sidebar OBSERVABILITY Section Missing System Graph

| Field | Value |
|-------|-------|
| **Defect ID** | D14 |
| **Title** | Sidebar OBSERVABILITY section missing System Graph |
| **Reproduction steps** | 1. Open Sidebar. 2. Expand OBSERVABILITY section. 3. Compare with Runtime sub-nav and UX spec. |
| **Expected behavior** | Sidebar OBSERVABILITY lists all six Runtime/Debug workspaces including System Graph. |
| **Actual behavior** | Sidebar lists Runtime, Logs, LLM Calls, Agent Activity, Metrics. System Graph (rd_system_graph) is missing. Users must open Runtime/Debug first, then select System Graph from sub-nav. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `sidebar_config.py` |
| **Type** | Navigation gap |

---

### D15: Command Palette Missing Workspace-Specific Navigation

| Field | Value |
|-------|-------|
| **Defect ID** | D15 |
| **Title** | Command Palette does not offer Knowledge, Prompt Studio, Agent Tasks |
| **Reproduction steps** | 1. Open Command Palette (Ctrl+Shift+P). 2. Search for "Knowledge", "Prompt Studio", "Agent Tasks". |
| **Expected behavior** | Users can navigate to these workspaces via Command Palette (consistent with Chat, Projects). |
| **Actual behavior** | Command Palette offers: Open Dashboard, Open Projects, Open Chat, Open Control Center, Open QA & Governance, Open Runtime/Debug, Open Settings, Switch Theme, Reload Theme. No commands for Knowledge, Prompt Studio, or Agent Tasks. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `app.gui.commands.bootstrap` |
| **Type** | UX inconsistency |

---

## Minor Defects

### D7: Breadcrumb vs Sidebar/Operations – Label Inconsistency (Existing)

| Field | Value |
|-------|-------|
| **Defect ID** | D7 |
| **Title** | Breadcrumb vs Sidebar/Operations label mismatch |
| **Reproduction steps** | 1. Open Operations → Agent Tasks. 2. Inspect Breadcrumb. 3. Compare with Sidebar and Operations Nav. |
| **Expected behavior** | Consistent labels across Breadcrumb, Sidebar, and Operations Nav. |
| **Actual behavior** | Breadcrumb shows "Agents" for operations_agent_tasks; Sidebar and Operations Nav show "Agent Tasks". Breadcrumb shows "Project Overview" (EN) for operations_projects; Sidebar and Operations Nav show "Projekte" (DE). Mixed EN/DE. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `BreadcrumbManager.WORKSPACE_INFO`, `sidebar_config.py`, `OperationsNav` |
| **Type** | UX inconsistency |

**Label mapping:**

| workspace_id | Breadcrumb | Sidebar | Operations Nav |
|-------------|------------|---------|----------------|
| operations_projects | "Project Overview" | "Projekte" | "Projekte" |
| operations_agent_tasks | "Agents" | "Agent Tasks" | "Agent Tasks" |
| operations_knowledge | "Knowledge / RAG" | "Knowledge" | "Knowledge / RAG" |

---

### D8: Settings Project/Workspace Categories – Placeholder Content (Existing)

| Field | Value |
|-------|-------|
| **Defect ID** | D8 |
| **Title** | Settings Project/Workspace categories are placeholders |
| **Reproduction steps** | 1. Open Settings → Project. 2. Open Settings → Workspace. |
| **Expected behavior** | Functional settings or clear "Not yet available" message. |
| **Actual behavior** | Project: "Projektspezifische Einstellungen" + "Dieser Bereich wird in einer zukünftigen Version erweitert." Workspace: "Workspace-spezifische Einstellungen" + same message. Acceptable for initial release. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `ProjectCategory`, `WorkspaceCategory` |
| **Type** | Placeholder |

---

### D9: Inspector May Show Stale Content on Rapid Workspace Switching (Existing)

| Field | Value |
|-------|-------|
| **Defect ID** | D9 |
| **Title** | Control Center does not use content_token; risk of stale inspector |
| **Reproduction steps** | 1. Open Control Center → Models (Inspector shows model details). 2. Quickly switch to Providers, then to Agents. |
| **Expected behavior** | Inspector always shows content for the current workspace. |
| **Actual behavior** | `OperationsScreen._on_workspace_changed` uses `prepare_for_setup` and `content_token`. `ControlCenterScreen._on_workspace_changed` does NOT. Rapid switching in Control Center (Models → Providers → Agents) has higher risk of stale inspector. Same for QAGovernanceScreen, RuntimeDebugScreen. |
| **Severity** | Minor |
| **Confidence** | Medium |
| **Likely subsystem** | `ControlCenterScreen`, `QAGovernanceScreen`, `RuntimeDebugScreen`, `InspectorHost` |
| **Type** | Bug |

---

### D10: Project Hub vs Projects vs Dashboard – Overlapping Entry Points (Existing)

| Field | Value |
|-------|-------|
| **Defect ID** | D10 |
| **Title** | Project Hub vs Projects vs Dashboard – overlapping entry points |
| **Reproduction steps** | 1. Open Sidebar PROJECT section. 2. Compare "Projektübersicht", "Systemübersicht", "Projekte". |
| **Expected behavior** | Clear distinction between project overview, dashboard, and project list. |
| **Actual behavior** | Project Hub (standalone), Dashboard (Command Center), Projects (Operations) overlap in purpose. Naming and roles could be clearer. Tooltips help but labels are similar. |
| **Severity** | Minor |
| **Confidence** | Medium |
| **Likely subsystem** | Navigation, `sidebar_config.py` |
| **Type** | UX inconsistency |

---

### D16: Mixed Language in Empty States and Placeholder Texts

| Field | Value |
|-------|-------|
| **Defect ID** | D16 |
| **Title** | Mixed DE/EN in empty states and placeholders |
| **Reproduction steps** | 1. Open Knowledge (no project). 2. Open Agent Activity (no runs). 3. Open Collection Panel (no project). 4. Inspect empty-state texts. |
| **Expected behavior** | Consistent language (DE or EN) across empty states. |
| **Actual behavior** | Mix: "Kein Projekt ausgewählt" (DE), "No project selected" (EN), "No agent runs yet" (EN), "Bitte Projekt auswählen" (DE), "No events yet" (EN). |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `EmptyStateWidget` usages, `agent_activity_panel`, `agent_runs_panel`, `collection_panel`, `source_list_panel` |
| **Type** | UX inconsistency |

---

### D17: Settings Categories – Multiple "In Entwicklung" Placeholders

| Field | Value |
|-------|-------|
| **Defect ID** | D17 |
| **Title** | Several Settings categories show "In Entwicklung" without clear scope |
| **Reproduction steps** | 1. Open Settings → Application. 2. Open AI/Models, Data, Privacy, Advanced. |
| **Expected behavior** | Functional settings or clearly scoped "Coming soon" with timeline/scope. |
| **Actual behavior** | Application: "Systemoptionen werden hier erscheinen. (In Entwicklung)". AI/Models, Data, Privacy: "(In Entwicklung)". Advanced: "Developer Settings", "Debug Panel", "Experimentelle Features (noch nicht verfügbar)". No indication of priority or roadmap. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `application_category`, `ai_models_category`, `data_category`, `privacy_category`, `advanced_category` |
| **Type** | Placeholder |

---

### D18: Control Center Agents Workspace – Placeholder Panels

| Field | Value |
|-------|-------|
| **Defect ID** | D18 |
| **Title** | Control Center Agents workspace has "Coming soon" style placeholder sections |
| **Reproduction steps** | 1. Open Control Center → Agents. 2. Inspect Library, Runs, Activity, Skills panels. |
| **Expected behavior** | Functional agent design/management or clear empty state. |
| **Actual behavior** | `agent_workspace.py` uses `_placeholder_widget()` for Library, Runs, Activity, Skills – "Coming soon" style sections. |
| **Severity** | Minor |
| **Confidence** | Medium |
| **Likely subsystem** | `app.gui.domains.control_center.workspaces.agents_workspace`, `app.ui.agents.agent_workspace` |
| **Type** | Placeholder |

---

### D19: Inspector Default Content – German Only

| Field | Value |
|-------|-------|
| **Defect ID** | D19 |
| **Title** | Inspector default placeholder uses German only |
| **Reproduction steps** | 1. Open any workspace with Inspector. 2. Ensure no selection. 3. Inspect Inspector panel. |
| **Expected behavior** | Default placeholder matches app language. |
| **Actual behavior** | InspectorHost shows "Kontext", "Auswahl", "Details" with "Kein Kontext ausgewählt.", "Wählen Sie ein Objekt aus.", "Objektinformationen erscheinen hier." – German only. If app targets mixed audience, consider consistency. |
| **Severity** | Minor |
| **Confidence** | Low |
| **Likely subsystem** | `InspectorHost` |
| **Type** | UX inconsistency |

---

## Cosmetic / UX Polish

### D20: Command Palette Placeholder – "Befehl eingeben..."

| Field | Value |
|-------|-------|
| **Defect ID** | D20 |
| **Title** | Command Palette search placeholder mixed with English command titles |
| **Reproduction steps** | 1. Open Command Palette. 2. Inspect search placeholder and command titles. |
| **Expected behavior** | Consistent language. |
| **Actual behavior** | Placeholder "Befehl eingeben..." (DE), command titles "Open Dashboard", "Open Chat" (EN). |
| **Severity** | Cosmetic |
| **Confidence** | High |
| **Likely subsystem** | `CommandPaletteDialog` |
| **Type** | UX inconsistency |

---

### D21: Breadcrumb "Active Project" Fallback in English

| Field | Value |
|-------|-------|
| **Defect ID** | D21 |
| **Title** | BreadcrumbManager fallback "Active Project" is English |
| **Reproduction steps** | 1. Open Command Center with no project. 2. Inspect breadcrumb. |
| **Expected behavior** | Fallback matches app language. |
| **Actual behavior** | `BreadcrumbManager.set_area` uses `"Active Project"` when area_id is COMMAND_CENTER and no project. Rest of breadcrumb logic uses German. |
| **Severity** | Cosmetic |
| **Confidence** | High |
| **Likely subsystem** | `BreadcrumbManager` |
| **Type** | UX inconsistency |

---

### D22: Qt D-Bus Portal Warning on Startup

| Field | Value |
|-------|-------|
| **Defect ID** | D22 |
| **Title** | Qt D-Bus portal warning on application startup |
| **Reproduction steps** | 1. Run `python main.py`. 2. Observe console output. |
| **Expected behavior** | Clean startup or suppressed non-fatal warnings. |
| **Actual behavior** | `qt.qpa.services: Failed to register with host portal QDBusError("org.freedesktop.portal.Error.Failed", "Could not register app ID: Connection already associated with an application ID")`. Non-fatal but visible. |
| **Severity** | Cosmetic |
| **Confidence** | High |
| **Likely subsystem** | Qt platform integration |
| **Type** | Visual/layout issue |

---

### D23: Control Center Workspace Host Hardcoded Background

| Field | Value |
|-------|-------|
| **Defect ID** | D23 |
| **Title** | Control Center workspace host uses hardcoded background color |
| **Reproduction steps** | 1. Switch to Dark theme. 2. Open Control Center. 3. Inspect main workspace area. |
| **Expected behavior** | Theme-consistent background. |
| **Actual behavior** | `control_center_screen.py` sets `#controlCenterWorkspaceHost { background: #f1f5f9; }` – light gray, may clash with dark theme. |
| **Severity** | Cosmetic |
| **Confidence** | Medium |
| **Likely subsystem** | `ControlCenterScreen` |
| **Type** | Visual/layout issue |

---

## Coverage Summary

### Areas Explicitly Checked

| Area | Checked | Notes |
|------|---------|------|
| **Global Shell** | ✓ | TopBar, Sidebar, Breadcrumbs, Command Palette, Inspector, Docks |
| **Operations** | ✓ | Chat, Knowledge, Prompt Studio, Agent Tasks, Projects |
| **Control Center** | ✓ | Models, Providers, Agents, Tools, Data Stores |
| **QA & Governance** | ✓ | Test Inventory, Coverage, Incidents, Replay, Gaps |
| **Runtime / Debug** | ✓ | EventBus, Logs, LLM Calls, Agent Activity, Metrics, System Graph |
| **Settings** | ✓ | All 8 categories |
| **Project Hub** | ✓ | Entry point, empty state |
| **Command Center / Dashboard** | ✓ | Entry point |
| **Navigation** | ✓ | Sidebar, sub-navs, breadcrumbs, Command Palette |
| **Inspector** | ✓ | setup_inspector flow, content_token, default content |
| **Empty states** | ✓ | Chat, Knowledge, Prompt Studio, Agent Tasks, Settings |
| **Placeholder panels** | ✓ | Settings categories, Agent workspace |

### Verification Items (No Defect Observed)

| ID | Scenario | Result |
|----|----------|--------|
| V1 | Project-scoped data isolation | Chat, Knowledge, Prompt Studio, Agent Tasks subscribe to `project_context_changed`; data is project-scoped. Manual confirmation recommended. |
| V2 | Project context sync (TopBar ↔ Projects) | Both paths use `ProjectContextManager.set_active_project()`. |
| V3 | Workspace switching order | `test_workspace_switch_order_no_crash` passes. Note: crash to Prompt Studio occurs only when InspectorHost is connected (full app). |
| V4 | Application startup | App starts; D-Bus warning non-fatal. |
| V5 | Chat navigation language (D6) | Resolved; `test_chat_navigation_language_consistency` passes. |
| V6 | Settings breadcrumb (D1) | Resolved; `test_settings_breadcrumb_correctness` passes. |
| V7 | Inspector prepare_for_setup | InspectorHost has `prepare_for_setup` and token guard. OperationsScreen uses it. |
| V8 | Project Hub tooltips (D10) | `test_project_hub_navigation` checks tooltips; passes. |

---

## Open Questions

1. **Legacy vs new Prompt Studio:** Should OperationsScreen use `app.gui.domains.operations.prompt_studio.PromptStudioWorkspace` (with content_token) instead of `app.ui.prompts.PromptStudioWorkspace`? The gui version re-exports from ui – need to verify which implementation is intended.
2. **System Graph visibility:** Is System Graph intentionally omitted from Sidebar to reduce clutter, or an oversight?
3. **Agents in SYSTEM:** Same question – intentional simplification or oversight?
4. **Manual GUI confirmation:** Defects D13, D9, V1 should be confirmed with manual GUI testing. Automated tests use WorkspaceHost without full InspectorHost connection, so D13 does not surface in `test_workspace_switch_order_no_crash`.

---

## Recommended Fix Priority

1. **Critical:** ~~Fix D13 – Prompt Studio crash~~ **DONE.** `app.ui.prompts.PromptStudioWorkspace.setup_inspector` now accepts `content_token`.
2. **Major:** Add Agents to Sidebar SYSTEM (D12). Add System Graph to Sidebar OBSERVABILITY (D14). Add Knowledge, Prompt Studio, Agent Tasks to Command Palette (D15).
3. **Minor:** Align Breadcrumb labels with Sidebar/Operations (D7). Add `prepare_for_setup`/`content_token` to ControlCenterScreen, QAGovernanceScreen, RuntimeDebugScreen (D9). Unify empty-state language (D16).
4. **Cosmetic:** Command Palette and Breadcrumb language consistency (D20, D21). Theme-aware Control Center background (D23).

---

## Test Artifacts

- `tests/behavior/ux_behavior_simulation.py` – Programmatic simulation of user flows
- `tests/behavior/ux_regression_tests.py` – Regression tests for D1, D6, D7, D9, V1
- `tests/smoke/test_shell_gui.py` – Smoke tests for ShellMainWindow

---

*This report documents defects identified through behavior simulation, crash reproduction, and systematic UI structure exploration. Manual GUI testing is recommended to confirm and refine findings.*
