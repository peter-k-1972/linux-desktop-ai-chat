# QA & Governance – Implementierung

## Übersicht

Der Bereich **QA & Governance** nutzt reale QA-/Governance-Artefakte und zeigt sie in fünf Workspaces an.

## Wichtige Klassen

### QAGovernanceService (`app/services/qa_governance_service.py`)

Zentrale Service-Schicht für alle QA-Artefakte:

- **list_tests()** – Tests aus `docs/qa/QA_TEST_INVENTORY.json`
- **get_test_detail()** – Detail eines Tests
- **get_test_summary()** – Zusammenfassung (Anzahl, Subsysteme, Domains)
- **get_coverage_entries()** – Coverage-Einträge aus `docs/qa/QA_COVERAGE_MAP.json`
- **get_coverage_summary()** – Coverage-Stärke, Gap-Counts
- **list_incidents()** – Incidents aus `docs/qa/incidents/index.json`
- **list_gaps()** – Gaps aus `docs/qa/PHASE3_GAP_REPORT.json`
- **list_replays()** – Replay-Artefakte (Incidents + Coverage-Bindings)

### Workspaces

| Workspace | Panels | Datenquelle |
|-----------|--------|-------------|
| **TestInventoryWorkspace** | TestListPanel, TestSummaryPanel, TestDetailPanel | QA_TEST_INVENTORY.json |
| **CoverageMapWorkspace** | CoverageOverviewPanel, CoverageListPanel, CoverageDetailPanel | QA_COVERAGE_MAP.json |
| **IncidentsWorkspace** | IncidentListPanel, IncidentSummaryPanel, IncidentDetailPanel | incidents/index.json |
| **ReplayLabWorkspace** | ReplayListPanel, ReplaySummaryPanel, ReplayDetailPanel | Incidents + Coverage replay_binding |
| **GapAnalysisWorkspace** | GapListPanel, GapSummaryPanel, GapDetailPanel | PHASE3_GAP_REPORT.json |

### Daten-/Signalflüsse

1. **Laden**: Panels rufen beim Erstellen `get_qa_governance_service()` auf und laden Daten.
2. **Auswahl**: Klick auf eine Zeile → `*_selected` Signal → Detail-Panel + Inspector werden aktualisiert.
3. **Inspector**: Jeder Workspace erhält `setup_inspector(inspector_host)` und zeigt bei Auswahl passende Inspector-Inhalte (TestInspector, CoverageInspector, etc.).

## Startanweisung

```bash
cd /home/peter/Projektsammlung/intern_systems/Linux-Desktop-Chat
.venv/bin/python -m app.main
```

1. In der linken Navigation **QA & Governance** wählen.
2. Unterbereich wählen: Test Inventory, Coverage Map, Incidents, Replay Lab, Gap Analysis.
3. In Listen klicken → Details im Panel und im Inspector rechts.

## Artefakt-Pfade

- `docs/qa/QA_TEST_INVENTORY.json`
- `docs/qa/QA_COVERAGE_MAP.json`
- `docs/qa/PHASE3_GAP_REPORT.json`
- `docs/qa/incidents/index.json`

Fehlende oder fehlerhafte Dateien werden ohne Absturz behandelt (leere Listen, Hinweistexte).
