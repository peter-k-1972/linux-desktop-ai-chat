# Project Hub – Implementierung

**Status:** Implementiert  
**Datum:** 2026-03-15

## Überblick

Der Project Hub ist der zentrale Einstiegspunkt für projektbezogene Arbeit. Er fasst Chats, Quellen und Prompts eines Projekts zusammen, zeigt letzte Aktivität und bietet Quick Actions zur Navigation in die jeweiligen Workspaces.

---

## Wichtigste Klassen

| Klasse | Datei | Zweck |
|--------|------|-------|
| **ProjectOverviewPanel** | `projects/panels/project_overview_panel.py` | Haupt-Dashboard: Header, Stats, Aktivität, Quick Actions |
| **ProjectHeaderCard** | `projects/panels/project_header_card.py` | Projektname, Beschreibung, Metadaten |
| **ProjectStatsPanel** | `projects/panels/project_stats_panel.py` | Kennzahlen: Chats, Quellen, Prompts |
| **ProjectActivityPanel** | `projects/panels/project_activity_panel.py` | Drei Blöcke: Letzte Chats, Quellen, Prompts (klickbar) |
| **ProjectQuickActionsPanel** | `projects/panels/project_quick_actions_panel.py` | Neuer Chat, Quelle hinzufügen, Neuer Prompt, Knowledge, Prompt Studio, Agents |
| **OperationsContext** | `operations/operations_context.py` | Pending Context für Hub→Workspace-Navigation |

---

## UX-Entscheidungen

1. **Projekt-Hub als Default-Screen**  
   Der Project Hub ist Teil des ProjectsWorkspace. Beim Öffnen von Operations/Projekte erscheint die Projektliste links, der Hub rechts.

2. **Aktivierung vor Navigation**  
   Beim Klick auf Chat/Prompt/Quelle oder Quick Action wird das angezeigte Projekt automatisch als aktiv gesetzt, falls noch nicht.

3. **Direkte Navigation mit Kontext**  
   Klick auf einen Chat öffnet ChatWorkspace mit diesem Chat. Klick auf Prompt öffnet PromptStudio mit diesem Prompt. Klick auf Quelle öffnet Knowledge mit dieser Quelle.

4. **Drei getrennte Aktivitätsblöcke**  
   Letzte Chats, Quellen, Prompts werden in eigenen Abschnitten angezeigt – nicht in einer gemischten Liste.

5. **Quick Actions**  
   Sechs Aktionen: Neuer Chat, Quelle hinzufügen, Neuer Prompt, Knowledge öffnen, Prompt Studio öffnen, Agents öffnen.

---

## Service-Integration

| Service | Methode | Verwendung |
|---------|---------|------------|
| ProjectService | get_project_summary | Stats, Metadaten |
| ProjectService | get_recent_project_activity | Chats, Prompts, Quellen |
| ProjectService | count_chats_of_project | Stat-Karte |
| ProjectService | get_project_sources | Quellen-Liste |
| PromptService | list_project_prompts | Nur projektbezogene Prompts |

---

## Navigation mit Kontext

1. **OperationsContext**  
   `set_pending_context({"chat_id": 123})` vor `show_area()`.

2. **OperationsScreen.show_workspace**  
   Nach dem Wechsel: `consume_pending_context()` und `widget.open_with_context(ctx)`.

3. **Workspace-APIs**  
   - ChatWorkspace: `open_with_context({"chat_id": int})`
   - PromptStudioWorkspace: `open_with_context({"prompt_id": int})`
   - KnowledgeWorkspace: `open_with_context({"source_path": str})`

---

## Startanweisung

```bash
cd Linux-Desktop-Chat
.venv/bin/python main.py
```

1. Operations → Projekte
2. Projekt aus der Liste wählen
3. Project Hub zeigt: Header, Stats, Letzte Chats/Quellen/Prompts, Quick Actions
4. Klick auf Chat → ChatWorkspace mit diesem Chat
5. Klick auf Prompt → PromptStudio mit diesem Prompt
6. Klick auf Quelle → Knowledge mit dieser Quelle
7. Quick Actions → Navigation in die jeweiligen Workspaces

---

## Dateien (neu/geändert)

- `app/gui/domains/operations/operations_context.py` – **neu**
- `app/gui/domains/operations/operations_screen.py` – consume_pending_context, open_with_context
- `app/gui/domains/operations/chat/chat_workspace.py` – open_with_context
- `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py` – open_with_context
- `app/gui/domains/operations/knowledge/knowledge_workspace.py` – open_with_context
- `app/gui/domains/operations/knowledge/panels/knowledge_source_explorer_panel.py` – select_source
- `app/gui/domains/operations/projects/panels/project_overview_panel.py` – Navigation mit Context, _ensure_project_active
- `app/gui/domains/operations/projects/panels/project_activity_panel.py` – Drei Blöcke, source_clicked
- `app/gui/domains/operations/projects/panels/project_quick_actions_panel.py` – Knowledge, Prompt Studio
- `app/services/project_service.py` – list_project_prompts für recent
