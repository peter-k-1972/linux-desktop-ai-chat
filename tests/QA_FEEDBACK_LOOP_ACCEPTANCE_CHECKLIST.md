# QA Feedback Loop – Abnahme- und Testlücken-Checkliste

**Erstellt:** 2026-03-15  
**Ziel:** Präzise Abnahme- und Testlücken-Checkliste vor Freigabe für die QA-Pipeline

---

## 1. Abnahmeurteil

### **partially-test-ready**

Die Implementierung ist funktional, aber **nicht vollständig test-ready**. Es fehlen:

- Injizierbarkeit von `generated_at` für deterministische Snapshot-Tests
- Defensive Validierung von JSON-Strukturen (z.B. `incidents` als Liste)
- Explizite Fehlerbehandlung bei Schreibfehlern
- Klare Dokumentation der erwarteten Schemata für Test-Fixtures

**Empfehlung:** Die unten genannten Testfälle können größtenteils mit Fixture-Dateien und Mock-Pfaden abgedeckt werden. Für deterministische JSON-Vergleiche muss `generated_at` vorher auf einen festen Wert gesetzt oder aus dem Vergleich ausgeschlossen werden.

---

## 2. Testlücken-Checkliste

### P1 – Kritisch (Freigabe blockierend)

| # | Testname | Ziel | Eingabekonstellation | Erwartetes Ergebnis |
|---|----------|------|----------------------|---------------------|
| 1 | **HP-CC-Full** | Happy Path Control Center | Alle Dateien vorhanden: index.json (≥1 Incident), analytics.json, QA_AUTOPILOT_V2.json, QA_CONTROL_CENTER.json, QA_PRIORITY_SCORE.json | Exit 0; QA_CONTROL_CENTER.json und Trace-Datei geschrieben; Output enthält `current_focus`, `governance_alerts`, `escalations`, `pilot_tracking` |
| 2 | **HP-PS-Full** | Happy Path Priority Scores | Alle Dateien vorhanden; QA_PRIORITY_SCORE.json mit `scores[]`; Incidents mit Subsystemen | Exit 0; QA_PRIORITY_SCORE.json und Trace geschrieben; `scores[]` enthält Subsysteme; `subsystem_scores` und `failure_class_scores` vorhanden |
| 3 | **HP-RR-Full** | Happy Path Risk Radar | Alle Dateien vorhanden; QA_RISK_RADAR.md oder .json als Baseline | Exit 0; QA_RISK_RADAR.json und Trace geschrieben; `subsystems` und `failure_classes` vorhanden; `risk_policy` dokumentiert |
| 4 | **DRY-CC** | Dry-run Control Center | `--dry-run`; alle Inputs vorhanden | Exit 0; keine Datei geschrieben; JSON auf stdout; Trace auf stderr |
| 5 | **DRY-PS** | Dry-run Priority Scores | `--dry-run`; alle Inputs vorhanden | Exit 0; keine Datei geschrieben |
| 6 | **DRY-RR** | Dry-run Risk Radar | `--dry-run`; alle Inputs vorhanden | Exit 0; keine Datei geschrieben |
| 7 | **MISS-Autopilot-CC** | Fehlende Autopilot-Datei (Control Center) | QA_AUTOPILOT_V2.json fehlt oder leer/ungültig | Exit 1; LOG.error "QA_AUTOPILOT_V2.json fehlt – Abbruch"; keine Schreibvorgänge |
| 8 | **MISS-Both-PS** | Fehlende Baseline (Priority Scores) | Weder QA_PRIORITY_SCORE.json noch incidents/index.json vorhanden | Exit 1; LOG.error "Weder QA_PRIORITY_SCORE.json noch incidents/index.json gefunden – Abbruch" |
| 9 | **CAP-Delta-PS** | Max-Delta-Capping | Input: Subsystem mit raw_delta > 10 (z.B. viele Incidents + Replay-Gap + Regression-Gap + Autopilot-Focus + Dependency) | `new_score - old_score` ≤ 10; `suppressed_changes` enthält Eintrag mit `raw_delta` und `capped_delta` |
| 10 | **BND-Esc-RR** | Bounded Risk Escalation | Input: Subsystem mit old_level=low, Signale für computed_level=critical (z.B. 3+ Incidents, hohe Gaps) | `new_risk_level` = medium (nur eine Stufe hoch von low); nicht critical |
| 11 | **OUT-Stdout** | Output auf stdout | `--output -` bei allen drei Skripten | Exit 0; JSON auf stdout; Trace-Datei trotzdem geschrieben (kein Trace auf stderr) |

