# replay.yaml – Verbindlicher Feldstandard

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Deklarativer Reproduktionsvertrag – kein Testcode, kein pytest. Spezifikation, was reproduziert und geprüft werden soll.

---

## 1. Grundprinzip: Deklarativ vor Testcode

### 1.1 Was replay.yaml ist

- **Reproduktionsvertrag:** Vereinbarung zwischen Incident und künftigem Test
- **Spezifikation:** Was muss passieren? Was muss gelten? Wie erkennt man Erfolg/Fehler?
- **Plattformunabhängig:** Kein pytest, kein Python – nur Struktur und Semantik

### 1.2 Was replay.yaml NICHT ist

- **Kein Testcode:** Keine Assertions, keine Fixtures im Code-Sinne
- **Kein pytest-Test:** Kein `def test_...`, kein `assert`
- **Kein Runner:** replay.yaml beschreibt; ein (zukünftiger) Runner führt aus

### 1.3 Begründung: Warum deklarativ vor Testcode?

| Aspekt | Begründung |
|--------|------------|
| **Trennung von Spezifikation und Implementierung** | Der Vertrag (was) bleibt stabil; die Testimplementierung (wie) kann wechseln (pytest, unittest, eigener Runner). |
| **Reviewbarkeit** | QA, Architekten und Entwickler können den Vertrag prüfen, ohne Testcode zu lesen. |
| **Governance** | Replay-Verträge sind maschinenlesbar – Priorisierung, Abdeckung, Risikoachsen können automatisch aggregiert werden. |
| **Wiederverwendbarkeit** | Ein Vertrag kann von verschiedenen Testframeworks oder manuellen Checklisten umgesetzt werden. |
| **Auditierbarkeit** | Der Vertrag dokumentiert die Absicht; der Test dokumentiert die Umsetzung. Beide können abgeglichen werden. |
| **Langlebigkeit** | Code ändert sich; eine deklarative Spezifikation überlebt Refactorings besser. |

---

## 2. Sektionsübersicht

| Sektion | Zweck | Pflicht |
|---------|-------|---------|
| **schema_version** | Schema-Version für Validierung | ja |
| **identity** | Replay-Identität, Verknüpfung zum Incident | ja |
| **replay_type** | Art des Replay-Szenarios | ja |
| **preconditions** | Vorbedingungen vor der Ausführung | ja |
| **fixtures** | Referenzen auf Vorlagen in fixtures/ | nein |
| **execution** | Ausführungsschritte | ja |
| **assertion_contract** | Was muss nach dem Replay gelten? | ja |
| **observability_contract** | Was muss sichtbar/beobachtbar sein? | ja |
| **determinism** | Hinweise zu Determiniertheit | ja |
| **mapping** | Testdomänen, Risikoachsen | ja |
| **verification** | Verifikationsstatus | ja |

---

## 3. Vollständiger Feldkatalog

### 3.1 schema_version (Top-Level)

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **schema_version** | Schema-Version für Validierung und Migration. | **ja** | `"1.0"` |

---

### 3.2 identity

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **identity.id** | Eindeutige Replay-ID. | **ja** | Pattern: `REPLAY-INC-YYYYMMDD-NNN` |
| **identity.incident_id** | Referenz auf den zugehörigen Incident. | **ja** | Pattern: `INC-YYYYMMDD-NNN` |
| **identity.title** | Kurzbeschreibung des Replay-Szenarios. | **ja** | String, max. 80 Zeichen |
| **identity.created** | Zeitpunkt der Erstellung. | **ja** | ISO 8601 |
| **identity.updated** | Zeitpunkt der letzten Änderung. | **ja** | ISO 8601 |

**Regel:** `identity.id` muss zu `identity.incident_id` passen (REPLAY-INC-xxx ↔ INC-xxx).

---

### 3.3 replay_type

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **replay_type.type** | Art des Replay-Szenarios. | **ja** | Siehe Tabelle unten |
| **replay_type.description** | Kurze Erläuterung des Typs in diesem Kontext. | nein | String |

