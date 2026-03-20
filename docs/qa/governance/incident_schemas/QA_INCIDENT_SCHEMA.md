# QA Incident Schema – incident.yaml Standard

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Vollständiger Feldstandard für incident.yaml im QA Incident Replay System.

---

## 1. Zielbild

incident.yaml erfasst den **beobachteten Vorfall** – was tatsächlich passiert ist, uninterpretiert. Es ist die Quelle der Wahrheit für den Vorfall. Klassifikation (Fehlerklasse, Subsystem) erfolgt in incident.yaml (classification) und wird in bindings.json für die Integration gespiegelt.

---

## 2. Sektionsübersicht

| Sektion | Zweck | Pflicht |
|---------|-------|---------|
| **schema_version** | Schema-Version für Validierung und Migration | ja |
| **identity** | Incident-Identität, eindeutige Zuordnung | ja |
| **detection** | Wie und wann wurde der Vorfall erkannt? | ja |
| **environment** | Umgebung, in der der Vorfall auftrat | ja |
| **classification** | Fehlerklasse, Subsystem, Schicht | ja |
| **behavior** | Erwartetes vs. tatsächliches Verhalten | ja |
| **evidence** | Referenzen auf Belege | nein |
| **analysis** | Root Cause, Untersuchung | nein |
| **resolution** | Fix, Abschluss | nein |
| **qa** | QA-Lifecycle, Replay-Status | ja |

---

## 3. Vollständiger Feldkatalog

### 3.1 schema_version

| Feld | Pflicht | Typ | Erlaubte Werte |
|------|---------|-----|----------------|
| schema_version | **ja** | string | `"1.0"` |

---

### 3.2 identity

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| identity.id | **ja** | string | Pattern: `INC-YYYYMMDD-NNN`. Muss mit Verzeichnisnamen übereinstimmen. |
| identity.title | **ja** | string | Kurzbeschreibung, max. 80 Zeichen |
| identity.created | **ja** | datetime | ISO 8601 (z.B. 2026-03-15T10:00:00Z) |
| identity.updated | **ja** | datetime | ISO 8601, muss ≥ created sein |
| identity.source | **ja** | enum | Siehe Tabelle identity.source |
| identity.reporter | nein | string | Wer hat erfasst? |

**Erlaubte Werte identity.source:**

| Wert | Bedeutung |
|------|------------|
| production | In Produktion beobachtet |
| staging | In Staging/Testumgebung |
| development | Während Entwicklung |
| manual | Manuell reproduziert |
| audit | Im Audit identifiziert |
| regression | Bei Regressionstest |
| other | Sonstiges (in context/reporter erläutern) |

---

### 3.3 detection

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| detection.when | **ja** | datetime | Wann beobachtet? ISO 8601 |
| detection.how | **ja** | enum | Siehe Tabelle detection.how |
| detection.context | nein | string | Zusätzlicher Kontext |

**Erlaubte Werte detection.how:**

| Wert | Bedeutung |
|------|------------|
| manual | Manuell durch Nutzer/Entwickler beobachtet |
| test_failure | Durch fehlgeschlagenen Test erkannt |
| ci_failure | In CI-Pipeline erkannt |
| monitoring | Durch Monitoring/Alerting erkannt |
| audit | Im Rahmen eines Audits identifiziert |
| regression | Bei Regressionstest reproduziert |
| other | Sonstiges (in context erläutern) |

---

### 3.4 environment

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| environment.runtime_layer | **ja** | enum | Siehe Tabelle environment.runtime_layer |
| environment.platform | nein | string | z.B. Ubuntu 24.04 |
| environment.python_version | nein | string | z.B. 3.12 |
| environment.dependencies | nein | string[] | Ollama, ChromaDB, etc. |
| environment.config | nein | object/string | Relevante Konfiguration |
| environment.notes | nein | string | Freie Notizen |

**Erlaubte Werte environment.runtime_layer:**

| Wert | Bedeutung |
|------|------------|
| ui | UI-Schicht (PySide6, Widgets, Signale) |
| service | Service-Schicht (Chat, RAG, Agent, Provider) |
| persistence | Persistenz (SQLite, ChromaDB) |
| integration | Integration mehrerer Schichten |
| startup | Startup/Bootstrap |
| observability | Debug, EventBus, Metrics |
| cross_layer | Übergreifend (UI↔Service↔Persistenz) |
| other | Sonstiges (in notes erläutern) |

