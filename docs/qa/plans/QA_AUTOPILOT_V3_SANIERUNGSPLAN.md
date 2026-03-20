# QA Autopilot v3 – Konsolidierter Sanierungsplan

**Erstellt:** 2026-03-15  
**Basis:** Architektur-/Governance-Review, Fachlogik-Review, Determinismus-/IO-Review  
**Status:** Planung – noch keine Umsetzung

---

## 1. Consolidated Findings Report

### Critical

| ID | Titel | Datei(en) | Kategorie | Ursache | Risiko | Korrekturrichtung |
|----|-------|-----------|-----------|---------|--------|-------------------|
| **C1** | Regression-Binding ignoriert Incident-Status | `scripts/qa/autopilot_v3/rules.py` (Z. 220–230) | domain_logic, governance | Nur `binding_status` geprüft; `bound_to_regression` und `closed` sind qa.status-Werte, nicht binding_status | Falsche Translation-Gaps für geschlossene Incidents; Verletzung Schema-Konsistenz | `inc.get("status") in ("bound_to_regression", "closed")` zusätzlich prüfen; Logik an Normalizer angleichen |
| **C2** | Laufzeitfehler bei ungültigem Score in QA_PRIORITY_SCORE | `scripts/qa/autopilot_v3/rules.py` (Z. 235) | determinism, io/cli | `int(x.get("Score", 0))` wirft bei `""`, `"high"`, `None` oder nicht-numerischen Werten; `s.get()` crasht bei nicht-Dict-Einträgen in `scores` | Unhandled Exception, Abbruch bei fehlerhaften oder unvollständigen Daten | `_safe_score()` mit try/except; Filter `scores = [s for s in scores if isinstance(s, dict)]` |

---

### High

| ID | Titel | Datei(en) | Kategorie | Ursache | Risiko | Korrekturrichtung |
|----|-------|-----------|-----------|---------|--------|-------------------|
| **H1** | Toter Code – autopilot_v3/utils.py | `scripts/qa/autopilot_v3/utils.py` | architecture | Datei wird nirgends importiert; Feedback-Loop hat eigene Utils | Verwirrung, Wartungsaufwand, Inkonsistenz-Risiko | Datei löschen oder sinnvoll integrieren (empfohlen: löschen) |
| **H2** | load_json prüft nicht path.is_file() | `scripts/qa/feedback_loop/utils.py` (Z. 38–48) | io/cli | Nur `path.exists()`; Verzeichnisse führen zu IsADirectoryError | Unklare Fehler bei Verwechslung Pfad/Datei | `if not path.is_file(): return None` ergänzen |
| **H3** | load_json nicht robust gegen path=None | `scripts/qa/feedback_loop/utils.py` (Z. 38) | io/cli | `path.exists()` bei `path=None` → AttributeError | Crash bei fehlerhaften Aufrufern | `if path is None: return None` am Anfang |

---

### Medium

| ID | Titel | Datei(en) | Kategorie | Ursache | Risiko | Korrekturrichtung |
|----|-------|-----------|-----------|---------|--------|-------------------|
| **M1** | Architektur-Dokumentation binding_status unvollständig | `docs/qa/QA_AUTOPILOT_V3_ARCHITECTURE.md` (Z. 86) | governance | Nur `binding_status != catalog_bound` dokumentiert; status nicht erwähnt | Falsche Implementierung bei zukünftigen Änderungen | Tabelle um „status ∉ {bound_to_regression, closed}“ ergänzen |
| **M2** | mkdir-Fehler nicht spezifisch behandelt | `scripts/qa/generate_autopilot_v3.py` (Z. 132, 144) | io/cli | mkdir und write_text im gleichen try-Block; generische Exception-Meldung | Unklare Fehlermeldung bei Verzeichnisproblemen | mkdir in eigenem try/except; spezifische LOG.error für Verzeichnis vs. Schreibfehler |
| **M3** | supporting_evidence-Listen ohne explizite Sortierung | `scripts/qa/autopilot_v3/projections.py` (Z. 116–117) | determinism | `list(dict.keys())` – Reihenfolge implizit aus Normalizer | Potentielle Nicht-Reproduzierbarkeit bei Änderungen am Normalizer | `sorted(report.per_subsystem_results.keys())` bzw. `sorted(...per_failure_class_results.keys())` |
| **M4** | Dry-Run: Trace bei --trace-output - nicht ausgegeben | `scripts/qa/generate_autopilot_v3.py` (Z. 122–127) | io/cli | Bedingung `if str(args.trace_output) != "-"` blendet Trace aus, wenn "-" gewählt | Inkonsistent zu --output -; Trace geht verloren | Bei --trace-output - Trace auf stderr ausgeben (analog zu --output -) |
| **M5** | event_contract_guard bei einem Incident | `scripts/qa/autopilot_v3/rules.py` (Z. 151) | domain_logic | Schwellwert ≥1; failure_replay_guard und startup haben ≥2 | Viele Guard-Gaps bei Einzelincidents; Rauschen | Schwellwert auf ≥2 erhöhen |
| **M6** | ui_state_drift nicht in DRIFT_FAILURE_CLASSES | `scripts/qa/autopilot_v3/models.py` | domain_logic | ui_state_drift in EVENT_CONTRACT_FC, aber nicht in DRIFT_FAILURE_CLASSES | Uneinheitliche Behandlung; missing_contract_test für ui_state_drift fehlt | Entweder hinzufügen oder Begründung dokumentieren |
| **M7** | Translation-Gaps erzeugen keine Backlog-Einträge | `scripts/qa/autopilot_v3/projections.py` | domain_logic | Backlog nur aus test_gaps + guard_gaps; translation_gaps fließen nicht ein | Diskrepanz: viele Translation-Gaps, wenige Backlog-Einträge | Design-Entscheidung: dokumentieren oder aggregierte Backlog-Einträge einführen |

