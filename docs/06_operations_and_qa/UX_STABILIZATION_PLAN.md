# UX Stabilization Plan – Linux Desktop Chat

**Version:** 1.0  
**Date:** 2026-03-16  
**Author:** Senior Software Architect / UX Stabilization Engineer  
**Scope:** Structured strategy for resolving UX defects identified across four audit reports  
**Status:** Strategy only – no implementation

---

## 1. Defect Classification

Defects are grouped by subsystem and category. Resolved defects (D1–D6, D11, D13) are excluded.

### 1.1 Inspector / Workspace State

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D24** | WorkspaceHost area switch does not use content_token | WorkspaceHost, InspectorHost |
| **D9** | Control Center, QA, Runtime/Debug do not use content_token | ControlCenterScreen, QAGovernanceScreen, RuntimeDebugScreen |
| **D39** | Inspector dock closed – setup_inspector still runs | WorkspaceHost, InspectorHost |
| **D27** | Agents Inspector always shows "Research Agent" | agents_workspace, agent_inspector |

**Dependency:** D24 and D9 share the same root cause (missing token-based staleness guard). D24 is area-level; D9 is sub-workspace-level. Fixing D24 requires WorkspaceHost to pass `content_token`; screens must accept it. D9 requires screens to pass `content_token` to their workspace widgets.

---

### 1.2 Navigation Architecture

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D12** | Sidebar SYSTEM missing Agents | sidebar_config.py |
| **D14** | Sidebar OBSERVABILITY missing System Graph | sidebar_config.py |
| **D10** | Project Hub vs Projects vs Dashboard overlap | sidebar_config.py, tooltips |

**Dependency:** D12 and D14 are independent; both are config-only changes in `sidebar_config.py`. D10 is a naming/clarity issue; may require tooltip refinement or label changes.

---

### 1.3 Command Palette

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D15** | Command Palette missing Knowledge, Prompt Studio, Agent Tasks, Control Center sub-workspaces | commands/bootstrap.py |
| **D20** | Command Palette placeholder DE vs command titles EN | CommandPaletteDialog, commands |

**Dependency:** D15 is additive (new commands); D20 is cosmetic. No dependency between them.

---

### 1.4 Context Menus

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D37** | Knowledge source list items have no context menu | source_list_item.py, knowledge_source_explorer_panel |

**Dependency:** Isolated. No other defects depend on D37.

---

### 1.5 Theme System

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D34** | Widespread hardcoded #f1f5f9, #e2e8f0, background: white | Multiple panel files |
| **D35** | Control Center, QA workspace host hardcoded #f1f5f9 | control_center_screen, qa_governance_screen |
| **D36** | Navigation Sidebar hardcoded colors | sidebar.py |
| **D23** | Control Center workspace host hardcoded background | control_center_screen (overlaps D35) |

**Dependency:** D34 is the umbrella; D35, D36, D23 are specific instances. All require replacing hardcoded colors with theme tokens from `ThemeManager` or `tokens.py`.

---

### 1.6 Language Consistency

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D7** | Breadcrumb vs Sidebar/Operations label mismatch | BreadcrumbManager.WORKSPACE_INFO |
| **D16** | Mixed DE/EN in empty states | EmptyStateWidget usages, agent_activity_panel, etc. |
| **D19** | Inspector default content German only | InspectorHost |
| **D20** | Command Palette placeholder vs titles | CommandPaletteDialog |
| **D21** | Breadcrumb "Active Project" fallback English | BreadcrumbManager |
| **D28** | Agent editor mixed language | agent_editor_panel |
| **D29** | Knowledge source "Enter your note text..." | source_list_panel |
| **D30** | Settings Advanced mixed language | advanced_category, advanced_workspace |
| **D32** | Dock titles English | docking_config.py |
| **D33** | Bottom Panel tabs English | bottom_panel_host.py |

**Dependency:** All are independent label/string changes. Decision needed: standardize on DE or EN.

---

