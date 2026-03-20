# QA Incident Replay – Validierungsstandard

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Technischer Validierungsstandard für incident.yaml, replay.yaml, bindings.json.

---

## 1. Übersicht

Dieses Dokument definiert:

- Schema-Definitionen (Incident, Replay, Bindings)
- Pflichtfelder
- Allowed Values
- Lifecycle-Validierungsregeln (Statusübergänge)
- Konsistenzregeln zwischen Dateien
- Fehlerklassen der Validierung

---

## 2. Schema-Definitionen

### 2.1 Incident (incident.yaml)

**Schema-Datei:** `docs/qa/incidents/_schema/incident.schema.yaml`

**Pflichtfelder (Top-Level):**

| Sektion      | Pflichtfelder |
|-------------|----------------|
| schema_version | `"1.0"` |
| identity    | id, title, created, updated, source |
| detection   | when, how |
| environment | runtime_layer |
| classification | failure_class, subsystem, severity, priority |
| behavior    | description, expected, actual, repro_steps, reproducibility |
| qa          | status |

**Zusätzliche Pflichtfelder je Status:**

| Status | Zusätzliche Pflichtfelder |
|--------|---------------------------|
| duplicate | qa.duplicate_of (INC-xxx) |
| invalid, archived | qa.status_reason oder notes.md |
| closed | resolution.fix, resolution.verified |
| triaged | classification.severity, classification.priority |
| classified | classification.failure_class, classification.subsystem |

### 2.2 Replay (replay.yaml)

**Schema-Datei:** `docs/qa/incidents/_schema/replay.schema.yaml`

**Pflichtfelder (Top-Level):**

| Sektion | Pflichtfelder |
|---------|----------------|
| schema_version | `"1.0"` |
| identity | id, incident_id, title, created, updated |
| replay_type | type |
| preconditions | system |
| execution | steps |
| assertion_contract | success, failure |
| determinism | level, isolated |
| mapping | test_domains, risk_axes |
| verification | status |

### 2.3 Bindings (bindings.json)

**Schema-Datei:** `docs/qa/incidents/_schema/bindings.schema.json`

**Pflichtfelder (Top-Level):**

| Sektion | Pflichtfelder |
|---------|----------------|
| schema_version | `"1.0"` |
| identity | incident_id |
| regression_catalog | failure_class |
| risk_radar | subsystem |
| heatmap | dimensions |
| status | binding_status, updated |
| meta | created, updated |

---

## 3. Allowed Values

### 3.1 incident.yaml

| Feld | Erlaubte Werte |
|------|----------------|
| **qa.status** | new, triaged, classified, replay_defined, replay_verified, bound_to_regression, closed, invalid, duplicate, archived |
| **classification.severity** | blocker, critical, high, medium, low, cosmetic |
| **classification.priority** | P0, P1, P2, P3 |
| **classification.failure_class** | ui_state_drift, async_race, late_signal_use_after_destroy, request_context_loss, rag_silent_failure, debug_false_truth, startup_ordering, degraded_mode_failure, contract_schema_drift, metrics_false_success, tool_failure_visibility, optional_dependency_missing |
| **behavior.reproducibility** | always, intermittent, once, unknown, requires_specific_state |
| **environment.runtime_layer** | ui, service, persistence, integration, startup, observability, cross_layer, other |
| **identity.source** | production, staging, development, manual, audit, regression, other |
| **detection.how** | manual, test_failure, ci_failure, monitoring, audit, regression, other |

### 3.2 replay.yaml

| Feld | Erlaubte Werte |
|------|----------------|
| **verification.status** | draft, validated, test_bound, guarded, obsolete |
| **replay_type.type** | startup_dependency_failure, provider_unreachable, fault_injection, event_contract_drift, state_sequence, cross_layer, async_race, hybrid |
| **determinism.level** | fully_deterministic, deterministic_with_mocks, timing_sensitive, intermittent, environment_dependent |
| **execution.steps[].actor** | app, user, system, injector |
| **execution.ordering** | sequential, parallel_allowed, timing_sensitive |

### 3.3 bindings.json

| Feld | Erlaubte Werte |
|------|----------------|
| **status.binding_status** | proposed, validated, catalog_bound, rejected, archived |
| **regression_catalog.failure_class** | (identisch zu incident.yaml) |
| **risk_radar.subsystem** | Chat, Agentensystem, Prompt-System, RAG, Debug/EventBus, Metrics, Startup/Bootstrap, Tools, Provider/Ollama, Persistenz/SQLite |
| **risk_radar.priority** | P0, P1, P2, P3 |
| **heatmap.dimensions** | Failure_Coverage, Contract_Coverage, Async_Coverage, Cross_Layer_Coverage, Drift_Governance_Coverage, Restrisiko |

