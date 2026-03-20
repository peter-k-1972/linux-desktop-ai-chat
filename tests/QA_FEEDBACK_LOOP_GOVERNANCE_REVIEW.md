# QA Feedback Loop – Fachliches Governance-Review

**Review-Datum:** 2026-03-15  
**Fokus:** QA-Fachlogik, Signalfluss, Governance-Richtigkeit (keine Stilbewertung)

---

## 1. Fachliches Gesamturteil

### **needs_revision**

Die Fachlogik ist grundsätzlich stimmig und Governance-konform. Es gibt jedoch **einen klaren Modellierungsfehler** (Replay/Regression-Vermischung), **ungenutzte Signale** sowie **Lücken** bei der per-Subsystem-Regression und der Drift-Abdeckung. Die Pilotkonstellationen werden korrekt abgebildet; die Governance-Grenze wird eingehalten.

---

## 2. Was fachlich gut modelliert ist

| Aspekt | Bewertung |
|--------|-----------|
| **Governance-Konformität** | Die Logik beschränkt sich auf Priorisierung, Warnung, Projektion und Eskalation. Keine Tests, keine Incident-Mutation, kein Regression Catalog, keine Replay-Daten, kein Produktcode. |
| **Pilotkonstellationen** | Die drei Piloten (Startup/Ollama, RAG/ChromaDB, Debug/EventBus) sind in `update_control_center.py` explizit definiert und werden über `pilot_constellation_matched` aus dem Autopilot korrekt abgebildet. |
| **Drift als strukturelles Signal** | Drift wird über `DRIFT_FAILURE_CLASSES` und `structural.drift_risk` (FL-RISK-005) als eigenes Signal behandelt, nicht wie ein normaler Incident. FL-PRIO-007 und FL-CTRL-004 adressieren Drift-Muster separat. |
| **Bounded Mutation** | Prioritäts- und Risiko-Eskalation sind begrenzt (MAX_DELTA_PER_RUN, bounded_escalation, single_incident_not_auto_high). Keine selbstverstärkende Fehllogik erkennbar. |
| **Schwellenwert-Trennung** | Replay und Regression haben getrennte Schwellen (REPLAY_GAP_WARNING=0.5, REGRESSION_GAP_WARNING=0.3). |
| **Control Center** | `current_focus`, `governance_alerts`, `escalations`, `pilot_tracking` und `feedback_loop_summary` liefern eine führungstaugliche Struktur, keine bloße Rohdaten-Umverpackung. |
| **Severity-Gewichtung** | `SEVERITY_WEIGHTS` (blocker 5.0 bis cosmetic 0.5) ist fachlich plausibel. |
| **Startup-kritische Subsysteme** | `STARTUP_CRITICAL` und `dependency_weight` priorisieren Startup/Bootstrap, Provider/Ollama, RAG, Persistenz/SQLite angemessen. |

---

## 3. Fachliche Schwächen / Modellierungsfehler

### HIGH: Replay-Gap und Regression-Gap vermischt

**Ort:** `scripts/qa/feedback_loop/normalizer.py` Zeilen 84–99, Funktion `_subsystem_replay_gap`

**Problem:**  
Die Funktion zählt Incidents als „ohne Replay“, wenn `replay_status` fehlt **oder** `binding_status is None`:

```python
if status is None or status in ("", "missing") or binding is None:
    no_replay[sub] += 1
```

**Folge:**  
Incidents mit definiertem Replay (`replay_status` gesetzt), aber ohne Regression-Binding (`binding_status=None`) werden fälschlich als Replay-Gap gezählt. Replay-Gap und Regression-Gap werden vermischt.

**Fachliche Trennung:**  
- **Replay-Gap:** Anteil Incidents ohne Replay-Definition (replay.yaml fehlt oder replay_status fehlt/„missing“).  
- **Regression-Gap:** Anteil Incidents ohne Regression-Binding (binding_status ≠ catalog_bound).

---

### HIGH: Keine per-Subsystem-Regression

**Ort:** `scripts/qa/feedback_loop/normalizer.py` Zeilen 173–174

**Problem:**  
`sub_reg_gap` wird für alle Subsysteme mit Incidents aus dem **globalen** `reg_gap` (analytics.qa_coverage.regression_bound_ratio) abgeleitet:

```python
sub_reg_gap = reg_gap if inc_count > 0 else 0.0
```

**Folge:**  
Subsystem A mit 100 % Regression-Binding und Subsystem B mit 0 % erhalten dieselbe `regression_gap_rate`. Die Projektion kann Subsysteme mit guter Regression-Abdeckung fälschlich als problematisch markieren.

