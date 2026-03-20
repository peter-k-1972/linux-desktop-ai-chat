# Final Pre-Release UX Kill Sweep – Defect Report

**Version:** 1.0  
**Date:** 2026-03-16  
**Scope:** Final destructive UX and behavior audit before release  
**Method:** Destructive workflow simulation, inspector stability testing, context menu audit, keyboard/resize/theme checks  
**Reference:** [UX_DEFECTS_BEHAVIOR_AUDIT_2_2026-03-16.md](UX_DEFECTS_BEHAVIOR_AUDIT_2_2026-03-16.md) (second audit D24–D36)

---

## Executive Summary

This final kill sweep identified **1 Critical**, **5 Major**, **12 Minor**, and **7 Cosmetic** defects. Several are **new** from destructive testing. The application **survived** chaotic workspace/project switching without crash. Key remaining risks:

- **WorkspaceHost area-level inspector** – no `content_token`; stale content on rapid area switch (D24).
- **Knowledge source list items** – no context menu; inconsistent with Chat, Prompts (D37).
- **No explicit tab order or focus policy** – keyboard navigation may be suboptimal (D38).
- **Command Palette** – many workspaces unreachable (D15).
- **Inspector dock closed** – setup_inspector still runs; no crash, but no handling for "Inspector hidden" state (D39).

---

## Summary by Severity

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Major | 5 |
| Minor | 12 |
| Cosmetic | 7 |

---

## Defects by Severity

### Critical

#### D24: WorkspaceHost Area Switch Does Not Use content_token – Stale Inspector Risk

| Field | Value |
|-------|-------|
| **Defect ID** | D24 |
| **Title** | Inspector can show stale content when switching areas rapidly |
| **Reproduction steps** | 1. Open Operations → Chat, select a chat. 2. Quickly switch: Control Center → Settings → Operations → QA & Governance → Runtime. 3. Observe Inspector. |
| **Expected behaviour** | Inspector always shows content for the current area/workspace. |
| **Actual behaviour** | `WorkspaceHost._on_current_changed` calls `widget.setup_inspector(self._inspector_host)` without `prepare_for_setup()` or `content_token`. No token-based staleness guard at area level. |
| **Severity** | Critical |
| **Confidence** | High |
| **Likely subsystem** | `WorkspaceHost`, `InspectorHost` |
| **Defect type** | Bug |

---

### Major

#### D12: Sidebar SYSTEM Section Missing Agents

| Field | Value |
|-------|-------|
| **Defect ID** | D12 |
| **Title** | Sidebar SYSTEM missing Agents |
| **Reproduction steps** | 1. Open Sidebar. 2. Expand SYSTEM. |
| **Expected behaviour** | Models, Providers, **Agents**, Tools, Data Stores. |
| **Actual behaviour** | Agents (cc_agents) not in Sidebar; must open Control Center first. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `sidebar_config.py` |
| **Defect type** | Navigation gap |

---

#### D14: Sidebar OBSERVABILITY Section Missing System Graph

| Field | Value |
|-------|-------|
| **Defect ID** | D14 |
| **Title** | Sidebar OBSERVABILITY missing System Graph |
| **Reproduction steps** | 1. Open Sidebar. 2. Expand OBSERVABILITY. |
| **Expected behaviour** | Runtime, Logs, LLM Calls, Agent Activity, Metrics, **System Graph**. |
| **Actual behaviour** | System Graph (rd_system_graph) not in Sidebar. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `sidebar_config.py` |
| **Defect type** | Navigation gap |

---

#### D15: Command Palette Missing Workspace-Specific Commands

| Field | Value |
|-------|-------|
| **Defect ID** | D15 |
| **Title** | Command Palette does not offer Knowledge, Prompt Studio, Agent Tasks, Control Center sub-workspaces |
| **Reproduction steps** | 1. Open Command Palette (Ctrl+Shift+P). 2. Search "Knowledge", "Prompt Studio", "Agents", "Models", "System Graph". |
| **Expected behaviour** | Commands exist and open correct workspace. |
| **Actual behaviour** | Only: Dashboard, Projects, Chat, Control Center, QA & Governance, Runtime/Debug, Settings, Switch Theme, Reload Theme. No Knowledge, Prompt Studio, Agent Tasks, cc_models, cc_agents, rd_system_graph, etc. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `app.gui.commands.bootstrap` |
| **Defect type** | UX inconsistency |

---

#### D25: D13 Fix Not Verified by Automated Tests

| Field | Value |
|-------|-------|
| **Defect ID** | D25 |
| **Title** | test_workspace_switch_order_no_crash does not exercise Prompt Studio with InspectorHost |
| **Reproduction steps** | 1. Inspect test. 2. Note no `set_inspector_host()` call. |
| **Expected behaviour** | Test verifies D13 fix (Prompt Studio setup_inspector with content_token). |
| **Actual behaviour** | Test never sets inspector_host; D13 crash path never exercised. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `tests/behavior/ux_behavior_simulation.py` |
| **Defect type** | Regression |

