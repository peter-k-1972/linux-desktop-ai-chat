# QA Incident Replay – Integration

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Integration des Incident Replay Systems in die bestehende QA-Governance. Keine Parallelwelt – Incidents speisen die Artefakte.

---

## 1. Integrationsprinzip

| Prinzip | Beschreibung |
|---------|--------------|
| **Speisung, nicht Ersatz** | Incident-Daten fließen in bestehende Artefakte ein. Keine parallelen Strukturen. |
| **Bindings als Brücke** | bindings.json ist die Integrationsschicht. Alle Projektionen gehen von dort aus. |
| **Generator-basiert** | Bestehende Generator-Skripte werden erweitert, nicht ersetzt. |
| **Registrierung als Quelle** | _registry.json (aggregiert aus allen Incidents) ist Eingabe für alle Integrationspunkte. |

---

## 2. Projektion in REGRESSION_CATALOG

### 2.1 Datenquelle

| Quelle | Pfad | Verwendung |
|--------|------|------------|
| _registry.json | docs/qa/incidents/_registry.json | Aggregierte Incident-Daten |
| bindings.json | INC-*/bindings.json | failure_class, regression_test pro Incident |

### 2.2 Projektionen (Definition)

| Projektion | Quelle | Ziel in REGRESSION_CATALOG | Mechanismus |
|------------|--------|----------------------------|-------------|
| **Incidents pro Fehlerklasse** | _registry.incidents, failure_class | Neue Sektion „Incidents pro Fehlerklasse“ | Gruppierung nach failure_class |
| **incident_ref** | bindings.regression_catalog.regression_test | Spalte „Incident“ in Zuordnungstabelle | Rückwärts-Mapping Test → Incident |
| **Guarded pro Fehlerklasse** | status=closed, regression_test gesetzt | Zähler pro Fehlerklasse | Count |
| **Offene Incidents pro Fehlerklasse** | status ∈ {new,…,bound_to_regression} | Liste pro Fehlerklasse | Filter |

### 2.3 Neue Sektionen im REGRESSION_CATALOG

**Sektion A: Incidents pro Fehlerklasse**

| Fehlerklasse | Incidents | Guarded | Offen |
|--------------|-----------|---------|-------|
| rag_silent_failure | INC-20260315-001 | 1 | 0 |
| startup_ordering | – | 0 | 0 |
| optional_dependency_missing | INC-20260315-002 | 0 | 1 |

**Sektion B: Zuordnung Tests → Fehlerklassen (erweitert)**

| Datei | Test | Fehlerklasse | Incident |
|-------|------|--------------|----------|
| test_rag_retrieval_failure | test_rag_failure_emits_event | rag_silent_failure, debug_false_truth | INC-20260315-001 |

**Regel:** incident_ref wird aus bindings.json gelesen, wo regression_test dem Test-Pfad entspricht.

### 2.4 Generator-Logik (konzeptionell)

1. Lese _registry.json
2. Für jede failure_class: Sammle incident_ids
3. Für jeden Incident mit regression_test: Baue Test → Incident Mapping
4. Schreibe erweiterte Sektionen in REGRESSION_CATALOG.md / .json

---

## 3. Projektion in QA_CONTROL_CENTER

### 3.1 Datenquelle

| Quelle | Pfad | Verwendung |
|--------|------|------------|
| _registry.json | docs/qa/incidents/_registry.json | Alle Incident-Daten für Control Center |

### 3.2 Projektionen (Definition)

| Projektion | Bedingung | Darstellung |
|------------|-----------|-------------|
| **Offene Incidents** | status ∈ {new, triaged, classified, replay_defined, replay_verified, bound_to_regression} | Tabelle, siehe 3.3 |
| **Gesamtstatus** | Aggregation über alle Incidents | Metrik-Zeile |
| **Top-5 Empfehlungen** | Replay ohne Test, Subsystem in Autopilot | Empfehlungsliste |
| **Warnsignale** | Siehe Abschnitt 6 | Warnliste |

### 3.3 Sektion: Offene Incidents

**Tabellenstruktur:**

| Rang | Incident | Subsystem | Status | Tage seit Erfassung |
|------|----------|-----------|--------|---------------------|
| 1 | INC-20260315-002 | RAG | replay_verified | 3 |
| 2 | INC-20260315-001 | Startup/Bootstrap | classified | 5 |

**Sortierung:**  
1. bound_to_regression zuerst (nahe an Guard)  
2. replay_verified (Replay da, Test fehlt)  
3. replay_defined  
4. classified  
5. triaged, new  
6. Innerhalb gleicher Priorität: ältester zuerst (Tage absteigend)

