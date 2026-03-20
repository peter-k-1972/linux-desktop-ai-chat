# QA Feedback Loop – Konsolidierter Sanierungsplan

**Erstellt:** 2026-03-15  
**Basis:** Architektur-, Determinismus-, Governance-, CLI/IO-Review sowie Abnahme-Checkliste  
**Ziel:** Einheitliche Priorisierung und sichere Sanierungsreihenfolge – ohne sofortigen Code-Rewrite

---

## 1. Consolidated Findings Report

### Critical

| ID | Titel | Betroffene Datei(en) | Kategorie | Ursache | Risiko wenn ungefixt | Empfohlene Korrekturrichtung |
|----|-------|----------------------|-----------|---------|----------------------|------------------------------|
| C1 | **Regel-Ergebnisse des Kerns werden nicht genutzt** | update_priority_scores.py, update_risk_radar.py | architecture | Update-Skripte implementieren eigene Deltaberechnung statt `report.rule_results` zu nutzen | Divergenz Report vs. Governance-Dateien; Kern wird obsolet; Doppelte Pflege | Update-Skripte so umbauen, dass sie `rule_results` filtern und in Zielformate überführen; Deltaberechnung entfernen |
| C2 | **Regel-Logik divergiert zwischen Kern und Update-Skripten** | feedback_loop/rules.py, update_priority_scores.py | architecture | FL-PRIO-001 bis -007 unterschiedlich implementiert (Delta-Werte, Skala, incident_count-Check) | Gleiche Inputs → unterschiedliche Outputs; schlechte Auditierbarkeit | Eine autoritative Implementierung in rules.py; Update-Skripte nur als Adapter |

---

### High

| ID | Titel | Betroffene Datei(en) | Kategorie | Ursache | Risiko wenn ungefixt | Empfohlene Korrekturrichtung |
|----|-------|----------------------|-----------|---------|----------------------|------------------------------|
| H1 | **Replay-Gap und Regression-Gap vermischt** | feedback_loop/normalizer.py | domain_logic | `_subsystem_replay_gap` zählt `binding_status is None` als „no replay“ | Falsche Replay-Gap-Werte; Replay und Regression semantisch vermischt | Nur `replay_status` in _subsystem_replay_gap prüfen; `_subsystem_regression_gap` neu einführen |
| H2 | **Keine per-Subsystem-Regression** | feedback_loop/normalizer.py | domain_logic | `sub_reg_gap` für alle Subsysteme aus globalem `reg_gap` | Subsysteme mit guter Regression werden fälschlich als problematisch markiert | `_subsystem_regression_gap` aus Incidents berechnen; pro Subsystem nutzen |
| H3 | **generated_at bricht Determinismus** | projections.py, update_*.py | determinism | `datetime.now()` in Output und Trace | Snapshot-Tests, CI-Diffs, Reproduzierbarkeit eingeschränkt | Optionalen Parameter `optional_timestamp` / `--timestamp` oder Umgebungsvariable |
| H4 | **Keine Fehlerbehandlung bei Schreibfehlern** | update_control_center.py, update_priority_scores.py, update_risk_radar.py | io/cli | `write_text` ohne try/except | Unbehandelte OSError bei Disk voll, Rechten, Read-only; keine klare Fehlermeldung | try/except OSError um alle write_text; LOG.error; return 1 |
| H5 | **load_json validiert Rückgabetyp nicht** | feedback_loop/utils.py, loader.py | io/cli | JSON wie `"true"` oder `123` wird als gültig übernommen | AttributeError bei data.get(); unklare Fehler | `isinstance(data, dict)` prüfen; bei Nicht-Dict None zurückgeben |

---

### Medium

