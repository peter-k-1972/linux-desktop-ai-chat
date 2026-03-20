# QA & Governance – Architektur

## Übersicht

QA & Governance ist der Prüf-, Analyse- und Governance-Bereich der Plattform. Er unterscheidet sich visuell von Operations (Arbeiten) und Control Center (Verwalten) und wirkt als ruhige, analytische Oberfläche mit Governance-/Audit-Anmutung.

## Struktur

```
QAGovernanceScreen
  ├─ QAGovernanceNav (sekundäre Bereichsleiste)
  └─ QStackedWidget (QAGovernanceWorkspaceHost)
       ├─ TestInventoryWorkspace
       ├─ CoverageMapWorkspace
       ├─ GapAnalysisWorkspace
       ├─ IncidentsWorkspace
       └─ ReplayLabWorkspace
```

## Klassenzuständigkeiten

| Klasse | Zuständigkeit |
|--------|----------------|
| **QAGovernanceScreen** | Koordinator: Nav + Stack, Inspector-Delegation, Signal-Verkabelung |
| **QAGovernanceNav** | Sekundäre Navigation: Test Inventory, Coverage Map, Gap Analysis, Incidents, Replay Lab |
| **BaseAnalysisWorkspace** | Basis für alle fünf Workspaces, `setup_inspector`-Schnittstelle |
| **TestInventoryWorkspace** | Test List, Kategorien, Status, Details, Filter |
| **CoverageMapWorkspace** | Coverage Overview, Failure Classes, Guards, Regression |
| **GapAnalysisWorkspace** | Gap Summary, Priorität, Review Candidates, offene Analysepunkte |
| **IncidentsWorkspace** | Incident List, Severity, Status, Timeline, Replay-Zusammenhang |
| **ReplayLabWorkspace** | Replay Cases, Status, letzte Runs, Result-Fläche, Trigger-Control |

## Panels (pro Workspace)

- **Test Inventory**: TestListPanel, TestSummaryPanel
- **Coverage Map**: CoverageOverviewPanel, FailureClassPanel
- **Gap Analysis**: GapSummaryPanel, GapReviewPanel
- **Incidents**: IncidentListPanel, IncidentSummaryPanel
- **Replay Lab**: ReplayListPanel, ReplaySummaryPanel

## Inspectors

Jeder Workspace liefert einen kontextsensitiven Inspector-Inhalt:

- **TestInspector**: Test-ID, Kategorie, Status, Tags, Mapping
- **CoverageInspector**: Failure Class, Guard-Zuordnung, Coverage-Status
- **GapInspector**: Gap-Typ, Priorität, Status, Review-Hinweise
- **IncidentInspector**: Incident-ID, Severity, Status, letzte Aktivität
- **ReplayInspector**: Replay-ID, Status, letzter Lauf, Ergebniszusammenfassung

## Dateistruktur

```
app/gui/domains/qa_governance/
├── __init__.py
├── qa_governance_screen.py
├── qa_governance_nav.py
├── panels/
│   ├── __init__.py
│   ├── test_inventory_panels.py
│   ├── coverage_map_panels.py
│   ├── gap_analysis_panels.py
│   ├── incidents_panels.py
│   └── replay_lab_panels.py
└── workspaces/
    ├── __init__.py
    ├── base_analysis_workspace.py
    ├── test_inventory_workspace.py
    ├── coverage_map_workspace.py
    ├── gap_analysis_workspace.py
    ├── incidents_workspace.py
    └── replay_lab_workspace.py

app/gui/inspector/
├── test_inspector.py
├── coverage_inspector.py
├── gap_inspector.py
├── incident_inspector.py
└── replay_inspector.py
```

## Integration

- **WorkspaceHost**: Ruft `setup_inspector` beim Wechsel zu QA & Governance auf.
- **QAGovernanceScreen**: Delegiert an den aktuell sichtbaren Workspace.
- **BottomPanelHost**: Bleibt shell-weit; keine Duplikation.
- **Bootstrap**: QA & Governance ist bereits registriert, keine Änderung nötig.

## Design

- Teal/Cyan-Akzent (#0e7490, #cffafe) für Auswahl – unterscheidet sich von Control Center (Indigo) und Operations (Blau).
- Ruhige, analytische Oberfläche.
- Governance-/Audit-Anmutung.

## Erweiterbarkeit

- Dummy-Daten in Tabellen und Panels sind durch echte QA-/Replay-/Incident-Logik ersetzbar.
- Jeder Workspace ist eigenständig; neue Panels/Inspectors können ergänzt werden.
- Keine God-Class; klare Trennung von Nav, Screen und Workspaces.
