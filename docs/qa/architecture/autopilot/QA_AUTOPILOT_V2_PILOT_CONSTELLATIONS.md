# QA Autopilot v2 – Pilotkonstellationen

**Datum:** 15. März 2026  
**Status:** Konkrete Pilot-Szenarien  
**Zweck:** Detaillierte Abbildung von drei Pilotkonstellationen auf Input-Signale, Priorisierung, Guard-Typen, Sprint-Empfehlungen und Warnungen.

---

## Übersicht

| Konstellation | Subsystem | Szenario |
|---------------|-----------|----------|
| **1** | Startup/Bootstrap | Ollama unreachable beim Start |
| **2** | RAG | ChromaDB Netzwerk/Dependency-Failure |
| **3** | Debug/EventBus | EventType-Drift |

---

## 1. Startup / Ollama unreachable

### 1.1 Szenario

- **Kontext:** App startet, Ollama ist nicht erreichbar (offline, falscher Port, Timeout).
- **Erwartung:** Graceful Degradation – App startet, RAG/LLM deaktiviert, Nutzer wird informiert.
- **Typische Failure Classes:** `startup_ordering`, `degraded_mode_failure`, `optional_dependency_missing`
- **Runtime Layer:** `startup`

### 1.2 Relevante Input-Signale

| Signal | Quelle | Erwarteter Wert / Bedeutung |
|--------|--------|-----------------------------|
| **subsystem** | Risk Radar, Analytics | Startup/Bootstrap |
| **risk_priority** | QA_RISK_RADAR | P1 (Failure Impact High, Restlücken Medium) |
| **priority_score** | QA_PRIORITY_SCORE | 5 (höchster Score) |
| **naechster_schritt** | QA_PRIORITY_SCORE, Evolution Map | „Init-Reihenfolge Contract“ |
| **heatmap_weak_dimensions** | QA_HEATMAP | Contract_Coverage = 1 |
| **startup_criticality** | runtime_layer, subsystem | true |
| **dependency_cascade_risk** | QA_DEPENDENCY_GRAPH | high (Startup → Provider/Ollama, RAG, Persistenz) |
| **failure_class** | incidents | startup_ordering, degraded_mode_failure |
| **subsystem_risk_score** | analytics | Gewichtet nach Severity (blocker/critical = hoher Score) |
| **incident_count** | index, analytics | Anzahl Startup-Incidents |
| **replay_gap_ratio** | analytics | Anteil ohne Replay |
| **user_visible_impact** | severity | true bei blocker/critical (App startet nicht) |

### 1.3 Priorisierung

| Ebene | Ergebnis |
|-------|----------|
| **Subsystem** | Startup/Bootstrap (höchste Priorität) |
| **Failure Class** | degraded_mode_failure, startup_ordering |
| **Testdomäne** | startup, contract |
| **Gewichtung** | startup_criticality (1.2) + user_visible_impact (1.4) + dependency_cascade_risk (1.1) + priority_score (1.0) |

**Begründung:** Startup blockiert alle Subsysteme. Risk Radar P1, Dependency Graph: Startup → Ollama high. Bei realen Incidents: zusätzlich incident_basiert × 1.5.

### 1.4 Empfohlener Guard-Typ

**startup_degradation_guard** + **contract_guard**

- **startup_degradation_guard:** Init-Reihenfolge, Graceful Degradation bei fehlendem Ollama
- **contract_guard:** Init-Contract für Dependency-Check-Reihenfolge

### 1.5 QA-Sprint-Empfehlung

**Empfohlener Sprint:** „Startup Degradation + Ollama-Init Contract“

| Element | Inhalt |
|---------|--------|
| **Fokus** | Startup/Bootstrap |
| **Ziel** | App startet auch ohne Ollama; klare Degradation; Init-Reihenfolge formal abgesichert |
| **Konkrete Schritte** | 1) test_startup_without_ollama erweitern/verifizieren 2) Contract für Init-Reihenfolge (Ollama-Check vor RAG) 3) Replay für „Ollama unreachable“ falls Incident vorhanden |
| **Testdomänen** | startup, contract |

### 1.6 Warnungen / Eskalationen

| Code | Bedingung | Stufe |
|------|-----------|-------|
| **STARTUP_RISK_ESCALATION** | Mindestens 1 Startup-Incident mit severity ≥ high | Eskalation |
| **REAL_INCIDENT_CLUSTER** | ≥2 Incidents mit failure_class ∈ {startup_ordering, degraded_mode_failure} und runtime_layer=startup | Warnung → Eskalation bei ≥3 |
| **REPLAY_GAP_CRITICAL** | replay_defined_ratio < 0.3 bei Startup-Incidents | Warnung |
| **REGRESSION_BINDING_GAP** | regression_bound_ratio < 0.2 und Startup-Incident mit severity blocker/critical | Eskalation |

---

## 2. RAG / ChromaDB network/dependency failure

### 2.1 Szenario

