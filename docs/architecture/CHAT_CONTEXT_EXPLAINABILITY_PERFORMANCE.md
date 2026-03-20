# Chat Context Explainability – Performance Contract

**Stand:** 2026-03-17  
**Ziel:** Observability ohne unverhältnismäßigen Laufzeit-Overhead.

---

## 1. Performance Guarantees

| Guarantee | Implementation |
|-----------|----------------|
| **Instrumentation metadata only** | Explanation records decisions; no extra provider calls, no LLM invocations |
| **No extra provider calls** | Token counting uses chars/4; no tokenizer API |
| **No repeated context assembly** | `inspect()` uses single resolution path via `preview_with_trace_and_fragment()` |
| **Formatted blocks on demand** | `include_formatted=False` skips format_context_* calls |
| **Payload preview optional** | `include_payload_preview=False` skips build_payload_preview |
| **Dropped summaries reuse accounting** | `_build_dropped_context_report` derives from sources/compressions/warnings; no duplicate token counting |
| **Serializer: no recursion** | `explanation_to_dict`, `trace_to_dict` use explicit per-type mappers; no `__dict__` recursion |

---

## 2. Lazy Formatting Rule

- **Explanation data** (ContextExplanation, trace) is always available when explain=True.
- **Formatted text blocks** (summary, budget, sources, warnings) are built only when `include_formatted=True` in `inspect()`.
- **Payload preview** is built only when `include_payload_preview=True`.
- **Debug logging** (`format_context_debug_blocks`) runs only when `is_context_debug_enabled()` and `logging.DEBUG` are active.

---

## 3. Single Resolution Path

`ContextInspectionService.inspect()` calls `preview_with_trace_and_fragment()` once, which invokes `get_context_explanation(return_trace=True, return_fragment=True)`. One resolution yields both trace and fragment; payload preview is built from the fragment without re-assembling context.

Standalone `preview_payload()` and `get_context_payload_fragment()` remain for backward compatibility but are not used in the inspect flow.

---

## 4. Guardrails

| Guardrail | Location |
|-----------|----------|
| Payload preview optional | `inspect(include_payload_preview=False)` |
| Formatted blocks optional | `inspect(include_formatted=False)` |
| Dropped context reuses accounting | `_build_dropped_context_report(sources, compressions, warnings, ...)` |
| Serializer explicit mapping | `context_explanation_serializer.py` – no recursive walk of arbitrary objects |

---

## 5. Token Counting

- **Single source**: `chars // 4` (CHARS_PER_TOKEN). No tokenizer library.
- **Per-source accounting**: Computed once in `_build_context_sources`; reused in `_build_dropped_context_report`.
- **Compression stats**: `get_context_fragment_stats(fragment)` returns chars/lines; tokens derived once.

---

## 6. Non-Goals

- No premature optimization refactor
- No framework additions
- Implementation kept simple