| ID | Titel | Betroffene Datei(en) | Kategorie | Ursache | Risiko wenn ungefixt | Empfohlene Korrekturrichtung |
|----|-------|----------------------|-----------|---------|----------------------|------------------------------|
| M1 | **Keine Validierung von incidents als Liste** | feedback_loop/normalizer.py | io/cli | `incidents` kann String sein; `for inc in "invalid"` → AttributeError | Kryptische Laufzeitfehler bei kaputten Schemata | `isinstance(incidents, list)` prüfen; Fallback `[]` |
| M2 | **load_feedback_inputs_from_paths lädt kein Risk Radar** | feedback_loop/loader.py, update_risk_radar.py | architecture | Kein Parameter `risk_radar_path`; update_risk_radar lädt manuell | Inkonsistente Lade-Strategie | Loader um risk_radar_path erweitern; update_risk_radar nutzen |
| M3 | **Fehlende sort_keys in run_feedback_loop** | run_feedback_loop.py | determinism | `json.dumps` ohne sort_keys | JSON-Key-Reihenfolge kann bei Änderungen instabil werden | `sort_keys=True` ergänzen |
| M4 | **Set-Iteration ohne Sortierung** | feedback_loop/normalizer.py | determinism | `for sub in set(...) \| set(...)` | Potenziell nicht deterministisch bei künftigen Änderungen | `sorted(set(...) \| set(...))` |
| M5 | **FL-CTRL-002/003 nutzen Autopilot statt Analytics** | feedback_loop/rules.py | domain_logic | replay_ratio/reg_ratio aus supporting_evidence statt analytics.qa_coverage | Redundanz; Abweichung wenn Autopilot und Analytics unterschiedlich | Analytics als primäre Quelle; Autopilot als Fallback |
| M6 | **Phantom-Subsysteme bei leeren Incidents** | feedback_loop/normalizer.py | domain_logic | Fallback all_subs/all_fc bei leerem Set | Fiktive Subsysteme bei Projektstart ohne Daten | Fallback dokumentieren oder optional machen; ggf. leeres Ergebnis + Warning |
| M7 | **Analytics risk_signals ungenutzt** | feedback_loop/normalizer.py | domain_logic | subsystem_risk_score, failure_class_frequency nicht in Projektion | Vorberechnete Risiko-Signale gehen verloren | Optional in SubsystemFeedbackState; in Pressure/Regeln einbeziehen |
| M8 | **Drift-Failure-Classes unvollständig** | feedback_loop/normalizer.py | domain_logic | ui_state_drift, EventType-Drift nicht in DRIFT_FAILURE_CLASSES | Manche Drift-Muster werden nicht erkannt | Erweitern oder konfigurierbar machen |
| M9 | **argparse-Hilfe uneinheitlich** | update_priority_scores.py, update_risk_radar.py | io/cli | Mehrere Argumente ohne help | Schlechtere Nutzbarkeit von --help | help= für alle Argumente ergänzen |
| M10 | **Kein --trace-output -** | update_*.py | io/cli | Trace immer in Datei; kein „nur stdout“-Modus | CI/Pipelining eingeschränkt | `--trace-output -` → Trace auf stderr |
| M11 | **Tote CLI-Argumente** | update_risk_radar.py | io/cli | --input-stability-index, --input-heatmap definiert, nicht genutzt | Verwirrung; Nutzer denken, sie beeinflussen Projektion | Entfernen oder tatsächlich einbinden |

---

### Low

| ID | Titel | Betroffene Datei(en) | Kategorie | Ursache | Risiko wenn ungefixt | Empfohlene Korrekturrichtung |
|----|-------|----------------------|-----------|---------|----------------------|------------------------------|
| L1 | **FL-PRIO-007 nur für ein Subsystem** | feedback_loop/rules.py | domain_logic | `break` nach erstem drift-betroffenen Subsystem | Unklar ob gewollt; andere Subsysteme ohne contract_priority | Dokumentieren oder break entfernen |
| L2 | **FL-PRIO-002/003 ohne expliziten incident_count-Check** | feedback_loop/rules.py | domain_logic | Normalizer setzt bei 0 Incidents 0; praktisch OK | Weniger selbsterklärend; anfällig bei Änderungen | Explizit `incident_count > 0` in Regeln |
| L3 | **_extract_old_subsystem_scores ohne Typ-Check** | update_priority_scores.py | io/cli | scores kann Nicht-Liste sein | AttributeError bei abweichendem Schema | `isinstance(scores, list)` prüfen |
| L4 | **sys.path-Mutation** | run_feedback_loop.py, update_*.py | testability | sys.path.insert(0, ...) | Namenskollisionen, parallele Läufe | Üblich für Skripte; ggf. dokumentieren |
| L5 | **Kein atomisches Schreiben** | update_*.py | io/cli | Direktes write_text | Bei Abbruch teilweise geschriebene Datei | Optional: Temp-Datei + rename |
| L6 | **Relative Pfade cwd-abhängig** | Alle Skripte | io/cli | Relative Pfade relativ zu cwd | Falsche Dateien bei anderem Arbeitsverzeichnis | Dokumentieren oder gegen Projekt-Root auflösen |
| L7 | **read_text ohne Größenlimit** | update_risk_radar.py | io/cli | Ganze MD-Datei im Speicher | Theoretisch Speicherproblem bei sehr großen Dateien | Praktisch selten; optional begrenzen |

