# QA Autopilot v2 – Architekturmodell

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf  
**Zweck:** Erweiterung des QA Autopilots um Incident-Daten und Incident-Analytics für priorisierte QA-Sprint-Empfehlungen.

---

## 1. Übersicht

QA Autopilot v2 kombiniert **statische QA-Artefakte** mit **Incident Replay Daten** und **Incident Analytics**, um:

- priorisierte QA-Sprint-Empfehlungen abzuleiten
- reale Fehlersignaturen höher zu gewichten als theoretische Testlücken
- Replay-Gaps, Regression-Gaps und Drift-Muster zu erkennen
- Governance-Signale und Eskalationen zu erzeugen

**Der Autopilot handelt NICHT autonom.** Er empfiehlt, priorisiert, warnt und fokussiert – er schließt keine Incidents, setzt keine Severity endgültig fest und generiert keine Tests.

---

## 2. Input-Schicht

### 2.1 Input-Modell (konsolidiert)

Der Autopilot führt Daten aus folgenden Quellen in ein einheitliches **Input-Modell** zusammen:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     QA AUTOPILOT v2 – INPUT-MODELL                       │
├─────────────────────────────────────────────────────────────────────────┤
│  A) Statische QA-Artefakte                                               │
│     • QA_RISK_RADAR.md          → subsystem_priorities, risk_dimensions  │
│     • QA_HEATMAP.json           → coverage_per_subsystem, weak_dimensions │
│     • QA_PRIORITY_SCORE.json    → scores, naechster_schritt, begruendung  │
│     • QA_DEPENDENCY_GRAPH.md    → kaskaden, top_qa_hebel                  │
│     • QA_STABILITY_INDEX.json   → index, belastungsfaktoren               │
│     • QA_CONTROL_CENTER.json    → offene_incidents, metrics               │
├─────────────────────────────────────────────────────────────────────────┤
│  B) Incident Replay Daten                                                 │
│     • incidents/index.json      → incidents[], clusters, metrics         │
│     • incidents/analytics.json  → risk_signals, qa_coverage, warnings    │
├─────────────────────────────────────────────────────────────────────────┤
│  C) Optionale spätere Quellen (Erweiterung)                               │
│     • flaky_test_signals        → test_id, flakiness_rate                 │
│     • weak_test_signals         → test_id, coverage_gap                  │
│     • anomaly_detection_signals → subsystem, anomaly_type                 │
│     • self_healing_suggestions  → suggestion_type, target                 │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Normalisiertes Input-Schema (konzeptionell)

| Feld | Quelle(n) | Typ | Beschreibung |
|------|-----------|-----|--------------|
| **subsystem** | Risk Radar, Heatmap, Priority Score, Analytics | string | Subsystem-Name |
| **risk_priority** | Risk Radar, Priority Score | P1\|P2\|P3 | Theoretische Priorität |
| **priority_score** | QA_PRIORITY_SCORE | number | Numerischer Score |
| **heatmap_weak_dimensions** | QA_HEATMAP | string[] | Dimensionen mit Wert 1 |
| **naechster_schritt** | Priority Score, Evolution Map | string | Empfohlener QA-Schritt |
| **subsystem_risk_score** | analytics.json | number | Gewichteter Incident-Risk-Score |
| **failure_class_frequency** | analytics.json | {fc: count} | Häufigkeit pro Fehlerklasse |
| **incident_count** | index.json, analytics.json | number | Anzahl Incidents pro Subsystem |
| **replay_defined_ratio** | analytics.json | 0..1 | Anteil mit Replay definiert |
| **regression_bound_ratio** | analytics.json | 0..1 | Anteil mit Regression-Test |
| **replay_gap_ratio** | abgeleitet | 1 - replay_defined_ratio | Replay-Lücke |
| **regression_gap_ratio** | abgeleitet | 1 - regression_bound_ratio | Regression-Lücke |
| **dependency_cascade_risk** | QA_DEPENDENCY_GRAPH | high\|medium\|low | Kaskadenwirkung |
| **drift_signals** | analytics.json, failure_class | boolean | contract_schema_drift, debug_false_truth, metrics_false_success |
| **startup_criticality** | runtime_layer=startup, subsystem | boolean | Startup/Bootstrap betroffen |
| **user_visible_impact** | severity blocker/critical/high | boolean | Hohe Nutzerauswirkung |
| **recurrence_of_real_incidents** | incident_count, incident_growth_rate | number | Reale Wiederholungsrate |

### 2.3 Quellen-Mapping

