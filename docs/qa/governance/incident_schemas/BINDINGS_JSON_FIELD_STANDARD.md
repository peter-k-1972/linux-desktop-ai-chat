# bindings.json – Verbindlicher Feldstandard

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Maschinenlesbare Integrationsschicht zwischen Incident Replay und den bestehenden QA-Artefakten.

---

## 1. Rolle von bindings.json

bindings.json verbindet einen Incident (mit Replay) mit dem QA-Ökosystem:

- **REGRESSION_CATALOG** – Fehlerklasse, Test-Zuordnung
- **QA_RISK_RADAR** – Subsystem, Priorität, Risikodimensionen
- **QA_HEATMAP** – Abdeckungsdimensionen, Weak Spots
- **QA_CONTROL_CENTER** – Steuerungsboard, offene Incidents
- **QA_AUTOPILOT** – Sprint-Kandidaten, empfohlene Testart
- **QA_DEPENDENCY_GRAPH** – Kaskadenpfade, betroffene Subsysteme

bindings.json ist **kein Ersatz** für incident.yaml oder replay.yaml. Es ist die **Integrationsschicht** – die Brücke, über die Generatoren und Tooling Incidents in die QA-Artefakte einbinden.

---

## 2. Sektionsübersicht

| Sektion | Zweck | Pflicht |
|---------|-------|---------|
| **schema_version** | Schema-Version | ja |
| **identity** | Incident/Replay-Referenz | ja |
| **regression_catalog** | Binding zu REGRESSION_CATALOG | ja |
| **risk_radar** | Binding zu QA_RISK_RADAR | ja |
| **heatmap** | Binding zu QA_HEATMAP | ja |
| **control_center** | Binding zu QA_CONTROL_CENTER | nein |
| **autopilot** | Binding zu QA_AUTOPILOT | nein |
| **dependency_graph** | Binding zu QA_DEPENDENCY_GRAPH | nein |
| **status** | Binding-Statusmodell | ja |
| **meta** | Erzeugung, Review, Audit | ja |

---

## 3. Vollständiger Feldkatalog

### 3.1 schema_version (Top-Level)

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **schema_version** | Schema-Version für Validierung. | **ja** | `"1.0"` |

---

### 3.2 identity

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **identity.incident_id** | Referenz auf incident.yaml. | **ja** | Pattern: `INC-YYYYMMDD-NNN` |
| **identity.replay_id** | Referenz auf replay.yaml. | nein | Pattern: `REPLAY-INC-YYYYMMDD-NNN` |
| **identity.incident_dir** | Relativer Pfad zum Incident-Verzeichnis. | nein | String (z.B. `INC-20260315-001`) |

---

### 3.3 regression_catalog

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **regression_catalog.failure_class** | Fehlerklasse aus REGRESSION_CATALOG. | **ja** | Siehe REGRESSION_CATALOG |
| **regression_catalog.regression_test** | Pfad zum Regressionstest (falls vorhanden). | nein | String (z.B. `tests/failure_modes/test_foo.py::test_bar`) |
| **regression_catalog.catalog_entry** | Referenz auf Eintrag im Catalog (Datei, Test). | nein | String |
| **regression_catalog.notes** | Zusätzliche Catalog-Notizen. | nein | String |

**Erlaubte Werte failure_class:** ui_state_drift, async_race, late_signal_use_after_destroy, request_context_loss, rag_silent_failure, debug_false_truth, startup_ordering, degraded_mode_failure, contract_schema_drift, metrics_false_success, tool_failure_visibility, optional_dependency_missing

---

### 3.4 risk_radar

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **risk_radar.subsystem** | Betroffenes Subsystem aus QA_RISK_RADAR. | **ja** | Siehe QA_RISK_RADAR |
| **risk_radar.priority** | Priorität (P1, P2, P3). | nein | `P1`, `P2`, `P3` |
| **risk_radar.risk_dimensions** | Betroffene Risikodimensionen. | nein | Liste, siehe unten |
| **risk_radar.top_risk_relevance** | Ist dieser Incident im Top-Risiko-Bereich? | nein | Boolean |
| **risk_radar.notes** | Zusätzliche Risk-Radar-Notizen. | nein | String |

**Erlaubte Werte risk_radar.subsystem:** Chat, Agentensystem, Prompt-System, RAG, Debug/EventBus, Metrics, Startup/Bootstrap, Tools, Provider/Ollama, Persistenz/SQLite

**Erlaubte Werte risk_radar.risk_dimensions:** Failure_Impact, Async_State, Cross_Layer, Failure_Test, Contract_Gov, Drift_Risiko, Restluecken

---

