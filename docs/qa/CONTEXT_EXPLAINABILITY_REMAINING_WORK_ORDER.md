# Context Explainability – Remaining Work Order

**Stand:** 17. März 2026

Execution order: P0 → P1 → P2. Each item is independent; no refactors.

---

## P0 – Critical Path / Serializer / Determinism

| # | Item | Priority | Exact Reason | Blocking Impact | Affected Files | Required Tests | Done Condition |
|---|------|----------|--------------|-----------------|----------------|----------------|----------------|
| 1 | Request capture in CI gate | P0 | test_request_capture not in context_observability marker; CI does not run capture tests | Regressions in capture (forbidden keys, disabled gating) go undetected in CI | `tests/context/test_request_capture.py` | Existing tests | pytest -m context_observability includes test_request_capture.py |
| 2 | trace_to_dict explicit test | P0 | trace_to_dict has no direct determinism test; only covered indirectly via inspection | Serializer drift (policy_chain, limits) not detected in CI | `tests/context/test_context_resolution_chain_explainability.py` or new `test_context_explanation_serializer.py` | `trace_to_dict(trace)` twice, json.dumps compare; assert identical | New test passes; trace_to_dict determinism asserted |

---

## P1 – Inspection Tooling / Debug Gating

| # | Item | Priority | Exact Reason | Blocking Impact | Affected Files | Required Tests | Done Condition |
|---|------|----------|--------------|-----------------|----------------|----------------|----------------|
| 3 | preview_context_fragment in CI gate | P1 | test_preview_context_fragment not in context_observability marker | Dev script regressions (mode, policy, limits) not run in CI | `tests/scripts/test_preview_context_fragment.py` | Existing tests | pytest -m context_observability includes test_preview_context_fragment.py |
| 4 | load_request_fixture unit tests | P1 | load_request_fixture has no direct tests; validation only exercised via CLI | Schema changes (ALLOWED_KEYS, types) can break without detection | `tests/context/test_request_fixture_loader.py` (new) | `load_request_fixture` valid path; FixtureValidationError on unknown keys, missing chat_id, invalid types | New test file; all 4+ cases pass |
| 5 | CLI snapshot for 4 remaining fixtures | P1 | Only 3 of 7 fixtures have CLI snapshot; profile_strict_minimal, budget_exhausted_request, topic_disabled_request, empty_context_sources missing | Fixture-specific behavior changes undetected | `tests/context/test_context_inspect_cli.py`, `tests/context/expected/context_inspect_*.txt` | 4 new snapshot tests | 4 new tests pass; 4 new expected files |
| 6 | context_explain CLI tests | P1 | context_explain.py has no tests; only context_inspect.py tested | CLI regressions (--format json, --show-*) go undetected | `tests/scripts/test_context_explain_cli.py` (new) | Subprocess: --chat-id 1 --format json; exit 0; JSON has explanation | New test file; subprocess test passes |

---

## P2 – GUI / Doc Sync

| # | Item | Priority | Exact Reason | Blocking Impact | Affected Files | Required Tests | Done Condition |
|---|------|----------|--------------|-----------------|----------------|----------------|----------------|
| 7 | ContextInspectionPanel UI test | P2 | Panel has no test; set_chat_id, set_request, _refresh untested | Panel wiring regressions (e.g. wrong service call) undetected | `tests/context/test_context_inspection_panel.py` or `tests/ui/test_context_inspection_panel.py` | Panel with mock result; set_chat_id → summary displayed | New test passes; panel displays lines |
| 8 | Schema doc inspection_result_to_dict | P2 | CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md documents explainability_to_dict only; inspection_result_to_dict output (trace, formatted_blocks) not documented | Docs mismatch; consumers cannot infer inspection output structure | `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` | None | New section "Inspection Output" with trace, explanation, payload_preview, formatted_blocks |

---

## Execution Sequence

| Step | Item | Action |
|------|------|--------|
| 1 | P0 #1 | Add `pytestmark = pytest.mark.context_observability` to test_request_capture.py |
| 2 | P0 #2 | Add test_trace_to_dict_deterministic in test_context_resolution_chain_explainability.py |
| 3 | P1 #3 | Add `pytestmark = pytest.mark.context_observability` to test_preview_context_fragment.py |
| 4 | P1 #4 | Create test_request_fixture_loader.py with load_request_fixture tests |
| 5 | P1 #5 | Add 4 snapshot tests + expected files for context_inspect CLI |
| 6 | P1 #6 | Create test_context_explain_cli.py with subprocess test |
| 7 | P2 #7 | Create test_context_inspection_panel.py with pytest-qt |
| 8 | P2 #8 | Add "Inspection Output (inspection_result_to_dict)" section to schema doc |
