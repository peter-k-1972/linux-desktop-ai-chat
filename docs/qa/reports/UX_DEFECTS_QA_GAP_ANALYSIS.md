# UX/UI Defects – QA Gap Analysis

**Date:** 2026-03-16  
**Source:** UX_ACCEPTANCE_REVIEW_REPORT.md  
**Purpose:** Map identified UX/UI defects to existing QA architecture; identify detection gaps and improvement opportunities.

---

## QA System Overview (Relevant Components)

| Component | Purpose | Coverage Focus |
|-----------|---------|----------------|
| **Test Inventory** | Catalogue all tests; map to subsystem, failure_class, test_domain | Backend, RAG, Chat, Agents, Debug, etc. |
| **Coverage Map** | Aggregate coverage by failure_class, guard, regression_requirement, replay_binding | Failure modes, regression, guards |
| **Gap Report** | Prioritized gaps (failure_class, orphan, replay) | Test coverage gaps |
| **Audit Report** | Architecture/implementation review | High-level structure |
| **GUI Architecture Guardrails** | PR review rules (G-1 to G-15) | Docking, routing, panel placement, no duplicate structures |
| **Architecture Drift Sentinels** | Meta-tests for EventType, marker discipline | Contract drift, marker violations |
| **Smoke Tests** | Shell startup, WorkspaceHost area switching | Basic GUI reachability |
| **UI Tests** | Command center adapter, chat/agent UI behavior | Adapter logic, widget behavior |
| **Incident/Replay** | Runtime failures, failure_class binding | Production incidents |

**Subsystem taxonomy (Test Inventory):** Agentensystem, Chat, Debug/EventBus, Metrics, Persistenz/SQLite, Prompt-System, Provider/Ollama, RAG, Startup/Bootstrap, Tools. **No "GUI", "Navigation", "Settings", or "UX" subsystem.**

---

## Defect-by-Defect Analysis

### Defect 1: Project Switcher in both TopBar and Sidebar (duplicate)

| Field | Value |
|-------|-------|
| **Defect summary** | Project Switcher appears in TopBar and Sidebar; redundant placement. |
| **Defect class** | UX-NAV, UX-WORKFLOW |
| **Severity** | Major |
| **Expected QA detection point** | UI smoke test (assert single ProjectSwitcher instance); GUI Guardrail (no duplicate UI elements); integration test (sidebar vs topbar widget count). |
| **Actual QA detection status** | Not detected. Smoke tests verify WorkspaceHost shows areas; they do not assert widget uniqueness or placement. Guardrails G-15.2 forbid "doppelte Strukturen" but in migration context (alt vs new); no explicit rule for duplicate UI elements. |
| **Classification** | **DETECTABLE BUT MISSED** |
| **Recommendation** | Add smoke/integration assertion: `assert count(ProjectSwitcherButton instances) == 1` after MainWindow creation. Extend GUI Guardrails with rule: "Kein doppeltes UI-Element an verschiedenen Orten (z.B. Project Switcher nur an einer Stelle)." |

---

### Defect 2: Settings – no Application/Project/Workspace separation

| Field | Value |
|-------|-------|
| **Defect summary** | Only Application-level settings; no Project or Workspace settings structure. |
| **Defect class** | UX-ARCH, INT-DATA |
| **Severity** | Critical |
| **Expected QA detection point** | Architecture audit rule (UX_CONCEPT compliance); Gap Report (UX architecture axis); integration test asserting Settings categories include project/workspace. |
| **Actual QA detection status** | Not detected. Coverage Map has no UX/architecture axis. Gap Report focuses on failure_class, guard, regression. No audit rule checks UX_CONCEPT or Settings structure. Test Inventory/Coverage Map subsystems do not include "Settings" or "UX". |
| **Classification** | **NOT CURRENTLY DETECTABLE** |
| **Recommendation** | Introduce **UX Architecture Audit** as periodic check: compare implementation against UX_CONCEPT (e.g., Settings must have Application | Project | Workspace). Add to Gap Report or new "UX_GAP_REPORT" with architecture compliance axis. Consider Architecture Drift Sentinel: "Settings categories must include settings_project, settings_workspace when UX_CONCEPT requires it." |

---

### Defect 3: Project Hub – overlapping entry points and inconsistent naming