### 3.5 heatmap

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **heatmap.dimensions** | Welche Heatmap-Dimensionen adressiert dieser Incident? | **ja** | Liste von Strings |
| **heatmap.weak_spot** | Trägt der Incident zu einem Weak Spot bei? | nein | Boolean |
| **heatmap.dimension_scores** | Erwartete Verbesserung pro Dimension (optional). | nein | Mapping |
| **heatmap.notes** | Zusätzliche Heatmap-Notizen. | nein | String |

**Erlaubte Werte heatmap.dimensions:** Failure_Coverage, Contract_Coverage, Async_Coverage, Cross_Layer_Coverage, Drift_Governance_Coverage, Restrisiko

---

### 3.6 control_center

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **control_center.included** | Wird dieser Incident im Control Center berücksichtigt? | nein | Boolean (default: true) |
| **control_center.open_incident** | Zählt als offener Incident (ohne Guard)? | nein | Boolean |
| **control_center.recommendation_relevant** | Relevant für Top-5-Empfehlungen? | nein | Boolean |
| **control_center.notes** | Zusätzliche Control-Center-Notizen. | nein | String |

---

### 3.7 autopilot

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **autopilot.sprint_candidate** | Kandidat für nächsten QA-Sprint? | nein | Boolean |
| **autopilot.recommended_test_art** | Empfohlene Testart (aus Autopilot-Logik). | nein | String |
| **autopilot.recommended_step** | Empfohlener QA-Schritt. | nein | String |
| **autopilot.priority_score** | Priority-Score-Wert (falls bekannt). | nein | Integer |
| **autopilot.notes** | Zusätzliche Autopilot-Notizen. | nein | String |

**Erlaubte Werte recommended_test_art:** Contract-Tests, Failure-Mode-Tests, Async-Behavior-Tests, Cross-Layer-Tests, Drift/Governance-Tests, Startup-Tests, Chaos-Tests

---

### 3.8 dependency_graph

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **dependency_graph.primary_subsystem** | Primär betroffenes Subsystem. | nein | String (wie risk_radar.subsystem) |
| **dependency_graph.cascade_subsystems** | Weitere betroffene Subsysteme (Kaskade). | nein | Liste von Strings |
| **dependency_graph.edge_types** | Betroffene Kanten-Typen. | nein | `runtime`, `startup`, `persistence`, `observability` |
| **dependency_graph.impact** | Impact-Level. | nein | `high`, `medium`, `low` |
| **dependency_graph.notes** | Zusätzliche Dependency-Notizen. | nein | String |

---

### 3.9 status

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **status.binding_status** | Status des Bindings im QA-System. | **ja** | Siehe Abschnitt 4 |
| **status.updated** | Zeitpunkt der letzten Statusänderung. | **ja** | ISO 8601 |
| **status.reason** | Grund für Statusänderung (bei rejected/archived). | nein | String |

---

### 3.10 meta

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **meta.created** | Zeitpunkt der Erstellung. | **ja** | ISO 8601 |
| **meta.updated** | Zeitpunkt der letzten Änderung. | **ja** | ISO 8601 |
| **meta.generated_fields** | Welche Felder wurden maschinell erzeugt? | nein | Liste von Pfaden (z.B. `["heatmap.weak_spot", "autopilot.sprint_candidate"]`) |
| **meta.review_required** | Sind Änderungen reviewpflichtig? | nein | Boolean |
| **meta.reviewed_at** | Zeitpunkt des letzten Reviews. | nein | ISO 8601 |
| **meta.reviewed_by** | Wer hat zuletzt reviewed? | nein | String |

---

## 4. Binding-Statusmodell

### 4.1 Erlaubte Statuswerte (status.binding_status)

| Status | Bedeutung | Nächste Aktionen |
|--------|------------|------------------|
| **proposed** | Binding vorgeschlagen, noch nicht geprüft | Review durchführen |
| **validated** | Binding manuell geprüft und bestätigt | In Catalog eintragen (falls noch nicht) |
| **catalog_bound** | In REGRESSION_CATALOG eingetragen, Test zugeordnet | – |
| **rejected** | Binding abgelehnt (falsche Zuordnung, nicht relevant) | Grund in status.reason dokumentieren |
| **archived** | Incident/Replay archiviert, Binding nicht mehr aktiv | – |

### 4.2 Statusübergänge

```
proposed ──► validated ──► catalog_bound
    │            │
    └────────────┼────► rejected
                 │
                 └────► archived (von validated oder catalog_bound)
```

### 4.3 Regeln pro Status

#### proposed

| Regel | Beschreibung |
|-------|--------------|
| **P1** | Initialer Status bei neuem Binding. Kann maschinell vorgeschlagen werden. |
| **P2** | Alle Pflichtfelder müssen ausgefüllt sein (failure_class, subsystem, heatmap.dimensions). |
| **P3** | proposed → validated erfordert manuellen Review. |

#### validated

