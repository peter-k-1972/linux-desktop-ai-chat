# Phase 1 — UX/UI Acceptance Review Report

**Date:** 2026-03-16  
**Scope:** Linux Desktop Chat – Project-centered UX architecture  
**Reference:** docs/UX_CONCEPT.md, docs/PYSIDE6_UI_ARCHITECTURE.md

---

## Executive Summary

The implementation largely follows the target UX architecture with project-centered workspaces, sidebar navigation, and workspace context propagation. **Critical defects** were identified in project context synchronization (dual context systems) and navigation consistency. Several areas show **PASS WITH ISSUES**; one area (**Project Context System**) is **FAIL** due to the dual-context bug.

---

## A. Project Context System

**Status:** **FAIL**

| Criterion | Assessment |
|-----------|------------|
| Architecture compliance | Two separate project context systems exist and are **not synchronized** |
| State handling | ProjectContextManager and ActiveProjectContext diverge |
| Propagation | Project Switcher updates only ProjectContextManager; Projects workspace updates only ActiveProjectContext |

**Defects:**

| ID | Class | Description |
|----|-------|-------------|
| D-001 | INT-CONTEXT | **Critical:** Dual project context systems – `ProjectContextManager` (project_events) vs `ActiveProjectContext` (app.context.active_project). Project Switcher (TopBar) updates ProjectContextManager; Operations > Projects "Set Active" updates ActiveProjectContext. Chat, Knowledge, Prompt Studio, Agent workspaces subscribe to project_events. Breadcrumbs and Projects workspace use ActiveProjectContext. Selecting project in one place does not update the other. |
| D-002 | UX-STATE | When user selects project in Projects workspace, Project Switcher button and all workspace data (Chat, Knowledge, Prompt) remain on previous project |
| D-003 | UX-STATE | When user selects project in Project Switcher, Breadcrumbs and Projects workspace overview may show stale project |

---

## B. Project Switcher

**Status:** **PASS WITH ISSUES**

| Criterion | Assessment |
|-----------|------------|
| Architecture compliance | Button in TopBar, opens dialog with Recent/All/Create |
| Navigation clarity | Clear; shows current project name |
| State handling | Updates label on project_context_changed; does not sync with ActiveProjectContext |

**Defects:**

| ID | Class | Description |
|----|-------|-------------|
| D-004 | INT-CONTEXT | Same as D-001 – not synced with ActiveProjectContext |

---

## C. Project Hub

**Status:** **PASS WITH ISSUES**

| Criterion | Assessment |
|-----------|------------|
| Architecture compliance | Overview of active project, stats, recent sections, quick actions |
| Navigation clarity | Quick actions navigate to workspaces correctly |
| Data binding | Uses ProjectContextManager; reacts to project_context_changed |
| Pending context | Correctly uses set_pending_context and show_area for Hub→Workspace navigation |

**Defects:**

| ID | Class | Description |
|----|-------|-------------|
| D-005 | INT-CONTEXT | Same as D-001 – uses ProjectContextManager only |
| D-006 | UX-LABEL | Labels "Recent Chats", "Recent Knowledge", "Recent Prompts" in English; UX_CONCEPT uses German ("Kommandozentrale", etc.) – minor inconsistency |

---

## D. Settings Workspace

**Status:** **PASS**

| Criterion | Assessment |
|-----------|------------|
| Architecture compliance | Left nav (categories), center content, right help panel |
| Navigation clarity | Categories: Application, Appearance, AI/Models, Data, Privacy, Advanced, Project, Workspace |
| State handling | Category stack; no project dependency for most categories |

**Defects:** None critical. Legacy workspace ID mapping present and functional.

---

## E. Chat Navigation and Topics

**Status:** **PASS WITH ISSUES**

| Criterion | Assessment |
|-----------|------------|
| Architecture compliance | ChatNavigationPanel with project header, search, topics, pinned, archived |
| Project context | Subscribes to project_context_changed; clears selection on project change |
| Data binding | ChatService.list_chats_for_project with filters |

**Defects:**

| ID | Class | Description |
|----|-------|-------------|
| D-007 | UX-ARCH | Two chat navigation implementations exist: `ChatSessionExplorerPanel` (gui/domains/operations/chat/panels) and `ChatNavigationPanel` (ui/chat). ChatWorkspace uses ChatNavigationPanel. ChatSessionExplorerPanel may be dead code or alternate path – potential confusion |
| D-008 | INT-CONTEXT | Chat workspace uses ProjectContextManager; if user sets project in Projects workspace, Chat shows wrong project until Switcher is used |

---

## F. Knowledge Workspace

**Status:** **PASS WITH ISSUES**

| Criterion | Assessment |
|-----------|------------|
| Architecture compliance | Explorer (sources), overview, retrieval test |
| Project context | KnowledgeSourceExplorerPanel subscribes to project_context_changed |
| Data binding | KnowledgeService.list_sources_for_project |

