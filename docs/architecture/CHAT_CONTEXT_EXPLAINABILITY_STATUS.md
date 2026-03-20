# Context Observability – Implementation Status

**Stand:** 17. März 2026

| Component | File(s) | State | Tests | Docs | Notes |
|-----------|---------|-------|-------|------|-------|
| explanation dataclasses | `app/context/explainability/context_explanation.py` | complete | yes | yes | ContextExplanation + 6 entry types |
| trace extension | `app/chat/context_profiles.py` | complete | yes | yes | ChatContextResolutionTrace with explanation, limits |
| resolver instrumentation | `app/services/chat_service.py` | complete | yes | yes | get_context_explanation, _build_* helpers |
| budget accounting | `app/context/explainability/context_explanation.py` | complete | yes | yes | configured/effective/available budget; per-source allocated/used/dropped |
| dropped-context accounting | `app/context/explainability/context_explanation.py`, `app/services/chat_service.py` | complete | yes | yes | dropped_by_source, dropped_reasons; _build_dropped_context_report |
| ignored inputs | `app/context/explainability/context_explanation.py` | complete | yes | yes | ContextIgnoredInputEntry; invalid/disabled inputs visible |
| serializer | `app/context/explainability/context_explanation_serializer.py` | complete | partial | yes | explanation_to_dict, trace_to_dict; trace_to_dict no explicit test |
| formatted debug output | `app/context/debug/context_debug.py` | complete | yes | yes | format_context_*, format_payload_preview |
| inspection service | `app/services/context_inspection_service.py` | complete | yes | yes | inspect(), inspect_as_dict(); delegates to ContextExplainService |
| inspection serializer | `app/context/explainability/context_inspection_serializer.py` | complete | yes | partial | inspection_result_to_dict; schema doc missing output format |
| inspection CLI | `scripts/dev/context_inspect.py` | complete | yes | yes | --chat-id, --fixture, --format; snapshot for 3 of 7 fixtures |
| fixture loader | `app/context/devtools/request_fixture_loader.py` | complete | partial | yes | load_request_fixture; no direct unit tests |
| request capture | `app/context/devtools/request_capture.py` | complete | yes | yes | capture/get_last_request gated; tests not in context_observability |
| view adapter | `app/context/inspection/context_inspection_view_adapter.py` | complete | yes | yes | to_view_model; UI-neutral, no imports |
| GUI inspection panel | `app/gui/domains/debug/context_inspection_panel.py` | complete | no | yes | Panel in ChatWorkspace, IntrospectionWorkspace; no UI tests |
| debug mode guard | `app/context/debug/context_debug_flag.py` | complete | yes | yes | is_context_debug_enabled (env + config) |
| snapshot suite | `tests/context/expected/` | complete | yes | yes | 10 explainability × 3 surfaces; 3 CLI fixture snapshots |
| CI gate | `.github/workflows/context-observability.yml` | complete | yes | yes | pytest -m context_observability on push/PR |
