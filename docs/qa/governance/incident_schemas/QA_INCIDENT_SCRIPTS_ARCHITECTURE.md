# QA Incident Replay – Skript-Architektur

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf  
**Zweck:** Zuschnitt, Verantwortung, Inputs, Outputs und Fehlerbehandlung der Generator- und Validierungs-Skripte. Keine Implementierung – sauberer Architekturzuschnitt.

---

## 1. Übersicht

| Skript | Typ | Verantwortung |
|--------|-----|---------------|
| create_incident.py | Erzeugung | Neues Incident-Verzeichnis anlegen |
| enrich_incident.py | Anreicherung | Incident aus Rohdaten vervollständigen |
| generate_replay_contract.py | Erzeugung | replay.yaml aus incident.yaml ableiten |
| validate_incident.py | Validierung | incident.yaml gegen Schema prüfen |
| bind_incident_to_regression.py | Binding | bindings.json erstellen/aktualisieren |
| project_incidents_to_control_center.py | Projektion | Control Center um Incident-Daten erweitern |
| project_incidents_to_autopilot.py | Projektion | Autopilot um Incident-Kandidaten erweitern |

**Zusätzlich (bereits in Integration erwähnt):** generate_incident_registry.py – aggregiert INC-*/ zu _registry.json

---

## 2. create_incident.py

### 2.1 Zweck

Legt ein neues Incident-Verzeichnis mit minimaler Struktur an. Erzeugt die Verzeichnisstruktur und initiale incident.yaml, bindings.json, notes.md. Keine inhaltliche Bewertung – nur Anlage.

### 2.2 Eingaben

| Eingabe | Typ | Pflicht | Beschreibung |
|---------|-----|---------|--------------|
| **--id** | CLI | nein | Incident-ID (INC-YYYYMMDD-NNN). Falls fehlt: nächste freie ID ermitteln. |
| **--title** | CLI | ja | Kurztitel (max. 80 Zeichen) |
| **--stdin** | CLI | nein | JSON/YAML mit Rohdaten (optional) |

### 2.3 Ausgaben

| Ausgabe | Beschreibung |
|---------|--------------|
| **stdout** | Pfad zum erstellten Verzeichnis, Incident-ID |
| **exit code** | 0 = Erfolg, 1 = Fehler |

### 2.4 Gelesene Dateien

| Datei | Zweck |
|-------|-------|
| docs/qa/incidents/_registry.json | Nächste freie ID ermitteln (falls --id fehlt) |
| docs/qa/REGRESSION_CATALOG.md | Fehlerklassen-Liste für Validierung (optional) |

### 2.5 Geschriebene Dateien

| Datei | Inhalt |
|-------|--------|
| docs/qa/incidents/INC-YYYYMMDD-NNN/incident.yaml | Minimale Struktur (schema_version, identity, detection, environment, classification, behavior, qa) mit Platzhaltern |
| docs/qa/incidents/INC-YYYYMMDD-NNN/bindings.json | Minimale Struktur (schema_version, identity, regression_catalog, risk_radar, heatmap, status, meta) mit Platzhaltern |
| docs/qa/incidents/INC-YYYYMMDD-NNN/notes.md | Leere Vorlage mit ## Review-Notizen |
| docs/qa/incidents/INC-YYYYMMDD-NNN/evidence/.gitkeep | Leeres Verzeichnis |
| docs/qa/incidents/INC-YYYYMMDD-NNN/fixtures/.gitkeep | Leeres Verzeichnis |
| docs/qa/incidents/INC-YYYYMMDD-NNN/derived/.gitkeep | Leeres Verzeichnis |

### 2.6 Angewendete Regeln

| Regel | Beschreibung |
|-------|--------------|
| INCIDENT_YAML_FIELD_STANDARD | Minimale Pflichtfelder für new |
| QA_INCIDENT_ARTIFACT_STANDARD | Verzeichnisstruktur |
| ID-Format | INC-YYYYMMDD-NNN, eindeutig |

### 2.7 Fehlerfälle

| Fehler | Bedingung | Reaktion |
|--------|-----------|----------|
| ID existiert bereits | Verzeichnis INC-xxx bereits vorhanden | Exit 1, Meldung |
| Ungültige ID | Format nicht INC-YYYYMMDD-NNN | Exit 1, Meldung |
| Titel zu lang | > 80 Zeichen | Exit 1 oder Truncate mit Warnung |
| incidents/ nicht beschreibbar | Keine Schreibrechte | Exit 1, Meldung |

