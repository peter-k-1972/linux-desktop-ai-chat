# Context Inspection Workflow

Developer and QA documentation for the context inspection tooling.

---

## 1. Purpose

Context inspection exposes **read-only** visibility into how chat context is resolved, assembled, and injected into LLM prompts. It enables:

- **Developers**: Debug context resolution, verify policy/hint behavior, inspect payload structure
- **QA**: Run repeatable inspections against fixtures, validate explainability output, maintain snapshot coverage

The tooling is **inspection-only**: no runtime mutation, no persistence, no UI-side interpretation.

---

## 2. Architecture Position

```
┌─────────────────────────────────────────────────────────────────┐
│  ChatService.get_context_explanation / get_context_payload_fragment
│  (resolver, limits, fragment assembly)
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  ContextExplainService (preview_with_trace, preview_payload)
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  ContextInspectionService.inspect() / inspect_as_dict()
│  (composes resolver + formatter + serializer)
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│  context_inspect CLI          │    │  Programmatic API             │
│  (scripts/dev/context_inspect) │    │  (get_context_inspection_service)
└──────────────────────────────┘    └──────────────────────────────┘
```

Inspection sits **above** the resolver. It reuses the same resolution path as production; it does not bypass or mock it.

---

## 3. Service Entrypoints

| Entrypoint | Returns | Use case |
|------------|---------|----------|
| `get_context_inspection_service()` | `ContextInspectionService` | Singleton access |
| `inspect(request)` | `ContextInspectionResult` | Typed result with explanation, trace, payload_preview, formatted blocks |
| `inspect_as_dict(request)` | `dict` | JSON-serializable output for tooling/API |

**Request type**: `ContextExplainRequest(chat_id, request_context_hint, context_policy)` from `app.services.context_explain_service`.

**Result structure** (`ContextInspectionResult`):

- `explanation` – `ContextExplanation` (sources, decisions, compressions, warnings, budget)
- `trace` – `ChatContextResolutionTrace` (policy chain, mode, detail, fields)
- `payload_preview` – `ContextPayloadPreview` (sections, tokens, lines)
- `formatted_summary` – resolution summary (one-line)
- `formatted_budget` – budget block
- `formatted_sources` – sources block
- `formatted_warnings` – optional; `None` when no warnings

---

## 4. CLI Usage

**Script**: `scripts/dev/context_inspect.py`

**Input** (mutually exclusive):

- `--chat-id N` – direct chat ID
- `--fixture PATH` – load request from JSON fixture

**Optional overrides** (with `--chat-id`):

- `--hint` – request context hint (e.g. `low_context_query`, `architecture_work`)
- `--policy` – context policy (e.g. `architecture`, `debug`, `exploration`)

**Output**:

- `--format text` (default) – human-readable blocks
- `--format json` – serializer-based structure (`inspection_result_to_dict`)

**Block flags** (text mode):

- `--show-trace` – Context Resolution block
- `--show-budget` – budget block
- `--show-sources` – sources block
- `--show-warnings` – warnings block
- `--show-payload-preview` – payload preview block

**Database**:

- `--db PATH` – SQLite database (default: `chat_history.db`)

**Examples**:

```bash
python scripts/dev/context_inspect.py --chat-id 1
python scripts/dev/context_inspect.py --chat-id 1 --hint low_context_query --policy architecture
python scripts/dev/context_inspect.py --fixture tests/fixtures/context_requests/minimal_default_request.json
python scripts/dev/context_inspect.py --chat-id 1 --format json
python scripts/dev/context_inspect.py --chat-id 1 --show-budget --show-sources
```

---

## 5. Fixture Usage

**Loader**: `app.context.devtools.request_fixture_loader.load_request_fixture(path)`

**Schema** (JSON):

```json
{
  "chat_id": 1,
  "project_id": null,
  "message": null,
  "context_policy": "architecture",
  "context_hint": "low_context_query",
  "settings": null
}
```

- `chat_id` – **required**, int
- `project_id`, `message`, `context_policy`, `context_hint`, `settings` – optional

**Validation**:

- Rejects non-dict root, malformed JSON, unknown keys
- Deterministic errors (`FixtureValidationError`)

**Fixture pack**: `tests/fixtures/context_requests/`

