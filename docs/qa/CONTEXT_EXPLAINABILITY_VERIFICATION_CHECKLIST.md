# Context Explainability – QA Verification Checklist

**Stand:** 17. März 2026

Each item is binary verifiable. Run the referenced test or inspect the referenced file.

---

## 1. Resolver / Trace

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 1.1 | trace.explanation is not None when get_context_explanation returns with return_trace=True | `test_context_explainability.py::test_explanation_exists` |
| 1.2 | trace contains policy_chain fields (source, mode, detail, limits_source, max_*_chars) | `app/chat/context_profiles.py` ChatContextResolutionTrace; `test_context_resolution_chain_explainability.py` |
| 1.3 | winning_source is populated and matches effective policy | `test_context_resolution_chain_explainability.py::test_winning_source_visible_for_effective_policy` |
| 1.4 | candidates list preserves exact priority order (profile_enabled, explicit_context_policy, …) | `test_context_resolution_chain_explainability.py::test_candidate_list_preserves_exact_priority_order` |
| 1.5 | skipped_reason is set for non-winning candidates | `test_context_resolution_chain_explainability.py::test_skipped_candidates_include_skipped_reason` |
| 1.6 | fallback_used is True when individual_settings wins | `test_context_resolution_chain_explainability.py::test_fallback_used_marked_when_no_higher_priority_applied` |

---

## 2. Budget / Compression

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 2.1 | configured_budget_total, effective_budget_total, available_budget_for_context are populated | `test_context_explainability_budget.py::test_budget_fields_populated` |
| 2.2 | available_budget_for_context equals effective minus reserved | `test_context_explainability_budget.py::test_available_budget_consistent_with_reservations` |
| 2.3 | per-source budget_allocated, budget_used, budget_dropped sum correctly | `test_context_explainability_budget.py::test_per_source_budget_accounting_sums` |
| 2.4 | dropped_total_tokens equals sum of dropped_by_source entries | `test_context_explainability_budget.py::test_dropped_total_equals_sum_of_dropped_entries` |
| 2.5 | source ordering matches selection_order (1=project, 2=chat, 3=topic) | `test_context_explainability_budget.py::test_source_ordering_matches_resolver_order` |
| 2.6 | budget exhaustion produces reason in source entry | `test_context_explainability_budget.py::test_skipped_sources_budget_exhaustion_visible` |
| 2.7 | compressions list contains operation, original_chars, final_chars when truncation occurs | `test_context_explainability.py::test_compression_visible` |

---

## 3. Dropped Context

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 3.1 | dropped_by_source contains entries when context excluded by profile | `test_context_explainability.py::test_dropped_context_report_with_profile_restriction` |
| 3.2 | dropped_reasons list is populated when context dropped | `app/services/chat_service.py` _build_dropped_context_report |
| 3.3 | ContextDroppedEntry has source_type, reason, dropped_tokens, source_id | `app/context/explainability/context_explanation.py` ContextDroppedEntry |
| 3.4 | Snapshot 05_budget_exhaustion includes dropped fields | `test_context_explainability_snapshots.py::test_snapshot_05_budget_exhaustion_*` |

---

## 4. Ignored Inputs

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 4.1 | invalid explicit policy produces ignored_inputs entry with reason | `test_context_resolution_chain_explainability.py::test_invalid_explicit_policy_visible_as_ignored_input` |
| 4.2 | missing profile when profile_enabled produces ignored_inputs entry | `test_context_resolution_chain_explainability.py::test_missing_profile_visible_as_ignored_input` |
| 4.3 | ContextIgnoredInputEntry has input_name, input_source, raw_value, reason, resolution_effect | `app/context/explainability/context_explanation.py` ContextIgnoredInputEntry |
| 4.4 | Snapshot 07_invalid_explicit_fallback includes ignored_inputs | `test_context_resolution_chain_explainability.py::test_snapshot_invalid_explicit_value_ignored` |

---