---

### P2 – Hoch (vor Pipeline-Freigabe empfohlen)

| # | Testname | Ziel | Eingabekonstellation | Erwartetes Ergebnis |
|---|----------|------|----------------------|---------------------|
| 12 | **EMPTY-Incidents** | Leere Incidents | index.json mit `{"incidents": [], "schema_version": "1.0", ...}`; restliche Inputs vorhanden | Kein Crash; Output mit leeren oder Fallback-Subsystemen (RAG, Startup/Bootstrap, Debug/EventBus); Warnings in Output |
| 13 | **MISS-Incidents-CC** | Fehlende Incidents (Control Center) | incidents/index.json fehlt; Autopilot vorhanden | Exit 0 (Autopilot reicht); `global_warnings` enthält Hinweis auf fehlende Incidents |
| 14 | **MISS-Analytics** | Fehlende Analytics | incidents/analytics.json fehlt | Defaults: replay_ratio=0.5, reg_ratio=0.0; Warnings in Output; kein Crash |
| 15 | **INCONS-Analytics** | Inkonsistente Analytics | analytics.json ohne `qa_coverage`; oder `qa_coverage` ohne `replay_defined_ratio` | Fallback replay=0.5, reg=0.0; kein Crash |
| 16 | **DRIFT-Proj** | Drift-Projektion | Incidents mit `failure_class` in DRIFT_FAILURE_CLASSES (contract_schema_drift, debug_false_truth, metrics_false_success); ≥2 solche Failure-Classes | FL-PRIO-007 und/oder FL-RISK-005 angewendet; `structural.drift_risk` oder `contract_priority` in Output; Eskalation bei Drift |
| 17 | **PILOT-Track** | Pilot-Tracking | QA_AUTOPILOT_V2.json mit `pilot_constellation_matched: {id: 2, name: "RAG / ChromaDB..."}` | `pilot_tracking.pilot_2_rag_chromadb_network_failure.active` = true; `current_matched` enthält Pilot-Daten |
| 18 | **TRACE-Content** | Trace-Dateien Inhalt | Happy-Path-Lauf | Trace enthält `generated_at`, `generator`, `input_sources`, `applied_rules` (sortiert), `summary`; JSON valide |
| 19 | **BC-Priority** | Backward Compatibility QA_PRIORITY_SCORE | Bestehendes QA_PRIORITY_SCORE.json mit `scores[]`, `Prioritaet`, `Begruendung`, `Naechster_QA_Schritt`, `top3_naechste_sprints` | Output behält Struktur; `scores[]` mit `Subsystem`, `Score`, `Prioritaet`, `Begruendung`, `Naechster_QA_Schritt`; `top3_prioritaeten` und `top3_naechste_sprints` vorhanden |
| 20 | **BC-Control** | Backward Compatibility QA_CONTROL_CENTER | Bestehendes QA_CONTROL_CENTER.json mit `gesamtstatus`, `top_risiken`, `iteration` | Diese Felder in Output erhalten (`_preserve_existing_fields`); `naechster_qa_sprint` vorhanden |
| 21 | **BC-Risk** | Backward Compatibility QA_RISK_RADAR | QA_RISK_RADAR.md mit Tabelle \| Subsystem \| Priorität \| | Alte Risk-Level aus MD geparst; Output enthält `old_risk_level` pro Subsystem |
| 22 | **UNK-FC** | Unbekannte failure_class | Incident mit `failure_class: "neue_unbekannte_klasse"` | Kein Crash; Failure-Class erscheint in `failure_class_scores`/`failure_classes`; `drift_related` = false (nicht in DRIFT_FAILURE_CLASSES) |
| 23 | **UNK-Sub** | Unbekanntes Subsystem | Incident mit `subsystem: "NeuesSubsystem"` (nicht in STARTUP_CRITICAL) | Kein Crash; Subsystem erscheint in Output; `dependency_weight` = 1.0 (MEDIUM) |