**Filter:** Nur offene Incidents (closed, invalid, duplicate, archived ausgeschlossen).

### 3.4 Sektion: Gesamtstatus (erweitert)

**Metrik-Zeile:**  
`Incidents offen: X | guarded: Y | total: Z (ohne invalid/duplicate)`

- **offen:** Count status ∈ {new, triaged, classified, replay_defined, replay_verified, bound_to_regression}
- **guarded:** Count status = closed
- **total:** Count aller Incidents außer invalid, duplicate

### 3.5 Sektion: Top-5 operative Empfehlungen (erweitert)

**Neuer Empfehlungstyp:**  
`Incident INC-xxx (Subsystem) als Regression Guard umsetzen`

**Bedingung:** Incident mit status=replay_verified oder bound_to_regression, regression_test=null oder Test nicht in CI. Subsystem passt zu Autopilot-Kandidaten.

### 3.6 Sektion: Aktuelle Warnsignale (erweitert)

**Quelle:** Abschnitt 6 (Warnsignal-Definition). Generator prüft Bedingungen W1–W8 gegen _registry.json und gibt ausgelöste Warnsignale aus.

---

## 4. Projektion in QA_AUTOPILOT

### 4.1 Datenquelle

| Eingabe | Quelle | Format |
|---------|--------|--------|
| incident_registry | docs/qa/incidents/_registry.json | JSON |

### 4.2 Projektionen (Definition)

| Projektion | Bedingung | Darstellung in QA_AUTOPILOT |
|------------|-----------|----------------------------|
| **incident_kandidaten** | Replay ohne Test, Subsystem in Autopilot | Liste von Incident-IDs mit empfohlenem Schritt |
| **top_incident_empfehlung** | Höchstpriorisierter Kandidat | Einzeilige Empfehlung |
| **Replay-Backlog** | status=replay_verified, regression_test=null | Empfohlener Schritt pro Incident |

### 4.3 Signale / Entscheidungslogik

| Signal | Bedingung | Wirkung |
|--------|-----------|---------|
| **Incident-Sprint-Kandidat** | Subsystem in Autopilot-Kandidaten UND Incident mit Replay ohne Test | Zusätzlicher Kandidat: „Incident INC-xxx als Guard umsetzen“ |
| **Incident-Priorität** | Incident mit severity ≥ high, status = replay_verified | Subsystem höher priorisieren |
| **Replay-Backlog** | Incidents mit replay_verified, regression_test=null | Empfohlener Schritt: „Test für INC-xxx schreiben“ |

### 4.4 Kandidaten-Selektion

**Eingabefilter für incident_kandidaten:**

- status ∈ {replay_verified, bound_to_regression}
- regression_test = null ODER Test nicht in CI
- subsystem ∈ Autopilot-Subsystem-Liste (aus QA_PRIORITY_SCORE, QA_HEATMAP)

**Priorisierung:**

1. Priority Score des Subsystems (aus QA_PRIORITY_SCORE)
2. Tiebreaker: severity (high > medium > low)
3. Tiebreaker: Ältester Incident zuerst

**Ausgabeformat (konzeptionell):**

```json
{
  "incident_kandidaten": [
    {
      "incident_id": "INC-20260315-002",
      "subsystem": "RAG",
      "status": "replay_verified",
      "regression_test": null,
      "empfohlener_schritt": "Test für INC-20260315-002 schreiben",
      "prioritaet": "P1"
    }
  ],
  "top_incident_empfehlung": "INC-20260315-002: RAG – ChromaDB Failure als Guard umsetzen"
}
```

---

## 5. KPI-Definition

### 5.1 Primäre KPIs

| KPI | Definition | Berechnung | Ziel | Verwendung |
|-----|------------|------------|------|------------|
| **incidents_open** | Incidents ohne Guard | Count status ∈ {new, triaged, classified, replay_defined, replay_verified, bound_to_regression} | 0 | Control Center, Warnsignale |
| **incidents_guarded** | Incidents mit Test in CI | Count status = closed | Steigend | Control Center |
| **incidents_total** | Alle relevanten Incidents | Count außer invalid, duplicate | – | Nenner für Guard-Rate |
| **guard_rate** | Anteil guarded | incidents_guarded / incidents_total × 100 | 100% | Control Center |
| **incidents_without_replay** | Kein replay.yaml | Count status ≤ classified UND replay.yaml fehlt | 0 | Warnsignal |
| **replay_without_test** | Replay validiert, kein Test | Count status=replay_verified UND regression_test=null | 0 | Warnsignal, Autopilot |
| **oldest_open_days** | Ältester offener Incident | Max(Tage seit identity.created) für offene | < 14 | Warnsignal |

### 5.2 Sekundäre KPIs (pro Dimension)

