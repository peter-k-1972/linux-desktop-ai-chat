# Chat-Kontext – Produktions-Checkliste

**Stand:** 2026-03-17  
**Ziel:** Vor Default-Entscheidung sicherstellen, dass der Kontextmechanismus produktionssauber ist.

---

## Checkliste

| # | Prüfpunkt | Status |
|---|-----------|--------|
| 1 | Default-Werte dokumentiert? | |
| 2 | Default entspricht ADR? | |
| 3 | Regressionstests grün? | |
| 4 | Preview-Script nutzbar? | |
| 5 | Matrix-Script erzeugt saubere Outputs? | |
| 6 | Failsafe-Regeln dokumentiert? | |
| 7 | Kein Settings-Import im Context-Modul? | |
| 8 | Keine UI-Interpretation? | |
| 9 | Explanation-Trace an Kontext-Auflösung angehängt? | |
| 10 | Debug-Formatter stabil (deterministisch)? | |
| 11 | Serializer stabil (explanation_to_dict, trace_to_dict)? | |
| 12 | Snapshot-Coverage für Explainability vorhanden? | |
| 13 | Failsafe-Warnungen sichtbar (effect, warning_count, failsafe_triggered)? | |
| 14 | Inspection-Service vorhanden (ContextInspectionService)? | |
| 15 | Inspection-Serializer stabil (inspection_result_to_dict)? | |
| 16 | CLI Fixture-Mode verfügbar (--fixture)? | |
| 17 | Snapshot-Fixtures gepflegt (tests/fixtures/context_requests/)? | |
| 18 | Keine doppelte Resolver-Logik im Inspection-Tooling? | |
| 19 | **CI: context_observability-Tests immer ausgeführt?** | |

---

## CI-Anforderung: Context Observability

Änderungen an der Kontext-Auflösung dürfen die Observability nicht still brechen. CI muss daher **immer** folgende Testgruppen ausführen:

- **Explainability-Tests** – `test_context_explainability*.py`
- **Inspection-Service-Tests** – `test_context_inspection_service.py`, `test_context_inspection_view_adapter.py`
- **Serializer-Determinismus** – `test_json_serializer_output_deterministic`, `test_inspect_as_dict_deterministic`, `test_formatted_debug_output_deterministic`
- **Snapshot-Suite** – `test_context_explainability_snapshots.py`, Budget-/Resolution-Chain-/CLI-/View-Adapter-Snapshots

**Ausführung**:

```bash
pytest -m context_observability -v
```

**Regeln**: Keine flaky Tests, keine zeitbasierten Assertions, keine Netzwerk-/Provider-Abhängigkeit.

---

## CONTEXT EXPLAINABILITY / OBSERVABILITY RELEASE GATE

Vor Freigabe der Context-Explainability-Funktionalität müssen alle Punkte erfüllt sein. Jeder Punkt ist durch Test oder Code-Review verifizierbar.

| # | Prüfpunkt | Verifikation |
|---|-----------|--------------|
| E1 | Explanation an Trace angehängt, wenn Auflösung mit Explanation erfolgt | `trace.explanation` ist nicht None nach `get_context_explanation(..., return_trace=True)`; `test_explanation_exists` |
| E2 | Winning-Source-Kette sichtbar | `resolved_settings` enthält pro Setting `winning_source` und `candidates`; `test_winning_source_visible_for_effective_policy` |
| E3 | Ignorierte Inputs sichtbar | `explanation.ignored_inputs` enthält Einträge bei ungültigen/übersprungenen Inputs; `test_invalid_explicit_policy_visible_as_ignored_input` |
| E4 | Budget-Accounting sichtbar | `configured_budget_total`, `effective_budget_total`, `available_budget_for_context` befüllt; `test_budget_fields_populated` |
| E5 | Dropped-Context-Accounting sichtbar | `dropped_by_source`, `dropped_total_tokens`, `dropped_reasons` befüllt wenn Kontext verworfen; `test_dropped_context_report_with_profile_restriction` |
| E6 | Failsafe-Warnungen strukturiert und sichtbar | `ContextWarningEntry` mit `warning_type`, `effect`; `explanation.warning_count`, `failsafe_triggered`; `test_failsafe_structured_warning_fields` |
| E7 | Serializer deterministisch | Zwei Aufrufe mit gleichem Input liefern identisches Dict/JSON; `test_json_serializer_output_deterministic`, `test_inspect_as_dict_deterministic` |
| E8 | Formatted Output deterministisch | Zwei Aufrufe `format_context_explanation(expl)` mit gleichem `expl` liefern identischen String; `test_formatted_debug_output_deterministic` |
| E9 | Inspection-Service read-only | `ContextInspectionService.inspect()` mutiert keine DB, Settings oder UI; keine Schreib-Pfade im Modul |
| E10 | Request-Capture nur in-memory | `request_capture` speichert nur in globaler Variable; keine Datei-/DB-Persistenz |
| E11 | Debug-Tooling durch Debug-Flag geschaltet | `capture`/`get_last_request` sind No-Op bzw. None wenn `CONTEXT_DEBUG_ENABLED` nicht gesetzt; `test_disabled_mode_produces_no_inspection_data` |
| E12 | Snapshot-Suite grün | `pytest -m context_observability` läuft ohne Fehler |
| E13 | CI-Gate aktiv | `.github/workflows/context-observability.yml` vorhanden; Trigger auf push/PR zu main, develop |
| E14 | Keine doppelte Resolver-Logik im Tooling | `ContextInspectionService` nutzt `ContextExplainService`; keine eigene Auflösungslogik in `app/context/` oder `app/services/context_inspection_service.py` |
| E15 | Keine UI-Entscheidungslogik eingeführt | `app/context/` enthält keine UI-Imports; Kontext-Entscheidungen (mode, policy, include_*) ausschließlich im Resolver |

---

## Referenzen

| Prüfpunkt | Referenz |
|-----------|----------|
| Default-Werte | CHAT_CONTEXT_GOVERNANCE.md §4 |
| Default entspricht ADR? | ADR_CHAT_CONTEXT_DEFAULT.md, test_default_configuration_matches_adr |
| Regressionstests | tests/chat/test_context_governance_regressions.py |
| Preview-Script | scripts/dev/preview_context_fragment.py |
| Matrix-Script | scripts/qa/run_context_matrix.py |
| Failsafe-Regeln | CHAT_CONTEXT_FAILSAFE_POLICY.md |
| Context-Modul | app/chat/context.py |
| UI-Verbot | CHAT_CONTEXT_GOVERNANCE.md §2 |
| Explanation-Trace | ChatContextResolutionTrace.explanation, get_context_explanation() |
| Debug-Formatter | app/context/debug/context_debug.py |
| Serializer | app/context/explainability/context_explanation_serializer.py |
| Snapshot-Coverage | tests/context/test_context_explainability_budget.py, test_context_resolution_chain_explainability.py |
| Failsafe-Warnungen | ContextWarningEntry.effect, ContextExplanation.warning_count, failsafe_triggered |
| Inspection-Service | app/services/context_inspection_service.py |
| Inspection-Serializer | app/context/explainability/context_inspection_serializer.py |
| CLI Fixture-Mode | scripts/dev/context_inspect.py --fixture |
| Snapshot-Fixtures | tests/fixtures/context_requests/, tests/context/expected/context_inspect_*.txt |
| Resolver-Logik | Inspection nutzt ContextExplainService; keine eigene Logik |
| CI context_observability | pytest -m context_observability; Marker in pytest.ini |
| Release Gate E1–E15 | CONTEXT EXPLAINABILITY / OBSERVABILITY RELEASE GATE (oben) |
