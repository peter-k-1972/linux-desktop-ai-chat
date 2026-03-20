# QA Incident Replay – Pilot-Iteration 1

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf  
**Zweck:** Drei realistisch priorisierte Pilotfälle als Startpunkt. Keine Tests, kein Runner – nur Pilotarchitektur und QA-Priorisierung.

---

## 1. Die drei Pilotfälle

| # | Subsystem | Incident-Klasse | Risk-Radar-Rang |
|---|-----------|-----------------|-----------------|
| 1 | Startup/Bootstrap | Ollama unreachable | Top-3 |
| 2 | RAG | ChromaDB Netzwerkfehler | Top-1 |
| 3 | Debug/EventBus | EventType Drift | Top-2 |

---

## 2. Warum genau diese drei Pilotfälle architektonisch sinnvoll sind

### 2.1 Abdeckung der Top-3-Risiken

| Begründung | Beschreibung |
|------------|---------------|
| **Risikokongruenz** | Die drei Pilotfälle entsprechen exakt den Top-3-Risiken aus QA_RISK_RADAR. Kein Zufall – sie adressieren die höchsten bekannten Lücken. |
| **Verschiedene Replay-Typen** | Jeder Pilotfall nutzt einen anderen replay_type: startup_dependency_failure, fault_injection, event_contract_drift. Die Pilotiteration validiert damit das Replay-Schema über unterschiedliche Szenarien. |
| **Verschiedene Schichten** | Startup (Bootstrap), RAG (Service/Persistenz), Debug (Observability). Keine Redundanz – drei architektonisch getrennte Bereiche. |
| **Kaskadenwirkung** | Alle drei betreffen kritische Abhängigkeiten: Ollama → Chat/Agent/RAG; ChromaDB → RAG; EventBus → Debug/Timeline. Fehler hier haben hohe Reichweite. |
| **Bestehende Test-Anker** | Es existieren bereits Tests in der Nähe (test_startup_without_ollama, test_chroma_unreachable, test_event_type_drift). Die Incidents können an diese angebunden werden – kein Greenfield. |
| **Governance-Validierung** | degraded_mode_failure, rag_silent_failure, debug_false_truth sind etablierte Fehlerklassen. Die Pilotiteration prüft, ob das Incident-System sauber in REGRESSION_CATALOG integriert. |

### 2.2 Architektonische Diversität

| Pilotfall | Laufzeit-Schicht | Abhängigkeitstyp | Fehlermodus |
|-----------|------------------|-------------------|-------------|
| Ollama unreachable | startup | runtime (Provider) | Externer Dienst nicht erreichbar |
| ChromaDB Netzwerkfehler | service/persistence | persistence (optional) | Netzwerk/Connection während Laufzeit |
| EventType Drift | observability | contract (Schema) | Drift zwischen Code und Registry |

**Ergebnis:** Drei unterschiedliche Fehlermuster. Keine Überlappung – maximale Lernkurve pro Pilotfall.

---

## 3. Replay-Typen pro Pilotfall

| Pilotfall | replay_type | Begründung |
|-----------|-------------|------------|
| **Startup / Ollama unreachable** | `startup_dependency_failure` | Optionale Abhängigkeit (Ollama) nicht erreichbar beim Start. Kein Runtime-Fault – der Zustand ist vor App-Start gegeben. |
| **RAG / ChromaDB Netzwerkfehler** | `fault_injection` | Gezielte Störung während Laufzeit: ChromaDB war erreichbar, wird dann unreachable (Connection refused, Timeout). Kein Import-Fehler. |
| **Debug/EventBus / EventType Drift** | `event_contract_drift` | Event/Schema passt nicht zu Erwartung: Neuer EventType emittiert, aber nicht in Registry/Timeline. Drift zwischen Code und Contract. |

**Alternativen (falls nötig):**

| Pilotfall | Alternative | Wann |
|-----------|-------------|------|
| Ollama unreachable | `provider_unreachable` | Wenn Fokus auf „Provider während Chat“ statt „Startup“ |
| ChromaDB Netzwerkfehler | `hybrid` | Wenn Startup + RAG-Check kombiniert werden muss |
| EventType Drift | – | `event_contract_drift` ist eindeutig passend |

---

## 4. Failure Classes pro Pilotfall

| Pilotfall | Primäre failure_class | Sekundäre failure_class | Begründung |
|-----------|------------------------|--------------------------|------------|
| **Startup / Ollama unreachable** | `degraded_mode_failure` | `optional_dependency_missing`, `startup_ordering` | App muss mit fehlendem Ollama starten (degraded). Optional: Import-Fehler. Init-Reihenfolge kann relevant sein. |
| **RAG / ChromaDB Netzwerkfehler** | `rag_silent_failure` | `debug_false_truth` | RAG fehlschlägt, Nutzer weiß es nicht. Wenn RAG_RETRIEVAL_FAILED nicht emittiert, auch debug_false_truth. |
| **Debug/EventBus / EventType Drift** | `debug_false_truth` | `contract_schema_drift` | Timeline zeigt nicht, was passiert (debug_false_truth). EventType-Registry ist Contract – Drift zwischen Code und Registry |

