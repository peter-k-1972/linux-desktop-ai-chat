# Phase 2 — Break-It Manual UX Test Report

**Date:** 2026-03-16  
**Method:** Simulated manual usage flows based on code analysis

---

## Test Scenarios Executed

### 1. Switching Projects Repeatedly

| Step | Action | Expected | Actual | Severity |
|------|--------|----------|--------|----------|
| 1.1 | Select Project A via TopBar Switcher | All workspaces show Project A data | ProjectContextManager updated; workspaces refresh | OK |
| 1.2 | Select Project B via TopBar Switcher | All workspaces show Project B data | Same | OK |
| 1.3 | Select Project A via Operations > Projects > "Set Active" | All workspaces + TopBar show Project A | **TopBar still shows Project B; Chat/Knowledge/Prompt still show Project B data** | **Critical** |
| 1.4 | Select Project B via Operations > Projects > "Set Active" | All workspaces + TopBar show Project B | **TopBar and workspaces stay on previous project** | **Critical** |

**Reproduction:** Operations → Projects → select project in list → click "Als aktiv setzen" (Set Active). ProjectContextManager is never updated.

---

### 2. Creating and Selecting Chats

| Step | Action | Expected | Actual | Severity |
|------|--------|----------|--------|----------|
| 2.1 | No project selected, open Chat | "Bitte Projekt auswählen" or disabled | Buttons disabled, empty state | OK |
| 2.2 | Select project via Switcher, create chat | Chat created in project | ChatService.create_chat_in_project called | OK |
| 2.3 | Switch project via Projects workspace "Set Active" | Chat list shows new project's chats | **Chat list still shows old project's chats** | **Major** |

---

### 3. Creating Knowledge Sources

| Step | Action | Expected | Actual | Severity |
|------|--------|----------|--------|----------|
| 3.1 | No project, open Knowledge | "Bitte Projekt auswählen" | Buttons disabled | OK |
| 3.2 | Select project, add file | File indexed to project collection | KnowledgeService.add_document(space, path, project_id) | OK |
| 3.3 | Switch project via Projects "Set Active" | Source list shows new project | **Source list still shows old project** | **Major** |

---

### 4. Navigating Between Workspaces

| Step | Action | Expected | Actual | Severity |
|------|--------|----------|--------|----------|
| 4.1 | Project Hub → Quick Action "New Chat" | Navigate to Chat, new chat in project | show_area(OPERATIONS, operations_chat) | OK |
| 4.2 | Project Hub → click Recent Chat | Navigate to Chat, select that chat | set_pending_context({chat_id}), show_area, open_with_context | OK |
| 4.3 | Settings → return to Chat | Chat workspace visible, project context intact | Stack switch; inspector refreshed | OK |

---

### 5. Prompt Studio

| Step | Action | Expected | Actual | Severity |
|------|--------|----------|--------|----------|
| 5.1 | Select project, create prompt | Prompt in project scope | PromptService.create with project_id | OK |
| 5.2 | Switch project via Projects "Set Active" | Prompt list shows new project | **Prompt list still shows old project** | **Major** |

---

### 6. Agent Workspace

| Step | Action | Expected | Actual | Severity |
|------|--------|----------|--------|----------|
| 6.1 | Open Agent Tasks | Agent list loads | AgentService.list_agents (global) | OK |
| 6.2 | Switch project | Agent list may filter by project | **Agents appear global; no project filter** | Minor (verify intent) |

---

### 7. Settings and Return

| Step | Action | Expected | Actual | Severity |
|------|--------|----------|--------|----------|
| 7.1 | Open Settings from sidebar | Settings categories visible | SettingsWorkspace with nav | OK |
| 7.2 | Return to Chat via sidebar | Chat workspace, project intact | Stack switch | OK |
| 7.3 | Breadcrumbs | Show current area/workspace | Uses ActiveProjectContext for project name | **May show wrong project if set via Switcher** | Major |

---

### 8. UI Refresh Behavior

| Step | Action | Expected | Actual | Severity |
|------|--------|----------|--------|----------|
| 8.1 | Project change via Switcher | All subscribers refresh | project_events.emit → listeners | OK |
| 8.2 | Project change via Projects "Set Active" | All subscribers refresh | **Only ActiveProjectContext listeners; ProjectContextManager subscribers not notified** | **Critical** |

---

## Defects Documented (Phase 2)

| ID | Severity | Reproduction | Expected | Actual |
|----|----------|---------------|----------|--------|
| D-001 | Critical | Set project in Operations > Projects | All UI shows that project | TopBar, Chat, Knowledge, Prompt show previous project |
| D-002 | Major | Same as D-001 | Chat list refreshes | Chat list stale |
| D-003 | Major | Set project in TopBar Switcher | Breadcrumbs show project | Breadcrumbs use ActiveProjectContext; may be stale |
| D-004 | Major | Navigate Project Hub → Chat with pending chat_id | Chat opens with that chat | Works if project already correct in ProjectContextManager |
| D-005 | Minor | Project Hub recent item from different project | Navigate and select | open_with_context may not find item if project was set via Projects |

---

## Stale UI State Summary

- **Context leak:** Projects workspace and Breadcrumbs use ActiveProjectContext; all other workspaces use ProjectContextManager. No synchronization.
- **Dead UI elements:** None identified; ChatSessionExplorerPanel may be unused.
- **Placeholder screens:** None critical.
- **Broken navigation:** Hub→Workspace flow works when project set via Switcher.
- **Unexpected empty states:** Correct when no project selected.
