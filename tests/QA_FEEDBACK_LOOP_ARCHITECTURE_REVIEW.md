# QA Feedback Loop – Architektur-Review

**Review-Datum:** 2026-03-15  
**Reviewer:** Principal QA-Architekt / Principal Python-Reviewer / Architektur-Auditor  
**Betroffene Bereiche:** `scripts/qa/feedback_loop/`, `update_control_center.py`, `update_priority_scores.py`, `update_risk_radar.py`

---

## 1. Gesamturteil

### **architecture_needs_revision**

Die Architektur ist grundsätzlich stimmig und Governance-konform, hat aber **kritische Inkonsistenzen** zwischen dem Feedback-Loop-Kern und den Update-Skripten. Die Regel-Ergebnisse des Kerns werden nicht für die tatsächliche Projektion genutzt; stattdessen existiert duplizierte, teils abweichende Logik in den Update-Skripten. Ohne Korrektur drohen divergierende Ergebnisse und Wartungsprobleme.

---

## 2. Positivliste

| Aspekt | Bewertung |
|--------|-----------|
| **Governance-Treue** | Keine unerlaubten Schreibzugriffe. Alle Schreibziele sind ausschließlich: QA_CONTROL_CENTER.json, QA_PRIORITY_SCORE.json, QA_RISK_RADAR.json, Trace-Dateien, optional FEEDBACK_LOOP_REPORT.json. Keine Änderungen an Incidents, Tests, Regression Catalog, Replay-Daten oder Produktcode. |
| **Modulare Trennung** | Klare Trennung: loader → normalizer → rules → projections. Modelle (models.py), Schwellenwerte (thresholds.py), Regeln (rules.py) und Trace (traces.py) sind sauber getrennt. |
| **Rule-IDs** | 17 Rule-IDs zentral in `models.py` definiert (FL-PRIO-001 bis FL-PRIO-007, FL-RISK-001 bis FL-RISK-005, FL-CTRL-001 bis FL-CTRL-005). Konsistente Benennung, wiederverwendbar. |
| **Bounded Mutation (update_priority_scores)** | `SCORE_MIN=0`, `SCORE_MAX=100`, `MAX_DELTA_PER_RUN=10`. Explizite Begrenzung gegen Score-Explosion. |
| **Bounded Escalation (update_risk_radar)** | `_apply_bounded_escalation`: maximal eine Risikostufe pro Lauf. `single_incident_not_auto_high=True` verhindert Überreaktion auf Einzelincidents. |
| **Robustheit bei fehlenden Dateien** | `load_json` gibt `None` bei Fehler; `safe_get` für verschachtelte Zugriffe; `suppressed_changes` dokumentiert nicht anwendbare Regeln; globale Warnings bei fehlenden Inputs. |
| **Deterministische Iteration** | `sorted(all_subs)`, `sorted(all_fc)` im Normalizer; `sorted(subsystem_scores.items())` in Update-Skripten; `sort_keys=True` bei JSON-Ausgabe. |
| **Trace/Audit** | Jedes Update-Skript schreibt eine Trace-Datei mit `applied_rules`, `input_sources`, `summary`. `report_to_dict` serialisiert den Report vollständig. |
| **Dokumentation** | `feedback_loop/README.md` beschreibt Architektur, Annahmen und Integrationspunkte klar. |

---

## 3. Kritische Mängel

### CRITICAL: Regel-Ergebnisse des Kerns werden nicht genutzt

**Ort:** `update_priority_scores.py`, `update_risk_radar.py`

**Problem:**  
`run_feedback_projections()` erzeugt `report.rule_results` mit `FeedbackRuleResult` für alle drei Artefakte. Die Update-Skripte **ignorieren diese Ergebnisse** und implementieren die Regellogik erneut:

- **update_priority_scores.py:** Eigene `_compute_subsystem_delta`, `_compute_failure_class_delta` – nutzt `report.per_subsystem_results` und `report.per_failure_class_results`, aber **nicht** `report.rule_results`.
- **update_risk_radar.py:** Eigene `_compute_subsystem_risk`, `_compute_failure_class_risk` – nutzt Report-States, aber **nicht** `report.rule_results`.
- **update_control_center.py:** Nutzt `report.rule_results` nur für die Trace-Ausgabe (filtert `ctrl_rules`), nicht für den eigentlichen Output. Output wird aus `report.per_subsystem_results`, `report.per_failure_class_results`, `autopilot` separat gebaut.