---

## 3. enrich_incident.py

### 3.1 Zweck

Reichert ein bestehendes Incident aus Rohdaten an. Liest incident.yaml, wendet Heuristiken an (z.B. failure_class aus Titel/Description), schlägt Werte vor oder setzt sie. Keine automatische Klassifikation ohne Review – eher Vorschläge oder teilautomatische Vervollständigung.

### 3.2 Eingaben

| Eingabe | Typ | Pflicht | Beschreibung |
|---------|-----|---------|--------------|
| **incident_id** | CLI/Arg | ja | INC-YYYYMMDD-NNN |
| **--source** | CLI | nein | Pfad zu Rohdaten (JSON/YAML) |
| **--dry-run** | CLI | nein | Nur Vorschläge ausgeben, nichts schreiben |
| **--apply** | CLI | nein | Vorschläge anwenden (nur sichere Felder) |

### 3.3 Ausgaben

| Ausgabe | Beschreibung |
|---------|--------------|
| **stdout** | Vorschläge, Diff-ähnliche Ausgabe |
| **incident.yaml** | Aktualisiert (wenn --apply) |
| **exit code** | 0 = OK, 1 = Fehler, 2 = Validierungsfehler |

### 3.4 Gelesene Dateien

| Datei | Zweck |
|-------|-------|
| docs/qa/incidents/INC-xxx/incident.yaml | Bestehendes Incident |
| docs/qa/REGRESSION_CATALOG.md | Fehlerklassen für Vorschläge |
| docs/qa/QA_RISK_RADAR.md | Subsysteme für Vorschläge |
| [--source] | Rohdaten |

### 3.5 Geschriebene Dateien

| Datei | Bedingung |
|-------|-----------|
| docs/qa/incidents/INC-xxx/incident.yaml | Nur bei --apply, nur wenn Anreicherung möglich |
| docs/qa/incidents/INC-xxx/derived/enrichment_suggestions.json | Optional: Vorschläge speichern |

### 3.6 Angewendete Regeln

| Regel | Beschreibung |
|-------|--------------|
| INCIDENT_YAML_FIELD_STANDARD | Nur gültige Werte setzen |
| REGRESSION_CATALOG | failure_class muss existieren |
| QA_RISK_RADAR | subsystem muss existieren |
| Keine Überschreibung von Review-Feldern | classification nur wenn leer |

### 3.7 Fehlerfälle

| Fehler | Bedingung | Reaktion |
|--------|-----------|----------|
| Incident nicht gefunden | Verzeichnis existiert nicht | Exit 1 |
| incident.yaml ungültig | YAML-Parse-Fehler | Exit 2 |
| Rohdaten ungültig | --source Parse-Fehler | Exit 1 |
| Konflikt | Vorschlag widerspricht bestehendem Wert | Nur anzeigen, nicht überschreiben (oder --force) |

---

## 4. generate_replay_contract.py

### 4.1 Zweck

Leitet aus incident.yaml ein replay.yaml ab. Nutzt behavior.repro_steps, classification, environment. Erzeugt einen ersten Entwurf – kein vollständiger Vertrag, sondern Vorlage. Menschliche Nachbearbeitung erforderlich.

### 4.2 Eingaben

| Eingabe | Typ | Pflicht | Beschreibung |
|---------|-----|---------|--------------|
| **incident_id** | CLI/Arg | ja | INC-YYYYMMDD-NNN |
| **--replay-type** | CLI | nein | replay_type.type (Vorschlag) |
| **--overwrite** | CLI | nein | Bestehendes replay.yaml überschreiben |

### 4.3 Ausgaben

| Ausgabe | Beschreibung |
|---------|--------------|
| **stdout** | Hinweise, abgeleitete Werte |
| **replay.yaml** | Neu oder aktualisiert |
| **exit code** | 0 = Erfolg, 1 = Fehler |

### 4.4 Gelesene Dateien

| Datei | Zweck |
|-------|-------|
| docs/qa/incidents/INC-xxx/incident.yaml | Quelle für preconditions, execution, assertion_contract |
| docs/qa/incidents/_schema/replay.schema.yaml | Schema für Validierung |
| docs/qa/REGRESSION_CATALOG.md | failure_class |
| docs/qa/QA_HEATMAP.json | mapping.test_domains, risk_axes |

### 4.5 Geschriebene Dateien