| Fixture | Target behavior |
|---------|-----------------|
| `minimal_default_request.json` | Default resolution, no policy/hint override |
| `explicit_policy_architecture.json` | Architecture policy → FULL_GUIDANCE |
| `profile_strict_minimal.json` | low_context_query → STRICT_MINIMAL |
| `invalid_policy_fallback.json` | Invalid policy → fallback, ignored_inputs |
| `budget_exhausted_request.json` | Debug policy → truncation when content exceeds budget |
| `topic_disabled_request.json` | low_context_query → topic excluded |
| `empty_context_sources.json` | Minimal request; empty sources when DB has no content |

---

## 6. Reading Explanation Blocks

Blocks use **stable markers** for grep-friendly parsing:

| Marker | Block | Content |
|--------|-------|---------|
| `[CTX_RESOLUTION]` | Summary | source, mode, detail, profile, policy, hint, fields |
| `[CTX_BUDGET]` | Budget | configured, effective, reserved, available, per-source used/dropped |
| `[CTX_SOURCES]` | Sources | source_type, included, order, id, chars, budget |
| `[CTX_WARN]` | Warnings | warning_type, message, effect, source_type, dropped_tokens |

**Deterministic order**: blocks are emitted in fixed order. No dynamic sorting.

**JSON** (`formatted_blocks` in serializer output):

- `summary`, `budget`, `sources` – always present
- `warnings` – present only when warnings exist

---

## 7. Reading Payload Preview

`ContextPayloadPreview` describes the **final assembled payload** only. It does not reconstruct dropped content.

**Fields**:

- `empty` – true if payload is empty
- `total_tokens`, `total_lines` – aggregate counts
- `sections` – list of `ContextPayloadSection`

**Section fields**:

- `section_name` – e.g. `project_context`, `chat_context`, `topic_context`, `header`, `instruction_block`
- `included` – whether section is in final payload
- `line_count`, `token_count` – per-section
- `source_type`, `source_id` – optional
- `preview_text` – first N safe lines (max 5 lines, 300 chars)
- `truncated_preview` – true if preview was cut

---

## 8. CI Quality Gate: Context Observability

Changes to context resolution must not silently break observability. CI must **always** run the `context_observability` test group:

```bash
pytest -m context_observability -v
```

**Included**:

- Explainability tests (`test_context_explainability*.py`)
- Inspection service tests (`test_context_inspection_service.py`, `test_context_inspection_view_adapter.py`)
- Serializer determinism tests (`explanation_to_dict`, `inspect_as_dict`, `format_context_explanation`)
- Snapshot suite (`test_context_explainability_snapshots.py`, budget/resolution-chain/CLI/view-adapter snapshots)
- Debug flag gating (`test_context_debug_flag.py`)

**Rules**: No flaky tests, no timing-based assertions, no network/provider dependency.

**Failure output**: Snapshot mismatches show a unified diff; serializer determinism failures include diagnostic hints.

---

## 9. QA Snapshot Workflow

**Tests**: `tests/context/test_context_inspect_cli.py`, `test_context_explainability_snapshots.py`, and others

**Snapshot tests** compare CLI text output against golden files in `tests/context/expected/`:

- `context_inspect_minimal_default.txt`
- `context_inspect_explicit_policy_architecture.txt`
- `context_inspect_invalid_policy_fallback.txt`

**Workflow**:

1. Run: `pytest tests/context/test_context_inspect_cli.py -v`
2. If output changed intentionally: update golden file, re-run to confirm
3. First run (missing golden): test creates file and skips; second run compares

**Service tests**: `tests/context/test_context_inspection_service.py` – assert structure and determinism.

---

## 10. Limitations / Non-Goals

### Explicit Non-Goals

- **No runtime mutation** – inspection does not change DB, settings, or UI state
- **No hidden scoring** – no relevance scores, ranking, or opaque metrics
- **No automatic remediation** – no auto-fix, no suggestions, no remediation actions
- **No UI-side interpretation** – no UI imports; output is plain text or JSON for tooling

### Limitations

- **Read-only** – cannot inject context or modify resolution from inspection
- **DB-dependent** – requires existing chat/project/topic data; fixtures only define request params
- **No async** – service methods are synchronous; CLI runs in single process
- **No persistence** – inspection results are not stored; each run is independent