**Folge:** Der Feedback-Loop-Kern ist faktisch ein „Parallelsystem“ – seine Regel-Ergebnisse werden nicht für die Governance-Projektion verwendet. Die Single Source of Truth für Regellogik ist damit nicht der Kern, sondern die Update-Skripte.

---

### CRITICAL: Regel-Logik divergiert zwischen Kern und Update-Skripten

**Ort:** `feedback_loop/rules.py` vs. `update_priority_scores.py`

**Problem:**  
Die Prioritätsregeln sind in beiden Stellen unterschiedlich implementiert:

| Regel | rules.py (Kern) | update_priority_scores.py |
|-------|-----------------|---------------------------|
| FL-PRIO-001 | `delta += 1` bei `incident_count >= 2` | `delta += min(3, incident_count)` |

| FL-PRIO-002 | `delta += 1` bei `replay_gap >= 0.5` | `delta += 2` bei `replay_gap >= 0.5` **und** `incident_count > 0` |
| FL-PRIO-003 | `delta += 1` bei `regression_gap >= 0.3` | `delta += 2` bei `regression_gap >= 0.3` **und** `incident_count > 0` |
| Skala | 0–10 | 0–100 (intern), Ausgabe 1–5 |

**Folge:** Gleiche Inputs können unterschiedliche Prioritätsempfehlungen liefern, je nachdem ob man `run_feedback_loop.py` (Report) oder `update_priority_scores.py` (tatsächliche Datei) auswertet. Auditierbarkeit und Erklärbarkeit leiden.

---

### HIGH: Kein gemeinsamer Apply-Step

**Ort:** Architektur insgesamt

**Problem:**  
Die README beschreibt einen „Apply-Step“, der `rule_results` liest und in Governance-Artefakte schreibt. Stattdessen existieren drei separate Update-Skripte mit eigener Logik. Es gibt keinen zentralen Mechanismus, der `FeedbackRuleResult` in die Zielformate überführt.

**Folge:** Jede Änderung an Regeln muss an mehreren Stellen (Kern + Update-Skripte) erfolgen. Risiko von Inkonsistenzen und Fehlern.

---

### HIGH: `generated_at` bricht strikten Determinismus

**Ort:** `feedback_loop/projections.py` Zeile 45, `update_control_center.py` Zeile 265, `update_priority_scores.py` Zeile 318, `update_risk_radar.py` Zeile 307

**Problem:**  
`generated_at = datetime.now(timezone.utc).strftime(...)` ist zeitabhängig. Gleiche Inputs zu unterschiedlichen Zeitpunkten liefern unterschiedliche JSON-Outputs.

**Folge:** Reproduzierbarkeit von Tests und CI-Vergleichen ist eingeschränkt. Für deterministische Regressionstests müsste `generated_at` injizierbar sein.

---

### MEDIUM: `load_feedback_inputs_from_paths` lädt kein Risk Radar

**Ort:** `feedback_loop/loader.py`

**Problem:**  
`load_feedback_inputs_from_paths()` hat keinen Parameter für `risk_radar_path`. `inputs.risk_radar_raw` bleibt immer `None`, wenn diese Funktion verwendet wird. `update_risk_radar.py` lädt das Risk Radar manuell über `args.input_risk_radar` – außerhalb des Loaders.

**Folge:** Inkonsistente Lade-Strategie; `suppressed_changes` in projections.py würde alle QA_RISK_RADAR-Ergebnisse unterdrücken, wenn `risk_radar_raw` fehlt – aber `update_risk_radar` nutzt diese Logik ohnehin nicht.

---

### MEDIUM: Phantom-Subsysteme bei leeren Incidents

**Ort:** `feedback_loop/normalizer.py` Zeilen 166–167, 243–244

**Problem:**  
Wenn `all_subs` leer ist (keine Incidents, kein Priority Score), wird `all_subs = {"RAG", "Startup/Bootstrap", "Debug/EventBus"}` gesetzt. Analog `all_fc = {"rag_silent_failure", "async_race", "ui_state_drift"}`. Diese Subsysteme werden mit 0 Incidents in den Report aufgenommen.

**Folge:** Bei komplettem Projektstart ohne Daten erscheinen fiktive Subsysteme mit 0 Incidents. Kann zu Verwirrung führen; die Intention (Fallback für leere Daten) ist nicht dokumentiert.

---

