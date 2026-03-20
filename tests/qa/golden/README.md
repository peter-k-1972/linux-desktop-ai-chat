# QA Golden-/Snapshot-Tests

## Ansatz

Die Golden-Tests vergleichen die JSON-Ausgaben der QA Feedback Loop Generatoren gegen **committete Referenzdateien** in `expected/`. Bei gleichen Inputs (aus `generator_fixtures_dir`) muss die Ausgabe exakt mit der Golden-Datei übereinstimmen.

### Vorteile

- **Determinismus:** Gleiche Inputs → gleiche Outputs
- **Diff-freundlich:** Änderungen an der Generator-Logik führen zu klaren Test-Diffs
- **Regression-Sicherheit:** Unbeabsichtigte Änderungen werden sofort erkannt

### Zeitfelder

`generated_at` wird über `--timestamp "2025-01-15T12:00:00Z"` injiziert und ist in allen Golden-Dateien identisch. Kein Ausschluss nötig – der Vergleich ist vollständig.

## Golden-Dateien

| Datei | Beschreibung |
|-------|--------------|
| `expected/control_center.json` | Control Center Output |
| `expected/control_center_trace.json` | Control Center Trace |
| `expected/priority_score.json` | Priority Score Output |
| `expected/priority_score_trace.json` | Priority Score Trace |
| `expected/risk_radar.json` | Risk Radar Output |
| `expected/risk_radar_trace.json` | Risk Radar Trace |

## Golden-Dateien aktualisieren

**Wann:** Nach bewussten Änderungen an der Generator-Logik, wenn die neue Ausgabe korrekt ist.

**Vorgehen:**

1. **Prüfen:** Ist die Änderung beabsichtigt? Regressionen nicht durch blindes Aktualisieren verschleiern.

2. **Input-Fixtures anlegen** (Inhalt wie `tests/qa/generators/conftest._minimal_fixture_dir`):
   - `incidents/index.json`, `incidents/analytics.json`
   - `QA_AUTOPILOT_V2.json`, `QA_PRIORITY_SCORE.json`, `QA_CONTROL_CENTER.json`, `QA_RISK_RADAR.md`

3. **Generatoren ausführen** mit `--dry-run --timestamp "2025-01-15T12:00:00Z"`:
   - stdout → `expected/<generator>.json`
   - stderr (nach `--- TRACE ---`) → `expected/<generator>_trace.json` (nur erstes JSON-Objekt)

4. **Tests erneut ausführen:** `pytest tests/qa/golden/ -v`