| Datei | Bedingung |
|-------|-----------|
| docs/qa/incidents/INC-xxx/replay.yaml | Neu oder bei --overwrite |
| docs/qa/incidents/INC-xxx/incident.yaml | qa.replay_id setzen (falls replay neu) |

### 4.6 Angewendete Regeln

| Regel | Beschreibung |
|-------|--------------|
| REPLAY_YAML_FIELD_STANDARD | Vollständige Pflichtfelder |
| incident_id → replay_id | REPLAY-INC-xxx |
| behavior.repro_steps → execution.steps | Transformation |
| behavior.expected/actual → assertion_contract | success/failure ableiten |
| classification → mapping | failure_class, subsystem |

### 4.7 Fehlerfälle

| Fehler | Bedingung | Reaktion |
|--------|-----------|----------|
| Incident nicht gefunden | Verzeichnis existiert nicht | Exit 1 |
| incident.yaml ungültig | Parse-Fehler | Exit 1 |
| incident status < classified | failure_class fehlt | Exit 1, Hinweis |
| replay.yaml existiert | Ohne --overwrite | Exit 1, Hinweis |
| Abgeleitete Werte unvollständig | execution.steps leer | Warnung, Platzhalter |

---

## 5. validate_incident.py

### 5.1 Zweck

Validiert incident.yaml, replay.yaml, bindings.json gegen die jeweiligen Schemas. Prüft Lifecycle-Bedingungen, Referenzen, Konsistenz. Keine Änderung – nur Prüfung.

### 5.2 Eingaben

| Eingabe | Typ | Pflicht | Beschreibung |
|---------|-----|---------|--------------|
| **incident_id** | CLI/Arg | nein | INC-YYYYMMDD-NNN. Falls fehlt: alle Incidents. |
| **--strict** | CLI | nein | Auch optionale Regeln als Fehler werten |
| **--schema** | CLI | nein | Pfad zu benutzerdefiniertem Schema |

### 5.3 Ausgaben

| Ausgabe | Beschreibung |
|---------|--------------|
| **stdout** | Validierungsergebnis (OK / Fehlerliste) |
| **exit code** | 0 = alle OK, 1 = mindestens ein Fehler |
| **derived/validierung.json** | Optional: strukturiertes Ergebnis pro Incident |

### 5.4 Gelesene Dateien

| Datei | Zweck |
|-------|-------|
| docs/qa/incidents/INC-xxx/incident.yaml | Zu validieren |
| docs/qa/incidents/INC-xxx/replay.yaml | Falls vorhanden |
| docs/qa/incidents/INC-xxx/bindings.json | Falls vorhanden |
| docs/qa/incidents/_schema/incident.schema.yaml | Schema |
| docs/qa/incidents/_schema/replay.schema.yaml | Schema |
| docs/qa/incidents/_schema/bindings.schema.json | Schema |
| docs/qa/REGRESSION_CATALOG.md | failure_class existiert |
| docs/qa/QA_RISK_RADAR.md | subsystem existiert |
| docs/qa/incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md | Übergangsregeln |

### 5.5 Geschriebene Dateien

| Datei | Bedingung |
|-------|-----------|
| docs/qa/incidents/INC-xxx/derived/validierung.json | Bei Validierung eines einzelnen Incidents |

### 5.6 Angewendete Regeln

| Regel | Beschreibung |
|-------|--------------|
| INCIDENT_YAML_FIELD_STANDARD | Pflichtfelder, erlaubte Werte |
| REPLAY_YAML_FIELD_STANDARD | Pflichtfelder, erlaubte Werte |
| BINDINGS_JSON_FIELD_STANDARD | Pflichtfelder, erlaubte Werte |
| QA_INCIDENT_REPLAY_LIFECYCLE | Statusübergänge, Bedingungen |
| V1–V7 (Validierungsregeln) | Aus Feldstandards |

### 5.7 Fehlerfälle

| Fehler | Bedingung | Reaktion |
|--------|-----------|----------|
| Schema nicht gefunden | _schema/ fehlt | Exit 1 |
| YAML/JSON Parse-Fehler | Syntaxfehler | Fehler ausgeben, Exit 1 |
| Pflichtfeld fehlt | Schema-Verletzung | Fehler ausgeben |
| Ungültiger Wert | Enum/Pattern verletzt | Fehler ausgeben |
| Lifecycle-Verletzung | z.B. classified ohne failure_class | Fehler ausgeben |
| Referenz fehlt | evidence ref, duplicate_of | Fehler oder Warnung |
| ID ≠ Verzeichnisname | identity.id ≠ INC-xxx | Fehler ausgeben |

