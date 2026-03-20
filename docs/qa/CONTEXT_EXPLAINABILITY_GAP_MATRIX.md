# Context Explainability – Remaining Gap Matrix

**Stand:** 17. März 2026  
**Ziel:** Konkrete Lücken zwischen Soll und Ist für Explainability/Observability.

---

## Legende

| Gap Type | Bedeutung |
|----------|-----------|
| missing implementation | Funktionalität fehlt im Code |
| partial wiring | Implementiert, aber nicht vollständig angeschlossen |
| missing tests | Keine oder unzureichende Testabdeckung |
| missing docs | Dokumentation fehlt oder ist veraltet |
| determinism risk | Potenzial für nicht-deterministische Ausgabe |
| debug gating gap | Debug-Gate nicht korrekt angewendet |
| audit mismatch | Audit-Report oder Checkliste weicht von Implementierung ab |

| Severity | Bedeutung |
|----------|-----------|
| critical | Blockiert Release oder verursacht Datenleck |
| major | Wichtige Lücke, sollte vor nächstem Release behoben werden |
| minor | Nice-to-have, niedrige Priorität |

---

## Gap-Matrix

| # | Area | Expected State | Actual State | Gap Type | Severity | Concrete Next File(s) | Verification Method |
|---|------|----------------|--------------|----------|----------|----------------------|----------------------|
| 1 | Resolver instrumentation | Explanation bei jeder Auflösung; Trace mit explanation; _build_dropped_context_report, _build_resolved_settings integriert | Implementiert in chat_service.py | — | — | — | Kein Gap |
| 2 | Trace attachment | ChatContextResolutionTrace.explanation bei jeder Auflösung | Implementiert; Trace enthält explanation | — | — | — | Kein Gap |
| 3 | Serializer coverage | explanation_to_dict, trace_to_dict, inspection_result_to_dict mit Determinismus-Tests | explanation_to_dict: test_json_serializer_output_deterministic, test_explanation_to_dict_ordering_contract; inspection_result_to_dict: test_inspect_as_dict_deterministic; trace_to_dict: nur indirekt via inspection | missing tests | minor | `tests/context/test_context_explanation_serializer.py` (neu) oder Erweiterung in `test_context_resolution_chain_explainability.py` | Test: `trace_to_dict(trace)` zweimal aufrufen, JSON dumps vergleichen; Roundtrip optional |
| 4 | Inspection service | inspect(), inspect_as_dict(); ein Entrypoint; Determinismus | Implementiert; test_inspect_returns_explanation_trace_payload_preview, test_inspect_as_dict_deterministic | — | — | — | Kein Gap |
| 5 | Inspection CLI | --chat-id, --fixture, --format text\|json, --show-*; Snapshot für Fixtures | Implementiert; Snapshot nur für 3 Fixtures (minimal_default, explicit_policy_architecture, invalid_policy_fallback) | missing tests | minor | `tests/context/test_context_inspect_cli.py` | Snapshot-Tests für profile_strict_minimal, budget_exhausted_request, topic_disabled_request, empty_context_sources hinzufügen |
| 6 | Fixture support | 7 JSON-Fixtures; load_request_fixture mit Schema-Validierung | 7 Fixtures vorhanden; Loader implementiert; keine direkten Unit-Tests für load_request_fixture | missing tests | minor | `tests/context/test_request_fixture_loader.py` (neu) | Tests: load_request_fixture mit gültigem Pfad; FixtureValidationError bei unknown keys, missing chat_id, invalid types |
| 7 | Payload preview | build_payload_preview, ContextPayloadPreview; format_payload_preview | Implementiert; test_inspect_returns_explanation_trace_payload_preview, test_payload_preview_reflects_final_payload_only, Snapshot 09_payload_preview | — | — | — | Kein Gap |
| 8 | Dropped-context accounting | dropped_by_source, dropped_reasons, dropped_total_tokens in Explanation | Implementiert; _build_dropped_context_report in chat_service; test_dropped_context_report_with_profile_restriction, Snapshot 05_budget_exhaustion | — | — | — | Kein Gap |
| 9 | Ignored-input accounting | ignored_inputs in Explanation; ContextIgnoredInputEntry | Implementiert; test_invalid_explicit_policy_visible_as_ignored_input, test_snapshot_invalid_explicit_value_ignored | — | — | — | Kein Gap |
| 10 | Debug logging | format_context_debug_blocks nur bei is_context_debug_enabled() | chat_service.py prüft is_context_debug_enabled() vor _log.debug(format_context_debug_blocks) | — | — | — | Kein Gap |
| 11 | Request capture | capture(), get_last_request(); nur bei CONTEXT_DEBUG_ENABLED; keine Persistenz | Implementiert; test_request_capture.py vorhanden; test_request_capture NICHT im context_observability-Marker | missing tests | major | `tests/context/test_request_capture.py` | pytestmark = pytest.mark.context_observability hinzufügen; oder CI-Workflow erweitern um test_request_capture |
| 12 | UI adapter | ContextInspectionViewAdapter.to_view_model; keine UI-Imports | Implementiert; test_context_inspection_view_adapter.py mit Snapshot | — | — | — | Kein Gap |
| 13 | GUI debug panel | ContextInspectionPanel; ChatWorkspace, IntrospectionWorkspace Integration | Implementiert; keine UI-Tests für Panel (set_chat_id, set_request, _refresh, Anzeige) | missing tests | minor | `tests/context/test_context_inspection_panel.py` (neu, pytest-qt) oder `tests/ui/test_context_inspection_panel.py` | Test: Panel mit Mock-InspectionResult; set_chat_id → _refresh aufgerufen; summary_lines angezeigt |
| 14 | Test coverage | context_observability-Marker auf allen Explainability-Tests | test_request_capture, test_preview_context_fragment, test_context_failsafe_limits ohne Marker | partial wiring | major | `tests/context/test_request_capture.py`, `tests/scripts/test_preview_context_fragment.py` | pytestmark = pytest.mark.context_observability hinzufügen; test_context_failsafe_limits: prüfen ob Failsafe zu Explainability gehört |
| 15 | Snapshot coverage | CLI-Snapshot für alle 7 Fixtures | Nur 3 Fixtures: minimal_default, explicit_policy_architecture, invalid_policy_fallback | missing tests | minor | `tests/context/test_context_inspect_cli.py` | 4 Snapshot-Tests + 4 expected/*.txt Dateien für profile_strict_minimal, budget_exhausted_request, topic_disabled_request, empty_context_sources |
| 16 | CI gates | pytest -m context_observability läuft alle relevanten Tests | Workflow vorhanden; test_request_capture, test_preview_context_fragment nicht im Marker | debug gating gap | major | `pytest.ini`, `tests/context/test_request_capture.py`, `tests/scripts/test_preview_context_fragment.py` | pytest -m context_observability ausführen; prüfen ob request_capture und preview_context_fragment Tests laufen |
| 17 | Governance/docs/audit sync | Schema-Dokumentation deckt alle Serializer-Outputs ab | CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md dokumentiert explainability_to_dict (policy_chain top-level); inspection_result_to_dict hat trace (nicht policy_chain), formatted_blocks – nicht dokumentiert | missing docs | minor | `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` | Abschnitt „Inspection Output (inspection_result_to_dict)“ hinzufügen: Top-Level trace, explanation, payload_preview, formatted_blocks; trace enthält policy_chain |
| 18 | context_explain CLI | CLI für Kontext-Erklärung; --format json, --show-trace, --show-budget | scripts/dev/context_explain.py implementiert; keine Tests | missing tests | minor | `tests/scripts/test_context_explain_cli.py` (neu) | Subprocess-Test: context_explain.py --chat-id 1 --format json; Exit 0; JSON mit explanation |

---

## Zusammenfassung

| Severity | Anzahl |
|----------|--------|
| critical | 0 |
| major | 3 (Gap 11, 14, 16 – CI-Marker fehlt bei request_capture, preview_context_fragment) |
| minor | 6 (Gap 3, 5, 6, 13, 15, 17, 18) |

**Keine Gaps:** Resolver instrumentation, Trace attachment, Inspection service, Payload preview, Dropped-context accounting, Ignored-input accounting, Debug logging, UI adapter.

**Priorisierte nächste Schritte:**
1. test_request_capture.py: context_observability-Marker hinzufügen (Gap 11, 14, 16)
2. test_preview_context_fragment.py: context_observability-Marker hinzufügen (Gap 14, 16)
3. trace_to_dict expliziter Test (Gap 3)
4. load_request_fixture Unit-Tests (Gap 6)
5. Schema-Dokumentation für inspection_result_to_dict (Gap 17)