### 1.7 Placeholder Panels

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D8** | Settings Project/Workspace placeholder | ProjectCategory, WorkspaceCategory |
| **D17** | Settings "In Entwicklung" placeholders | application, ai_models, data, privacy, advanced |
| **D18** | Control Center Agents placeholder sections | app.ui.agents (possibly legacy) |
| **D26** | Control Center Agents, Tools, Data Stores dummy data | agents_panels, tools_panels, data_stores_panels |
| **D31** | app.ui.agents.AgentWorkspace placeholder panels | app.ui.agents.agent_workspace |

**Dependency:** D26 and D27 relate to Control Center Agents. D26 is "add Demo data label"; D27 is "bind Inspector to selection". D8, D17, D18, D31 are documentation or "coming soon" clarity.

---

### 1.8 Keyboard Navigation

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D38** | No explicit tab order or focus policy | Multiple workspaces |

**Dependency:** Isolated. Requires audit of tab order; may touch many files.

---

### 1.9 Tests / Regression Coverage

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D25** | D13 fix not verified by automated tests | tests/behavior/ux_behavior_simulation.py |

**Dependency:** Should be fixed early to prevent regressions when implementing D24, D9.

---

### 1.10 Cosmetic / Other

| Defect | Title | Subsystem |
|--------|-------|-----------|
| **D22** | Qt D-Bus portal warning on startup | Qt platform |

**Dependency:** Isolated. May require Qt/env configuration; low priority.

---

## 2. Architectural Fixes

### 2.1 WorkspaceHost Inspector Token Handling (D24)

| Field | Value |
|-------|-------|
| **Root cause** | `WorkspaceHost._on_current_changed` calls `widget.setup_inspector(self._inspector_host)` without `prepare_for_setup()` or `content_token`. When switching areas rapidly (Operations → Control Center → Settings), async or delayed `setup_inspector` calls can complete out of order, leaving stale content in the Inspector. |
| **Proposed change** | 1. In `_on_current_changed`, call `content_token = self._inspector_host.prepare_for_setup()` before delegating. 2. Call `widget.setup_inspector(self._inspector_host, content_token=content_token)`. 3. All screens with `setup_inspector` must accept `content_token: int | None = None` and pass it to workspace widgets or `inspector_host.set_content()`. |
| **Files affected** | `app/gui/workspace/workspace_host.py`, `app/gui/domains/control_center/control_center_screen.py`, `app/gui/domains/qa_governance/qa_governance_screen.py`, `app/gui/domains/runtime_debug/runtime_debug_screen.py`, `app/gui/domains/settings/settings_screen.py`, `app/gui/domains/dashboard/dashboard_screen.py` (if exists), `app/gui/domains/project_hub/project_hub_screen.py` (if exists). Plus all workspace widgets that call `inspector_host.set_content()` – Control Center workspaces, QA workspaces, Runtime workspaces. |
| **Risk level** | **High.** Many files; signature change propagates. Must ensure all `setup_inspector` implementations accept `content_token` (optional). Backward compatibility: `content_token=None` should behave as today. |

---

### 2.2 Screen-Level content_token Propagation (D9)

| Field | Value |
|-------|-------|
| **Root cause** | `ControlCenterScreen`, `QAGovernanceScreen`, `RuntimeDebugScreen` call `widget.setup_inspector(self._inspector_host)` without token. Their workspace widgets do not pass `content_token` to `inspector_host.set_content()`. |
| **Proposed change** | 1. Each screen's `_on_workspace_changed` calls `content_token = self._inspector_host.prepare_for_setup()`. 2. Pass `content_token` to `widget.setup_inspector(self._inspector_host, content_token=content_token)`. 3. Each workspace widget's `setup_inspector` accepts `content_token` and passes it to `inspector_host.set_content(widget, content_token=content_token)`. |
| **Files affected** | Control Center: `control_center_screen.py`, `models_workspace.py`, `providers_workspace.py`, `agents_workspace.py`, `tools_workspace.py`, `data_stores_workspace.py`, `base_management_workspace.py`. QA: `qa_governance_screen.py`, all qa workspaces, `base_analysis_workspace.py`. Runtime: `runtime_debug_screen.py`, all rd workspaces, `base_monitoring_workspace.py`. |
| **Risk level** | **Medium.** Pattern already exists in OperationsScreen; replication is straightforward. Must not break workspaces that call `clear_content()` instead of `set_content()`. |

