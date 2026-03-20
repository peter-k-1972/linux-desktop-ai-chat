# Kommandozentrale – Architekturbegründung

**Version:** Phase C (Operations Center)  
**Datum:** 2026-03-15

## Ziel

Die Kommandozentrale dient als Operations Center mit geordneten Arbeitskontexten und Guided Workflows. Rein UI-/Read-Modell-orientiert, keine Änderung an QA-Logik, scripts/qa oder docs/qa.

## Architektur-Entscheidungen

### 1. Integrationspunkt

- **Ort:** `QStackedWidget` im `MainWindow` (neben `ChatWidget`, `ProjectChatListWidget`)
- **Zugang:** Toolbar-Button „Kommandozentrale“ (info.svg)
- **Begründung:** Einheitliches Navigationsmuster; kein separates Fenster

### 2. Modulare Struktur (Phase B)

| Komponente | Datei | Rolle |
|------------|------|-------|
| **QADashboardAdapter** | `app/qa/dashboard_adapter.py` | Read-only, load(), load_qa_drilldown(), load_subsystem_detail(), load_governance() |
| **CommandCenterView** | `app/ui/command_center/command_center_view.py` | Haupt-View mit Stack-Navigation |
| **QADrilldownView** | `app/ui/command_center/qa_drilldown_view.py` | QA-Detail: Gaps, Coverage, Orphan Backlog |
| **SubsystemDetailView** | `app/ui/command_center/subsystem_detail_view.py` | Subsystem-Detail: Tests, Domains, Hints |
| **RuntimeDebugView** | `app/ui/command_center/runtime_debug_view.py` | Einstieg Runtime/Debug – verlinkt auf Chat-Sidepanel |
| **GovernanceView** | `app/ui/command_center/governance_view.py` | Freeze-Zonen: QA-Kern, Produkt, Experimentell |
| **Drilldown-DTOs** | `app/qa/drilldown_models.py` | QADrilldownData, SubsystemDetailData, GovernanceData |
| **OperationsAdapter** | `app/qa/operations_adapter.py` | load_incident_operations, load_qa_operations, load_review_operations, load_audit_operations |
| **QAOperationsView** | `app/ui/command_center/qa_operations_view.py` | Verifikationsstatus, Artefakte |
| **IncidentOperationsView** | `app/ui/command_center/incident_operations_view.py` | Incidents, Bindings, Replay-Status |
| **ReviewOperationsView** | `app/ui/command_center/review_operations_view.py` | Orphan Backlog, Review-Batches |
| **AuditOperationsView** | `app/ui/command_center/audit_operations_view.py` | Audit-Follow-ups, Technical Debt |

### 3. Navigationspunkte

| Von | Aktion | Nach |
|-----|--------|------|
| Overview | „QA Drilldown →“ | QADrilldownView |
| Overview | Klick auf Subsystem-Karte | SubsystemDetailView |
| Overview | „Zum Chat (Debug-Panel)“ | Chat (MainWindow) |
| Overview | „Governance anzeigen →“ | GovernanceView |
| Overview | Guided Workflow / Operations-Buttons | QA/Incident/Review/Audit Operations |
| Drilldown-Views | „← Zurück“ | Overview |

### 4. Wiederverwendete Panels

- **AgentDebugPanel** (Aktivität, Timeline, Task-Graph, Tool-Execution, Model-Usage): Im Chat-Sidepanel – RuntimeDebugView verlinkt dorthin, dupliziert nicht.

### 5. Phase-B-Funktionen

1. **QA Drilldown:** Priorisierte Gaps (Tabelle), Coverage-Achsen, Orphan-Backlog-Aufschlüsselung
2. **Subsystem Drilldown:** Klickbare Karten → Detail mit Testanzahl, Domains, Failure Classes, Hints
3. **Runtime/Debug:** Zentraler Einstieg, Link zum Chat/Debug-Panel, leerer Zustand wenn keine Live-Daten
4. **Governance:** Sichtbare Trennung QA-Kern (stabil), Produktentwicklung (aktiv), Experimentell
5. **Next Actions:** Erweitert um auffällige Subsysteme (wenig Tests)

### 6. Phase-C: Operations Center

1. **Guided Workflow Entry:** Orphan Review, QA Verification, Incident-Status, Audit Follow-up
2. **QA Operations:** Verifikationsstatus, Artefakt-Links, Einstieg Verifikation
3. **Incident Operations:** Incidents-Übersicht, Bindings, Replay-Readiness, Warnungen
4. **Review Operations:** Orphan Backlog, Review-Batches, treat_as
5. **Audit Operations:** Strukturierte Darstellung aus AUDIT_REPORT.md (Kategorie, Datei, Beschreibung)

### 7. Datenfluss

```
docs/qa/*.json ─► QADashboardAdapter ─► DTOs (DashboardData, QADrilldownData, …) ─► Views
```

- GUI parst keine JSON-Dateien direkt
- Saubere Trennung: Adapter (Read-Model) ↔ View

### 8. Tests

- `tests/ui/test_command_center_dashboard.py`
  - Adapter: load, load_qa_drilldown, load_subsystem_detail, load_governance
  - Operations: load_incident_operations, load_review_operations, load_guided_workflows, load_audit_operations
  - View: Öffnen, Drilldown-Navigation, Operations-Navigation, leere Zustände

## Keine Änderungen an

- scripts/qa
- docs/qa (nur Lesen)
- Gap-Priorisierung, Coverage-Map-Regeln, Orphan-Governance
