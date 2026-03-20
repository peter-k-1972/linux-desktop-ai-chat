# Phase 4 — QA System Validation

**Date:** 2026-03-16  
**Scope:** Compare discovered defects against existing QA architecture

---

## Defect vs QA Detection Analysis

### D-001: Dual Project Context (Critical) — RESOLVED

| Question | Answer |
|----------|--------|
| Should the QA system have detected this? | **Yes** |
| Where should detection have happened? | **Integration test** or **UI smoke test** |
| Classification | **DETECTABLE BUT MISSED** |

**Rationale:** A test that (1) sets project via Project Switcher, (2) verifies ProjectContextManager and ActiveProjectContext both have the same project_id, (3) sets project via Operations > Projects "Set Active", (4) verifies both contexts and all workspace subscribers receive the update, would have caught the divergence. No such test exists in `tests/smoke/`, `tests/ui/`, or `tests/integration/`.

**Existing coverage:** `tests/test_projects.py` tests database CRUD for projects. `tests/smoke/test_shell_gui.py` tests WorkspaceHost area switching but does not exercise project context. No test covers ProjectContextManager or ActiveProjectContext synchronization.

---

### D-002, D-003: State Divergence (Major) — RESOLVED

| Question | Answer |
|----------|--------|
| Should the QA system have detected this? | **Yes** (same as D-001) |
| Where should detection have happened? | **Integration test** |
| Classification | **DETECTABLE BUT MISSED** |

**Rationale:** Same root cause as D-001. A project-context integration test would have exposed stale Chat/Knowledge/Prompt data and Breadcrumbs when project is set from Projects workspace.

---

### D-006: Label Inconsistency (Minor)

| Question | Answer |
|----------|--------|
| Should the QA system have detected this? | **Unlikely** |
| Where should detection have happened? | **Audit rule** (if i18n/label audit exists) |
| Classification | **NOT CURRENTLY DETECTABLE** |

**Rationale:** Label consistency is typically checked by manual UX review or i18n tooling. No automated audit for label consistency exists in the QA architecture.

---

### D-007: ChatSessionExplorerPanel vs ChatNavigationPanel

| Question | Answer |
|----------|--------|
| Should the QA system have detected this? | **Partially** |
| Where should detection have happened? | **Gap report** (dead code), **audit rule** |
| Classification | **NOT CURRENTLY DETECTABLE** |

**Rationale:** Dead/unused code detection would require static analysis or coverage tooling. The QA architecture does not include dead-code or duplicate-implementation audits.

---

### D-010: Knowledge select_source When Project Differs

| Question | Answer |
|----------|--------|
| Should the QA system have detected this? | **Yes, with specific test** |
| Where should detection have happened? | **Integration test** or **golden path** |
| Classification | **DETECTABLE BUT MISSED** |

**Rationale:** A golden-path test: Project Hub → click Recent Knowledge (from project A) → switch to project B → navigate to Knowledge → verify source selection behavior. Not covered by existing golden-path tests.

---

### D-013: Agent Scope (Global vs Project)

| Question | Answer |
|----------|--------|
| Should the QA system have detected this? | **N/A** |
| Where should detection have happened? | **Product/UX decision** |
| Classification | **OUT OF QA SCOPE** |

**Rationale:** This is a product/architecture decision, not a defect. QA can verify implemented behavior but cannot determine intended behavior.

---

## Recurring QA Blind Spots

| Blind Spot | Description | Recommendation |
|------------|--------------|----------------|
| **Project context sync** | No test verifies ProjectContextManager and ActiveProjectContext stay in sync | Add integration test: `test_project_context_sync_via_switcher_and_projects_workspace` |
| **Cross-workspace state** | Smoke tests cover area switching but not project-scoped data refresh | Extend smoke or add integration test for project change → workspace refresh |
| **Hub→Workspace pending context** | No test verifies set_pending_context + open_with_context flow | Add test: Project Hub click Recent Chat → Chat workspace shows correct chat |
| **Label/i18n consistency** | No automated check | Optional: Add audit rule or i18n extraction + review |

---

## Missing QA Coverage

| Area | Current | Recommended |
|------|---------|-------------|
| Project context | None | Integration test for ProjectContextManager ↔ ActiveProjectContext sync |
| Project Switcher | None | UI test: dialog opens, project selection updates context |
| Project Hub → Workspace | None | Integration test: pending context consumed by target workspace |
| Workspace refresh on project change | None | Unit/integration: project_context_changed → workspace panels reload |

---

## High-Value QA Improvements

1. **Integration test: project context sync**  
   - Set project via ProjectContextManager → assert ActiveProjectContext matches.  
   - Set project via ActiveProjectContext (simulating Projects workspace) → assert ProjectContextManager matches and project_events emitted.  
   - **Effort:** Low. **Value:** High (would have caught D-001).

2. **Smoke test: project change propagates**  
   - Create two projects, set project A, navigate to Chat, create chat. Set project B via Projects workspace. Assert Chat list shows project B's chats (or empty).  
   - **Effort:** Medium (requires Qt, mocked DB). **Value:** High.

3. **Gap report rule: project context**  
   - Add "Project Context System" to coverage map; flag if no test covers project switch propagation.  
   - **Effort:** Low. **Value:** Medium.