| Input-Signal | Primäre Quelle | Fallback |
|--------------|----------------|----------|
| subsystem_risk_score | analytics.risk_signals.subsystem_risk_score | – |
| failure_class_frequency | analytics.risk_signals.failure_class_frequency | – |
| replay_gap_ratio | 1 - analytics.qa_coverage.replay_defined_ratio | – |
| regression_gap_ratio | 1 - analytics.qa_coverage.regression_bound_ratio | – |
| incident_clusters | analytics.clusters | index.clusters |
| dependency_cascade_risk | QA_DEPENDENCY_GRAPH | – |
| drift_signals | analytics.warnings (DRIFT_PATTERN) | failure_class ∈ drift_classes |
| startup_criticality | runtime_layer=startup, subsystem=Startup/Bootstrap | – |

---

## 3. Bewertungslogik

### 3.1 Grundprinzip

**Reale Incidents wiegen stärker als theoretische Risiken.**

| Faktorentyp | Gewichtung | Begründung |
|-------------|------------|------------|
| **Incident-basiert** | Hoch (Faktor 1.5–2.0) | Echter Bug, reproduzierbar, Nutzer betroffen |
| **Risiko-basiert** | Mittel (Faktor 1.0) | Theoretische Lücke aus Risk Radar/Heatmap |
| **Unterstützend** | Niedrig (Faktor 0.5) | Zusatzsignal, z.B. Stability Index |

### 3.2 Bewertungsfaktoren und Gewichtung

| Faktor | Gewicht | Quelle | Beschreibung |
|--------|---------|--------|--------------|
| **subsystem_risk_score** | 1.5 | analytics | Gewichteter Incident-Score pro Subsystem |
| **incident_frequency** | 1.5 | analytics, index | Anzahl Incidents pro Subsystem |
| **failure_class_frequency** | 1.2 | analytics | Häufung einer Fehlerklasse |
| **replay_gap_ratio** | 1.3 | analytics | Anteil Incidents ohne Replay |
| **regression_gap_ratio** | 1.3 | analytics | Anteil ohne Regression-Test |
| **dependency_cascade_risk** | 1.1 | QA_DEPENDENCY_GRAPH | Kaskadenwirkung |
| **drift_signals** | 1.2 | analytics, failure_class | Drift-Muster erkannt |
| **startup_criticality** | 1.2 | runtime_layer, subsystem | Startup betroffen |
| **user_visible_impact** | 1.4 | severity | blocker/critical/high |
| **recurrence_of_real_incidents** | 1.3 | incident_growth_rate | Wiederholungsrate |
| **priority_score** | 1.0 | QA_PRIORITY_SCORE | Theoretische Priorität |
| **heatmap_weak_spots** | 0.8 | QA_HEATMAP | Abdeckungslücken |
| **stability_belastungsfaktor** | 0.5 | QA_STABILITY_INDEX | Zusatzsignal |

### 3.3 Konsolidierter Score (Formel, konzeptionell)

```
Score(subsystem) =
  Σ (incident_basierte_faktoren × 1.5) +
  Σ (risiko_basierte_faktoren × 1.0) +
  Σ (unterstuetzende_faktoren × 0.5)
```

**Incident-basiert:** subsystem_risk_score, incident_frequency, replay_gap, regression_gap, user_visible_impact, recurrence  
**Risiko-basiert:** priority_score, failure_class_frequency, dependency_cascade_risk, drift_signals, startup_criticality  
**Unterstützend:** heatmap_weak_spots, stability_belastungsfaktor  

---

## 4. Priorisierungslogik

### 4.1 Priorisierungsebenen

Der Autopilot erzeugt mindestens diese Ebenen:

| Ebene | Feld | Beschreibung |
|-------|------|---------------|
| **Subsystem** | recommended_focus_subsystem | Höchster konsolidierter Score |
| **Failure Class** | recommended_focus_failure_class | Häufigste mit Replay-Gap oder Regression-Gap |
| **Testdomäne** | recommended_test_domain | failure_modes, contract, async_behavior, cross_layer, startup, chaos, integration |
| **Guard-Typ** | recommended_guard_type | Siehe 4.2 |
| **Sprint-Fokus** | recommended_next_sprint | Kombination aus Subsystem + Guard-Typ |

### 4.2 Guard-Typen

| Guard-Typ | Trigger | Typische Testdomäne |
|-----------|---------|---------------------|
| **contract_guard** | contract_schema_drift, Contract_Coverage weak | contract |
| **failure_replay_guard** | Replay-Gap, failure_class häufig | failure_modes |
| **cross_layer_guard** | Cross-Layer-Incidents, Cross_Layer_Coverage weak | cross_layer |
| **chaos_guard** | intermittent, async_race, provider_unreachable | chaos |
| **startup_degradation_guard** | startup_ordering, degraded_mode_failure, runtime_layer=startup | startup |
| **event_contract_guard** | debug_false_truth, EventType-Drift, Drift_Governance weak | drift_governance |

