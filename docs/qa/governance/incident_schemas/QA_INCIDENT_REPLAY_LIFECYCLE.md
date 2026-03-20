# QA Incident Replay – Verbindlicher Lifecycle

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Klarer Statusfluss für Incidents und Replays, Governance-Regeln, Reviewpflichten.

---

## 1. Grundprinzip: Zwei getrennte Lifecycles

| Lifecycle | Träger | Zweck |
|-----------|--------|-------|
| **Incident-Lifecycle** | incident.yaml (qa.status) | Lebensweg des beobachteten Vorfalls |
| **Replay-Lifecycle** | replay.yaml (verification.status) | Lebensweg des Reproduktionsvertrags |

**Trennung:** Ein Incident kann existieren ohne Replay (bis replay_defined). Ein Replay ist immer einem Incident zugeordnet. Die Lifecycles sind gekoppelt, aber nicht identisch.

---

## 2. Incident-Lifecycle

### 2.1 Statusübersicht

| Status | Bedeutung | Nächste erlaubte Übergänge |
|--------|------------|----------------------------|
| **new** | Neu erfasst, unvollständig | triaged, invalid, duplicate |
| **triaged** | Erste Bewertung erfolgt | classified, invalid, duplicate |
| **classified** | Fehlerklasse, Subsystem zugeordnet | replay_defined, invalid, duplicate, archived |
| **replay_defined** | replay.yaml existiert | replay_verified, invalid, duplicate, archived |
| **replay_verified** | Replay manuell bestätigt | bound_to_regression, invalid, duplicate, archived |
| **bound_to_regression** | Test existiert, in Catalog | closed, archived |
| **closed** | Erfolgreich abgeschlossen | archived |
| **invalid** | Kein gültiger Bug | archived |
| **duplicate** | Duplikat eines anderen Incidents | archived |
| **archived** | Archiviert, nicht mehr aktiv | – (Endzustand) |

### 2.2 Statusfluss (Diagramm)

```
                    ┌─────────┐
                    │  new    │
                    └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌──────────┐    ┌──────────┐
    │ triaged │    │ invalid  │    │ duplicate│
    └────┬────┘    └────┬─────┘    └────┬─────┘
         │              │               │
         ▼              │               │
    ┌───────────┐       │               │
    │ classified│       │               │
    └─────┬─────┘       │               │
          │             │               │
          ▼             │               │
    ┌──────────────┐    │               │
    │replay_defined│    │               │
    └──────┬───────┘    │               │
           │            │               │
           ▼            │               │
    ┌──────────────┐    │               │
    │replay_verified│   │               │
    └──────┬───────┘    │               │
           │            │               │
           ▼            │               │
    ┌─────────────────┐ │               │
    │bound_to_regression│               │
    └──────┬──────────┘ │               │
           │            │               │
           ▼            ▼               ▼
    ┌─────────┐    ┌──────────┐
    │ closed  │    │ archived │
    └────┬────┘    └──────────┘
         │
         ▼
    ┌──────────┐
    │ archived │
    └──────────┘
```

### 2.3 Bedingungen je Statuswechsel

| Übergang | Bedingungen |
|----------|-------------|
| **new → triaged** | incident.yaml: identity, detection, environment, behavior (description, expected, actual, repro_steps) vollständig. severity, priority gesetzt. |
| **triaged → classified** | classification.failure_class und classification.subsystem gesetzt. failure_class muss in REGRESSION_CATALOG existieren. |
| **classified → replay_defined** | replay.yaml existiert im Incident-Verzeichnis. replay.yaml valide gegen Schema. identity.incident_id verknüpft. |
| **replay_defined → replay_verified** | Replay manuell ausgeführt, Bug reproduziert. verification.status in replay.yaml = validated. |
| **replay_verified → bound_to_regression** | regression_test in bindings.json gesetzt. Test existiert. Eintrag in REGRESSION_CATALOG. |
| **bound_to_regression → closed** | Test in CI, letzter Lauf grün. resolution.fix und resolution.verified in incident.yaml. |
| **→ invalid** | Begründung in notes.md oder resolution. reason: "invalid" erforderlich. |
| **→ duplicate** | duplicate_of: INC-xxx in incident.yaml oder notes.md. Referenz auf kanonischen Incident. |
| **→ archived** | Grund in notes.md oder status.reason. Von closed, invalid, duplicate, oder bei Obsoletwerden. |