**Regel:** Jeder Pilotfall hat genau eine **primäre** failure_class für die Incident-Klassifikation. Sekundäre sind für Cross-Referencing (z.B. Replay kann mehrere Fehlerklassen adressieren).

---

## 5. Observability Contracts pro Pilotfall

### 5.1 Startup / Ollama unreachable

| observability_contract | Wichtigkeit | Begründung |
|------------------------|-------------|------------|
| **events** | niedrig | Kein spezielles Event bei Startup ohne Ollama – App startet, Chat verfügbar. |
| **ui_state** | **hoch** | MainWindow muss erscheinen. Chat-Widget muss sichtbar und nutzbar sein. |
| **debug_visibility** | niedrig | Kein RAG/LLM-Event bei Startup – irrelevant. |
| **invariant** | **hoch** | Kein Crash. Kein ImportError. |

**Kern:** Sichtbarkeit der UI (MainWindow, Chat-Widget). Kein Crash. Kein harter Import.

### 5.2 RAG / ChromaDB Netzwerkfehler

| observability_contract | Wichtigkeit | Begründung |
|------------------------|-------------|------------|
| **events** | **hoch** | RAG_RETRIEVAL_FAILED muss emittiert werden. |
| **events[].in_timeline** | **hoch** | Event muss in Debug-Timeline sichtbar sein. |
| **debug_visibility** | **hoch** | RAG_RETRIEVAL_FAILED in Timeline sichtbar. |
| **ui_state** | mittel | Chat läuft weiter. Send-Button wieder klickbar. |

**Kern:** RAG_RETRIEVAL_FAILED present + in_timeline. Ohne das ist der Replay nicht erfüllt.

### 5.3 Debug/EventBus / EventType Drift

| observability_contract | Wichtigkeit | Begründung |
|------------------------|-------------|------------|
| **events** | **hoch** | EventType muss in Registry sein. |
| **events[].in_timeline** | **hoch** | EventType muss in Timeline mit korrektem Label erscheinen. |
| **debug_visibility** | **hoch** | Kein „unknown“, kein Filter. |
| **invariant** | **hoch** | Alle emittierten EventTypes in Registry. |

**Kern:** Vollständige Sichtbarkeit in Registry und Timeline. Kein Drift.

---

## 6. Testdomänen – später ableitbar

| Pilotfall | Testdomänen (aus mapping) | Begründung |
|-----------|----------------------------|------------|
| **Startup / Ollama unreachable** | `startup`, `failure_modes` | Startup-Tests für degraded_mode. failure_mode für „Ollama unreachable“. |
| **RAG / ChromaDB Netzwerkfehler** | `failure_modes`, `chaos`, `cross_layer` | failure_mode für ChromaDB Connection Error. chaos für Fault-Injection. cross_layer für Debug-Sichtbarkeit (RAG_RETRIEVAL_FAILED in Timeline). |
| **Debug/EventBus / EventType Drift** | `contract`, `failure_modes`, `meta` | contract für EventType-Registry. failure_mode für RAG-Fehler (der das Event auslöst). meta für Drift-Sentinel. |

**Ableitung:** `replay.yaml` → `mapping.test_domains` → spätere Testimplementierung. Die Pilotiteration definiert nur die Ziele – keine Tests.

### 6.1 Konkrete Testdomänen-Matrix

| Pilotfall | Primäre Domäne | Sekundäre Domäne | Marker (später) |
|-----------|----------------|------------------|-----------------|
| Ollama unreachable | startup | failure_modes | startup, failure_mode |
| ChromaDB Netzwerkfehler | failure_modes | chaos, cross_layer | failure_mode, chaos |
| EventType Drift | contract | meta, failure_modes | contract |

---

## 7. Risiken, die früh adressiert werden

### 7.1 Risk-Radar-Entlastung

| Risiko (aus QA_RISK_RADAR) | Pilotfall | Entlastung |
|----------------------------|-----------|------------|
| **RAG: ChromaDB Netzwerk-Fehler nicht getestet** | ChromaDB Netzwerkfehler | Incident + Replay definieren. Später: Test als Guard. Restlücken reduzieren. |
| **Debug/EventBus: Drift – Neuer EventType ohne Registry/Timeline** | EventType Drift | Incident + Replay definieren. Später: Meta-Test/Drift-Sentinel. Drift-Risiko reduzieren. |
| **Startup: Ollama nicht erreichbar nicht getestet** | Ollama unreachable | Incident + Replay definieren. Später: Startup-Test. Restlücken reduzieren. |

