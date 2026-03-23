# DOC DRIFT REPORT

*Generated: 2026-03-20 21:26 UTC* — `python3 tools/doc_drift_check.py`

Vergleich **Ist-Repository** (u. a. `app/`, `tests/`, `tools/`) mit **README.md**, `docs/**`, `help/**`, `docs_manual/**`. Die Codebasis gilt als maßgeblich. Unter `docs/**` werden Pfade nur aus **Backticks** und **Markdown-Links** gelesen (weniger Rauschen als Volltext). „Probable actual path“ ist deterministisch geraten (z. B. eindeutiger Basename unter `app/`, `app/ui/`→`app/gui/`, Icons→`assets/icons/svg/`); bei Unsicherheit steht „—“. Abschnitt **Details** enthält Fundstellen und False-Positive-Hinweise.

## 1. Summary

- **drift_count:** 39
- **blocker_count:** 0
- **high_count:** 0
- **medium_count:** 32
- **low_count:** 7

## 2. Missing Paths

| Documented path | Severity (status) | Probable actual path | First source |
|-----------------|-------------------|----------------------|--------------|
| `app/core/project_context_manager.py` | low | app/core/context/project_context_manager.py | `docs/06_operations_and_qa/UX_BUG_FIXES_PHASE3.md` |
| `app/gui/domains/knowledge/` | low | — | `docs/refactoring/KNOWLEDGE_UI_TO_GUI_ANALYSIS.md` |
| `app/gui/domains/project/` | low | — | `docs/refactoring/PROJECT_UI_TO_GUI_ANALYSIS.md` |
| `app/gui/domains/prompts/` | low | — | `docs/refactoring/PROMPTS_UI_TO_GUI_ANALYSIS.md` |
| `app/gui/settings_backend.py` | low | app/core/config/settings_backend.py | `docs/refactoring/GUI_POST_MIGRATION_AUDIT.md` |
| `app/ui/* (101 distinct paths, aggregated)` | low | app/gui/ | `docs/04_architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md` |
| `app/chat_widget.py` | medium | app/gui/legacy/chat_widget.py | `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md` |
| `app/context/active_project.py` | medium | app/core/context/active_project.py | `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md` |
| `app/core/feature_registry_loader.py` | medium | app/core/navigation/feature_registry_loader.py | `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md` |
| `app/escalation_manager.py` | medium | app/core/models/escalation_manager.py | `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md` |
| `app/file_explorer_widget.py` | medium | app/gui/legacy/file_explorer_widget.py | `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md` |
| `app/gui/domains/operations/chat/panels/session_explorer_panel.py` | medium | — | `docs/04_architecture/DESIGN_SYSTEM_LIGHT.md` |
| `app/gui/domains/settings/settings_nav.py` | medium | — | `docs/04_architecture/SETTINGS_CONSOLIDATION_REPORT.md` |
| `app/gui/icons/svg` | medium | assets/icons/svg/ | `docs/05_developer_guide/PHASE1_CHANGES.md` |
| `app/gui/icons/svg/` | medium | assets/icons/svg/ | `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md` |
| `app/message_widget.py` | medium | app/gui/legacy/message_widget.py | `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md` |
| `app/model_orchestrator.py` | medium | — | `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md` |
| `app/model_registry.py` | medium | — | `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md` |
| `app/model_roles.py` | medium | — | `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md` |
| `app/model_router.py` | medium | — | `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md` |
| `app/project_chat_list_widget.py` | medium | app/gui/legacy/project_chat_list_widget.py | `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md` |
| `app/response_filter.py` | medium | app/core/llm/response_filter.py | `docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md` |
| `app/settings.py` | medium | app/core/config/settings.py | `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md` |
| `app/sidebar_widget.py` | medium | app/gui/legacy/sidebar_widget.py | `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md` |
| `app/tools.py` | medium | — | `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md` |
| `app/web_search.py` | medium | app/tools/web_search.py | `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md` |
| `tests/context/test_context_explanation_serializer.py` | medium | — | `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md` |
| `tests/context/test_context_inspection_panel.py` | medium | — | `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md` |
| `tests/context/test_request_fixture_loader.py` | medium | — | `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md` |
| `tests/failure_modes/test_foo.py` | medium | — | `docs/qa/architecture/coverage/QA_COVERAGE_MAP_GENERATOR.md` |
| `tests/help/` | medium | — | `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md` |
| `tests/scripts/test_context_explain_cli.py` | medium | — | `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md` |
| `tests/ui/test_context_inspection_panel.py` | medium | — | `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md` |

