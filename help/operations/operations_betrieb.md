---
id: operations_betrieb
title: Betrieb (Audit, Störungen, Plattform)
category: operations
tags: [betrieb, audit, incidents, plattform, operations]
related: [workflows_workspace, deployment_workspace, scheduling_workflows]
workspace: operations_audit_incidents
screen: operations
order: 38
---

# Betrieb (Operations)

Unter **Operations → Betrieb** sehen Sie drei Registerkarten: **Aktivität**, **Störungen** und **Plattform**. Hier geht es um Nachvollziehbarkeit, Fehler aus Workflow-Läufen und einen schnellen Gesundheitscheck — ohne tiefe Architektur.

## Register **Aktivität** (Audit Events)

Chronologische Liste der protokollierten Ereignisse.

| Spalte | Bedeutung |
|--------|-----------|
| **Zeit** | Zeitstempel des Ereignisses (`occurred_at`) |
| **Typ** | Technischer Ereignistyp (z. B. `workflow_started`, `incident_created`) |
| **Zusammenfassung** | Kurztext zur schnellen Orientierung |
| **Projekt** | Projekt-ID, falls zutreffend (sonst leer) |
| **Workflow** | `workflow_id`, falls zutreffend |
| **Run** | `run_id`, falls zutreffend |

**Filter:** Dropdown **Ereignistyp** — z. B. nur Workflow-Starts, Projektänderungen, Incident-Erstellung oder Deployment-Ereignisse. **Alle Typen** zeigt die komplette Liste (begrenzte Anzahl, typischerweise bis ca. 800 Einträge).

**Aktualisieren** lädt die Tabelle neu.

**Typische Nutzung:** Nachvollziehen, wer was wann getan hat; Zusammenhang zwischen Workflow-Aktivität und anderen Domänen (Projekt, Deployment) erkennen.

## Register **Störungen** (Incidents)

Liste von **Störungen**, die aus **fehlgeschlagenen Workflow-Läufen** abgeleitet werden (siehe auch [Workflow-Editor](workflows_workspace)).

| Spalte | Bedeutung |
|--------|-----------|
| **Zuletzt** | Letztes Auftreten |
| **Status** | z. B. offen, zur Kenntnis genommen, erledigt, ignoriert |
| **Schwere** | Einordnung der Störung |
| **Titel** | Kurzüberschrift (aus Lauf-Diagnose) |
| **Workflow** | Zugehörige `workflow_id` |
| **Run** | Zugehörige `workflow_run_id` |
| **Anz.** | Wie oft dieselbe Störung (Fingerprint) wieder aufgetreten ist |

**Filter:** **Statusfilter** — nur Einträge mit gewähltem Status oder **alle Stati**.

**Detailbereich** (rechts nach Auswahl einer Zeile): Kurzbeschreibung, Fingerprint, optional Diagnosecode und Notiz.

**Aktionen**

- **Status setzen:** Neuen Status wählen, optional **Notiz** eintragen, dann **Status setzen**.
- **Zum Run …:** Wechselt zu **Operations → Workflows** und öffnet den Kontext für den in der Zeile stehenden **Run** (gleicher Mechanismus wie bei Deployment-Rollouts mit Run-Verknüpfung).

**Zusammenhang Workflow-Run → Incident:** Endet ein Lauf mit Status **fehlgeschlagen** (`failed`), legt das System ein Incident an oder erhöht die **Wiederholungsanzahl** bei gleichem Fingerprint. In **Aktivität** erscheinen passende Audit-Einträge (z. B. Incident erstellt, Status geändert).

## Register **Plattform**

Read-only-Übersicht: **Gesamtstatus** (OK / Warnung / Fehler), Zeitpunkt der letzten Prüfung, Tabelle der Einzelchecks.

| Spalte | Bedeutung |
|--------|-----------|
| **Check** | Bezeichnung (z. B. Data-Store, Ollama lokal, Tool) |
| **Status** | Schweregrad in Kurzform (OK / WARNING / ERROR) |
| **Detail** | Erläuterung oder Fehlertext |

**Erneut prüfen** startet die Checks erneut (läuft im Hintergrund; die Oberfläche friert nicht ein).

**Typische Nutzung:** Schnell prüfen, ob lokale Infrastruktur (z. B. Ollama) und konfigurierte Data Stores / Tools in einem erwarteten Zustand sind.

## Siehe auch

- [Workflow-Editor](workflows_workspace) — Runs, Diagnose, Re-Run  
- [Deployment](deployment_workspace) — Rollouts mit optionaler Run-ID  