**Defects:**

| ID | Class | Description |
|----|-------|-------------|
| D-009 | INT-CONTEXT | Same as D-008 – project context from ProjectContextManager only |
| D-010 | UX-WORKFLOW | select_source(path) called from open_with_context; if source not yet in list (e.g. different project), selection may fail silently |

---

## G. Prompt Studio

**Status:** **PASS WITH ISSUES**

| Criterion | Assessment |
|-----------|------------|
| Architecture compliance | Library panel (left), editor + preview (center) |
| Project context | PromptLibraryPanel subscribes to project_context_changed |
| Data binding | list_project_prompts + list_global_prompts |

**Defects:**

| ID | Class | Description |
|----|-------|-------------|
| D-011 | INT-CONTEXT | Same as D-008 |
| D-012 | UX-EMPTY | When no project selected, shows "Bitte Projekt auswählen" – correct empty state |

---

## H. Agent Workspace

**Status:** **PASS WITH ISSUES**

| Criterion | Assessment |
|-----------|------------|
| Architecture compliance | Registry, Task panel, Active panel, Summary, Result |
| Project context | Subscribes to project_context_changed; _refresh_agents reloads |
| Data binding | AgentService.list_agents – **agents appear global, not project-scoped** per UX_CONCEPT |

**Defects:**

| ID | Class | Description |
|----|-------|-------------|
| D-013 | INT-DATA | Agent registry lists all agents; UX_CONCEPT suggests project-scoped agents in Operations. May be intentional (Control Center vs Operations split) – verify |
| D-014 | INT-CONTEXT | Same as D-008 |

---

## I. Workspace Context Sync

**Status:** **PASS WITH ISSUES**

| Criterion | Assessment |
|-----------|------------|
| Pending context | OperationsContext (set_pending_context, consume_pending_context) used correctly by ProjectHubPage and OperationsScreen |
| Hub→Workspace | ProjectHubPage sets pending context, calls host.show_area; OperationsScreen consumes and passes to open_with_context |
| Inspector refresh | Workspaces call setup_inspector on show; inspector updated on workspace change |

**Defects:**

| ID | Class | Description |
|----|-------|-------------|
| D-015 | INT-CONTEXT | ProjectHubPage._find_workspace_host() traverses parent for widget with show_area and _area_to_index. WorkspaceHost has these. Hierarchy: ProjectHubPage → viewport → scroll → ProjectHubScreen → WorkspaceHost. Valid. |
| D-016 | UX-NAV | WorkspaceHost.show_area(OPERATIONS, "operations_chat") correctly delegates to OperationsScreen.show_workspace which consumes pending context. Flow correct. |

---

## J. Navigation and Naming Consistency

**Status:** **PASS WITH ISSUES**

| Criterion | Assessment |
|-----------|------------|
| Sidebar sections | PROJECT, WORKSPACE, SYSTEM, OBSERVABILITY, QUALITY, SETTINGS |
| Naming | Mix of English (Project Hub, Chat, Knowledge) and German (Bitte Projekt auswählen, Neuer Chat) |
| UX_CONCEPT | Specifies German ("Kommandozentrale", "Operations") – implementation uses English in sidebar |

**Defects:**

| ID | Class | Description |
|----|-------|-------------|
| D-017 | UX-LABEL | Sidebar uses "Project Hub", "Dashboard", "Chat", "Agents" (English); UX_CONCEPT uses "Kommandozentrale", "Chat Workspace", "Agent Tasks" – acceptable if product is bilingual |
| D-018 | UX-NAV | OperationsNav uses "Projekte", "Chat", "Agent Tasks", "Knowledge / RAG", "Prompt Studio" – consistent within Operations |

---

## Summary by Status

| Area | Status |
|------|--------|
| A. Project Context System | **FAIL** |
| B. Project Switcher | PASS WITH ISSUES |
| C. Project Hub | PASS WITH ISSUES |
| D. Settings Workspace | PASS |
| E. Chat Navigation | PASS WITH ISSUES |
| F. Knowledge Workspace | PASS WITH ISSUES |
| G. Prompt Studio | PASS WITH ISSUES |
| H. Agent Workspace | PASS WITH ISSUES |
| I. Workspace Context Sync | PASS WITH ISSUES |
| J. Navigation Consistency | PASS WITH ISSUES |

---

## Defect Classification Summary

| Class | Count |
|-------|-------|
| INT-CONTEXT | 8 |
| UX-STATE | 2 |
| UX-LABEL | 2 |
| UX-ARCH | 1 |
| UX-WORKFLOW | 1 |
| INT-DATA | 1 |

**Critical:** D-001 (dual project context)  
**Major:** D-002, D-003 (state divergence)  
**Minor:** D-006, D-007, D-010, D-017, D-018
