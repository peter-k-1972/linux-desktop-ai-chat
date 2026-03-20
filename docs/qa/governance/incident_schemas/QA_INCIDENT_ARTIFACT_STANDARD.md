# QA Incident Replay – Verbindlicher Artefaktstandard

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Standardisierte, dateibasierte Incident-Struktur für lokale QA-Governance.

---

## 1. Ziel-Verzeichnisstruktur

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
│   ├── notes.md                          # Führend: Menschliche Review-Notizen
│   │
│   ├── evidence/                         # Unterstützend: Belege
│   │   ├── .gitkeep
│   │   └── (screenshots, logs, stacktraces)
│   │
│   ├── fixtures/                         # Unterstützend: Replay-Vorlagen
│   │   ├── .gitkeep
│   │   └── (state files, mock data)
│   │
│   └── derived/                          # Abgeleitet: Generierte Artefakte
│       ├── .gitkeep
│       └── (validierung.json, status.json – niemals von Hand)
│
└── _registry.json                        # Abgeleitet: Aggregiert aus allen Incidents
```

**Lifecycle:** [QA_INCIDENT_LIFECYCLE.md](QA_INCIDENT_LIFECYCLE.md)

### 1.1 Namenskonvention

| Element | Format | Beispiel |
|---------|--------|----------|
| Incident-Verzeichnis | `INC-YYYYMMDD-NNN` | `INC-20260315-001` |
| Schema-Verzeichnis | `_schema` | Reserviert, Unterstrich = Meta |
| Registry | `_registry.json` | Unterstrich = Meta, Projekt-weit |

---

## 2. Zweck jeder Datei und jedes Verzeichnisses

### 2.1 Kernartefakte (führend)

| Artefakt | Format | Zweck |
|----------|--------|-------|
| **incident.yaml** | YAML | Beobachteter Vorfall – was tatsächlich passiert ist. Unverfälschte Erfassung: Beschreibung, Schritte, Umgebung, Verhalten. Quelle der Wahrheit für den Vorfall. |
| **replay.yaml** | YAML | Reproduktionsvertrag – minimale, vereinbarte Reproduktion. Was wird getestet? Vorbedingungen, Aktionen, erwartetes Ergebnis, Fehlerindikator. Vertrag zwischen Incident und künftigem Test. |
| **bindings.json** | JSON | QA-Bindings – maschinenlesbare Verknüpfungen: Fehlerklasse, Subsystem, Regression Catalog, Test-Pfad. Integration in das QA-Ökosystem. |
| **notes.md** | Markdown | Menschliche Review-Notizen – Kontext, Entscheidungen, Diskussionen. Nicht für Tooling, nur für Menschen. |

### 2.2 Unterstützende Verzeichnisse

| Verzeichnis | Zweck |
|-------------|-------|
| **evidence/** | Belege für den Vorfall: Screenshots, Log-Ausschnitte, Stacktraces, Event-Logs. Unterstützen `incident.yaml`, werden darin referenziert. Keine Ableitung – manuell beigefügt. |
| **fixtures/** | Vorbereitete Zustände für Replay: Mock-Daten, State-Dumps, Konfigurationen. Unterstützen `replay.yaml`. Ermöglichen deterministische Reproduktion. |

### 2.3 Abgeleitete Verzeichnisse

| Verzeichnis | Zweck |
|-------------|-------|
| **derived/** | Generierte Artefakte: Validierungsbericht, Status-Snapshot, Aggregationen. **Niemals von Hand bearbeiten.** Werden von Generatoren überschrieben. |

### 2.4 Meta-Artefakte

| Artefakt | Zweck |
|----------|-------|
| **_schema/** | JSON/YAML-Schemas für Validierung. Einmalig, projektspezifisch anpassbar. |
| **_registry.json** | Aggregiertes Register aller Incidents. Wird aus den Incident-Verzeichnissen generiert. |

---

## 3. Trennung der Verantwortlichkeiten

### 3.1 Vier getrennte Konzerne

```
┌─────────────────────────────────────────────────────────────────┐
│  incident.yaml          │  BEOBACHTETER VORFALL                   │
│  Was ist passiert?      │  Faktisch, uninterpretiert              │
│  Wer hat es gesehen?   │  Reproduktionsschritte (wie beobachtet) │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  replay.yaml            │  REPRODUKTIONSVERTRAG                  │
│  Was wird getestet?      │  Minimal, vereinbart                  │
│  Wie erkennt man Bug?   │  Vorbedingungen, Aktionen, Assertion   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  bindings.json          │  QA-BINDINGS                          │
│  Wo gehört es hin?     │  Fehlerklasse, Subsystem, Test-Pfad    │
│  Wie integriert?        │  Maschinenlesbar, Tooling              │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  notes.md                │  MENSCHLICHE REVIEW-NOTIZEN           │
│  Warum so entschieden?   │  Kontext, Diskussion, Offene Punkte   │
│  Was ist unklar?         │  Frei formuliert, nicht geparst       │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Tabelle: Was gehört wohin?