**Erlaubte Werte replay_type.type:**

| Wert | Bedeutung | Beispiel |
|------|------------|----------|
| `startup_dependency_failure` | Optionale Abhängigkeit fehlt oder unreachable beim Start | ChromaDB Import fehlschlägt, Ollama nicht erreichbar |
| `provider_unreachable` | Externer Provider (Ollama, API) nicht erreichbar | Ollama offline, Timeout |
| `fault_injection` | Gezielte Störung während Laufzeit | ChromaDB Connection Error, Provider Delay |
| `event_contract_drift` | Event/Schema passt nicht zu Erwartung | Neuer EventType ohne Registry, falsches Format |
| `state_sequence` | Bestimmte Abfolge von Zuständen/Aktionen | Send → Cancel → Send (Race) |
| `cross_layer` | Übergreifend UI↔Service↔Persistenz | Prompt anwenden, Request nutzt falschen Kontext |
| `async_race` | Async/Race-Condition | Signal nach Widget-Destroy |
| `hybrid` | Kombination mehrerer Typen | Startup mit degradiertem RAG + Chat-Aktion |

---

### 3.4 preconditions

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **preconditions.system** | Systemzustand vor dem Replay. | **ja** | Liste von Strings |
| **preconditions.external** | Externe Bedingungen (Dienste, Netzwerk). | nein | Liste von Strings |
| **preconditions.config** | Erforderliche Konfiguration. | nein | Mapping oder Liste |
| **preconditions.notes** | Zusätzliche Vorbedingungen. | nein | String |

**Beispiel:** `system: ["App nicht gestartet", "ChromaDB nicht installiert"]`

---

### 3.5 fixtures

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **fixtures.refs** | Referenzen auf Dateien in fixtures/. | nein | Liste von Objekten |
| **fixtures.refs[].file** | Dateiname relativ zu fixtures/. | – | String |
| **fixtures.refs[].purpose** | Zweck der Fixture (z.B. initial state, mock data). | nein | String |
| **fixtures.refs[].format** | Format der Fixture. | nein | `json`, `yaml`, `sqlite`, `binary`, `other` |

---

### 3.6 execution

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **execution.steps** | Ausführungsschritte in Reihenfolge. | **ja** | Liste von Objekten |
| **execution.steps[].id** | Schritt-ID (z.B. S1, S2). | **ja** | String |
| **execution.steps[].action** | Was wird ausgeführt? | **ja** | String |
| **execution.steps[].actor** | Wer führt aus? (app, user, system, injector). | nein | String |
| **execution.steps[].trigger** | Auslöser (z.B. user_click, timeout, fault). | nein | String |
| **execution.steps[].notes** | Zusätzliche Hinweise. | nein | String |
| **execution.ordering** | Sind die Schritte strikt sequentiell? | nein | `sequential`, `parallel_allowed`, `timing_sensitive` |

**Erlaubte Werte execution.steps[].actor:**

| Wert | Bedeutung |
|------|------------|
| `app` | Die Anwendung selbst (z.B. Startup) |
| `user` | Nutzeraktion (Klick, Eingabe) |
| `system` | Systemaktion (z.B. Netzwerk unterbrechen) |
| `injector` | Fault-Injection (Stub, Mock, Delay) |

---

### 3.7 assertion_contract

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **assertion_contract.success** | Was muss gelten, wenn der Replay „erfolgreich“ (Bug behoben) ist? | **ja** | Liste von Strings |
| **assertion_contract.failure** | Was gilt, wenn der Bug noch besteht? (Fehlerindikator) | **ja** | Liste von Strings |
| **assertion_contract.invariant** | Invarianten, die immer gelten müssen. | nein | Liste von Strings |
| **assertion_contract.no_crash** | Explizit: Kein Crash erlaubt. | nein | Boolean (default: true) |

**Semantik:** Ein Replay ist „bestanden“, wenn alle `success`-Bedingungen erfüllt und keine `failure`-Bedingung erfüllt ist.

