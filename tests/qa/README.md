# QA Feedback Loop – Testarchitektur

Pytest-Tests für die QA Feedback Loop Architektur: gemeinsamer Kern, Generatoren, Determinismus, IO-Robustheit.

## Struktur

```
tests/qa/
├── README.md                    # Diese Datei
├── conftest.py                  # Gemeinsame Fixtures (generator_fixtures_dir)
├── golden/                      # Golden-/Snapshot-Tests
│   ├── README.md                # Snapshot-Ansatz, Aktualisierung
│   ├── expected/                # Referenz-JSON (control_center, priority_score, risk_radar + Traces)
│   └── test_golden_snapshots.py
├── feedback_loop/               # Unit-Tests für den gemeinsamen Kern
│   ├── conftest.py              # Fixtures (FeedbackLoopInputs, Report)
│   ├── test_utils.py            # load_json, safe_get, Pfade, defensive Defaults
│   ├── test_loader.py           # load_feedback_inputs_from_paths, leere/ungültige/unvollständige JSON
│   ├── test_normalizer.py       # Replay/Regression, Drift, SubsystemFeedbackState, Escalation
│   ├── test_projections.py      # run_feedback_projections, optional_timestamp, rule_results
│   ├── test_rules.py            # Rule-IDs, bounded mutation, Drift-Eskalation
│   ├── test_traces.py           # report_to_dict, Pflichtfelder, stabiler Inhalt
│   └── test_determinism.py      # Gleiche Inputs -> gleiche Outputs, sortierte Keys
└── generators/                  # Generator- und CLI-Tests
    ├── conftest.py              # Fixture-Verzeichnisse, run_generator_script
    ├── test_update_control_center.py
    ├── test_update_priority_scores.py
    ├── test_update_risk_radar.py
    └── test_cli_io.py           # --output -, Trace-Inhalt, invalid JSON
```

## Abdeckung nach Themen

| Thema | Dateien | Tests |
|-------|---------|-------|
| **Utils** | test_utils.py | load_json (Dict/Array/fehlend/leer), safe_get, Pfade, defensive Defaults |
| **Loader** | test_loader.py | load_feedback_inputs_from_paths, fehlende/leere/ungültige/unvollständige JSON |
| **Normalizer** | test_normalizer.py | Replay/Regression, SubsystemFeedbackState, Drift, Escalation, Defaults |
| **Projektionen** | test_projections.py | run_feedback_projections, optional_timestamp, rule_results |
| **Regeln** | test_rules.py | Rule-IDs, bounded mutation (0–10), Drift-Eskalation (FL-RISK-005, FL-PRIO-007) |
| **Traces** | test_traces.py | report_to_dict, Pflichtfelder, stabiler Inhalt, keine Nebeneffekte |
| **Determinismus** | test_determinism.py | Gleiche Inputs -> gleiche Outputs, sortierte Keys |
| **Control Center** | test_update_control_center.py | HP-CC, fehlende Baseline, Change Log, Pilot Tracking, Dry-run, defekte Inputs, Determinismus |
| **Priority Scores** | test_update_priority_scores.py | HP-PS, max_delta, suppressed_changes, Score-Bounds, Replay/Regression-Gap, Drift, Autopilot-Focus, fehlende Baseline, Dry-run, Determinismus |
| **Risk Radar** | test_update_risk_radar.py | HP-RR, single_incident_not_auto_high, Cluster, Replay/Regression-Marker, Drift, Bounded Escalation, fehlende Baseline, Dry-run, Determinismus |
| **CLI/IO** | test_cli_io.py | OUT-Stdout, TRACE-Content, INVALID-JSON, Custom-Pfade |
| **Golden/Snapshot** | golden/test_golden_snapshots.py | Determinismus, diff-freundliche Outputs, Trace-Pflichtfelder |

## Ausführung

```bash
# Alle QA-Tests
pytest tests/qa/ -v

# Nur Feedback-Loop-Kern
pytest tests/qa/feedback_loop/ -v

# Nur Generatoren
pytest tests/qa/generators/ -v
```

## Annahmen

- **Fixtures:** Alle Tests nutzen `tmp_path`; keine Abhängigkeit von `docs/qa`.
- **Determinismus:** `--timestamp` bzw. `optional_timestamp` für reproduzierbare Läufe.
- **Governance:** Tests schreiben nur in tmp_path; keine Änderung an Produktions-Artefakten.

## Offene Projektintegrationspunkte

- **run_feedback_loop.py:** Noch nicht getestet (optional).
- **Golden-Snapshots:** `tests/qa/golden/` – Referenz-JSON in `expected/`, vollständiger Vergleich bei `--timestamp`.
- **M4 (Set-Iteration):** Normalizer nutzt `set(...) | set(...)` ohne Sortierung; aktuell stabil.
