# UX Defect Report – Second Full Behavior Audit

**Version:** 1.0  
**Date:** 2026-03-16  
**Scope:** Second, deeper exploratory UX and behavior audit of Linux Desktop Chat  
**Method:** Behavior simulation (pytest), code flow trace, systematic UI structure exploration  
**Reference:** [UX_DEFECTS_BEHAVIOR_AUDIT_2026-03-16.md](UX_DEFECTS_BEHAVIOR_AUDIT_2026-03-16.md) (first audit D13–D23)

---

## Executive Summary

This second audit identified **1 Critical** (regression risk), **4 Major**, **10 Minor**, and **6 Cosmetic** defects. Several are **new** (not in the first audit). Key findings:

- **WorkspaceHost area-level switching** does not use `content_token` – risk of stale inspector when switching Operations ↔ Control Center ↔ Settings rapidly.
- **D13 fix not covered by automated tests** – `test_workspace_switch_order_no_crash` does not set `inspector_host`, so the Prompt Studio crash path is never exercised.
- **Control Center Agents, Tools, Data Stores** use hardcoded dummy data – misleading; users may assume real data.
- **Widespread hardcoded theme colors** – many panels use `#f1f5f9`, `#e2e8f0`, `background: white`; dark theme will show inconsistent styling.
- **Command Palette** still missing Knowledge, Prompt Studio, Agent Tasks, and all Control Center sub-workspaces (D15 confirmed).
- **Sidebar** still missing Agents (D12) and System Graph (D14).

---

## Summary Table

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Major | 4 |
| Minor | 10 |
| Cosmetic | 6 |

| Defect Type | Count |
|-------------|-------|
| Bug | 2 |
| Regression | 1 |
| Navigation gap | 2 |
| Placeholder | 3 |
| UX inconsistency | 5 |
| Theme issue | 3 |
| Unimplemented widget | 1 |
| Visual/layout issue | 2 |

---

## Critical Defects

### D24: WorkspaceHost Area Switch Does Not Use content_token – Stale Inspector Risk

| Field | Value |
|-------|-------|
| **Defect ID** | D24 |
| **Title** | Inspector can show stale content when switching areas (Operations ↔ Control Center ↔ Settings) |
| **Reproduction steps** | 1. Open Operations → Chat, select a chat (Inspector shows session details). 2. Quickly switch to Control Center (e.g. Sidebar → Models). 3. Quickly switch to Settings → Appearance. 4. Observe Inspector content. |
| **Expected behavior** | Inspector always shows content for the current area/workspace. |
| **Actual behavior** | `WorkspaceHost._on_current_changed` calls `widget.setup_inspector(self._inspector_host)` without `prepare_for_setup()` or `content_token`. There is no token-based staleness guard at area level. Rapid area switching can leave stale inspector content visible. |
| **Severity** | Critical |
| **Confidence** | High |
| **Likely subsystem** | `WorkspaceHost`, `InspectorHost` |
| **Type** | Bug |

**Note:** OperationsScreen uses `content_token` for sub-workspace switching (Chat → Knowledge → Prompt Studio). WorkspaceHost does not use it for area switching (Operations → Control Center → Settings).

---

## Major Defects

### D12: Sidebar SYSTEM Section Missing Agents (Existing, Confirmed)

| Field | Value |
|-------|-------|
| **Defect ID** | D12 |
| **Title** | Sidebar SYSTEM section missing Agents |
| **Reproduction steps** | 1. Open Sidebar. 2. Expand SYSTEM. 3. Compare with Control Center sub-nav. |
| **Expected behavior** | Sidebar lists Models, Providers, **Agents**, Tools, Data Stores. |
| **Actual behavior** | Sidebar lists only Models, Providers, Tools, Data Stores. Agents (cc_agents) not reachable via one-click. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `sidebar_config.py` |
| **Type** | Navigation gap |

---

### D14: Sidebar OBSERVABILITY Section Missing System Graph (Existing, Confirmed)

