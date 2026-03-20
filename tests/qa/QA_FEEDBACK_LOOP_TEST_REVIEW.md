# QA Feedback Loop – Test-Review

**Review-Datum:** 2025-03-15  
**Reviewer:** Principal QA-Architekt  
**Scope:** tests/qa/feedback_loop/*, tests/qa/generators/*, tests/qa/golden/*

---

## 1. Test-Review-Urteil

### **needs_revision**

Die Tests decken viele Kernrisiken ab und sind technisch solide, aber es gibt **triviale Assertions**, **kritische Lücken** und **potenzielle falsche Sicherheit**. Für Regression-Sicherheit in Produktion sind Ergänzungen erforderlich.

---

## 2. Positivliste

| Bereich | Was gut funktioniert |
|---------|----------------------|
| **Loader** | Leere Datei, ungültiges JSON, fehlende Datei, unvollständige Struktur, empty-dict-Truthiness – klar getestet |
| **Normalizer** | Replay/Regression-Trennung, Drift-Density, Escalation-Level, SubsystemFeedbackState-Bildung, Defaults – präzise |
| **Rules** | Rule-IDs (FL-PRIO-001/002, FL-RISK-001/005, FL-PRIO-007), bounded 0–10, Drift-Eskalation – direkt unit-getestet |
| **Determinismus** | `test_det_*`, sortierte Keys, optional_timestamp, Golden-Tests – gut abgesichert |
| **Bounded Mutation** | `test_max_delta_per_run_capped`, `test_suppressed_changes_documented`, Score-Bounds 0–100 |
| **Dry-run** | Alle drei Generatoren: keine Dateien geschrieben |
| **single_incident_not_auto_high** | Expliziter Test mit single_incident_fixtures_dir |
| **Golden-Tests** | Vollständiger JSON-Vergleich, Trace, generated_at normalisiert |
| **Fixtures** | tmp_path, keine Produktdateien, wartbare _minimal_fixture_dir |
| **CLI/IO** | --output -, invalid JSON, Custom-Pfade |

---

## 3. Kritische Testlücken

### P0 – Blockierend für Regression-Sicherheit

| Lücke | Datei | Beschreibung |
|-------|-------|--------------|
| **Triviale Assertion** | `test_projections.py:46–52` | `assert len(prio) >= 0 and len(risk) >= 0` ist **immer wahr** – Test liefert keine Aussage |
| **Triviale Assertion** | `test_update_control_center.py:104–120` | `test_hp_governance_alerts_when_gaps`: `assert ... or len(alerts) >= 0` – kann immer grün sein |
| **load_feedback_inputs nicht getestet** | – | `load_feedback_inputs(base_path)` wird von `run_feedback_loop.py` genutzt, nur `load_feedback_inputs_from_paths` ist getestet |

### P1 – Wichtige Lücken

| Lücke | Datei | Beschreibung |
|-------|-------|--------------|
| **_preserve_existing_fields** | `update_control_center.py` | Bestehende Felder (gesamtstatus, top_risiken, …) werden bei Update erhalten – **kein Test** |
| **--smoothing** | `update_priority_scores.py` | Glättung bei `abs(delta) > 5` – **nicht getestet** |
| **_parse_risk_radar_md** | `update_risk_radar.py` | Markdown-Parsing für P1/P2/P3 → risk_level – **nicht unit-getestet** |
| **Negative bounded delta** | `update_priority_scores.py` | `raw_delta < -10` → capped auf -10 – **nicht explizit getestet** |
| **apply_control_center_rules** | `rules.py` | FL-CTRL-001 bis FL-CTRL-005 – nur indirekt über Generator, keine direkten Unit-Tests |

### P2 – Nützliche Ergänzungen

| Lücke | Datei | Beschreibung |
|-------|-------|--------------|
| **run_feedback_loop.py** | – | Orchestrierungsskript – **nicht getestet** |
| **Schreibfehler** | Generatoren | Read-only-Verzeichnis, OSError – **nicht getestet** |
| **metrics_false_success** | `normalizer.py` | DRIFT_FAILURE_CLASSES enthält `metrics_false_success` – **nicht in Drift-Tests** |
| **Cluster-Dichte** | `normalizer.py` | `_subsystem_cluster_density` – **nicht getestet** |

---

## 4. Konkrete Ergänzungsvorschläge

### 4.1 Sofort: Triviale Tests ersetzen

**test_projections.py – test_rule_results_contain_priority_and_risk:**

```python
def test_rule_results_contain_priority_and_risk(feedback_loop_report: object) -> None:
    """rule_results enthält QA_PRIORITY_SCORE und QA_RISK_RADAR bei passenden Signalen."""
    prio = [r for r in feedback_loop_report.rule_results if r.target_artifact == "QA_PRIORITY_SCORE"]
    risk = [r for r in feedback_loop_report.rule_results if r.target_artifact == "QA_RISK_RADAR"]
    # Mit RAG Incidents (2x), replay/regression gap, autopilot focus MÜSSEN Regeln feuern
    assert len(prio) >= 1, "Mindestens eine Priority-Regel bei RAG-Incidents erwartet"
    assert len(risk) >= 1, "Mindestens eine Risk-Regel bei RAG-Incidents erwartet"
```

**test_update_control_center.py – test_hp_governance_alerts_when_gaps:**

```python
def test_hp_governance_alerts_when_gaps(generator_fixtures_dir: Path) -> None:
    """governance_alerts enthält REPLAY_GAP oder REGRESSION_GAP bei entsprechenden Incidents."""
    # ... (bestehender Setup)
    codes = [a.get("code") for a in alerts if isinstance(a, dict)]
    assert "REPLAY_GAP" in codes or "REGRESSION_GAP" in codes or "INCIDENT_PRESSURE" in codes, \
        f"Erwarte mindestens einen Gap/Incident-Alert, bekam: {codes}"
```

### 4.2 load_feedback_inputs testen

**Neuer Test in test_loader.py:**

```python
def test_load_feedback_inputs_with_base_path(tmp_path: Path) -> None:
    """load_feedback_inputs lädt aus base_path/docs/qa wenn QA_AUTOPILOT_V2.json in base_path."""
    docs_qa = tmp_path / "docs" / "qa"
    docs_qa.mkdir(parents=True)
    (docs_qa / "incidents").mkdir(parents=True)
    # Minimale Dateien anlegen
    # ...
    inputs = load_feedback_inputs(base_path=tmp_path)
    assert inputs.autopilot_v2 is not None
```

### 4.3 _preserve_existing_fields testen

**Neuer Test in test_update_control_center.py:**

```python
def test_preserve_existing_fields(generator_fixtures_dir: Path) -> None:
    """Bestehende Felder (gesamtstatus, top_risiken, …) werden bei Update erhalten."""
    old_cc = {"naechster_qa_sprint": {...}, "gesamtstatus": "ok", "top_risiken": ["R1"]}
    (generator_fixtures_dir / "QA_CONTROL_CENTER.json").write_text(json.dumps(old_cc), ...)
    # Generator ausführen
    output = json.loads(...)
    assert "gesamtstatus" in output
    assert output["gesamtstatus"] == "ok"
```

### 4.4 --smoothing testen

**Neuer Test in test_update_priority_scores.py:**

```python
def test_smoothing_reduces_delta(high_delta_fixtures_dir: Path) -> None:
    """--smoothing reduziert große Deltas (Glättung)."""
    out_no_smooth = ...
    out_smooth = ...  # mit --smoothing
    # Bei raw_delta > 5: capped_delta mit smoothing < capped_delta ohne
    # Oder: abs(delta) mit smoothing <= abs(delta) ohne bei großen Deltas
```

### 4.5 Risk-Radar-MD-Parsing testen

**Neuer Test (Unit oder Generator):**

```python
def test_parse_risk_radar_md_p1_p2_p3() -> None:
    """_parse_risk_radar_md extrahiert P1/P2/P3 korrekt aus Tabelle."""
    from scripts.qa.update_risk_radar import _parse_risk_radar_md, _prioritaet_to_risk_level
    md = "| Subsystem | Priorität |\n|-----------|----------|\n| RAG | P1 |\n| X | P2 |"
    m = _parse_risk_radar_md(md)
    assert m.get("RAG") == "P1"
    assert _prioritaet_to_risk_level("P1") == "high"
```

---

## 5. Falsche Sicherheit

| Problem | Wo | Risiko |
|---------|-----|--------|
| **Triviale Assertions** | test_rule_results_contain_priority_and_risk, test_hp_governance_alerts_when_gaps | Tests können grün sein, obwohl keine Regeln feuern |
| **Kein Mock-Overkill** | – | Gut: Keine schweren Mocks, echte Subprocess-Aufrufe |
| **Golden nur ein Input-Set** | golden/expected/ | Ein Fixture-Set – Änderungen an anderen Input-Kombinationen werden nicht erfasst |
| **test_incidents_non_list_fallback** | test_normalizer.py:46 | `assert "RAG" in states or "Startup/Bootstrap" in states or "Debug/EventBus"` – Fallback-Set ist fix; wenn Default geändert wird, Test bleibt grün, Verhalten könnte falsch sein |

---

## 6. Einschätzung: Regression-Readiness

### **partially_regression_ready**

**Begründung:**

- **Stark:** Determinismus, bounded mutation, Dry-run, IO-Robustheit, Drift, Replay/Regression-Trennung, Golden-Snapshots
- **Schwach:** Triviale Assertions, fehlende Tests für `load_feedback_inputs`, `_preserve_existing_fields`, `--smoothing`, Risk-Radar-MD-Parsing
- **Risiko:** Zwei Tests können grün sein, obwohl fachliche Logik fehlerhaft ist

**Empfehlung:** Vor Freigabe die P0-Lücken schließen (triviale Assertions ersetzen, `load_feedback_inputs` testen). P1-Lücken für vollständige Regression-Sicherheit adressieren.
