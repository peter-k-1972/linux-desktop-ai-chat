# QA Incident Replay – Architektur

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Überblicksarchitektur des QA Incident Replay Systems. Reale Bugs als strukturierte Incidents erfassen, in Replay-Szenarien überführen, später als Regression Guards nutzen.

---

## 1. Zielbild und Motivation

### 1.1 Zielbild

| Aspekt | Beschreibung |
|--------|--------------|
| **Vom Bug zum Guard** | Jeder reale Bug wird als Incident erfasst, in ein Replay-Szenario überführt und schließlich durch einen Regressionstest abgesichert. |
| **Strukturierte Erfassung** | Incidents sind maschinenlesbar (YAML/JSON), nicht Prosa. Reproduktion, Klassifikation und Integration sind standardisiert. |
| **Governance durch Lifecycle** | Klare Statusübergänge von `new` bis `closed`. Kein Incident „verschwindet“ – jeder durchläuft definierte Schritte. |
| **Integration statt Parallelwelt** | Incidents speisen REGRESSION_CATALOG, QA_CONTROL_CENTER, QA_AUTOPILOT. Keine isolierten Strukturen. |

### 1.2 Motivation

| Lücke (vorher) | Lösung (Incident Replay) |
|----------------|--------------------------|
| REGRESSION_CATALOG ordnet Tests Fehlerklassen zu – aber nicht: *Welcher Bug führte zu welchem Test?* | Incident-ID verknüpft Bug ↔ Test ↔ Fehlerklasse |
| Historische Bugs (AUDIT_REPORT) sind Prosa – nicht maschinenlesbar | incident.yaml + replay.yaml als strukturierte Quelle |
| Kein standardisierter Pfad: Bug → Incident → Replay → Guard | Lifecycle mit definierten Übergängen und Governance |
| Restlücken im Risk Radar (ChromaDB, Ollama, EventType Drift) nicht testbar | Pilotfälle definieren Reproduktionsverträge für Top-Risiken |

### 1.3 Einordnung in die QA-Architektur

Incident Replay ist eine **neue QA-Schicht** zwischen:

- **Input:** Reale Bugs (Produktion, Staging, manuelle Reproduktion)
- **Output:** Strukturierte Incidents → Replay-Artefakte → (später) Regression-Tests

Sie schließt die Lücke: *Vom Bug zum dauerhaften Guard.*

---

## 2. Incident-Verzeichnisstruktur

```
docs/qa/incidents/
├── _schema/                              # Zentral (einmalig)
│   ├── incident.schema.yaml
│   ├── replay.schema.yaml
│   └── bindings.schema.json
│
├── templates/                            # Verbindliche Vorlagen
│   ├── incident.template.yaml
│   ├── replay.template.yaml
│   ├── bindings.template.json
│   └── notes.template.md
│
├── INC-YYYYMMDD-NNN/                     # Pro Incident ein Verzeichnis
│   ├── incident.yaml                     # Führend: Beobachteter Vorfall
│   ├── replay.yaml                       # Führend: Reproduktionsvertrag
│   ├── bindings.json                     # Führend: QA-Bindings
│   ├── notes.md                          # Führend: Review-Notizen
│   │
│   ├── evidence/                         # Unterstützend: Belege
│   │   └── (screenshots, logs, stacktraces)
│   │
│   ├── fixtures/                         # Unterstützend: Replay-Vorlagen
│   │   └── (state files, mock data)
│   │
│   └── derived/                          # Abgeleitet: Generierte Artefakte
│       └── (validierung.json – niemals von Hand)
│
└── _registry.json                        # Abgeleitet: Aggregiert aus allen Incidents
```

### 2.1 Namenskonvention

| Element | Format | Beispiel |
|---------|--------|----------|
| Incident-Verzeichnis | `INC-YYYYMMDD-NNN` | `INC-20260315-001` |
| Replay-ID | `REPLAY-INC-YYYYMMDD-NNN` | `REPLAY-INC-20260315-001` |
| Schema-Verzeichnis | `_schema` | Reserviert, Unterstrich = Meta |
| Registry | `_registry.json` | Projekt-weit, generiert |

### 2.2 Trennung der Verantwortlichkeiten

| Artefakt | Zweck |
|----------|-------|
| **incident.yaml** | Was ist passiert? Beobachtung, uninterpretiert |
| **replay.yaml** | Was wird getestet? Reproduktionsvertrag, minimal |
| **bindings.json** | Wo gehört es hin? Fehlerklasse, Subsystem, Test-Pfad |
| **notes.md** | Warum so entschieden? Kontext, Diskussion |

---

## 3. incident.yaml Standard

