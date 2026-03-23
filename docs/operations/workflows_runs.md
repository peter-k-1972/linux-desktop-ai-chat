# Workflows und Runs

**Zielgruppe:** Betrieb, Entwickler.  
**Bezug zur Oberfläche:** Operations → **Workflows** (Editor, **Geplant**, Run-Liste und Detail).

## Begriffe

| Begriff | Bedeutung |
|---------|-----------|
| **Workflow** | Persistierte **WorkflowDefinition** (DAG aus Knoten und Kanten), Version und Status `valid`/`invalid`. |
| **Run** | Ein konkreter Ausführungsversuch: `WorkflowRun` mit `run_id`, Snapshot der Definition zum Startzeitpunkt, `initial_input`, globalem Status und zugehörigen **NodeRuns**. |
| **Diagnose** | Aus einem Run abgeleitete Zusammenfassung für Menschen: Kopfzeile, Kurztext, optional **fehlernder Knoten** und Fehlertexte (`app/workflows/diagnostics.py`). |
| **Re-Run** | Neuer Run mit derselben `workflow_id` und den Eingaben eines früheren Laufs (`WorkflowService.start_run_from_previous` → intern `start_run(..., is_rerun=True)`). |

## Run-Read-Modell (Lesen und Historie)

- **Runs** und **NodeRuns** liegen in der App-Datenbank (Workflow-Repository).
- Die Run-Liste in der GUI nutzt schlanke **Summaries** (`list_run_summaries`), das Detail lädt den vollen Run inkl. Knotenläufe.
- **definition_snapshot** im Run erklärt, warum ältere Läufe von der aktuellen Graph-Struktur abweichen können.

## Ausführung (Kurz)

1. `WorkflowService.start_run(workflow_id, initial_input)` validiert die **aktuelle** Definition.
2. Run wird als `pending` gespeichert, Audit `workflow_started` (wenn Audit angebunden).
3. `WorkflowExecutor` führt Knoten sequentiell aus; NodeRuns werden währenddessen persistiert.
4. Abschluss: Run-Status `succeeded` / `failed` / `cancelled` / …; bei **`failed`** → Incident-Sync (siehe [audit_and_incidents.md](audit_and_incidents.md)).

**Geplante und manuelle „Jetzt ausführen“-Starts** enden im selben `start_run`-Pfad (`ScheduleService.tick_due` / `run_now`).

## Typische Fehlerbilder

| Bild | Hinweise |
|------|----------|
| **Fehlgeschlagener Knoten** | NodeRun mit Status `failed`; Diagnose zeigt `node_id` / Typ und Fehlertext. |
| **Fehlende Inputs** | Validierungsfehler vor Run oder Laufzeitfehler im Knoten, wenn `initial_input` / Kontext nicht passt. |
| **Externe Fehler** | z. B. Provider/HTTP, Tool nicht verfügbar — oft im Knoten- oder Run-Fehlertext. |
| **Run ohne FAILED-Knoten, aber Run failed** | Executor setzt Run auf failed ohne einzelnen FAILED-Node; Diagnose verweist darauf. |
| **Re-Run nicht möglich** | Historischer Run ohne brauchbare `workflow_id` → `IncompleteHistoricalRunError`. |

## Zusammenhänge zwischen Modulen

```
WorkflowDefinition (workflows)
        ▲
        │ snapshot beim start_run
WorkflowRun + NodeRuns
        │
        ├──► GUI: Liste, Detail, Canvas-Overlay
        ├──► diagnostics.summarize_workflow_run
        └──► bei FAILED: IncidentService.sync_from_failed_run
```

## Siehe auch

- [Audit und Incidents](audit_and_incidents.md)  
- Benutzer: [`docs/user/scheduling.md`](../user/scheduling.md) — Tabellen `workflow_schedules` / `schedule_run_log`  
- In-App: `help/operations/workflows_workspace.md`, `help/operations/scheduling_workflows.md`  