| Field | Value |
|-------|-------|
| **Defect ID** | D14 |
| **Title** | Sidebar OBSERVABILITY section missing System Graph |
| **Reproduction steps** | 1. Open Sidebar. 2. Expand OBSERVABILITY. 3. Compare with Runtime sub-nav. |
| **Expected behavior** | Sidebar lists Runtime, Logs, LLM Calls, Agent Activity, Metrics, **System Graph**. |
| **Actual behavior** | System Graph (rd_system_graph) missing. Must open Runtime/Debug first, then select from sub-nav. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `sidebar_config.py` |
| **Type** | Navigation gap |

---

### D15: Command Palette Missing Workspace-Specific Navigation (Existing, Confirmed)

| Field | Value |
|-------|-------|
| **Defect ID** | D15 |
| **Title** | Command Palette does not offer Knowledge, Prompt Studio, Agent Tasks, or Control Center sub-workspaces |
| **Reproduction steps** | 1. Open Command Palette (Ctrl+Shift+P). 2. Search for "Knowledge", "Prompt Studio", "Agent Tasks", "Agents", "Models", "System Graph". |
| **Expected behavior** | Users can navigate to these workspaces via Command Palette. |
| **Actual behavior** | Only: Open Dashboard, Open Projects, Open Chat, Open Control Center, Open QA & Governance, Open Runtime/Debug, Open Settings, Switch Theme, Reload Theme. No Knowledge, Prompt Studio, Agent Tasks. No cc_models, cc_providers, cc_agents, cc_tools, cc_data_stores. No rd_system_graph. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `app.gui.commands.bootstrap` |
| **Type** | UX inconsistency |

---

### D25: D13 Fix Not Verified by Automated Tests – Regression Risk

| Field | Value |
|-------|-------|
| **Defect ID** | D25 |
| **Title** | test_workspace_switch_order_no_crash does not exercise Prompt Studio setup_inspector with InspectorHost |
| **Reproduction steps** | 1. Inspect `test_workspace_switch_order_no_crash`. 2. Note that `WorkspaceHost` is created without `set_inspector_host()`. 3. Switch to operations_prompt_studio. |
| **Expected behavior** | Test verifies that switching to Prompt Studio with InspectorHost connected does not crash (D13 fix). |
| **Actual behavior** | Test never calls `host.set_inspector_host()`. OperationsScreen._inspector_host remains None. `_on_workspace_changed` returns early; `setup_inspector` is never called. The D13 crash path is never exercised. A future regression (e.g. removing content_token from PromptStudioWorkspace) would not be caught. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `tests/behavior/ux_behavior_simulation.py` |
| **Type** | Regression |

---

## Minor Defects

### D26: Control Center Agents, Tools, Data Stores Use Hardcoded Dummy Data

| Field | Value |
|-------|-------|
| **Defect ID** | D26 |
| **Title** | Control Center Agents, Tools, Data Stores display fake data without indication |
| **Reproduction steps** | 1. Open Control Center → Agents. 2. Inspect Agent Registry table. 3. Open Tools, Data Stores. |
| **Expected behavior** | Real data from backend, or clear "Demo data" / "No data" indication. |
| **Actual behavior** | Agents: hardcoded "Research Agent", "Code Agent", "General Assistant". Tools: hardcoded table + "7 Tools verfügbar". Data Stores: hardcoded "Sessions: 12 · Vectors: 1.2k". No indication that data is dummy. Users may assume it is real. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `agents_panels.py`, `tools_panels.py`, `data_stores_panels.py` |
| **Type** | Placeholder |

---

### D27: Control Center Agents Inspector Uses Hardcoded Agent

