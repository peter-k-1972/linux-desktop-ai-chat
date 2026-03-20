# UX/UI Acceptance Review Report – Linux Desktop Chat

**Version:** 1.0  
**Date:** 2026-03-16  
**Reviewer:** Senior UX/UI Reviewer  
**Scope:** Project-centered UX architecture vs. implementation

---

## Executive Summary

The implementation follows a **project-centered, workspace-based** architecture with good coverage of the target areas. Several areas pass or pass with minor issues. Critical gaps exist in **Settings separation** (Application vs. Project vs. Workspace), **navigation naming consistency**, and **placeholder UI**. No fixes are applied in this step; findings are documented for remediation.

---

## A. Project Context System

**Status:** PASS WITH ISSUES

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | `ProjectContextManager` correctly tracks active project, loads from SQLite, and emits `project_context_changed` via EventBus. | — | — |
| 2 | `project_events.py` uses a simple listener list rather than a full EventBus; payload is `{"project_id": ...}`. Listeners receive `project_id` but must fetch full project from manager. | Minor | INT-CONTEXT |
| 3 | `emit_project_context_changed(None)` is called when clearing; some listeners may expect `project_id` in payload. Payload consistency is maintained. | — | — |

### Recommended Fix

- **F2:** Document that listeners should call `get_project_context_manager().get_active_project()` when `project_id` is non-null, rather than relying on payload for full project data. Consider extending payload with `project` dict for convenience.

---

## B. Project Switcher

**Status:** PASS WITH ISSUES

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | Project Switcher appears in both **TopBar** and **Sidebar** (duplicate instances). | Major | UX-NAV |
| 2 | `ProjectSwitcherButton` correctly uses `ProjectContextManager` and `project_context_changed`. | — | — |
| 3 | Dropdown with project list, new project creation, and clear-project option is implemented. | — | — |
| 4 | Redundant placement may confuse users and consume space. | Minor | UX-WORKFLOW |

### Recommended Fix

- **F1:** Choose a single canonical location (TopBar recommended per docs). Remove or hide the duplicate in the Sidebar, or clearly differentiate (e.g., Sidebar = quick context, TopBar = full switcher).

---

## C. Project Hub

**Status:** PASS WITH ISSUES

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | Two overlapping entry points: **Project Hub Screen** (standalone, area `project_hub`) and **Project Overview** (inside Operations → Projects). Both show project stats, activity, and quick actions. | Major | UX-NAV |
| 2 | Sidebar PROJECT section has three items: "Overview" (project_hub), "Active Project" (command_center), "Project Overview" (operations_projects). Naming is inconsistent and overlapping. | Major | UX-LABEL |
| 3 | `ProjectHubPage` and `ProjectOverviewPanel` implement similar content (stats, recent chats/sources/prompts, quick actions). | Minor | UX-ARCH |
| 4 | `_find_workspace_host()` in `ProjectHubPage` traverses parent hierarchy; may fail if widget tree changes. | Minor | QA-MISS |
| 5 | Quick Actions correctly use `OperationsContext` + `show_area` for Hub→Workspace navigation with pending context. | — | — |

### Recommended Fix

- **F1–F2:** Consolidate to a single Project Hub concept. Either (a) make Project Hub the main entry and remove "Project Overview" from Operations, or (b) make Operations/Projects the canonical hub and remove the standalone Project Hub screen.
- **F3:** Align sidebar labels: e.g., "Project Hub" (or "Overview") as the main project dashboard; "Active Project" should map to Command Center/Dashboard; avoid "Project Overview" as a separate label if it duplicates Hub.

---

## D. Settings Workspace

**Status:** FAIL

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | Target: clean separation of **Application Settings**, **Project Settings**, and **Workspace Settings**. | — | — |
| 2 | Current implementation: only **Application-level** categories (Application, Appearance, AI/Models, Data, Privacy, Advanced). No Project Settings or Workspace Settings. | Critical | UX-ARCH |
| 3 | Settings categories are global; no project-scoped or workspace-scoped settings UI. | Critical | INT-DATA |
| 4 | Knowledge Settings, Prompt Studio Settings, Agent Workspace Settings exist as **placeholders** within their workspaces, not in the central Settings Workspace. | Major | UX-EMPTY |

### Recommended Fix

