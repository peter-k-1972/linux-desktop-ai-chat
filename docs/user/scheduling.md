# Workflow-Scheduling — Grundprinzip

Die App kann Workflow-Läufe **zeitgesteuert** oder per **Jetzt ausführen** anstoßen. Dieses Dokument fasst die **Daten** und den **Ausführungspfad** zusammen.

## Tabellen

### `workflow_schedules`

Speichert pro Eintrag u. a.:

- `schedule_id`, `workflow_id`
- `enabled` — ob der Eintrag für automatische Fälligkeit berücksichtigt wird
- `initial_input_json` — JSON-Objekt als Starteingaben für `start_run`
- `next_run_at` — nächster geplanter Start (UTC, ISO)
- `rule_json` — Regel, insbesondere **`repeat_interval_seconds`** (0 = nach Ausführung kein weiterer Termin)
- `last_fired_at`, `claim_until` — Fortschreibung und kurzfristige Sperre bei Tick-Verarbeitung

Repository: `app/workflows/persistence/schedule_repository.py`.

### `schedule_run_log`

Protokoll je ausgelöstem Lauf (über einen Schedule):

- `schedule_id`, `run_id`
- `due_at`, `claimed_at`
- `trigger_type` — z. B. fälliger Tick (**due**) oder **manuell** (`run_now`)
- `finished_status` — Endstatus des Runs (nach Ausführung)

Die letzte Run-ID pro Schedule wird u. a. für **„Zum letzten Run“** in der GUI genutzt.

## Grundprinzip

**Scheduling erzeugt nur Trigger** (fällige Zeiten, manueller Knopf). Die **Ausführung** erfolgt ausschließlich über:

```text
WorkflowService.start_run(workflow_id, initial_input)
```

Der `ScheduleService` (`app/services/schedule_service.py`):

- ermittelt fällige IDs (`list_schedule_ids_due`),
- setzt kurzzeitig `claim_until` (`try_claim_schedule`),
- ruft `start_run` auf,
- schreibt `schedule_run_log` und aktualisiert `next_run_at` / `enabled` / `last_fired_at` (`persist_due_tick_outcome`).

Der **UI-Ticker** (`ScheduleTickController`) ruft nur periodisch `tick_due` auf — er ist **kein** eigener Workflow-Interpreter.

## Siehe auch

- In-App-Hilfe: `help/operations/scheduling_workflows.md`  
- Operator-Tiefe: [`docs/operations/workflows_runs.md`](../operations/workflows_runs.md)  
- Glossar: [`docs/glossary/terminology.md`](../glossary/terminology.md)  