---

### 3.5 classification

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| classification.failure_class | **ja** | string | Aus REGRESSION_CATALOG, siehe Tabelle |
| classification.subsystem | **ja** | string | Aus QA_RISK_RADAR, siehe Tabelle |
| classification.severity | **ja** | enum | Siehe Tabelle classification.severity |
| classification.priority | **ja** | enum | Siehe Tabelle classification.priority |
| classification.tags | nein | string[] | Zusätzliche Tags |

**Erlaubte Werte classification.failure_class** (aus REGRESSION_CATALOG):

| Wert |
|------|
| ui_state_drift |
| async_race |
| late_signal_use_after_destroy |
| request_context_loss |
| rag_silent_failure |
| debug_false_truth |
| startup_ordering |
| degraded_mode_failure |
| contract_schema_drift |
| metrics_false_success |
| tool_failure_visibility |
| optional_dependency_missing |

**Erlaubte Werte classification.subsystem** (aus QA_RISK_RADAR):

| Wert |
|------|
| Chat |
| Agentensystem |
| Prompt-System |
| RAG |
| Debug/EventBus |
| Metrics |
| Startup/Bootstrap |
| Tools |
| Provider/Ollama |
| Persistenz/SQLite |

**Erlaubte Werte classification.severity:**

| Wert | Bedeutung |
|------|------------|
| critical | App crasht, Datenverlust, nicht nutzbar |
| high | Kernfunktion ausgefallen, Workaround nötig |
| medium | Deutlich beeinträchtigt, aber nutzbar |
| low | Kleiner Fehler, Randfall |
| cosmetic | Nur optisch, keine Funktionsbeeinträchtigung |

**Erlaubte Werte classification.priority:**

| Wert | Bedeutung |
|------|------------|
| P0 | Sofort beheben |
| P1 | Nächster Sprint |
| P2 | Geplant, mittlere Dringlichkeit |
| P3 | Backlog, niedrige Dringlichkeit |

---

### 3.6 behavior

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| behavior.description | **ja** | string | Was ist passiert? Reproduzierbar beschreiben. |
| behavior.expected | **ja** | string | Was hätte passieren sollen? |
| behavior.actual | **ja** | string | Was ist tatsächlich passiert? |
| behavior.repro_steps | **ja** | string[] | Schritte zur Reproduktion, min. 1 Eintrag |
| behavior.reproducibility | **ja** | enum | Siehe Tabelle behavior.reproducibility |
| behavior.impact | nein | string | Nutzerauswirkung |

**Erlaubte Werte behavior.reproducibility:**

| Wert | Bedeutung |
|------|------------|
| always | Jederzeit reproduzierbar |
| intermittent | Gelegentlich, unter bestimmten Bedingungen |
| once | Einmalig beobachtet, nicht wieder reproduziert |
| unknown | Noch nicht versucht |
| requires_specific_state | Nur mit speziellem Zustand reproduzierbar |

---

### 3.7 evidence

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| evidence.refs | nein | object[] | Referenzen auf evidence/ |
| evidence.refs[].file | – | string | Dateiname relativ zu evidence/ |
| evidence.refs[].type | – | enum | screenshot, log, stacktrace, event_log, config, other |
| evidence.refs[].description | nein | string | Kurzbeschreibung |

---

### 3.8 analysis

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| analysis.root_cause | nein | string | Bekannte oder vermutete Ursache |
| analysis.affected_components | nein | string[] | Betroffene Module/Dateien (Pfade) |
| analysis.related_incidents | nein | string[] | Verwandte Incident-IDs (INC-...) |
| analysis.notes | nein | string | Freie Notizen |

---

### 3.9 resolution

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| resolution.fix | nein | string | Beschreibung des Fixes |
| resolution.fix_commit | nein | string | Commit-Referenz (Hash, Tag) |
| resolution.resolved_at | nein | datetime | ISO 8601 |
| resolution.verified | nein | boolean | Fix verifiziert? |
| resolution.waived | nein | boolean | Regression-Pflicht ausnahmsweise aufgehoben (nur mit Begründung in notes.md, G6) |

---

