# Audit und Incidents (Betrieb)

**Zielgruppe:** Betrieb, Entwickler, Second-Level-Support.  
**Bezug zur Oberfläche:** Operations → Betrieb → Register **Aktivität** / **Störungen**.

## Tabellen (SQLite, App-Datenbank)

### `audit_events`

Append-only-Protokoll für nachvollziehbare Vorgänge.

| Feld (konzeptionell) | Rolle |
|----------------------|--------|
| `occurred_at` | Zeitstempel |
| `event_type` | Stabiler Code (z. B. `workflow_started`, `project_created`, `deployment_rollout_recorded`) |
| `actor` | Wer / was (V1 typisch `local`) |
| `summary` | Kurztext für Listen und Suche |
| `payload_json` | Optionale strukturierte Details |
| `project_id`, `workflow_id`, `run_id`, `incident_id` | optionale Fremdverknüpfungen |

**Abdeckung über die reine Workflow-Fehlerwelt hinaus:** u. a. Projekt-Lebenszyklus (erstellt / geändert / gelöscht), Deployment-Mutationen (Ziel, Release, Rollout protokolliert), Workflow-Starts und Re-Runs, Incident-Erstellung und Statuswechsel.

Implementierung: `app/core/audit/repository.py`, Typen in `app/core/audit/models.py` (`AuditEventType`).

### `incidents`

Störungen, die **operativ** aus fehlgeschlagenen Workflow-Läufen entstehen und bearbeitet werden können.

| Feld (konzeptionell) | Rolle |
|----------------------|--------|
| `status` | z. B. offen, zur Kenntnis genommen, erledigt, ignoriert |
| `severity` | Einordnung |
| `title`, `short_description` | Anzeige in der UI |
| `workflow_run_id`, `workflow_id` | Anker zum fehlgeschlagenen Lauf |
| `project_id` | aus Snapshot der Definition, falls vorhanden |
| `fingerprint` | Dedupe mehrerer Fehlläufe „derselben“ Ursache |
| `diagnostic_code` | maschinenlesbare Einordnung |
| `occurrence_count`, `first_seen_at`, `last_seen_at` | Wiederholung |

## Wann entsteht ein Incident?

**Nur** wenn ein Workflow-Lauf terminal mit Status **`failed`** endet.

Ablauf (vereinfacht):

1. `WorkflowService.start_run()` führt den Lauf aus und persistiert den Run inkl. NodeRuns.
2. Bei `FAILED` ruft der Service `IncidentService.sync_from_failed_run(run)` auf.
3. Existiert noch kein Incident mit gleichem **Fingerprint**, wird ein neuer Datensatz angelegt und ein Audit-Ereignis `incident_created` geschrieben.
4. Bei gleichem Fingerprint wird die **Wiederholungsanzahl** aktualisiert und `last_seen_at` / Beschreibung angepasst — ohne erneutes „create“-Audit pro Wiederholung.

Die **Diagnose** (Titel, Kurztext, optional fehlernder Knoten) kommt aus `app/workflows/diagnostics.summarize_workflow_run()`.

## Typische Fehlerbilder

- **Knoten fehlgeschlagen:** Erster `FAILED`-NodeRun liefert Kontext; sonst Run-Fehlermeldung.
- **Validierung vor Start:** Kein Incident, weil kein persistierter fehlgeschlagener Run (Start schlägt mit `WorkflowValidationError` fehl).
- **Mehrfach dieselbe Ursache:** Eine Incident-Zeile, steigende **Anz.** — sinnvoll für Alarmierungs-Spam zu vermeiden.

## Zusammenhänge zwischen Modulen

```
WorkflowService.start_run
        │
        ▼ (Run = FAILED)
IncidentService.sync_from_failed_run
        │
        ├──► incidents (insert/update by fingerprint)
        └──► audit_events (bei neuem Incident: incident_created)

AuditService / record_*  ──► audit_events (Projekt, Deployment, Workflow, …)
```

## Siehe auch

- [Plattform-Gesundheit](platform_health.md) — separates Lesen, keine Incident-Tabelle  
- [Workflows und Runs](workflows_runs.md) — Run-Modell, Re-Run, Diagnose  
- In-App: `help/operations/operations_betrieb.md`  
