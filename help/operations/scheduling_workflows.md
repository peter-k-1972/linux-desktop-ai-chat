---
id: scheduling_workflows
title: Geplante Workflow-Ausführungen
category: operations
tags: [workflows, scheduling, geplant, operations]
related: [workflows_workspace, operations_betrieb]
# Kontexthilfe: nur workflows_workspace.md trägt workspace: operations_workflows (kanonisch).
screen: operations
order: 36
---

# Geplant (Workflows)

Im Bereich **Operations → Workflows** gibt es den Unter-Tab **Geplant** (neben Editor und Läufen). Dort pflegen Sie **zeitgesteuerte Auslöser** für gespeicherte Workflows.

## Tabelle „Geplante Ausführungen“

| Spalte | Bedeutung |
|--------|-----------|
| **workflow_id** | ID des Workflows, der gestartet werden soll |
| **Name** | Anzeigename des Workflows (aus der Definition) |
| **next_run_at (UTC)** | Nächster geplanter Startzeitpunkt in UTC (ISO-Format) |
| **lokal** | dieselbe Zeit für Lesbarkeit in lokaler Zeitzone |
| **aktiv** | **ja** / **nein** — nur aktive Einträge werden automatisch berücksichtigt |
| **letzter Run** | Run-ID des zuletzt über diesen Schedule gestarteten Laufs (sofern protokolliert) |

Unter der Tabelle zeigt eine **Detailzeile** u. a. `schedule_id`, `rule_json` (Regel inkl. Wiederholung) und `last_fired_at`.

## Intervall (Wiederholung)

Beim **Anlegen** oder **Bearbeiten** eines Schedules (Dialog):

- **next_run_at (UTC):** erster bzw. nächster Start.
- **repeat_interval_seconds:** Wiederholungsabstand in Sekunden (≥ 60 s für Wiederholung, **0** = nach Ausführung kein weiterer automatischer Termin).
- **initial_input (JSON):** Starteingaben des Workflows.
- **Aktiv:** Schalter, ob der Eintrag läuft.

Die **nächste Ausführung** entspricht dem Feld `next_run_at` in der Tabelle; nach einem erfolgreichen Tick wird sie gemäß Regel fortgeschrieben (oder der Eintrag deaktiviert, wenn einmalig).

## Schaltflächen

| Aktion | Wirkung |
|--------|---------|
| **Aktualisieren** | Liste neu laden |
| **Anlegen…** / **Bearbeiten…** | Dialog für Zeit, Workflow, JSON-Eingabe, Intervall, Aktiv |
| **Aktivieren/Deaktivieren** | Kippt den Aktiv-Status des gewählten Eintrags |
| **Jetzt ausführen** | Startet den Workflow **sofort** mit den gespeicherten Eingaben (siehe unten) |
| **Zum letzten Run** | Springt zum zuletzt protokollierten Run (nur wenn vorhanden) |
| **Löschen** | Entfernt den Schedule (inkl. zugehörigem Ausführungs-Log) |

**Hinweis:** **Jetzt ausführen** ist nur sinnvoll, wenn der Eintrag **aktiv** ist; deaktivierte Schedules werden abgewiesen.

## Wichtig: keine eigene Ausführungs-Engine

**Scheduling startet keine separate Workflow-Engine.** Ob ein Termin fällig wird (**Tick**) oder Sie **Jetzt ausführen** wählen — die eigentliche Ausführung läuft immer über **`WorkflowService.start_run()`** (derselbe Codepfad wie manuelle/Test-Runs im Workflow-Bereich).

Die App nutzt dafür den **ScheduleService** (Claim, Log, Fortschreiben von `next_run_at`). Technische Vertiefung: [`docs/user/scheduling.md`](../../docs/user/scheduling.md).

## Siehe auch

- [Workflow-Editor](workflows_workspace) — Definitionen speichern, validieren, Test-Runs  
- [Betrieb](operations_betrieb) — Incidents bei fehlgeschlagenen Läufen  