## 5. Serializer

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 5.1 | explanation_to_dict produces identical JSON on two calls with same input | `test_context_resolution_chain_explainability.py::test_json_serializer_output_deterministic` |
| 5.2 | explanation_to_dict key order is resolved_settings, decisions, sources, compressions, warnings, ignored_inputs | `test_context_resolution_chain_explainability.py::test_explanation_to_dict_ordering_contract` |
| 5.3 | inspection_result_to_dict produces identical output on two calls | `test_context_inspection_service.py::test_inspect_as_dict_deterministic` |
| 5.4 | Serializer uses explicit field mapping only (no __dict__ recursion) | `app/context/explainability/context_explanation_serializer.py` |
| 5.5 | trace_to_dict includes explainability_schema_version and policy_chain | `app/context/explainability/context_explanation_serializer.py` trace_to_dict |

---

## 6. Inspection Service

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 6.1 | inspect() returns explanation, trace, payload_preview, formatted blocks | `test_context_inspection_service.py::test_inspect_returns_explanation_trace_payload_preview` |
| 6.2 | inspect_as_dict output is deterministic across runs | `test_context_inspection_service.py::test_inspect_as_dict_deterministic` |
| 6.3 | formatted_blocks contains summary, budget, sources; warnings when present | `test_context_inspection_service.py::test_formatted_blocks_present_and_stable` |
| 6.4 | warnings block is absent when explanation has no warnings | `test_context_inspection_service.py::test_warnings_block_absent_when_no_warnings` |
| 6.5 | payload_preview reflects final payload only (no dropped content) | `test_context_inspection_service.py::test_payload_preview_reflects_final_payload_only` |
| 6.6 | include_payload_preview=False and include_formatted=False skip optional work | `test_context_inspection_service.py::test_inspect_optional_payload_and_formatted` |

---

## 7. CLI

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 7.1 | --chat-id produces text output with [CTX_RESOLUTION] | `test_context_inspect_cli.py::test_text_output_includes_summary` |
| 7.2 | --show-budget includes [CTX_BUDGET] block | `test_context_inspect_cli.py::test_show_budget_includes_budget_block` |
| 7.3 | --show-sources includes [CTX_SOURCES] block | `test_context_inspect_cli.py::test_show_sources_includes_sources_block` |
| 7.4 | --format json returns explainability_schema_version, trace, explanation, payload_preview, formatted_blocks | `test_context_inspect_cli.py::test_format_json_returns_serializer_structure` |
| 7.5 | --fixture loads JSON and produces output | `test_context_inspect_cli.py::test_fixture_loads_request_correctly` |
| 7.6 | Invalid fixture (unknown keys) fails with exit code 1 and error in stderr | `test_context_inspect_cli.py::test_invalid_fixture_fails_deterministically` |
| 7.7 | CLI exits 0 with message when CONTEXT_DEBUG_ENABLED not set | `test_context_debug_flag.py::test_cli_exits_gracefully_when_disabled` |
| 7.8 | CLI runs when CONTEXT_DEBUG_ENABLED=1 | `test_context_debug_flag.py::test_cli_runs_when_enabled` |
| 7.9 | Snapshot for minimal_default fixture matches expected file | `test_context_inspect_cli.py::test_snapshot_minimal_default` |
| 7.10 | Snapshot for explicit_policy_architecture fixture matches expected file | `test_context_inspect_cli.py::test_snapshot_explicit_policy_architecture` |
| 7.11 | Snapshot for invalid_policy_fallback fixture matches expected file | `test_context_inspect_cli.py::test_snapshot_invalid_policy_fallback` |

---

## 8. Fixtures

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 8.1 | 7 JSON fixtures exist in tests/fixtures/context_requests/ | `tests/fixtures/context_requests/*.json` |
| 8.2 | load_request_fixture requires chat_id (int) | `app/context/devtools/request_fixture_loader.py` _validate_types |
| 8.3 | load_request_fixture rejects unknown top-level keys | `app/context/devtools/request_fixture_loader.py` _validate_keys; ALLOWED_KEYS |
| 8.4 | Fixture schema: chat_id, project_id, message, context_policy, context_hint, settings | `app/context/devtools/request_fixture_loader.py` |
| 8.5 | CLI maps context_hint to request_context_hint when building ContextExplainRequest | `scripts/dev/context_inspect.py` _load_request_from_args |

---

