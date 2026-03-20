# QA Autopilot v3 – Architektur- und Governance-Review

**Review-Datum:** 2026-03-15  
**Reviewer:** Principal QA-Architekt, Principal Python-Reviewer, Governance-Auditor  
**Scope:** scripts/qa/generate_autopilot_v3.py, scripts/qa/autopilot_v3/*, docs/qa/QA_AUTOPILOT_V3.json

---

## 1. Gesamturteil

**needs_revision**

Das System erfüllt die Governance-Grenzen und ist architektonisch stimmig. Es gibt jedoch **kritische Fachlogik-Fehler** (insbesondere bei der Regression-Binding-Prüfung) und **tote Code-Bausteine**, die vor Merge behoben werden müssen.

---

## 2. Positivliste

| Bereich | Befund |
|--------|--------|
| **Governance-Treue** | Keine Schreiboperationen auf Tests, Incidents, Replay-Daten, Regression Catalog oder Produktcode. Nur QA_AUTOPILOT_V3.json und autopilot_v3_trace.json werden geschrieben. |
| **Modulare Architektur** | Klare Trennung: loader → models → rules → projections → traces. Wiederverwendung von `run_feedback_projections` aus dem Feedback-Loop. |
| **Determinismus** | `--timestamp` steuerbar; `sort_keys=True` bei JSON; `sorted()` für Subsysteme, Failure-Classes und Backlog. Zwei identische Läufe liefern identischen Output (MD5 verifiziert). |
| **Pilotkonstellationen** | PILOT_1/2/3 explizit in models.py; Zuordnung zu Subsystemen und Guard-Typen konsistent. |
| **Explainability** | Jedes Finding hat `reasons`; `supporting_evidence` enthält Subsysteme, Failure-Classes, Incident-Count; Priorisierung nach (priority, subsystem) nachvollziehbar. |
| **Drift-Behandlung** | DRIFT_FAILURE_CLASSES für missing_contract_test; EVENT_CONTRACT_FC für event_contract_guard; Drift als strukturelles Signal berücksichtigt. |
| **Gap-Trennung** | Test-Gaps, Guard-Gaps und Translation-Gaps klar getrennt; keine Vermischung der Domänen. |

---

## 3. Kritische Mängel

### K1: Falsche Prüfung von Regression-Binding (Governance/Fachlogik)

**Datei:** `scripts/qa/autopilot_v3/rules.py`  
**Zeilen:** 221–230

**Problem:**  
Die Bedingung für `incident_not_bound_to_regression` prüft ausschließlich `binding_status`:

```python
if binding_status not in ("catalog_bound", "bound_to_regression", "closed"):
```

Laut Schema (QA_INCIDENT_LIFECYCLE, bindings.schema.json) gilt:
- `binding_status` (aus bindings.json): `proposed`, `validated`, `catalog_bound`, `rejected`, `archived`
- `bound_to_regression` und `closed` sind Werte von **qa.status** (incident.yaml), nicht von `binding_status`.

**Folge:**  
Incidents mit `status=closed` oder `status=bound_to_regression` werden fälschlich als „nicht gebunden“ erkannt, wenn `binding_status` fehlt oder anders gesetzt ist.

**Referenz:**  
Der Feedback-Loop-Normalizer prüft korrekt beide Quellen:

```python
# normalizer.py, Zeilen 110–116
has_binding = (
    inc.get("binding_status") == "catalog_bound"
    or inc.get("status") in ("bound_to_regression", "closed")
)
```

---

### K2: Potentieller Laufzeitfehler bei pilot_not_sufficiently_translated

**Datei:** `scripts/qa/autopilot_v3/rules.py`  
**Zeile:** 235

**Problem:**  
```python
top3_subs = {s.get("Subsystem") for s in sorted(scores, key=lambda x: -int(x.get("Score", 0)))[:3] if s.get("Subsystem")}
```

`int(x.get("Score", 0))` wirft `ValueError` oder `TypeError`, wenn `Score` ein leerer String, `None` oder ein nicht-numerischer Wert ist.

**Korrektur:**  
`int(x.get("Score") or 0)` oder explizite Fehlerbehandlung.

---

### K3: Toter Code – autopilot_v3/utils.py

**Datei:** `scripts/qa/autopilot_v3/utils.py`  
**Gesamte Datei**

**Problem:**  
`autopilot_v3/utils.py` wird nirgends importiert. Der Feedback-Loop nutzt seine eigene `utils`-Implementierung. Die Datei dupliziert `load_json` und `safe_get` und ist faktisch tot.

**Folge:**  
Verwirrung, Wartungsaufwand, Risiko von Inkonsistenzen bei späteren Änderungen.

---

### K4: Inkonsistenz binding_status vs. status (Dokumentation)

**Datei:** `docs/qa/QA_AUTOPILOT_V3_ARCHITECTURE.md`  
**Zeile:** 86

**Problem:**  
Die Architektur-Dokumentation beschreibt:

> `binding_status != catalog_bound` | incident_not_bound_to_regression

Damit wird impliziert, dass nur `binding_status` relevant ist. Korrekt wäre: Ein Incident gilt als gebunden, wenn `binding_status == "catalog_bound"` **oder** `status in ("bound_to_regression", "closed")`.

---

## 4. Konkrete Korrekturanweisungen

### A1: Regression-Binding-Prüfung anpassen (rules.py)

**Ersetze Zeilen 220–230:**

```python
# 2. incident without regression => incident_not_bound_to_regression
if binding_status not in ("catalog_bound", "bound_to_regression", "closed"):
```

**Durch:**

```python
# 2. incident without regression => incident_not_bound_to_regression
# Consider bound if: binding_status == catalog_bound OR status in (bound_to_regression, closed)
inc_status = inc.get("status")
is_bound = (
    binding_status in ("catalog_bound", "bound_to_regression", "closed")
    or inc_status in ("bound_to_regression", "closed")
)
if not is_bound:
```

(Danach den Block mit `findings.append(TranslationGapFinding(...))` entsprechend anpassen.)

---

### A2: Robuste Score-Verarbeitung (rules.py, Zeile 235)

**Ersetze:**

```python
top3_subs = {s.get("Subsystem") for s in sorted(scores, key=lambda x: -int(x.get("Score", 0)))[:3] if s.get("Subsystem")}
```

**Durch:**

```python
def _safe_score(x: dict) -> int:
    v = x.get("Score")
    try:
        return int(v) if v is not None else 0
    except (ValueError, TypeError):
        return 0

top3_subs = {s.get("Subsystem") for s in sorted(scores, key=lambda x: -_safe_score(x))[:3] if s.get("Subsystem")}
```

---

### A3: Toten Code entfernen oder nutzen

**Option A (empfohlen):**  
`scripts/qa/autopilot_v3/utils.py` löschen. Der Autopilot v3 nutzt den Feedback-Loop-Loader und benötigt keine eigene Utils-Schicht.

**Option B:**  
Falls Utils benötigt werden: Import in `loader.py` oder `rules.py` ergänzen und Duplikation mit dem Feedback-Loop vermeiden (z.B. gemeinsame Utils nutzen).

---

### A4: Architektur-Dokumentation aktualisieren

**Datei:** `docs/qa/QA_AUTOPILOT_V3_ARCHITECTURE.md`

**Ersetze Zeile 86:**

> | binding_status != catalog_bound | incident_not_bound_to_regression |

**Durch:**

> | binding_status ≠ catalog_bound **und** status ∉ {bound_to_regression, closed} | incident_not_bound_to_regression |

---

## 5. Merge-Empfehlung

**merge_with_conditions**

**Bedingungen:**
1. K1 (Regression-Binding-Prüfung) muss behoben werden – sonst falsche Translation-Gaps.
2. K2 (Score-Verarbeitung) sollte behoben werden – sonst Laufzeitfehler bei ungültigen QA_PRIORITY_SCORE-Daten.
3. K3 (toter Code): Entweder `utils.py` entfernen oder sinnvoll integrieren.
4. K4 (Dokumentation): Architektur-Dokumentation anpassen.

**Nach Erfüllung der Bedingungen:** merge_ready.

---

## 6. Anhang: Prüf-Checkliste

| Prüfpunkt | Status |
|-----------|--------|
| Schreibt nur erlaubte Artefakte (QA_AUTOPILOT_V3.json, trace) | ✓ |
| Keine pytest-Dateien, keine Test-Generierung | ✓ |
| Keine Mutation von Incidents, Replay, Regression Catalog | ✓ |
| Models / Loader / Rules / Projections / Traces getrennt | ✓ |
| Replay-Gaps vs. Regression-Gaps vs. Translation-Gaps getrennt | ✓ |
| Drift als strukturelles Signal (DRIFT_FAILURE_CLASSES) | ✓ |
| Pilotkonstellationen berücksichtigt | ✓ |
| Empfehlungen mit reasons/Evidenz | ✓ |
| Priorisierung auditierbar (sortiert, dokumentiert) | ✓ |
| Determinismus (timestamp, sort_keys, sorted) | ✓ |
| binding_status/status-Konsistenz mit Schema | ✗ (K1) |
| Robuste Verarbeitung von QA_PRIORITY_SCORE | ✗ (K2) |
| Kein toter Code | ✗ (K3) |
