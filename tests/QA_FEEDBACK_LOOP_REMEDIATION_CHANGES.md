# QA Feedback Loop – Critical/High Findings Remediation

**Datum:** 2026-03-15  
**Scope:** Nur critical und high Findings aus dem konsolidierten Sanierungsplan

---

## 1. Geänderte Dateien und zugehörige Findings

### 1.1 `scripts/qa/feedback_loop/utils.py`

**Warum geändert:** `load_json` lieferte bisher beliebige JSON-Strukturen (z.B. Listen) zurück; Downstream erwartet ein Dict.

**Findings adressiert:** **H5** – `load_json` validiert nicht, dass das Ergebnis ein Dict ist.

**Änderung:** Nach `json.loads()` wird `isinstance(data, dict)` geprüft; bei Nicht-Dict wird `None` zurückgegeben.

---

### 1.2 `scripts/qa/feedback_loop/normalizer.py`

**Warum geändert:** Replay-Gap und Regression-Gap wurden vermischt; Regression war global statt pro Subsystem.

**Findings adressiert:** **H1** – Replay-Gap und Regression-Gap wurden in `_subsystem_replay_gap` vermischt; **H2** – `sub_reg_gap` war global; **M1** – `incidents` wurde nicht als Liste validiert.

**Änderungen:**
- `_subsystem_replay_gap`: `binding is None` aus der Bedingung entfernt; nur noch `replay_status` prüfen.
- `_subsystem_regression_gap()` neu: Berechnet pro Subsystem den Anteil ohne Regression-Binding.
- `sub_reg_gap` nutzt nun `regression_by_sub.get(sub, ...)` statt globalem `reg_gap`.
- `incidents_raw` wird mit `isinstance(incidents_raw, list)` geprüft; bei Nicht-Liste wird `[]` verwendet.

---

### 1.3 `scripts/qa/feedback_loop/rules.py`

**Warum geändert:** FL-PRIO-002 und FL-PRIO-003 fehlte die Bedingung `incident_count > 0` (im Gegensatz zu FL-RISK-002/003).

**Findings adressiert:** **C2** – Regellogik vereinheitlicht; Update-Skripte agieren als Adapter.

**Änderung:** `state.incident_count > 0` zu beiden Bedingungen für FL-PRIO-002 und FL-PRIO-003 ergänzt.

---

### 1.4 `scripts/qa/feedback_loop/projections.py`

**Warum geändert:** `datetime.now()` im Projektionslauf verhindert Determinismus bei Tests.

**Findings adressiert:** **H3** – `generated_at` bricht Determinismus; optionaler Timestamp-Parameter ergänzt.

**Änderung:** `run_feedback_projections()` erhält `optional_timestamp: str | None = None`; wird bei `None` durch `datetime.now(timezone.utc)` ersetzt.

---

### 1.5 `scripts/qa/update_control_center.py`

**Warum geändert:** Schreibfehler wurden nicht abgefangen; `generated_at` war nicht deterministisch steuerbar.

**Findings adressiert:** **H4** – Kein Fehlerhandling um `write_text`; **H3** – `optional_timestamp` für deterministische Tests.

**Änderungen:**
- `try/except OSError` um alle `write_text`-Aufrufe; bei Fehler `LOG.error` und `return 1`.
- `--timestamp` als CLI-Argument; wird an `run_feedback_projections` und `build_control_center_output` weitergereicht.
- `build_control_center_output` erhält `optional_timestamp` und nutzt ihn für `generated_at`.

---

### 1.6 `scripts/qa/update_priority_scores.py`

**Warum geändert:** Skript hatte eigene Regellogik statt `report.rule_results` zu nutzen; Schreibfehler und Determinismus fehlten.

**Findings adressiert:** **C1** – Update-Skripte nutzen `report.rule_results` statt eigener Logik; **H4** – Schreibfehler-Handling; **H3** – `optional_timestamp`.