- **F1:** Introduce a Settings structure that separates:
  - **Application Settings** (current categories) – global
  - **Project Settings** – shown when a project is active (e.g., project-specific defaults)
  - **Workspace Settings** – per-workspace (Knowledge, Prompt Studio, Agents) or link from workspace to a dedicated settings section
- **F2:** Either integrate workspace-specific settings into the Settings Workspace (with project context) or document that they remain in-workspace and ensure consistency.

---

## E. Chat Navigation + Topics

**Status:** PASS WITH ISSUES

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | Chat navigation has **Topics** (collapsible sections), Pinned, Ungrouped, Archived. Matches target "lightweight Topics." | — | — |
| 2 | `ChatNavigationPanel` subscribes to `project_context_changed` and filters chats by project. | — | — |
| 3 | "Neuer Chat" and "Neues Topic" disabled when no project selected; correct project-scoped behavior. | — | — |
| 4 | `ChatService.list_chats_for_project` and `TopicService` are used; data binding is project-scoped. | — | — |
| 5 | Mixed language: "Ungrouped" (EN) vs. "Archiviert", "Angeheftet" (DE). | Minor | UX-LABEL |
| 6 | `_group_chats_by_topic` uses "Ungrouped" as section name; other labels are German. | Minor | UX-LABEL |

### Recommended Fix

- **F1:** Standardize language (all DE or all EN) for Chat navigation labels.

---

## F. Knowledge Workspace

**Status:** PASS WITH ISSUES

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | Target: Sources / Collections / Index / Settings. Implemented: Sources, Collections, Index, **Settings (placeholder)**. | — | — |
| 2 | `KnowledgeNavigationPanel` has sections: Sources, Collections, Index, Settings. | — | — |
| 3 | `KnowledgeContentPlaceholder` used for Settings: "Content panel – implement section-specific UI here." | Major | UX-EMPTY |
| 4 | Knowledge workspace subscribes to `project_context_changed`; sources are project-scoped. | — | — |
| 5 | URL/Note indexing shows "not yet implemented" messages. | Minor | UX-EMPTY |

### Recommended Fix

- **F1:** Implement Knowledge Settings section (chunk size, embedding model, etc.) or remove from nav until ready.
- **F2:** Add clear empty-state messaging for URL/Note indexing instead of inline "not yet implemented."

---

## G. Prompt Studio

**Status:** PASS WITH ISSUES

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | Target: Prompts / Templates / Test Lab / Settings. Implemented: Prompts, Templates, Test Lab, **Settings (placeholder)**. | — | — |
| 2 | `PromptStudioWorkspace` has `_create_placeholder_widget("Settings", "Prompt Studio Einstellungen. (Coming soon)")`. | Major | UX-EMPTY |
| 3 | Prompts are project-scoped; `PromptListPanel` refreshes on `project_context_changed`. | — | — |
| 4 | `open_with_context({"prompt_id": int})` works for Project Hub → Prompt Studio navigation. | — | — |

### Recommended Fix

- **F1:** Implement Prompt Studio Settings or remove from navigation until ready; avoid "Coming soon" placeholders in production.

---

## H. Agent Workspace

**Status:** PASS WITH ISSUES

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | Target: Agent Library / Runs / Activity / Skills / Settings. Implemented: Library, Runs, Activity, Skills, **Settings (placeholder)**. | — | — |
| 2 | Agent Library, Runs, Activity, Skills panels are implemented. Settings is `_placeholder_widget("Settings", "Agent-Workspace-Einstellungen.")`. | Major | UX-EMPTY |
| 3 | Agent Library is project-scoped; `AgentListPanel` filters by `project_id`; create flow requires project. | — | — |
| 4 | `AgentNavigationPanel` shows project header "Bitte Projekt auswählen" when no project; consistent with Chat/Knowledge. | — | — |
| 5 | `open_with_context` supports `section_id` and `agent_id` for Command Palette. | — | — |

### Recommended Fix

- **F1:** Implement Agent Workspace Settings or remove from navigation; replace placeholder with a minimal settings form or clear "Not yet available" state.

---

## I. Workspace Context Sync

