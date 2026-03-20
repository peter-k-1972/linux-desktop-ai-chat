# QA Risk Radar – Linux Desktop Chat

**Datum:** 15. März 2026  
**Zweck:** Priorisierte Risikoübersicht pro Subsystem für risikobasierte QA-Planung.  
**Kein Code-Coverage** – QA-/Architektur-Risiko sichtbar machen.

---

## 1. Zweck

Das Risk Radar unterstützt:

- **Priorisierung:** Welche Subsysteme zuerst absichern?
- **Planung:** Nächste QA-Schwerpunkte ableiten
- **Transparenz:** Risikodimensionen nachvollziehbar bewerten

---

## 2. Bewertungslogik

### Risikodimensionen

| Dimension | Bedeutung | Stufen |
|-----------|-----------|--------|
| **Failure Impact** | Wie kritisch ist ein Fehler für den Nutzer? | Low / Medium / High |
| **Async/State** | qasync, Signale, Race-Conditions | Low / Medium / High |
| **Cross-Layer** | UI↔Service↔Persistenz, Wahrheitsebenen | Low / Medium / High |
| **Failure-Test** | failure_mode-Tests vorhanden? | Low / Medium / High |
| **Contract/Gov** | Contract-Tests, Governance-Regeln | Low / Medium / High |
| **Drift-Risiko** | Neue EventTypes, Services ohne Sentinel | Low / Medium / High |
| **Restlücken** | Bekannte offene Lücken aus Coverage Map | Low / Medium / High |

### Priorität

- **P1:** Mindestens eine Dimension High + Restlücken oder Drift-Risiko
- **P2:** Mehrere Medium oder eine kritische Lücke
- **P3:** Überwiegend Low, gut abgedeckt

---

## 3. Subsystem-Bewertung

| Subsystem | Failure Impact | Async/State | Cross-Layer | Failure-Test | Contract/Gov | Drift | Restlücken | **Priorität** |
|-----------|----------------|-------------|-------------|--------------|--------------|-------|------------|---------------|
| **Chat** | High | High | High | High | High | Medium | Low | **P2** |
| **Agentensystem** | High | Medium | Medium | Medium | High | Low | Low | **P2** |
| **Prompt-System** | Medium | Low | High | Low | High | Low | Low | **P2** |
| **RAG** | High | Medium | Medium | High | High | Low | Medium | **P1** |
| **Debug/EventBus** | Medium | Medium | Medium | High | High | High | Low | **P1** |
| **Metrics** | Medium | Low | Low | High | Medium | Low | Low | **P3** |
| **Startup/Bootstrap** | High | Medium | Medium | High | Low | Medium | Medium | **P1** |
| **Tools** | Medium | Low | Low | High | High | Low | Low | **P3** |
| **Provider/Ollama** | High | Medium | Low | Medium | Low | Low | Medium | **P2** |
| **Persistenz/SQLite** | Medium | Low | Medium | High | Low | Low | Low | **P3** |

---

## 4. Begründung pro Subsystem

### Chat (P2)
- **Failure Impact High:** Kernfunktion, Antwort sichtbar/leer = kritisch
- **Async/State High:** Streaming, qasync, Senden während Stream
- **Cross-Layer High:** UI↔run_chat↔LLM↔RAG
- **Abdeckung gut:** Golden Path, cross_layer, async_behavior, failure (LLM Chunk)
- **Restlücke:** ChromaDB Netzwerk-Fehler indirekt über RAG

### Agentensystem (P2)
- **Failure Impact High:** Agent-Auswahl, System-Prompt in Messages
- **Async/State Medium:** Orchestration, ExecutionEngine
- **Abdeckung:** Golden Path, regression, state_consistency
- **Restlücke:** Live-Tests für echte Agent-Ausführung

### Prompt-System (P2)
- **Cross-Layer High:** UI→Service→Request, request_context_loss
- **Failure-Test Low:** Kein dedizierter failure_mode für Prompt
- **Abdeckung:** Contract, cross_layer (prompt_apply_affects_real_request)

