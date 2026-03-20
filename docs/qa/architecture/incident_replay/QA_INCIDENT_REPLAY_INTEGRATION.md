# QA Incident Replay – Integrationsarchitektur

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf  
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

### 2.1 Wie Incidents projiziert werden

| Projektion | Quelle | Ziel | Mechanismus |
|------------|--------|------|-------------|
| **Incidents pro Fehlerklasse** | bindings.json → regression_catalog.failure_class | REGRESSION_CATALOG | Neue Sektion „Incidents pro Fehlerklasse“ |
| **Test ↔ Incident** | bindings.json → regression_test | Bestehende Zuordnungstabelle | Spalte „Incident“ ergänzen |
| **Historische Bugs** | incident.yaml (closed) | Historische Bugs | Incident als strukturierter Eintrag |

**Datenfluss:** `docs/qa/incidents/INC-*/` → `_registry.json` → `REGRESSION_CATALOG` (Generator liest Registry, erweitert Catalog)

### 2.2 Neue Felder / Kategorien im Catalog

| Neues Element | Struktur | Zweck |
|---------------|----------|-------|
| **incidents_pro_fehlerklasse** | Mapping: failure_class → [incident_ids] | Welche Incidents pro Fehlerklasse? |
| **incident_ref** | Spalte in „Zuordnung: Tests → Fehlerklassen“ | Welcher Incident führte zu diesem Test? |
| **incident_guarded** | Boolean pro Fehlerklasse | Sind alle Incidents dieser Klasse guarded? |
| **offene_incidents** | Liste pro Fehlerklasse | Incidents mit Status ≠ closed/invalid/duplicate/archived |

**Beispiel-Regression-Catalog-Erweiterung:**

```markdown
## Incidents pro Fehlerklasse (aus Incident Replay)

| Fehlerklasse | Incidents | Guarded | Offen |
|--------------|-----------|---------|-------|
| rag_silent_failure | INC-20260315-001 | 1 | 0 |
| startup_ordering | – | 0 | 0 |
| optional_dependency_missing | INC-20260315-002 | 0 | 1 |

## Zuordnung: Tests → Fehlerklassen

| Datei | Test | Fehlerklasse | Incident |
|-------|------|--------------|----------|
| test_rag_retrieval_failure | test_rag_failure_emits_event | rag_silent_failure, debug_false_truth | INC-20260315-001 |
```

### 2.3 Maschinenlesbare Erweiterung (REGRESSION_CATALOG.json)

```json
{
  "incidents": {
    "rag_silent_failure": ["INC-20260315-001"],
    "optional_dependency_missing": ["INC-20260315-002"]
  },
  "incidents_guarded": {
    "rag_silent_failure": 1,
    "optional_dependency_missing": 0
  },
  "incidents_open": {
    "rag_silent_failure": 0,
    "optional_dependency_missing": 1
  }
}
```

---

## 3. QA_CONTROL_CENTER – Incident-Daten

### 3.1 Neue Sektionen / Erweiterungen

| Sektion | Inhalt | Quelle |
|---------|--------|--------|
| **8. Offene Incidents** (neu) | Anzahl, Top-3 nach Subsystem, älteste ohne Replay | _registry.json |
| **1. Gesamtstatus** (erweitert) | Metrik: Incidents offen, Incidents guarded | _registry.json |
| **7. Top-5 operative Empfehlungen** (erweitert) | Kandidat: „Incident INC-xxx als Guard umsetzen“ | _registry + Autopilot |
| **4. Aktuelle Warnsignale** (erweitert) | Warnsignal: „X Incidents ohne Replay > 2 Sprints“ | _registry.json |

### 3.2 Darstellung (konzeptionell)

**Offene Incidents:**  
- Tabelle: Rang | Incident | Subsystem | Status | Tage seit Erfassung  
- Nur Incidents mit status ∈ {new, triaged, classified, replay_defined, replay_verified, bound_to_regression}  
- Sortierung: Nach Priorität (bound_to_regression zuerst), dann nach Alter  