## 9. Request Capture

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 9.1 | capture() stores chat_id, project_id, message (truncated), request_context_hint, context_policy | `test_request_capture.py::test_request_stored_after_execution` |
| 9.2 | message truncated to MAX_MESSAGE_CHARS (500) | `test_request_capture.py::test_message_truncated_deterministically` |
| 9.3 | capture does NOT store context payload | `test_request_capture.py::test_no_context_payload_stored` |
| 9.4 | capture does NOT store provider output | `test_request_capture.py::test_no_provider_output_stored` |
| 9.5 | get_last_request returns None when no capture has run | `test_request_capture.py::test_get_last_request_returns_none_if_no_request_executed` |
| 9.6 | get_last_request returns None when CONTEXT_DEBUG_ENABLED not set | `test_context_debug_flag.py::test_disabled_mode_produces_no_inspection_data` |
| 9.7 | capture is called in chat send path (chat_service.py) | `app/services/chat_service.py` ~line 406 |

---

## 10. UI Adapter / Panel

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 10.1 | to_view_model returns summary_lines, budget_lines, source_lines, warning_lines, payload_preview_lines | `test_context_inspection_view_adapter.py::test_adapter_returns_all_sections` |
| 10.2 | View model preserves ordering from formatter output | `test_context_inspection_view_adapter.py::test_ordering_preserved` |
| 10.3 | has_warnings matches presence of warning lines | `test_context_inspection_view_adapter.py::test_warnings_flag_correct` |
| 10.4 | has_payload matches not result.payload_preview.empty | `test_context_inspection_view_adapter.py::test_payload_flag_correct` |
| 10.5 | No data loss between formatter output and view model lines | `test_context_inspection_view_adapter.py::test_no_data_loss_between_formatter_and_view_model` |
| 10.6 | Snapshot view_adapter_lines matches expected | `test_context_inspection_view_adapter.py::test_snapshot_view_model_lines` |
| 10.7 | ContextInspectionViewAdapter has no UI imports | `app/context/inspection/context_inspection_view_adapter.py` |
| 10.8 | ContextInspectionPanel uses ContextInspectionService and ViewAdapter | `app/gui/domains/debug/context_inspection_panel.py` |
| 10.9 | Panel shown in ChatWorkspace only when is_context_debug_enabled() | `app/gui/domains/operations/chat/chat_workspace.py` ~line 623 |

---

## 11. Determinism / Snapshots

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 11.1 | format_context_explanation produces identical output on two calls with same input | `test_context_explainability_budget.py::test_formatted_debug_output_deterministic` |
| 11.2 | Same fixture produces identical JSON across runs | `test_context_resolution_chain_explainability.py::test_json_serializer_output_deterministic` |
| 11.3 | 10 explainability scenarios have formatted, inspection, json snapshots | `test_context_explainability_snapshots.py` test_snapshot_01 through test_snapshot_10 |
| 11.4 | Snapshot files exist in tests/context/expected/explainability_snapshots/ | `tests/context/expected/explainability_snapshots/*.txt`, `*.json` |
| 11.5 | assert_snapshot uses unified diff on mismatch | `tests/context/conftest.py` assert_snapshot |
| 11.6 | No dict/set iteration in serializer (fixed key order) | `app/context/explainability/context_explanation_serializer.py` |

---

## 12. CI / Audit / Docs

| # | Verified if … | File / Test |
|---|---------------|-------------|
| 12.1 | pytest -m context_observability runs without failure | `pytest -m context_observability -v --tb=short` |
| 12.2 | context_observability marker defined in pytest.ini | `pytest.ini` markers |
| 12.3 | .github/workflows/context-observability.yml exists and triggers on push/PR to main, develop | `.github/workflows/context-observability.yml` |
| 12.4 | Workflow runs pytest -m context_observability | `.github/workflows/context-observability.yml` |
| 12.5 | CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md documents explanation, policy_chain, payload_preview | `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` |
| 12.6 | CONTEXT_INSPECTION_WORKFLOW.md documents CLI usage and service entrypoints | `docs/dev/CONTEXT_INSPECTION_WORKFLOW.md` |
| 12.7 | AUDIT_REPORT.md section 9 reflects implementation status | `docs/AUDIT_REPORT.md` |
| 12.8 | CHAT_CONTEXT_EXPLAINABILITY_STATUS.md lists all 18 components with state | `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_STATUS.md` |
