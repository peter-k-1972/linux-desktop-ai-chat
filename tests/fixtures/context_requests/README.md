# Context Request Fixtures

QA/dev fixture pack for context inspection. Each fixture targets one observable behavior.

| Fixture | Target behavior |
|---------|-----------------|
| `minimal_default_request.json` | Default resolution, no policy/hint override |
| `explicit_policy_architecture.json` | Architecture policy → FULL_GUIDANCE, larger limits |
| `profile_strict_minimal.json` | low_context_query hint → STRICT_MINIMAL profile |
| `invalid_policy_fallback.json` | Invalid policy string → fallback, ignored_inputs in trace |
| `budget_exhausted_request.json` | Debug policy (smallest limits) → truncation when content exceeds budget |
| `topic_disabled_request.json` | low_context_query → topic excluded from fields |
| `empty_context_sources.json` | Minimal request; empty sources when DB has no project/chat/topic content |

All fixtures use deterministic values. No hidden dependencies on UI state.