**Änderungen:**
- `_compute_subsystem_delta` und `_compute_failure_class_delta` entfernt.
- `_subsystem_scores_from_rule_results()`: Filtert `rule_results` für `QA_PRIORITY_SCORE`, `scores.{sub}.Score` und `scores.{sub}.contract_priority`; skaliert 0–10 → 0–100; wendet `MAX_DELTA_PER_RUN` an.
- `_failure_class_scores_from_rule_results()`: Filtert `failure_class.{fc}.priority_boost` aus `rule_results`.
- `try/except OSError` um `write_text`; `--timestamp`; `optional_timestamp` in `build_priority_score_output`.
- `dependency_graph` wird nicht mehr verwendet (Parameter entfernt).

---

### 1.7 `scripts/qa/update_risk_radar.py`

**Warum geändert:** Skript hatte eigene Regellogik statt `report.rule_results` zu nutzen; Schreibfehler und Determinismus fehlten.

**Findings adressiert:** **C1** – Update-Skripte nutzen `report.rule_results`; **H4** – Schreibfehler-Handling; **H3** – `optional_timestamp`.

**Änderungen:**
- `_compute_subsystem_risk` ersetzt durch: `_markers_and_rules_from_rule_results()` (liest Marker aus `rule_results`) und `_subsystem_risk_level_from_markers()` (Eskalationslogik bleibt im Skript).
- `_compute_failure_class_risk` ersetzt durch `_failure_class_from_rule_results()`: Filtert `failure_class.{fc}.severity` und `structural.drift_risk`.
- `try/except OSError` um `write_text`; `--timestamp`; `optional_timestamp` in `build_risk_radar_output`.

---

## 2. Change Summary

### Behobene Findings

| Priorität | Finding | Status |
|-----------|---------|--------|
| **C1** | Update-Skripte nutzen `report.rule_results` statt eigener Logik | ✅ Behoben |
| **C2** | FL-PRIO-002/003: `incident_count > 0` ergänzt | ✅ Behoben |
| **H1** | Replay-Gap und Regression-Gap getrennt in `_subsystem_replay_gap` | ✅ Behoben |
| **H2** | Per-Subsystem-Regression via `_subsystem_regression_gap()` | ✅ Behoben |
| **H3** | `optional_timestamp` für Determinismus in `projections` und allen Update-Skripten | ✅ Behoben |
| **H4** | `try/except OSError` um alle `write_text`-Aufrufe | ✅ Behoben |
| **H5** | `load_json` validiert Dict-Rückgabe | ✅ Behoben |
| **M1** | `incidents` als Liste validiert | ✅ Behoben |

### Bewusst offen gelassen

- **Medium** (außer M1): Keine weiteren Medium-Findings umgesetzt.
- **Low**: Keine Low-Findings umgesetzt.
- **Governance-Grenzen**: Unverändert; keine neuen Features.

---

## 3. Risiko-Hinweise

### Folgeanpassungen

1. **`run_feedback_loop.py`**  
   - Ruft `run_feedback_projections(inputs)` ohne `optional_timestamp` auf – unkritisch, da Parameter optional bleibt.

2. **`update_priority_scores.py` – `dependency_graph`**  
   - `--input-dependency-graph` bleibt im Parser, wird aber nicht mehr genutzt.  
   - Optional: Argument entfernen oder für spätere Nutzung dokumentieren.

3. **Failure-Class-Scores**  
   - FL-PRIO-007 (Drift) erzeugt nur `scores.{sub}.contract_priority`; Failure-Class-Scores werden nicht mehr direkt von FL-PRIO-007 beeinflusst.  
   - Verhalten entspricht der Single-Source-of-Truth-Architektur aus `rules.py`.

4. **Tests**  
   - Bestehende Tests sollten mit `--timestamp` oder `optional_timestamp` laufen, um deterministische Ergebnisse zu erhalten.

### Verifikation

- `python3 scripts/qa/update_control_center.py --dry-run`
- `python3 scripts/qa/update_priority_scores.py --dry-run`
- `python3 scripts/qa/update_risk_radar.py --dry-run`
- `python3 scripts/qa/run_feedback_loop.py`

Alle Skripte liefen erfolgreich durch.