### 4.3 Priorisierungsreihenfolge

1. **Incident-Signale prüfen:** Gibt es reale Incidents mit hoher Severity?
2. **Replay-Gap prüfen:** Welche Subsysteme/Failure-Classes haben viele Incidents ohne Replay?
3. **Regression-Gap prüfen:** Wo fehlen Regression-Tests?
4. **Risiko-Signale:** Priority Score, Heatmap Weak Spots
5. **Tiebreaker:** Dependency Cascade, Startup-Criticality, Drift-Signals

---

## 5. Sprint-Empfehlungslogik

### 5.1 Allgemeine Regeln

| Bedingung | Empfehlung |
|-----------|------------|
| **Viele Startup-Incidents** (runtime_layer=startup, failure_class ∈ {startup_ordering, degraded_mode_failure}) | Sprint-Fokus = Startup/Bootstrap, Guard-Typ = startup_degradation_guard oder contract_guard |
| **Hohe Benutzerauswirkung** (severity blocker/critical) + **replay_gap hoch** | Sprint-Fokus = betroffenes Subsystem, Guard-Typ = failure_replay_guard |
| **EventType-Drift mehrfach** (failure_class = debug_false_truth, subsystem = Debug/EventBus) | Sprint-Fokus = Debug/EventBus, Guard-Typ = event_contract_guard |
| **RAG/Chroma Incidents** + **dependency_risk hoch** + **replay_binding gering** | Sprint-Fokus = RAG, Guard-Typ = failure_replay_guard + degradation_guard |
| **contract_schema_drift** oder **metrics_false_success** | Sprint-Fokus = betroffenes Subsystem, Guard-Typ = contract_guard |
| **async_race** häufig + **Cross_Layer weak** | Sprint-Fokus = Subsystem mit meisten async_race, Guard-Typ = cross_layer_guard |
| **catalog_candidates > 0** (Replay ohne Test) | recommended_sprint_target = catalog_candidates_count, Fokus auf diese Incidents |

### 5.2 Regel-Priorität

1. **Eskalationen** (siehe Abschnitt 6) überschreiben normale Empfehlungen
2. **REAL_INCIDENT_CLUSTER** → Subsystem/Failure-Class des Clusters
3. **REPLAY_GAP_CRITICAL** → failure_replay_guard priorisieren
4. **REGRESSION_BINDING_GAP** → Regression-Tests priorisieren
5. **DRIFT_PATTERN_DETECTED** → event_contract_guard oder contract_guard
6. **STARTUP_RISK_ESCALATION** → startup_degradation_guard
7. Fallback: Priority Score + Heatmap (wie v1)

---

## 6. Warning- und Escalation-Logik

### 6.1 Warnungsklassen

| Code | Bedeutung | Trigger | Priorität |
|------|------------|---------|-----------|
| **REAL_INCIDENT_CLUSTER** | Cluster von Incidents (≥2) gleicher failure_class/subsystem | analytics.clusters mit incident_count ≥ 2 | Hoch |
| **REPLAY_GAP_CRITICAL** | Replay-Abdeckung kritisch niedrig | replay_defined_ratio < 0.3 | Hoch |
| **REGRESSION_BINDING_GAP** | Regression-Tests fehlen massiv | regression_bound_ratio < 0.2 | Hoch |
| **DRIFT_PATTERN_DETECTED** | Drift-Muster (contract, metrics, debug) | DRIFT_PATTERN aus analytics | Mittel |
| **STARTUP_RISK_ESCALATION** | Startup-Incidents mit hoher Severity | runtime_layer=startup + severity ≥ high | Hoch |
| **OBSERVABILITY_GAP** | Debug/EventBus Incidents, Timeline nicht sichtbar | failure_class = debug_false_truth | Mittel |
| **DEPENDENCY_FAILURE_CONCENTRATION** | Viele Incidents in dependency-kritischem Subsystem | RAG, Provider/Ollama, Startup + incident_count ≥ 2 | Mittel |

### 6.2 Hinweis vs. Eskalation

| Stufe | Kriterium | Aktion |
|-------|-----------|--------|
| **Hinweis** | Warnung erfüllt, aber kein kritisches Signal | In warnings[], confidence normal |
| **Eskalation** | Warnung + (severity blocker/critical ODER incident_count ≥ 3 ODER replay_gap < 0.2) | In escalations[], confidence high, priorisiert |

