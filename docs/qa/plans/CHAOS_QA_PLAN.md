# Chaos QA Plan – Linux Desktop Chat

**Datum:** 15. März 2026  
**Zweck:** Kontrollierte Fault-Injection für Resilienz-Prüfung der wichtigsten Kaskadenpfade.

---

## 1. Zweck

Die Chaos-Test-Suite simuliert gezielte Störungen und prüft:

- **Recovery:** System bleibt nach Fehlern benutzbar
- **Zustandskonsistenz:** Keine Halbzustände, _streaming wird zurückgesetzt
- **Sichtbarkeit:** Fehler werden nicht still verschluckt (z.B. RAG_RETRIEVAL_FAILED)
- **Keine Flakiness:** Reproduzierbar, keine Zufallsparameter

---

## 2. Marker / Ausführungslogik

| Marker | Bedeutung |
|--------|-----------|
| `@pytest.mark.chaos` | Chaos-Test (Fault-Injection, Resilienz) |

**Ausführung:**

```bash
# Nur Chaos-Tests
pytest -m chaos -v

# Standard-CI (Chaos inkludiert)
pytest -m "not live and not slow"
```

**Einordnung:** Chaos-Tests sind `integration` + `chaos`. Sie laufen in der Standard-CI (full).

---

## 3. Chaos-Szenarien

| Szenario | Datei | Beschreibung |
|----------|-------|--------------|
| Provider Timeout | test_provider_timeout_chat.py | Provider verzögert stark → Abbruch → _streaming zurückgesetzt |
| Provider Delay | test_provider_timeout_chat.py | Provider antwortet verzögert → zweiter Send funktioniert |
| RAG unreachable | test_embedding_service_unreachable.py | RAG/Embedding nicht erreichbar → Chat läuft weiter, RAG_RETRIEVAL_FAILED |
| Startup partial | test_startup_partial_services.py | MainWindow mit degradiertem RAG → App startet |
| Persistence failure | test_persistence_failure_after_success.py | DB schlägt nach Assistant-Save fehl → _streaming zurückgesetzt |
| Recovery after persistence | test_persistence_failure_after_success.py | Nach DB-Fehler: Wechsel zu funktionierender DB → Chat funktioniert |

---

## 4. Zugehörige Fehlerklassen

| Chaos-Szenario | Fehlerklasse (REGRESSION_CATALOG) |
|----------------|-----------------------------------|
| Provider Timeout | async_race, late_signal_use_after_destroy |
| RAG unreachable | rag_silent_failure, debug_false_truth |
| Startup partial | degraded_mode_failure, startup_ordering |
| Persistence failure | – (erweitert Failure Coverage) |

---

## 5. Erwartetes Recovery-Verhalten

| Störung | Erwartetes Verhalten |
|---------|----------------------|
| Provider Timeout | Task abbrechbar, _streaming = False, zweiter Send möglich |
| RAG unreachable | Chat läuft weiter, RAG_RETRIEVAL_FAILED Event, kein stilles Scheitern |
| Startup partial | MainWindow startet, Chat-Widget vorhanden, degradierter Modus konsistent |
| Persistence failure | _streaming = False, zweiter Chat mit funktionierender DB möglich |

---

## 6. Einordnung CI / Testlevel

| Level | Chaos-Tests |
|-------|-------------|
| **fast** | – |
| **full** | Alle Chaos-Tests (integration, nicht live) |
| **live** | – |

**CI-Kommando:** `pytest -m "not live and not slow"` – Chaos-Tests enthalten.

---

## 7. Helpers (tests/helpers/chaos_fixtures.py)

| Helper | Zweck |
|--------|-------|
| DelayedProviderStub | Provider mit konfigurierbarer Verzögerung |
| TimeoutProviderStub | Provider der sehr lange wartet (Timeout-Simulation) |
| FailingRepositoryStub | DB die bei assistant-Save fehlschlägt |

---

## 8. Empfehlung für Mini-Chaos-QA Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | test_provider_partial_stream.py | Abgebrochener Stream nach Teilantwort |
| 2 | test_duplicate_or_delayed_events.py | EventBus unter Doppel-/Verzögerungs-Events |
| 3 | Chaos-Tests in QA_DEPENDENCY_GRAPH verknüpfen | Kaskadenpfade ↔ Chaos-Szenarien |

---

*Chaos QA Plan erstellt am 15. März 2026.*
