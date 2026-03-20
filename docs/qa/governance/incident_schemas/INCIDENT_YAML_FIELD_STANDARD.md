# incident.yaml – Verbindlicher Feldstandard

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Vollständiger Feldkatalog für incident.yaml im QA Incident Replay System.

---

## 1. Sektionsübersicht

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

## 2. Vollständiger Feldkatalog

### 2.1 schema_version (Top-Level)

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **schema_version** | Ermöglicht Schema-Migration und Validierung. Jede incident.yaml MUSS dieses Feld enthalten. | **ja** | `"1.0"` (aktuell) |

---

### 2.2 identity

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **identity.id** | Eindeutige Incident-ID. Muss mit Verzeichnisnamen übereinstimmen. | **ja** | Pattern: `INC-YYYYMMDD-NNN` |
| **identity.title** | Kurzbeschreibung für Übersichten und Suche. | **ja** | String, max. 80 Zeichen |
| **identity.created** | Zeitpunkt der Erfassung. | **ja** | ISO 8601 (z.B. `2026-03-15T10:00:00Z`) |
| **identity.updated** | Zeitpunkt der letzten Änderung. | **ja** | ISO 8601 |
| **identity.source** | Herkunft des Incidents. | **ja** | Siehe Regeln unten |
| **identity.reporter** | Wer hat den Vorfall erfasst? | nein | String (Name, Team, System) |

**Regeln identity:**
- `identity.id` = Verzeichnisname (z.B. `INC-20260315-001`)
- `identity.updated` ≥ `identity.created`

---

### 2.3 detection

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **detection.when** | Wann wurde der Vorfall beobachtet? | **ja** | ISO 8601 oder Datum |
| **detection.how** | Wie wurde er erkannt? (manuell, Test, Monitoring) | **ja** | Siehe Regeln unten |
| **detection.context** | Zusätzlicher Kontext (z.B. „während Release-Test“). | nein | String |

**Erlaubte Werte detection.how:**

| Wert | Bedeutung |
|------|-----------|
| `manual` | Manuell durch Nutzer/Entwickler beobachtet |
| `test_failure` | Durch fehlgeschlagenen Test erkannt |
| `ci_failure` | In CI-Pipeline erkannt |
| `monitoring` | Durch Monitoring/Alerting erkannt |
| `audit` | Im Rahmen eines Audits identifiziert |
| `regression` | Bei Regressionstest reproduziert |
| `other` | Sonstiges (in context erläutern) |

---

### 2.4 environment

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **environment.runtime_layer** | Welche Laufzeit-Schicht war betroffen? | **ja** | Siehe Regeln unten |
| **environment.platform** | Betriebssystem/Plattform. | nein | String (z.B. `Linux`, `Ubuntu 24.04`) |
| **environment.python_version** | Python-Version. | nein | String (z.B. `3.12`) |
| **environment.dependencies** | Relevante Abhängigkeiten (Ollama, ChromaDB, etc.). | nein | Liste von Strings |
| **environment.config** | Relevante Konfiguration (z.B. `.env`-Ausschnitt). | nein | Mapping oder String |
| **environment.notes** | Freie Notizen zur Umgebung. | nein | String |

**Erlaubte Werte environment.runtime_layer:**

| Wert | Bedeutung |
|------|-----------|
| `ui` | UI-Schicht (PySide6, Widgets, Signale) |
| `service` | Service-Schicht (Chat, RAG, Agent, Provider) |
| `persistence` | Persistenz (SQLite, ChromaDB) |
| `integration` | Integration mehrerer Schichten |
| `startup` | Startup/Bootstrap |
| `observability` | Debug, EventBus, Metrics |
| `cross_layer` | Übergreifend (UI↔Service↔Persistenz) |
| `other` | Sonstiges (in notes erläutern) |

---

### 2.5 classification

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **classification.failure_class** | Fehlerklasse aus REGRESSION_CATALOG. | **ja** | Siehe Regeln unten |
| **classification.subsystem** | Betroffenes Subsystem aus QA_RISK_RADAR. | **ja** | Siehe Regeln unten |
| **classification.severity** | Auswirkung auf Nutzer/System. | **ja** | Siehe Regeln unten |
| **classification.priority** | QA-Priorität für Bearbeitung. | **ja** | Siehe Regeln unten |
| **classification.tags** | Zusätzliche Tags für Filterung. | nein | Liste von Strings |

**Erlaubte Werte classification.failure_class** (aus REGRESSION_CATALOG):

