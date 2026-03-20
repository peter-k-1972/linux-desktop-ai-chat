# QA Feedback Loop – Gemeinsamer technischer Kern

## Architektur-Begründung

Der Feedback Loop ist als **reiner Auswertungs- und Projektionskern** konzipiert:

1. **Laden → Normalisieren → Regeln → Projektion**  
   Klare Pipeline ohne Seiteneffekte. Jeder Schritt ist testbar und deterministisch.

2. **Dataclasses statt Pydantic**  
   Keine zusätzliche Abhängigkeit, ausreichend für die Projektstruktur. `asdict()` für JSON-Serialisierung.

3. **Zentrale Rule-IDs**  
   Alle 17 Rule-IDs in `models.py` definiert. Wiederverwendbar in Regeln, Traces und Reports.

4. **Keine Schreibzugriffe**  
   Der Kern erzeugt nur `FeedbackRuleResult` und `FeedbackProjectionReport`. Das tatsächliche Schreiben in QA_CONTROL_CENTER, QA_PRIORITY_SCORE, QA_RISK_RADAR erfolgt außerhalb (z.B. durch einen separaten Apply-Step oder manuell).

5. **Robustheit**  
   Fehlende Dateien führen zu Warnings und Defaults, nicht zu Crashes. `suppressed_changes` dokumentiert Regelergebnisse, die nicht angewendet werden konnten.

## Annahmen

- **Pfade:** `docs/qa/` als Basis; `docs/qa/incidents/` für index.json und analytics.json.
- **Schema-Kompatibilität:** Analytics kann `qa_coverage` oder Top-Level `replay_defined_ratio`/`regression_bound_ratio` haben.
- **Incident-Index:** Enthält `incidents[]` und optional `clusters.subsystem`, `clusters.failure_class`.
- **QA_AUTOPILOT_V2.json:** Enthält `recommended_focus_subsystem`, `recommended_focus_failure_class`, `supporting_evidence`, `escalations`, `pilot_constellation_matched`.
- **QA_PRIORITY_SCORE.json:** Enthält `scores[]` mit `Subsystem`, `Score`.
- **QA_RISK_RADAR:** Markdown; wird geladen, aber nicht geparst (zukünftige Erweiterung).
- **Determinismus:** Kein Zufall, keine Zeitstempel in Berechnungen (nur in `generated_at`).

## Offene Integrationspunkte

1. **Apply-Step:** Ein separates Script, das `rule_results` liest und tatsächlich in QA_PRIORITY_SCORE.json, QA_CONTROL_CENTER.json schreibt. Der Kern liefert nur Vorschläge.

2. **QA_RISK_RADAR:** Aktuell Markdown. Parsing und strukturierte Aktualisierung (z.B. neue Risiko-Marker) noch nicht implementiert.

3. **CI-Integration:** Feedback Loop in Pipeline einbinden (z.B. nach `analyze_incidents.py` und `generate_autopilot_v2.py`).

4. **Diff/Review:** Vor dem Apply: Diff zwischen aktuellem Stand und vorgeschlagenen Änderungen anzeigen.

5. **Historisierung:** FeedbackProjectionReport archivieren für Trend-Analyse.

## Beispiel-JSON (Auszug)

```json
{
  "generated_at": "2026-03-15T16:17:05Z",
  "generator": "feedback_loop",
  "input_sources": ["incidents/index.json", "incidents/analytics.json", "QA_AUTOPILOT_V2.json", "..."],
  "per_subsystem_results": {
    "RAG": {
      "subsystem": "RAG",
      "incident_count": 1,
      "feedback_pressure_score": 15.9,
      "autopilot_focus": true,
      "escalation_level": 1
    }
  },
  "rule_results": [
    {
      "target_artifact": "QA_CONTROL_CENTER",
      "target_key": "naechster_qa_sprint",
      "old_value": {"subsystem": "Startup/Bootstrap", "schritt": "Init-Reihenfolge Contract"},
      "new_value": {"subsystem": "RAG", "schritt": "RAG Failure Replay + Chat Cross-Layer", "source": "QA_AUTOPILOT_V2"},
      "applied_rule_ids": ["FL-CTRL-001"]
    }
  ]
}
```

## Verwendung

```bash
python scripts/qa/run_feedback_loop.py
python scripts/qa/run_feedback_loop.py --output docs/qa/FEEDBACK_LOOP_REPORT.json --verbose
```

Programmatisch:

```python
from scripts.qa.feedback_loop import load_feedback_inputs, run_feedback_projections, report_to_dict

inputs = load_feedback_inputs()
report = run_feedback_projections(inputs)
data = report_to_dict(report)
```