### 6.3 Eskalations-Schwellen

| Eskalation | Bedingung |
|------------|-----------|
| **REPLAY_GAP_CRITICAL** → Eskalation | replay_defined_ratio < 0.2 ODER (replay_defined_ratio < 0.3 UND open_incidents ≥ 3) |
| **REGRESSION_BINDING_GAP** → Eskalation | regression_bound_ratio < 0.15 ODER (regression_bound_ratio < 0.2 UND severity blocker/critical vorhanden) |
| **STARTUP_RISK_ESCALATION** | Mindestens 1 Startup-Incident mit severity ≥ high |
| **REAL_INCIDENT_CLUSTER** → Eskalation | incident_count ≥ 3 im Cluster |

---

## 7. Output-Artefaktstruktur

### 7.1 Datei

**Empfehlung:** `docs/qa/QA_AUTOPILOT_V2.json` (neues Artefakt, QA_AUTOPILOT.json bleibt für v1)

**Alternative:** `docs/qa/QA_AUTOPILOT.json` erweitern mit `version: 2` und neuen Feldern.

### 7.2 Output-Schema (vollständig)

```json
{
  "schema_version": "2.0",
  "generated_at": "2026-03-15T12:00:00Z",
  "overall_recommendation": "Kurze Zusammenfassung (1–2 Sätze)",

  "recommended_focus_subsystem": "RAG",
  "recommended_focus_failure_class": "rag_silent_failure",
  "recommended_test_domain": "failure_modes",
  "recommended_guard_type": "failure_replay_guard",
  "recommended_next_sprint": "RAG Failure Replay + Chroma Degradation",

  "top_risk_signals": [
    {
      "type": "incident_based",
      "subsystem": "RAG",
      "signal": "subsystem_risk_score",
      "value": 8.0,
      "source": "analytics.risk_signals"
    }
  ],
  "top_incident_signals": [
    {
      "incident_id": "INC-20260315-002",
      "subsystem": "RAG",
      "failure_class": "async_race",
      "severity": "high",
      "relevance": "catalog_candidate"
    }
  ],
  "warnings": [
    {
      "code": "REGRESSION_BINDING_GAP",
      "message": "...",
      "priority": "high",
      "source_ref": "analytics.warnings"
    }
  ],
  "escalations": [
    {
      "code": "REPLAY_GAP_CRITICAL",
      "message": "...",
      "recommended_action": "failure_replay_guard für RAG priorisieren"
    }
  ],

  "supporting_evidence": {
    "risk_radar_refs": ["RAG: P1", "Startup/Bootstrap: P1"],
    "incident_cluster_refs": ["C001", "C002"],
    "replay_gap_refs": ["analytics.qa_coverage.replay_defined_ratio"],
    "dependency_graph_refs": ["RAG → ChromaDB cascade"]
  },

  "confidence": 0.85,
  "reasoning_summary": "Empfehlung basiert primär auf 3 RAG-Incidents (2x rag_silent_failure, 1x async_race), replay_gap 67%, regression_gap 100%. Risk Radar P1 bestätigt. Keine Startup-Eskalation.",
  "recommendation_basis": "incident_dominant",

  "input_sources_used": [
    "QA_PRIORITY_SCORE.json",
    "QA_HEATMAP.json",
    "incidents/index.json",
    "incidents/analytics.json"
  ]
}
```

### 7.3 Feldliste (minimal)

| Feld | Pflicht | Beschreibung |
|------|---------|--------------|
| generated_at | ja | Zeitstempel |
| overall_recommendation | ja | 1–2 Sätze |
| recommended_focus_subsystem | ja | Top-Subsystem |
| recommended_focus_failure_class | nein | Top Failure Class |
| recommended_test_domain | ja | failure_modes, contract, … |
| recommended_guard_type | ja | contract_guard, failure_replay_guard, … |
| recommended_next_sprint | ja | Konkrete Sprint-Beschreibung |
| top_risk_signals | ja | Array, min. 1 |
| top_incident_signals | nein | Relevante Incidents |
| warnings | ja | Array (kann leer sein) |
| escalations | ja | Array (kann leer sein) |
| supporting_evidence | ja | Objekt mit Refs |
| confidence | ja | 0..1 |
| reasoning_summary | ja | Begründung |
| recommendation_basis | ja | incident_dominant \| risk_dominant \| balanced |

---

## 8. Traceability

### 8.1 Input-Signal-Referenzierung

Jede Empfehlung muss im Output referenzierbar sein:

