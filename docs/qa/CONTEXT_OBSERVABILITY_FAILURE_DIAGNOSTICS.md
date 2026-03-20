# Context Observability – Failure Diagnostics Contract

**Purpose:** When a QA failure occurs, developers know exactly which artifact to inspect first.

---

## 1. Primary Failure Classes

| Class | Symptom |
|-------|---------|
| missing explanation | `trace.explanation` is None or empty |
| wrong winning source | `winning_source` does not match expected priority |
| ordering drift | sources or keys in wrong order |
| budget accounting mismatch | budget fields inconsistent or sum mismatch |
| dropped-context mismatch | `dropped_total_tokens` ≠ sum of `dropped_by_source`; wrong dropped entries |
| serializer drift | `explanation_to_dict` / `inspection_result_to_dict` non-deterministic |
| snapshot drift | formatted text or JSON differs from golden file |
| request capture leakage | capture stores forbidden keys; `get_last_request` returns data when disabled |

---

## 2. Per-Failure-Class Diagnostics

### 2.1 Missing explanation

| Field | Value |
|-------|-------|
| **Likely source module** | `app.services.chat_service` |
| **First files to inspect** | `app/services/chat_service.py` (get_context_explanation, _build_explanation), `app/services/context_explain_service.py` |
| **Expected invariants** | `trace.explanation` is never None when resolution ran; `ContextExplanation()` used as fallback when no resolver path |
| **Related tests** | `test_explanation_exists`, `test_inspect_returns_explanation_trace_payload_preview` |
| **Behavior vs observability** | Observability only; resolution may still produce fragment |

---

### 2.2 Wrong winning source

| Field | Value |
|-------|-------|
| **Likely source module** | `app.services.chat_service` |
| **First files to inspect** | `app/services/chat_service.py` (winning_idx, _PRIORITY_SOURCES, resolve_chat_context_profile), `app/chat/context_profiles.py`, `app/chat/context_policies.py` |
| **Expected invariants** | `winning_source` ∈ {profile_enabled, explicit_context_policy, chat_default_context_policy, project_default_context_policy, request_context_hint, individual_settings}; exactly one candidate has `applied=True` per setting |
| **Related tests** | `test_winning_source_visible_for_effective_policy`, `test_fallback_used_marked_when_no_higher_priority_applied`, `test_snapshot_explicit_policy_wins`, `test_snapshot_profile_wins` |
| **Behavior vs observability** | **Behavior affected** – wrong winning source implies wrong effective mode/detail/policy |

---

### 2.3 Ordering drift

| Field | Value |
|-------|-------|
| **Likely source module** | `app.context.explainability.context_explanation_serializer`, `app.context.debug.context_debug` |
| **First files to inspect** | `app/context/explainability/context_explanation_serializer.py` (_sources_by_selection_order, key order), `app/context/debug/context_debug.py` (_sources_by_selection_order) |
| **Expected invariants** | resolved_settings: mode, detail_level, policy, project_enabled, chat_enabled, topic_enabled; sources: by selection_order (1=project, 2=chat, 3=topic); dict keys: fixed order, no dict/set iteration |
| **Related tests** | `test_explanation_to_dict_ordering_contract`, `test_source_ordering_matches_resolver_order`, `test_ordering_preserved` |
| **Behavior vs observability** | Observability only; resolution order unchanged |

---

### 2.4 Budget accounting mismatch

| Field | Value |
|-------|-------|
| **Likely source module** | `app.services.chat_service` |
| **First files to inspect** | `app/services/chat_service.py` (compute_budget_accounting, _explanation_with_budget), `app/chat/context_limits.py`, `app/chat/context_policies.py` |
| **Expected invariants** | `available_budget_for_context` = effective − reserved_system − reserved_user; `dropped_total_tokens` = sum(dropped_tokens for e in dropped_by_source) when both populated; per-source budget_allocated/budget_used/budget_dropped consistent |
| **Related tests** | `test_budget_fields_populated`, `test_available_budget_consistent_with_reservations`, `test_dropped_total_equals_sum_of_dropped_entries`, `test_per_source_budget_accounting_sums` |
| **Behavior vs observability** | Observability only; actual truncation logic separate |

---

### 2.5 Dropped-context mismatch