| KPI | Dimension | Definition |
|-----|-----------|------------|
| **incidents_per_failure_class** | Fehlerklasse | Count pro failure_class |
| **guarded_per_failure_class** | Fehlerklasse | Count status=closed pro failure_class |
| **open_per_failure_class** | Fehlerklasse | Count offene pro failure_class |
| **incidents_per_subsystem** | Subsystem | Count pro risk_radar.subsystem |
| **open_per_subsystem** | Subsystem | Count offene pro Subsystem |

### 5.3 KPI-Aggregation

**Eingabe:** _registry.json  
**Berechnung:** Filter und Count pro KPI-Definition  
**Ausgabe:** Für Control Center, Anomaly Detection, Reports

---

## 6. Warnsignal-Definition

### 6.1 Warnsignale (vollständig)

| ID | Signal | Bedingung | Schwere | Reaktion |
|----|--------|-----------|---------|----------|
| **W1** | Incidents ohne Replay | ≥1 Incident mit status < replay_defined, älter als 14 Tage | mittel | Replay erfassen |
| **W2** | Replay ohne Test | ≥1 Incident mit status=replay_verified, regression_test=null | mittel | Test schreiben |
| **W3** | Incident-Stau | ≥3 offene Incidents pro Subsystem | hoch | Priorisierung, Sprint-Fokus |
| **W4** | Fehlerklasse unguarded | Fehlerklasse mit ≥1 Incident, guarded=0 | niedrig | Beobachten |
| **W5** | Incident ohne Classification | Incident mit status=new oder triaged, älter als 7 Tage | niedrig | Triage abschließen |
| **W6** | Duplicate-Rate | >2 Incidents als duplicate in einem Sprint | niedrig | Triage-Prozess prüfen |
| **W7** | Ältester offener Incident | oldest_open_days ≥ 14 | mittel | Incident priorisieren |
| **W8** | Guard-Rate niedrig | guard_rate < 80% (bei incidents_total ≥ 5) | niedrig | Backlog abbauen |

### 6.2 Schwellen (konfigurierbar)

| Schwellenwert | Standard | Verwendung |
|---------------|----------|------------|
| Tage ohne Replay | 14 | W1 |
| Tage ohne Classification | 7 | W5 |
| Offene pro Subsystem | 3 | W3 |
| Guard-Rate Minimum | 80% | W8 |
| Incidents für Guard-Rate-Berechnung | 5 | W8 |

### 6.3 Integration in QA_ANOMALY_DETECTION

| Anomalie-Klasse | Bedingung | Schwellen |
|-----------------|-----------|-----------|
| **incident_backlog** | Incidents ohne Guard, pro Subsystem | incidents_open ≥ 5 = Beobachtung; ≥ 10 = Anomalie |
| **incident_replay_gap** | Replay ohne Test | replay_without_test ≥ 1 = Beobachtung; ≥ 3 = Anomalie |

**Eingabedaten:** _registry.json

---

## 7. Risk Radar und Priority Score

### 7.1 Risk Radar – Einfluss durch Incidents

| Einfluss | Mechanismus | Priorität |
|----------|-------------|-----------|
| **Subsystem mit Incident** | Risk Radar hat bereits Priorität. Incident bestätigt Risiko. | Bestätigung |
| **Neuer Incident, kein Test** | Subsystem mit offenem Incident → Restlücken erhöhen | P1/P2 |
| **Incident guarded** | Subsystem mit geschlossenem Incident → Restlücken reduzieren | Entlastung |

**Konkret:** Risk Radar bleibt **manuell** gepflegt. Incidents werden **nicht** automatisch in QA_RISK_RADAR.md geschrieben. **QA_PRIORITY_SCORE** kann Incident-Daten als **zusätzlichen Faktor** nutzen.

### 7.2 Erweiterung QA_PRIORITY_SCORE

| Neuer Faktor | Bedeutung | Gewichtung |
|--------------|-----------|------------|
| **Offene Incidents pro Subsystem** | Subsystem mit offenem Incident → Score +1 (oder +2 bei severity high) | Optional |
| **Incidents guarded** | Subsystem mit geschlossenem Incident → leichte Entlastung | Optional |

---

## 8. Datenfluss (Übersicht)

