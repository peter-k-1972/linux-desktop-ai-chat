# QA Level 3 – Test Governance Rules

**Datum:** 15. März 2026  
**Zweck:** Konkrete Testpflichten für neue Codepfade. Keine Prosa – anwendbare Regeln.

---

## 1. Neuer Workflow (z.B. Chat-Flow, Agent-Flow, RAG-Flow)

| Pflicht | Regel | Marker |
|---------|-------|--------|
| Golden Path | Mindestens 1 Test: E2E mit realistischen Mocks | `golden_path` |
| Cross-Layer | Mindestens 1 Test: UI ↔ Service ↔ Persistenz | `cross_layer` |
| Failure | Mindestens 1 Test: Was passiert, wenn ein Schritt fehlschlägt? | `failure_mode` |
| Debug | Debug-Sichtbarkeit: Wird ein Event emittiert? Ist es in der Timeline? | – |
| Async | Falls async: `async_behavior`-Test für Race/Cancellation | `async_behavior` |
| Datenstruktur | Falls neue Struktur: Contract-Test | `contract` |

---

## 2. Neuer EventType (EventBus / Debug)

| Pflicht | Regel | Marker |
|---------|-------|--------|
| Contract | `test_debug_event_contract.py`: EventType-Enum-Wert in Stabilitätstest | `contract` |
| Debug-Sichtbarkeit | Event in Timeline sichtbar? Falls nicht: `event_timeline_view.py` type_map ergänzen | – |
| Failure-Pfad | Falls Event bei Fehler emittiert: `failure_mode`-Test prüft Emission | `failure_mode` |

---

## 3. Neuer Service (z.B. RAG, Metrics, Tool)

| Pflicht | Regel | Marker |
|---------|-------|--------|
| Failure | Mindestens 1 Test: Service wirft / externe Abhängigkeit fehlt | `failure_mode` |
| Debug | Fehler-Events werden emittiert und sind sichtbar | – |
| Optional | Falls optional (ChromaDB, Ollama): `degraded_mode`-Test | `startup` |

---

## 4. Neuer UI-Pfad (z.B. Panel, Button, Combo)

| Pflicht | Regel | Marker |
|---------|-------|--------|
| Behavior | UI-Test: Sichtbar, klickbar, Signal/Effekt | `ui` |
| Cross-Layer | Falls Wirkung auf Service: `cross_layer`-Test | `cross_layer` |
| State | Falls State-Konsistenz relevant: `state_consistency` | `state_consistency` |

---

## 5. Neue optionale Abhängigkeit

| Pflicht | Regel | Marker |
|---------|-------|--------|
| Import | Import-Fehler → `VectorStoreError` o.ä., kein Crash | `failure_mode` |
| Startup | App startet mit fehlender Abhängigkeit, degradiert sauber | `startup` |
| Nutzung | Nutzung nach Startup funktioniert (z.B. Chat ohne RAG) | `startup` |

---

## 6. Neue Datenstruktur / API (Contract)

| Pflicht | Regel | Marker |
|---------|-------|--------|
| Pflichtfelder | Contract-Test: Pflichtfelder, Serialisierung | `contract` |
| Stabilität | Enum-Werte, Typen stabil | `contract` |

---

## 7. Checkliste für neue Features

```
[ ] Golden Path oder Cross-Layer Test
[ ] Failure-Test (falls Fehler möglich)
[ ] Debug-Sichtbarkeit (Event, Timeline)
[ ] Async-Test (falls async)
[ ] Contract-Test (falls neue Struktur)
[ ] Marker gesetzt (contract, failure_mode, cross_layer, async_behavior, startup)
```

---

## 8. Marker-Konvention

| Marker | Wann setzen |
|--------|-------------|
| `contract` | Vertrag, Schema, API-Stabilität |
| `failure_mode` | Fehlerinjection, Exception-Handling |
| `async_behavior` | Event-Loop, Race, Cancellation |
| `cross_layer` | Mehrere Schichten (UI↔Service↔Persistenz) |
| `startup` | App-Start, degraded mode |
| `regression` | Reproduziert bekannten Bug |

---

*Test Governance Rules erstellt am 15. März 2026.*