---

### 3.8 observability_contract

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **observability_contract.events** | Welche Events müssen emittiert werden (oder fehlen)? | nein | Liste von Objekten |
| **observability_contract.events[].type** | EventType (z.B. RAG_RETRIEVAL_FAILED). | – | String |
| **observability_contract.events[].expected** | `present` oder `absent`. | – | String |
| **observability_contract.events[].in_timeline** | Muss in Debug-Timeline sichtbar sein? | nein | Boolean |
| **observability_contract.ui_state** | Erwarteter UI-Zustand (z.B. „Chat-Widget sichtbar“). | nein | Liste von Strings |
| **observability_contract.debug_visibility** | Was muss im Debug-Panel sichtbar sein? | nein | Liste von Strings |
| **observability_contract.notes** | Zusätzliche Beobachtbarkeitsanforderungen. | nein | String |

---

### 3.9 determinism

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **determinism.level** | Wie deterministisch ist der Replay? | **ja** | Siehe Tabelle unten |
| **determinism.nondeterminism_sources** | Quellen von Nichtdeterminiertheit. | nein | Liste von Strings |
| **determinism.mitigation** | Wie wird Nichtdeterminiertheit adressiert? | nein | String |
| **determinism.isolated** | Kann ohne Live-Dienste (Ollama, ChromaDB) ausgeführt werden? | **ja** | Boolean |

**Erlaubte Werte determinism.level:**

| Wert | Bedeutung |
|------|------------|
| `fully_deterministic` | Immer gleiches Ergebnis bei gleichen Vorbedingungen |
| `deterministic_with_mocks` | Deterministisch mit Mocks/Stubs, nicht mit echten Diensten |
| `timing_sensitive` | Ergebnis kann von Timing abhängen (z.B. async) |
| `intermittent` | Gelegentlich unterschiedliches Ergebnis |
| `environment_dependent` | Abhängig von Umgebung (Netzwerk, Dienste) |

---

### 3.10 mapping

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **mapping.test_domains** | Testdomänen, die diesen Replay abdecken (sollten). | **ja** | Liste von Strings |
| **mapping.risk_axes** | Risikoachsen aus QA_HEATMAP. | **ja** | Liste von Strings |
| **mapping.pytest_markers** | Empfohlene pytest-Marker. | nein | Liste von Strings |
| **mapping.subsystem** | Betroffenes Subsystem (aus incident). | nein | String |
| **mapping.failure_class** | Fehlerklasse (aus incident). | nein | String |

**Erlaubte Werte mapping.test_domains:**

| Wert | Bedeutung |
|------|------------|
| `failure_modes` | Failure-Injection-Tests |
| `contract` | Contract-Tests |
| `async_behavior` | Async/Race-Tests |
| `cross_layer` | Cross-Layer-Tests |
| `startup` | Startup-Tests |
| `chaos` | Chaos/Fault-Injection |
| `integration` | Integrationstests |
| `state_consistency` | State-Consistency |
| `golden_path` | Golden-Path E2E |
| `regression` | Regressionstests |

**Erlaubte Werte mapping.risk_axes:**

| Wert | Bedeutung |
|------|------------|
| `Failure_Coverage` | Failure-Abdeckung |
| `Contract_Coverage` | Contract-Abdeckung |
| `Async_Coverage` | Async-Abdeckung |
| `Cross_Layer_Coverage` | Cross-Layer-Abdeckung |
| `Drift_Governance_Coverage` | Drift/Governance-Abdeckung |
| `Restrisiko` | Restrisiko |

---

### 3.11 verification

| Feld | Zweck | Pflicht | Erlaubte Werte |
|------|-------|---------|----------------|
| **verification.status** | Verifikationsstatus des Replay. | **ja** | Siehe Abschnitt 4 |
| **verification.verified_at** | Zeitpunkt der letzten Verifikation. | nein | ISO 8601 |
| **verification.verified_by** | Wer hat verifiziert? | nein | String |
| **verification.notes** | Verifikationsnotizen. | nein | String |