| Field | Value |
|-------|-------|
| **Defect ID** | D27 |
| **Title** | Control Center Agents workspace Inspector always shows "Research Agent" |
| **Reproduction steps** | 1. Open Control Center → Agents. 2. Inspect Inspector panel. 3. Click different rows in Agent Registry (if possible). |
| **Expected behavior** | Inspector reflects selected agent or shows "Select an agent". |
| **Actual behavior** | `AgentsWorkspace.setup_inspector` creates `AgentInspector(agent="Research Agent", ...)` with hardcoded values. No selection binding. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `agents_workspace.py`, `agent_inspector.py` |
| **Type** | Unimplemented widget |

---

### D7: Breadcrumb vs Sidebar/Operations – Label Inconsistency (Existing, Confirmed)

| Field | Value |
|-------|-------|
| **Defect ID** | D7 |
| **Title** | Breadcrumb labels mismatch Sidebar/Operations (EN vs DE, "Agents" vs "Agent Tasks") |
| **Reproduction steps** | 1. Open Operations → Agent Tasks. 2. Inspect Breadcrumb. 3. Compare with Sidebar and Operations Nav. |
| **Expected behavior** | Consistent labels. |
| **Actual behavior** | Breadcrumb "Agents" vs Sidebar/Operations "Agent Tasks". Breadcrumb "Project Overview" (EN) vs "Projekte" (DE). |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `BreadcrumbManager.WORKSPACE_INFO` |
| **Type** | UX inconsistency |

---

### D9: Control Center, QA, Runtime/Debug Do Not Use content_token (Existing, Confirmed)

| Field | Value |
|-------|-------|
| **Defect ID** | D9 |
| **Title** | Control Center, QA & Governance, Runtime/Debug screens do not pass content_token to setup_inspector |
| **Reproduction steps** | 1. Open Control Center → Models. 2. Quickly switch Models → Providers → Agents. 3. Observe Inspector. |
| **Expected behavior** | Inspector always shows content for current workspace. |
| **Actual behavior** | Only OperationsScreen uses `prepare_for_setup` and `content_token`. ControlCenterScreen, QAGovernanceScreen, RuntimeDebugScreen do not. Higher risk of stale inspector on rapid sub-workspace switching. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `ControlCenterScreen`, `QAGovernanceScreen`, `RuntimeDebugScreen` |
| **Type** | Bug |

---

### D28: Mixed Language in Agent Editor Panel

| Field | Value |
|-------|-------|
| **Defect ID** | D28 |
| **Title** | Agent editor panel mixes English and German placeholders |
| **Reproduction steps** | 1. Open Control Center → Agents (or app.ui.agents flow if reachable). 2. Inspect agent form placeholders. |
| **Expected behavior** | Consistent language. |
| **Actual behavior** | `agent_editor_panel.py`: "Agent name (e.g. Research Agent)" (EN), "Modell-ID oder leer für Auto" (DE), "System prompt for the agent" (EN), "e.g. rag, web_search" (EN). |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `app.ui.agents.agent_editor_panel` |
| **Type** | UX inconsistency |

---

### D29: Mixed Language in Knowledge Source List

| Field | Value |
|-------|-------|
| **Defect ID** | D29 |
| **Title** | Knowledge source list "Enter your note text..." in English |
| **Reproduction steps** | 1. Open Knowledge. 2. Add source, note type. 3. Inspect note input placeholder. |
| **Expected behavior** | German placeholder to match app language. |
| **Actual behavior** | `source_list_panel.py`: `setPlaceholderText("Enter your note text...")` (EN). |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `app.ui.knowledge.source_list_panel` |
| **Type** | UX inconsistency |

---

### D30: Settings Advanced Category Mixed Language

| Field | Value |
|-------|-------|
| **Defect ID** | D30 |
| **Title** | Settings Advanced category mixes "Developer Settings", "Experimental" (EN) with "Noch nicht" (DE) |
| **Reproduction steps** | 1. Open Settings → Advanced. 2. Inspect section labels. |
| **Expected behavior** | Consistent language. |
| **Actual behavior** | "Developer Settings", "Debug Panel", "Experimental Features (noch nicht verfügbar)" – mixed EN/DE. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `advanced_category.py`, `advanced_workspace.py` |
| **Type** | UX inconsistency |