**Gesamtstatus:**  
- Zeile: „Incidents offen: X | guarded: Y | total: Z“

**Empfehlungen:**  
- Wenn Autopilot-Kandidat Subsystem hat und Incident mit Replay ohne Test existiert: „Incident INC-xxx (RAG) als Regression Guard umsetzen“

### 3.3 Keine UI – nur Datenstruktur

Das Control Center ist ein generiertes Markdown/JSON. Die „Integration“ bedeutet: Der Generator liest _registry.json und schreibt zusätzliche Abschnitte in QA_CONTROL_CENTER.md und QA_CONTROL_CENTER.json.

---

## 4. KPIs (Key Performance Indicators)

### 4.1 Incident-spezifische KPIs

| KPI | Definition | Berechnung | Ziel |
|-----|------------|------------|------|
| **Incidents offen** | Incidents ohne Guard (Status ≠ closed) | Count aus _registry | 0 |
| **Incidents guarded** | Incidents mit Test in CI | Count status = closed | Steigend |
| **Incidents ohne Replay** | Status ≤ classified, kein replay.yaml | Count | 0 |
| **Replay ohne Test** | replay_verified, kein regression_test | Count | 0 |
| **Ältester offener Incident** | Max(Tage seit Erfassung) für offene | Tage | < 14 |
| **Guard-Rate** | guarded / total (ohne invalid/duplicate) | Prozent | 100% |

### 4.2 Pro Fehlerklasse

| KPI | Definition |
|-----|------------|
| **Incidents pro Fehlerklasse** | Anzahl Incidents je failure_class |
| **Guarded pro Fehlerklasse** | Anteil guarded |
| **Fehlerklassen ohne Incident** | Klassen mit 0 Incidents (keine reale Bug-Historie) |

### 4.3 Pro Subsystem

| KPI | Definition |
|-----|------------|
| **Incidents pro Subsystem** | Aus bindings.json risk_radar.subsystem |
| **Offene Incidents pro Subsystem** | Für Priorisierung |

### 4.4 Aggregat-KPIs für Control Center

| KPI | Anzeige |
|-----|---------|
| **Incident Guard Rate** | 85% (17/20 guarded) |
| **Offene Incidents** | 3 |
| **Replay ohne Test** | 2 |
| **Ältester offener** | 12 Tage (INC-20260315-002) |

---

## 5. Signale an QA_AUTOPILOT

### 5.1 Neue Eingabedaten

| Eingabe | Quelle | Format |
|---------|--------|--------|
| **incident_registry** | docs/qa/incidents/_registry.json | JSON |

### 5.2 Neue Signale / Entscheidungslogik

| Signal | Bedingung | Wirkung |
|--------|-----------|---------|
| **Incident-Sprint-Kandidat** | Subsystem in Autopilot-Kandidaten UND Incident mit Replay ohne Test existiert | Zusätzlicher Kandidat: „Incident INC-xxx als Guard umsetzen“ |
| **Incident-Priorität** | Incident mit severity ≥ high, status = replay_verified | Subsystem höher priorisieren |
| **Replay-Backlog** | Incidents mit replay_verified, kein regression_test | Empfohlener Schritt: „Test für INC-xxx schreiben“ |

### 5.3 Erweiterung der Autopilot-Kandidaten

**Bestehende Kandidaten:** Aus QA_PRIORITY_SCORE, QA_HEATMAP (Subsystem + nächster Schritt)

**Neue Kandidaten:** Aus _registry.json – Incidents mit:
- status = replay_verified oder bound_to_regression
- bindings.json regression_test = null (oder Test nicht in CI)
- Subsystem passt zu Autopilot-Liste

**Sortierung:** Priority Score + „Incident hat Replay“ = Tiebreaker (höher priorisieren)

### 5.4 Beispiel Autopilot-Erweiterung (JSON)

```json
{
  "incident_kandidaten": [
    {
      "incident_id": "INC-20260315-002",
      "subsystem": "RAG",
      "status": "replay_verified",
      "regression_test": null,
      "empfohlener_schritt": "Test für ChromaDB-Failure schreiben",
      "prioritaet": "P1"
    }
  ],
  "top_incident_empfehlung": "INC-20260315-002: RAG – ChromaDB Failure als Guard umsetzen"
}
```