### 2.4 Feldzuordnung (incident.yaml)

| Incident-Status | Entspricht qa.status (alt) | Speicherort |
|-----------------|----------------------------|-------------|
| new | draft | incident.yaml qa.status |
| triaged | draft (mit mehr Feldern) | incident.yaml qa.status |
| classified | captured | incident.yaml qa.status |
| replay_defined | replay_created | incident.yaml qa.status |
| replay_verified | replay_validated | incident.yaml qa.status |
| bound_to_regression | test_bound | incident.yaml qa.status |
| closed | guarded | incident.yaml qa.status |
| invalid | – | incident.yaml qa.status |
| duplicate | – | incident.yaml qa.status |
| archived | – | incident.yaml qa.status |

---

## 3. Replay-Lifecycle

### 3.1 Statusübersicht

| Status | Bedeutung | Nächste erlaubte Übergänge |
|--------|------------|----------------------------|
| **draft** | Replay definiert, nicht validiert | validated, obsolete |
| **validated** | Manuell reproduziert, bestätigt | test_bound, obsolete |
| **test_bound** | Test existiert, führt Replay aus | guarded, obsolete |
| **guarded** | Test in CI, grün | obsolete |
| **obsolete** | Nicht mehr relevant | – (Endzustand) |

### 3.2 Statusfluss (Diagramm)

```
    ┌─────────┐     ┌───────────┐     ┌────────────┐     ┌─────────┐
    │  draft  │ ──► │ validated  │ ──► │ test_bound │ ──► │ guarded │
    └────┬────┘     └─────┬─────┘     └──────┬─────┘     └────┬────┘
         │                │                  │                │
         └────────────────┴──────────────────┴────────────────┘
                                    │
                                    ▼
                              ┌──────────┐
                              │ obsolete │
                              └──────────┘
```

### 3.3 Bedingungen je Statuswechsel

| Übergang | Bedingungen |
|----------|-------------|
| **draft → validated** | Replay manuell ausgeführt. assertion_contract.failure erfüllt (Bug reproduziert). Reviewer bestätigt. |
| **validated → test_bound** | regression_test in bindings.json gesetzt. Test implementiert, bildet Replay ab. |
| **test_bound → guarded** | Test in CI integriert. Letzter Lauf grün. |
| **→ obsolete** | Incident invalid/duplicate/archived. Oder Replay nicht mehr anwendbar (z.B. Code geändert). |

### 3.4 Kopplung Incident ↔ Replay

| Incident-Status | Replay-Status (typisch) |
|-----------------|--------------------------|
| replay_defined | draft |
| replay_verified | validated |
| bound_to_regression | test_bound |
| closed | guarded |
| invalid, duplicate | obsolete |

**Regel:** Incident-Status hat Vorrang. Wenn Incident → invalid/duplicate, muss Replay → obsolete.

---

## 4. Erlaubte Statusübergänge (Konsolidiert)

### 4.1 Incident

| Von | Nach | Reviewpflichtig |
|-----|------|-----------------|
| new | triaged | nein |
| new | invalid | **ja** |
| new | duplicate | **ja** |
| triaged | classified | **ja** |
| triaged | invalid | **ja** |
| triaged | duplicate | **ja** |
| classified | replay_defined | nein (replay.yaml vorhanden) |
| classified | invalid | **ja** |
| classified | duplicate | **ja** |
| classified | archived | **ja** |
| replay_defined | replay_verified | **ja** |
| replay_defined | invalid | **ja** |
| replay_defined | duplicate | **ja** |
| replay_defined | archived | **ja** |
| replay_verified | bound_to_regression | **ja** |
| replay_verified | invalid | **ja** |
| replay_verified | duplicate | **ja** |
| replay_verified | archived | **ja** |
| bound_to_regression | closed | **ja** |
| bound_to_regression | archived | **ja** |
| closed | archived | nein |
| invalid | archived | nein |
| duplicate | archived | nein |