### 7.2 Frühe Risikominimierung (ohne Test)

| Nutzen | Beschreibung |
|--------|--------------|
| **Bewusstsein** | Die drei Risiken werden explizit als Incidents dokumentiert. Kein implizites Wissen mehr. |
| **Reproduzierbarkeit** | Replay-Verträge definieren die Reproduktion. Später: Test folgt dem Vertrag. |
| **Priorisierung** | Control Center und Autopilot können Incidents ohne Guard sichtbar machen. |
| **Governance** | Incident-Replay-Lifecycle wird validiert. Skripte (create, validate, bind) können an echten Fällen erprobt werden. |
| **Kaskaden-Sicht** | Dependency Graph: Ollama und ChromaDB sind in kritischen Pfaden. Incidents dokumentieren die tatsächlichen Ausfallstellen. |

### 7.3 Heatmap-Dimensionen

| Pilotfall | Heatmap-Dimensionen | Verbesserung |
|-----------|---------------------|--------------|
| Ollama unreachable | Failure_Coverage, Drift_Governance_Coverage | Startup/Bootstrap: Contract weak → Incident adressiert |
| ChromaDB Netzwerkfehler | Failure_Coverage, Drift_Governance_Coverage | RAG: ChromaDB Netzwerk weak → Incident adressiert |
| EventType Drift | Contract_Coverage, Drift_Governance_Coverage | Debug/EventBus: Drift weak → Incident adressiert |

---

## 8. Pilotfall-Spezifikation (Kurz)

### 8.1 Pilotfall 1: Startup / Ollama unreachable

| Attribut | Wert |
|----------|------|
| **Incident-ID** | INC-PILOT-001 (Platzhalter) |
| **Subsystem** | Startup/Bootstrap |
| **replay_type** | startup_dependency_failure |
| **failure_class** | degraded_mode_failure |
| **Observability** | ui_state (MainWindow, Chat-Widget), no_crash |
| **Testdomänen** | startup, failure_modes |
| **Risiko** | Top-3, Restlücken Medium |

### 8.2 Pilotfall 2: RAG / ChromaDB Netzwerkfehler

| Attribut | Wert |
|----------|------|
| **Incident-ID** | INC-PILOT-002 (Platzhalter) |
| **Subsystem** | RAG |
| **replay_type** | fault_injection |
| **failure_class** | rag_silent_failure, debug_false_truth |
| **Observability** | RAG_RETRIEVAL_FAILED present, in_timeline |
| **Testdomänen** | failure_modes, chaos, cross_layer |
| **Risiko** | Top-1, Restlücken Medium |

### 8.3 Pilotfall 3: Debug/EventBus / EventType Drift

| Attribut | Wert |
|----------|------|
| **Incident-ID** | INC-PILOT-003 (Platzhalter) |
| **Subsystem** | Debug/EventBus |
| **replay_type** | event_contract_drift |
| **failure_class** | debug_false_truth, contract_schema_drift |
| **Observability** | EventType in Registry, in Timeline mit Label |
| **Testdomänen** | contract, meta, failure_modes |
| **Risiko** | Top-2, Drift-Risiko High |

---

## 9. Nächste Schritte (nach Pilotarchitektur)

| Schritt | Beschreibung |
|---------|--------------|
| 1 | Incident-Verzeichnisse anlegen (create_incident.py oder manuell) |
| 2 | incident.yaml für Pilotfall 1, 2, 3 ausfüllen |
| 3 | replay.yaml für Pilotfall 1, 2, 3 ausfüllen |
| 4 | bindings.json erstellen |
| 5 | validate_incident.py ausführen |
| 6 | generate_incident_registry.py ausführen |
| 7 | Projektion in Control Center, Autopilot prüfen |

**Keine Tests in dieser Iteration.** Kein Runner. Nur Pilotarchitektur und QA-Priorisierung.

---

## 10. Zusammenfassung

| Frage | Antwort |
|-------|---------|
| **Warum diese drei?** | Top-3-Risiken, verschiedene Replay-Typen, verschiedene Schichten, bestehende Test-Anker. |
| **Replay-Typen** | startup_dependency_failure, fault_injection, event_contract_drift |
| **Failure Classes** | degraded_mode_failure, rag_silent_failure, debug_false_truth (+ optional: optional_dependency_missing, startup_ordering, contract_schema_drift) |
| **Observability** | Ollama: ui_state, no_crash. ChromaDB: RAG_RETRIEVAL_FAILED in Timeline. EventType: Registry + Timeline. |
| **Testdomänen** | startup, failure_modes, chaos, cross_layer, contract, meta |
| **Risiken adressiert** | Top-3 aus Risk Radar, Restlücken, Drift-Risiko, Heatmap Weak Spots |

---

*QA Incident Pilot – Iteration 1. Architektur, keine Implementierung.*