| Frage | Artefakt | Begründung |
|-------|----------|------------|
| Was ist passiert? | incident.yaml | Beobachtung, nicht Interpretation |
| Was hätte passieren sollen? | incident.yaml | Teil der Beobachtung (Soll-Ist) |
| Wie reproduziert man es? | incident.yaml (Schritte) + replay.yaml (Vertrag) | incident = wie beobachtet, replay = wie getestet |
| Welche Fehlerklasse? | bindings.json | Klassifikation, nicht Beobachtung |
| Welches Subsystem? | bindings.json | Zuordnung zum QA-Ökosystem |
| Welcher Test deckt ab? | bindings.json | Verknüpfung, kann sich ändern |
| Warum diese Zuordnung? | notes.md | Menschliche Begründung |
| Screenshot vom Fehler? | evidence/ | Beleg, referenziert in incident.yaml |
| Mock-Daten für Replay? | fixtures/ | Unterstützung des Reproduktionsvertrags |

---

## 4. Architektonische Begründung der Trennung

### 4.1 Warum vier getrennte Dateien?

| Prinzip | Begründung |
|---------|------------|
| **Single Responsibility** | Jedes Artefakt hat eine klar abgegrenzte Verantwortung. Änderung an einer Dimension betrifft nur eine Datei. |
| **Unterschiedliche Lebenszyklen** | Incident kann „eingefroren“ werden (Vorfall abgeschlossen), Replay kann verfeinert werden (bessere Reproduktion), Bindings ändern sich (neuer Test), Notes wachsen (Review). |
| **Unterschiedliche Autoren** | Reporter (incident), QA-Engineer (replay), Tooling/Governance (bindings), Reviewer (notes). |
| **Unterschiedliche Formate** | YAML für menschlich bearbeitbare Strukturdaten, JSON für maschinenorientierte Bindings, Markdown für Prosa. |
| **Auditierbarkeit** | Beobachtung (incident) bleibt getrennt von Klassifikation (bindings). Keine Vermischung von Fakt und Zuordnung. |

### 4.2 Warum evidence/ und fixtures/ getrennt?