### RAG (P1)
- **Failure Impact High:** RAG fehlschlägt, Nutzer weiß es nicht
- **Restlücken Medium:** ChromaDB Netzwerk nicht getestet, nur Import-Fehler
- **Abdeckung:** retrieval_failure, chroma_import_failure, rag_empty_results
- **Drift:** Optional dependency – neue RAG-Features können Lücken öffnen

### Debug/EventBus (P1)
- **Drift-Risiko High:** Neuer EventType ohne Contract/Timeline
- **Abdeckung:** EventStore, DebugStore, cross_layer (debug_view_matches_failure)
- **Sentinel:** EventType-Registry, Meta-Tests vorhanden

### Metrics (P3)
- **Failure-Test High:** test_metrics_on_failed_chat_or_task
- **Abdeckung gut:** metrics_false_success abgedeckt
- **Impact Medium:** Falsche Metriken stören, brechen aber nicht

### Startup/Bootstrap (P1)
- **Failure Impact High:** App startet nicht = Blockade
- **Restlücken Medium:** Ollama nicht erreichbar nicht getestet
- **Abdeckung:** RAG degraded, startup_ordering
- **Contract/Gov Low:** Keine dedizierten Contract-Tests für Init-Reihenfolge

### Tools (P3)
- **Failure-Test High:** test_tool_failure, tool_failure_visibility
- **Contract High:** test_tool_result_contract
- **Abdeckung gut**

### Provider/Ollama (P2)
- **Failure Impact High:** LLM nicht erreichbar
- **Failure-Test Medium:** test_ollama_broken_response
- **Restlücken Medium:** Ollama offline/degraded nicht getestet
- **Contract Low:** Kein Provider-Contract

### Persistenz/SQLite (P3)
- **Failure-Test High:** test_sqlite_lock
- **Abdeckung:** Integration-Tests, state_consistency
- **Impact Medium:** DB-Fehler meist recoverable

---

## 5. Top-3-Risikobereiche

*(Wird vom QA-Cockpit gelesen und in QA_STATUS.md angezeigt.)*

| Rang | Subsystem | Hauptrisiko |
|------|-----------|-------------|
| 1 | **RAG** | ChromaDB Netzwerk-Fehler nicht getestet; optional dependency |
| 2 | **Debug/EventBus** | Drift: Neuer EventType ohne Registry/Timeline |
| 3 | **Startup/Bootstrap** | Ollama nicht erreichbar nicht getestet; degraded_mode nur RAG |

---

## 6. Empfohlene nächste QA-Schwerpunkte

| Priorität | Schwerpunkt | Aufwand | Status |
|-----------|-------------|---------|--------|
| 1 | **RAG:** test_chroma_unreachable (Netzwerk) | Klein | ✅ umgesetzt |
| 2 | **Startup:** degraded_mode ohne Ollama | Mittel | ✅ umgesetzt |
| 3 | **Provider:** Contract für Ollama-Response-Format | Klein | ✅ umgesetzt |
| 4 | **Prompt:** failure_mode für Prompt-Service | Klein | ✅ umgesetzt |

---

## 7. Pflege

- **Aktualisierung:** Bei neuem Subsystem, neuem Risiko oder abgeschlossener Lücke
- **Quellen:** QA_LEVEL3_COVERAGE_MAP.md, REGRESSION_CATALOG.md, AUDIT_REPORT.md
- **Verknüpfung:** [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md) – Subsystem ↔ Fehlerklasse ↔ Tests
- **Frequenz:** Nach größeren Releases oder QA-Sprints
- **Cockpit:** Top-3 wird automatisch aus dieser Datei gelesen (scripts/qa/checks.py)

---

## 8. Empfehlung für Risk Radar Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Risiko-Scores pro Subsystem in Cockpit/JSON | Automatische Prioritätsberechnung |
| 2 | Verknüpfung Subsystem ↔ Testdomänen | Welche Tests decken welches Risiko ab |
| 3 | Lücken-Check: Restlücken vs. tatsächliche Tests | Drift bei neuem Risiko ohne Test |

---

*Risk Radar erstellt am 15. März 2026. Basis: Coverage Map, Regression Catalog, Audit-Matrix.*