---

### D8: Settings Project/Workspace Categories – Placeholder (Existing, Confirmed)

| Field | Value |
|-------|-------|
| **Defect ID** | D8 |
| **Title** | Settings Project and Workspace categories are placeholders |
| **Reproduction steps** | 1. Open Settings → Project. 2. Open Settings → Workspace. |
| **Expected behavior** | Functional settings or clear "Not yet available". |
| **Actual behavior** | EmptyStateWidget: "Dieser Bereich wird in einer zukünftigen Version erweitert." |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `ProjectCategory`, `WorkspaceCategory` |
| **Type** | Placeholder |

---

### D31: app.ui.agents.AgentWorkspace Has Placeholder Panels – Possibly Dead Code

| Field | Value |
|-------|-------|
| **Defect ID** | D31 |
| **Title** | app.ui.agents.AgentWorkspace uses _placeholder_widget for Library, Runs, Activity, Skills |
| **Reproduction steps** | 1. Determine where app.ui.agents.AgentWorkspace is used. 2. If used, inspect Library, Runs, Activity, Skills panels. |
| **Expected behavior** | Functional panels or clear "Coming soon". |
| **Actual behavior** | `agent_workspace.py` uses `_placeholder_widget(title, message)` for these sections. Control Center uses `app.gui.domains.control_center.workspaces.agents_workspace` (different implementation). app.ui.agents may be legacy; if still reachable, shows placeholders. |
| **Severity** | Minor |
| **Confidence** | Medium |
| **Likely subsystem** | `app.ui.agents.agent_workspace` |
| **Type** | Placeholder |

---

### D32: Dock Titles in English

| Field | Value |
|-------|-------|
| **Defect ID** | D32 |
| **Title** | Dock widgets use English titles: "Navigation", "Inspector", "Monitor" |
| **Reproduction steps** | 1. Inspect dock widget titles. |
| **Expected behavior** | Consistent with app language (DE). |
| **Actual behavior** | `docking_config.py`: "Navigation", "Inspector", "Monitor". Rest of UI often German. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `docking_config.py` |
| **Type** | UX inconsistency |

---

### D33: Bottom Panel Tab Labels in English

| Field | Value |
|-------|-------|
| **Defect ID** | D33 |
| **Title** | Bottom Panel tabs: "Logs", "Events", "Metrics", "Agent Activity", "LLM Trace" – all English |
| **Reproduction steps** | 1. Open Bottom Panel. 2. Inspect tab labels. |
| **Expected behavior** | Consistent with app language. |
| **Actual behavior** | All English. Sidebar and many panels use German. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `bottom_panel_host.py` |
| **Type** | UX inconsistency |

---

## Cosmetic Defects

### D34: Widespread Hardcoded Theme Colors – Dark Theme Inconsistency

| Field | Value |
|-------|-------|
| **Defect ID** | D34 |
| **Title** | Many panels use hardcoded #f1f5f9, #e2e8f0, #334155, background: white |
| **Reproduction steps** | 1. Switch to Dark theme (Command Palette → Switch Theme). 2. Open Control Center, QA & Governance, Knowledge, Chat, Settings. 3. Inspect panel backgrounds and borders. |
| **Expected behavior** | All panels adapt to dark theme. |
| **Actual behavior** | `agents_panels.py`, `tools_panels.py`, `data_stores_panels.py`, `models_panels.py`, `providers_panels.py`, `test_inventory_panels.py`, `session_explorer_panel.py`, `library_panel.py`, `chat_navigation_panel.py`, `source_details_panel.py`, `project_hub_page.py`, and many others use inline `background: white`, `#e2e8f0`, `#f1f5f9`, `#334155`. Dark theme will show light panels on dark background. |
| **Severity** | Cosmetic |
| **Confidence** | High |
| **Likely subsystem** | Multiple panel files |
| **Type** | Theme issue |