---

## 6. Risk Radar und Priority Score – Einfluss durch Incidents

### 6.1 Wie reale Incidents Risk Radar beeinflussen

| Einfluss | Mechanismus | Priorität |
|----------|-------------|-----------|
| **Subsystem mit Incident** | Risk Radar hat bereits Priorität. Incident bestätigt Risiko. | Bestätigung |
| **Neuer Incident, kein Test** | Subsystem mit offenem Incident → Restlücken erhöhen | P1/P2 |
| **Incident in Top-Risiko** | Subsystem mit Incident + Top-Risiko-Relevanz → Priorität beibehalten | – |
| **Incident guarded** | Subsystem mit geschlossenem Incident → Restlücken reduzieren | Entlastung |

**Konkret:**  
- Risk Radar bleibt **manuell** gepflegt.  
- Incidents werden **nicht** automatisch in QA_RISK_RADAR.md geschrieben.  
- **QA_PRIORITY_SCORE** kann aber Incident-Daten als **zusätzlichen Faktor** nutzen.

### 6.2 Erweiterung QA_PRIORITY_SCORE

| Neuer Faktor | Bedeutung | Gewichtung |
|--------------|-----------|------------|
| **Offene Incidents pro Subsystem** | Subsystem mit offenem Incident → Score +1 (oder +2 bei severity high) | Optional |
| **Incidents guarded** | Subsystem mit geschlossenem Incident → leichte Entlastung | Optional |

**Scoring-Logik (Erweiterung):**  
- `Score_Incident = +1 pro offenem Incident (Subsystem)`  
- `Score_Incident = -0.5 pro guarded Incident (Subsystem)` (optional, Entlastung)  
- Maximaler Zusatz: +2 pro Subsystem (Cap)

**Bedingung:** Nur Incidents mit status ∈ {classified, replay_defined, replay_verified, bound_to_regression} zählen als „offen“.

### 6.3 Dependency Graph

| Einfluss | Mechanismus |
|----------|-------------|
| **Kaskadenpfade** | Incident in Subsystem A → Dependency Graph zeigt: Wenn A fehlschlägt, B, C betroffen. Incident bestätigt Kaskade. |
| **Priorisierung** | Incident in Subsystem mit hoher Kaskadenreichweite → höhere Priorität für Guard |

**Keine Änderung am Dependency Graph selbst.** Incidents werden bei der **Autopilot-Priorisierung** berücksichtigt: Subsystem mit Incident + hoher Kaskadenreichweite = höherer Sprint-Kandidat.

---

## 7. Neue Warnsignale durch Incident Replay

### 7.1 Incident-spezifische Warnsignale

| Signal | Bedingung | Schwere | Reaktion |
|--------|-----------|---------|----------|
| **Incidents ohne Replay** | ≥1 Incident mit status < replay_defined, älter als 14 Tage | mittel | Replay erfassen |
| **Replay ohne Test** | ≥1 Incident mit replay_verified, kein regression_test | mittel | Test schreiben |
| **Incident-Stau** | ≥3 offene Incidents pro Subsystem | hoch | Priorisierung |
| **Fehlerklasse unguarded** | Fehlerklasse mit Incident, aber 0 guarded | niedrig | Beobachten |
| **Incident ohne Classification** | Incident mit status = new/triaged > 7 Tage | niedrig | Triage abschließen |
| **Duplicate-Rate** | >2 Incidents als duplicate in einem Sprint | niedrig | Triage verbessern |

### 7.2 Integration in QA_ANOMALY_DETECTION

| Erweiterung | Beschreibung |
|-------------|--------------|
| **Neue Anomalie-Klasse** | `incident_backlog` – Incidents ohne Guard, pro Subsystem |
| **Neue Anomalie-Klasse** | `incident_replay_gap` – Replay ohne Test |
| **Schwellen** | incidents_open ≥ 5 = Beobachtung; incidents_open ≥ 10 = Anomalie |
| **Eingabedaten** | _registry.json |