| Field | Value |
|-------|-------|
| **Likely source module** | `app.services.chat_service` |
| **First files to inspect** | `app/services/chat_service.py` (_build_dropped_context_report, dropped_by_source construction), `app/context/explainability/context_explanation.py` (ContextDroppedEntry) |
| **Expected invariants** | `dropped_total_tokens` equals sum of `dropped_by_source[].dropped_tokens`; each dropped entry has source_type, reason; no duplicate source_type+reason for same drop |
| **Related tests** | `test_dropped_context_report_with_profile_restriction`, `test_dropped_total_equals_sum_of_dropped_entries`, `test_skipped_sources_budget_exhaustion_visible` |
| **Behavior vs observability** | Observability only; actual drop behavior unchanged |

---

### 2.6 Serializer drift

| Field | Value |
|-------|-------|
| **Likely source module** | `app.context.explainability.context_explanation_serializer`, `app.context.explainability.context_inspection_serializer` |
| **First files to inspect** | `app/context/explainability/context_explanation_serializer.py`, `app/context/explainability/context_inspection_serializer.py` |
| **Expected invariants** | Same input → same dict; same dict → same JSON (with sort_keys); no dict/set iteration; no timestamp/random injection |
| **Related tests** | `test_json_serializer_output_deterministic`, `test_inspect_as_dict_deterministic`, `test_formatted_debug_output_deterministic` |
| **Behavior vs observability** | Observability only |

---

### 2.7 Snapshot drift

| Field | Value |
|-------|-------|
| **Likely source module** | Resolver, formatter, or serializer (depends on which surface failed) |
| **First files to inspect** | Pytest output shows unified diff; identify surface: formatted → `app/context/debug/context_debug.py`; inspection text → `ContextInspectionService` + formatters; JSON → `context_explanation_serializer` / `context_inspection_serializer` |
| **Expected invariants** | Deterministic output for same fixture; no timing, no network |
| **Related tests** | `test_context_explainability_snapshots.py`, `test_snapshot_*` in budget/resolution_chain/inspect_cli/view_adapter |
| **Behavior vs observability** | Depends: formatted/inspection/JSON drift is observability; if resolver changed, behavior may be affected |

---

### 2.8 Request capture leakage

| Field | Value |
|-------|-------|
| **Likely source module** | `app.context.devtools.request_capture`, `app.context.debug.context_debug_flag` |
| **First files to inspect** | `app/context/devtools/request_capture.py`, `app/context/debug/context_debug_flag.py` |
| **Expected invariants** | Allowed keys only: chat_id, project_id, message, request_context_hint, context_policy; no context_payload, resolved_context, fragment, response, provider_output; `get_last_request()` returns None when CONTEXT_DEBUG_ENABLED not set |
| **Related tests** | `test_no_context_payload_stored`, `test_no_provider_output_stored`, `test_disabled_mode_produces_no_inspection_data` |
| **Behavior vs observability** | Observability only; capture is read-only, no effect on resolution |

---

## 3. Minimal Troubleshooting Workflow

Execute in order. Stop when the failure is localized.

### Step 1: Fixture

Reproduce with a known fixture. Eliminates DB/session variance.

```bash
python scripts/dev/context_inspect.py --db /path/to/test.db --fixture tests/fixtures/context_requests/minimal_default_request.json --show-budget --show-sources
```

If fixture fails: check `load_request_fixture`, fixture schema, DB state for chat_id.

### Step 2: Inspect CLI

Run CLI with same request. Compare text output to expected.

```bash
CONTEXT_DEBUG_ENABLED=1 python scripts/dev/context_inspect.py --db /path/to/test.db --chat-id 1 --show-budget --show-sources
```

If CLI fails: `ContextInspectionService.inspect`, resolver path, DB content.

### Step 3: Serializer JSON

Get raw serializer output. Isolates resolver vs serializer.

```bash
CONTEXT_DEBUG_ENABLED=1 python scripts/dev/context_inspect.py --db /path/to/test.db --chat-id 1 --format json
```

If JSON wrong: `explanation_to_dict`, `inspection_result_to_dict`, key order, nested structure.

### Step 4: Formatted blocks

Inspect `formatted_summary`, `formatted_budget`, `formatted_sources`, `formatted_warnings`. Compare to `format_context_explanation`, `format_context_resolution_summary`, `format_context_budget_summary`, `format_context_source_summary`.

If blocks wrong: `app/context/debug/context_debug.py`, block order, marker strings.

### Step 5: Resolver trace

Inspect `trace.explanation`, `trace.policy_chain`, `trace.mode`, `trace.detail_level`. Verify resolver produced correct explanation before formatter/serializer.

If trace wrong: `app/services/chat_service.py` `get_context_explanation`, `_build_explanation`, policy resolution, budget computation.
