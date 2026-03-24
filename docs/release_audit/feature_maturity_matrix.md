# Feature maturity matrix — Linux Desktop Chat

**Roles:** Release Manager + Product Architect.  
**Scope:** Every feature row in `docs/FEATURE_REGISTRY.md` (auto-generated index, stamp 2026-03-22), plus **Command Center (Dashboard)** from `docs/00_map_of_the_system.md` §3 (registered in navigation but absent as its own registry row).  
**Cross-references:** `docs/release_audit/architecture_status.md` (2026-03-24), `docs/FEATURE_REGISTRY.md` columns *Tests*, *Help*, *QA docs*.

---

## Maturity scale

| Level | Meaning |
|-------|---------|
| **5** | Production-ready: strong automated coverage, architecture aligned with guards, reachable in normal GUI navigation, user/help or ops docs, dependencies understood and bounded. |
| **4** | Stable: usable for release with known gaps (polish, partial docs, or non-blocking arch/test debt). |
| **3** | Functional but incomplete: real UI or backend path exists; tests and/or docs and/or architecture integration are thin. |
| **2** | Experimental: intended for builders/QA; behaviour or contracts may change; heavy reliance on optional tooling or scripts. |
| **1** | Abandoned / dead end: no maintained path or deliberately empty shell (not claimed for any registry workspace below). |

**Global context (applies to several features):** `tests/architecture` had **5 failing guards** at last audit (`core`↔theme coupling, `core`→`services` in orchestrator, service→provider-class imports, root entrypoint allowlist). That is **cross-cutting dependency/architecture risk** for model/provider/chat flows—not repeated on every row.

---

## Matrix