| Field | Value |
|-------|-------|
| **Defect summary** | Project Hub Screen and Project Overview (Operations/Projects) overlap; sidebar labels "Overview", "Active Project", "Project Overview" inconsistent. |
| **Defect class** | UX-NAV, UX-LABEL |
| **Severity** | Major |
| **Expected QA detection point** | UI smoke test (sidebar nav items match expected labels); audit rule (no overlapping nav targets); Gap Report (naming consistency). |
| **Actual QA detection status** | Not detected. Smoke tests check area switching, not label content. No automated check for nav label consistency or overlap. Guardrails cover routing structure, not UX copy. |
| **Classification** | **NOT CURRENTLY DETECTABLE** |
| **Recommendation** | Add **sidebar config snapshot test**: assert `sidebar_config.get_sidebar_sections()` yields expected PROJECT section labels (e.g., no duplicate "Overview"/"Project Overview"). Introduce UX naming convention in Guardrails: "Nav labels must be unique and non-overlapping within a section." |

---

### Defect 4: Knowledge / Prompt Studio / Agent – Settings placeholder (dead-end UI)

| Field | Value |
|-------|-------|
| **Defect summary** | Knowledge, Prompt Studio, Agent workspaces expose Settings in nav but show placeholder ("Coming soon", "implement section-specific UI here"). |
| **Defect class** | UX-EMPTY |
| **Severity** | Major |
| **Expected QA detection point** | UI integration test (no nav item leads to placeholder-only content); audit rule (no "Coming soon" in production nav); static analysis (detect placeholder text in nav targets). |
| **Actual QA detection status** | Not detected. UI tests focus on adapter and widget behavior, not nav→content consistency. No rule forbids placeholders in nav. ARCHITECTURE_DRIFT_SENTINELS lists "Neuer UI-Pfad ohne Behavior-Test" as planned but not implemented. |
| **Classification** | **DETECTABLE BUT MISSED** |
| **Recommendation** | Add **placeholder detection**: grep/assert no "Coming soon", "implement section-specific UI here", "Content panel – implement" in code paths reachable from nav. Alternatively: if nav item exists, content must not be KnowledgeContentPlaceholder or equivalent. Add Guardrail: "Nav items must not lead to placeholder-only content; remove from nav until implemented." |

---

### Defect 5: Project context payload – listeners receive project_id only

| Field | Value |
|-------|-------|
| **Defect summary** | project_events payload is `{"project_id": ...}`; listeners must call get_active_project() for full data. |
| **Defect class** | INT-CONTEXT |
| **Severity** | Minor |
| **Expected QA detection point** | Contract test (payload schema); unit test (listener behavior with payload). |
| **Actual QA detection status** | Not detected. No contract for project_events payload. EventType contract exists for debug events, not project events. |
| **Classification** | **OUT OF QA SCOPE** (design choice, not defect) |
| **Recommendation** | Low priority. If formalized: add contract test for project_context_changed payload schema. Document listener contract in code. |

---

### Defect 6: Chat – mixed DE/EN labels (Ungrouped vs Archiviert)

| Field | Value |
|-------|-------|
| **Defect summary** | "Ungrouped" (EN) vs "Archiviert", "Angeheftet" (DE) in Chat nav. |
| **Defect class** | UX-LABEL |
| **Severity** | Minor |
| **Expected QA detection point** | L10n/i18n test; static analysis (language consistency); manual UX review. |
| **Actual QA detection status** | Not detected. No i18n or language-consistency tests. |
| **Classification** | **OUT OF QA SCOPE** (convention, not functional defect) |
| **Recommendation** | If language consistency is policy: add i18n test or lint rule. Otherwise: manual UX review. |

---

### Defect 7: _find_workspace_host() – fragile parent traversal

| Field | Value |
|-------|-------|
| **Defect summary** | ProjectHubPage and ProjectOverviewPanel traverse parent hierarchy to find WorkspaceHost; may fail if widget tree changes. |
| **Defect class** | QA-MISS, INT-CONTEXT |
| **Severity** | Minor |
| **Expected QA detection point** | Integration test (Hub→Workspace navigation with context); refactoring test (widget tree change breaks traversal). |
| **Actual QA detection status** | Not detected. No test exercises Hub→Chat/Prompt/Knowledge navigation with pending context. Golden path tests exist for chat/agent but not for Project Hub quick actions. |
| **Classification** | **DETECTABLE BUT MISSED** |
| **Recommendation** | Add **golden path test**: Project Hub → click Recent Chat → Chat workspace opens with that chat. Project Hub → Quick Action "New Chat" → Chat workspace. Covers open_with_context and _find_workspace_host. |

---

### Defect 8: Control Center vs Operations – Agents placement

| Field | Value |
|-------|-------|
| **Defect summary** | UX_CONCEPT: Agents in Control Center (design) and Operations (tasks). Sidebar has "Agents" under WORKSPACE only. |
| **Defect class** | UX-ARCH |
| **Severity** | Minor |
| **Expected QA detection point** | Architecture audit (UX_CONCEPT vs sidebar_config); Gap Report (architecture compliance). |
| **Actual QA detection status** | Not detected. No automated UX_CONCEPT compliance check. |
| **Classification** | **NOT CURRENTLY DETECTABLE** |
| **Recommendation** | Add UX architecture compliance check: sidebar_config vs UX_CONCEPT expected structure. Document deviation or fix. |