---

### Low

| ID | Titel | Datei(en) | Kategorie | Ursache | Risiko | Korrekturrichtung |
|----|-------|-----------|-----------|---------|--------|-------------------|
| **L1** | Translation-Gap-Priorität unabhängig von Severity | `scripts/qa/autopilot_v3/rules.py` (Z. 207, 227) | domain_logic | Alle incident_not_bound_to_replay/regression haben priority="medium" | High-Severity-Incidents werden nicht höher priorisiert | `priority = "high" if (inc.get("severity") or "").lower() == "high" else "medium"` |
| **L2** | Guard-Gap-Backlog-Titel wenig spezifisch | `scripts/qa/autopilot_v3/projections.py` (Z. 80) | domain_logic | Titel „Chat – event_contract_guard gap“ ohne Failure-Class | Weniger direkte Zuordnung für Tester | `f"{gg.subsystem} – {gg.failure_class} ({gg.guard_type})"` |

---

## 2. Detaillierte Finding-Beschreibungen

### C1: Regression-Binding ignoriert Incident-Status

**Betroffene Dateien:** `scripts/qa/autopilot_v3/rules.py`  
**Zeilen:** 220–230

**Ursache:**  
Die Bedingung `binding_status not in ("catalog_bound", "bound_to_regression", "closed")` behandelt `bound_to_regression` und `closed` als Werte von `binding_status`. Laut Schema stammen diese aus `qa.status` (incident.yaml). `binding_status` (bindings.json) hat nur: `proposed`, `validated`, `catalog_bound`, `rejected`, `archived`.

**Risiko:**  
Incidents mit `status=closed` oder `status=bound_to_regression` werden fälschlich als „nicht gebunden“ erkannt → falsche Translation-Gaps, fehlerhafte Metriken.

**Korrekturrichtung:**  
```python
inc_status = inc.get("status")
is_bound = (
    binding_status in ("catalog_bound",)  # binding_status-Werte
    or inc_status in ("bound_to_regression", "closed")
)
if not is_bound:
    # ... findings.append(...)
```

---

### C2: Laufzeitfehler bei ungültigem Score

**Betroffene Dateien:** `scripts/qa/autopilot_v3/rules.py`  
**Zeile:** 235

**Ursache:**  
- `int(x.get("Score", 0))` → ValueError bei `Score: ""`, `"high"`, etc.  
- `s.get("Subsystem")` → AttributeError bei `s` nicht-Dict (z.B. `scores = [None]`)

**Risiko:**  
Unhandled Exception, Abbruch des Generators bei fehlerhaften QA_PRIORITY_SCORE-Daten.

**Korrekturrichtung:**  
- `_safe_score(x)` mit try/except  
- `scores = [s for s in (priority_score.get("scores") or []) if isinstance(s, dict)]`

---

### H1: Toter Code autopilot_v3/utils.py

**Betroffene Dateien:** `scripts/qa/autopilot_v3/utils.py`  
**Gesamte Datei**

**Ursache:**  
Kein Import in autopilot_v3; Feedback-Loop nutzt eigene Utils.

**Risiko:**  
Tote Codebasis, Verwirrung, Duplikation.

**Korrekturrichtung:**  
Datei löschen (empfohlen) oder in autopilot_v3 nutzen und Duplikation vermeiden.

---

### H2, H3: load_json Robustheit

**Betroffene Dateien:** `scripts/qa/feedback_loop/utils.py`  
**Zeilen:** 38–48

**Ursache:**  
- Keine Prüfung `path.is_file()`  
- Keine Prüfung `path is None`