---

#### D37: Knowledge Source List Items Have No Context Menu (NEW)

| Field | Value |
|-------|-------|
| **Defect ID** | D37 |
| **Title** | Knowledge source list items lack context menu |
| **Reproduction steps** | 1. Open Knowledge. 2. Select a project. 3. Right-click a source item. |
| **Expected behaviour** | Context menu with actions (e.g. Delete, Reindex, Open). |
| **Actual behaviour** | No context menu. Chat items and Prompt library items have context menus; Knowledge source items do not. |
| **Severity** | Major |
| **Confidence** | High |
| **Likely subsystem** | `app.gui.domains.operations.knowledge.panels.source_list_item` |
| **Defect type** | UX inconsistency |

---

### Minor

#### D9: Control Center, QA, Runtime/Debug Do Not Use content_token

| Field | Value |
|-------|-------|
| **Defect ID** | D9 |
| **Title** | Sub-workspace switching in Control Center, QA, Runtime/Debug lacks content_token |
| **Reproduction steps** | 1. Open Control Center. 2. Rapidly switch Models → Providers → Agents → Tools. 3. Observe Inspector. |
| **Expected behaviour** | Inspector always matches current workspace. |
| **Actual behaviour** | Only OperationsScreen uses content_token. ControlCenterScreen, QAGovernanceScreen, RuntimeDebugScreen do not. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `ControlCenterScreen`, `QAGovernanceScreen`, `RuntimeDebugScreen` |
| **Defect type** | Bug |

---

#### D26: Control Center Agents, Tools, Data Stores Use Dummy Data

| Field | Value |
|-------|-------|
| **Defect ID** | D26 |
| **Title** | Control Center displays hardcoded dummy data without indication |
| **Reproduction steps** | 1. Open Control Center → Agents, Tools, Data Stores. |
| **Expected behaviour** | Real data or clear "Demo data" label. |
| **Actual behaviour** | Hardcoded tables; no indication data is fake. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `agents_panels.py`, `tools_panels.py`, `data_stores_panels.py` |
| **Defect type** | Placeholder |

---

#### D27: Control Center Agents Inspector Always Shows "Research Agent"

| Field | Value |
|-------|-------|
| **Defect ID** | D27 |
| **Title** | Agents Inspector not bound to table selection |
| **Reproduction steps** | 1. Open Control Center → Agents. 2. Click different rows. |
| **Expected behaviour** | Inspector reflects selected agent. |
| **Actual behaviour** | Inspector always shows hardcoded "Research Agent". |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `agents_workspace.py` |
| **Defect type** | Unimplemented widget |

---

#### D7: Breadcrumb vs Sidebar/Operations Label Mismatch

| Field | Value |
|-------|-------|
| **Defect ID** | D7 |
| **Title** | Breadcrumb "Agents", "Project Overview" vs Sidebar "Agent Tasks", "Projekte" |
| **Reproduction steps** | 1. Open Operations → Agent Tasks. 2. Compare Breadcrumb and Sidebar. |
| **Expected behaviour** | Consistent labels. |
| **Actual behaviour** | Mixed EN/DE, different terms. |
| **Severity** | Minor |
| **Confidence** | High |
| **Likely subsystem** | `BreadcrumbManager.WORKSPACE_INFO` |
| **Defect type** | UX inconsistency |

---

#### D38: No Explicit Tab Order or Focus Policy (NEW)

| Field | Value |
|-------|-------|
| **Defect ID** | D38 |
| **Title** | No setTabOrder or focus policy; keyboard navigation may be suboptimal |
| **Reproduction steps** | 1. Tab through Chat workspace. 2. Tab through Settings. 3. Observe focus flow. |
| **Expected behaviour** | Logical tab order; no focus traps. |
| **Actual behaviour** | No `setTabOrder` or `setFocusPolicy` found. Qt default (creation order) used. May work but not verified. |
| **Severity** | Minor |
| **Confidence** | Medium |
| **Likely subsystem** | Multiple workspaces |
| **Defect type** | UX inconsistency |

---

#### D39: Inspector Dock Closed – No Special Handling (NEW)

| Field | Value |
|-------|-------|
| **Defect ID** | D39 |
| **Title** | When Inspector dock is closed, setup_inspector still runs on hidden widget |
| **Reproduction steps** | 1. Close Inspector dock. 2. Switch workspaces repeatedly. 3. Reopen Inspector. |
| **Expected behaviour** | Inspector shows correct content when reopened. |
| **Actual behaviour** | setup_inspector runs; content is set on hidden widget. On reopen, content is correct. No crash. But no optimization to skip setup when Inspector is hidden. |
| **Severity** | Minor |
| **Confidence** | Low |
| **Likely subsystem** | `WorkspaceHost`, `InspectorHost` |
| **Defect type** | State synchronization issue |

---

#### D8, D28–D33: Settings Placeholders, Mixed Language, Dock Labels