### 4.2 Replay

| Von | Nach | Reviewpflichtig |
|-----|------|-----------------|
| draft | validated | **ja** |
| draft | obsolete | **ja** |
| validated | test_bound | **ja** |
| validated | obsolete | **ja** |
| test_bound | guarded | nein (CI-Ergebnis) |
| test_bound | obsolete | **ja** |
| guarded | obsolete | **ja** |

---

## 5. Governance-Regeln

### 5.1 Allgemeine Regeln

| ID | Regel | Beschreibung |
|----|-------|--------------|
| **G1** | classified ohne failure_class unzulässig | Status classified erfordert classification.failure_class in incident.yaml. |
| **G2** | classified ohne subsystem unzulässig | Status classified erfordert classification.subsystem. |
| **G3** | replay_defined ohne replay.yaml unzulässig | replay.yaml muss existieren und valide sein. |
| **G4** | failure_class muss in REGRESSION_CATALOG existieren | Neue Fehlerklasse: Zuerst REGRESSION_CATALOG erweitern. |
| **G5** | closed nur mit Begründung | resolution.fix und resolution.verified erforderlich. notes.md oder resolution.fix muss Fix beschreiben. |
| **G6** | regression_required nicht still schließen | Ein Incident mit classification.severity ≥ medium und ohne regression_test darf nicht nach closed wechseln, außer mit expliziter Ausnahme (resolution.waived: true + Begründung). |
| **G7** | invalid/duplicate nur mit Begründung | status.reason oder notes.md muss Grund enthalten. |
| **G8** | duplicate erfordert Referenz | duplicate_of: INC-xxx muss gesetzt sein (in incident.yaml oder notes.md). |
| **G9** | archived erfordert Grund | status.reason oder notes.md. |
| **G10** | bound_to_regression erfordert Test | regression_test in bindings.json muss gesetzt und Test muss existieren. |

### 5.2 Spezielle Regeln

| ID | Regel | Beschreibung |
|----|-------|--------------|
| **G11** | Kein Überspringen von Status | new → classified ohne triaged unzulässig. classified → replay_verified ohne replay_defined unzulässig. |
| **G12** | Rückwärts nur zu Korrektur | Rückwärts zu new/triaged/classified nur bei Korrektur, mit Begründung. |
| **G13** | Replay obsolete bei Incident invalid/duplicate | Wenn Incident → invalid oder duplicate, Replay → obsolete. |
| **G14** | Bindings-Status synchron | bindings.json status.binding_status: catalog_bound nur wenn Incident bound_to_regression oder closed. |

---

## 6. Reviewpflichten

### 6.1 Wann ist Review erforderlich?

| Aktion | Reviewpflicht | Reviewer |
|--------|---------------|----------|
| new → triaged | nein | – |
| triaged → classified | **ja** | QA oder Entwickler mit Domain-Kenntnis |
| classified → replay_defined | nein | – (replay.yaml Vorhandenheit) |
| replay_defined → replay_verified | **ja** | QA (manuelle Reproduktion) |
| replay_verified → bound_to_regression | **ja** | QA (Test-Abbildung prüfen) |
| bound_to_regression → closed | **ja** | QA (CI-Erfolg bestätigen) |
| → invalid | **ja** | QA Lead oder Entwickler |
| → duplicate | **ja** | QA (Duplikat bestätigen) |
| → archived | **ja** (außer von closed/invalid/duplicate) | QA |

### 6.2 Review-Dokumentation

| Feld | Speicherort | Inhalt |
|------|-------------|--------|
| reviewed_at | bindings.json meta | Zeitpunkt des Reviews |
| reviewed_by | bindings.json meta | Name/Team des Reviewers |
| reason | incident.yaml / notes.md | Begründung bei invalid, duplicate, archived |
| duplicate_of | incident.yaml (neues Feld) oder notes.md | Referenz bei duplicate |