---

## Summary Table

| Defect | Class | Severity | Classification | Expected Detection Point |
|--------|-------|----------|----------------|--------------------------|
| Project Switcher duplicate | UX-NAV | Major | DETECTABLE BUT MISSED | Smoke/integration test, Guardrail |
| Settings separation | UX-ARCH | Critical | NOT CURRENTLY DETECTABLE | UX audit, Gap Report axis |
| Project Hub overlap/naming | UX-NAV, UX-LABEL | Major | NOT CURRENTLY DETECTABLE | Sidebar config test, audit |
| Placeholder UI (Knowledge/Prompt/Agent) | UX-EMPTY | Major | DETECTABLE BUT MISSED | Placeholder detection, Guardrail |
| Project context payload | INT-CONTEXT | Minor | OUT OF QA SCOPE | Contract test (optional) |
| Mixed DE/EN labels | UX-LABEL | Minor | OUT OF QA SCOPE | i18n test (optional) |
| _find_workspace_host fragility | QA-MISS | Minor | DETECTABLE BUT MISSED | Golden path test |
| Agents placement | UX-ARCH | Minor | NOT CURRENTLY DETECTABLE | UX compliance check |

---

## Top Recurring QA Blind Spots

1. **No UX/architecture axis in QA**  
   Coverage Map, Gap Report, and Test Inventory focus on failure_class, subsystem (backend), regression, guards. No axis for UX structure, nav consistency, or UX_CONCEPT compliance.

2. **UI tests are adapter- and widget-focused, not UX-flow-focused**  
   UI tests cover adapter loading, widget behavior. They do not assert nav structure, duplicate elements, placeholder content, or Hub→Workspace navigation flows.

3. **Guardrails are structural, not UX-semantic**  
   Guardrails forbid duplicate *code* structures (alt vs new), wrong paths, wrong base classes. They do not forbid duplicate *UI* elements, placeholder nav items, or inconsistent labels.

4. **No UX_CONCEPT compliance automation**  
   UX_CONCEPT.md defines target architecture. No automated check compares implementation (sidebar_config, settings categories, workspace nav) against it.

5. **Smoke tests are minimal**  
   Smoke tests verify shell starts and areas switch. They do not assert widget count, nav content, or Settings structure.

---

## Highest-Value Additions to QA

| Priority | Addition | Effort | Impact |
|----------|----------|--------|--------|
| 1 | **UX Architecture Compliance Check** – Script or test comparing sidebar_config, settings_navigation, workspace nav against UX_CONCEPT (or derived spec). Run in CI or pre-merge. | Medium | Critical defects (Settings, nav structure) |
| 2 | **Placeholder Detection** – Assert no "Coming soon", "implement section-specific UI" in nav-reachable code. Or: nav items must not target placeholder-only widgets. | Low | Major placeholder defects |
| 3 | **Project Hub → Workspace Golden Path** – Integration test: set pending context, show_area(OPERATIONS, workspace_id), assert widget.open_with_context called and content correct. | Medium | Context sync, _find_workspace_host |
| 4 | **Single-Instance Assertions** – Smoke/integration: assert exactly one ProjectSwitcherButton (or other global UI elements) after MainWindow creation. | Low | Duplicate UI elements |
| 5 | **Sidebar Config Snapshot Test** – Assert PROJECT section labels, no duplicates, expected structure. Catches nav renames and overlap. | Low | Naming consistency |

---

## Is the UX Architecture Sufficiently Protected by Current QA?

**No.**

| Aspect | Current QA | Gap |
|--------|-------------|-----|
| **UX structure (Settings, nav)** | Not covered | No UX axis in Coverage/Gap; no UX_CONCEPT compliance |
| **Duplicate UI elements** | Not covered | No widget-count or placement assertions |
| **Placeholder / dead-end UI** | Not covered | No placeholder detection |
| **Nav→content consistency** | Partially (area switching) | No check that nav items lead to real content |
| **Hub→Workspace context flow** | Not covered | No golden path for open_with_context |
| **Naming consistency** | Not covered | No i18n or label consistency tests |

**Conclusion:** The QA system is strong for backend, failure modes, regression, and structural GUI rules (Guardrails). It does **not** protect UX architecture, nav consistency, or UX_CONCEPT compliance. The identified defects are mostly **DETECTABLE BUT MISSED** or **NOT CURRENTLY DETECTABLE** because QA has no UX-focused automation.

**Recommendation:** Introduce a **UX QA layer** – lightweight checks (sidebar config, placeholder detection, single-instance assertions, Hub golden path) plus an optional **UX Architecture Compliance** script run periodically or in CI.