---

### 2.3 Command Palette Command Registry (D15)

| Field | Value |
|-------|-------|
| **Root cause** | `register_commands()` only registers area-level navigation (Dashboard, Projects, Chat, Control Center, QA, Runtime, Settings). No workspace-specific commands for Knowledge, Prompt Studio, Agent Tasks, or Control Center sub-workspaces (Models, Providers, Agents, Tools, Data Stores), or Runtime sub-workspaces (e.g. System Graph). |
| **Proposed change** | Extend `register_commands()` to add commands that call `workspace_host.show_area(area_id, workspace_id)` for each missing workspace. Use a data-driven approach: define a list of (id, title, description, area_id, workspace_id) and register in a loop. Ensures Command Palette stays in sync with Sidebar. |
| **Files affected** | `app/gui/commands/bootstrap.py`. Optionally: introduce a `NAV_COMMANDS` config that both Sidebar and Command Palette consume. |
| **Risk level** | **Low.** Additive only; no changes to existing commands. |

---

### 2.4 Theme Token System (D34, D35, D36, D23)

| Field | Value |
|-------|-------|
| **Root cause** | Many panels use inline `setStyleSheet()` or `_cc_panel_style()` with hardcoded hex colors (`#f1f5f9`, `#e2e8f0`, `#334155`, `background: white`). ThemeManager provides tokens, but panels do not use them. |
| **Proposed change** | 1. Define a shared `get_panel_style()` (or similar) that reads from `ThemeManager.get_tokens()` and returns a stylesheet string. 2. Replace hardcoded colors in panels with token references. 3. Ensure panels re-apply styles on theme change (ThemeManager may need to emit a signal). |
| **Files affected** | `app/gui/themes/`, `app/gui/domains/control_center/panels/*.py`, `app/gui/domains/qa_governance/panels/*.py`, `app/gui/domains/runtime_debug/panels/*.py`, `app/gui/navigation/sidebar.py`, `app/gui/domains/control_center/control_center_screen.py`, `app/gui/domains/qa_governance/qa_governance_screen.py`, and many others. |
| **Risk level** | **Medium–High.** Many files; risk of missing a panel or breaking layout. Should be done incrementally, starting with high-visibility areas (Sidebar, Control Center host). |

---

## 3. Low-Risk Fixes

These fixes are isolated and unlikely to cause regressions.

| Defect | Fix | Files | Risk |
|--------|-----|-------|------|
| **D12** | Add `NavItem` for cc_agents to SYSTEM section in `get_sidebar_sections()` | sidebar_config.py | Low |
| **D14** | Add `NavItem` for rd_system_graph to OBSERVABILITY section | sidebar_config.py | Low |
| **D37** | Add `setContextMenuPolicy(CustomContextMenu)` and `customContextMenuRequested` to SourceListItemWidget; implement `_show_context_menu` with Delete, Reindex (or similar) | source_list_item.py, knowledge_source_explorer_panel | Low |
| **D7** | Update `WORKSPACE_INFO` in BreadcrumbManager: "Project Overview" → "Projekte", "Agents" → "Agent Tasks" | breadcrumbs/manager.py | Low |
| **D21** | Change "Active Project" → "Aktives Projekt" (or chosen language) | breadcrumbs/manager.py | Low |
| **D26** | Add a small "Demo-Daten" or "Beispieldaten" label above/below Control Center Agents, Tools, Data Stores tables | agents_panels.py, tools_panels.py, data_stores_panels.py | Low |
| **D32** | Change dock titles to "Navigation", "Inspector", "Monitor" → German equivalents if app is DE | docking_config.py | Low |
| **D33** | Change Bottom Panel tab labels to German if app is DE | bottom_panel_host.py | Low |
| **D29** | Change "Enter your note text..." → "Notiztext eingeben..." | source_list_panel.py | Low |
| **D28** | Unify agent_editor_panel placeholders to one language | agent_editor_panel.py | Low |
| **D30** | Unify advanced_category/advanced_workspace labels | advanced_category.py, advanced_workspace.py | Low |
| **D20** | Unify Command Palette: either all DE or all EN for placeholder and command titles | CommandPaletteDialog, commands/bootstrap | Low |
| **D10** | Refine tooltips for Projektübersicht, Systemübersicht, Projekte (already present; optionally clarify labels) | sidebar_config.py | Low |