- **Kontext:** RAG nutzt ChromaDB; ChromaDB nicht erreichbar (Netzwerk, nicht gestartet, Timeout).
- **Erwartung:** RAG degradiert, Event RAG_RETRIEVAL_FAILED, Chat läuft ohne RAG weiter.
- **Typische Failure Classes:** `rag_silent_failure`, `optional_dependency_missing`, `degraded_mode_failure`
- **Runtime Layer:** `service`, `persistence`

### 2.2 Relevante Input-Signale

| Signal | Quelle | Erwarteter Wert / Bedeutung |
|--------|--------|-----------------------------|
| **subsystem** | Risk Radar, Analytics | RAG |
| **risk_priority** | QA_RISK_RADAR | P1 (ChromaDB Netzwerk nicht getestet) |
| **priority_score** | QA_PRIORITY_SCORE | 4 |
| **naechster_schritt** | QA_PRIORITY_SCORE | „Embedding-Service Failure (Ollama Embedding-API)“ |
| **heatmap_weak_dimensions** | QA_HEATMAP | Restrisiko Medium |
| **dependency_cascade_risk** | QA_DEPENDENCY_GRAPH | RAG → ChromaDB, RAG → Provider/Ollama |
| **failure_class** | incidents | rag_silent_failure, optional_dependency_missing |
| **subsystem_risk_score** | analytics | Gewichtet nach Severity |
| **incident_count** | index, analytics | Anzahl RAG-Incidents |
| **replay_gap_ratio** | analytics | Anteil RAG-Incidents ohne Replay |
| **regression_gap_ratio** | analytics | Anteil ohne Regression-Test |
| **user_visible_impact** | severity | true bei rag_silent_failure (Nutzer weiß nicht, dass RAG fehlschlug) |

### 2.3 Priorisierung

| Ebene | Ergebnis |
|-------|----------|
| **Subsystem** | RAG (P1, hoher Incident-Score bei realen Bugs) |
| **Failure Class** | rag_silent_failure, optional_dependency_missing |
| **Testdomäne** | failure_modes |
| **Gewichtung** | incident_frequency (1.5) + replay_gap (1.3) + regression_gap (1.3) + dependency_cascade_risk (1.1) + user_visible_impact (1.4) |

**Begründung:** Risk Radar Top-1 „ChromaDB Netzwerk-Fehler nicht getestet“. Dependency Graph: RAG → ChromaDB. Bei realen Incidents: rag_silent_failure = hohe Nutzerauswirkung.

### 2.4 Empfohlener Guard-Typ

**failure_replay_guard** + **degradation_guard** (implizit in failure_modes)

- **failure_replay_guard:** Replay für ChromaDB unreachable, RAG-Retrieval-Exception
- **Degradation:** Test für „RAG degradiert, Chat läuft weiter“

### 2.5 QA-Sprint-Empfehlung

**Empfohlener Sprint:** „RAG ChromaDB Failure + Degradation Replay“

| Element | Inhalt |
|---------|--------|
| **Fokus** | RAG |
| **Ziel** | ChromaDB-Netzwerk-Fehler abgedeckt; RAG-Fehler sichtbar (Event); Graceful Degradation |
| **Konkrete Schritte** | 1) test_chroma_unreachable (Netzwerk) verifizieren 2) test_rag_retrieval_failure prüfen 3) Replay für „ChromaDB timeout“ falls Incident 4) Event RAG_RETRIEVAL_FAILED in Timeline (debug_false_truth) |
| **Testdomänen** | failure_modes |

### 2.6 Warnungen / Eskalationen

| Code | Bedingung | Stufe |
|------|-----------|-------|
| **DEPENDENCY_FAILURE_CONCENTRATION** | RAG + incident_count ≥ 2 + dependency_cascade | Warnung |
| **REAL_INCIDENT_CLUSTER** | ≥2 Incidents mit failure_class ∈ {rag_silent_failure, optional_dependency_missing} und subsystem=RAG | Warnung → Eskalation bei ≥3 |
| **REPLAY_GAP_CRITICAL** | replay_defined_ratio < 0.3 bei RAG-Incidents | Warnung |
| **REGRESSION_BINDING_GAP** | regression_bound_ratio < 0.2 und RAG-Incident mit severity ≥ high | Eskalation |
| **OBSERVABILITY_GAP** | rag_silent_failure + debug_false_truth (Event nicht in Timeline) | Hinweis |

---

## 3. Debug/EventBus / EventType drift

### 3.1 Szenario

- **Kontext:** Neuer EventType wird emittiert, aber nicht in Registry/Timeline registriert.
- **Erwartung:** Alle EventTypes in Registry; Timeline zeigt korrekte Events.
- **Typische Failure Classes:** `debug_false_truth`, `contract_schema_drift`
- **Runtime Layer:** `observability`

### 3.2 Relevante Input-Signale