| Wert | Bedeutung |
|------|-----------|
| `ui_state_drift` | UI-Zustand weicht von Backend ab |
| `async_race` | Race Condition in async/Event-Loop |
| `late_signal_use_after_destroy` | Signal auf zerstörtes Widget |
| `request_context_loss` | Request-Kontext geht verloren |
| `rag_silent_failure` | RAG-Fehler wird nicht sichtbar |
| `debug_false_truth` | Debug-Panel zeigt Falsches |
| `startup_ordering` | Falsche Initialisierungsreihenfolge |
| `degraded_mode_failure` | Degraded Mode bricht App |
| `contract_schema_drift` | Schema/Struktur geändert |
| `metrics_false_success` | Metrics zählen falsch |
| `tool_failure_visibility` | Tool-Fehler nicht sichtbar |
| `optional_dependency_missing` | Optionale Dependency fehlt |

**Erlaubte Werte classification.subsystem** (aus QA_RISK_RADAR):

| Wert |
|------|
| `Chat` |
| `Agentensystem` |
| `Prompt-System` |
| `RAG` |
| `Debug/EventBus` |
| `Metrics` |
| `Startup/Bootstrap` |
| `Tools` |
| `Provider/Ollama` |
| `Persistenz/SQLite` |

**Erlaubte Werte classification.severity:**

| Wert | Bedeutung |
|------|-----------|
| `critical` | App crasht, Datenverlust, nicht nutzbar |
| `high` | Kernfunktion ausgefallen, Workaround nötig |
| `medium` | Deutlich beeinträchtigt, aber nutzbar |
| `low` | Kleiner Fehler, Randfall |
| `cosmetic` | Nur optisch, keine Funktionsbeeinträchtigung |

**Erlaubte Werte classification.priority:**

| Wert | Bedeutung |
|------|-----------|
| `P0` | Sofort beheben |
| `P1` | Nächster Sprint |
| `P2` | Geplant, mittlere Dringlichkeit |
| `P3` | Backlog, niedrige Dringlichkeit |

---

### 2.6 behavior

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **behavior.description** | Was ist passiert? Reproduzierbar beschreiben. | **ja** | String (mehrzeilig) |
| **behavior.expected** | Was hätte passieren sollen? | **ja** | String (mehrzeilig) |
| **behavior.actual** | Was ist tatsächlich passiert? | **ja** | String (mehrzeilig) |
| **behavior.repro_steps** | Schritte zur Reproduktion (wie beobachtet). | **ja** | Liste von Strings, min. 1 |
| **behavior.reproducibility** | Wie zuverlässig reproduzierbar? | **ja** | Siehe Regeln unten |
| **behavior.impact** | Kurze Beschreibung der Nutzerauswirkung. | nein | String |

**Erlaubte Werte behavior.reproducibility:**

| Wert | Bedeutung |
|------|-----------|
| `always` | Jederzeit reproduzierbar |
| `intermittent` | Gelegentlich, unter bestimmten Bedingungen |
| `once` | Einmalig beobachtet, nicht wieder reproduziert |
| `unknown` | Noch nicht versucht |
| `requires_specific_state` | Nur mit speziellem Zustand reproduzierbar |

---

### 2.7 evidence

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **evidence.refs** | Referenzen auf Dateien in evidence/. | nein | Liste von Objekten |
| **evidence.refs[].file** | Dateiname relativ zu evidence/. | – | String (z.B. `screenshot_001.png`) |
| **evidence.refs[].type** | Art des Belegs. | – | `screenshot`, `log`, `stacktrace`, `event_log`, `config`, `other` |
| **evidence.refs[].description** | Kurzbeschreibung. | nein | String |

---

### 2.8 analysis

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **analysis.root_cause** | Bekannte oder vermutete Ursache. | nein | String (mehrzeilig) |
| **analysis.affected_components** | Betroffene Module/Dateien. | nein | Liste von Strings (Pfade) |
| **analysis.related_incidents** | Verwandte Incident-IDs. | nein | Liste von Strings (INC-...) |
| **analysis.notes** | Freie Analyse-Notizen. | nein | String |

---

### 2.9 resolution

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **resolution.fix** | Beschreibung des Fixes. | nein | String (mehrzeilig) |
| **resolution.fix_commit** | Commit-Referenz (Hash, Tag). | nein | String |
| **resolution.resolved_at** | Zeitpunkt der Behebung. | nein | ISO 8601 |
| **resolution.verified** | Wurde der Fix verifiziert? | nein | Boolean |

