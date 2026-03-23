---
id: projects_overview
title: Projekte
category: operations
tags: [projekte, workspace, kontext]
related: [chat_overview, knowledge_overview]
workspace: operations_projects
order: 50
---

# Projekte

## Überblick

**Projekte** gruppieren Chats, Knowledge-Quellen, Prompts und Agent-Tasks. Der aktive Projekt-Kontext bestimmt, welche Daten sichtbar sind.

**Operations → Projekte** ist die zentrale Verwaltungsoberfläche: dort legen Sie Projekte an, bearbeiten Name/Beschreibung/Status, setzen optional die **Standard-Kontextpolicy** (Render-Budget für Chat-Kontext, wenn der Chat keine eigene Policy hat) und löschen Projekte mit klarer Bestätigung. Kennzahlen im Überblicksbereich beziehen sich auf **Knowledge-Quellen** (RAG), **projektgebundene Workflows** und **Datei-Links in der Datenbank** (`project_files`) — letztere sind keine Knowledge-Quellen.

Ohne gewähltes Projekt arbeiten viele Bereiche in einem **globalen** Kontext; mit Projekt sehen Sie nur die zugehörigen Sessions und Quellen — sinnvoll, wenn Sie mehrere Mandanten oder Themen strikt trennen möchten.

## Projekt wechseln

- **Operations → Projekte**: Projekt in der Liste wählen; optional **Als aktives Projekt setzen**
- **Sidebar** (Bereich PROJECT): **Projekte** wählen; Projekt in der Liste anklicken
- **Project Switcher** (z. B. in der TopBar): aktives Projekt wechseln

## Projekt-spezifische Daten

- Chat-Sessions (Zuordnung)
- Knowledge-Quellen (RAG, Ordner `project_<id>` unter dem App-RAG-Pfad)
- Prompts
- Agentenprofile (projektbezogene Einträge)
- Workflows mit Projektzuordnung

## Projekt löschen

Beim Löschen eines Projekts (z. B. **Operations → Projekte** → „Projekt löschen“, oder in der **Legacy-Sidebar**):

- **Chats** bleiben erhalten; nur die **Zuordnung** zum Projekt und die **Themen** dieses Projekts entfallen bzw. werden entfernt.
- **Prompts**, **Agenten** und **Workflows**, die nur diesem Projekt zugeordnet waren, werden **nicht** gelöscht: sie werden **global** (ohne `project_id`), damit keine Inhalte verloren gehen.
- **Knowledge:** der RAG-Unterordner `project_<id>` wird entfernt (Index und Metadaten der App). **Dateien auf Ihrer Festplatte**, die nur in Quellenlisten referenziert waren, werden dabei **nicht** automatisch gelöscht.
- **Datei-Verknüpfungen** (`project_files`) in der Datenbank werden aufgehoben; die Einträge in der Dateitabelle bleiben.
- War das gelöschte Projekt **aktiv**, wird der aktive Projektkontext **geleert** (kein Ersatzprojekt wird automatisch gewählt).

## Siehe auch

- [Chat](chat_overview)
- [Knowledge](knowledge_overview)