---

## 4. Lifecycle-Validierungsregeln (Statusübergänge)

### 4.1 Erlaubte Incident-Statusübergänge

| Von | Nach |
|-----|------|
| new | triaged, invalid, duplicate |
| triaged | classified, invalid, duplicate |
| classified | replay_defined, invalid, duplicate, archived |
| replay_defined | replay_verified, invalid, duplicate, archived |
| replay_verified | bound_to_regression, invalid, duplicate, archived |
| bound_to_regression | closed, archived |
| closed | archived |
| invalid | archived |
| duplicate | archived |
| archived | – (Endzustand) |

### 4.2 Ungültige Übergänge (Beispiele)

- new → classified (Überspringen von triaged)
- triaged → replay_defined (Überspringen von classified)
- classified → replay_verified (ohne replay_defined)
- replay_defined → bound_to_regression (ohne replay_verified)
- new → closed (direkt)
- closed → new (Rückwärts ohne Korrektur)

**Hinweis:** Die Validierung von Statusübergängen erfordert Kenntnis des vorherigen Status (z.B. via `qa.status_history` oder Git-Diff). Der Validator prüft bei Vorhandensein von `qa.status_history` die Übergänge.

### 4.3 Erlaubte Replay-Statusübergänge

| Von | Nach |
|-----|------|
| draft | validated, obsolete |
| validated | test_bound, obsolete |
| test_bound | guarded, obsolete |
| guarded | obsolete |
| obsolete | – (Endzustand) |

---

## 5. Konsistenzregeln zwischen Dateien

### 5.1 incident.yaml ↔ replay.yaml

| Regel | Beschreibung |
|-------|--------------|
| **C1** | incident_id muss identisch sein: incident.yaml identity.id = replay.yaml identity.incident_id |
| **C2** | replay_id muss übereinstimmen: incident.yaml qa.replay_id = replay.yaml identity.id |
| **C3** | Status replay_defined erfordert: replay.yaml existiert und ist valide |
| **C4** | Status replay_verified erfordert: replay.yaml verification.status = validated |
| **C5** | failure_class muss übereinstimmen: incident classification.failure_class = replay mapping.failure_class (falls gesetzt) |

### 5.2 incident.yaml ↔ bindings.json

| Regel | Beschreibung |
|-------|--------------|
| **C6** | incident_id muss identisch sein: incident identity.id = bindings identity.incident_id |
| **C7** | Status bound_to_regression erfordert: bindings.json existiert |
| **C8** | Status bound_to_regression erfordert: bindings.json regression_catalog.regression_test gesetzt |
| **C9** | failure_class muss übereinstimmen: incident classification.failure_class = bindings regression_catalog.failure_class |
| **C10** | severity blocker/critical: control_center.included = true (im Control Center sichtbar) |
| **C11** | binding_status catalog_bound nur wenn incident status = bound_to_regression oder closed |

### 5.3 replay.yaml ↔ bindings.json

| Regel | Beschreibung |
|-------|--------------|
| **C12** | incident_id muss identisch sein: replay identity.incident_id = bindings identity.incident_id |
| **C13** | replay_id muss übereinstimmen: replay identity.id = bindings identity.replay_id (falls gesetzt) |
| **C14** | regression_test in bindings muss auf existierenden Test verweisen (bei catalog_bound) |

---

## 6. Fehlerklassen der Validierung

| Code | Bedeutung | Beispiel |
|------|------------|----------|
| **SCHEMA_ERROR** | JSON/YAML-Struktur oder Schema-Verletzung | Fehlendes Pflichtfeld, falscher Typ |
| **MISSING_FIELD** | Pflichtfeld fehlt | identity.id fehlt |
| **INVALID_STATUS_TRANSITION** | Ungültiger Statusübergang | new → classified |
| **CONSISTENCY_ERROR** | Inkonsistenz zwischen Dateien | incident_id unterschiedlich |
| **UNKNOWN_VALUE** | Wert nicht in Allowed Values | severity: "x" statt "critical" |
| **FILE_MISSING** | Erforderliche Datei fehlt | replay_defined ohne replay.yaml |
| **LIFECYCLE_VIOLATION** | Lifecycle-Bedingung verletzt | bound_to_regression ohne regression_test |
| **PATTERN_VIOLATION** | Pattern nicht erfüllt | id: "INC-123" statt INC-20260315-001 |

---

## 7. Validator-Output

| Output | Bedeutung |
|--------|-----------|
| **OK** | Alle Prüfungen bestanden |
| **WARN** | Mindestens eine Warnung, keine Fehler |
| **ERROR** | Mindestens ein Fehler |

Exit-Codes:

- 0 = OK
- 1 = WARN
- 2 = ERROR