---

## 4. Fix Phases

### Phase 1 — Critical Architecture Fixes

| Target | Defects | Modules | Risk |
|--------|---------|---------|------|
| WorkspaceHost content_token | D24 | workspace_host.py | High |
| Screen setup_inspector signature | D24, D9 | All screens with setup_inspector | High |
| Workspace widget content_token | D9 | Control Center, QA, Runtime workspace widgets | Medium |

**Order:** 1) Add regression test (D25) first to lock D13 behavior. 2) Update WorkspaceHost. 3) Update screens and workspace widgets to accept and pass content_token. 4) Run full test suite.

---

### Phase 2 — Navigation Completeness

| Target | Defects | Modules | Risk |
|--------|---------|---------|------|
| Sidebar entries | D12, D14 | sidebar_config.py | Low |
| Command Palette commands | D15 | commands/bootstrap.py | Low |

**Order:** 1) Add Sidebar entries. 2) Add Command Palette commands. 3) Verify both Sidebar and Command Palette open correct workspaces.

---

### Phase 3 — Inspector / State Synchronization

| Target | Defects | Modules | Risk |
|--------|---------|---------|------|
| Agents Inspector selection | D27 | agents_workspace.py, agent_inspector.py | Medium |
| Inspector dock closed (D39) | D39 | Optional: skip setup when dock hidden | Low |

**Order:** 1) Bind Agents Inspector to table selection. 2) Optionally add visibility check before setup_inspector (low priority; current behavior is correct).

---

### Phase 4 — UX Consistency

| Target | Defects | Modules | Risk |
|--------|---------|---------|------|
| Context menu | D37 | source_list_item, knowledge_source_explorer_panel | Low |
| Breadcrumb labels | D7, D21 | breadcrumbs/manager.py | Low |
| Language consistency | D16, D19, D20, D28, D29, D30, D32, D33 | Multiple | Low |
| Placeholder indicators | D26 | agents_panels, tools_panels, data_stores_panels | Low |
| Project Hub clarity | D10 | sidebar_config.py | Low |

**Order:** 1) Context menu (D37). 2) Breadcrumb and language labels. 3) Placeholder indicators. 4) Project Hub tooltips.

---

### Phase 5 — Theme Cleanup

| Target | Defects | Modules | Risk |
|--------|---------|---------|------|
| Hardcoded colors | D34, D35, D36, D23 | Multiple panels, sidebar, screens | Medium |

**Order:** 1) Sidebar (D36). 2) Control Center and QA workspace hosts (D35, D23). 3) High-traffic panels (Control Center, QA). 4) Remaining panels incrementally.

---

### Phase 6 — Test Coverage Improvements

| Target | Defects | Modules | Risk |
|--------|---------|---------|------|
| D13 regression test | D25 | tests/behavior/ux_behavior_simulation.py | Low |
| Workspace switch with InspectorHost | — | New test | Low |
| Command palette navigation | — | New test | Low |
| Project switch + restore | — | Extend existing | Low |

**Order:** 1) Add D13 regression test (with set_inspector_host). 2) Add destructive workflow test with InspectorHost. 3) Add Command Palette navigation test. 4) Extend project switch test if needed.

---

## 5. Regression Safety

### 5.1 Tests to Add or Extend

| Scenario | Current Coverage | Action |
|----------|------------------|--------|
| **Workspace switching with InspectorHost** | test_workspace_switch_order_no_crash does NOT set inspector_host | Add `host.set_inspector_host(InspectorHost())` and verify no crash when switching to operations_prompt_studio |
| **Prompt Studio setup_inspector** | None | Add test that switches to Prompt Studio with InspectorHost; assert no TypeError |
| **Area-level inspector** | None | Add test: switch Operations → Control Center → Settings rapidly; assert Inspector content updates (or at least no crash) |
| **Command Palette navigation** | None | Add test: execute nav.knowledge, nav.prompt_studio, nav.agent_tasks; assert correct area/workspace shown |
| **Project switching** | V2 verified in code | Consider adding behavior test for project switch + workspace restore |
| **Inspector setup_inspector signature** | None | Add test that all screens' setup_inspector accept content_token (optional) |