---

## 2. Widersprüche / Spannungen zwischen Findings

| Spannung | Beschreibung | Empfehlung |
|----------|--------------|------------|
| **C1/C2 vs. Stabilität** | Umstellung auf rule_results als Single Source of Truth erfordert größeren Refactor. Risiko von Regressionen. | Phase 2: Erst nach Stabilisierung (Phase 1). Kleinschrittig: Zuerst rules.py vereinheitlichen, dann Update-Skripte schrittweise anpassen. |
| **H1/H2 vs. Backward Compatibility** | Replay/Regression-Trennung und per-Subsystem-Regression ändern berechnete Werte. Bestehende Outputs können sich ändern. | Als Verbesserung kommunizieren; ggf. Vergleichstests mit Alt-Verhalten; keine Breaking Changes für Schema. |
| **H3 vs. Auditierbarkeit** | `generated_at` ist für Audit wichtig. Injizierbarer Timestamp darf Audit-Trail nicht verwässern. | Optionaler Parameter nur für Tests; Produktivläufe nutzen weiterhin datetime.now(). |
| **M5 vs. Autopilot-Abhängigkeit** | FL-CTRL-002/003 auf Analytics umstellen reduziert Abhängigkeit vom Autopilot. Autopilot könnte aber aktuellere Werte haben. | Analytics als primäre Quelle (konsistent mit Normalizer); Autopilot als Fallback wenn Analytics fehlt. |
| **M6 vs. EMPTY-Incidents-Test** | Phantom-Subsysteme sind in Abnahme-Checkliste als erwartetes Verhalten bei leeren Incidents dokumentiert. | Entweder beibehalten und dokumentieren ODER optional machen; Test anpassen. |
| **Logging vs. diff-freundliche Outputs** | Zusätzliche LOG-Zeilen bei Fehlern ändern stderr, nicht die JSON-Outputs. Kein Konflikt. | Keine Spannung. |
| **Atomisches Schreiben vs. Einfachheit** | Temp-Datei + rename erhöht Robustheit, aber Komplexität. | Phase 4; optional. |

---

## 3. Empfohlene Sanierungsreihenfolge

### Phase 1: Harte Release-Blocker

**Ziel:** Betriebssicherheit und fachliche Korrektheit ohne Architektur-Refactor.

| Reihenfolge | Finding | Begründung |
|-------------|---------|------------|
| 1.1 | H1 – Replay/Regression trennen | Fachlich falsch; beeinflusst alle Projektionen |
| 1.2 | H2 – Per-Subsystem-Regression | Ergänzt H1; gleiche Datei, zusammenhängend |
| 1.3 | H4 – Schreibfehler abfangen | Operative Stabilität; verständliche Fehlermeldungen |
| 1.4 | H5 – load_json Dict-Validierung | Verhindert AttributeError bei kaputten Dateien |
| 1.5 | M1 – incidents als Liste prüfen | Verhindert kryptische Fehler bei Schema-Abweichungen |

**Exit-Kriterium Phase 1:** Alle P1-Tests aus Abnahme-Checkliste grün; keine neuen Abstürze bei Randfällen.

---

### Phase 2: Stabilisierung

**Ziel:** Determinismus, IO-Robustheit, Konsistenz.

| Reihenfolge | Finding | Begründung |
|-------------|---------|------------|
| 2.1 | H3 – generated_at injizierbar | Ermöglicht deterministische Tests |
| 2.2 | M3 – sort_keys in run_feedback_loop | Diff-freundliche Ausgabe |
| 2.3 | M4 – Set-Iteration sortieren | Explizite Determinismus-Sicherheit |
| 2.4 | M9 – argparse help | Bessere CLI-Nutzbarkeit |
| 2.5 | L3 – _extract_old_subsystem_scores Typ-Check | Defensive Robustheit |

**Exit-Kriterium Phase 2:** DET-JSON, INVALID-JSON, STRUCT-Incidents-List (nach Fix) grün.

---