**Vollständige Spezifikation:** [QA_INCIDENT_SCHEMA.md](QA_INCIDENT_SCHEMA.md)

### 3.1 Sektionsübersicht

| Sektion | Pflicht | Zweck |
|---------|---------|-------|
| schema_version | ja | Schema-Version |
| identity | ja | ID, Titel, Quelle, Zeitstempel |
| detection | ja | Wann, wie erkannt |
| environment | ja | Laufzeit-Schicht, Plattform |
| classification | ja | Fehlerklasse, Subsystem, Severity, Priority |
| behavior | ja | Beschreibung, erwartet vs. tatsächlich, Reproduktionsschritte |
| evidence | nein | Referenzen auf Belege |
| analysis | nein | Root Cause, betroffene Komponenten |
| resolution | nein | Fix, Verifizierung |
| qa | ja | Lifecycle-Status |

### 3.2 Kernfelder

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| identity.id | string | `INC-YYYYMMDD-NNN`, muss Verzeichnisname entsprechen |
| classification.failure_class | string | Aus REGRESSION_CATALOG |
| classification.subsystem | string | Aus QA_RISK_RADAR |
| behavior.repro_steps | string[] | Nummerierte Reproduktionsschritte |
| qa.status | enum | new, triaged, classified, replay_defined, replay_verified, bound_to_regression, closed, invalid, duplicate, archived |

---

## 4. replay.yaml Standard

**Vollständige Spezifikation:** [QA_REPLAY_SCHEMA.md](QA_REPLAY_SCHEMA.md)

### 4.1 Grundprinzip: Deklarativ vor Testcode

- **Reproduktionsvertrag:** Vereinbarung zwischen Incident und künftigem Test
- **Kein Testcode:** Keine Assertions, kein pytest – nur Struktur und Semantik
- **Plattformunabhängig:** Ein (zukünftiger) Runner führt aus

### 4.2 Sektionsübersicht

| Sektion | Pflicht | Zweck |
|---------|---------|-------|
| schema_version | ja | Schema-Version |
| identity | ja | Replay-ID, Incident-Referenz |
| replay_type | ja | startup_dependency_failure, fault_injection, event_contract_drift, … |
| preconditions | ja | System- und externe Bedingungen |
| execution | ja | Schritte (id, action, actor) |
| assertion_contract | ja | success, failure, no_crash |
| observability_contract | ja | events, ui_state, debug_visibility |
| determinism | ja | level, isolated |
| mapping | ja | test_domains, risk_axes |
| verification | ja | status (draft, validated, test_bound, guarded, obsolete) |

### 4.3 Replay-Typen

| Typ | Bedeutung |
|-----|-----------|
| startup_dependency_failure | Optionale Abhängigkeit fehlt/unreachable beim Start |
| provider_unreachable | Externer Provider (Ollama, API) nicht erreichbar |
| fault_injection | Gezielte Störung während Laufzeit |
| event_contract_drift | Event/Schema passt nicht zu Erwartung |
| state_sequence | Bestimmte Abfolge von Zuständen/Aktionen |
| cross_layer | UI↔Service↔Persistenz |
| async_race | Async/Race-Condition |
| hybrid | Kombination mehrerer Typen |

---

## 5. bindings.json Standard

**Vollständige Spezifikation:** [incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md](incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md)

### 5.1 Rolle

bindings.json ist die **Integrationsschicht** – die Brücke zu REGRESSION_CATALOG, QA_RISK_RADAR, QA_HEATMAP, QA_CONTROL_CENTER, QA_AUTOPILOT.

### 5.2 Kernsektionen

| Sektion | Pflicht | Zweck |
|---------|---------|-------|
| identity | ja | incident_id, replay_id |
| regression_catalog | ja | failure_class, regression_test |
| risk_radar | ja | subsystem, priority |
| heatmap | ja | dimensions |
| status | ja | binding_status (proposed, validated, catalog_bound, rejected, archived) |
| meta | ja | created, updated |

### 5.3 Binding-Status

| Status | Bedeutung |
|--------|-----------|
| proposed | Vorgeschlagen, noch nicht geprüft |
| validated | Manuell bestätigt |
| catalog_bound | In REGRESSION_CATALOG eingetragen |
| rejected | Abgelehnt |
| archived | Historisch, nicht mehr aktiv |

---

## 6. Lifecycle und Governance

**Vollständige Spezifikation:** [QA_INCIDENT_LIFECYCLE.md](QA_INCIDENT_LIFECYCLE.md)

### 6.1 Incident-Lifecycle

