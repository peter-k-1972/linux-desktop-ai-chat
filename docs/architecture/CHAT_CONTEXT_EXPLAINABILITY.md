# Chat Context Explainability and Observability

**Stand:** 2026-03-17  
**Ziel:** Transparenz über Kontext-Auflösung, Budget und abgeworfene Inhalte – ohne Magie, ohne versteckte Schichten.

---

## 1. Purpose

Context explainability provides **traceability** for how chat context is resolved, budgeted, and truncated. It answers:

- Which sources (project, chat, topic) were included or excluded, and why
- How token budget was allocated and consumed
- What was dropped (truncation, profile restriction, budget exhaustion)
- Which policy chain and limits were applied

The system is **instrumentation-only**: it records decisions made by the resolver. No logic, no UI imports, no hidden interpretation.

**Performance:** See `CHAT_CONTEXT_EXPLAINABILITY_PERFORMANCE.md` for the performance contract (no duplicate assembly, lazy formatting, optional payload preview).

---

## 2. Scope

| In scope | Out of scope |
|----------|--------------|
| Resolution trace (policy, profile, hint, fields) | Automatic quality scoring |
| Budget accounting (configured, effective, reserved, available) | Hidden decision layer |
| Per-source budget (allocated, used, dropped) | UI interpretation of explanation |
| Dropped context metadata (reason, tokens) | LLM-based context selection |
| Deterministic debug formatter | |
| Developer CLI for inspection | |

---

## 3. Explanation Model

All types live in `app/context/explainability/context_explanation.py`. Pure dataclasses, no logic.

### ContextExplanation

Aggregated explanation of context resolution:

- **sources** – Per-source entries (project, chat, topic)
- **decisions** – Policy/profile/hint decisions (resolver order)
- **compressions** – Compression steps (original/final chars, dropped tokens)
- **warnings** – Fail-safe warnings
- **configured_budget_total**, **effective_budget_total**, **reserved_budget_system**, **reserved_budget_user**, **available_budget_for_context**
- **budget_strategy**, **budget_source**
- **dropped_total_tokens**, **dropped_by_source**, **dropped_reasons**

### ContextSourceEntry

- `source_type`, `identifier`, `included`
- `chars_before`, `chars_after`, `chars`, `lines`
- `budget_allocated`, `budget_used`, `budget_dropped`
- `selection_order` (1=project, 2=chat, 3=topic)
- `reason` (e.g. `budget_exhausted`, `truncated_to_budget`)

### ContextDroppedEntry

- `source_type`, `reason`, `dropped_tokens`, `source_id`
- Reasons: `policy_exclusion`, `field_disabled`, `profile_restriction`, `compression`, `token_budget_exhaustion`, `failsafe_cleanup`

### ContextCompressionEntry

- `operation`, `original_chars`, `final_chars`, `before_tokens`, `after_tokens`, `dropped_tokens`, `reason`

---

## 4. Budget Visibility

Budget accounting is computed in `app/chat/context_limits.compute_budget_accounting()` and exposed on `ContextExplanation`:

| Field | Meaning |
|-------|---------|
| `configured_budget_total` | Tokens from limits (chars/4) |
| `effective_budget_total` | After any capping |
| `reserved_budget_system` | Tokens for labels/overhead |
| `reserved_budget_user` | Reserved for user (0 if unused) |
| `available_budget_for_context` | effective − reserved (floor 0) |
| `budget_strategy` | e.g. `per_field_and_lines` |
| `budget_source` | Same as limits_source |

Per-source accounting:

- `budget_allocated` – max chars for this source
- `budget_used` – chars in final fragment
- `budget_dropped` – chars dropped (truncation or skip)

Invariants: `available_budget_for_context == effective − reserved_system − reserved_user`; `budget_used + budget_dropped == chars_before` per source.

---

## 5. Dropped-Context Visibility

Dropped context is reported as **metadata only** – no content preview, no sensitive data.

- **dropped_total_tokens** – Sum of all dropped tokens
- **dropped_by_source** – List of `ContextDroppedEntry` with `source_type`, `reason`, `dropped_tokens`, `source_id`
- **dropped_reasons** – Distinct reasons (e.g. for summaries)