**Risiko:**  
Unklare Fehler bei Verzeichnissen; Crash bei `path=None`.

**Korrekturrichtung:**  
```python
if path is None or not path.exists() or not path.is_file():
    return None
```

---

## 3. Widersprüche / Spannungen zwischen Findings

| Spannung | Beschreibung | Empfehlung |
|----------|--------------|------------|
| **M5 vs. M7** | event_contract_guard Schwellwert erhöhen (M5) reduziert Guard-Gaps; Translation-Gaps in Backlog (M7) erhöht Backlog-Einträge | Beide unabhängig umsetzbar; M5 zuerst (weniger Rauschen), M7 als Design-Entscheidung klären |
| **M6 vs. Fachlogik** | ui_state_drift zu DRIFT_FAILURE_CLASSES hinzufügen (M6) erzeugt mehr missing_contract_test; event_contract_guard bleibt bei 1 Incident (wenn M5 nicht umgesetzt) | M6 und M5 gemeinsam prüfen; ui_state_drift semantisch: eher Contract (UI State Machine) oder eher Guard? |
| **C1 vs. Normalizer** | rules.py soll an Normalizer angleichen; Normalizer ist Referenz | C1-Fix explizit an normalizer.py Zeilen 110–116 orientieren |
| **H2 vs. Rückwärtskompatibilität** | `path.is_file()` könnte bei Symlinks anders wirken | Prüfen: Symlinks auf Dateien → is_file() True; auf Verzeichnisse → False. Unkritisch. |

---

## 4. Empfohlene Sanierungsreihenfolge

### Phase 1: Release-Blocker (vor Merge)

| Reihenfolge | Finding | Begründung |
|-------------|---------|------------|
| 1 | **C1** | Falsche Fachlogik, Schema-Verletzung |
| 2 | **C2** | Laufzeitfehler bei realen Daten |

**Exit-Kriterium Phase 1:**  
Generator läuft stabil, Regression-Binding korrekt; keine unhandled Exceptions bei typischen Inputs.

---

### Phase 2: Stabilisierung (kurz nach Merge)

| Reihenfolge | Finding | Begründung |
|-------------|---------|------------|
| 3 | **H1** | Toter Code entfernen |
| 4 | **H2, H3** | load_json robuster |
| 5 | **M2** | Klarere Fehlermeldungen bei IO |
| 6 | **M3** | Explizite Sortierung für Determinismus |

**Exit-Kriterium Phase 2:**  
Robustheit und Determinismus abgesichert; keine toten Code-Bausteine.

---

### Phase 3: Nachschärfung (nächster Sprint)

| Reihenfolge | Finding | Begründung |
|-------------|---------|------------|
| 7 | **M1** | Dokumentation an Code anpassen |
| 8 | **M4** | Dry-Run-Verhalten vereinheitlichen |
| 9 | **M5** | event_contract_guard Schwellwert |
| 10 | **M6** | ui_state_drift-Konsistenz |
| 11 | **M7** | Translation-Gaps ↔ Backlog (Design klären) |

**Exit-Kriterium Phase 3:**  
Fachlogik und Dokumentation konsistent; Dry-Run verständlich.

---

### Phase 4: Optional (Backlog)

| Reihenfolge | Finding | Begründung |
|-------------|---------|------------|
| 12 | **L1** | Severity-basierte Priorität |
| 13 | **L2** | Spezifischere Backlog-Titel |

---

## 5. Merge-Empfehlung

**merge_with_conditions**

**Bedingungen für Merge:**
1. **C1** behoben (Regression-Binding-Prüfung)
2. **C2** behoben (Score-Verarbeitung)

**Nach Phase 1:** merge_ready

**Nach Phase 2:** stabil für Produktion

**Hinweis:**  
Ohne C1 und C2 ist ein Merge nicht empfehlenswert, da falsche Ergebnisse und Laufzeitfehler zu erwarten sind.

---

## 6. Abhängigkeitsgraph (vereinfacht)

```
C1 ──────────────────────────────────────► merge_ready
C2 ──────────────────────────────────────► merge_ready
H1 ──► (unabhängig)
H2,H3 ──► (unabhängig)
M2 ──► (unabhängig)
M3 ──► (unabhängig)
M1 ──► C1 (Dokumentation folgt Code-Fix)
M4 ──► (unabhängig)
M5,M6,M7 ──► (domain_logic, können parallel)
L1,L2 ──► (optional)
```

---

## 7. Review-Quellen

| Review | Findings übernommen |
|--------|---------------------|
| Architektur-/Governance | C1, C2, H1, M1 |
| Fachlogik | C1, M5, M6, M7, L1, L2 |
| Determinismus/IO | C2, H2, H3, M2, M3, M4 |