---

### D35: Control Center, QA Workspace Host Hardcoded Background

| Field | Value |
|-------|-------|
| **Defect ID** | D35 |
| **Title** | Control Center and QA Governance workspace hosts use hardcoded #f1f5f9 |
| **Reproduction steps** | 1. Switch to Dark theme. 2. Open Control Center. 3. Open QA & Governance. |
| **Expected behavior** | Theme-consistent background. |
| **Actual behavior** | `control_center_screen.py`: `#controlCenterWorkspaceHost { background: #f1f5f9; }`. `qa_governance_screen.py`: `#qaGovernanceWorkspaceHost { background: #f1f5f9; }`. |
| **Severity** | Cosmetic |
| **Confidence** | High |
| **Likely subsystem** | `control_center_screen.py`, `qa_governance_screen.py` |
| **Type** | Theme issue |

---

### D36: Navigation Sidebar Hardcoded Colors

| Field | Value |
|-------|-------|
| **Defect ID** | D36 |
| **Title** | NavigationSidebar uses hardcoded #f8fafc, #e2e8f0, #3b82f6 |
| **Reproduction steps** | 1. Switch to Dark theme. 2. Inspect Sidebar. |
| **Expected behavior** | Theme-consistent. |
| **Actual behavior** | `sidebar.py` _sidebar_stylesheet: `background: #f8fafc`, `#e2e8f0`, `#3b82f6` (selected). |
| **Severity** | Cosmetic |
| **Confidence** | High |
| **Likely subsystem** | `navigation/sidebar.py` |
| **Type** | Theme issue |

---

### D20: Command Palette Placeholder Mixed Language (Existing, Confirmed)

| Field | Value |
|-------|-------|
| **Defect ID** | D20 |
| **Title** | Command Palette search "Befehl eingeben..." (DE) vs command titles "Open Dashboard" (EN) |
| **Reproduction steps** | 1. Open Command Palette. 2. Inspect placeholder and command list. |
| **Expected behavior** | Consistent language. |
| **Actual behavior** | Placeholder DE, commands EN. |
| **Severity** | Cosmetic |
| **Confidence** | High |
| **Likely subsystem** | `CommandPaletteDialog` |
| **Type** | UX inconsistency |

---

### D21: Breadcrumb "Active Project" Fallback in English (Existing, Confirmed)

| Field | Value |
|-------|-------|
| **Defect ID** | D21 |
| **Title** | BreadcrumbManager fallback "Active Project" is English |
| **Reproduction steps** | 1. Open Command Center with no project. 2. Inspect breadcrumb. |
| **Expected behavior** | German fallback. |
| **Actual behavior** | "Active Project" (EN). |
| **Severity** | Cosmetic |
| **Confidence** | High |
| **Likely subsystem** | `BreadcrumbManager` |
| **Type** | UX inconsistency |

---

### D22: Qt D-Bus Portal Warning on Startup (Existing, Confirmed)

| Field | Value |
|-------|-------|
| **Defect ID** | D22 |
| **Title** | Qt D-Bus portal warning on application startup |
| **Reproduction steps** | 1. Run `python main.py`. 2. Observe console. |
| **Expected behavior** | Clean startup or suppressed warning. |
| **Actual behavior** | `qt.qpa.services: Failed to register with host portal QDBusError(...)`. Non-fatal. |
| **Severity** | Cosmetic |
| **Confidence** | High |
| **Likely subsystem** | Qt platform |
| **Type** | Visual/layout issue |

---

## Coverage Summary

### Areas Inspected