| Signal | Quelle | Erwarteter Wert / Bedeutung |
|--------|--------|-----------------------------|
| **subsystem** | Risk Radar, Analytics | Debug/EventBus |
| **risk_priority** | QA_RISK_RADAR | P1 (Drift-Risiko High) |
| **priority_score** | QA_PRIORITY_SCORE | 3 |
| **naechster_schritt** | QA_PRIORITY_SCORE, Evolution Map | „Drift-Sentinel bei neuem EventType (bereits vorhanden)“ |
| **drift_signals** | analytics.warnings (DRIFT_PATTERN), failure_class | true bei debug_false_truth, contract_schema_drift |
| **failure_class** | incidents | debug_false_truth, contract_schema_drift |
| **subsystem_risk_score** | analytics | Gewichtet |
| **incident_count** | index, analytics | Anzahl Debug/EventBus-Incidents |
| **heatmap_weak_dimensions** | QA_HEATMAP | Drift_Governance_Coverage |

### 3.3 Priorisierung

| Ebene | Ergebnis |
|-------|----------|
| **Subsystem** | Debug/EventBus |
| **Failure Class** | debug_false_truth, contract_schema_drift |
| **Testdomäne** | drift_governance, contract |
| **Gewichtung** | drift_signals (1.2) + failure_class_frequency (1.2) + priority_score (1.0) |

**Begründung:** Risk Radar Top-2 „Drift: Neuer EventType ohne Registry/Timeline“. Drift-Muster erfordert event_contract_guard.

### 3.4 Empfohlener Guard-Typ

**event_contract_guard**

- **Trigger:** debug_false_truth, contract_schema_drift, EventType-Registry
- **Ziel:** Neuer EventType → Registry-Check, Timeline-Darstellung

### 3.5 QA-Sprint-Empfehlung

**Empfohlener Sprint:** „EventType Drift Sentinel + Contract“

| Element | Inhalt |
|---------|--------|
| **Fokus** | Debug/EventBus |
| **Ziel** | EventType-Registry aktuell; Timeline zeigt alle relevanten Events; Drift-Sentinel bei neuem EventType |
| **Konkrete Schritte** | 1) EventType-Registry/Meta-Tests prüfen 2) Drift-Sentinel bei neuem EventType (bereits vorhanden) 3) test_debug_view_matches_failure_events, test_event_store_failure 4) Replay für „Event fehlt in Timeline“ falls Incident |
| **Testdomänen** | drift_governance, contract, cross_layer |

### 3.6 Warnungen / Eskalationen

| Code | Bedingung | Stufe |
|------|-----------|-------|
| **DRIFT_PATTERN_DETECTED** | failure_class ∈ {debug_false_truth, contract_schema_drift, metrics_false_success} | Warnung |
| **OBSERVABILITY_GAP** | debug_false_truth + Subsystem Debug/EventBus | Warnung |
| **REAL_INCIDENT_CLUSTER** | ≥2 Incidents mit failure_class = debug_false_truth und subsystem = Debug/EventBus | Warnung → Eskalation bei ≥3 |
| **REGRESSION_BINDING_GAP** | regression_bound_ratio < 0.2 und Drift-Incident | Hinweis |

---

## 4. Zusammenfassung: Konstellation → Autopilot-Output

| Konstellation | recommended_focus_subsystem | recommended_guard_type | recommended_next_sprint | Typische Eskalation |
|---------------|----------------------------|------------------------|-------------------------|---------------------|
| **1. Startup/Ollama** | Startup/Bootstrap | startup_degradation_guard, contract_guard | Startup Degradation + Ollama-Init Contract | STARTUP_RISK_ESCALATION |
| **2. RAG/ChromaDB** | RAG | failure_replay_guard | RAG ChromaDB Failure + Degradation Replay | DEPENDENCY_FAILURE_CONCENTRATION, REGRESSION_BINDING_GAP |
| **3. Debug/EventBus** | Debug/EventBus | event_contract_guard | EventType Drift Sentinel + Contract | DRIFT_PATTERN_DETECTED, OBSERVABILITY_GAP |

---

## 5. Signal-Fluss (vereinfacht)

```
Konstellation 1 (Startup):
  QA_RISK_RADAR (P1) + QA_DEPENDENCY_GRAPH (Startup→Ollama) + [Incidents]
  → startup_criticality=true, user_visible_impact=true
  → recommended_guard_type = startup_degradation_guard
  → Eskalation: STARTUP_RISK_ESCALATION bei severity≥high

Konstellation 2 (RAG):
  QA_RISK_RADAR (P1, ChromaDB) + analytics.replay_gap + [Incidents]
  → dependency_cascade_risk, replay_gap_ratio, regression_gap_ratio
  → recommended_guard_type = failure_replay_guard
  → Eskalation: DEPENDENCY_FAILURE_CONCENTRATION, REGRESSION_BINDING_GAP

Konstellation 3 (Debug/EventBus):
  QA_RISK_RADAR (P1, Drift) + analytics.warnings.DRIFT_PATTERN + [Incidents]
  → drift_signals=true, failure_class=debug_false_truth
  → recommended_guard_type = event_contract_guard
  → Eskalation: DRIFT_PATTERN_DETECTED, OBSERVABILITY_GAP
```

---

*QA Autopilot v2 – Pilotkonstellationen, 15. März 2026.*