```
docs/qa/incidents/
├── INC-*/ (incident.yaml, replay.yaml, bindings.json)
└── _registry.json  ← generiert aus INC-*/


_registry.json
    │
    ├──► REGRESSION_CATALOG (Generator + incidents)
    │         → incidents_pro_fehlerklasse
    │         → incident_ref in Zuordnung
    │
    ├──► QA_CONTROL_CENTER (Generator + incidents)
    │         → Offene Incidents
    │         → KPIs (offen, guarded)
    │         → Warnsignale
    │
    ├──► QA_AUTOPILOT (Generator + incidents)
    │         → incident_kandidaten
    │         → top_incident_empfehlung
    │
    ├──► QA_PRIORITY_SCORE (optional, Generator + incidents)
    │         → Offene Incidents als Score-Faktor
    │
    ├──► QA_ANOMALY_DETECTION (Generator + incidents)
    │         → incident_backlog
    │         → incident_replay_gap
    │
    └──► QA_STABILITY_INDEX (optional, Generator + incidents)
              → Belastung/Bonus durch Incidents
```

---

## 9. Incident Registry – Anschlussfähigkeit

### 9.1 _registry.json (Zielstruktur)

Die Incident Registry wird aus allen `INC-*/` Verzeichnissen aggregiert. Sie ist die **einzige maschinenlesbare Quelle** für Incident-Aggregationen.

```json
{
  "schema_version": "1.0",
  "generated": "2026-03-15T12:00:00Z",
  "source": "docs/qa/incidents/",
  "incidents": [
    {
      "id": "INC-20260315-001",
      "title": "RAG-Fehler nicht in Timeline sichtbar",
      "status": "classified",
      "failure_class": "rag_silent_failure",
      "subsystem": "RAG",
      "path": "INC-20260315-001/",
      "replay_id": "REPLAY-INC-20260315-001",
      "regression_test": null
    }
  ],
  "statistik": {
    "gesamt": 0,
    "nach_status": {},
    "nach_fehlerklasse": {},
    "ohne_guard": 0
  }
}
```

### 9.2 Anschlussfähigkeit für Generatoren

| Generator | Eingabe | Ausgabe |
|-----------|---------|---------|
| generate_incident_registry | INC-*/ (incident.yaml, bindings.json, replay.yaml) | _registry.json |
| REGRESSION_CATALOG Generator | _registry.json | incidents_pro_fehlerklasse, incident_ref |
| QA_CONTROL_CENTER Generator | _registry.json | Offene Incidents, KPIs |
| QA_AUTOPILOT Generator | _registry.json | incident_kandidaten |

**Reihenfolge:** 1. generate_incident_registry → 2. übrige Generatoren (lesen _registry.json)

---

## 10. Zusammenfassung

| Artefakt | Integration |
|----------|-------------|
| **REGRESSION_CATALOG** | Incidents pro Fehlerklasse, incident_ref in Zuordnung |
| **QA_RISK_RADAR** | Keine direkte Änderung; Incidents bestätigen Risiken |
| **QA_HEATMAP** | Keine direkte Änderung; bindings.json heatmap.dimensions |
| **QA_PRIORITY_SCORE** | Optional: Offene Incidents als Score-Faktor |
| **QA_DEPENDENCY_GRAPH** | Keine Änderung; Nutzung bei Autopilot-Priorisierung |
| **QA_STABILITY_INDEX** | Optional: Incidents als Belastung/Bonus |
| **QA_CONTROL_CENTER** | Offene Incidents, KPIs, Warnsignale |
| **QA_AUTOPILOT** | Incident-Kandidaten, empfohlener Schritt |

| Neue KPIs | incidents_open, incidents_guarded, guard_rate, incidents_without_replay, replay_without_test, oldest_open_days |
| Neue Warnsignale | W1–W8 (Incidents ohne Replay, Replay ohne Test, Incident-Stau, etc.) |

---

## 11. Verweise

| Dokument | Inhalt |
|----------|--------|
| [QA_INCIDENT_REPLAY_ARCHITECTURE.md](QA_INCIDENT_REPLAY_ARCHITECTURE.md) | Überblicksarchitektur |
| [QA_INCIDENT_LIFECYCLE.md](QA_INCIDENT_LIFECYCLE.md) | Lifecycle, Governance |
| [QA_INCIDENT_ARTIFACT_STANDARD.md](QA_INCIDENT_ARTIFACT_STANDARD.md) | Verbindlicher Artefaktstandard |
| [QA_INCIDENT_REPLAY_INTEGRATION.md](QA_INCIDENT_REPLAY_INTEGRATION.md) | Detaillierte Integrationsarchitektur (Schema-Version) |
| [REGRESSION_CATALOG.md](REGRESSION_CATALOG.md) | Fehlerklassen |
| [QA_CONTROL_CENTER.md](QA_CONTROL_CENTER.md) | Steuerungsboard |
| [QA_AUTOPILOT.md](QA_AUTOPILOT.md) | Sprint-Empfehlung |

---

*QA Incident Integration – verbindlich ab 15. März 2026. Nur QA-Architektur, keine Implementierung.*