| Regel | Beschreibung |
|-------|--------------|
| **V1** | Binding wurde von einer berechtigten Person geprüft und bestätigt. |
| **V2** | validated → catalog_bound: Wenn Test existiert und in REGRESSION_CATALOG eingetragen. |
| **V3** | validated → rejected: Wenn Zuordnung falsch oder Incident nicht relevant. |
| **V4** | validated → archived: Wenn Incident/Replay archiviert wird. |

#### catalog_bound

| Regel | Beschreibung |
|-------|--------------|
| **C1** | regression_catalog.regression_test muss gesetzt sein (oder Catalog-Eintrag existiert). |
| **C2** | Incident ist im REGRESSION_CATALOG verzeichnet. |
| **C3** | catalog_bound → archived: Nur wenn Incident obsolet wird. |

#### rejected

| Regel | Beschreibung |
|-------|--------------|
| **R1** | status.reason muss den Ablehnungsgrund enthalten. |
| **R2** | rejected ist Endzustand (kein Übergang zu validated ohne erneutes proposed). |
| **R3** | Rejected Bindings werden von Aggregatoren ignoriert. |

#### archived

| Regel | Beschreibung |
|-------|--------------|
| **A1** | Binding ist historisch, wird nicht mehr aktiv genutzt. |
| **A2** | Archived Bindings können für Statistiken berücksichtigt werden, nicht für Empfehlungen. |
| **A3** | status.reason kann Grund der Archivierung enthalten. |

---

## 5. Maschinell erzeugbare vs. reviewpflichtige Teile

### 5.1 Maschinell erzeugbar (ohne Review)

Diese Felder dürfen von Generatoren/Tooling **automatisch** gesetzt oder aktualisiert werden:

| Feld | Begründung |
|------|------------|
| **identity.incident_dir** | Ableitbar aus incident_id |
| **identity.replay_id** | Ableitbar aus replay.yaml |
| **regression_catalog.failure_class** | Aus incident.yaml classification |
| **risk_radar.subsystem** | Aus incident.yaml classification |
| **heatmap.dimensions** | Aus replay.yaml mapping.risk_axes + mapping.test_domains |
| **heatmap.weak_spot** | Berechnet aus QA_HEATMAP (Subsystem hat Wert 1 in Dimension) |
| **autopilot.sprint_candidate** | Berechnet (Replay ohne Test + Subsystem in Autopilot-Kandidaten) |
| **autopilot.recommended_test_art** | Aus QA_AUTOPILOT für Subsystem |
| **autopilot.recommended_step** | Aus QA_AUTOPILOT für Subsystem |
| **autopilot.priority_score** | Aus QA_PRIORITY_SCORE |
| **control_center.open_incident** | Berechnet (status in incident.yaml ≠ guarded) |
| **dependency_graph.primary_subsystem** | Gleich risk_radar.subsystem |
| **dependency_graph.cascade_subsystems** | Aus QA_DEPENDENCY_GRAPH berechnet |
| **meta.generated_fields** | Liste der maschinell gesetzten Felder |
| **meta.updated** | Bei jeder Änderung |

**Bedingung:** Maschinell erzeugte Werte müssen als solche markiert sein (meta.generated_fields). Bei Konflikt mit manuell gesetzten Werten gilt: reviewpflichtige Felder haben Vorrang.

### 5.2 Reviewpflichtig (manuell bestätigen)

Diese Felder **müssen** von einer berechtigten Person geprüft und bestätigt werden:

| Feld | Begründung |
|------|------------|
| **regression_catalog.regression_test** | Pfad muss korrekt sein, Test muss existieren |
| **regression_catalog.catalog_entry** | Eintrag muss im Catalog existieren |
| **risk_radar.priority** | Priorisierung ist Entscheidung |
| **risk_radar.risk_dimensions** | Zuordnung zu Dimensionen ist fachlich |
| **risk_radar.top_risk_relevance** | Kann maschinell vorgeschlagen, muss bestätigt werden |
| **control_center.included** | Entscheidung, ob im Control Center sichtbar |
| **control_center.recommendation_relevant** | Entscheidung für Top-5 |
| **status.binding_status** | Übergang proposed → validated erfordert Review |
| **status.reason** | Bei rejected/archived: Begründung erforderlich |
| **meta.reviewed_at** | Wird bei Review gesetzt |
| **meta.reviewed_by** | Wird bei Review gesetzt |

### 5.3 Übersicht

| Kategorie | Felder | Regel |
|-----------|--------|-------|
| **Maschinell** | identity.incident_dir, identity.replay_id, failure_class, subsystem, heatmap.dimensions, heatmap.weak_spot, autopilot.*, control_center.open_incident, dependency_graph.* | Generator darf setzen, meta.generated_fields pflegen |
| **Reviewpflichtig** | regression_test, catalog_entry, risk_radar.priority, risk_radar.risk_dimensions, status.binding_status, status.reason, control_center.included, control_center.recommendation_relevant | Manuell bestätigen vor Status validated |
| **Hybrid** | risk_radar.subsystem, regression_catalog.failure_class | Können aus incident.yaml übernommen werden, aber Review bestätigt Korrektheit |

