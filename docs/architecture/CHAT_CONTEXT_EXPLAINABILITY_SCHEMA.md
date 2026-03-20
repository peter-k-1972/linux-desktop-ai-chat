# Chat Context Explainability – JSON Schema

**Stand:** 2026-03-17  
**Version:** 1.0  
**Ziel:** Stabile, maschinenlesbare Export-Spezifikation für QA und Tooling.

---

## 1. Overview

The explainability export is produced by `app/context/explainability/context_explanation_serializer.py`. It uses **explicit schema mapping only** – no `__dict__` recursion, no dynamic dumping. Field order is deterministic for stable snapshots.

---

## 2. Top-Level Structure

```json
{
  "explainability_schema_version": "1.0",
  "explanation": { ... },
  "policy_chain": { ... },
  "payload_preview": { ... }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `explainability_schema_version` | string | yes | Schema version (e.g. `"1.0"`) |
| `explanation` | object | yes | ContextExplanation |
| `policy_chain` | object | no | Trace metadata (when include_trace) |
| `payload_preview` | object | no | Payload sections (when include_payload_preview) |

---

## 3. Explanation Object

```json
{
  "resolved_settings": [ ... ],
  "decisions": [ ... ],
  "sources": [ ... ],
  "compressions": [ ... ],
  "warnings": [ ... ],
  "ignored_inputs": [ ... ],
  "budget": { ... },
  "dropped": { ... }
}
```

**Field order:** Resolver semantic order (fixed). sources ordered by selection_order (1=project, 2=chat, 3=topic).

### 3.1 sources (array of ContextSourceEntry)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_type` | string | yes | project \| chat \| topic |
| `identifier` | string | yes | Source identifier |
| `included` | boolean | yes | Whether included in payload |
| `chars_before` | int | no | Chars before truncation |
| `chars_after` | int | no | Chars after truncation |
| `chars` | int | no | Final chars |
| `lines` | int | no | Line count |
| `budget_allocated` | int | no | Allocated budget |
| `budget_used` | int | no | Used budget |
| `budget_dropped` | int | no | Dropped budget |
| `selection_order` | int | no | 1=project, 2=chat, 3=topic |
| `reason` | string | no | budget_exhausted \| truncated_to_budget |

### 3.2 decisions (array of ContextDecisionEntry)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `decision_type` | string | yes | policy \| profile \| request_hint \| field |
| `reason` | string | no | Reason key |
| `outcome` | string | no | Outcome value |

### 3.3 compressions (array of ContextCompressionEntry)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operation` | string | yes | e.g. truncate |
| `original_chars` | int | no | Chars before |
| `final_chars` | int | no | Chars after |
| `before_tokens` | int | no | Tokens before |
| `after_tokens` | int | no | Tokens after |
| `dropped_tokens` | int | no | Tokens dropped |
| `reason` | string | no | e.g. limits |

### 3.4 warnings (array of ContextWarningEntry)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `warning_type` | string | yes | header_only_fragment_removed \| marker_only_fragment_removed \| empty_injection_prevented \| budget_missing_fallback_used \| ... |
| `message` | string | no | Additional message (e.g. mode=off, fragment_empty) |
| `source_type` | string | no | project \| chat \| topic \| context |
| `source_id` | string | no | Identifier for the source |
| `effect` | string | no | removed_fragment \| skipped_injection (when failsafe changed payload) |
| `dropped_tokens` | int | no | Tokens dropped by this failsafe action |

### 3.4a Failsafe counters (top-level)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `warning_count` | int | yes | Total number of warnings |
| `failsafe_triggered` | boolean | yes | True if any failsafe logic changed the final payload |

### 3.5 resolved_settings (array of ContextResolvedSettingEntry)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `setting_name` | string | yes | mode \| detail_level \| policy \| project_enabled \| chat_enabled \| topic_enabled |
| `final_value` | string\|bool\|null | yes | Effective value |
| `winning_source` | string | yes | profile_enabled \| explicit_context_policy \| ... |
| `candidates` | array | yes | Ordered candidates |
| `fallback_used` | boolean | yes | True if individual_settings won |