| Feature | Workspace ID | Maturity | Issues | Recommendation |
|---------|----------------|----------|--------|----------------|
| **Chat** | `operations_chat` | **4** | Broad tests (+5 more in registry); `ChatPresenter`+port wired but panels still use direct `get_*_service()`; chat stack sensitive to provider/Ollama availability. | Keep presenter/sink expansion; reduce scattered service calls in chat panels; track provider-governance fixes. |
| **Knowledge** | `operations_knowledge` | **4** | Strong tests including chaos/failure; Chroma optional → env instability; RAG stack shared with other features. | Document Chroma-offline behaviour in help; maintain failure-mode tests in CI. |
| **Prompt Studio** | `operations_prompt_studio` | **4** | Good contract/golden/integration coverage; mixed port-driven and `get_prompt_service()` paths (`uses_port_driven_detail()` gating). | Finish port-driven path as default; one integration test matrix for both modes until unified. |
| **Workflows** | `operations_workflows` | **4** | Smoke + substantial `unit/gui` and workflow tests; scheduling (“Geplant”) adds complexity; depends on workflow engine + persistence. | Keep workflow smoke in release checklist; monitor scheduling vs. executor tests. |
| **Deployment** | `operations_deployment` | **4** | Focused unit/service/GUI tests; narrow surface; registry lists no QA docs. | Add short user-facing help topic; confirm panel guardrails stay green when editing dialogs. |
| **Betrieb** (audit / incidents / platform health) | `operations_audit_incidents` | **4** | Dedicated workspace + service/repo tests; help `operations_betrieb`. | Align naming (DE/EN) in docs; extend failure-mode tests for incident ingestion if scope grows. |
| **Agent Tasks** | `operations_agent_tasks` | **4** | Architecture remediation tests + golden paths + contracts; presenter/adapter slices present in `ui_application`. | Continue migrating inspector/runtime panels to ports; keep registry tests updated. |
| **Projects** | `operations_projects` | **4** | Multiple integration/regression/structure tests; central to project context. | Tie help to project-switch UX; add UI smoke for milestone dialogs if user-visible. |
| **Control Center — Models** | `cc_models` | **4** | Good test breadth; **failing provider-orchestrator guard** affects model/catalog services globally; settings/MVP theme path touches `ui_application`→`gui`. | Prioritise fixing `model_orchestrator_service` / `unified_model_catalog_service` provider-class imports; decouple theme from `core` settings. |
| **Control Center — Providers** | `cc_providers` | **3** | Registry lists only **two** test files; same provider-stack instability as Models. | Expand contract/smoke tests for provider workspace; surface health errors consistently in UI. |
| **Control Center — Agents** | `cc_agents` | **4** | Same agent test corpus as Agent Tasks / chat agents; GUI in `agents_ui`. | Keep parity between CC agents and operations agent tasks documentation. |
| **Control Center — Tools** | `cc_tools` | **4** | Solid contract/failure/unit coverage; no backing service in registry (by design). | Document tool execution limits and security expectations in help. |
| **Control Center — Data Stores** | `cc_data_stores` | **4** | Shares RAG/Chroma test story with Knowledge; help present. | Same as Knowledge for optional Chroma. |
| **QA — Test Inventory** | `qa_test_inventory` | **4** | Rich `tests/qa/*` + **QA doc bundle** in registry; operator-oriented. | Treat as internal release gate; keep generated artefacts deterministic in CI. |
| **QA — Coverage Map** | `qa_coverage_map` | **4** | Dedicated coverage_map tests; **no Help key** in registry. | Add help stub or link to `docs/qa/00_map_of_qa_system.md` from UI. |
| **QA — Gap Analysis** | `qa_gap_analysis` | **3** | Depends on `tests/qa/autopilot_v3` and coverage_map; **no Help**; “autopilot” naming implies evolving automation. | Stabilise public UI labels vs. experimental scripts; document what is machine-generated vs. manual. |
| **QA — Incidents** | `qa_incidents` | **3** | **Registry Tests: —**; workspace and panels **are implemented** (`IncidentsWorkspace`, incident inspector). | Add focused unit/UI tests for incident list/detail; add help topic. |
| **QA — Replay Lab** | `qa_replay_lab` | **3** | Only **three** linked tests (CLI + context + binding); power-user workflow; **no Help**. | Expand integration tests for GUI replay path; link to `docs/qa/.../incident_replay` architecture doc from workspace. |
| **Runtime / Debug — EventBus** | `rd_eventbus` | **4** | Strong governance + contract + cross-layer tests; **no Help** in registry. | Add minimal runtime help page describing event semantics for operators. |
| **Runtime / Debug — Logs** | `rd_logs` | **3** | Tests thinly linked (`test_backlog`, `test_streaming_logic`); help `runtime_overview` (shared). | Add targeted UI smoke for log workspace; clarify relationship to autopilot backlog tests. |
| **Runtime / Debug — Metrics** | `rd_metrics` | **4** | Multiple metrics tests; **no Help** in registry. | Add help subsection for metric semantics and failure-mode behaviour. |
| **Runtime / Debug — LLM Calls** | `rd_llm_calls` | **4** | Good contract/chat/QA trace coverage; **no Help**. | Document how traces relate to privacy and local-only storage. |
| **Runtime / Debug — Agent Activity** | `rd_agent_activity` | **3** | **Registry Tests: —**; workspace **implemented** with stream/status/detail panels. | Add tests wired to `AgentActivityMonitor`/EventBus; add help topic. |
| **Runtime / Debug — System Graph** | `rd_system_graph` | **4** | Architecture graph + workflow graph validator tests; **no Help**. | Add operator help explaining graph sources and refresh behaviour. |
| **Settings — Application** | `settings_application` | **4** | Startup/chaos/integration/smoke coverage; **global** coupling risk from `AppSettings`→`app.gui.themes` (failing core↔gui guard). | Move theme-id validation to `core`-safe module or inject validator from GUI bootstrap. |
| **Settings — Appearance** | `settings_appearance` | **4** | UI + regression theme tests; help `settings_overview`. | Same theme decoupling as Application once settings adapter/theme pipeline is refactored. |
| **Settings — AI / Models** | `settings_ai_models` | **4** | Integration/smoke + model router/bindings; **no Help** in registry. | Add settings help for routing/catalog; align with provider governance fixes. |
| **Settings — Data** | `settings_data` | **4** | Shared settings smoke/integration; **no Help** in registry. | Document RAG paths and data directories in help. |
| **Settings — Privacy** | `settings_privacy` | **3** | **Registry Tests: —**; **no Help**; UI is **informational placeholder** (static QLabel copy, no real controls). | Either implement real privacy/telemetry toggles and tests, or downgrade visibility until scope is defined. |
| **Settings — Advanced** | `settings_advanced` | **4** | Same shared settings test bundle as other categories; **no Help** in registry. | Add help for advanced flags; ensure architecture guardrails for advanced panel stay green. |
| **Settings — Project** | `settings_project` | **4** | Strong linkage to project context tests; **no Help** in registry. | Add help for project defaults vs. operations projects workspace. |
| **Settings — Workspace** | `settings_workspace` | **4** | Includes `test_tools_workspace_paths`; **no Help** in registry. | Document workspace path resolution and tool discovery in help. |
| **Command Center (Dashboard)** | *(area `command_center`)* | **4** | Not a separate registry row; `tests/ui/test_command_center_dashboard.py` exists; navigation registry includes dashboard entry. | Add explicit FEATURE_REGISTRY row on next regeneration for traceability. |

