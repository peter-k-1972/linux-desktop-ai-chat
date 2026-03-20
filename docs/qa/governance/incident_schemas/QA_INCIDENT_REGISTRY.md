# QA Incident Registry – Datenstruktur und Index-Format

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Zentrale Registry für Incident-Aggregation und QA-Projektion.

---

## 1. Registry-Datenstruktur

### 1.1 Speicherort

```
docs/qa/incidents/index.json
```

### 1.2 Incident-Verzeichnisstruktur

Jeder Incident liegt unter:

```
docs/qa/incidents/
├── INC-20260315-001/           # oder INC-YYYYMMDD-NNN_slug
│   ├── incident.yaml           # Pflicht
│   ├── replay.yaml             # optional
│   ├── bindings.json           # optional
│   └── notes.md                # optional
├── INC-20260315-002_slug/
│   └── ...
└── index.json                  # generiert
```

Unterverzeichnisse `templates/`, `_schema/` werden beim Scan ignoriert.

---

## 2. Index-Dateiformat (index.json)

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-15T12:00:00Z",
  "incident_count": 42,
  "incidents": [
    {
      "incident_id": "INC-20260315-001",
      "slug": "test-incident",
      "title": "Kurzbeschreibung",
      "status": "new",
      "severity": "medium",
      "priority": "P2",
      "subsystem": "Chat",
      "component": null,
      "runtime_layer": "ui",
      "failure_class": "ui_state_drift",
      "reproducibility": "always",
      "regression_required": true,
      "replay_status": null,
      "binding_status": null,
      "detected_at": "2026-03-15T10:00:00Z",
      "first_seen_version": null,
      "last_seen_version": null,
      "risk_tags": [],
      "autopilot_eligible": false,
      "catalog_candidate": false
    }
  ],
  "clusters": {
    "failure_class": { "ui_state_drift": 5, "async_race": 3 },
    "subsystem": { "Chat": 4, "RAG": 3 },
    "runtime_layer": { "ui": 6, "service": 2 }
  },
  "metrics": {
    "open_incidents": 8,
    "classified_incidents": 12,
    "replay_defined": 6,
    "replay_verified": 4,
    "bound_to_regression": 2
  },
  "warnings": [
    {
      "code": "MISSING_REPLAY",
      "incident_id": "INC-20260315-002",
      "message": "replay.yaml fehlt"
    }
  ]
}
```

---

## 3. Registry-Felder pro Incident

| Feld | Quelle | Beschreibung |
|------|--------|--------------|
| **incident_id** | incident.yaml identity.id | Eindeutige ID |
| **slug** | Verzeichnisname oder abgeleitet | Kurzbezeichnung |
| **title** | incident.yaml identity.title | Kurzbeschreibung |
| **status** | incident.yaml qa.status | Lifecycle-Status |
| **severity** | incident.yaml classification.severity | Schweregrad |
| **priority** | incident.yaml classification.priority | Priorität |
| **subsystem** | incident.yaml classification.subsystem | Betroffenes Subsystem |
| **component** | incident.yaml analysis.affected_components[0] | Primäre Komponente |
| **runtime_layer** | incident.yaml environment.runtime_layer | Laufzeit-Schicht |
| **failure_class** | incident.yaml classification.failure_class | Fehlerklasse |
| **reproducibility** | incident.yaml behavior.reproducibility | Reproduzierbarkeit |
| **regression_required** | abgeleitet | severity ≥ medium und kein regression_test |
| **replay_status** | replay.yaml verification.status | Replay-Lifecycle |
| **binding_status** | bindings.json status.binding_status | Binding-Status |
| **detected_at** | incident.yaml detection.when | Zeitpunkt der Erkennung |
| **first_seen_version** | incident.yaml (optional) | Erste Version |
| **last_seen_version** | incident.yaml (optional) | Letzte Version |
| **risk_tags** | classification.tags + bindings | Risiko-Tags |
| **autopilot_eligible** | bindings.json autopilot.sprint_candidate | Sprint-Kandidat |
| **catalog_candidate** | abgeleitet | Replay vorhanden, kein Test |

---

## 4. Warnungsklassen

| Code | Bedeutung |
|------|-----------|
| **MISSING_REPLAY** | replay.yaml fehlt (bei status ≥ classified erwartet) |
| **MISSING_BINDING** | bindings.json fehlt (bei status ≥ replay_defined erwartet) |
| **UNKNOWN_STATUS** | qa.status nicht in Allowed Values |
| **UNKNOWN_FAILURE_CLASS** | failure_class nicht in REGRESSION_CATALOG |
| **UNKNOWN_SEVERITY** | severity nicht in Allowed Values |
| **UNKNOWN_SUBSYSTEM** | subsystem nicht in QA_RISK_RADAR |
| **PARSE_ERROR** | Datei konnte nicht geladen werden |
| **SKIPPED_DIR** | Verzeichnis übersprungen (kein incident.yaml) |

---

## 5. Metrik-Definitionen

| Metrik | Definition |
|--------|------------|
| **open_incidents** | status ∈ {new, triaged, classified, replay_defined, replay_verified} |
| **classified_incidents** | status ∈ {classified, replay_defined, replay_verified, bound_to_regression, closed} |
| **replay_defined** | status = replay_defined oder replay_verified oder bound_to_regression oder closed |
| **replay_verified** | status = replay_verified oder bound_to_regression oder closed |
| **bound_to_regression** | status = bound_to_regression oder closed |