---

## 6. Pflichtfeld-Checkliste

| Sektion | Pflichtfelder |
|---------|---------------|
| Top-Level | `schema_version` |
| identity | `incident_id` |
| regression_catalog | `failure_class` |
| risk_radar | `subsystem` |
| heatmap | `dimensions` |
| status | `binding_status`, `updated` |
| meta | `created`, `updated` |

**Optionale Sektionen:** control_center, autopilot, dependency_graph (können ganz fehlen).

---

## 7. Beispielstruktur

```json
{
  "schema_version": "1.0",

  "identity": {
    "incident_id": "INC-20260315-001",
    "replay_id": "REPLAY-INC-20260315-001",
    "incident_dir": "INC-20260315-001"
  },

  "regression_catalog": {
    "failure_class": "rag_silent_failure",
    "regression_test": "tests/failure_modes/test_rag_retrieval_failure.py::test_rag_failure_emits_event",
    "catalog_entry": "REGRESSION_CATALOG.md – test_rag_retrieval_failure",
    "notes": null
  },

  "risk_radar": {
    "subsystem": "RAG",
    "priority": "P1",
    "risk_dimensions": ["Failure_Impact", "Restluecken"],
    "top_risk_relevance": true,
    "notes": null
  },

  "heatmap": {
    "dimensions": ["Failure_Coverage", "Drift_Governance_Coverage"],
    "weak_spot": true,
    "notes": null
  },

  "control_center": {
    "included": true,
    "open_incident": false,
    "recommendation_relevant": false,
    "notes": "Guarded, nicht mehr in Top-5"
  },

  "autopilot": {
    "sprint_candidate": false,
    "recommended_test_art": "Failure-Mode-Tests",
    "recommended_step": "Embedding-Service Failure (Ollama Embedding-API)",
    "priority_score": 4,
    "notes": null
  },

  "dependency_graph": {
    "primary_subsystem": "RAG",
    "cascade_subsystems": ["Chat", "Agentensystem"],
    "edge_types": ["runtime", "persistence"],
    "impact": "high",
    "notes": null
  },

  "status": {
    "binding_status": "catalog_bound",
    "updated": "2026-03-15T14:00:00Z",
    "reason": null
  },

  "meta": {
    "created": "2026-03-15T11:00:00Z",
    "updated": "2026-03-15T14:00:00Z",
    "generated_fields": [
      "heatmap.weak_spot",
      "autopilot.sprint_candidate",
      "autopilot.recommended_test_art",
      "control_center.open_incident",
      "dependency_graph.cascade_subsystems"
    ],
    "review_required": false,
    "reviewed_at": "2026-03-15T13:00:00Z",
    "reviewed_by": "QA Lead"
  }
}
```

---

## 8. Validierungsregeln

| Regel | Beschreibung |
|-------|--------------|
| **V1** | `identity.incident_id` muss auf existierendes Incident-Verzeichnis verweisen. |
| **V2** | `regression_catalog.failure_class` muss in REGRESSION_CATALOG existieren. |
| **V3** | `risk_radar.subsystem` muss in QA_RISK_RADAR existieren. |
| **V4** | `heatmap.dimensions` nur gültige Werte aus QA_HEATMAP. |
| **V5** | `status.binding_status` = validated|catalog_bound erfordert meta.reviewed_at. |
| **V6** | `status.binding_status` = rejected erfordert status.reason. |
| **V7** | `status.binding_status` = catalog_bound erfordert regression_catalog.regression_test oder catalog_entry. |

---

## 9. Integration: Wie Bindings genutzt werden

| QA-Artefakt | Nutzung der Bindings |
|-------------|----------------------|
| **REGRESSION_CATALOG** | Aggregator liest alle bindings.json, gruppiert nach failure_class, erzeugt „Incidents pro Fehlerklasse“. |
| **QA_RISK_RADAR** | Bindings mit subsystem → Incidents pro Subsystem, Priorität. |
| **QA_HEATMAP** | Bindings mit heatmap.dimensions → welche Incidents adressieren welche Lücken. |
| **QA_CONTROL_CENTER** | Bindings mit status ≠ rejected/archived, control_center.included → offene Incidents, Top-5. |
| **QA_AUTOPILOT** | Bindings mit autopilot.sprint_candidate → „Incident X als nächsten Guard umsetzen“. |
| **QA_DEPENDENCY_GRAPH** | Bindings mit dependency_graph → Incidents entlang Kaskadenpfaden. |

---

*Bindings JSON Feldstandard – verbindlich ab 15. März 2026.*