**Status:** PASS WITH ISSUES

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | `OperationsContext` provides `set_pending_context` / `consume_pending_context` for Hub→Workspace navigation. | — | — |
| 2 | `OperationsScreen.show_workspace` consumes pending context and calls `widget.open_with_context(ctx)`. | — | — |
| 3 | Chat, Knowledge, Prompt Studio, Agent Tasks support `open_with_context` for chat_id, source_path, prompt_id, section_id. | — | — |
| 4 | `ProjectHubPage._find_workspace_host()` uses `hasattr(p, "show_area") and hasattr(p, "_area_to_index")`; WorkspaceHost has both. Traversal may be fragile if widget hierarchy changes. | Minor | QA-MISS |
| 5 | `ProjectOverviewPanel` (in ProjectsWorkspace) uses same `_find_workspace_host` pattern; both need a stable way to obtain the host. | Minor | INT-CONTEXT |

### Recommended Fix

- **F1:** Consider injecting `WorkspaceHost` reference (or a navigation service) into Project Hub / Project Overview instead of parent traversal. Reduces coupling to widget hierarchy.

---

## J. Navigation / Naming Consistency

**Status:** FAIL

### Findings

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | Sidebar PROJECT section: "Overview", "Active Project", "Project Overview" – overlapping and unclear. | Major | UX-LABEL |
| 2 | "Active Project" maps to Command Center (Dashboard); "Overview" maps to Project Hub; "Project Overview" maps to Operations/Projects. | Major | UX-NAV |
| 3 | WORKSPACE section: "Chat", "Knowledge", "Prompt Studio", "Agents" – consistent. | — | — |
| 4 | SYSTEM: "Models", "Providers", "Tools", "Data Stores" – Control Center items; no "Agents" in Control Center in sidebar (Agents is under WORKSPACE). Target architecture has Agents in Control Center (design) and Operations (tasks). | Minor | UX-ARCH |
| 5 | Mixed EN/DE: "Overview", "Chat", "Knowledge" vs. "Einstellungen", "Wissensräume", "Bitte Projekt auswählen". | Minor | UX-LABEL |
| 6 | Settings categories: "Application", "Appearance", "AI / Models", "Data", "Privacy", "Advanced" – English. Rest of app partially German. | Minor | UX-LABEL |

### Recommended Fix

- **F1:** Redesign PROJECT section: single "Project Hub" or "Overview" for project dashboard; remove or rename "Active Project" and "Project Overview" to avoid duplication.
- **F2:** Decide on primary UI language (DE or EN) and apply consistently across navigation, labels, and placeholders.
- **F3:** Align with UX_CONCEPT: Control Center should include "Agents" (design/registry); Operations has "Agent Tasks". Current sidebar has "Agents" under WORKSPACE – clarify if this is Agent Tasks or Agent design.

---

## Summary Matrix

| Area | Status | Critical | Major | Minor |
|------|--------|----------|-------|-------|
| A. Project Context System | PASS WITH ISSUES | 0 | 0 | 1 |
| B. Project Switcher | PASS WITH ISSUES | 0 | 1 | 1 |
| C. Project Hub | PASS WITH ISSUES | 0 | 2 | 2 |
| D. Settings Workspace | FAIL | 2 | 1 | 0 |
| E. Chat Navigation + Topics | PASS WITH ISSUES | 0 | 0 | 2 |
| F. Knowledge Workspace | PASS WITH ISSUES | 0 | 1 | 1 |
| G. Prompt Studio | PASS WITH ISSUES | 0 | 1 | 0 |
| H. Agent Workspace | PASS WITH ISSUES | 0 | 1 | 0 |
| I. Workspace Context Sync | PASS WITH ISSUES | 0 | 0 | 2 |
| J. Navigation / Naming | FAIL | 0 | 2 | 2 |

---

## Category Legend

| Code | Description |
|------|-------------|
| UX-ARCH | Architecture compliance |
| UX-NAV | Navigation consistency |
| UX-STATE | State handling |
| UX-LABEL | Label/naming consistency |
| UX-EMPTY | Placeholder / unfinished UI |
| UX-WORKFLOW | Workflow / usability |
| INT-CONTEXT | Context propagation |
| INT-DATA | Data binding |
| QA-MISS | Potential quality / robustness |

---

## Recommended Priority Order for Fixes

1. **Critical:** Settings separation (Application / Project / Workspace)
2. **Major:** Project Hub consolidation and naming; Project Switcher deduplication; placeholder replacement for Knowledge/Prompt/Agent Settings
3. **Minor:** Language consistency; `_find_workspace_host` robustness; Control Center vs. Operations Agents clarification

---

*This report documents findings only. No code changes were made.*