Invariant: `dropped_total_tokens == sum(dropped_tokens for e in dropped_by_source)` when both are populated.

Skipped sources due to budget exhaustion appear in `sources` with `included=False` and `reason="budget_exhausted"`.

---

## 6. Debug Formatter

`app/context/debug/context_debug.format_context_explanation()` produces deterministic, snapshot-friendly plain text.

**Sections (fixed order):**

1. Context Resolution (if trace provided): source, mode, detail, profile, policy, hint, fields
2. Budget: configured, effective, reserved, available, strategy, source
3. Source Budget Consumption: per-source used/dropped
4. Dropped Context Summary: total_dropped_tokens
5. Dropped By Source: per-entry reason, dropped_tokens, id
6. Dropped Reasons: distinct reasons
7. Decisions: resolver order
8. Sources: selection order (1,2,3), included, chars, budget
9. Compression: operation, chars, tokens
10. Warnings

**Options:** `include_budget`, `include_dropped` (both default True).

Output is stable: same input → same output. No dynamic dict sorting.

---

## 7. Developer CLI Usage

### context_explain.py

Inspect context explanation for a chat:

```bash
python scripts/dev/context_explain.py --chat-id 1
python scripts/dev/context_explain.py --db chat_history.db --chat-id 1 --hint low_context_query
python scripts/dev/context_explain.py --chat-id 1 --policy architecture --format json
python scripts/dev/context_explain.py --chat-id 1 --format text --show-trace --show-budget --show-dropped
```

| Option | Default | Description |
|--------|---------|--------------|
| `--db` | chat_history.db | SQLite database path |
| `--chat-id` | required | Chat ID |
| `--hint` | - | Request context hint (e.g. low_context_query) |
| `--policy` | - | Context policy (architecture, debug, exploration) |
| `--format` | text | Output format: text, json |
| `--json` | - | Alias for --format json |
| `--show-trace` | off | Include policy chain, limits, fields |
| `--show-budget` | on | Include budget accounting |
| `--show-dropped` | on | Include dropped context |
| `--no-budget` | - | Exclude budget |
| `--no-dropped` | - | Exclude dropped |

### preview_context_fragment.py

Preview context fragment without DB or provider call (fixed example context):

```bash
python scripts/dev/preview_context_fragment.py --mode semantic --detail standard --fields all
python scripts/dev/preview_context_fragment.py --policy architecture --project-name "Lang"
python scripts/dev/preview_context_fragment.py --policy debug --chat-title "X" * 100
```

---

## 8. QA Assertions

Tests in `tests/context/test_context_explainability.py` and `tests/context/test_context_explainability_budget.py`:

| Assertion | File |
|-----------|------|
| Budget fields populated when explain=True | test_context_explainability_budget |
| available_budget consistent with reservations | test_context_explainability_budget |
| Per-source budget_used + budget_dropped == chars_before | test_context_explainability_budget |
| dropped_total_tokens == sum(dropped_by_source) | test_context_explainability_budget |
| Skipped sources (budget_exhausted) visible | test_context_explainability_budget |
| Source ordering matches resolver order (1=project, 2=chat, 3=topic) | test_context_explainability_budget |
| Formatted debug output deterministic | test_context_explainability_budget |
| Snapshot: normal request | test_context_explainability_budget |
| Snapshot: compressed request | test_context_explainability_budget |
| Snapshot: budget exhausted request | test_context_explainability_budget |

Rules: use real resolver, no fake explanation objects, no behavior changes.

---

## 9. Non-Goals

The following are **explicitly out of scope**:

| Non-goal | Rationale |
|----------|-----------|
| **No automatic quality scoring** | Explainability records decisions; it does not score or grade context quality. |
| **No hidden decision layer** | All decisions are made by the resolver and recorded. No opaque intermediate layer. |
| **No UI interpretation** | The explanation model is backend-only. UI does not interpret or display explanation data. |
| **No LLM-based context selection** | Context resolution is rule-based (policy, profile, limits). No LLM decides what to include. |

These align with `CHAT_CONTEXT_GOVERNANCE.md`: no magic, no hidden rules, no UI interpretation.
