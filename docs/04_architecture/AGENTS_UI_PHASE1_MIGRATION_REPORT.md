# Agents UI Phase 1 Migration Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Sprint:** Agents UI Migration Phase 1  
**Referenz:** AGENTS_UI_ARCHITECTURE_AUDIT.md, APP_UI_TO_GUI_TRANSITION_PLAN.md, Strategy C (Hybrid)

---

## 1. Executive Summary

Phase 1 of the Agents UI migration is **complete**. The productive Agent Manager flow has been moved from `app/ui/agents/` to `app/gui/domains/control_center/agents_ui/`, the Control Center Agents workspace now hosts the canonical implementation, and `app/ui/agents/` serves as a thin compatibility layer for the 7 migrated files.

---

## 2. Moved Files

| Source | Target | Status |
|--------|--------|--------|
| app/ui/agents/agent_manager_panel.py | app/gui/domains/control_center/agents_ui/agent_manager_panel.py | ✓ |
| app/ui/agents/agent_list_panel.py | app/gui/domains/control_center/agents_ui/agent_list_panel.py | ✓ |
| app/ui/agents/agent_list_item.py | app/gui/domains/control_center/agents_ui/agent_list_item.py | ✓ |
| app/ui/agents/agent_profile_panel.py | app/gui/domains/control_center/agents_ui/agent_profile_panel.py | ✓ |
| app/ui/agents/agent_avatar_widget.py | app/gui/domains/control_center/agents_ui/agent_avatar_widget.py | ✓ |
| app/ui/agents/agent_form_widgets.py | app/gui/domains/control_center/agents_ui/agent_form_widgets.py | ✓ |
| app/ui/agents/agent_performance_tab.py | app/gui/domains/control_center/agents_ui/agent_performance_tab.py | ✓ |

---

## 3. Changed Imports

