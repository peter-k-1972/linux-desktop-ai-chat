# QA Self-Healing – Linux Desktop Chat

**Iteration:** 1  
**Generiert:** 2026-03-15 14:49 UTC  
**Zweck:** Wartungs- und Driftprobleme in der Testsuite erkennen, daraus sinnvolle QA-Wartungsempfehlungen ableiten.

---

## 1. Zweck

Der QA Self-Healing-Prozess **erkennt** und **diagnostiziert** – nicht automatisch repariert.

- Erkennung von Flaky-Risiken
- Erkennung potenziell schwacher Tests
- Analyse der Fehlerklassen-Streuung
- Priorisierte Wartungsempfehlungen

---

## 2. Verwendete Checks

- Flaky-Risiko-Heuristik: async_behavior, chaos, qtbot.wait, asyncio.sleep, timeout/delay, lifecycle
- Schwache-Test-Heuristik: assert is not None, count()>=1, nur isVisible
- Fehlerklassen-Streuung: pro Fehlerklasse Anzahl Testdomänen aus REGRESSION_CATALOG
- QA-Wartungsempfehlungen: Zusammenführung aus allen Checks, Top-5 priorisiert

---

## 3. Auffällige Flaky-Risiken

*(Heuristik: erhöhtes Risiko, keine Behauptung „dieser Test ist flaky“)*

| Datei | Test | Signale | Beschreibung |
|-------|------|---------|--------------|
| tests/async_behavior/test_signal_after_widget_destroy.py | test_signal_after_widget_destroy_no_crash | 4 | Cleanup-/Destroy-Sensitivität; Event-Wait, Timing-… |
| tests/async_behavior/test_chatwidget_signal_after_destroy.py | test_chatwidget_signal_during_destroy_no_crash | 4 | Cleanup-/Destroy-Sensitivität; Event-Wait, Timing-… |
| tests/chaos/test_provider_timeout_chat.py | test_provider_delay_then_cancel_cleans_up_streaming_state | 3 | Timeout-/Delay-Szenarien; Fault-Injection, Timing-… |
| tests/smoke/test_app_startup.py | (mehrere) | 3 | Event-Wait, Timing-abhängig; Async/Event-Loop-Sens… |
| tests/ui/test_debug_panel_ui.py | test_agent_activity_shows_task_status | 3 | Event-Wait, Timing-abhängig; Async/Event-Loop-Sens… |
| tests/ui/test_chat_ui.py | test_conversation_view_message_content_visible | 3 | Event-Wait, Timing-abhängig |
| tests/state_consistency/test_prompt_consistency.py | test_prompt_ui_service_storage_roundtrip | 3 | Event-Wait, Timing-abhängig |
| tests/async_behavior/test_chatwidget_signal_after_destroy.py | test_chatwidget_late_signal_no_crash | 3 | Event-Wait, Timing-abhängig; Async/Event-Loop-Sens… |
| tests/integration/test_rag_chat_integration.py | (mehrere) | 2 | Async/Event-Loop-Sensitivität |
| tests/integration/test_chat_streaming_behavior.py | (mehrere) | 2 | Async/Event-Loop-Sensitivität; Delay-basiert |
| tests/chaos/test_provider_timeout_chat.py | (mehrere) | 2 | Timeout-/Delay-Szenarien; Fault-Injection, Timing-… |
| tests/chaos/test_provider_timeout_chat.py | test_provider_delay_completes_then_second_send_works | 2 | Timeout-/Delay-Szenarien; Fault-Injection, Timing-… |
| tests/chaos/test_provider_timeout_chat.py | test_no_double_send_while_streaming | 2 | Timeout-/Delay-Szenarien; Delay-basiert |
| tests/chaos/test_persistence_failure_after_success.py | (mehrere) | 2 | Timeout-/Delay-Szenarien; Fault-Injection, Timing-… |
| tests/regression/test_agent_delete_removes_from_list.py | (mehrere) | 2 | Event-Wait, Timing-abhängig |

---

## 4. Potenziell schwache Tests

*(Nur markieren – keine automatische Änderung)*

