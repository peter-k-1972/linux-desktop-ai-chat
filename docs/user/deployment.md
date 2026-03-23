# Deployment — Fachmodell für Anwender und Admins

Dieses Kapitel beschreibt das **Deployment-Light** in der Desktop-App: Begriffe, Lifecycle und Audit — ohne Implementierungsdetails der GUI.

## Begriffe

| Begriff | Kurzbeschreibung |
|---------|------------------|
| **Target** | Benanntes Deployment-Ziel (Umgebung, Standort, …) mit optionaler Art und Projektbezug. |
| **Release** | Logische Software-/Paket-Version mit Metadaten (Name, Versionstext, Artefakt-Hinweise). |
| **Rollout** | Protokolleintrag: „Release X wurde Ziel Y mit Ergebnis Z ausgeführt“, optional mit Zeitfenster, Nachricht und Verknüpfung zu einem **Workflow-Run**. |

Persistenz: Tabellen über `DeploymentRepository` / Service `DeploymentOperationsService` (`app/core/deployment/`, `app/services/deployment_operations_service.py`).

## Lifecycle eines Releases

| Status | Bedeutung |
|--------|-----------|
| **draft** | In Arbeit; **keine** neuen Rollouts erlaubt. |
| **ready** | Freigegeben; **nur** in diesem Status dürfen neue Rollout-Einträge erstellt werden. |
| **archived** | Abgeschlossen; keine neuen Rollouts. |

Neue Releases starten typischerweise als **draft**; über Bearbeitung wechseln Sie zu **ready**, wenn die Version ausrollbar ist. **Archivieren** ist ein expliziter Schritt in der Oberfläche.

## Rollouts

- Rollouts sind **Historie** — sie lösen kein externes Deployment aus.
- Ein optional gesetztes **`workflow_run_id`** dient der **Nachverfolgbarkeit** (z. B. Automatisierungslauf, der das Deployment durchgeführt hat).

## Audit-Ereignisse für Deployment

Mutationen schreiben **Audit-Events** (Tabelle `audit_events`), u. a.:

- `deployment_target_mutated` — Anlegen/Aktualisieren eines Ziels  
- `deployment_release_mutated` — Anlegen/Aktualisieren/Archivieren  
- `deployment_rollout_recorded` — neuer Rollout-Eintrag  

Damit sind Deployment-Aktionen in **Operations → Betrieb → Aktivität** nach Typ filterbar.

## Siehe auch

- In-App-Hilfe: `help/operations/deployment_workspace.md`  
- Glossar: [`docs/glossary/terminology.md`](../glossary/terminology.md)  