---

## Not in `FEATURE_REGISTRY.md` (navigation map only)

These `workspace_id` values appear in `arch_guard_config.GUI_SCREEN_WORKSPACE_MAP` under `runtime_debug` but **not** as separate features in the current registry export:

- `rd_introspection`, `rd_qa_cockpit`, `rd_qa_observability`

**Suggestion:** Regenerate or extend `tools/generate_feature_registry.py` inputs so runtime introspection/QA cockpit surfaces are inventoried like other workspaces.

---

## Summary counts (this matrix)

| Level | Count |
|-------|-------|
| 5 | 0 |
| 4 | 26 |
| 3 | 7 |
| 2 | 0 |
| 1 | 0 |

*(33 feature rows in the table above.)*

**Rationale for no LEVEL 5:** No single vertical satisfies all five criteria simultaneously at “ship with confidence” level—global architecture debt (failing guards), optional external dependencies (Ollama/Chroma), or missing help/tests on several user-visible shells prevents a straight LEVEL 5 call without exception footnotes.

**Rationale for no LEVEL 2 in table:** Experimental automation is confined to QA sub-features still classified **LEVEL 3** (functional but incomplete) because shipped UI exists; a dedicated “labs” flag could justify LEVEL 2 in a future product taxonomy.

**Rationale for no LEVEL 1:** All listed registry workspaces have **implemented** entry code paths; none are orphaned packages in the registry sense.

---

## Criteria → evidence used

| Criterion | Primary evidence |
|-----------|------------------|
| **Test coverage** | `docs/FEATURE_REGISTRY.md` *Tests* column (`—` = none listed); spot checks for implemented-but-unlisted UI (`privacy_category.py`, `incidents_workspace.py`, `agent_activity_workspace.py`). |
| **Architectural cleanliness** | `docs/release_audit/architecture_status.md` (global + settings adapter); per-feature only where specific (e.g. chat presenter mix, provider governance). |
| **User accessibility (GUI)** | Registry *Code* paths under `app/gui/...`; navigation registration per `docs/00_map_of_the_system.md` and `GUI_SCREEN_WORKSPACE_MAP`. |
| **Documentation** | Registry *Help* and *QA docs* columns; absence noted explicitly. |
| **Dependency stability** | Ollama/Chroma/optional services called out where features depend on them; global guard failures called out once in header. |

---

*This matrix is a release-planning aid. It is not a substitute for running `pytest tests/architecture` and the full test suite before tagging a release.*