### MEDIUM: FL-CTRL-002/003 nutzen Autopilot statt Analytics

**Ort:** `feedback_loop/rules.py` Zeilen 234–265

**Problem:**  
`replay_ratio` und `reg_ratio` werden aus `autopilot_data["supporting_evidence"]["replay_gap_refs"][0]` gelesen. Die Normalisierung nutzt dagegen `analytics.qa_coverage.replay_defined_ratio` / `regression_bound_ratio`. Zwei unterschiedliche Quellen für dieselbe semantische Information.

**Folge:** Wenn Autopilot und Analytics unterschiedliche Werte liefern (z.B. durch unterschiedliche Laufzeitpunkte), können FL-CTRL-002/003 andere Schwellen treffen als die Subsystem-Level-Replay-Gaps im Normalizer. Redundanz und potenzielle Inkonsistenz.

---

### LOW: FL-PRIO-007 nur für ein Subsystem

**Ort:** `feedback_loop/rules.py` Zeilen 114–128

**Problem:**  
Bei `drift_count >= DRIFT_COUNT_ESCALATION` wird nur für das **erste** Subsystem mit `drift_density > 0` ein `FeedbackRuleResult` erzeugt (durch `break`). Alle anderen drift-betroffenen Subsysteme erhalten kein `contract_priority`-Update.

**Folge:** Unklar, ob gewollt (Begrenzung) oder Versehen. Dokumentation fehlt.

---

### LOW: Tote CLI-Argumente in update_risk_radar

**Ort:** `update_risk_radar.py` Zeilen 381–382

**Problem:**  
`--input-stability-index` und `--input-heatmap` werden definiert, aber nicht an den Loader oder die Projektionslogik übergeben. Sie werden nirgends verwendet.

**Folge:** Tote Optionen; Nutzer könnten annehmen, diese Dateien würden die Projektion beeinflussen.

---

## 4. Konkrete Korrekturanweisungen

### 4.1 Regel-Ergebnisse als Single Source of Truth (CRITICAL)

**Ziel:** Update-Skripte müssen `report.rule_results` für die Projektion nutzen, nicht eigene Logik.

1. **update_priority_scores.py**
   - `build_subsystem_scores` und `build_failure_class_scores` so umbauen, dass sie `report.rule_results` filtern (`target_artifact == "QA_PRIORITY_SCORE"`) und daraus die neuen Scores ableiten.
   - Skalierung vereinheitlichen: Entweder Kern auf 0–100 (mit Skalierungsparameter) umstellen ODER Update-Skript führt nur Skalierung 0–10 → 1–5 durch. Keine doppelte Deltaberechnung.
   - Die Funktionen `_compute_subsystem_delta` und `_compute_failure_class_delta` entfernen oder durch einen Adapter ersetzen, der `rule_results` in das Output-Format überführt.

2. **update_risk_radar.py**
   - `build_subsystems` und `build_failure_classes` so umbauen, dass sie `report.rule_results` mit `target_artifact == "QA_RISK_RADAR"` nutzen.
   - Die Funktionen `_compute_subsystem_risk` und `_compute_failure_class_risk` durch Mapping von `FeedbackRuleResult` auf Risk-Level ersetzen.

3. **update_control_center.py**
   - Output-Struktur (`naechster_qa_sprint`, `governance_alerts`, `escalations`, `pilot_tracking`) aus `report.rule_results` mit `target_artifact == "QA_CONTROL_CENTER"` ableiten, statt aus separater Logik.

### 4.2 Regel-Logik vereinheitlichen (CRITICAL)

**Ziel:** Eine einzige Implementierung der Regeln im Kern.

1. **feedback_loop/rules.py**
   - FL-PRIO-001 bis FL-PRIO-007 als einzige autoritative Implementierung festlegen.
   - Dokumentieren, ob FL-PRIO-002/003 den Zusatz `incident_count > 0` haben sollen (empfohlen: ja, analog zu FL-RISK-002/003).
   - Skala für Priorität explizit wählen (0–10 oder 0–100) und in `models.py` / README dokumentieren.

2. **update_priority_scores.py**
   - Alle Deltaberechnungen entfernen; nur noch `rule_results` lesen und in das Zielformat (z.B. 1–5 für QA_PRIORITY_SCORE) skalieren.

### 4.3 Determinismus (HIGH)