(Summarized from prior audits: D8 placeholder categories; D28–D30 mixed DE/EN; D32–D33 dock/bottom panel labels in English.)

---

### Cosmetic

#### D34–D36: Hardcoded Theme Colors

(Summarized: Many panels use #f1f5f9, #e2e8f0, background: white; dark theme inconsistent.)

---

#### D20, D21, D22: Command Palette/Breadcrumb Language, D-Bus Warning

(Summarized from prior audits.)

---

## Verified Stable Areas

The following areas **passed** destructive testing and appear stable:

| Area | Test | Result |
|------|------|--------|
| **Rapid workspace switching** | Chat → Knowledge → Prompt Studio → Chat → Agents → Projects → Chat | No crash |
| **Rapid project switching** | Project A → Chat, Project B → Knowledge, Project A → Prompt Studio, etc. | No crash |
| **Combined chaos** | Workspace + project switching in mixed order | No crash |
| **Chat delete selection** | `_on_chat_deleted` clears current chat, selects first remaining, refreshes inspector | Correct |
| **Project context change** | `_on_project_context_changed` clears workspace, restores last selection | Correct |
| **Command Palette execution** | Commands call `show_area`; breadcrumb_changed emitted; sidebar updated | Correct |
| **Command Palette keyboard** | Escape closes; Down/Up between search and list; Enter executes | Works |
| **Inspector dock closed** | setup_inspector runs; no crash; content correct on reopen | Works |
| **Prompt Studio** | D13 fix applied; setup_inspector accepts content_token | Fixed |
| **Chat context menus** | Chat items (via ChatNavigationPanel) have context menu | Present |
| **Prompt library context menu** | Prompt items have context menu | Present |
| **Collection context menu** | Collection items have context menu | Present |

---

## Context Menu Coverage

| Component | Context Menu | Notes |
|-----------|--------------|-------|
| Chat items | ✓ | Via ChatNavigationPanel, build_chat_item_context_menu |
| Chat topics | ✓ | Header and item context menus |
| Prompt library items | ✓ | _show_context_menu in library_panel |
| Prompt templates | ✓ | _show_context_menu |
| Collection items | ✓ | setContextMenuPolicy, _show_context_menu |
| **Knowledge source items** | ✗ | **Missing** |
| Models list | ✗ | Not checked |
| Agent Registry table | ✗ | Not checked |
| Logs / Events | ✗ | Not checked |
| Project switcher | ✓ | Dropdown menu |

---

## Command Palette Kill Test Results

| Search Term | Command Exists | Opens Correct Workspace |
|-------------|----------------|-------------------------|
| Chat | ✓ nav.chat | ✓ operations_chat |
| Projects | ✓ nav.projects | ✓ operations_projects |
| Dashboard | ✓ nav.dashboard | ✓ command_center |
| Control Center | ✓ nav.control_center | ✓ (default cc_models) |
| Settings | ✓ nav.settings | ✓ (last category) |
| Knowledge | ✗ | — |
| Prompt Studio | ✗ | — |
| Agent Tasks | ✗ | — |
| Models | ✗ | — |
| Providers | ✗ | — |
| Agents | ✗ | — |
| Tools | ✗ | — |
| Data Stores | ✗ | — |
| Runtime | ✓ nav.runtime_debug | ✓ (default rd_eventbus) |
| Logs | ✗ | — |
| Metrics | ✗ | — |
| System Graph | ✗ | — |

---

## Window Resize Notes

- **Minimum size:** 1000×700 (setMinimumSize). Prevents very narrow/short window.
- **No resizeEvent handlers** in main window or workspaces.
- **Dock constraints:** NAV_SIDEBAR 180–320px, INSPECTOR 200–400px, BOTTOM 120–400px.
- **Risk:** At 1000×700 with all docks open, central workspace may be cramped. Not verified.

---

## Recommended Fix Priority (Pre-Release)

1. **Critical:** D24 – Add `prepare_for_setup` and `content_token` to WorkspaceHost._on_current_changed.
2. **Major:** D37 – Add context menu to Knowledge source list items.
3. **Major:** D25 – Add regression test for D13 with InspectorHost connected.
4. **Major:** D12, D14 – Add Agents and System Graph to Sidebar.
5. **Major:** D15 – Extend Command Palette with missing workspace commands.
6. **Minor:** D9 – Add content_token to Control Center, QA, Runtime screens.
7. **Minor:** D38 – Audit and set tab order where needed.
8. **Cosmetic:** D34–D36 – Replace hardcoded colors with theme tokens.

---

## Test Artifacts

- Destructive workflow: `python -c "..."` (manual run) – passed.
- `tests/behavior/ux_behavior_simulation.py` – workspace switch (no inspector_host).
- `tests/behavior/ux_regression_tests.py` – D6, D7, D9, D1, V1.

---

*This report documents the final pre-release UX kill sweep. The application survived destructive workflow testing. Remaining defects are documented above. Manual GUI verification recommended before release.*
