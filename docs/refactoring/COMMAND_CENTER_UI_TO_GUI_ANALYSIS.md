# Command-Center-Subsystem: UI → GUI Migration – Ist-Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Phase:** 1 – Ist-Analyse

---

## 1. Ausgangslage

### 1.1 Legacy-Bereich

| Pfad | Typ | Inhalt |
|------|-----|--------|
| `app/ui/command_center/` | Verzeichnis | Vollständige Implementierung (keine Re-Exports) |

### 1.2 Enthaltene Dateien und Klassen

| Datei | Klassen/Komponenten | Abhängigkeiten |
|-------|---------------------|----------------|
| `command_center_view.py` | CommandCenterView, _StatusCard, _SubsystemCard | app.qa.dashboard_adapter, app.resources.styles, Sub-Views |
| `qa_drilldown_view.py` | QADrilldownView | app.qa.dashboard_adapter, app.qa.drilldown_models |
| `subsystem_detail_view.py` | SubsystemDetailView | app.qa.dashboard_adapter, app.qa.drilldown_models |
| `runtime_debug_view.py` | RuntimeDebugView | app.resources.styles |
| `governance_view.py` | GovernanceView | app.qa.dashboard_adapter, app.qa.drilldown_models |
| `qa_operations_view.py` | QAOperationsView | app.qa.operations_adapter, app.qa.operations_models |
| `incident_operations_view.py` | IncidentOperationsView | app.qa.operations_adapter, app.qa.operations_models |
| `review_operations_view.py` | ReviewOperationsView | app.qa.operations_adapter, app.qa.operations_models |
| `audit_operations_view.py` | AuditOperationsView | app.qa.operations_adapter, app.qa.operations_models |

### 1.3 Externe Konsumenten

| Konsument | Import | Verwendung |
|-----------|--------|------------|
| `app/main.py` | `from app.ui.command_center import CommandCenterView` | Legacy MainWindow – stacked widget |
| `tests/ui/test_command_center_dashboard.py` | Diverse Views | Unit-Tests |

### 1.4 Keine gui-Implementierung

- `app/gui/domains/command_center/` existiert nicht
- Command Center ist ausschließlich in ui implementiert
- Keine Überschneidungen mit bereits migrierten Domains (agents, chat, settings, project, knowledge, prompts, debug, sidepanel)

---

## 2. Zielstruktur

```
app/gui/domains/command_center/
├── __init__.py
├── command_center_view.py
├── qa_drilldown_view.py
├── subsystem_detail_view.py
├── runtime_debug_view.py
├── governance_view.py
├── qa_operations_view.py
├── incident_operations_view.py
├── review_operations_view.py
└── audit_operations_view.py
```

1:1-Migration, keine Aufsplitterung.

---

## 3. Anpassungen bei Migration

1. **Imports in command_center_view.py:** `app.ui.command_center.*` → `app.gui.domains.command_center.*`
2. **_project_root():** `parent.parent.parent.parent` → `parent.parent.parent.parent.parent` (gui/domains tiefer)
3. **app.main.py:** `from app.ui.command_center` → `from app.gui.domains.command_center`
4. **tests/ui/test_command_center_dashboard.py:** `from app.ui.command_center` → `from app.gui.domains.command_center`

---

## 4. Klassifikation

| Komponente | Aktion |
|------------|--------|
| Alle 10 Dateien | MIGRATE_AS_IS |