| Verzeichnis | Begründung |
|-------------|------------|
| **evidence/** | Belege gehören zum **Vorfall**. Sie dokumentieren, was passiert ist. Sie werden von `incident.yaml` referenziert (z.B. `evidence/screenshot_001.png`). Nicht Teil des Reproduktionsvertrags. |
| **fixtures/** | Vorlagen gehören zum **Replay**. Sie ermöglichen deterministische Reproduktion. Werden von `replay.yaml` referenziert. Getrennt, weil sie anderen Zwecken dienen (Replay-Setup vs. Vorfall-Dokumentation). |

### 4.3 Warum derived/ strikt abgeleitet?

- **Keine Handbearbeitung:** Alles in `derived/` wird von Generatoren erzeugt. Bearbeitung würde bei nächstem Lauf überschrieben.
- **Klare Autorität:** Führende Artefakte sind Quelle; derived ist Spiegel. Bei Konflikt gilt das führende Artefakt.
- **Reproduzierbarkeit:** `derived/` kann bei Bedarf gelöscht und neu generiert werden.

---

## 5. Führende vs. abgeleitete Artefakte

### 5.1 Führend (canonical, Quelle der Wahrheit)

| Artefakt | Bearbeitung | Autorität |
|----------|-------------|-----------|
| incident.yaml | Manuell | Einzige Quelle für den beobachteten Vorfall |
| replay.yaml | Manuell | Einzige Quelle für den Reproduktionsvertrag |
| bindings.json | Manuell oder Tool (mit Review) | Einzige Quelle für QA-Verknüpfungen |
| notes.md | Manuell | Einzige Quelle für Review-Kontext |
| evidence/* | Manuell hinzugefügt | Belege, referenziert in incident.yaml |
| fixtures/* | Manuell hinzugefügt | Vorlagen, referenziert in replay.yaml |

### 5.2 Abgeleitet (generiert, niemals von Hand)

| Artefakt | Erzeuger | Regel |
|----------|----------|-------|
| derived/* | Generator-Skripte | Alles unter derived/ ist generiert. Löschen und neu generieren erlaubt. |
| _registry.json | generate_incident_registry.py | Aggregation aller Incident-Verzeichnisse. |

### 5.3 Regeln der Autorität

| Regel | Beschreibung |
|-------|--------------|
| **R1** | Bei Konflikt zwischen führendem und abgeleitetem Artefakt gilt das führende. |
| **R2** | Abgeleitete Artefakte dürfen führende nicht überschreiben. |
| **R3** | Änderung an führendem Artefakt erfordert ggf. Regenerierung von derived/ und _registry. |
| **R4** | evidence/ und fixtures/ sind unterstützend, nicht abgeleitet – sie werden manuell gepflegt, aber von incident.yaml bzw. replay.yaml referenziert. |
| **R5** | _registry.json ist immer abgeleitet. Manuelle Änderung ist verboten. |

---

## 6. Minimale Struktur der Kernartefakte

### 6.1 incident.yaml (Beobachteter Vorfall)

**Vollständiger Feldstandard:** [incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md](incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md)

**Sektionen (verbindlich):** schema_version, identity, detection, environment, classification, behavior, qa  
**Optionale Sektionen:** evidence, analysis, resolution

```yaml
schema_version: "1.0"

identity:
  id: INC-20260315-001
  title: "Kurzbeschreibung (max. 80 Zeichen)"
  created: "2026-03-15T10:00:00Z"
  updated: "2026-03-15T10:00:00Z"
  source: manual  # production | staging | development | manual | audit | regression

detection:
  when: "2026-03-15T09:30:00Z"
  how: manual  # manual | test_failure | ci_failure | monitoring | audit | regression

environment:
  runtime_layer: cross_layer  # ui | service | persistence | integration | startup | observability | cross_layer

classification:
  failure_class: rag_silent_failure  # aus REGRESSION_CATALOG
  subsystem: RAG                     # aus QA_RISK_RADAR
  severity: medium                   # critical | high | medium | low | cosmetic
  priority: P1                       # P0 | P1 | P2 | P3

behavior:
  description: "Was ist passiert?"
  expected: "Was hätte passieren sollen?"
  actual: "Was ist tatsächlich passiert?"
  repro_steps: ["1. Schritt eins", "2. Schritt zwei"]
  reproducibility: always  # always | intermittent | once | unknown | requires_specific_state

qa:
  status: new  # new | triaged | classified | replay_defined | replay_verified | bound_to_regression | closed | invalid | duplicate | archived
```

**Templates:** [incidents/templates/incident.template.yaml](incidents/templates/incident.template.yaml)

**Hinweis:** classification in incident.yaml ist die primäre Klassifikation. bindings.json spiegelt sie für die Integration (regression_catalog.failure_class, risk_radar.subsystem) – siehe Abschnitt 7.

### 6.2 replay.yaml (Reproduktionsvertrag)

**Vollständiger Feldstandard:** [incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md](incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md)

**Deklarativ, kein Testcode.** replay.yaml ist der Reproduktionsvertrag – Spezifikation, was reproduziert und geprüft werden soll.

```yaml
schema_version: "1.0"

identity:
  id: REPLAY-INC-20260315-001
  incident_id: INC-20260315-001
  title: "Kurzbeschreibung"
  created: "2026-03-15T11:00:00Z"
  updated: "2026-03-15T11:00:00Z"

replay_type:
  type: fault_injection  # startup_dependency_failure | provider_unreachable | fault_injection | event_contract_drift | ...

preconditions:
  system: ["Bedingung 1", "Bedingung 2"]

execution:
  steps:
    - id: S1
      action: "Aktion 1"
      actor: user
    - id: S2
      action: "Aktion 2"
      actor: app
  ordering: sequential

assertion_contract:
  success: ["Erfolgskriterium 1"]
  failure: ["Fehlerindikator 1"]
  no_crash: true

observability_contract:
  events: []
  debug_visibility: []

determinism:
  level: fully_deterministic  # fully_deterministic | deterministic_with_mocks | timing_sensitive | ...
  isolated: true

mapping:
  test_domains: [failure_modes, chaos]
  risk_axes: [Failure_Coverage]

verification:
  status: draft  # draft | validated | test_bound | guarded | obsolete
```

**Templates:** [incidents/templates/replay.template.yaml](incidents/templates/replay.template.yaml)

### 6.3 bindings.json (QA-Bindings)

**Vollständiger Feldstandard:** [incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md](incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md)

Maschinenlesbare Integrationsschicht zu REGRESSION_CATALOG, QA_RISK_RADAR, QA_HEATMAP, QA_CONTROL_CENTER, QA_AUTOPILOT, QA_DEPENDENCY_GRAPH.

```json
{
  "schema_version": "1.0",
  "identity": {
    "incident_id": "INC-20260315-001",
    "replay_id": "REPLAY-INC-20260315-001"
  },
  "regression_catalog": {
    "failure_class": "rag_silent_failure",
    "regression_test": null
  },
  "risk_radar": {
    "subsystem": "RAG",
    "priority": "P1"
  },
  "heatmap": {
    "dimensions": ["Failure_Coverage", "Drift_Governance_Coverage"]
  },
  "status": {
    "binding_status": "proposed",
    "updated": "2026-03-15T11:00:00Z"
  },
  "meta": {
    "created": "2026-03-15T11:00:00Z",
    "updated": "2026-03-15T11:00:00Z"
  }
}
```

**Binding-Status:** proposed | validated | catalog_bound | rejected | archived

**Templates:** [incidents/templates/bindings.template.json](incidents/templates/bindings.template.json)

### 6.4 notes.md (Menschliche Review-Notizen)

```markdown
# Review-Notizen: INC-20260315-001

## Kontext
...

## Entscheidungen
...

## Offene Punkte
...
```

Keine feste Struktur. Frei formuliert.

**Templates:** [incidents/templates/notes.template.md](incidents/templates/notes.template.md)

---

## 7. Klassifikation: incident.yaml vs. bindings.json

**Regel:** Klassifikation (failure_class, subsystem) existiert an **zwei Stellen** – sie müssen übereinstimmen:

| Ort | Zweck | Autorität |
|-----|-------|-----------|
| **incident.yaml** (classification) | Primäre Klassifikation des Vorfalls – Teil der Incident-Dokumentation | Quelle für den Incident-Kontext |
| **bindings.json** (regression_catalog, risk_radar) | Integrationsschicht – Generatoren lesen von hier | Muss mit incident.yaml übereinstimmen |

**Synchronisationsregel:** `bindings.json.regression_catalog.failure_class` = `incident.yaml.classification.failure_class`. `bindings.json.risk_radar.subsystem` = `incident.yaml.classification.subsystem`. Bei Abweichung gilt incident.yaml als autoritativ; bindings.json ist zu korrigieren.

---

## 8. Verzeichnis-Pflichten

| Verzeichnis | Pflicht | Inhalt |
|-------------|---------|--------|
| INC-*/ | Ja | Jeder Incident hat genau ein Verzeichnis |
| INC-*/evidence/ | Nein | Kann leer sein (.gitkeep) |
| INC-*/fixtures/ | Nein | Kann leer sein (.gitkeep) |
| INC-*/derived/ | Nein | Wird bei Bedarf generiert |
| _schema/ | Ja | Einmalig anlegen |
| _registry.json | Abgeleitet | Wird generiert |

---

## 9. Zusammenfassung

| Kategorie | Artefakte | Bearbeitung |
|-----------|-----------|-------------|
| **Führend** | incident.yaml, replay.yaml, bindings.json, notes.md | Manuell |
| **Unterstützend** | evidence/*, fixtures/* | Manuell |
| **Abgeleitet** | derived/*, _registry.json | Nur Generator |

| Trennung | incident.yaml | replay.yaml | bindings.json | notes.md |
|----------|---------------|-------------|---------------|----------|
| **Inhalt** | Beobachteter Vorfall | Reproduktionsvertrag | QA-Bindings | Review-Notizen |
| **Zweck** | Was ist passiert? | Was wird getestet? | Wo gehört es hin? | Warum so? |

---

*QA Incident Artefaktstandard – verbindlich ab 15. März 2026.*