| Area | Inspected | Notes |
|------|-----------|-------|
| **Global Shell** | ✓ | TopBar, Sidebar, Breadcrumbs, Command Palette, Inspector, Docks |
| **Operations** | ✓ | Chat, Knowledge, Prompt Studio, Agent Tasks, Projects |
| **Control Center** | ✓ | Models, Providers, Agents, Tools, Data Stores |
| **QA & Governance** | ✓ | Test Inventory, Coverage, Incidents, Replay, Gaps |
| **Runtime / Debug** | ✓ | EventBus, Logs, LLM Calls, Agent Activity, Metrics, System Graph |
| **Settings** | ✓ | All 8 categories |
| **Project Hub** | ✓ | |
| **Command Center** | ✓ | |
| **Bottom Panel** | ✓ | Logs, Events, Metrics, Agent Activity, LLM Trace |
| **Navigation** | ✓ | Sidebar, sub-navs, breadcrumbs, Command Palette |
| **Inspector** | ✓ | setup_inspector flow, content_token, area-level switching |
| **Theme** | ✓ | Hardcoded colors, light/dark tokens |
| **Language** | ✓ | Mixed DE/EN across panels |

### Newly Discovered Areas

| Area | Notes |
|------|-------|
| **WorkspaceHost area-level inspector flow** | Not in first audit; D24 documents missing content_token at area switch. |
| **D13 regression test gap** | First audit did not note that test does not verify D13 fix. |
| **Control Center dummy data** | First audit noted "functional (dummy)"; D26/D27 clarify misleading nature. |
| **app.ui.agents vs gui.domains.control_center** | Two different Agent implementations; app.ui.agents has placeholders. |
| **Dock and Bottom Panel labels** | D32, D33 – language consistency. |

---

## Verification Items (No Defect Observed)

| ID | Scenario | Result |
|----|----------|--------|
| V1 | Sidebar passes workspace_id to show_area | ✓ MainWindow forwards (area_id, workspace_id) correctly. |
| V2 | Breadcrumb click navigates | ✓ BreadcrumbBar emits navigate_requested; MainWindow calls show_area. |
| V3 | Bottom Panel tabs functional | ✓ All 5 tabs (Logs, Events, Metrics, Agent Activity, LLM Trace) have real monitors. |
| V4 | QA & Governance workspaces functional | ✓ All use QAGovernanceService; no placeholders. |
| V5 | Runtime/Debug workspaces functional | ✓ All use DebugStore or live data. |
| V6 | Project Hub and Command Center functional | ✓ No placeholders. |
| V7 | D13 fix – PromptStudioWorkspace accepts content_token | ✓ Code verified; manual testing recommended. |
| V8 | Operations workspace switching with InspectorHost | ✓ OperationsScreen uses content_token; D13 fix applied. |

---

## Recommended Fix Priority

1. **Critical:** Add `prepare_for_setup` and `content_token` to WorkspaceHost._on_current_changed (D24). Prevents stale inspector on area switch.
2. **Major:** Add D13 regression test with InspectorHost connected (D25). Add Agents and System Graph to Sidebar (D12, D14). Extend Command Palette with Knowledge, Prompt Studio, Agent Tasks, Control Center sub-workspaces (D15).
3. **Minor:** Add content_token to ControlCenterScreen, QAGovernanceScreen, RuntimeDebugScreen (D9). Align Breadcrumb labels (D7). Add "Demo data" indication to Control Center Agents/Tools/Data Stores (D26). Fix Agent Inspector selection binding (D27). Unify language in agent editor, knowledge, settings (D28–D30).
4. **Cosmetic:** Replace hardcoded colors with theme tokens (D34–D36). Unify Command Palette and Breadcrumb language (D20, D21). Localize dock and bottom panel labels (D32, D33).

---

## Test Artifacts

- `tests/behavior/ux_behavior_simulation.py` – Workspace switching; **does not** set inspector_host (D25).
- `tests/behavior/ux_regression_tests.py` – D6, D7, D9, D1, V1.
- `tests/smoke/test_shell_gui.py` – Shell startup, areas.

---

*This report documents defects identified through the second full behavior-first audit. Manual GUI testing is recommended to confirm findings, especially D24 (area-level stale inspector) and D13 (Prompt Studio with InspectorHost).*