1. **projections.py** (Zeile 45):
   ```python
   # Statt:
   generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
   # Option: Parameter optional_timestamp für Tests
   def run_feedback_projections(inputs: FeedbackLoopInputs, optional_timestamp: str | None = None) -> FeedbackProjectionReport:
       generated_at = optional_timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
   ```

2. Analog in allen Update-Skripten: `generated_at` als optionalen Parameter unterstützen (z.B. für `--timestamp` in dry-run/Test-Modus).

### 4.4 Loader erweitern (MEDIUM)

1. **loader.py**
   - `load_feedback_inputs_from_paths` um `risk_radar_path: Path | None = None` erweitern.
   - Wenn gesetzt: `risk_radar_raw = path.read_text(encoding="utf-8")` bei existierender Datei.

2. **update_risk_radar.py**
   - `load_feedback_inputs_from_paths` mit `risk_radar_path=args.input_risk_radar` aufrufen.
   - Manuelles Laden von `args.input_risk_radar` entfernen.

### 4.5 Phantom-Subsysteme (MEDIUM)

1. **normalizer.py**
   - Fallback `all_subs = {"RAG", "Startup/Bootstrap", "Debug/EventBus"}` nur anwenden, wenn explizit gewünscht (z.B. Parameter `use_fallback_subsystems: bool = False`).
   - Oder: Bei leerem `all_subs` leeres Ergebnis zurückgeben und in projections eine entsprechende `global_warning` ergänzen: „Keine Subsysteme aus Incidents oder Priority Score – Projektion leer“.

### 4.6 FL-CTRL-002/003 Datenquelle (MEDIUM)

1. **rules.py**
   - Für FL-CTRL-002/003 `analytics.qa_coverage` als primäre Quelle nutzen (über `inputs.analytics`), mit Fallback auf `autopilot.supporting_evidence.replay_gap_refs` wenn Analytics fehlt.
   - Oder: Klar dokumentieren, dass bewusst Autopilot genutzt wird (weil Autopilot die Analytics bereits aggregiert hat).

### 4.7 FL-PRIO-007 (LOW)

1. **rules.py**
   - Entweder `break` entfernen und alle Subsysteme mit `drift_density > 0` berücksichtigen.
   - Oder Kommentar ergänzen: „Nur erstes Subsystem, um Überflutung zu vermeiden“.

### 4.8 Tote Argumente (LOW)

1. **update_risk_radar.py**
   - `--input-stability-index` und `--input-heatmap` entfernen, ODER sie tatsächlich in die Projektion einbinden (z.B. für zusätzliche Risikofaktoren).

---

## 5. Mögliche Folgefehler bei Nicht-Behebung

| Mangel | Folgefehler |
|--------|-------------|
| Regel-Ergebnisse nicht genutzt | Divergenz zwischen Report und tatsächlichen Governance-Dateien; Regeln im Kern werden obsolet; Änderungen müssen doppelt gepflegt werden. |
| Divergente Regel-Logik | Unterschiedliche Prioritäten je nach Ausführungspfad; Audits können nicht auf eine konsistente Regelbasis verweisen. |
| Kein gemeinsamer Apply-Step | Jedes neue Governance-Artefakt erfordert ein weiteres Update-Skript mit eigener Logik; Wartungsaufwand steigt. |
| `generated_at` nicht injizierbar | Deterministische CI-Tests und Snapshot-Vergleiche sind nicht zuverlässig möglich. |
| Phantom-Subsysteme | Bei leeren Projekten erscheinen fiktive Subsysteme; Dashboards oder Reports können irreführend sein. |
| Zwei Datenquellen für Replay/Regression | FL-CTRL-002/003 können andere Schwellen treffen als Subsystem-Level-Berechnungen; Erklärbarkeit leidet. |

---

## 6. Zusammenfassung

Die QA Feedback Loop Architektur ist **Governance-konform** und in der Modulstruktur **sauber getrennt**. Die kritischen Punkte liegen in der **Nutzung der Regel-Ergebnisse** und der **Vereinheitlichung der Logik** zwischen Kern und Update-Skripten. Ohne die beschriebenen Korrekturen bleibt der Kern ein paralleles System ohne tatsächliche Steuerungswirkung auf die Governance-Artefakte.

**Empfehlung:** Zuerst die CRITICAL-Punkte (4.1, 4.2) adressieren, danach HIGH und MEDIUM. Die LOW-Punkte können im Rahmen der nächsten Iteration behoben werden.