---

### P3 – Mittel (Stabilität, empfohlen)

| # | Testname | Ziel | Eingabekonstellation | Erwartetes Ergebnis |
|---|----------|------|----------------------|---------------------|
| 24 | **DET-JSON** | Deterministische JSON-Ausgabe | Gleiche Inputs, zweimal hintereinander (ohne generated_at-Vergleich) | Gleiche Struktur; `sort_keys=True` → Keys sortiert; Listen-Reihenfolge stabil (sorted) |
| 25 | **DET-Timestamp** | generated_at in Output | Beliebiger Lauf | `generated_at` im ISO-8601-Format (YYYY-MM-DDTHH:MM:SSZ); in Output und Trace |
| 26 | **MISS-CC-Baseline** | Fehlendes Control Center als Input | QA_CONTROL_CENTER.json fehlt | `old_cc` = None; `change_log` enthält "Keine Vorversion"; Output wird neu erzeugt |
| 27 | **MISS-PS-Baseline** | Fehlendes Priority Score als Input | QA_PRIORITY_SCORE.json fehlt; incidents/index.json vorhanden | Lauf mit `old_scores` = {}; Subsysteme aus Incidents; Output mit neuen Scores |
| 28 | **MISS-RR-Baseline** | Fehlendes Risk Radar als Input | QA_RISK_RADAR.md fehlt | `old_risk_levels` = {}; Default "medium" pro Subsystem; Output wird erzeugt |
| 29 | **CLI-Output-Path** | Output-Pfad CLI | `--output /tmp/out.json` | Datei unter /tmp/out.json geschrieben; Verzeichnis bei Bedarf angelegt |
| 30 | **CLI-Input-Paths** | Input-Pfade CLI | `--input-incidents /path/to/index.json` etc. | Korrekte Dateien geladen; `input_sources` im Output reflektiert geladene Quellen |
| 31 | **INVALID-JSON** | Kaputte JSON-Datei | incidents/index.json enthält ungültiges JSON (z.B. `{invalid}`) | load_json gibt None; Skript reagiert je nach Pflichtfeld (CC: Abbruch wenn Autopilot fehlt; PS: Abbruch wenn beide fehlen; RR: Warnung, minimale Projektion) |
| 32 | **EMPTY-JSON** | Leere JSON-Datei | Datei mit nur `{}` | `{}` ist truthy; wird geladen; nachgelagerte Logik nutzt Defaults; ggf. Warnings |
| 33 | **RUN-Feedback-Loop** | run_feedback_loop.py | Alle Inputs vorhanden; `--output report.json` | Exit 0; FEEDBACK_LOOP_REPORT.json mit `per_subsystem_results`, `rule_results`, `escalations` |

---

### P4 – Niedrig (Nice-to-have)

| # | Testname | Ziel | Eingabekonstellation | Erwartetes Ergebnis |
|---|----------|------|----------------------|---------------------|
| 34 | **STRUCT-Incidents-List** | incidents kein Array | index.json mit `{"incidents": "string"}` | Aktuell: potenzieller AttributeError. Erwartet nach Fix: Defensive Prüfung, Fallback auf [] |
| 35 | **SMOOTH-PS** | Smoothing-Option | `--smoothing`; Delta > 5 | `capped_delta` mit Faktor 0.7; `smoothing_enabled: true` in Output |
| 36 | **DEP-Graph-PS** | Dependency Graph (Priority Scores) | QA_DEPENDENCY_GRAPH.json vorhanden | Optional genutzt; Startup-Subsysteme mit dependency_weight 1.2 |
| 37 | **RR-MD-Parse** | Risk Radar MD-Parsing | QA_RISK_RADAR.md mit Tabelle, verschiedene P1/P2/P3 | `old_risk_levels` korrekt: P1→high, P2→medium, P3→low |
| 38 | **RR-JSON-Baseline** | Risk Radar JSON als Baseline | QA_RISK_RADAR.json (Output-Format) als Input | `old_risk_level` aus `subsystems[sub]` gelesen |
| 39 | **SEV-Weights** | Severity-Gewichtung | Incidents mit severity blocker, critical, high, medium, low, cosmetic | `weighted_severity` entsprechend SEVERITY_WEIGHTS (5.0, 4.0, 3.0, 2.0, 1.0, 0.5) |
| 40 | **CLUSTER-Density** | Cluster-Dichte | index.json mit `clusters.subsystem` Dict | `cluster_density` > 0 für betroffene Subsysteme |