### 3.10 qa

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| qa.status | **ja** | enum | Siehe Tabelle qa.status |
| qa.replay_id | nein | string | Pattern: REPLAY-INC-YYYYMMDD-NNN |
| qa.regression_test | nein | string | Pfad zum Test (z.B. tests/failure_modes/test_foo.py::test_bar) |
| qa.guarded | nein | boolean | Durch Test abgesichert? |
| qa.duplicate_of | Pflicht bei duplicate | string | Referenz auf kanonischen Incident (INC-YYYYMMDD-NNN) |
| qa.status_reason | Pflicht bei invalid/archived | string | Begründung für Status (oder in notes.md) |

**Erlaubte Werte qa.status:**

| Wert | Bedeutung |
|------|------------|
| new | Neu erfasst, unvollständig |
| triaged | Erste Bewertung erfolgt |
| classified | Fehlerklasse, Subsystem zugeordnet |
| replay_defined | replay.yaml existiert |
| replay_verified | Replay manuell bestätigt |
| bound_to_regression | Test existiert, in Catalog |
| closed | Erfolgreich abgeschlossen |
| invalid | Kein gültiger Bug |
| duplicate | Duplikat eines anderen Incidents |
| archived | Archiviert |

**Governance:** Bei status=duplicate muss qa.duplicate_of gesetzt sein. Bei status=invalid oder archived muss Begründung in qa.status_reason oder notes.md stehen.

---

## 4. Pflichtfeld-Checkliste

| Sektion | Pflichtfelder |
|---------|---------------|
| Top-Level | schema_version |
| identity | id, title, created, updated, source |
| detection | when, how |
| environment | runtime_layer |
| classification | failure_class, subsystem, severity, priority |
| behavior | description, expected, actual, repro_steps, reproducibility |
| qa | status |

---

## 5. Validierungsregeln

| Regel | Beschreibung |
|-------|--------------|
| V1 | identity.id muss dem Verzeichnisnamen entsprechen |
| V2 | classification.failure_class muss in REGRESSION_CATALOG existieren |
| V3 | classification.subsystem muss in QA_RISK_RADAR existieren |
| V4 | evidence.refs[].file muss unter evidence/ existieren |
| V5 | qa.replay_id muss auf existierendes replay.yaml verweisen |
| V6 | identity.updated >= identity.created |

---

## 6. Beispiel (Minimal)

```yaml
schema_version: "1.0"

identity:
  id: INC-20260315-001
  title: "RAG-Fehler nicht in Timeline sichtbar"
  created: "2026-03-15T10:00:00Z"
  updated: "2026-03-15T10:00:00Z"
  source: development

detection:
  when: "2026-03-15T09:30:00Z"
  how: manual

environment:
  runtime_layer: cross_layer

classification:
  failure_class: rag_silent_failure
  subsystem: RAG
  severity: medium
  priority: P1

behavior:
  description: "ChromaDB unreachable, Chat läuft weiter, kein RAG_RETRIEVAL_FAILED in Timeline sichtbar."
  expected: "RAG_RETRIEVAL_FAILED Event in Debug-Timeline sichtbar."
  actual: "Kein Event sichtbar."
  repro_steps:
    - "1. ChromaDB stoppen"
    - "2. App starten, Chat öffnen, RAG aktivieren"
    - "3. Nachricht senden"
    - "4. Debug-Panel, Timeline prüfen"
  reproducibility: always

qa:
  status: classified
  replay_id: REPLAY-INC-20260315-001
```

---

## 7. Template

**Vorlage:** [incidents/templates/incident.template.yaml](incidents/templates/incident.template.yaml)

---

## 8. Verweise

| Dokument | Inhalt |
|----------|--------|
| [QA_INCIDENT_REPLAY_ARCHITECTURE.md](QA_INCIDENT_REPLAY_ARCHITECTURE.md) | Überblicksarchitektur |
| [QA_INCIDENT_LIFECYCLE.md](QA_INCIDENT_LIFECYCLE.md) | Lifecycle, qa.status, G6 (regression_required) |
| [incidents/templates/incident.template.yaml](incidents/templates/incident.template.yaml) | Verbindliche Vorlage |
| [REGRESSION_CATALOG.md](REGRESSION_CATALOG.md) | Fehlerklassen |
| [QA_RISK_RADAR.md](QA_RISK_RADAR.md) | Subsysteme |

---

*QA Incident Schema – verbindlich ab 15. März 2026.*