#### ContextSettingCandidate (within candidates)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `priority_index` | int | yes | 0–5 |
| `source` | string | yes | Source name |
| `value` | string\|bool\|null | yes | Value |
| `applied` | boolean | yes | Whether this won |
| `skipped_reason` | string | no | higher_priority_won \| source_not_present |

### 3.6 ignored_inputs (array of ContextIgnoredInputEntry)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input_name` | string | yes | mode, detail_level, policy, ... |
| `input_source` | string | yes | request \| settings \| profile \| ... |
| `raw_value` | string\|bool\|null | no | Original value |
| `reason` | string | yes | invalid_value \| disabled_by_profile \| empty_source \| ... |
| `resolution_effect` | string | yes | ignored \| fallback_used \| field_disabled |

### 3.7 budget (object)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `configured_budget_total` | int | no | Tokens from limits |
| `effective_budget_total` | int | no | After capping |
| `reserved_budget_system` | int | no | System overhead |
| `reserved_budget_user` | int | no | User reserved |
| `available_budget_for_context` | int | no | effective − reserved |
| `budget_strategy` | string | no | e.g. per_field_and_lines |
| `budget_source` | string | no | default \| policy \| chat_policy \| project_policy |

### 3.8 dropped (object)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dropped_total_tokens` | int | no | Total dropped |
| `dropped_by_source` | array | yes | Per-source entries |
| `dropped_reasons` | array | yes | Reason strings |

#### ContextDroppedEntry (within dropped_by_source)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_type` | string | yes | project \| chat \| topic |
| `reason` | string | yes | policy_exclusion \| profile_restriction \| ... |
| `dropped_tokens` | int | no | Tokens dropped |
| `source_id` | string | no | Source identifier |

---

## 4. policy_chain (object)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | string | yes | individual_settings \| profile \| policy \| ... |
| `profile` | string | no | Profile value |
| `policy` | string | no | Explicit policy |
| `chat_policy` | string | no | Chat-level policy |
| `project_policy` | string | no | Project-level policy |
| `hint` | string | no | Request hint |
| `profile_enabled` | boolean | yes | Whether profile mode active |
| `mode` | string | yes | off \| neutral \| semantic |
| `detail` | string | yes | minimal \| standard \| full |
| `fields` | array | yes | project, chat, topic |
| `limits_source` | string | yes | default \| policy \| ... |
| `max_project_chars` | int | no | Limit |
| `max_chat_chars` | int | no | Limit |
| `max_topic_chars` | int | no | Limit |
| `max_total_lines` | int | no | Limit |

---

## 5. payload_preview (object)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `empty` | boolean | yes | True if no payload |
| `total_tokens` | int | yes | Total tokens |
| `total_lines` | int | yes | Total lines |
| `sections` | array | yes | Section entries |

#### ContextPayloadSection

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `section_name` | string | yes | project_context \| chat_context \| topic_context \| instruction_block \| header |
| `included` | boolean | yes | Whether in payload |
| `line_count` | int | yes | Lines |
| `token_count` | int | yes | Tokens |
| `source_type` | string | no | project \| chat \| topic |
| `source_id` | string | no | Identifier |
| `preview_text` | string | no | First N lines (max 5, 300 chars) |
| `truncated_preview` | boolean | yes | Whether preview truncated |

---

## 6. Serialization Rules

1. **Deterministic field order** – Objects use fixed key order for stable output.
2. **Omit None** – Optional fields with value `null` are omitted.
3. **No recursion** – Only explicit mappings; no generic `__dict__` or `asdict()` on unknown types.
4. **Version field** – `explainability_schema_version` is always present at top level.

---

## 7. Usage

```python
from app.context.explainability.context_explanation_serializer import (
    explainability_to_dict,
    explanation_to_dict,
    trace_to_dict,
)
import json

# Full export (trace + explanation + optional payload)
d = explainability_to_dict(
    trace, expl,
    include_trace=True,
    include_budget=True,
    include_dropped=True,
    include_payload_preview=True,
    payload_preview=payload,
)
print(json.dumps(d, indent=2, ensure_ascii=False))
```
