# QA Replay Schema – replay.yaml Standard

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Deklarativer Reproduktionsvertrag – kein Testcode, kein pytest. Spezifikation, was reproduziert und geprüft werden soll.

---

## 1. Zielbild und Grundprinzip

### 1.1 Was replay.yaml ist

- **Reproduktionsvertrag:** Vereinbarung zwischen Incident und künftigem Test
- **Spezifikation:** Was muss passieren? Was muss gelten? Wie erkennt man Erfolg/Fehler?
- **Plattformunabhängig:** Kein pytest, kein Python – nur Struktur und Semantik

### 1.2 Was replay.yaml NICHT ist

- **Kein Testcode:** Keine Assertions, keine Fixtures im Code-Sinne
- **Kein pytest-Test:** Kein `def test_...`, kein `assert`
- **Kein Runner:** replay.yaml beschreibt; ein (zukünftiger) Runner führt aus

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

### 3.1 schema_version

| Feld | Pflicht | Typ | Erlaubte Werte |
|------|---------|-----|----------------|
| schema_version | **ja** | string | `"1.0"` |

---

### 3.2 identity

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| identity.id | **ja** | string | Pattern: `REPLAY-INC-YYYYMMDD-NNN` |
| identity.incident_id | **ja** | string | Pattern: `INC-YYYYMMDD-NNN` |
| identity.title | **ja** | string | Kurzbeschreibung, max. 80 Zeichen |
| identity.created | **ja** | datetime | ISO 8601 |
| identity.updated | **ja** | datetime | ISO 8601 |

**Regel:** identity.id = `REPLAY-` + identity.incident_id

---

### 3.3 replay_type

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| replay_type.type | **ja** | enum | Siehe Tabelle replay_type.type |
| replay_type.description | nein | string | Erläuterung des Typs in diesem Kontext |

**Erlaubte Werte replay_type.type:**

| Wert | Bedeutung |
|------|------------|
| startup_dependency_failure | Optionale Abhängigkeit fehlt/unreachable beim Start |
| provider_unreachable | Externer Provider (Ollama, API) nicht erreichbar |
| fault_injection | Gezielte Störung während Laufzeit |
| event_contract_drift | Event/Schema passt nicht zu Erwartung |
| state_sequence | Bestimmte Abfolge von Zuständen/Aktionen |
| cross_layer | UI↔Service↔Persistenz |
| async_race | Async/Race-Condition |
| hybrid | Kombination mehrerer Typen |

---

### 3.4 preconditions

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| preconditions.system | **ja** | string[] | Systemzustand vor dem Replay, min. 1 Eintrag |
| preconditions.external | nein | string[] | Externe Bedingungen (Dienste, Netzwerk) |
| preconditions.config | nein | object/string[] | Erforderliche Konfiguration |
| preconditions.notes | nein | string | Zusätzliche Vorbedingungen |

---

### 3.5 fixtures

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| fixtures.refs | nein | object[] | Referenzen auf fixtures/ |
| fixtures.refs[].file | – | string | Dateiname relativ zu fixtures/ |
| fixtures.refs[].purpose | nein | string | Zweck (initial state, mock data) |
| fixtures.refs[].format | nein | enum | json, yaml, sqlite, binary, other |

---

### 3.6 execution

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| execution.steps | **ja** | object[] | Ausführungsschritte in Reihenfolge, min. 1 |
| execution.steps[].id | **ja** | string | Schritt-ID (z.B. S1, S2) |
| execution.steps[].action | **ja** | string | Was wird ausgeführt? |
| execution.steps[].actor | nein | enum | Siehe Tabelle execution.steps[].actor |
| execution.steps[].trigger | nein | string | user_click, timeout, fault, startup, … |
| execution.steps[].notes | nein | string | Zusätzliche Hinweise |
| execution.ordering | nein | enum | Siehe Tabelle execution.ordering |

**Erlaubte Werte execution.steps[].actor:**

| Wert | Bedeutung |
|------|------------|
| app | Die Anwendung selbst (z.B. Startup) |
| user | Nutzeraktion (Klick, Eingabe) |
| system | Systemaktion (z.B. Netzwerk unterbrechen) |
| injector | Fault-Injection (Stub, Mock, Delay) |

**Erlaubte Werte execution.ordering:**

| Wert | Bedeutung |
|------|------------|
| sequential | Schritte strikt nacheinander |
| parallel_allowed | Parallele Ausführung erlaubt |
| timing_sensitive | Ergebnis kann von Timing abhängen |

---

### 3.7 assertion_contract

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| assertion_contract.success | **ja** | string[] | Was muss gelten, wenn Bug behoben? (Erfolgskriterien) |
| assertion_contract.failure | **ja** | string[] | Fehlerindikator – was gilt, wenn Bug besteht? |
| assertion_contract.invariant | nein | string[] | Invarianten, die immer gelten müssen |
| assertion_contract.no_crash | nein | boolean | Kein Crash erlaubt (default: true) |

**Semantik:** Replay ist „bestanden“, wenn alle success erfüllt und keine failure erfüllt ist.

---

### 3.8 observability_contract

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| observability_contract.events | nein | object[] | Welche Events müssen emittiert werden? |
| observability_contract.events[].type | – | string | EventType (z.B. RAG_RETRIEVAL_FAILED) |
| observability_contract.events[].expected | – | enum | present, absent |
| observability_contract.events[].in_timeline | nein | boolean | Muss in Debug-Timeline sichtbar sein? |
| observability_contract.ui_state | nein | string[] | Erwarteter UI-Zustand |
| observability_contract.debug_visibility | nein | string[] | Was muss im Debug-Panel sichtbar sein? |
| observability_contract.notes | nein | string | Zusätzliche Anforderungen |