---

## 4. Erlaubte Statuswerte für Replay (verification.status)

**Vollständiger Lifecycle:** [QA_INCIDENT_REPLAY_LIFECYCLE.md](QA_INCIDENT_REPLAY_LIFECYCLE.md)

| Status | Bedeutung | Nächste Aktion |
|--------|------------|----------------|
| `draft` | Replay entworfen, nicht validiert | Manuell ausführen, prüfen |
| `validated` | Manuell ausgeführt, Bug reproduziert | Test implementieren |
| `test_bound` | Test existiert, führt Replay aus | In CI integrieren |
| `guarded` | Test in CI, grün | Replay abgeschlossen |
| `obsolete` | Nicht mehr relevant | – (Endzustand) |

**Übergangsregeln:**
- `draft` → `validated`: Manuell reproduziert, assertion_contract.failure erfüllt
- `validated` → `test_bound`: Test geschrieben, Replay abgebildet
- `test_bound` → `guarded`: Test in CI, letzter Lauf erfolgreich
- `*` → `obsolete`: Incident invalid/duplicate/archived oder Replay nicht mehr anwendbar

---

## 5. Pflichtfeld-Checkliste

| Sektion | Pflichtfelder |
|---------|---------------|
| Top-Level | `schema_version` |
| identity | `id`, `incident_id`, `title`, `created`, `updated` |
| replay_type | `type` |
| preconditions | `system` |
| execution | `steps` (mit `id`, `action` pro Schritt) |
| assertion_contract | `success`, `failure` |
| observability_contract | (mindestens eines: events, ui_state, debug_visibility, notes) |
| determinism | `level`, `isolated` |
| mapping | `test_domains`, `risk_axes` |
| verification | `status` |

**Hinweis:** observability_contract ist als Sektion pflicht, der Inhalt kann leer sein. Bei keinen Beobachtbarkeitsanforderungen: `observability_contract: {}` oder `notes: "Keine speziellen Anforderungen"`.

---

## 6. Beispielstrukturen

### 6.1 Startup Dependency Failure

```yaml
schema_version: "1.0"

identity:
  id: REPLAY-INC-20260315-001
  incident_id: INC-20260315-001
  title: "App startet mit fehlendem ChromaDB-Import"
  created: "2026-03-15T11:00:00Z"
  updated: "2026-03-15T11:00:00Z"

replay_type:
  type: startup_dependency_failure
  description: "ChromaDB nicht installiert oder Import schlägt fehl"

preconditions:
  system:
    - "ChromaDB nicht installiert oder chromadb-Paket fehlt"
    - "Oder: ChromaDB-Import wirft ImportError"
  external: []
  notes: "Simuliert optional_dependency_missing"

fixtures: {}

execution:
  steps:
    - id: S1
      action: "App starten (main.py)"
      actor: app
      trigger: startup
    - id: S2
      action: "MainWindow initialisieren, RAG-Service laden"
      actor: app
  ordering: sequential

assertion_contract:
  success:
    - "MainWindow erscheint"
    - "Chat-Widget ist sichtbar und nutzbar"
    - "RAG-Service im degradierten Modus (kein Crash)"
  failure:
    - "App crasht mit ImportError"
    - "MainWindow erscheint nicht"
  no_crash: true

observability_contract:
  events: []
  ui_state:
    - "Chat-Widget sichtbar"
  notes: "Kein RAG_RETRIEVAL_FAILED nötig – RAG gar nicht aktiv"

determinism:
  level: fully_deterministic
  isolated: true
  nondeterminism_sources: []
  notes: "Import-Zeitpunkt ist deterministisch"

mapping:
  test_domains:
    - startup
    - failure_modes
  risk_axes:
    - Failure_Coverage
    - Drift_Governance_Coverage
  pytest_markers:
    - startup
    - failure_mode
  subsystem: "Startup/Bootstrap"
  failure_class: optional_dependency_missing

verification:
  status: validated
  verified_at: "2026-03-15T12:00:00Z"
  notes: "Manuell mit pip uninstall chromadb reproduziert"
```