### Phase 3: Nachschärfung

**Ziel:** Architektur-Konsistenz, Datenquellen, Dokumentation.

| Reihenfolge | Finding | Begründung |
|-------------|---------|------------|
| 3.1 | C1 – rule_results nutzen | Architektur-Kern; erfordert Refactor |
| 3.2 | C2 – Regel-Logik vereinheitlichen | Mit C1 verbunden; eine autoritative Quelle |
| 3.3 | M2 – Loader risk_radar_path | Konsistente Lade-Strategie |
| 3.4 | M5 – FL-CTRL-002/003 Analytics | Einheitliche Datenquelle |
| 3.5 | M6 – Phantom-Subsysteme | Dokumentieren oder optional machen |
| 3.6 | M10 – --trace-output - | CI/Pipelining |
| 3.7 | M11 – Tote Argumente entfernen | Klarheit |

**Exit-Kriterium Phase 3:** Report und Governance-Dateien konsistent; Regel-Änderungen nur an einer Stelle.

---

### Phase 4: Optionale Verbesserungen

**Ziel:** Nice-to-have; kein Release-Blocker.

| Reihenfolge | Finding | Begründung |
|-------------|---------|------------|
| 4.1 | M7 – Analytics risk_signals | Zusatzsignal; Erweiterung |
| 4.2 | M8 – Drift-Failure-Classes erweitern | Erweiterung; konfigurierbar |
| 4.3 | L1 – FL-PRIO-007 Dokumentation | Klarheit |
| 4.4 | L2 – FL-PRIO-002/003 explizit | Selbsterklärend |
| 4.5 | L5 – Atomisches Schreiben | Robustheit bei Abbruch |
| 4.6 | L6 – Relative Pfade auflösen | Optional; Doku reicht ggf. |

---

## 4. Merge-Empfehlung

### **merge_with_conditions**

**Begründung:**

- Die Implementierung ist **Governance-konform** und funktional.
- Es gibt **keine unerlaubten Schreibzugriffe**; Dry-run ist write-frei.
- **Kritische fachliche Fehler** (Replay/Regression-Vermischung) und **fehlende Fehlerbehandlung** sollten vor Produktiveinsatz behoben werden.
- Der **Architektur-Refactor** (C1, C2) kann in einer späteren Iteration erfolgen.

**Bedingungen für Merge:**

1. **Phase 1 abgeschlossen** (H1, H2, H4, H5, M1).
2. **Minimaler Freigabekatalog** aus Abnahme-Checkliste: Alle 11 blockierenden Testfälle (HP-CC-Full, HP-PS-Full, HP-RR-Full, DRY-*, MISS-Autopilot-CC, MISS-Both-PS, CAP-Delta-PS, BND-Esc-RR, OUT-Stdout) manuell oder automatisiert bestanden.
3. **Dokumentation:** In README oder CHANGELOG vermerken, dass Replay/Regression-Trennung und Schreibfehlerbehandlung in Phase 1 geplant sind.
4. **Kein Merge**, wenn Phase 1-Fixes zu riskant erscheinen – dann `merge_blocked` bis Phase 1.

**Nach Phase 1:** `merge_ready` für QA-Pipeline-Integration.

---

## 5. Übersicht: Finding-IDs nach Kategorie

| Kategorie | Findings |
|-----------|----------|
| architecture | C1, C2, M2 |
| governance | (keine – Governance-Konformität bestätigt) |
| determinism | H3, M3, M4 |
| io/cli | H4, H5, M1, M9, M10, M11, L3, L5, L6, L7 |
| domain_logic | H1, H2, M5, M6, M7, M8, L1, L2 |
| testability | H3, L4 |

---

## 6. Abhängigkeiten zwischen Findings

```
H1 (Replay/Regression) ──┬──> H2 (per-Subsystem-Regression) [gleiche Datei, gleicher Fix]
                          │
H5 (load_json) ──────────┼──> M1 (incidents Liste) [beide defensive Validierung]
                          │
C2 (Regel-Logik) ────────┴──> C1 (rule_results nutzen) [C2 vor C1: erst vereinheitlichen, dann nutzen]

M5 (FL-CTRL Analytics) ─────> Unabhängig von C1/C2
```

**Empfehlung:** H1 und H2 zusammen umsetzen (ein PR). H5 und M1 zusammen (ein PR). C2 vor C1.