### 6.3 Review-Checkliste (classified)

- [ ] failure_class existiert in REGRESSION_CATALOG
- [ ] subsystem existiert in QA_RISK_RADAR
- [ ] severity und priority plausibel
- [ ] behavior.repro_steps vollständig

### 6.4 Review-Checkliste (replay_verified)

- [ ] Replay manuell ausgeführt
- [ ] Bug reproduziert (assertion_contract.failure erfüllt)
- [ ] replay.yaml vollständig und valide
- [ ] determinism.level und isolated plausibel

### 6.5 Review-Checkliste (bound_to_regression)

- [ ] Test existiert am angegebenen Pfad
- [ ] Test bildet Replay ab (assertion_contract)
- [ ] Test in REGRESSION_CATALOG eingetragen
- [ ] Test läuft grün (lokal oder CI)

---

## 7. Validierungsregeln

### 7.1 Pro Status

| Status | Validierung |
|--------|-------------|
| **new** | incident.yaml: schema_version, identity, detection, environment, behavior (minimal) |
| **triaged** | + classification.severity, classification.priority |
| **classified** | + classification.failure_class, classification.subsystem. failure_class ∈ REGRESSION_CATALOG |
| **replay_defined** | + replay.yaml existiert, valide, identity.incident_id stimmt |
| **replay_verified** | + replay.yaml verification.status = validated |
| **bound_to_regression** | + bindings.json regression_test gesetzt, Test existiert |
| **closed** | + resolution.fix, resolution.verified. regression_test in CI grün |
| **invalid** | + status.reason oder notes.md mit Begründung |
| **duplicate** | + duplicate_of: INC-xxx |
| **archived** | + status.reason oder notes.md |

### 7.2 Replay-Validierung

| Replay-Status | Validierung |
|---------------|-------------|
| **draft** | replay.yaml valide gegen Schema. execution.steps, assertion_contract nicht leer. |
| **validated** | + Manuell bestätigt (meta.reviewed_at) |
| **test_bound** | + bindings.json regression_test verweist auf existierenden Test |
| **guarded** | + Test in CI, letzter Lauf grün |
| **obsolete** | + status.reason oder Incident invalid/duplicate |

---

## 8. Mapping zu bestehenden Artefakten

### 8.1 incident.yaml qa.status

| Lifecycle-Status | qa.status (incident.yaml) |
|------------------|---------------------------|
| new | new |
| triaged | triaged |
| classified | classified |
| replay_defined | replay_defined |
| replay_verified | replay_verified |
| bound_to_regression | bound_to_regression |
| closed | closed |
| invalid | invalid |
| duplicate | duplicate |
| archived | archived |

### 8.2 replay.yaml verification.status

| Lifecycle-Status | verification.status (replay.yaml) |
|------------------|-----------------------------------|
| draft | draft |
| validated | validated |
| test_bound | test_bound |
| guarded | guarded |
| obsolete | obsolete |

### 8.3 bindings.json status.binding_status

| Incident-Status | binding_status |
|-----------------|-----------------|
| new, triaged, classified | proposed |
| replay_defined, replay_verified | validated |
| bound_to_regression, closed | catalog_bound |
| invalid, duplicate | rejected |
| archived | archived |

---

## 9. Neue Pflichtfelder (Erweiterungen)

### 9.1 incident.yaml

| Feld | Sektion | Pflicht bei | Beschreibung |
|------|---------|-------------|--------------|
| **duplicate_of** | identity oder qa | status = duplicate | Referenz auf kanonischen Incident (INC-xxx) |
| **status_reason** | qa | invalid, duplicate, archived | Grund für Status (oder in notes.md) |
| **regression_waived** | resolution | closed ohne Test | Boolean, true nur mit Begründung |

### 9.2 notes.md

Bei invalid, duplicate, archived: Begründung in notes.md unter ## Statusänderung.

---

*QA Incident Replay Lifecycle – verbindlich ab 15. März 2026.*