---

### 2.10 qa

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **qa.status** | Lifecycle-Status des Incidents. | **ja** | Siehe Regeln unten |
| **qa.replay_id** | ID des zugehörigen Replay-Szenarios. | nein | Pattern: `REPLAY-INC-YYYYMMDD-NNN` |
| **qa.regression_test** | Pfad zum Regressionstest (falls vorhanden). | nein | String (z.B. `tests/failure_modes/test_foo.py::test_bar`) |
| **qa.guarded** | Ist der Incident durch Test abgesichert? | nein | Boolean (abgeleitet aus status) |

**Erlaubte Werte qa.status:** Siehe [QA_INCIDENT_REPLAY_LIFECYCLE.md](QA_INCIDENT_REPLAY_LIFECYCLE.md)

| Wert | Bedeutung |
|------|-----------|
| `new` | Neu erfasst, unvollständig |
| `triaged` | Erste Bewertung erfolgt |
| `classified` | Fehlerklasse, Subsystem zugeordnet |
| `replay_defined` | replay.yaml existiert |
| `replay_verified` | Replay manuell bestätigt |
| `bound_to_regression` | Test existiert, in Catalog |
| `closed` | Erfolgreich abgeschlossen |
| `invalid` | Kein gültiger Bug |
| `duplicate` | Duplikat eines anderen Incidents |
| `archived` | Archiviert |

---

## 3. Erlaubte Werte identity.source

| Wert | Bedeutung |
|------|-----------|
| `production` | In Produktion beobachtet |
| `staging` | In Staging/Testumgebung |
| `development` | Während Entwicklung |
| `manual` | Manuell reproduziert |
| `audit` | Im Audit identifiziert |
| `regression` | Bei Regressionstest |
| `other` | Sonstiges (in reporter/context erläutern) |

---

## 4. Regeln für kontrollierte Felder

### 4.1 severity

| Regel | Beschreibung |
|-------|--------------|
| **S1** | `critical` nur bei App-Crash, Datenverlust oder vollständiger Nutzungsunfähigkeit. |
| **S2** | `high` bei Ausfall einer Kernfunktion (Chat, Agent, RAG). |
| **S3** | `medium` bei deutlicher Beeinträchtigung mit Workaround. |
| **S4** | `low` und `cosmetic` für Randfälle und optische Mängel. |
| **S5** | severity ist objektiv (Auswirkung), priority ist subjektiv (Dringlichkeit). |

### 4.2 priority

| Regel | Beschreibung |
|-------|--------------|
| **P1** | P0 nur für Blocker (Release blockiert, kritischer Bug). |
| **P2** | P1 für Bugs, die im nächsten Sprint behoben werden sollen. |
| **P3** | P2/P3 für Backlog-Items. |
| **P4** | priority kann unabhängig von severity gesetzt werden (z.B. low severity, P1 priority bei Kundenrelevanz). |

### 4.3 status

| Regel | Beschreibung |
|-------|--------------|
| **ST1** | `draft` → `captured`: Alle Pflichtfelder vollständig, repro_steps validiert. |
| **ST2** | `captured` → `replay_created`: replay.yaml existiert und ist verknüpft. |
| **ST3** | `replay_created` → `replay_validated`: Replay manuell ausgeführt, Bug reproduziert. |
| **ST4** | `replay_validated` → `test_bound`: Test geschrieben oder existierender zugeordnet. |
| **ST5** | `test_bound` → `guarded`: Test in CI, letzter Lauf grün. |
| **ST6** | Rückwärts zu `draft` jederzeit erlaubt (Korrektur). |

### 4.4 failure_class

| Regel | Beschreibung |
|-------|--------------|
| **FC1** | Muss eine gültige ID aus REGRESSION_CATALOG sein. |
| **FC2** | Neue Fehlerklasse: Zuerst REGRESSION_CATALOG erweitern, dann verwenden. |
| **FC3** | Ein Incident hat genau eine failure_class. |

### 4.5 reproducibility

| Regel | Beschreibung |
|-------|--------------|
| **R1** | `always` nur wenn mindestens 3x erfolgreich reproduziert. |
| **R2** | `intermittent` erfordert Angabe der Bedingungen in behavior.description oder analysis.notes. |
| **R3** | `once` und `unknown` → status sollte `draft` bleiben bis Reproduktion bestätigt. |
| **R4** | `requires_specific_state` → fixtures/ nutzen für Replay. |

