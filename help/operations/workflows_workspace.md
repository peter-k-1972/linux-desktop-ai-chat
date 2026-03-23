---
id: workflows_workspace
title: Workflow-Editor
category: operations
tags: [workflows, operations, dag, editor]
related: [prompt_studio_overview, agents_overview, chat_overview]
workspace: operations_workflows
order: 35
---

# Workflow-Editor (Operations)

## Überblick

Unter **Operations → Workflows** bearbeiten Sie **gespeicherte Workflow-Definitionen** (Knoten + Kanten als DAG). Ausführung und Historie laufen über den **WorkflowService** und die App-Datenbank — unabhängig vom Chat-Fenster.

**Hinweis:** Slash-Commands wie `/delegate` oder Research-Pfade sind **Chat-Abläufe**, nicht dieselben Objekte wie die hier gespeicherten Workflows. Kurzüberblick: [`docs/02_user_manual/workflows.md`](../../docs/02_user_manual/workflows.md).

## Projektzuordnung

- Workflows können **global** sein (in der Liste „Global“) oder einem **Projekt** zugeordnet.
- **Neu anlegen:** Standard ist das **aktive Projekt** aus der Kopfzeile; ohne aktives Projekt wird der Workflow **global** gespeichert.
- **Liste:** Mit aktivem Projekt sehen Sie **Projekt-Workflows** und **globale** Workflows. Ohne aktives Projekt: **alle** Einträge.
- Im Bereich **Workflow** (Kopf des Editors): **Projekt** per Dropdown ändern und speichern.

## Bedienung

1. **Workflow wählen oder anlegen** (Liste links; Spalte **Projekt** zeigt die Zuordnung).
2. **Knoten/Kanten** im Tabellen-Editor pflegen; optional **Canvas** zur Orientierung.
3. **Knoten wählen** → **Inspector** (Dock): `node_id`, Typ, Titel, `config` als JSON bearbeiten und anwenden.
4. **Speichern** — speichert immer; bei Validierungsfehlern wird der Status `invalid`, der Text der Fehler erscheint in der Meldung.
5. **Validieren** — nur Prüfung, ohne erneutes Speichern erzwingen.
6. **Test-Run** — Dialog für `initial_input` (JSON-Objekt); Run wird synchron ausgeführt, danach erscheint er in der **Run-Liste**.

## Run-Ansicht

- Tabelle **Runs**: Status, Zeiten, `workflow_version` (Stand des Snapshots beim Start).
- **NodeRuns**: Reihenfolge der ausgeführten Knoten; Doppelklick / „Knoten im Editor wählen“ springt zum Knoten.
- **Input / Output / Fehler**: Payloads als JSON-Text. Nicht serialisierbare Werte werden als `repr` dargestellt.

Wenn ein Run **älter** ist als die aktuelle Definition, können Knoten **ohne** NodeRun existieren (Knoten wurde später hinzugefügt oder der Lauf war abgebrochen). Das Canvas-Overlay zeigt dann für diese Knoten keinen Status.

## Wichtige Grenzen

- Kantenfeld **`condition`** wird nicht ausgewertet (nur Warnung bei Validierung).
- Keine parallele Ausführung von Knoten in dieser Engine-Phase.
- **`context_load`** und **`chain_delegate` / execute** haben zusätzliche fachliche Voraussetzungen (gültige `chat_id` bzw. Agent-Routing); siehe Benutzerhandbuch.

## Siehe auch

- [Prompt Studio](prompt_studio_overview) (Vorlagen für `prompt_build` mit `prompt_id`)
- [Agenten](agents_overview) (Bezug zu `agent`-Knoten)