**Hinweis:** Sektion ist pflicht; Inhalt kann leer sein (`events: []`, `ui_state: []`, etc.).

---

### 3.9 determinism

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| determinism.level | **ja** | enum | Siehe Tabelle determinism.level |
| determinism.isolated | **ja** | boolean | Ohne Live-Dienste (Ollama, ChromaDB) ausführbar? |
| determinism.nondeterminism_sources | nein | string[] | Quellen von Nichtdeterminiertheit |
| determinism.mitigation | nein | string | Wie wird Nichtdeterminiertheit adressiert? |

**Erlaubte Werte determinism.level:**

| Wert | Bedeutung |
|------|------------|
| fully_deterministic | Immer gleiches Ergebnis bei gleichen Vorbedingungen |
| deterministic_with_mocks | Deterministisch mit Mocks/Stubs, nicht mit echten Diensten |
| timing_sensitive | Ergebnis kann von Timing abhängen |
| intermittent | Gelegentlich unterschiedliches Ergebnis |
| environment_dependent | Abhängig von Umgebung (Netzwerk, Dienste) |

---

### 3.10 mapping

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| mapping.test_domains | **ja** | string[] | Siehe Tabelle mapping.test_domains |
| mapping.risk_axes | **ja** | string[] | Siehe Tabelle mapping.risk_axes |
| mapping.pytest_markers | nein | string[] | Empfohlene pytest-Marker |
| mapping.subsystem | nein | string | Betroffenes Subsystem |
| mapping.failure_class | nein | string | Fehlerklasse |

**Erlaubte Werte mapping.test_domains:**

| Wert | Bedeutung |
|------|------------|
| failure_modes | Failure-Injection-Tests |
| contract | Contract-Tests |
| async_behavior | Async/Race-Tests |
| cross_layer | Cross-Layer-Tests |
| startup | Startup-Tests |
| chaos | Chaos/Fault-Injection |
| integration | Integrationstests |
| state_consistency | State-Consistency |
| golden_path | Golden-Path E2E |
| regression | Regressionstests |

**Erlaubte Werte mapping.risk_axes:**

| Wert | Bedeutung |
|------|------------|
| Failure_Coverage | Failure-Abdeckung |
| Contract_Coverage | Contract-Abdeckung |
| Async_Coverage | Async-Abdeckung |
| Cross_Layer_Coverage | Cross-Layer-Abdeckung |
| Drift_Governance_Coverage | Drift/Governance-Abdeckung |
| Restrisiko | Restrisiko |

---

### 3.11 verification

| Feld | Pflicht | Typ | Beschreibung |
|------|---------|-----|--------------|
| verification.status | **ja** | enum | Siehe Tabelle verification.status |
| verification.verified_at | nein | datetime | ISO 8601 |
| verification.verified_by | nein | string | Wer hat verifiziert? |
| verification.notes | nein | string | Verifikationsnotizen |

**Erlaubte Werte verification.status:**

| Wert | Bedeutung |
|------|------------|
| draft | Replay definiert, nicht validiert |
| validated | Manuell reproduziert, bestätigt |
| test_bound | Test existiert, führt Replay aus |
| guarded | Test in CI, grün |
| obsolete | Nicht mehr relevant |

---

## 4. Pflichtfeld-Checkliste

| Sektion | Pflichtfelder |
|---------|---------------|
| Top-Level | schema_version |
| identity | id, incident_id, title, created, updated |
| replay_type | type |
| preconditions | system |
| execution | steps (mit id, action pro Schritt) |
| assertion_contract | success, failure |
| observability_contract | (Sektion pflicht; Inhalt kann leer sein) |
| determinism | level, isolated |
| mapping | test_domains, risk_axes |
| verification | status |

---

## 5. Validierungsregeln

| Regel | Beschreibung |
|-------|--------------|
| V1 | identity.incident_id muss auf existierendes incident.yaml verweisen |
| V2 | identity.id = REPLAY- + identity.incident_id |
| V3 | execution.steps mindestens ein Schritt |
| V4 | assertion_contract.success und failure nicht leer |
| V5 | mapping.test_domains und mapping.risk_axes nicht leer |
| V6 | fixtures.refs[].file muss unter fixtures/ existieren (falls angegeben) |

---

## 6. Beispiel (Minimal – Fault Injection)

```yaml
schema_version: "1.0"

identity:
  id: REPLAY-INC-20260315-001
  incident_id: INC-20260315-001
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

mapping:
  test_domains:
    - failure_modes
    - chaos
  risk_axes:
    - Failure_Coverage
    - Drift_Governance_Coverage
  subsystem: RAG
  failure_class: rag_silent_failure

verification:
  status: draft
```

---

## 7. Template

**Vorlage:** [incidents/templates/replay.template.yaml](incidents/templates/replay.template.yaml)

---

## 8. Verweise

| Dokument | Inhalt |
|----------|--------|
| [QA_INCIDENT_REPLAY_ARCHITECTURE.md](QA_INCIDENT_REPLAY_ARCHITECTURE.md) | Überblicksarchitektur |
| [QA_INCIDENT_LIFECYCLE.md](QA_INCIDENT_LIFECYCLE.md) | Replay-Lifecycle, verification.status |
| [incidents/templates/replay.template.yaml](incidents/templates/replay.template.yaml) | Verbindliche Vorlage |
| [incidents/QA_INCIDENT_PILOT_ITERATION.md](incidents/QA_INCIDENT_PILOT_ITERATION.md) | Pilotfälle, Replay-Typen pro Pilotfall |

---

*QA Replay Schema – verbindlich ab 15. März 2026.*