### 4.6 runtime_layer

| Regel | Beschreibung |
|-------|--------------|
| **RL1** | Primär betroffene Schicht. Bei mehreren: die tiefste/ursächliche. |
| **RL2** | `cross_layer` wenn der Bug die Grenze zwischen Schichten betrifft (z.B. UI↔Service). |
| **RL3** | `integration` wenn mehrere Schichten gemeinsam betroffen sind. |
| **RL4** | `startup` nur für Bootstrap/Init-Probleme. |

---

## 5. Empfohlene Beispielstruktur

```yaml
schema_version: "1.0"

identity:
  id: INC-20260315-001
  title: "RAG-Fehler nicht in Timeline sichtbar"
  created: "2026-03-15T10:00:00Z"
  updated: "2026-03-15T10:00:00Z"
  source: development
  reporter: "QA Team"

detection:
  when: "2026-03-15T09:30:00Z"
  how: manual
  context: "Während manueller Chat-Tests mit RAG aktiv"

environment:
  runtime_layer: cross_layer
  platform: "Ubuntu 24.04"
  python_version: "3.12"
  dependencies:
    - "ChromaDB"
    - "Ollama"
  notes: "ChromaDB war temporär nicht erreichbar"

classification:
  failure_class: rag_silent_failure
  subsystem: RAG
  severity: medium
  priority: P1
  tags:
    - "debug"
    - "visibility"

behavior:
  description: |
    Bei deaktiviertem ChromaDB wurde eine Chat-Anfrage mit RAG aktiv gestellt.
    Der Chat lief weiter, aber es wurde kein RAG_RETRIEVAL_FAILED Event
    in der Debug-Timeline angezeigt.
  expected: |
    RAG_RETRIEVAL_FAILED Event sollte emittiert und in der Timeline sichtbar sein.
  actual: |
    Kein Event in der Timeline. Nutzer weiß nicht, dass RAG fehlgeschlagen ist.
  repro_steps:
    - "1. ChromaDB stoppen oder unreachable machen"
    - "2. App starten, Chat öffnen"
    - "3. RAG aktivieren, Nachricht senden"
    - "4. Debug-Panel öffnen, Timeline prüfen"
  reproducibility: always
  impact: "Nutzer erhält keine Rückmeldung bei RAG-Fehler"

evidence:
  refs:
    - file: "timeline_screenshot.png"
      type: screenshot
      description: "Timeline ohne RAG_RETRIEVAL_FAILED"
    - file: "event_log.txt"
      type: event_log
      description: "EventBus-Log ohne RAG-Event"

analysis:
  root_cause: "RAG-Service fängt Exception, emittiert kein Event"
  affected_components:
    - "app/rag/rag_service.py"
    - "app/debug/event_bus.py"
  notes: "Verknüpfung mit debug_false_truth möglich"

resolution:
  fix: "RAG_RETRIEVAL_FAILED Event in rag_service emittieren"
  fix_commit: "abc1234"
  resolved_at: "2026-03-15T14:00:00Z"
  verified: true

qa:
  status: replay_created
  replay_id: REPLAY-INC-20260315-001
  regression_test: "tests/failure_modes/test_rag_retrieval_failure.py::test_rag_failure_emits_event"
  guarded: false
```

---

## 6. Pflichtfeld-Checkliste

| Sektion | Pflichtfelder |
|---------|---------------|
| Top-Level | `schema_version` |
| identity | `id`, `title`, `created`, `updated`, `source` |
| detection | `when`, `how` |
| environment | `runtime_layer` |
| classification | `failure_class`, `subsystem`, `severity`, `priority` |
| behavior | `description`, `expected`, `actual`, `repro_steps`, `reproducibility` |
| qa | `status` |

**Optionale Sektionen:** evidence, analysis, resolution (können ganz fehlen).

---

## 7. Validierungsregeln

| Regel | Beschreibung |
|-------|--------------|
| **V1** | `identity.id` muss dem Verzeichnisnamen entsprechen. |
| **V2** | `classification.failure_class` muss in REGRESSION_CATALOG existieren. |
| **V3** | `classification.subsystem` muss in QA_RISK_RADAR existieren. |
| **V4** | `evidence.refs[].file` muss unter evidence/ existieren. |
| **V5** | `qa.replay_id` muss auf existierendes replay.yaml verweisen. |
| **V6** | `identity.updated` >= `identity.created`. |

---

*Incident YAML Feldstandard – verbindlich ab 15. März 2026.*