### 5.2 Pre-Implementation Checklist

Before implementing Phase 1:

1. Add D13 regression test (D25) and ensure it passes with current code.
2. Run full test suite and record baseline.
3. Document all `setup_inspector` call sites and signatures.

Before implementing Phase 2–4:

1. Run Phase 1 tests.
2. Manual smoke test: Sidebar, Command Palette, context menus.

Before implementing Phase 5:

1. Run theme-related tests (e.g. test_settings_theme_tokens).
2. Manual verification: switch Light ↔ Dark, check all modified panels.

---

## 6. Final Execution Plan

Ordered list of steps for safe execution:

1. **Add D13 regression test** (D25) – extend `test_workspace_switch_order_no_crash` to set InspectorHost and switch to Prompt Studio. Verify pass.
2. **Document setup_inspector matrix** – list all screens and workspace widgets with setup_inspector; note which accept content_token.
3. **Phase 1a: WorkspaceHost** – Add prepare_for_setup and content_token to WorkspaceHost._on_current_changed. Temporarily pass content_token only to screens that support it; others receive it but may ignore (optional param).
4. **Phase 1b: Screen signatures** – Add `content_token: int | None = None` to all screen setup_inspector methods. Pass through to workspace widgets.
5. **Phase 1c: Workspace widgets** – Add content_token to Control Center, QA, Runtime workspace setup_inspector; pass to inspector_host.set_content where applicable.
6. **Phase 1 verification** – Run tests; manual rapid area switching.
7. **Phase 2a: Sidebar** – Add Agents (D12), System Graph (D14) to sidebar_config.
8. **Phase 2b: Command Palette** – Add Knowledge, Prompt Studio, Agent Tasks, cc_models, cc_providers, cc_agents, cc_tools, cc_data_stores, rd_system_graph commands.
9. **Phase 2 verification** – Manual: click each new Sidebar item; run each new Command Palette command.
10. **Phase 3: Agents Inspector** – Bind Agents Inspector to table selection (D27).
11. **Phase 4a: Context menu** – Add context menu to Knowledge source items (D37).
12. **Phase 4b: Labels** – Fix D7, D21, D28, D29, D30, D32, D33, D20.
13. **Phase 4c: Placeholder indicators** – Add "Demo-Daten" to Control Center panels (D26).
14. **Phase 5: Theme** – Replace hardcoded colors in Sidebar, screens, panels (D34–D36, D23, D35).
15. **Phase 6: Additional tests** – Add Command Palette test, area-switch test.
16. **Final verification** – Full test suite, manual destructive workflow, theme switch.

---

## 7. Dependency Graph (Simplified)

```
D25 (test) ──────────────────────────────────────────► Prevents regression
                                                              │
D24 (WorkspaceHost) ──► All screens setup_inspector ──► D9 (screens)
                                                              │
                                                              ▼
D12, D14 (Sidebar) ──► Independent
D15 (Command Palette) ──► Independent
D37 (context menu) ──► Independent
D7, D21, D28–D33 (language) ──► Independent
D26 (placeholder label) ──► Independent
D34–D36 (theme) ──► Independent, but many files
D27 (Agents Inspector) ──► Independent
D38 (tab order) ──► Independent, optional
D39 (Inspector dock) ──► Optional, low priority
```

---

## 8. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **D24/D9 implementation breaks existing screens** | Add content_token as optional (`= None`); backward compatible. Test each screen after change. |
| **Theme refactor breaks layout** | Change one panel at a time; verify visually. Use theme tokens that already exist. |
| **Command Palette commands wrong workspace_id** | Derive from sidebar_config or single source of truth. |
| **Regression in D13** | Add test before any Phase 1 change; run after every change. |
| **Language changes inconsistent** | Define language policy (DE vs EN) in one place; apply consistently. |

---

*This plan is a strategy document only. No code changes have been made. Execute phases in order; verify after each phase before proceeding.*