| Output-Element | Referenzierte Inputs |
|----------------|---------------------|
| recommended_focus_subsystem | analytics.risk_signals.subsystem_risk_score, index.incidents[].subsystem |
| recommended_focus_failure_class | analytics.risk_signals.failure_class_frequency, analytics.autopilot_hints |
| recommended_guard_type | analytics.warnings, failure_class, runtime_layer |
| top_risk_signals | Explizit source + value |
| supporting_evidence | risk_radar_refs, incident_cluster_refs, replay_gap_refs, dependency_graph_refs |

### 8.2 reasoning_summary Aufbau

1. **Primärer Treiber:** Was hat die Empfehlung ausgelöst? (Incident-Cluster, Replay-Gap, …)
2. **Quantitative Stützung:** Zahlen (Incident-Count, Ratios, Scores)
3. **Sekundäre Signale:** Risk Radar, Heatmap, Dependency
4. **Ausschlüsse:** Was wurde geprüft und verworfen? (z.B. „Keine Startup-Eskalation“)

### 8.3 recommendation_basis

| Wert | Bedeutung |
|------|-----------|
| **incident_dominant** | Empfehlung basiert primär auf Incident-Daten (subsystem_risk_score, incident_clusters, replay_gap) |
| **risk_dominant** | Empfehlung basiert primär auf Risk Radar, Priority Score, Heatmap |
| **balanced** | Beide Quellen gleichgewichtet |

**Erkennung:** Wenn `top_risk_signals` überwiegend `type: "incident_based"` → incident_dominant. Wenn überwiegend `type: "risk_based"` → risk_dominant.

---

## 9. Guardrails

### 9.1 Der Autopilot DARF NICHT

- selbstständig Incidents schließen
- Severity final überschreiben
- Regression Catalog Einträge finalisieren
- Tests automatisch schreiben
- Produktcode modifizieren
- CI-Pipeline ändern
- Bindings.json oder incident.yaml schreiben

### 9.2 Der Autopilot SOLL

- empfehlen (Sprint, Subsystem, Guard-Typ)
- priorisieren (Sortierung, Top-N)
- begründen (reasoning_summary, supporting_evidence)
- sichtbar machen (warnings, escalations)
- Eskalationen markieren (escalations[] mit recommended_action)

---

## 10. Offene Architekturentscheidungen

| Entscheidung | Optionen | Empfehlung |
|--------------|----------|------------|
| **Output-Datei** | QA_AUTOPILOT_V2.json neu vs. QA_AUTOPILOT.json erweitern | Neues QA_AUTOPILOT_V2.json für klare Versionierung |
| **Gewichtungsfaktoren** | Konfigurierbar vs. fest | Konfigurierbar in Config-Datei (z.B. autopilot_weights.json) |
| **Integration mit v1** | Ersetzen vs. Parallel | Parallel: v1 bleibt, v2 ergänzt. Später v1 optional ausphasen |
| **Flaky/Weak Test Signals** | Zeitpunkt der Integration | Phase 2, wenn Signale verfügbar |
| **Anomaly Detection** | Integration | Phase 2, wenn QA_ANOMALY_DETECTION strukturiert |
| **Confidence-Berechnung** | Formel | Noch offen: z.B. (incident_count / max_expected) × source_quality |
| **Backward-Kompatibilität** | QA_AUTOPILOT.json v1 | Unverändert lassen, v2 als Add-on |

---

## 11. Abhängigkeiten

| Komponente | Voraussetzung |
|------------|---------------|
| build_registry.py | Muss vor Autopilot v2 laufen (index.json) |
| analyze_incidents.py | Muss vor Autopilot v2 laufen (analytics.json) |
| QA_PRIORITY_SCORE.json | Von generate_qa_priority_score.py |
| QA_HEATMAP.json | Von generate_qa_heatmap.py |
| QA_DEPENDENCY_GRAPH.md | Manuell/Generator |

---

## 12. Pilotkonstellationen

Konkrete Abbildung von drei Pilot-Szenarien auf Input-Signale, Priorisierung, Guard-Typen und Sprint-Empfehlungen:

→ **[QA_AUTOPILOT_V2_PILOT_CONSTELLATIONS.md](QA_AUTOPILOT_V2_PILOT_CONSTELLATIONS.md)**

| Konstellation | Subsystem | Guard-Typ |
|---------------|-----------|-----------|
| Startup / Ollama unreachable | Startup/Bootstrap | startup_degradation_guard, contract_guard |
| RAG / ChromaDB network failure | RAG | failure_replay_guard |
| Debug/EventBus / EventType drift | Debug/EventBus | event_contract_guard |

---

*QA Autopilot v2 – Architekturmodell, 15. März 2026.*
