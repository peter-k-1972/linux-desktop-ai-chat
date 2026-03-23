---
id: agents_overview
title: Agenten-System
category: operations
tags: [agenten, personas, departments]
related: [chat_overview, control_center_agents]
workspace: operations_agent_tasks
screen: operations
order: 20
---

# Agenten-System

## Inhalt

- [Konzept](#konzept)
- [Departments](#departments)
- [Standard-Agenten (18)](#standard-agenten-18)
- [Agenten erstellen](#agenten-erstellen)
- [Agenten im Chat](#agenten-im-chat)
- [Delegation](#delegation)

**Siehe auch (Repository)**

- [Feature: Agenten](../../docs/FEATURES/agents.md) · [Workflow: Agenten](../../docs_manual/workflows/agent_usage.md) · [Benutzerhandbuch – Delegation](../../docs/USER_GUIDE.md#55-delegation) · [Control Center – Agents](../control_center/control_center_agents.md)

## Konzept

Agenten sind **spezialisierte Personas** mit eigenem System-Prompt, zugewiesenem Modell und Fähigkeiten. Sie erscheinen in der Agent-Auswahl im Chat-Header.

Die folgenden **Departments** gruppieren vordefinierte Rollen; sie helfen bei der Auswahl, welcher Agent-Typ zu einer Aufgabe passt.

## Departments

- **Planning**: Planung, Projektmanagement
- **Research**: Recherche, Kritik, Wissensmanagement
- **Development**: Code, Debugging, Dokumentation, Skripte
- **Media**: Voice, Image, Video, Music
- **Automation**: Workflows, Tools, Scheduler
- **System**: Admin, Update, Recovery, Monitoring

Die Tabelle listet die mitgelieferten Standard-Agenten mit Kurzzuordnung; eigene Agenten legen Sie im Control Center an (siehe unten).

## Standard-Agenten (18)

| Agent | Department | Rolle |
|-------|------------|-------|
| Planner Agent | Planning | Planung |
| Critic Agent | Research | Qualitätssicherung |
| Research Agent | Research | Recherche, RAG |
| Knowledge Agent | Research | Wissensmanagement |
| Code Agent | Development | Programmierung |
| Debugger Agent | Development | Debugging |
| Documentation Agent | Development | Technische Texte |
| Script Agent | Development | Skripte |
| Voice Agent | Media | Audio/Voice |
| Image Agent | Media | Bildgenerierung |
| Video Agent | Media | Video |
| Music Agent | Media | Musik |
| Workflow Agent | Automation | ComfyUI |
| Tool Agent | Automation | Tool-Ausführung |
| Scheduler Agent | Automation | Zeitplanung |
| System Agent | System | Admin |
| Update Agent | System | Updates |
| Recovery Agent | System | Recovery |
| Monitor Agent | System | Monitoring |

## Agenten erstellen

1. **Control Center → Agents** öffnen
2. **Neuer Agent** – Formular ausfüllen
3. **Name, Slug, Department, Rolle, Modell, System-Prompt** setzen
4. Speichern

## Agenten im Chat

- Agent im Header auswählen → System-Prompt wird automatisch als erste Nachricht gesendet
- Modell wird aus `assigned_model` oder `assigned_model_role` übernommen
- Auto-Routing ist bei aktivem Agent deaktiviert (Agent bestimmt Modell)

## Delegation

Mit `/delegate <Anfrage>` wird die **Agenten-Orchestrierung** gestartet:

1. Task Planner zerlegt die Anfrage
2. Delegation Engine ordnet Tasks Agenten zu
3. Execution Engine führt Tasks aus
4. Ergebnis wird aggregiert
