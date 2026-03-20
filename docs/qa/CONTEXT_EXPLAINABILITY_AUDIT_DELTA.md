# Context Explainability – Audit Delta Report

**Stand:** 17. März 2026  
**Basis:** Vergleich vorheriger Audit-Formulierung (AUDIT_REPORT.md vor Ist-Stand-Update) mit aktuellem Code, Tests und Doku.

---

## 1. Newly Implemented Since Previous Audit

*(Komponenten, die im Code existieren, aber im vorherigen Audit nicht oder unvollständig dokumentiert waren.)*

| Item | Previous Audit | Current Evidence |
|------|----------------|-----------------|
| Debug-Panel-Integration | Nicht explizit dokumentiert; Section 9.5 Classification sagte „keine UI-Anzeige“ | **Files:** `app/gui/domains/debug/context_inspection_panel.py`, `app/gui/domains/operations/chat/chat_workspace.py` (Zeile 623), `app/gui/domains/runtime_debug/workspaces/introspection_workspace.py` (Zeile 259–281). **Tests:** Keine UI-Tests. Panel in ChatWorkspace nur bei `is_context_debug_enabled()`; IntrospectionWorkspace „Inspect Last Context“-Button |
| CLI-Verhalten bei deaktiviertem Debug | Nicht präzise beschrieben | **Files:** `scripts/dev/context_inspect.py` (Zeile 171–179), `scripts/dev/context_explain.py` (Zeile 117–126). Beide prüfen `is_context_debug_enabled()`; bei False: Exit 0, Hinweis auf stderr, keine Inspection-Ausgabe |
| test_request_capture / test_preview_context_fragment ohne context_observability-Marker | Nicht erwähnt | **Files:** `tests/context/test_request_capture.py`, `tests/scripts/test_preview_context_fragment.py`. Kein `pytestmark = pytest.mark.context_observability` |
| inspection_result_to_dict Output-Struktur | Schema-Dokumentation beschreibt nur explainability_to_dict (policy_chain top-level) | **Files:** `app/context/explainability/context_inspection_serializer.py`. Top-Level: trace, explanation, payload_preview, formatted_blocks. `trace` enthält policy_chain. **Docs:** `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` dokumentiert inspection_result_to_dict nicht |

---

## 2. Corrected Audit Claims

*(Vorherige Audit-Aussagen, die der aktuelle Code/Docs widerlegt.)*

| Previous Claim | Source (Previous Audit) | Correction | Evidence |
|----------------|------------------------|------------|----------|
| „Debug-only: Keine UI-Anzeige; Developer-Tooling, CLI, Logging bei DEBUG“ | Section 9.5 Classification | **Outdated.** ContextInspectionPanel existiert und wird in ChatWorkspace (bei Debug) und IntrospectionWorkspace angezeigt | `app/gui/domains/debug/context_inspection_panel.py`; `chat_workspace.py` Zeile 623; `introspection_workspace.py` Zeile 278 |
| „CLI läuft auch ohne, nutzt dann nur DB/Infra“ | Section 10.5 CLI Status | **Outdated.** CLI beendet mit Exit 0 und Hinweis, wenn CONTEXT_DEBUG_ENABLED nicht gesetzt; es wird keine Inspection-Ausgabe erzeugt | `scripts/dev/context_inspect.py` Zeile 171–179; `test_context_debug_flag.py::test_cli_exits_gracefully_when_disabled` |
| „Umfang: 91 Tests“ | Section 10.7 CI Gate Status | **Unverified.** Exakte Testanzahl nicht geprüft; test_request_capture und test_preview_context_fragment sind nicht im context_observability-Marker | `pytest.ini`; `tests/context/test_request_capture.py` (kein Marker); `tests/scripts/test_preview_context_fragment.py` (kein Marker) |

---

## 3. Still-Open Items

*(Lücken, die im Gap-Matrix und Work-Order dokumentiert sind.)*

| Item | Gap Matrix # | Evidence |
|------|--------------|----------|
| trace_to_dict ohne expliziten Determinismus-Test | Gap 3 | `test_context_resolution_chain_explainability.py` testet explanation_to_dict; trace_to_dict nur indirekt über inspection_result_to_dict |
| load_request_fixture ohne direkte Unit-Tests | Gap 6 | `app/context/devtools/request_fixture_loader.py`; nur über CLI getestet |
| CLI-Snapshot nur für 3 von 7 Fixtures | Gap 5, 15 | `tests/context/test_context_inspect_cli.py`; fehlend: profile_strict_minimal, budget_exhausted_request, topic_disabled_request, empty_context_sources |
| ContextInspectionPanel ohne UI-Tests | Gap 13 | `app/gui/domains/debug/context_inspection_panel.py`; keine pytest-qt-Tests |
| context_explain CLI ohne Tests | Gap 18 | `scripts/dev/context_explain.py`; keine Subprocess-Tests |
| Schema-Dokumentation für inspection_result_to_dict fehlt | Gap 17 | `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`; kein Abschnitt für trace, formatted_blocks |