### Details

- **app/core/project_context_manager.py**
  - Referenced in: docs/06_operations_and_qa/UX_BUG_FIXES_PHASE3.md. Suggested path: `app/core/context/project_context_manager.py`
  - Source: `docs/06_operations_and_qa/UX_BUG_FIXES_PHASE3.md`
  - Notes: Possible historical / migration context; verify before changing.
- **app/gui/domains/knowledge/**
  - Referenced in: docs/refactoring/KNOWLEDGE_UI_TO_GUI_ANALYSIS.md. Suggested path: —
  - Source: `docs/refactoring/KNOWLEDGE_UI_TO_GUI_ANALYSIS.md`
  - Notes: Possible historical / migration context; verify before changing.
- **app/gui/domains/project/**
  - Referenced in: docs/refactoring/PROJECT_UI_TO_GUI_ANALYSIS.md. Suggested path: —
  - Source: `docs/refactoring/PROJECT_UI_TO_GUI_ANALYSIS.md`
  - Notes: Possible historical / migration context; verify before changing.
- **app/gui/domains/prompts/**
  - Referenced in: docs/refactoring/PROMPTS_UI_TO_GUI_ANALYSIS.md. Suggested path: —
  - Source: `docs/refactoring/PROMPTS_UI_TO_GUI_ANALYSIS.md`
  - Notes: Possible historical / migration context; verify before changing.
- **app/gui/settings_backend.py**
  - Referenced in: docs/refactoring/GUI_POST_MIGRATION_AUDIT.md, docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md. Suggested path: `app/core/config/settings_backend.py`
  - Source: `docs/refactoring/GUI_POST_MIGRATION_AUDIT.md`
  - Notes: Possible historical / migration context; verify before changing.
- **app/ui/* (101 distinct paths, aggregated)**
  - Referenced in: docs/04_architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md, docs/04_architecture/AGENTS_UI_PHASE1_MIGRATION_REPORT.md, docs/04_architecture/AGENTS_UI_PHASE1_VALIDATION.md, docs/04_architecture/AGENTS_UI_PHASE2_ANALYSIS.md, docs/04_architecture/AGENTS_UI_PHASE2_EXECUTION.md, docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/CHAT_UI_PHASE1_ANALYSIS.md, docs/04_architecture/CHAT_UI_PHASE2_MIGRATION_REPORT.md, docs/04_architecture/CHAT_UI_PHASE3_MIGRATION_REPORT.md, docs/04_architecture/CHAT_UI_PHASE4_SIDEPANEL_REPORT.md …. Real tree: `app/gui/`.
  - Source: `docs/04_architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md`
  - Notes: Migration / audit docs often retain app/ui/ paths. False positive if text is explicitly historical.
- **app/chat_widget.py**
  - Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/GUI_ARCHITECTURE_GUARDRAILS.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md, docs/05_developer_guide/PHASE1_CHANGES.md. Suggested path: `app/gui/legacy/chat_widget.py`
  - Source: `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`
- **app/context/active_project.py**
  - Referenced in: docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md. Suggested path: `app/core/context/active_project.py`
  - Source: `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md`
- **app/core/feature_registry_loader.py**
  - Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md. Suggested path: `app/core/navigation/feature_registry_loader.py`
  - Source: `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`
- **app/escalation_manager.py**
  - Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md. Suggested path: `app/core/models/escalation_manager.py`
  - Source: `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`
- **app/file_explorer_widget.py**
  - Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md. Suggested path: `app/gui/legacy/file_explorer_widget.py`
  - Source: `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`
- **app/gui/domains/operations/chat/panels/session_explorer_panel.py**
  - Referenced in: docs/04_architecture/DESIGN_SYSTEM_LIGHT.md, docs/06_operations_and_qa/CHAT_LIST_PROJECT_UX.md, docs/06_operations_and_qa/UX_EMPTY_STATE_IMPLEMENTATION.md, docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md. Suggested path: —
  - Source: `docs/04_architecture/DESIGN_SYSTEM_LIGHT.md`
- **app/gui/domains/settings/settings_nav.py**
  - Referenced in: docs/04_architecture/SETTINGS_CONSOLIDATION_REPORT.md, docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md. Suggested path: —
  - Source: `docs/04_architecture/SETTINGS_CONSOLIDATION_REPORT.md`
- **app/gui/icons/svg**
  - Referenced in: docs/05_developer_guide/PHASE1_CHANGES.md. Suggested path: `assets/icons/svg/`
  - Source: `docs/05_developer_guide/PHASE1_CHANGES.md`
- **app/gui/icons/svg/**
  - Referenced in: docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md, docs/06_operations_and_qa/CONSOLIDATION_REPORT.md, docs/06_operations_and_qa/CONSOLIDATION_RULES.md. Suggested path: `assets/icons/svg/`
  - Source: `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`
- **app/message_widget.py**
  - Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md. Suggested path: `app/gui/legacy/message_widget.py`
  - Source: `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`
- **app/model_orchestrator.py**
  - Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md, docs/FEATURES/providers.md. Suggested path: —
  - Source: `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`
- **app/model_registry.py**
  - Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md. Suggested path: —
  - Source: `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`
- **app/model_roles.py**
  - Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md. Suggested path: —
  - Source: `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`
- **app/model_router.py**
  - Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md. Suggested path: —
  - Source: `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`
- **app/project_chat_list_widget.py**
  - Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md. Suggested path: `app/gui/legacy/project_chat_list_widget.py`
  - Source: `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`
- **app/response_filter.py**
  - Referenced in: docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md. Suggested path: `app/core/llm/response_filter.py`
  - Source: `docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md`
- **app/settings.py**
  - Referenced in: docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md, docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md, docs/05_developer_guide/PHASE1_CHANGES.md, docs/CHANGELOG_NORMALIZATION.md, docs/DOC_GAP_ANALYSIS.md. Suggested path: `app/core/config/settings.py`
  - Source: `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md`
- **app/sidebar_widget.py**
  - Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md. Suggested path: `app/gui/legacy/sidebar_widget.py`
  - Source: `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`
- **app/tools.py**
  - Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md. Suggested path: —
  - Source: `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`
- **app/web_search.py**
  - Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md. Suggested path: `app/tools/web_search.py`
  - Source: `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`
- **tests/context/test_context_explanation_serializer.py**
  - Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md. Suggested path: —
  - Source: `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`
- **tests/context/test_context_inspection_panel.py**
  - Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md, docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md. Suggested path: —
  - Source: `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`
- **tests/context/test_request_fixture_loader.py**
  - Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md, docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md. Suggested path: —
  - Source: `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`
- **tests/failure_modes/test_foo.py**
  - Referenced in: docs/qa/architecture/coverage/QA_COVERAGE_MAP_GENERATOR.md, docs/qa/governance/incident_schemas/BINDINGS_JSON_FIELD_STANDARD.md, docs/qa/governance/incident_schemas/INCIDENT_YAML_FIELD_STANDARD.md. Suggested path: —
  - Source: `docs/qa/architecture/coverage/QA_COVERAGE_MAP_GENERATOR.md`
- **tests/help/**
  - Referenced in: docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md. Suggested path: —
  - Source: `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`
- **tests/scripts/test_context_explain_cli.py**
  - Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md, docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md. Suggested path: —
  - Source: `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`
- **tests/ui/test_context_inspection_panel.py**
  - Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md, docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md. Suggested path: —
  - Source: `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`

## 3. Missing Documentation Coverage

- **app/core/ has 43 Python files but no docs_manual/modules/core/README.md**
  - Source: `app/`
  - Notes: Heuristic threshold; add manual or lower threshold in tools/doc_drift_check.py if intentional.
- **app/pipelines/ has 17 Python files but no docs_manual/modules/pipelines/README.md**
  - Source: `app/`
  - Notes: Heuristic threshold; add manual or lower threshold in tools/doc_drift_check.py if intentional.
- **app/services/ has 14 Python files but no docs_manual/modules/services/README.md**
  - Source: `app/`
  - Notes: Heuristic threshold; add manual or lower threshold in tools/doc_drift_check.py if intentional.

## 4. Outdated Structural Claims

- **Numeric settings claim may be stale: 2 (code has 8 categories)**
  - Detail: Match: '2 Settings-Kategorien'
  - Source: `docs/04_architecture/SETTINGS_AND_WORKSPACES_HARDENING_ANALYSIS.md`
  - Notes: Heuristic; confirm context (may refer to workspaces, not categories).
- **Documentation cites removed `app/ui/` filesystem tree**
  - Detail: Aggregated 101 missing paths; current GUI code lives under `app/gui/`.
  - Source: `docs/**, docs_manual/**, help/**`
  - Notes: Prefer curating current-structure docs vs. retaining obsolete path lists in active manuals.

## 5. Generated File Drift

| File | Status | Notes |
|------|--------|-------|
| `docs/SYSTEM_MAP.md` | review | SYSTEM_MAP missing entry: app/diagnostics/ |
| `docs/TRACE_MAP.md` | ok | — |
| `docs/FEATURE_REGISTRY.md` | ok | — |

## 6. Recommended Fixes

- `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`: `app/chat_widget.py` — Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/GUI_ARCHITECTURE_GUARDRAILS.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md, docs/05_developer_guide/PHASE1_CHANGES.md. Suggested path: `app/gui/legacy/chat_widget.py`
- `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md`: `app/context/active_project.py` — Referenced in: docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md. Suggested path: `app/core/context/active_project.py`
- `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`: `app/core/feature_registry_loader.py` — Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md. Suggested path: `app/core/navigation/feature_registry_loader.py`
- `docs/06_operations_and_qa/UX_BUG_FIXES_PHASE3.md`: `app/core/project_context_manager.py` — Referenced in: docs/06_operations_and_qa/UX_BUG_FIXES_PHASE3.md. Suggested path: `app/core/context/project_context_manager.py`
- `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`: `app/escalation_manager.py` — Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md. Suggested path: `app/core/models/escalation_manager.py`
- `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`: `app/file_explorer_widget.py` — Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md. Suggested path: `app/gui/legacy/file_explorer_widget.py`
- `docs/refactoring/KNOWLEDGE_UI_TO_GUI_ANALYSIS.md`: `app/gui/domains/knowledge/` — Referenced in: docs/refactoring/KNOWLEDGE_UI_TO_GUI_ANALYSIS.md. Suggested path: —
- `docs/04_architecture/DESIGN_SYSTEM_LIGHT.md`: `app/gui/domains/operations/chat/panels/session_explorer_panel.py` — Referenced in: docs/04_architecture/DESIGN_SYSTEM_LIGHT.md, docs/06_operations_and_qa/CHAT_LIST_PROJECT_UX.md, docs/06_operations_and_qa/UX_EMPTY_STATE_IMPLEMENTATION.md, docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md. Suggested path: —
- `docs/refactoring/PROJECT_UI_TO_GUI_ANALYSIS.md`: `app/gui/domains/project/` — Referenced in: docs/refactoring/PROJECT_UI_TO_GUI_ANALYSIS.md. Suggested path: —
- `docs/refactoring/PROMPTS_UI_TO_GUI_ANALYSIS.md`: `app/gui/domains/prompts/` — Referenced in: docs/refactoring/PROMPTS_UI_TO_GUI_ANALYSIS.md. Suggested path: —
- `docs/04_architecture/SETTINGS_CONSOLIDATION_REPORT.md`: `app/gui/domains/settings/settings_nav.py` — Referenced in: docs/04_architecture/SETTINGS_CONSOLIDATION_REPORT.md, docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md. Suggested path: —
- `docs/05_developer_guide/PHASE1_CHANGES.md`: `app/gui/icons/svg` — Referenced in: docs/05_developer_guide/PHASE1_CHANGES.md. Suggested path: `assets/icons/svg/`
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`: `app/gui/icons/svg/` — Referenced in: docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md, docs/06_operations_and_qa/CONSOLIDATION_REPORT.md, docs/06_operations_and_qa/CONSOLIDATION_RULES.md. Suggested path: `assets/icons/svg/`
- `docs/refactoring/GUI_POST_MIGRATION_AUDIT.md`: `app/gui/settings_backend.py` — Referenced in: docs/refactoring/GUI_POST_MIGRATION_AUDIT.md, docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md. Suggested path: `app/core/config/settings_backend.py`
- `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`: `app/message_widget.py` — Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md. Suggested path: `app/gui/legacy/message_widget.py`
- `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`: `app/model_orchestrator.py` — Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md, docs/FEATURES/providers.md. Suggested path: —
- `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`: `app/model_registry.py` — Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md. Suggested path: —
- `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`: `app/model_roles.py` — Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md. Suggested path: —
- `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`: `app/model_router.py` — Referenced in: docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md. Suggested path: —
- `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`: `app/project_chat_list_widget.py` — Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md. Suggested path: `app/gui/legacy/project_chat_list_widget.py`
- `docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md`: `app/response_filter.py` — Referenced in: docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md. Suggested path: `app/core/llm/response_filter.py`
- `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md`: `app/settings.py` — Referenced in: docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md, docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md, docs/05_developer_guide/PHASE1_CHANGES.md, docs/CHANGELOG_NORMALIZATION.md, docs/DOC_GAP_ANALYSIS.md. Suggested path: `app/core/config/settings.py`
- `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`: `app/sidebar_widget.py` — Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md, docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md. Suggested path: `app/gui/legacy/sidebar_widget.py`
- `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`: `app/tools.py` — Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md. Suggested path: —
- `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`: `app/web_search.py` — Referenced in: docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md. Suggested path: `app/tools/web_search.py`
- `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`: `tests/context/test_context_explanation_serializer.py` — Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md. Suggested path: —
- `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`: `tests/context/test_context_inspection_panel.py` — Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md, docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md. Suggested path: —
- `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`: `tests/context/test_request_fixture_loader.py` — Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md, docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md. Suggested path: —
- `docs/qa/architecture/coverage/QA_COVERAGE_MAP_GENERATOR.md`: `tests/failure_modes/test_foo.py` — Referenced in: docs/qa/architecture/coverage/QA_COVERAGE_MAP_GENERATOR.md, docs/qa/governance/incident_schemas/BINDINGS_JSON_FIELD_STANDARD.md, docs/qa/governance/incident_schemas/INCIDENT_YAML_FIELD_STANDARD.md. Suggested path: —
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`: `tests/help/` — Referenced in: docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md. Suggested path: —
- `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`: `tests/scripts/test_context_explain_cli.py` — Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md, docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md. Suggested path: —
- `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`: `tests/ui/test_context_inspection_panel.py` — Referenced in: docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md, docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md. Suggested path: —
- Regenerate system map: `python3 tools/generate_system_map.py`