**Fachlich:**  
Es existiert `binding_status` pro Incident. Eine per-Subsystem-Regression-Ratio ist berechenbar und sollte genutzt werden.

---

### MEDIUM: Analytics-Signale ungenutzt

**Ort:** `scripts/qa/feedback_loop/normalizer.py`; `analytics.json` enthält `risk_signals`

**Problem:**  
- `analytics.risk_signals.subsystem_risk_score` wird nicht verwendet.  
- `analytics.risk_signals.failure_class_frequency` wird nur genutzt, um Failure-Classes zu `all_fc` hinzuzufügen, nicht für die Gewichtung.

**Folge:**  
Vorberechnete Risiko-Signale aus der Incident-Analyse gehen in der Feedback-Loop-Projektion verloren.

---

### MEDIUM: Drift-Failure-Classes unvollständig

**Ort:** `scripts/qa/feedback_loop/normalizer.py` Zeile 27

**Problem:**  
```python
DRIFT_FAILURE_CLASSES = {"contract_schema_drift", "debug_false_truth", "metrics_false_success"}
```

Pilot 3 („Debug/EventBus / EventType drift“) deutet auf EventType-Drift hin. `ui_state_drift` und `async_race` aus den Incidents sind nicht in `DRIFT_FAILURE_CLASSES`. Die Abdeckung von Drift-relevanten Failure-Classes ist möglicherweise zu eng.

**Folge:**  
Manche Drift-Muster werden nicht als Drift erkannt und erhalten keine erhöhte Priorität oder Risiko-Eskalation.

---

### MEDIUM: Autopilot `top_risk_signals` nicht direkt genutzt

**Ort:** `scripts/qa/feedback_loop/`; `QA_AUTOPILOT_V2.json` enthält `top_risk_signals`

**Problem:**  
`top_risk_signals` (z. B. „Contract Coverage gering; Drift/Governance schwach“ für Provider/Ollama, Persistenz/SQLite) fließt nur indirekt über die Autopilot-Empfehlung ein. Die Feedback-Loop-Regeln nutzen diese Signale nicht explizit.

**Folge:**  
Zusätzliche Risiko- und Governance-Hinweise aus dem Autopilot werden in der Projektion nicht direkt abgebildet.

---

### LOW: FL-PRIO-002/003 ohne expliziten Incident-Check

**Ort:** `scripts/qa/feedback_loop/rules.py` Zeilen 66–75

**Problem:**  
FL-PRIO-002 und FL-PRIO-003 erhöhen die Priorität bei Replay- bzw. Regression-Gap ohne explizite Prüfung von `incident_count > 0`. Der Normalizer setzt bei 0 Incidents `replay_gap_rate=0` und `regression_gap_rate=0`, sodass es praktisch nicht triggert.

**Folge:**  
Fachlich unkritisch, aber die Regeln sind ohne explizite Bedingung weniger selbsterklärend und anfällig für spätere Änderungen.

---

### LOW: FL-CTRL-002/003 nutzen Autopilot statt Analytics

**Ort:** `scripts/qa/feedback_loop/rules.py` Zeilen 234–265

**Problem:**  
Replay- und Regression-Ratio werden aus `autopilot.supporting_evidence.replay_gap_refs` gelesen, nicht aus `analytics.qa_coverage`. Die Werte stammen ursprünglich aus Analytics, werden aber über den Autopilot weitergeleitet.

**Folge:**  
Redundanz und potenzielle Abweichung, wenn Autopilot und Analytics zu unterschiedlichen Zeitpunkten laufen.

---

## 4. Konkrete Verbesserungsvorschläge

### 4.1 Replay-Gap und Regression-Gap trennen (HIGH)

**Datei:** `scripts/qa/feedback_loop/normalizer.py`

**Änderung 1 – `_subsystem_replay_gap` nur auf Replay prüfen:**

```python
def _subsystem_replay_gap(incidents: list[dict]) -> dict[str, float]:
    """Anteil Incidents pro Subsystem ohne Replay (replay_status fehlt oder nicht verified)."""
    total: dict[str, int] = defaultdict(int)
    no_replay: dict[str, int] = defaultdict(int)
    for inc in incidents:
        sub = inc.get("subsystem") or "_unknown"
        if sub == "_unknown":
            continue
        total[sub] += 1
        status = inc.get("replay_status")
        # Nur Replay prüfen – binding_status gehört zur Regression
        if status is None or status in ("", "missing"):
            no_replay[sub] += 1
    return {
        sub: (no_replay[sub] / total[sub]) if total[sub] > 0 else 0.0
        for sub in total
    }
```

