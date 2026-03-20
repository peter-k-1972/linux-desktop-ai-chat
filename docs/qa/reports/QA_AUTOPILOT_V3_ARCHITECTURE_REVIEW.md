# QA Autopilot v3 – Architektur-Review

**Review-Datum:** 2026-03-15  
**Reviewer:** Principal QA-Architekt / Architektur-Auditor  
**Scope:** generate_autopilot_v3.py, autopilot_v3/*, QA_AUTOPILOT_V3.json

---

## 1. Gesamturteil

### **needs_revision**

Die Implementierung ist fachlich stimmig und governance-treu, aber es gibt **kritische Lücken** bei der Nutzbarkeit des Backlogs und **potenzielle Fehler** in der Fachlogik. Vor Merge sind gezielte Korrekturen erforderlich.

---

## 2. Positivliste

| Bereich | Bewertung |
|---------|-----------|
| **Governance-Treue** | Schreibziele nur QA_AUTOPILOT_V3.json und autopilot_v3_trace.json; keine Änderung an Incidents, Replay, Regression Catalog, Produktcode |
| **Determinismus** | `--timestamp` steuerbar; `sort_keys=True` bei allen JSON-Ausgaben; sortierte Iteration (subsystem_states, failure_class_states) |
| **Struktur** | Saubere Trennung models/loader/rules/projections/traces; Wiederverwendung von run_feedback_projections |
| **Pilotkonstellationen** | Explizit in models.py; pilot_id in GuardGapFinding; pilot_not_sufficiently_translated nutzt Top-3-Prioritäten |
| **Drift-Behandlung** | DRIFT_FAILURE_CLASSES; missing_contract_test bei ≥2 Drift-Incidents; event_contract_guard bei Drift-Failure-Classes |
| **Gap-Trennung** | Test-Gaps (replay/regression/contract), Guard-Gaps, Translation-Gaps klar getrennt |
| **CLI** | --dry-run, --output -, --trace-output, --timestamp; argparse; OSError-Handling |
| **Type Hints** | Durchgängig verwendet |

---

## 3. Kritische Mängel

### P0 – Vor Merge beheben

| # | Mangel | Ort | Beschreibung |
|---|--------|-----|--------------|
| 1 | **recommended_test_backlog ohne Translation-Gaps** | projections.py | `incident_not_bound_to_replay` / `incident_not_bound_to_regression` erzeugen keine Backlog-Einträge. Folgearbeit kann nicht direkt aus Translation-Gaps ableiten, welche Tests fehlen. |
| 2 | **supporting_evidence.incident_count falsch** | projections.py:118–121 | Summe über `per_subsystem_results` zählt pro Subsystem – korrekt. Aber: `sum(getattr(s, "incident_count", 0) for s in ...)` – jeder Incident gehört zu genau einem Subsystem, also ist die Summe korrekt. *Nachprüfung: OK.* |
| 3 | **top3_subs Comprehension fehleranfällig** | rules.py:239 | `{s.get("Subsystem") for s in sorted(...)[:3] if s.get("Subsystem")}` – bei `Score` als Float (z.B. 2.5) wirft `int(x.get("Score", 0))` nicht, aber `int(2.5)==2`. Bei leeren scores ist top3_subs leer → `ap_focus not in top3_subs` immer True → pilot_not_sufficiently_translated auch wenn Fokus korrekt ist. |

### P1 – Wichtige Verbesserungen

| # | Mangel | Ort | Beschreibung |
|---|--------|-----|--------------|
| 4 | **Kein Verweis incident_id → Backlog** | projections.py | Translation-Gap-Findings enthalten incident_id, Backlog-Items nicht. Keine Verknüpfung „dieser Backlog-Eintrag behebt jenen Incident“. |
| 5 | **Guard-Gap bei drift_count >= 1 zu sensitiv** | rules.py:152–154 | Bereits 1 Drift-Incident löst event_contract_guard aus. Spezifikation: „repeated drift“ – mindestens 2 empfohlen. |
| 6 | **metrics_false_success in DRIFT_FAILURE_CLASSES, nicht in EVENT_CONTRACT_FC** | rules.py, models.py | metrics_false_success ist Drift, wird aber nicht für event_contract_guard berücksichtigt. Inkonsistenz. |

---

## 4. Konkrete Korrekturanweisungen

### 4.1 Translation-Gaps in Backlog überführen (P0)

**Ziel:** Für `incident_not_bound_to_replay` und `incident_not_bound_to_regression` Backlog-Einträge erzeugen, damit Folgearbeit sie direkt nutzen kann.

**Vorgehen:** In `projections.py` → `_build_recommended_test_backlog` zusätzlich `translation_gap_findings` verarbeiten:

- Für `incident_not_bound_to_replay`: Backlog-Item mit `test_type="replay"`, `guard_type="failure_replay_guard"`, `incident_id` in reasons oder als neues Feld.
- Für `incident_not_bound_to_regression`: Backlog-Item mit `test_type="regression"`.
- Deduplizierung: Ein Incident kann beide Gaps haben → ein kombinierter Eintrag oder zwei getrennte mit Verweis auf incident_id.

### 4.2 pilot_not_sufficiently_translated absichern (P0)

**Ziel:** Verhindern, dass die Regel feuert, wenn `scores` leer oder nur 1–2 Einträge haben.

**Änderung in rules.py:237–248:**

```python
if pilot_matched and ap_focus and priority_score:
    scores = priority_score.get("scores", [])
    if len(scores) >= 3:  # Nur prüfen wenn mindestens 3 Prioritäten existieren
        top3_subs = {s.get("Subsystem") for s in sorted(scores, key=lambda x: -(float(x.get("Score", 0)) or 0))[:3] if s.get("Subsystem")}
        if top3_subs and ap_focus not in top3_subs:
            ...
```

- Zusätzlich: `int()` durch `float()` ersetzen, falls Score als Dezimalzahl vorkommt.

### 4.3 Guard-Gap-Schwelle für Drift anheben (P1)

**Änderung in rules.py:** `if drift_count >= 1` → `if drift_count >= 2` für event_contract_guard, um „repeated drift“ abzubilden.

### 4.4 metrics_false_success in EVENT_CONTRACT_FC (P1)

**Änderung in rules.py:151:**

```python
EVENT_CONTRACT_FC = {"contract_schema_drift", "debug_false_truth", "ui_state_drift", "metrics_false_success"}
```

---

## 5. Merge-Empfehlung

### **Merge nach P0-Korrekturen**

- **P0-1 (Translation-Gaps → Backlog):** Erweiterung der Nutzbarkeit; ohne sie ist der Backlog für Translation-Gaps nicht operativ.
- **P0-3 (pilot_not_sufficiently_translated):** Verhindert falsch-positive Findings bei wenigen Prioritäten.

**P1** kann in einem Folgeticket umgesetzt werden.

---

## 6. Zusammenfassung

| Kriterium | Status |
|-----------|--------|
| Governance-Treue | ✅ pass |
| Fachlogik (Gap-Trennung, Drift, Pilots) | ⚠️ needs_revision (P1) |
| Determinismus | ✅ pass |
| Nutzbarkeit (Backlog, Findings) | ⚠️ needs_revision (P0) |

**Fazit:** Architektur und Governance sind solide. Die fachlichen Korrekturen (P0/P1) sind begrenzt und gut umsetzbar. Nach P0-Anpassungen ist ein Merge vertretbar.