---

## 6. bind_incident_to_regression.py

### 6.1 Zweck

Erstellt oder aktualisiert bindings.json für ein Incident. Kann aus incident.yaml und replay.yaml ableiten (failure_class, subsystem, heatmap.dimensions). Setzt regression_test wenn Test-Pfad angegeben. Aktualisiert status.binding_status.

### 6.2 Eingaben

| Eingabe | Typ | Pflicht | Beschreibung |
|---------|-----|---------|--------------|
| **incident_id** | CLI/Arg | ja | INC-YYYYMMDD-NNN |
| **--regression-test** | CLI | nein | Pfad zum Test (z.B. tests/foo.py::test_bar) |
| **--status** | CLI | nein | binding_status (proposed, validated, catalog_bound, …) |
| **--auto** | CLI | nein | Maschinell ableitbare Felder setzen |

### 6.3 Ausgaben

| Ausgabe | Beschreibung |
|---------|--------------|
| **stdout** | Gesetzte/aktualisierte Felder |
| **bindings.json** | Neu oder aktualisiert |
| **exit code** | 0 = Erfolg, 1 = Fehler |

### 6.4 Gelesene Dateien

| Datei | Zweck |
|-------|-------|
| docs/qa/incidents/INC-xxx/incident.yaml | classification, qa.status |
| docs/qa/incidents/INC-xxx/replay.yaml | mapping.test_domains, risk_axes |
| docs/qa/incidents/INC-xxx/bindings.json | Falls vorhanden, merge |
| docs/qa/REGRESSION_CATALOG.md | failure_class validieren |
| docs/qa/QA_RISK_RADAR.md | subsystem validieren |
| docs/qa/QA_HEATMAP.json | dimensions validieren |
| docs/qa/QA_AUTOPILOT.json | recommended_test_art, recommended_step |
| tests/ | Test existiert? (bei --regression-test) |

### 6.5 Geschriebene Dateien

| Datei | Bedingung |
|-------|-----------|
| docs/qa/incidents/INC-xxx/bindings.json | Immer (neu oder aktualisiert) |

### 6.6 Angewendete Regeln

| Regel | Beschreibung |
|-------|--------------|
| BINDINGS_JSON_FIELD_STANDARD | Vollständige Struktur |
| failure_class ∈ REGRESSION_CATALOG | Validierung |
| subsystem ∈ QA_RISK_RADAR | Validierung |
| meta.generated_fields | Bei --auto: Liste der gesetzten Felder |
| status.binding_status | Nur erlaubte Übergänge |

### 6.7 Fehlerfälle

| Fehler | Bedingung | Reaktion |
|--------|-----------|----------|
| Incident nicht gefunden | Verzeichnis existiert nicht | Exit 1 |
| incident.yaml fehlt classification | failure_class, subsystem fehlen | Exit 1 |
| failure_class ungültig | Nicht in REGRESSION_CATALOG | Exit 1 |
| subsystem ungültig | Nicht in QA_RISK_RADAR | Exit 1 |
| regression_test Pfad ungültig | Test existiert nicht | Exit 1 oder Warnung |
| Status-Übergang ungültig | proposed → catalog_bound ohne Test | Exit 1 |

---

## 7. project_incidents_to_control_center.py

### 7.1 Zweck

Projiziert Incident-Daten in das QA Control Center. Liest _registry.json (oder aggregiert aus INC-*/), erweitert QA_CONTROL_CENTER.md und QA_CONTROL_CENTER.json um Offene Incidents, KPIs, Warnsignale. Kann als Modul in generate_qa_control_center.py integriert oder als separater Schritt laufen.

### 7.2 Eingaben

| Eingabe | Typ | Pflicht | Beschreibung |
|---------|-----|---------|--------------|
| **--registry** | CLI | nein | Pfad zu _registry.json. Default: docs/qa/incidents/_registry.json |
| **--merge** | CLI | nein | In bestehendes Control Center mergen (sonst nur Incident-Abschnitt ausgeben) |

### 7.3 Ausgaben

| Ausgabe | Beschreibung |
|---------|--------------|
| **stdout** | Kurze Summary (Anzahl offen, guarded, Warnsignale) |
| **QA_CONTROL_CENTER.md** | Erweitert um Sektion 8 (Offene Incidents), KPIs in Sektion 1 |
| **QA_CONTROL_CENTER.json** | Erweitert um incidents_offen, incidents_guarded, incident_warnsignale |
| **exit code** | 0 = Erfolg, 1 = Fehler |