---

### 6.2 Provider Unreachable

```yaml
schema_version: "1.0"

identity:
  id: REPLAY-INC-20260315-002
  incident_id: INC-20260315-002
  title: "Chat bei unreachable Ollama – Timeout, kein Crash"
  created: "2026-03-15T11:00:00Z"
  updated: "2026-03-15T11:00:00Z"

replay_type:
  type: provider_unreachable
  description: "Ollama nicht erreichbar, Provider antwortet nicht"

preconditions:
  system:
    - "App gestartet, Chat geöffnet"
    - "Ollama-Stub oder -Mock: antwortet nicht / Timeout"
  external:
    - "Ollama nicht laufend oder Netzwerk blockiert"

fixtures:
  refs:
    - file: "ollama_timeout_stub.py"
      purpose: "Stub für Ollama-Provider mit konfigurierbarem Delay"
      format: other

execution:
  steps:
    - id: S1
      action: "Nachricht im Chat eingeben und senden"
      actor: user
      trigger: user_click
    - id: S2
      action: "Provider-Anfrage an Ollama (Timeout)"
      actor: injector
      trigger: fault
    - id: S3
      action: "Warten auf Abbruch oder Timeout"
      actor: app
  ordering: timing_sensitive

assertion_contract:
  success:
    - "Task bricht ab oder zeigt Fehler"
    - "_streaming wird auf false zurückgesetzt"
    - "Zweiter Send ist möglich (kein hängender Zustand)"
  failure:
    - "App hängt"
    - "Zweiter Send blockiert"
    - "Crash bei Timeout"
  no_crash: true

observability_contract:
  events:
    - type: TASK_FAILED
      expected: present
      in_timeline: true
  ui_state:
    - "Send-Button wieder klickbar"
  debug_visibility:
    - "TASK_FAILED in Timeline"

determinism:
  level: deterministic_with_mocks
  isolated: true
  nondeterminism_sources:
    - "Timeout-Dauer (mit Stub konfigurierbar)"
  mitigation: "Stub mit festem Delay"

mapping:
  test_domains:
    - chaos
    - failure_modes
    - async_behavior
  risk_axes:
    - Failure_Coverage
    - Async_Coverage
  pytest_markers:
    - chaos
    - failure_mode
  subsystem: "Provider/Ollama"
  failure_class: contract_schema_drift

verification:
  status: test_bound
  verified_at: "2026-03-15T13:00:00Z"
  notes: "test_provider_timeout_chat.py deckt ab"
```

---

### 6.3 Event Contract Drift

```yaml
schema_version: "1.0"

identity:
  id: REPLAY-INC-20260315-003
  incident_id: INC-20260315-003
  title: "Neuer EventType ohne Registry/Timeline"
  created: "2026-03-15T11:00:00Z"
  updated: "2026-03-15T11:00:00Z"

replay_type:
  type: event_contract_drift
  description: "EventType wird emittiert, aber nicht in Registry/Timeline"

preconditions:
  system:
    - "EventType RAG_RETRIEVAL_FAILED im Code emittiert"
    - "Registry oder Timeline nicht aktualisiert"
  config:
    - "event_type_registry.py: EventType fehlt"
    - "event_timeline_view.py: type_map fehlt"

execution:
  steps:
    - id: S1
      action: "RAG-Fehler auslösen (ChromaDB unreachable)"
      actor: injector
    - id: S2
      action: "Chat mit RAG aktiv senden"
      actor: user
    - id: S3
      action: "Debug-Panel, Timeline öffnen"
      actor: user
  ordering: sequential

assertion_contract:
  success:
    - "RAG_RETRIEVAL_FAILED in Registry"
    - "RAG_RETRIEVAL_FAILED in Timeline sichtbar"
  failure:
    - "Event emittiert, aber nicht in Timeline"
    - "Event fehlt in Registry"
    - "Timeline zeigt 'unknown' oder filtert Event"
  invariant:
    - "Alle emittierten EventTypes in Registry"

observability_contract:
  events:
    - type: RAG_RETRIEVAL_FAILED
      expected: present
      in_timeline: true
  debug_visibility:
    - "RAG_RETRIEVAL_FAILED in Timeline mit korrektem Label"

determinism:
  level: fully_deterministic
  isolated: true

mapping:
  test_domains:
    - contract
    - failure_modes
    - cross_layer
  risk_axes:
    - Contract_Coverage
    - Drift_Governance_Coverage
  pytest_markers:
    - contract
  subsystem: "Debug/EventBus"
  failure_class: debug_false_truth

verification:
  status: guarded
  verified_at: "2026-03-15T14:00:00Z"
  notes: "tests/meta/test_event_type_drift.py"
```