| Datei | Test | Signale | Beschreibung |
|-------|------|---------|--------------|
| tests/smoke/test_app_startup.py | test_critical_imports | 5 | Nur Existenzprüfung |
| tests/test_agent_hr.py | test_registry_lookup | 3 | Nur Existenzprüfung |
| tests/test_agent_hr.py | test_agent_create | 2 | Nur Existenzprüfung |
| tests/test_agent_hr.py | test_agent_duplicate | 2 | Nur Existenzprüfung |
| tests/integration/test_sqlite.py | test_create_and_get_agent | 2 | Nur Existenzprüfung |
| tests/golden_path/test_agent_golden_path.py | test_agent_create_save_load_edit_delete | 2 | Nur Existenzprüfung |
| tests/golden_path/test_prompt_golden_path.py | test_prompt_create_save_load_edit_delete | 2 | Nur Existenzprüfung |
| tests/smoke/test_basic_chat.py | test_conversation_view_add_message | 2 | Nur Existenzprüfung; Nur count >= 1 |
| tests/smoke/test_app_startup.py | ? | 2 | Nur Existenzprüfung |
| tests/ui/test_chat_ui.py | test_conversation_view_add_message | 2 | Nur Existenzprüfung; Nur count >= 1 |
| tests/ui/test_chat_ui.py | test_conversation_view_message_content_visible | 2 | Nur Existenzprüfung |
| tests/state_consistency/test_prompt_consistency.py | test_prompt_db_list_editor_consistency | 2 | Nur Existenzprüfung |
| tests/test_agent_hr.py | test_agent_save_load | 1 | Nur Existenzprüfung |
| tests/test_agent_hr.py | test_validation_duplicate_name | 1 | Nur Existenzprüfung |
| tests/test_agent_hr.py | test_validation_empty_name | 1 | Nur Existenzprüfung |

---

## 5. Fehlerklassen mit geringer Streuung

*(Nur eine Domäne deckt die Fehlerklasse ab → weniger robust)*

| Fehlerklasse | Domänen | Bewertung |
|--------------|---------|-----------|
| rag_silent_failure | failure_modes | Nur eine Domäne |
| tool_failure_visibility | failure_modes | Nur eine Domäne |
| contract_schema_drift | failure_modes | Nur eine Domäne |
| optional_dependency_missing | failure_modes | Nur eine Domäne |
| metrics_false_success | failure_modes | Nur eine Domäne |
| late_signal_use_after_destroy | async_behavior | Nur eine Domäne |
| async_race | async_behavior | Nur eine Domäne |
| request_context_loss | cross_layer | Nur eine Domäne |
| startup_ordering | startup | Nur eine Domäne |

---

## 6. Top-5 Wartungsempfehlungen

| Priorität | Typ | Ziel | Empfehlung |
|-----------|-----|------|------------|
| 1 | Flaky-Risiko | tests/async_behavior/test_signal_after_widget_destroy.py::test_signal_after_widget_destroy_no_crash | Flaky-Risiko prüfen: Cleanup-/Destroy-Sensitivität; Event-Wait, Timing… |
| 2 | Flaky-Risiko | tests/async_behavior/test_chatwidget_signal_after_destroy.py::test_chatwidget_signal_during_destroy_no_crash | Flaky-Risiko prüfen: Cleanup-/Destroy-Sensitivität; Event-Wait, Timing… |
| 3 | Flaky-Risiko | tests/chaos/test_provider_timeout_chat.py::test_provider_delay_then_cancel_cleans_up_streaming_state | Flaky-Risiko prüfen: Timeout-/Delay-Szenarien; Fault-Injection, Timing… |
| 4 | Schwacher Test | tests/smoke/test_app_startup.py::test_critical_imports | Assertion prüfen: Nur Existenzprüfung. Wirkung statt nur Existenz test… |
| 5 | Schwacher Test | tests/test_agent_hr.py::test_registry_lookup | Assertion prüfen: Nur Existenzprüfung. Wirkung statt nur Existenz test… |

---

## 7. Empfehlung für QA Self-Healing Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | AST-basierte Assertion-Analyse | Schwache Tests präziser erkennen |
| 2 | Flaky-Historie aus CI-Logs | Tatsächlich flaky vs. nur Risiko |
| 3 | Autopilot-Integration | Wartungsempfehlungen in Sprint-Planung |

---

## 8. Verweise

- [REGRESSION_CATALOG.md](REGRESSION_CATALOG.md)
- [CHAOS_QA_PLAN.md](CHAOS_QA_PLAN.md)
- [QA_AUTOPILOT.md](QA_AUTOPILOT.md)

*QA Self-Healing Iteration 1 – generiert am 2026-03-15.*
