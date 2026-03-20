# QA Evolution Map – Linux Desktop Chat

**Datum:** 15. März 2026  
**Zweck:** Strategische Übersicht – Subsystem ↔ Fehlerklasse ↔ Test-Absicherung ↔ Restrisiko ↔ nächster QA-Hebel.  
**Verbindet:** Risk Radar, Regression Catalog, Coverage Map.

---

## 1. Zweck

Die Evolution Map unterstützt:

- **Verknüpfung:** Welche Fehlerklassen betreffen welches Subsystem?
- **Absicherung:** Welche Tests/Testdomänen decken das ab?
- **Restrisiko:** Was bleibt offen?
- **Priorisierung:** Welcher nächste QA-Schritt bringt den größten Nutzen?

---

## 2. Leselogik

| Spalte | Bedeutung |
|--------|-----------|
| **Subsystem** | Aus Risk Radar |
| **Relevante Fehlerklassen** | Aus Regression Catalog, diesem Subsystem zugeordnet |
| **Abgesichert durch** | Testdomänen + konkrete Dateien |
| **Restrisiko** | Low / Medium / High |
| **Nächster QA-Hebel** | Empfohlener nächster Schritt |

---

## 3. Evolution Map pro Subsystem

| Subsystem | Relevante Fehlerklassen | Abgesichert durch | Restrisiko | Nächster QA-Hebel |
|-----------|-------------------------|-------------------|------------|-------------------|
| **Chat** | ui_state_drift, async_race, late_signal_use_after_destroy, request_context_loss, contract_schema_drift | async_behavior (shutdown, signal_after_destroy), cross_layer (prompt_apply), failure_modes (llm_chunk_parsing), golden_path | Low | – |
| **Agentensystem** | ui_state_drift | regression (agent_delete), cross_layer (agent_delete), golden_path | Low | Live-Tests für echte Agent-Ausführung |
| **Prompt-System** | request_context_loss | cross_layer (prompt_apply_affects_real_request), contracts (prompt_contract), failure_modes (prompt_service_failure) | Low | – |
| **RAG** | rag_silent_failure, debug_false_truth, optional_dependency_missing, degraded_mode_failure | failure_modes (chroma_unreachable, chroma_import, rag_retrieval), contracts (rag_retrieval) | Low | – |
| **Debug/EventBus** | debug_false_truth, contract_schema_drift | cross_layer (debug_view_matches_failure), failure_modes (event_store), contracts (debug_event), meta (event_type_drift) | Low | Drift-Sentinel bei neuem EventType (bereits vorhanden) |
| **Metrics** | metrics_false_success | failure_modes (metrics_on_failed_chat_or_task) | Low | – |
| **Startup/Bootstrap** | startup_ordering, degraded_mode_failure | startup (without_ollama, optional_dependencies_missing) | Low | – |
| **Tools** | tool_failure_visibility | failure_modes (tool_failure), contracts (tool_result_contract) | Low | – |
| **Provider/Ollama** | contract_schema_drift | failure_modes (ollama_broken_response), contracts (ollama_response_contract, llm_stream_contract) | Low | – |
| **Persistenz/SQLite** | – | failure_modes (sqlite_lock), integration, state_consistency | Low | – |

---

## 4. Fehlerklassen-Übersicht (welche Subsysteme)

| Fehlerklasse | Betroffene Subsysteme | Abdeckung |
|--------------|------------------------|-----------|
| ui_state_drift | Chat, Agentensystem | ✅ |
| async_race | Chat | ✅ |
| late_signal_use_after_destroy | Chat | ✅ |
| request_context_loss | Chat, Prompt-System | ✅ |
| rag_silent_failure | RAG | ✅ |
| debug_false_truth | RAG, Debug/EventBus | ✅ |
| startup_ordering | Startup/Bootstrap | ✅ |
| degraded_mode_failure | RAG, Startup/Bootstrap | ✅ |
| contract_schema_drift | Chat, Debug/EventBus, Provider/Ollama | ✅ |
| metrics_false_success | Metrics | ✅ |
| tool_failure_visibility | Tools | ✅ |
| optional_dependency_missing | RAG | ✅ |

---

## 5. Top-3 QA-Hebel für den nächsten Sprint

| Rang | Hebel | Subsystem | Nutzen |
|------|-------|-----------|--------|
| 1 | **Live-Tests für Agent-Ausführung** | Agentensystem | Echte Orchestration/Execution abdecken |
| 2 | **Init-Reihenfolge Contract** | Startup/Bootstrap | startup_ordering formal absichern |
| 3 | **Embedding-Service Failure** | RAG | Ollama Embedding-API unreachable |

---

## 6. Restrisiken (klar sichtbar)

| Restrisiko | Subsystem | Priorität |
|------------|-----------|-----------|
| Echte Agent-Ausführung nur live getestet | Agentensystem | P2 |
| Kein dedizierter Contract für Startup-Init | Startup/Bootstrap | P3 |
| Embedding-API (Ollama) unreachable | RAG | P3 |

---

## 7. Verweise

- [QA_RISK_RADAR.md](QA_RISK_RADAR.md) – Priorisierte Risikoübersicht
- [REGRESSION_CATALOG.md](REGRESSION_CATALOG.md) – Fehlerklassen, Test-Zuordnung
- [QA_INCIDENT_REPLAY_ARCHITECTURE.md](QA_INCIDENT_REPLAY_ARCHITECTURE.md) – Incident → Replay → Regression Guard
- [QA_LEVEL3_COVERAGE_MAP.md](QA_LEVEL3_COVERAGE_MAP.md) – Risk-based Coverage

---

## 8. Empfehlung für Evolution Map Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Automatische Verknüpfung aus Regression Catalog parsen | Evolution Map aktuell halten |
| 2 | Restrisiko-Score pro Subsystem | Priorisierung verfeinern |
| 3 | Cockpit-Integration: Top-Hebel in QA_STATUS | Sichtbarkeit im Tagesgeschäft |

---

*Evolution Map erstellt am 15. März 2026. Basis: Risk Radar, Regression Catalog, Coverage Map.*