| Module | Change |
|--------|--------|
| app/main.py | Uses `app.ui.agents.AgentManagerDialog` (re-export) – no change |
| app/gui/domains/control_center/workspaces/agents_workspace.py | Imports `AgentManagerPanel` from `app.gui.domains.control_center.agents_ui` |
| app/ui/agents/*.py (7 files) | Re-exports from `app.gui.domains.control_center.agents_ui.*` |
| tests/regression/test_agent_delete_removes_from_list.py | Patch target: `app.gui.domains.control_center.agents_ui.agent_manager_panel.*` |
| tests/ui/test_agent_hr_ui.py | Patch target: `app.gui.domains.control_center.agents_ui.agent_manager_panel.*` |
| tests/ui/test_ui_behavior.py | Patch target: `app.gui.domains.control_center.agents_ui.agent_manager_panel.*` |
| tests/state_consistency/test_agent_consistency.py | Patch target: `app.gui.domains.control_center.agents_ui.agent_manager_panel.*` |

---

## 4. Demo Content Replacement

| Before | After |
|--------|-------|
| AgentRegistryPanel (demo table, 3 hardcoded rows) | AgentManagerPanel (AgentService, full CRUD) |
| AgentSummaryPanel (static summary) | AgentProfilePanel (profile view, edit mode) |
| Demo-only data | Real AgentService integration |

**AgentsWorkspace** now hosts `AgentManagerPanel` directly. The Inspector is bound to agent selection via `list_panel.agent_selected` → `_on_agent_selected` → `_refresh_inspector`.

**AgentRegistryPanel** and **AgentSummaryPanel** in `panels/agents_panels.py` are **isolated** – no longer used by AgentsWorkspace. They can be removed in a later cleanup sprint.

---

## 5. Remaining ui/agents Files and Status

| File | Status | Notes |
|------|--------|-------|
| agent_manager_panel.py | Re-export | From agents_ui |
| agent_list_panel.py | Re-export | From agents_ui |
| agent_list_item.py | Re-export | From agents_ui |
| agent_profile_panel.py | Re-export | From agents_ui |
| agent_avatar_widget.py | Re-export | From agents_ui |
| agent_form_widgets.py | Re-export | From agents_ui |
| agent_performance_tab.py | Re-export | From agents_ui |
| agent_workspace.py | **remove_later** | Never instantiated |
| agent_navigation_panel.py | **remove_later** | Only from AgentWorkspace |
| agent_library_panel.py | **remove_later** | Only from AgentWorkspace |
| agent_editor_panel.py | **manual_review** | Different API than AgentProfileForm |
| agent_runs_panel.py | **manual_review** | Migrate in Phase 3? |
| agent_activity_panel.py | **manual_review** | Migrate in Phase 3? |
| agent_skills_panel.py | **manual_review** | Migrate in Phase 3? |

---

## 6. Test Results

### Tests Executed

| Suite | Tests | Passed | Failed |
|-------|-------|--------|--------|
| tests/architecture/ | 12 | 12 | 0 |
| tests/ui/test_agent_hr_ui.py | 7 | 7 | 0 |
| tests/regression/test_agent_delete_removes_from_list.py | 3 | 3 | 0 |
| tests/state_consistency/test_agent_consistency.py | 2 | 2 | 0 |
| tests/ui/test_ui_behavior.py | 3 | 3 | 0 |
| tests/test_agent_hr.py | 12 | 12 | 0 |
| tests/smoke/test_agent_workflow.py | 6 | 6 | 0 |
| tests/ui/test_agent_performance_tab.py | 1 | 1 | 0 |
| tests/qa/generators/test_update_control_center.py | 14 | 14 | 0 |

### New Failures

None.

### Pre-existing Failures (not attributed to this sprint)

| Test | Cause |
|------|-------|
| tests/smoke/test_app_startup.py (4 failures) | sidebar_widget.py:194 – `ValueError: too many values to unpack` (DB schema) |
| tests/smoke/test_shell_gui.py (4 failures) | Same sidebar/DB issue |

---

## 7. Compatibility Fixes Applied

1. **AgentListPanel.list_widget** – Added QListWidget-like adapter for tests that expect `count()`, `item(i)`, `item.data(UserRole)`, `setCurrentItem()`. Tests use this for assertions.
2. **AgentManagerPanel._on_agent_selected** – Now calls `list_panel.set_current_agent(profile)` so `get_selected()` returns the correct profile when tests simulate selection.

---

## 8. Final Trees

### app/gui/domains/control_center/agents_ui/

```
agents_ui/
├── __init__.py
├── agent_avatar_widget.py
├── agent_form_widgets.py
├── agent_list_item.py
├── agent_list_panel.py
├── agent_manager_panel.py
├── agent_performance_tab.py
└── agent_profile_panel.py
```

### app/ui/agents/

```
agents/
├── __init__.py
├── agent_activity_panel.py      # manual_review
├── agent_avatar_widget.py       # Re-export
├── agent_editor_panel.py        # manual_review
├── agent_form_widgets.py        # Re-export
├── agent_library_panel.py       # remove_later
├── agent_list_item.py           # Re-export
├── agent_list_panel.py         # Re-export
├── agent_manager_panel.py      # Re-export
├── agent_navigation_panel.py   # remove_later
├── agent_performance_tab.py    # Re-export
├── agent_profile_panel.py     # Re-export
├── agent_runs_panel.py        # manual_review
├── agent_skills_panel.py      # manual_review
└── agent_workspace.py         # remove_later
```

---

## 9. Manual Review Points

- **AgentRegistryPanel / AgentSummaryPanel** – Isolated in `panels/agents_panels.py`. Consider removal in a later sprint.
- **agent_editor_panel, agent_runs_panel, agent_activity_panel, agent_skills_panel** – Not migrated. Audit recommends manual_review for Phase 3.
- **AgentWorkspace branch** – Not migrated. Dead code; remove_later.

---

## 10. Architecture Guard Rules

Add to ARCHITECTURE_GUARD_RULES.md:

- **gui/domains/control_center/agents_ui** is canonical for Agent Manager flow.
- **app.ui.agents** contains Re-Exports for migrated components; non-migrated files remain in ui.