---

## 3. Minimaler Freigabekatalog

**Bedingung:** Die folgenden Testfälle müssen mindestens grün sein, bevor die Implementierung in die QA-Pipeline darf.

### Blockierend (alle erforderlich)

| # | Testname | Begründung |
|---|----------|------------|
| 1 | HP-CC-Full | Kernfunktion Control Center |
| 2 | HP-PS-Full | Kernfunktion Priority Scores |
| 3 | HP-RR-Full | Kernfunktion Risk Radar |
| 4 | DRY-CC | Dry-run darf keine Dateien schreiben |
| 5 | DRY-PS | Dry-run darf keine Dateien schreiben |
| 6 | DRY-RR | Dry-run darf keine Dateien schreiben |
| 7 | MISS-Autopilot-CC | Sauberer Abbruch bei fehlendem Pflicht-Input |
| 8 | MISS-Both-PS | Sauberer Abbruch bei fehlenden Pflicht-Inputs |
| 9 | CAP-Delta-PS | Bounded Mutation – Schutz vor Score-Explosion |
| 10 | BND-Esc-RR | Bounded Escalation – Schutz vor Überreaktion |
| 11 | OUT-Stdout | `--output -` für Pipelining |

### Empfohlen (vor Produktiveinsatz)

| # | Testname | Begründung |
|---|----------|------------|
| 12 | EMPTY-Incidents | Häufiger Randfall bei neuem Projekt |
| 14 | MISS-Analytics | Fallback-Verhalten |
| 16 | DRIFT-Proj | Fachlich zentral |
| 17 | PILOT-Track | Fachlich zentral |
| 18 | TRACE-Content | Auditierbarkeit |
| 19 | BC-Priority | Abwärtskompatibilität |
| 20 | BC-Control | Abwärtskompatibilität |
| 22 | UNK-FC | Robustheit bei Schema-Erweiterung |
| 23 | UNK-Sub | Robustheit bei Schema-Erweiterung |
| 31 | INVALID-JSON | Fehlertoleranz |

### Optional (spätere Iteration)

- 24 (DET-JSON) – erfordert ggf. Anpassung für `generated_at`
- 34 (STRUCT-Incidents-List) – erfordert Code-Fix
- 35–40 – Stabilität und Randfälle

---

## 4. Hinweise zur Testdurchführung

1. **Fixture-Verzeichnis:** Ein separates Verzeichnis (z.B. `tests/fixtures/feedback_loop/`) mit minimalen, gültigen JSON-Dateien für Happy Path und Randfälle.
2. **generated_at:** Für Snapshot-Tests entweder aus dem Vergleich ausschließen oder per Umgebungsvariable/Parameter injizieren.
3. **Pfade:** Tests mit `--input-*` und `--output` auf temporäre Verzeichnisse (z.B. `tmp_path` in pytest) lenken.
4. **Exit-Codes:** `sys.exit(main())` prüfen; bei Abbruch muss Exit 1 sein.
5. **Datei-Existenz:** Nach Schreibvorgängen prüfen, dass Output- und Trace-Dateien existieren und valides JSON enthalten.
6. **Governance:** Keine Tests, die Incidents, Replay-Daten, Regression Catalog oder Produktcode verändern.