```
new → triaged → classified → replay_defined → replay_verified → bound_to_regression → closed
  │       │           │              │                │                    │
  └───────┴───────────┴──────────────┴────────────────┴────────────────────┴──► invalid, duplicate, archived
```

### 6.2 Replay-Lifecycle

```
draft → validated → test_bound → guarded
  │         │            │
  └─────────┴────────────┴────────────────► obsolete
```

### 6.3 Governance-Regeln (Auswahl)

| ID | Regel |
|----|-------|
| G1 | classified erfordert failure_class und subsystem |
| G2 | failure_class muss in REGRESSION_CATALOG existieren |
| G3 | replay_defined erfordert valides replay.yaml |
| G4 | closed erfordert resolution.fix und resolution.verified |
| G5 | bound_to_regression erfordert regression_test in bindings.json |
| G6 | invalid/duplicate erfordert Begründung |

---

## 7. Integration

**Vollständige Spezifikation:** [QA_INCIDENT_INTEGRATION.md](QA_INCIDENT_INTEGRATION.md)

### 7.1 Datenfluss

```
docs/qa/incidents/INC-*/
    │
    ▼
_registry.json (aggregiert)
    │
    ├──► REGRESSION_CATALOG (Incidents pro Fehlerklasse, incident_ref)
    ├──► QA_CONTROL_CENTER (Offene Incidents, KPIs, Warnsignale)
    ├──► QA_AUTOPILOT (Incident-Kandidaten, Empfehlungen)
    ├──► QA_PRIORITY_SCORE (optional: Incident-Faktor)
    └──► QA_ANOMALY_DETECTION (incident_backlog, incident_replay_gap)
```

### 7.2 Integrationspunkte

| Artefakt | Integration |
|----------|--------------|
| REGRESSION_CATALOG | Incidents pro Fehlerklasse, incident_ref in Zuordnung |
| QA_CONTROL_CENTER | Offene Incidents, KPIs, Warnsignale |
| QA_AUTOPILOT | Incident-Kandidaten, empfohlener Schritt |
| QA_RISK_RADAR | Keine direkte Änderung; Incidents bestätigen Risiken |

---

## 8. Pilotfälle

**Vollständige Spezifikation:** [incidents/QA_INCIDENT_PILOT_ITERATION.md](incidents/QA_INCIDENT_PILOT_ITERATION.md)

### 8.1 Drei Pilotfälle (Top-3-Risiken)

| # | Subsystem | Incident-Klasse | replay_type | failure_class |
|---|-----------|-----------------|-------------|---------------|
| 1 | Startup/Bootstrap | Ollama unreachable | startup_dependency_failure | degraded_mode_failure |
| 2 | RAG | ChromaDB Netzwerkfehler | fault_injection | rag_silent_failure |
| 3 | Debug/EventBus | EventType Drift | event_contract_drift | debug_false_truth |

### 8.2 Architektonische Begründung

- **Risikokongruenz:** Entsprechen exakt den Top-3 aus QA_RISK_RADAR
- **Verschiedene Replay-Typen:** Validierung des Schemas über unterschiedliche Szenarien
- **Verschiedene Schichten:** Startup, RAG, Debug – keine Redundanz
- **Bestehende Test-Anker:** test_startup_without_ollama, test_chroma_unreachable, test_event_type_drift

---

## 9. Verweise

| Dokument | Inhalt |
|----------|--------|
| [QA_INCIDENT_SCHEMA.md](QA_INCIDENT_SCHEMA.md) | incident.yaml Feldstandard |
| [QA_REPLAY_SCHEMA.md](QA_REPLAY_SCHEMA.md) | replay.yaml Feldstandard |
| [QA_INCIDENT_LIFECYCLE.md](QA_INCIDENT_LIFECYCLE.md) | Lifecycle, Governance, Reviewpflichten |
| [QA_INCIDENT_INTEGRATION.md](QA_INCIDENT_INTEGRATION.md) | Integration in Catalog, Control Center, Autopilot |
| [incidents/QA_INCIDENT_PILOT_ITERATION.md](incidents/QA_INCIDENT_PILOT_ITERATION.md) | Pilotfälle, Replay-Typen, Observability |
| [QA_INCIDENT_ARTIFACT_STANDARD.md](QA_INCIDENT_ARTIFACT_STANDARD.md) | Verbindlicher Artefaktstandard |
| [REGRESSION_CATALOG.md](REGRESSION_CATALOG.md) | Fehlerklassen |
| [QA_RISK_RADAR.md](QA_RISK_RADAR.md) | Subsystem-Risiken |

---

*QA Incident Replay Architektur – verbindlich ab 15. März 2026. Nur QA-Architektur, keine Implementierung.*
