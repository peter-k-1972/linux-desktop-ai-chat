# Command-Center-Subsystem: UI → GUI Migration Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Abschlussklassifikation:** `DONE`

---

## 1. Ausgangslage

- **app/ui/command_center/** – Vollständige Implementierung (keine Re-Exports)
- 10 Dateien mit CommandCenterView, QADrilldownView, SubsystemDetailView, RuntimeDebugView, GovernanceView, QAOperationsView, IncidentOperationsView, ReviewOperationsView, AuditOperationsView
- Konsumenten: app.main.py (Legacy MainWindow), tests/ui/test_command_center_dashboard.py

---

## 2. Migrierte Dateien/Klassen

| Alte Datei | Neue Datei |
|------------|------------|
| `app/ui/command_center/__init__.py` | `app/gui/domains/command_center/__init__.py` |
| `app/ui/command_center/command_center_view.py` | `app/gui/domains/command_center/command_center_view.py` |
| `app/ui/command_center/qa_drilldown_view.py` | `app/gui/domains/command_center/qa_drilldown_view.py` |
| `app/ui/command_center/subsystem_detail_view.py` | `app/gui/domains/command_center/subsystem_detail_view.py` |
| `app/ui/command_center/runtime_debug_view.py` | `app/gui/domains/command_center/runtime_debug_view.py` |
| `app/ui/command_center/governance_view.py` | `app/gui/domains/command_center/governance_view.py` |
| `app/ui/command_center/qa_operations_view.py` | `app/gui/domains/command_center/qa_operations_view.py` |
| `app/ui/command_center/incident_operations_view.py` | `app/gui/domains/command_center/incident_operations_view.py` |
| `app/ui/command_center/review_operations_view.py` | `app/gui/domains/command_center/review_operations_view.py` |
| `app/ui/command_center/audit_operations_view.py` | `app/gui/domains/command_center/audit_operations_view.py` |

---

## 3. Alte → neue Pfade

| Alt | Neu |
|-----|-----|
| `app.ui.command_center.CommandCenterView` | `app.gui.domains.command_center.CommandCenterView` |
| `app.ui.command_center.QADrilldownView` | `app.gui.domains.command_center.QADrilldownView` |
| `app.ui.command_center.SubsystemDetailView` | `app.gui.domains.command_center.SubsystemDetailView` |
| `app.ui.command_center.RuntimeDebugView` | `app.gui.domains.command_center.RuntimeDebugView` |
| `app.ui.command_center.GovernanceView` | `app.gui.domains.command_center.GovernanceView` |
| `app.ui.command_center.QAOperationsView` | `app.gui.domains.command_center.QAOperationsView` |
| `app.ui.command_center.IncidentOperationsView` | `app.gui.domains.command_center.IncidentOperationsView` |
| `app.ui.command_center.ReviewOperationsView` | `app.gui.domains.command_center.ReviewOperationsView` |
| `app.ui.command_center.AuditOperationsView` | `app.gui.domains.command_center.AuditOperationsView` |

---

## 4. Angepasste Importstellen

| Datei | Änderung |
|-------|----------|
| `app/main.py` | `from app.ui.command_center import CommandCenterView` → `from app.gui.domains.command_center import CommandCenterView` |
| `tests/ui/test_command_center_dashboard.py` | Alle 10 Imports: `from app.ui.command_center` → `from app.gui.domains.command_center` |

---

## 5. Technische Anpassungen

- **_project_root():** `parent.parent.parent.parent` → `Path(__file__).resolve().parents[4]` (gui/domains tiefer)
- **command_center_view.py:** Interne Imports von Sub-Views auf `app.gui.domains.command_center.*` umgestellt

---

## 6. Entfernte Legacy-Dateien

| Datei/Verzeichnis |
|-------------------|
| `app/ui/command_center/` (komplett) |
| `__init__.py`, `command_center_view.py`, `qa_drilldown_view.py`, `subsystem_detail_view.py`, `runtime_debug_view.py`, `governance_view.py`, `qa_operations_view.py`, `incident_operations_view.py`, `review_operations_view.py`, `audit_operations_view.py` |

---

## 7. Verbleibende temporäre Bridges

**Keine.**

---

## 8. Testläufe + Ergebnisse

| Test | Ergebnis |
|------|----------|
| `tests/architecture/test_gui_does_not_import_ui.py` | ✓ PASSED |
| `tests/ui/test_command_center_dashboard.py` | ✓ 25 passed |
| Import-Check: CommandCenterView, MainWindow | ✓ OK |

---

## 9. Bekannte Restrisiken

Keine.

---

## 10. Abschlussklassifikation

**DONE**

- Command-Center-Subsystem liegt kanonisch unter `app/gui/domains/command_center/`
- `app/ui/command_center/` vollständig entfernt
- Keine gui→ui-Verletzung
- Keine temporären Bridges
- Architekturguard grün
- Alle 25 Command-Center-Tests grün

---

## Konsole-Zusammenfassung

```
=== COMMAND CENTER UI → GUI MIGRATION ===

Migriert:
  - 10 Dateien: command_center_view, qa_drilldown_view, subsystem_detail_view,
    runtime_debug_view, governance_view, qa_operations_view, incident_operations_view,
    review_operations_view, audit_operations_view, __init__
  - Von: app/ui/command_center/
  - Nach: app/gui/domains/command_center/

Gelöscht:
  - app/ui/command_center/ (komplett)

Angepasst:
  - app/main.py: Import auf app.gui.domains.command_center
  - tests/ui/test_command_center_dashboard.py: 10 Import-Updates

Tests:
  - test_gui_does_not_import_ui: PASSED
  - test_command_center_dashboard: 25 passed

Blocker: Keine
```