---

## 4. Downgraded Assumptions

*(Annahmen, die nicht mehr oder nur eingeschränkt haltbar sind.)*

| Assumption | Previous Basis | Downgrade Reason | Evidence |
|------------|----------------|------------------|----------|
| „91 Tests“ im context_observability-Gate | Section 10.7 | Exakte Zahl nicht verifiziert; test_request_capture und test_preview_context_fragment laufen nicht unter -m context_observability | `pytest -m context_observability --collect-only`; Marker fehlt in beiden Dateien |
| „CLI läuft auch ohne“ (produziert Ausgabe) | Section 10.5 | CLI beendet ohne Ausgabe, wenn Debug deaktiviert | `scripts/dev/context_inspect.py` main() |
| HTTP/API für get_context_explanation „falls vorhanden“ | Section 9.3, 10.8 | Kein HTTP/API existiert; Formulierung irreführend | `grep` über Codebase: kein Endpoint |

---

## 5. Upgraded Confidence Areas

*(Bereiche mit stärkerer Evidenz durch Code-/Test-/Dokumentationsprüfung.)*

| Area | Upgrade | Evidence |
|------|---------|----------|
| Resolver-Instrumentierung | Vollständig bestätigt: _explanation_with_budget, _build_resolved_settings, _build_dropped_context_report in chat_service | `app/services/chat_service.py` Zeile 546, 604, 675, 130; Tests in test_context_explainability*.py, test_context_resolution_chain_explainability.py |
| Request-Capture im Sendepfad | Explizit bestätigt: capture() in chat_service vor _inject_chat_context | `app/services/chat_service.py` Zeile 406–415 |
| Debug-Logging-Gate | Bestätigt: format_context_debug_blocks nur bei is_context_debug_enabled() | `app/services/chat_service.py` Zeile 1194–1199, 1212–1217, 1267–1272, 1332–1346 |
| Serializer-Determinismus | explanation_to_dict und inspection_result_to_dict haben explizite Tests | `test_context_resolution_chain_explainability.py::test_json_serializer_output_deterministic`, `test_context_inspection_service.py::test_inspect_as_dict_deterministic` |
| Fixture-Schema | ALLOWED_KEYS und Validierung explizit im Code | `app/context/devtools/request_fixture_loader.py` Zeile 11–13, _validate_keys, _validate_types |
| Snapshot-Suite | 10 Szenarien × 3 Surfaces (formatted, inspection, json) vorhanden | `tests/context/expected/explainability_snapshots/`; `test_context_explainability_snapshots.py` |

---

## 6. Evidence References

### Files

| Purpose | Path |
|---------|------|
| Explanation dataclasses | `app/context/explainability/context_explanation.py` |
| Trace | `app/chat/context_profiles.py` |
| Resolver, capture | `app/services/chat_service.py` |
| Serializer | `app/context/explainability/context_explanation_serializer.py`, `context_inspection_serializer.py` |
| Fixture loader | `app/context/devtools/request_fixture_loader.py` |
| Request capture | `app/context/devtools/request_capture.py` |
| Debug flag | `app/context/debug/context_debug_flag.py` |
| Inspection panel | `app/gui/domains/debug/context_inspection_panel.py` |
| Panel integration | `app/gui/domains/operations/chat/chat_workspace.py`, `app/gui/domains/runtime_debug/workspaces/introspection_workspace.py` |
| CLI | `scripts/dev/context_inspect.py`, `scripts/dev/context_explain.py` |

### Tests

| Purpose | Test(s) |
|---------|---------|
| Explanation exists | `test_context_explainability.py::test_explanation_exists` |
| Serializer determinism | `test_context_resolution_chain_explainability.py::test_json_serializer_output_deterministic`, `test_context_inspection_service.py::test_inspect_as_dict_deterministic` |
| Debug gating | `test_context_debug_flag.py::test_disabled_mode_produces_no_inspection_data`, `test_cli_exits_gracefully_when_disabled` |
| Request capture | `test_request_capture.py` (5 tests) |
| Snapshot suite | `test_context_explainability_snapshots.py` (30 tests) |

### Docs

| Purpose | Path |
|---------|------|
| Schema (explainability_to_dict) | `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` |
| Inspection workflow | `docs/dev/CONTEXT_INSPECTION_WORKFLOW.md` |
| Gap matrix | `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md` |
| Work order | `docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md` |
| Status table | `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_STATUS.md` |
| Verification checklist | `docs/qa/CONTEXT_EXPLAINABILITY_VERIFICATION_CHECKLIST.md` |