**Änderung 2 – `_subsystem_regression_gap` einführen (analog zu analyze_incidents):**

```python
def _subsystem_regression_gap(incidents: list[dict]) -> dict[str, float]:
    """Anteil Incidents pro Subsystem ohne Regression-Binding."""
    total: dict[str, int] = defaultdict(int)
    no_binding: dict[str, int] = defaultdict(int)
    for inc in incidents:
        sub = inc.get("subsystem") or "_unknown"
        if sub == "_unknown":
            continue
        total[sub] += 1
        has_binding = (
            inc.get("binding_status") == "catalog_bound"
            or inc.get("status") in ("bound_to_regression", "closed")
        )
        if not has_binding:
            no_binding[sub] += 1
    return {
        sub: (no_binding[sub] / total[sub]) if total[sub] > 0 else 0.0
        for sub in total
    }
```

**Änderung 3 – In `normalize_to_subsystem_states`:**

- `replay_by_sub = _subsystem_replay_gap(incidents)` (unverändert, aber mit korrigierter Funktion)
- `regression_by_sub = _subsystem_regression_gap(incidents)` (neu)
- `sub_reg_gap = regression_by_sub.get(sub, reg_gap if inc_count > 0 else 0.0)` (Fallback auf globalen `reg_gap`, wenn Subsystem keine Incidents hat)

---

### 4.2 Per-Subsystem-Regression nutzen (HIGH)

**Datei:** `scripts/qa/feedback_loop/normalizer.py`

- `_subsystem_regression_gap` wie oben einführen.
- In `normalize_to_subsystem_states` `sub_reg_gap` aus `regression_by_sub` ableiten, mit Fallback auf globalen `reg_gap`, wenn das Subsystem keine Incidents hat.

---

### 4.3 Analytics `risk_signals` einbinden (MEDIUM)

**Datei:** `scripts/qa/feedback_loop/normalizer.py`

- `subsystem_risk_score` aus `analytics.risk_signals` lesen und in `SubsystemFeedbackState` als optionales Feld (z. B. `analytics_risk_score`) übernehmen.
- In der Pressure-Berechnung oder in den Regeln als Zusatzsignal verwenden (z. B. Gewichtung oder Schwellen-Anpassung).

---

### 4.4 Drift-Failure-Classes erweitern (MEDIUM)

**Datei:** `scripts/qa/feedback_loop/normalizer.py`

- `ui_state_drift` und ggf. weitere Drift-relevante Failure-Classes (z. B. aus Pilot 3: EventType-Drift) in `DRIFT_FAILURE_CLASSES` aufnehmen oder konfigurierbar machen.
- Optional: Mapping aus Konfiguration oder Schema statt Hardcoding.

---

### 4.5 FL-PRIO-002/003 explizit machen (LOW)

**Datei:** `scripts/qa/feedback_loop/rules.py`

```python
# FL-PRIO-002: replay gap (nur bei Incidents im Subsystem)
if state.incident_count > 0 and state.replay_gap_rate >= REPLAY_GAP_WARNING:
    delta += 1
    ...

# FL-PRIO-003: regression gap (nur bei Incidents im Subsystem)
if state.incident_count > 0 and state.regression_gap_rate >= REGRESSION_GAP_WARNING:
    delta += 1
    ...
```

---

### 4.6 FL-CTRL-002/003 auf Analytics abstellen (LOW)

**Datei:** `scripts/qa/feedback_loop/rules.py`

- Für FL-CTRL-002/003 primär `inputs.analytics` (bzw. über `FeedbackLoopInputs` verfügbar) nutzen.
- `autopilot.supporting_evidence.replay_gap_refs` nur als Fallback, wenn Analytics fehlt.

---

## 5. Zusammenfassung

| Kategorie | Urteil |
|-----------|--------|
| Governance-Konformität | **pass** – nur Priorisierung, Warnung, Projektion |
| Signalfluss | **needs_revision** – Replay/Regression vermischt, Analytics-Signale teils ungenutzt |
| Replay vs. Regression | **needs_revision** – Vermischung in `_subsystem_replay_gap` |
| Drift-Logik | **pass** – strukturell behandelt; Abdeckung erweiterbar |
| Priority-Projektion | **pass** – nachvollziehbar, begrenzt |
| Risk-Radar-Projektion | **pass** – angemessen, bounded |
| Control-Center | **pass** – führungstauglich |
| Pilotkonstellationen | **pass** – korrekt abgebildet |

**Priorität der Fixes:** 4.1 (Replay/Regression-Trennung) und 4.2 (per-Subsystem-Regression) zuerst, danach 4.3 und 4.4.