### 7.4 Gelesene Dateien

| Datei | Zweck |
|-------|-------|
| docs/qa/incidents/_registry.json | Incident-Daten |
| docs/qa/QA_CONTROL_CENTER.json | Bestehendes Control Center (bei --merge) |
| docs/qa/QA_CONTROL_CENTER.md | Bestehendes Control Center (bei --merge) |
| docs/qa/QA_INCIDENT_REPLAY_INTEGRATION.md | KPI-Definitionen, Sektionsstruktur |

### 7.5 Geschriebene Dateien

| Datei | Bedingung |
|-------|-----------|
| docs/qa/QA_CONTROL_CENTER.md | Bei --merge oder wenn Generator-Integration |
| docs/qa/QA_CONTROL_CENTER.json | Bei --merge oder wenn Generator-Integration |

### 7.6 Angewendete Regeln

| Regel | Beschreibung |
|-------|--------------|
| QA_INCIDENT_REPLAY_INTEGRATION | Sektion 8, KPIs, Warnsignale |
| Nur offene Incidents | status ∉ {closed, invalid, duplicate, archived} |
| Sortierung | Nach Priorität, dann Alter |
| Schwellen | Incidents ohne Replay > 14 Tage = Warnsignal |

### 7.7 Fehlerfälle

| Fehler | Bedingung | Reaktion |
|--------|-----------|----------|
| Registry nicht gefunden | _registry.json fehlt | Exit 1 oder leere Sektion (0 Incidents) |
| Registry ungültig | JSON-Parse-Fehler | Exit 1 |
| Control Center nicht beschreibbar | Keine Schreibrechte | Exit 1 |
| Merge-Konflikt | Control Center von anderem Prozess geändert | Warnung, überschreiben |

---

## 8. project_incidents_to_autopilot.py

### 8.1 Zweck

Projiziert Incident-Daten in den QA Autopilot. Liest _registry.json, identifiziert Incident-Kandidaten (Replay ohne Test, Subsystem in Autopilot-Liste), erweitert QA_AUTOPILOT.json um incident_kandidaten und top_incident_empfehlung. Kann als Modul in generate_qa_autopilot.py integriert oder als separater Schritt laufen.

### 8.2 Eingaben

| Eingabe | Typ | Pflicht | Beschreibung |
|---------|-----|---------|--------------|
| **--registry** | CLI | nein | Pfad zu _registry.json |
| **--merge** | CLI | nein | In bestehendes Autopilot mergen |

### 8.3 Ausgaben

| Ausgabe | Beschreibung |
|---------|--------------|
| **stdout** | Kurze Summary (Anzahl Incident-Kandidaten, Top-Empfehlung) |
| **QA_AUTOPILOT.json** | Erweitert um incident_kandidaten, top_incident_empfehlung |
| **QA_AUTOPILOT.md** | Erweitert um Incident-Abschnitt (falls vorhanden) |
| **exit code** | 0 = Erfolg, 1 = Fehler |

### 8.4 Gelesene Dateien

| Datei | Zweck |
|-------|-------|
| docs/qa/incidents/_registry.json | Incident-Daten |
| docs/qa/QA_AUTOPILOT.json | Bestehende Kandidaten (bei --merge) |
| docs/qa/QA_PRIORITY_SCORE.json | Subsystem-Priorität |
| docs/qa/QA_INCIDENT_REPLAY_INTEGRATION.md | Signale, Bedingungen |

### 8.5 Geschriebene Dateien

| Datei | Bedingung |
|-------|-----------|
| docs/qa/QA_AUTOPILOT.json | Bei --merge oder Generator-Integration |
| docs/qa/QA_AUTOPILOT.md | Falls als Markdown-Generator |

### 8.6 Angewendete Regeln

| Regel | Beschreibung |
|-------|--------------|
| QA_INCIDENT_REPLAY_INTEGRATION | Incident-Sprint-Kandidat, Replay-Backlog |
| Bedingung: replay_verified oder bound_to_regression | Ohne regression_test |
| Subsystem in Autopilot-Kandidaten | Priorisierung |
| severity ≥ high | Höhere Priorität |

### 8.7 Fehlerfälle

| Fehler | Bedingung | Reaktion |
|--------|-----------|----------|
| Registry nicht gefunden | _registry.json fehlt | Exit 1 oder leere incident_kandidaten |
| Registry ungültig | JSON-Parse-Fehler | Exit 1 |
| Autopilot nicht beschreibbar | Keine Schreibrechte | Exit 1 |

