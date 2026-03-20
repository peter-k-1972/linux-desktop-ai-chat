# QA Autopilot v3 – Architekturbegründung

**Version:** 3.0  
**Erstellt:** 2026-03-15

---

## 1. Architekturbegründung

### Ziel

Autopilot v3 erweitert die QA-Governance um **systematische Erkennung fehlender Testabsicherung**. Während v2 Prioritäten und Risiken empfiehlt, identifiziert v3 konkrete Lücken:

- **Test-Gaps:** Fehlende Replay-, Regression- oder Contract-Tests
- **Guard-Gaps:** Fehlende Guards (failure_replay, event_contract, startup_degradation)
- **Translation-Gaps:** Incidents nicht an Replay/Regression gebunden; Pilot-Empfehlungen nicht im Backlog

### Warum eigener Baustein?

- **Trennung der Verantwortlichkeiten:** v2 = Empfehlung, v3 = Lückenerkennung
- **Wiederverwendung:** Nutzt `run_feedback_projections` aus dem Feedback-Loop – keine Duplikation der Normalisierungslogik
- **Erweiterbarkeit:** Neue Gap-Typen und Regeln in `autopilot_v3/rules.py` ohne Änderung am Feedback-Loop

### Paketstruktur

```
scripts/qa/autopilot_v3/
├── __init__.py      # Public API
├── models.py        # TestGapFinding, GuardGapFinding, TranslationGapFinding, RecommendedTestBacklogItem
├── loader.py        # Wrapper um load_feedback_inputs_from_paths
├── rules.py         # Gap-Erkennungsregeln
├── projections.py  # Orchestrierung: run_feedback_projections + apply_gap_rules
└── traces.py        # Trace- und JSON-Serialisierung
```

---

## 2. Annahmen

| Annahme | Beschreibung |
|---------|--------------|
| **Inputs** | incidents/index.json, analytics.json, QA_AUTOPILOT_V2.json, QA_CONTROL_CENTER.json, QA_PRIORITY_SCORE.json |
| **Feedback-Loop** | `run_feedback_projections` liefert SubsystemFeedbackState und FailureClassFeedbackState – diese werden für Gap-Regeln verwendet |
| **Pilotkonstellationen** | 1: Startup/Ollama, 2: RAG/ChromaDB, 3: Debug/EventBus – explizit in rules.py berücksichtigt |
| **Schreibverbot** | Autopilot v3 schreibt nur QA_AUTOPILOT_V3.json und autopilot_v3_trace.json – keine Tests, Incidents, Replay-Daten, Regression Catalog, Produktcode |
| **Determinismus** | `--timestamp` für reproduzierbare Ausgabe; sort_keys=True bei JSON |

---

## 3. Bekannte Integrationspunkte

| Integrationspunkt | Beschreibung |
|-------------------|--------------|
| **Feedback-Loop** | `run_feedback_projections` – liefert per_subsystem_results, per_failure_class_results, global_warnings, escalations |
| **QA_AUTOPILOT_V2** | Wird als Input für recommended_focus_subsystem, pilot_constellation_matched genutzt |
| **QA_PRIORITY_SCORE** | Top-3 Prioritäten für pilot_not_sufficiently_translated |
| **update_control_center.py** | Kann zukünftig QA_AUTOPILOT_V3.json als zusätzliche Quelle für Governance-Alerts nutzen |
| **run_feedback_loop.py** | Optional: Autopilot v3 in Pipeline einbinden |

---

## 4. Regelübersicht

### Test Gap

| Bedingung | Gap-Typ | Priorität |
|-----------|---------|-----------|
| incident_count ≥ 2 + replay_gap ≥ 50% | missing_replay_test | high wenn ≥3 Incidents |
| incident_count ≥ 2 + regression_gap ≥ 30% | missing_regression_test | high wenn ≥3 Incidents |
| drift_failure_class + ≥2 Incidents | missing_contract_test | high |

### Guard Gap

| Bedingung | Guard-Typ |
|-----------|-----------|
| Network-failure-Cluster (≥2) | failure_replay_guard |
| Event/contract drift (≥1) | event_contract_guard |
| Startup degradation (≥1) | startup_degradation_guard |

### Translation Gap

| Bedingung | Gap-Typ |
|-----------|---------|
| replay_status missing | incident_not_bound_to_replay |
| binding_status != catalog_bound | incident_not_bound_to_regression |
| Pilot aktiv, Fokus nicht in Top-3 | pilot_not_sufficiently_translated |
