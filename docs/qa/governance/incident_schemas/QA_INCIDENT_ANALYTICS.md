# QA Incident Analytics Engine

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Automatische Analyse von Incidents für QA_RISK_RADAR, QA_HEATMAP, QA_AUTOPILOT, QA_CONTROL_CENTER.

---

## 1. Übersicht

Die Analytics Engine liest `docs/qa/incidents/index.json` und erzeugt `docs/qa/incidents/analytics.json`.

**Erkennt:**
- häufige Fehlerklassen
- riskante Subsysteme
- Drift-Muster
- Replay-Lücken
- Regression-Gaps

---

## 2. Input

| Datei | Beschreibung |
|-------|--------------|
| `docs/qa/incidents/index.json` | Incident Registry (Output von build_registry.py) |

---

## 3. Output-Struktur (analytics.json)

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-15T12:00:00Z",
  "failure_class_distribution": {
    "distribution": [{"key": "ui_state_drift", "count": 5}, ...],
    "total": 12
  },
  "subsystem_distribution": {
    "distribution": [{"key": "Chat", "count": 4}, ...],
    "total": 12
  },
  "runtime_layer_distribution": {
    "distribution": [{"key": "ui", "count": 6}, ...],
    "total": 12
  },
  "clusters": [
    {
      "cluster_id": "C001",
      "failure_class": "ui_state_drift",
      "subsystem": "Chat",
      "runtime_layer": "ui",
      "incident_count": 3,
      "incident_ids": ["INC-...", ...]
    }
  ],
  "risk_signals": {
    "subsystem_risk_score": [{"subsystem": "RAG", "score": 8.0}, ...],
    "failure_class_frequency": [{"failure_class": "async_race", "count": 4}, ...],
    "incident_growth_rate": 2.5
  },
  "qa_coverage": {
    "incident_count": 12,
    "replay_defined_ratio": 0.67,
    "replay_verified_ratio": 0.42,
    "regression_bound_ratio": 0.25,
    "replay_defined_count": 8,
    "replay_verified_count": 5,
    "regression_bound_count": 3
  },
  "autopilot_hints": {
    "recommended_focus_subsystem": "RAG",
    "recommended_focus_failure_class": "async_race",
    "recommended_sprint_target": 4,
    "catalog_candidates_count": 4,
    "autopilot_eligible_count": 2
  },
  "warnings": [
    {
      "code": "REGRESSION_GAP",
      "message": "Regression-Abdeckung niedrig: 25% (Schwelle: 30%)",
      "metric": "regression_bound_ratio",
      "value": 0.25
    }
  ]
}
```

---

## 4. Analysen

### 4.1 Top Distributions

- **Top Failure Classes:** Sortiert nach Häufigkeit
- **Top Subsystems:** Sortiert nach Häufigkeit
- **Top Runtime Layers:** Sortiert nach Häufigkeit

### 4.2 Clustering

Cluster nach `failure_class × subsystem × runtime_layer`:

| Feld | Beschreibung |
|------|--------------|
| cluster_id | Eindeutige ID (C001, C002, …) |
| failure_class | Fehlerklasse |
| subsystem | Subsystem |
| runtime_layer | Laufzeit-Schicht |
| incident_count | Anzahl Incidents im Cluster |
| incident_ids | Liste der Incident-IDs |

### 4.3 Risk Analysis

| Signal | Beschreibung |
|--------|--------------|
| **subsystem_risk_score** | Gewichtete Summe nach Severity (blocker=5, critical=4, high=3, medium=2, low=1) |
| **failure_class_frequency** | Häufigkeit pro Fehlerklasse |
| **incident_growth_rate** | Incidents pro Monat (aus detected_at) |

### 4.4 QA Coverage Analysis

| Metrik | Beschreibung |
|--------|--------------|
| incident_count | Gesamtanzahl Incidents |
| replay_defined_ratio | Anteil mit Replay definiert |
| replay_verified_ratio | Anteil mit Replay verifiziert |
| regression_bound_ratio | Anteil mit Regression-Test |

### 4.5 Autopilot Hints

| Hint | Beschreibung |
|------|--------------|
| recommended_focus_subsystem | Subsystem mit meisten offenen Incidents |
| recommended_focus_failure_class | Fehlerklasse mit meisten catalog_candidates |
| recommended_sprint_target | Anzahl catalog_candidates (Replay ohne Test) |

---

## 5. Warnungsklassen

| Code | Bedeutung |
|------|-----------|
| **REPLAY_GAP** | replay_defined_ratio < 50% |
| **REGRESSION_GAP** | regression_bound_ratio < 30% |
| **FAILURE_CLUSTER** | failure_class mit ≥ 2 Incidents |
| **SUBSYSTEM_RISK** | Subsystem mit ≥ 2 Incidents (severity blocker/critical/high) |
| **DRIFT_PATTERN** | Incidents mit contract_schema_drift, metrics_false_success, debug_false_truth |

---

## 6. Integration

Die Analytics Engine liefert Input für:

- **QA_RISK_RADAR:** subsystem_risk_score, risk_signals
- **QA_HEATMAP:** failure_class_distribution, runtime_layer_distribution
- **QA_AUTOPILOT:** autopilot_hints
- **QA_CONTROL_CENTER:** qa_coverage, warnings

---

## 7. Aufruf

```bash
python scripts/qa/incidents/analyze_incidents.py
python scripts/qa/incidents/analyze_incidents.py -i docs/qa/incidents/index.json -o docs/qa/incidents/analytics.json
```