---

### 6.4 ChromaDB Failure

```yaml
schema_version: "1.0"

identity:
  id: REPLAY-INC-20260315-004
  incident_id: INC-20260315-004
  title: "ChromaDB unreachable – RAG-Fehler sichtbar"
  created: "2026-03-15T11:00:00Z"
  updated: "2026-03-15T11:00:00Z"

replay_type:
  type: fault_injection
  description: "ChromaDB-Verbindung schlägt fehl (Netzwerk, nicht Import)"

preconditions:
  system:
    - "App gestartet, ChromaDB installiert"
    - "ChromaDB-Service nicht erreichbar (Connection refused, Timeout)"
  external:
    - "ChromaDB nicht gestartet oder Netzwerk blockiert"

execution:
  steps:
    - id: S1
      action: "Chat öffnen, RAG aktivieren"
      actor: user
    - id: S2
      action: "Nachricht senden (RAG-Retrieval wird ausgelöst)"
      actor: user
    - id: S3
      action: "RAG-Service versucht ChromaDB-Zugriff"
      actor: app
      trigger: fault
  ordering: sequential

assertion_contract:
  success:
    - "Chat läuft weiter (kein Crash)"
    - "RAG_RETRIEVAL_FAILED Event wird emittiert"
    - "Event in Debug-Timeline sichtbar"
    - "Nutzer erhält Hinweis oder leere Kontext-Erweiterung"
  failure:
    - "Exception wird verschluckt, kein Event"
    - "Chat hängt"
    - "Timeline zeigt kein RAG-Fehler-Event"
  no_crash: true

observability_contract:
  events:
    - type: RAG_RETRIEVAL_FAILED
      expected: present
      in_timeline: true
  debug_visibility:
    - "RAG_RETRIEVAL_FAILED in Timeline"

determinism:
  level: deterministic_with_mocks
  isolated: true
  nondeterminism_sources:
    - "Netzwerk-Timing (mit Mock eliminierbar)"
  mitigation: "ChromaDB-Mock mit ConnectionError"

mapping:
  test_domains:
    - failure_modes
    - chaos
  risk_axes:
    - Failure_Coverage
    - Drift_Governance_Coverage
  pytest_markers:
    - failure_mode
    - chaos
  subsystem: RAG
  failure_class: rag_silent_failure

verification:
  status: validated
  verified_at: "2026-03-15T12:30:00Z"
  notes: "test_chroma_unreachable deckt ab"
```

---

## 7. Validierungsregeln

| Regel | Beschreibung |
|-------|---------------|
| **V1** | `identity.incident_id` muss auf existierendes incident.yaml verweisen. |
| **V2** | `identity.id` = `REPLAY-` + `identity.incident_id`. |
| **V3** | `execution.steps` mindestens ein Schritt. |
| **V4** | `assertion_contract.success` und `assertion_contract.failure` nicht leer. |
| **V5** | `mapping.test_domains` und `mapping.risk_axes` nicht leer. |
| **V6** | `fixtures.refs[].file` muss unter fixtures/ existieren (falls angegeben). |

---

*Replay YAML Feldstandard – verbindlich ab 15. März 2026.*