---

## 9. Zusätzlich: generate_incident_registry.py

### 9.1 Zweck

Aggregiert alle Incident-Verzeichnisse zu _registry.json. Liest incident.yaml, replay.yaml, bindings.json aus jedem INC-*/, baut Statistik (nach Status, Fehlerklasse, Subsystem), schreibt _registry.json. Wird von project_incidents_to_* als Eingabe genutzt.

### 9.2 Eingaben

| Eingabe | Typ | Pflicht | Beschreibung |
|---------|-----|---------|--------------|
| **--incidents-dir** | CLI | nein | Pfad zu docs/qa/incidents/ |
| **--validate** | CLI | nein | Nur valide Incidents aufnehmen |

### 9.3 Ausgaben

| Ausgabe | Beschreibung |
|---------|--------------|
| **stdout** | Statistik (gesamt, nach Status, nach Fehlerklasse) |
| **_registry.json** | Aggregiertes Register |
| **exit code** | 0 = Erfolg, 1 = Fehler |

### 9.4 Gelesene Dateien

| Datei | Zweck |
|-------|-------|
| docs/qa/incidents/INC-*/incident.yaml | Pro Incident |
| docs/qa/incidents/INC-*/replay.yaml | Pro Incident (falls vorhanden) |
| docs/qa/incidents/INC-*/bindings.json | Pro Incident (falls vorhanden) |

### 9.5 Geschriebene Dateien

| Datei | Bedingung |
|-------|-----------|
| docs/qa/incidents/_registry.json | Immer |

### 9.6 Angewendete Regeln

| Regel | Beschreibung |
|-------|--------------|
| Nur INC-* Verzeichnisse | Ignoriere _schema, _registry |
| Statistik | nach_status, nach_fehlerklasse, nach_subsystem, ohne_guard |
| Abgeleitet | _registry ist abgeleitet, nie manuell bearbeiten |

### 9.7 Fehlerfälle

| Fehler | Bedingung | Reaktion |
|--------|-----------|----------|
| incident.yaml ungültig | Parse-Fehler | Incident überspringen, Warnung |
| Keine Incidents | Kein INC-* Verzeichnis | Leere Registry, Exit 0 |
| incidents/ nicht beschreibbar | Keine Schreibrechte | Exit 1 |

---

## 10. Abhängigkeiten und Reihenfolge

```
create_incident.py          → INC-*/ (neu)
enrich_incident.py          → INC-*/incident.yaml (bestehend)
generate_replay_contract.py → INC-*/replay.yaml (nach classified)
validate_incident.py        → (jederzeit, lesend)
bind_incident_to_regression.py → INC-*/bindings.json (nach replay)

generate_incident_registry.py → _registry.json
    │
    ├── project_incidents_to_control_center.py → QA_CONTROL_CENTER
    └── project_incidents_to_autopilot.py     → QA_AUTOPILOT
```

**Empfohlene Reihenfolge (Pipeline):**
1. create_incident.py (bei neuem Bug)
2. enrich_incident.py (optional)
3. validate_incident.py (vor classified)
4. generate_replay_contract.py (nach classified)
5. validate_incident.py (nach replay)
6. bind_incident_to_regression.py (bei Test-Zuordnung)
7. generate_incident_registry.py
8. project_incidents_to_control_center.py
9. project_incidents_to_autopilot.py

---

## 11. Verzeichnis der Skripte

| Skript | Pfad (empfohlen) |
|--------|------------------|
| create_incident.py | scripts/qa/incidents/create_incident.py |
| enrich_incident.py | scripts/qa/incidents/enrich_incident.py |
| generate_replay_contract.py | scripts/qa/incidents/generate_replay_contract.py |
| validate_incident.py | scripts/qa/incidents/validate_incident.py |
| bind_incident_to_regression.py | scripts/qa/incidents/bind_incident_to_regression.py |
| project_incidents_to_control_center.py | scripts/qa/incidents/project_incidents_to_control_center.py |
| project_incidents_to_autopilot.py | scripts/qa/incidents/project_incidents_to_autopilot.py |
| generate_incident_registry.py | scripts/qa/incidents/generate_incident_registry.py |

**Alternativ:** Alle unter scripts/qa/ mit Präfix incident_ (incident_create.py, incident_validate.py, …).

---

*QA Incident Scripts Architecture – Architektur, keine Implementierung.*