### 7.3 Warnsignale im Control Center

**Bestehende Sektion „Aktuelle Warnsignale“** wird erweitert um:

- „X Incidents ohne Replay > 14 Tage“
- „Y Replays ohne Test“
- „Subsystem Z: 3 offene Incidents“

---

## 8. QA_STABILITY_INDEX – Erweiterung

### 8.1 Mögliche Belastungsfaktoren

| Faktor | Bedingung | Abzug |
|--------|-----------|-------|
| **Offene Incidents** | incidents_open ≥ 5 | 2 |
| **Offene Incidents** | incidents_open ≥ 10 | 4 |
| **Replay ohne Test** | replay_verified ohne Test ≥ 3 | 1 |

### 8.2 Mögliche Stabilitätsboni

| Faktor | Bedingung | Bonus |
|--------|-----------|-------|
| **Incidents guarded** | incidents_guarded ≥ 5 | 1 |
| **Incident Guard Rate** | 100% (alle guarded) | 2 |

**Hinweis:** Stabilisatoren/Belastungsfaktoren sind optional. Die Integration kann schrittweise erfolgen (Iteration 1: nur Control Center, Iteration 2: Stability Index).

---

## 9. Datenfluss (Übersicht)

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

## 10. Skript-Architektur

**Vollständige Spezifikation:** [incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md](incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md)

| Skript | Zweck |
|--------|-------|
| create_incident.py | Neues Incident-Verzeichnis anlegen |
| enrich_incident.py | Incident aus Rohdaten anreichern |
| generate_replay_contract.py | replay.yaml aus incident.yaml ableiten |
| validate_incident.py | incident.yaml, replay.yaml, bindings.json validieren |
| bind_incident_to_regression.py | bindings.json erstellen/aktualisieren |
| generate_incident_registry.py | _registry.json aggregieren |
| project_incidents_to_control_center.py | Control Center um Incident-Daten erweitern |
| project_incidents_to_autopilot.py | Autopilot um Incident-Kandidaten erweitern |

---

## 11. Implementierungsreihenfolge (Empfehlung)

| Phase | Skript/Artefakt | Erweiterung |
|-------|----------|-------------|
| **1** | generate_incident_registry.py | _registry.json aus INC-*/ erzeugen |
| **2** | REGRESSION_CATALOG | Sektion „Incidents pro Fehlerklasse“, incident_ref |
| **3** | QA_CONTROL_CENTER | Offene Incidents, KPIs, Warnsignale |
| **4** | QA_AUTOPILOT | incident_kandidaten, top_incident_empfehlung |
| **5** | QA_ANOMALY_DETECTION | incident_backlog, incident_replay_gap |
| **6** | QA_PRIORITY_SCORE | Optional: Incident-Score-Faktor |
| **7** | QA_STABILITY_INDEX | Optional: Incident-Belastung/Bonus |

---

## 11. Zusammenfassung

| Artefakt | Integration |
|----------|-------------|
| **REGRESSION_CATALOG** | Incidents pro Fehlerklasse, incident_ref in Zuordnung |
| **QA_RISK_RADAR** | Keine direkte Änderung; Incidents bestätigen Risiken |
| **QA_HEATMAP** | Keine direkte Änderung; bindings.json heatmap.dimensions |
| **QA_PRIORITY_SCORE** | Optional: Offene Incidents als Score-Faktor |
| **QA_DEPENDENCY_GRAPH** | Keine Änderung; Nutzung bei Autopilot-Priorisierung |
| **QA_STABILITY_INDEX** | Optional: Incidents als Belastung/Bonus |
| **QA_AUTOPILOT** | Incident-Kandidaten, empfohlener Schritt |

| Neue KPIs | Offen, Guarded, Replay ohne Test, Guard-Rate, Ältester |
| Neue Warnsignale | Incidents ohne Replay, Replay ohne Test, Incident-Stau |

---

*QA Incident Replay Integration – Architektur, keine Implementierung.*
