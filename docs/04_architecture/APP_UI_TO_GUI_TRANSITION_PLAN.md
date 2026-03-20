# App UI → GUI Transition Plan

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Plan – keine physischen Datei-Moves  
**Referenz:** APP_MOVE_MATRIX.md, APP_TARGET_PACKAGE_ARCHITECTURE.md, APP_PACKAGE_ARCHITECTURE_ASSESSMENT.md

---

## Übersicht

`app/ui/` (89 Dateien) und `app/gui/` (210+ Dateien) existieren parallel. Die neue Shell nutzt `gui/domains/`; viele Workspaces importieren jedoch noch Komponenten aus `ui/`. Dieser Plan analysiert domainweise und definiert Aktionen pro Datei – **ohne sofortige physische Moves**.

---

## Querschnitt: ui-Module aktiv von gui/main importiert

| ui-Modul | Importiert von | Typ |
|----------|----------------|-----|
| `ui.chat` (ChatNavigationPanel, ChatDetailsPanel) | gui/domains/operations/chat/chat_workspace.py | Direkt |
| `ui.chat` (ConversationView, ChatComposerWidget, ChatHeaderWidget) | app/chat_widget.py (Legacy) | Direkt |
| `ui.prompts` (PromptStudioWorkspace) | ~~gui/domains/operations/operations_screen.py~~ | **✓ migriert** – nutzt gui |
| `ui.prompts` (PromptVersionPanel) | ~~gui/inspector/prompt_studio_inspector.py~~ | **✓ migriert** – nutzt gui |
| `ui.settings` (SettingsWorkspace) | gui/domains/settings/settings_screen.py | Lazy |
| `ui.project` (ProjectSwitcherButton) | gui/shell/top_bar.py | Direkt |
| `ui.project` (ProjectHubPage) | gui/domains/project_hub/project_hub_screen.py | Direkt |
| `ui.events` (subscribe_project_events) | gui (chat, knowledge, prompt_studio, agent_tasks, session_explorer, library_panel, knowledge_source_explorer), core/project_context_manager (emit) | Querschnitt |
| `ui.widgets` (EmptyStateWidget) | gui (knowledge_source_explorer, library_panel, session_explorer), ui (settings, knowledge, chat) | Querschnitt |
| `ui.sidepanel` (ChatSidePanel) | app/chat_widget.py (Legacy) | Direkt |
| `ui.command_center` (CommandCenterView) | app/main.py (Legacy) | Direkt |
| `ui.settings_dialog` (SettingsDialog) | app/main.py (Legacy) | Direkt |
| `ui.agents` (AgentManagerDialog) | app/main.py (Legacy) | Lazy |
| `ui.debug` (AgentDebugPanel) | ui/sidepanel/chat_side_panel.py | Direkt |

---

## Domain 1: Chat

### Aktive gui-Module

| Modul | Rolle |
|-------|-------|
| `gui/domains/operations/chat/chat_workspace.py` | ChatWorkspace – Session Explorer + Conversation + Input |
| `gui/domains/operations/chat/panels/` | ChatConversationPanel, ChatInputPanel, SessionExplorerPanel |

### Aktive ui-Module (Stand: 2026-03-16 Chat Migration Sprint)

| Modul | Importiert von | Status |
|-------|----------------|--------|
| `ui/chat/chat_navigation_panel.py` | – | **migriert** → gui/panels/ |
| `ui/chat/chat_details_panel.py` | – | **migriert** → gui/panels/ |
| `ui/chat/topic_actions.py` | – | **migriert** → gui/panels/; ui nur Re-Export |
| `ui/chat/topic_editor_dialog.py` | – | **migriert** → gui/panels/; ui nur Re-Export |
| `ui/chat/chat_item_context_menu.py` | – | **migriert** → gui/panels/; ui nur Re-Export |
| `ui/chat/chat_message_widget.py` | – | **migriert** → gui/panels/; ui nur Re-Export |
| `ui/chat/conversation_view.py` | chat_widget (Legacy) | keep_temporarily |
| `ui/chat/chat_composer_widget.py` | chat_widget (Legacy) | keep_temporarily |
| `ui/chat/chat_header_widget.py` | chat_widget (Legacy) | keep_temporarily |
| `ui/chat/chat_list_item.py` | ui.chat.chat_topic_section | keep_temporarily |
| `ui/chat/chat_topic_section.py` | gui.chat_navigation_panel | keep_temporarily |

### Überschneidungen

- **ChatNavigationPanel**: gui nutzt ui-Version. gui hat SessionExplorerPanel – andere API (projektbezogen).
- **ChatDetailsPanel**: gui nutzt ui-Version. Kein gui-Äquivalent.
- **ConversationView / ChatComposerWidget / ChatHeaderWidget**: Nur Legacy chat_widget. gui nutzt ChatConversationPanel, ChatInputPanel.

### Kanonischer Zielort

`gui/domains/operations/chat/panels/`

### Aktionen pro Datei

| ui-Datei | Aktion | Status (2026-03-16) |
|----------|--------|---------------------|
| chat_navigation_panel.py | **move** | ✓ migriert (Phase A.3) |
| chat_details_panel.py | **move** | ✓ migriert (Phase A.3) |
| topic_actions.py | **move** | ✓ migriert; ui Re-Export |
| topic_editor_dialog.py | **move** | ✓ migriert; ui Re-Export |
| chat_item_context_menu.py | **move** | ✓ migriert; ui Re-Export |
| chat_message_widget.py | **move** | ✓ migriert; ui Re-Export; conversation_view nutzt gui |
| chat_list_item.py | **merge** | keep_temporarily; Prüfen: gui hat kein direktes Äquivalent |
| chat_topic_section.py | **move** | keep_temporarily; von chat_navigation_panel importiert |
| conversation_view.py | **keep_temporarily** | Nur Legacy chat_widget |
| chat_composer_widget.py | **keep_temporarily** | Nur Legacy |
| chat_header_widget.py | **keep_temporarily** | Nur Legacy |

---

## Domain 2: Knowledge

### Aktive gui-Module

| Modul | Rolle |
|-------|-------|
| `gui/domains/operations/knowledge/knowledge_workspace.py` | KnowledgeWorkspace – RAG, Quellen-Explorer |
| `gui/domains/operations/knowledge/panels/` | KnowledgeSourceExplorerPanel, KnowledgeOverviewPanel, RetrievalTestPanel, SourceListItemWidget |

### Aktive ui-Module

| Modul | Importiert von |
|-------|----------------|
| `ui/knowledge/knowledge_workspace.py` | **Nicht von gui** |
| `ui/knowledge/source_list_panel.py` | ui.knowledge (intern) |
| `ui/knowledge/source_list_item.py` | ui.knowledge (intern) |
| `ui/knowledge/source_details_panel.py` | ui.knowledge (intern) |
| `ui/knowledge/collection_panel.py` | ui.knowledge (intern) |
| `ui/knowledge/collection_dialog.py` | ui.knowledge (intern) |
| `ui/knowledge/index_status_page.py` | ui.knowledge (intern) |
| `ui/knowledge/chunk_viewer_panel.py` | ui.knowledge (intern) |
| `ui/knowledge/knowledge_navigation_panel.py` | ui.knowledge (intern) |

### Überschneidungen

- **KnowledgeWorkspace**: gui hat eigene Implementierung (KnowledgeSourceExplorerPanel, RetrievalTestPanel). ui.knowledge_workspace wird **nicht** von gui importiert.
- **SourceListItem vs SourceListItemWidget**: Zwei verschiedene Implementierungen. ui: name, type, chunk_count, collection. gui: path, name, source_type, status, active. **Echte Duplikate** mit unterschiedlicher API.

### Kanonischer Zielort

`gui/domains/operations/knowledge/panels/` (gui ist bereits kanonisch für Operations)

### Aktionen pro Datei

| ui-Datei | Aktion | Status (2026-03-16) |
|----------|--------|---------------------|
| knowledge_workspace.py | **remove_later** | ✓ gui kanonisch |
| source_list_panel.py | **remove_later** | ✓ gui hat KnowledgeSourceExplorerPanel |
| source_list_item.py | **merge** | ✓ in SourceListItemWidget |
| source_details_panel.py | **move** | ✓ migriert nach gui/panels/ |
| collection_panel.py | **move** | ✓ migriert nach gui/panels/ |
| collection_dialog.py | **move** | ✓ migriert nach gui/panels/ |
| index_status_page.py | **move** | ✓ migriert nach gui/panels/ |
| chunk_viewer_panel.py | **move** | ✓ migriert nach gui/panels/ |
| knowledge_navigation_panel.py | **move** | ✓ migriert nach gui/panels/ |

**Phase A.10:** ui/knowledge nur noch Re-Exports.

---

## Domain 3: Prompts (Prompt Studio)

### Aktive gui-Module

| Modul | Rolle |
|-------|-------|
| `gui/domains/operations/prompt_studio/prompt_studio_workspace.py` | Eigene Implementierung (PromptLibraryPanel, PromptEditorPanel) |
| `gui/domains/operations/prompt_studio/panels/` | library_panel, editor_panel, preview_panel, prompt_list_item |
| `gui/inspector/prompt_studio_inspector.py` | ✓ Nutzt gui prompt_version_panel |

### Aktive ui-Module

| Modul | Importiert von |
|-------|----------------|
| `ui/prompts/prompt_studio_workspace.py` | gui/domains/operations/operations_screen.py |
| `ui/prompts/prompt_version_panel.py` | gui/inspector/prompt_studio_inspector.py |
| `ui/prompts/prompt_navigation_panel.py` | ui.prompts (intern) |
| `ui/prompts/prompt_list_panel.py` | ui.prompts (intern) |
| `ui/prompts/prompt_list_item.py` | ui.prompts (intern) |
| `ui/prompts/prompt_editor_panel.py` | ui.prompts (intern) |
| `ui/prompts/prompt_templates_panel.py` | ui.prompts (intern) |
| `ui/prompts/prompt_test_lab.py` | ui.prompts (intern) |

### Überschneidungen

- **✓ Erledigt (2026-03-16):** gui ist kanonisch. operations_screen und prompt_studio_inspector importieren aus gui. ui/prompts nur noch Re-Exports.

### Kanonischer Zielort

`gui/domains/operations/prompt_studio/` ✓

### Aktionen pro Datei

| ui-Datei | Aktion | Status |
|----------|--------|--------|
| prompt_studio_workspace.py | **merge** | ✓ Re-Export von gui |
| prompt_version_panel.py | **move** | ✓ Re-Export von gui |
| prompt_navigation_panel.py | **move** | ✓ Re-Export von gui |
| prompt_list_panel.py | **move** | ✓ Re-Export von gui |
| prompt_list_item.py | **merge** | ✓ Re-Export von gui |
| prompt_editor_panel.py | **move** | ✓ Re-Export von gui |
| prompt_templates_panel.py | **move** | ✓ Re-Export von gui |
| prompt_test_lab.py | **move** | ✓ Re-Export von gui |

---

## Domain 4: Settings ✓ (2026-03-16)

### Aktive gui-Module

| Modul | Rolle |
|-------|-------|
| `gui/domains/settings/settings_screen.py` | SettingsScreen – nutzt gui SettingsWorkspace ✓ |
| `gui/domains/settings/settings_workspace.py` | SettingsWorkspace – kanonisch ✓ |
| `gui/domains/settings/navigation.py` | SettingsNavigation – Kategorien-Sidebar ✓ |
| `gui/domains/settings/settings_nav.py` | SettingsNav – sekundäre Navigation |
| `gui/domains/settings/workspaces/` | appearance, models, agents, system, advanced |
| `gui/domains/settings/categories/` | Application, Appearance, AIModels, Data, Privacy, Advanced, Project, Workspace ✓ |

### Aktive ui-Module

| Modul | Status |
|-------|--------|
| `ui/settings/settings_workspace.py` | ✓ Re-Export von gui |
| `ui/settings/settings_navigation.py` | ✓ Re-Export von gui (navigation.py) |
| `ui/settings/categories/*` | ✓ Re-Export von gui |

### Überschneidungen

- **✓ Erledigt:** gui ist kanonisch. settings_screen importiert aus gui. ui/settings nur noch Re-Exports.

### Kanonischer Zielort

`gui/domains/settings/` ✓

### Aktionen pro Datei

| ui-Datei | Aktion | Status |
|----------|--------|--------|
| settings_workspace.py | **move** | ✓ Re-Export von gui |
| settings_navigation.py | **move** | ✓ Re-Export von gui |
| settings/categories/* | **move** | ✓ Re-Export von gui |
| settings_dialog.py | **keep_temporarily** | Legacy main.py; nach Legacy-Abschaltung move |

---

## Domain 5: Project

### Aktive gui-Module

| Modul | Rolle |
|-------|-------|
| `gui/domains/project_hub/project_hub_screen.py` | ProjectHubScreen – lädt ui.project.ProjectHubPage |
| `gui/project_switcher/` | (Struktur vorhanden, Inhalt prüfen) |

### Aktive ui-Module

| Modul | Importiert von |
|-------|----------------|
| `ui/project/project_switcher_button.py` | gui/shell/top_bar.py |
| `ui/project/project_hub_page.py` | gui/domains/project_hub/project_hub_screen.py |
| `ui/project/project_switcher_dialog.py` | ui.project (intern) |

### Überschneidungen

- gui hat project_hub_screen, nutzt aber ui.project.ProjectHubPage als Inhalt.
- gui/shell/top_bar nutzt **ui.project.ProjectSwitcherButton** – nicht die gui-Version.
- gui hat `gui/project_switcher/project_switcher_button.py` (eigene Implementierung mit IconManager) – **nicht aktiv genutzt**. Echte Duplikate.

### Kanonischer Zielort

`gui/project_switcher/` (Button, Dialog), `gui/domains/project_hub/` (Page)

### Aktionen pro Datei

| ui-Datei | Aktion | Begründung |
|----------|--------|------------|
| project_switcher_button.py | **merge** | gui hat eigene Version (unbenutzt); top_bar nutzt ui. API vereinheitlichen, eine kanonisch. |
| project_hub_page.py | **move** | Aktiv von gui genutzt |
| project_switcher_dialog.py | **move** | |

---

## Domain 6: Agents ✓ (2026-03-16 Phase 1)

**Audit:** docs/architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md (2026-03-16)  
**Migration Report:** docs/architecture/AGENTS_UI_PHASE1_MIGRATION_REPORT.md

### Aktive gui-Module

| Modul | Rolle |
|-------|-------|
| `gui/domains/control_center/workspaces/agents_workspace.py` | AgentsWorkspace – **AgentManagerPanel** (kanonisch) |
| `gui/domains/control_center/agents_ui/` | AgentManagerPanel, AgentListPanel, AgentProfilePanel, … (7 Dateien) |
| `gui/domains/control_center/panels/agents_panels.py` | AgentRegistryPanel, AgentSummaryPanel – **isoliert** (nicht mehr genutzt) |

### Aktive ui-Module

| Modul | Status |
|-------|--------|
| `ui/agents/agent_manager_panel.py` (AgentManagerDialog) | Re-Export von agents_ui; main.py (Legacy) |
| agent_list_panel, agent_profile_panel, agent_list_item, agent_avatar_widget, agent_form_widgets, agent_performance_tab | Re-Export von agents_ui |
| agent_workspace, agent_navigation_panel, agent_library_panel | remove_later |
| agent_editor_panel, agent_runs_panel, agent_activity_panel, agent_skills_panel | manual_review |

### Kanonischer Zielort

`gui/domains/control_center/agents_ui/` ✓ (Strategy C – Hybrid)

### Aktionen pro Datei (Phase 1 abgeschlossen)

| ui-Datei | Aktion | Status |
|----------|--------|--------|
| agent_manager_panel.py | **move** | ✓ migriert; ui Re-Export |
| agent_list_panel.py | **move** | ✓ migriert; ui Re-Export |
| agent_list_item.py | **move** | ✓ migriert; ui Re-Export |
| agent_profile_panel.py | **move** | ✓ migriert; ui Re-Export |
| agent_avatar_widget.py | **move** | ✓ migriert; ui Re-Export |
| agent_form_widgets.py | **move** | ✓ migriert; ui Re-Export |
| agent_performance_tab.py | **move** | ✓ migriert; ui Re-Export |
| agent_workspace.py | **remove_later** | Nicht migriert |
| agent_navigation_panel.py | **remove_later** | Nicht migriert |
| agent_library_panel.py | **remove_later** | Nicht migriert |
| agent_editor_panel.py | **manual_review** | Nicht migriert |
| agent_runs_panel.py | **manual_review** | Nicht migriert |
| agent_activity_panel.py | **manual_review** | Nicht migriert |
| agent_skills_panel.py | **manual_review** | Nicht migriert |

---

## Domain 7: Command Center

### Aktive gui-Module

| Modul | Rolle |
|-------|-------|
| `gui/domains/dashboard/dashboard_screen.py` | DashboardScreen – SystemStatusPanel, ActiveWorkPanel, QAStatusPanel, IncidentsPanel |
| `gui/domains/dashboard/panels/` | Andere Karten |

### Aktive ui-Module

| Modul | Importiert von |
|-------|----------------|
| `ui/command_center/command_center_view.py` | app/main.py (Legacy) |
| `ui/command_center/*_view.py` | ui.command_center (intern) |

### Überschneidungen

- **CommandCenterView**: Vollständige QA/Kommandozentrale (QAOperations, Governance, Incidents, …). Nur Legacy main.py.
- **DashboardScreen**: gui hat anderes Konzept (Status-Karten). Kein 1:1-Ersatz.

### Kanonischer Zielort

`gui/domains/dashboard/command_center/` (falls ui-Views übernommen werden)

### Aktionen pro Datei

| ui-Datei | Aktion | Begründung |
|----------|--------|------------|
| command_center_view.py | **keep_temporarily** | Nur Legacy; nach Legacy-Abschaltung move |
| qa_operations_view.py | **move** | |
| qa_drilldown_view.py | **move** | |
| governance_view.py | **move** | |
| incident_operations_view.py | **move** | |
| review_operations_view.py | **move** | |
| audit_operations_view.py | **move** | |
| runtime_debug_view.py | **move** | |
| subsystem_detail_view.py | **move** | |

---

## Domain 8: Debug

### Aktive gui-Module

| Modul | Rolle |
|-------|-------|
| `gui/domains/runtime_debug/` | RuntimeDebugScreen, Workspaces (Logs, EventBus, AgentActivity, …) |
| `gui/domains/runtime_debug/panels/` | agent_activity_stream_panel, agent_status_panel, etc. |

### Aktive ui-Module

| Modul | Importiert von |
|-------|----------------|
| `ui/debug/agent_debug_panel.py` | ui/sidepanel/chat_side_panel.py |
| `ui/debug/agent_activity_view.py` | ui.debug (intern) |
| `ui/debug/event_timeline_view.py` | ui.debug (intern) |
| `ui/debug/model_usage_view.py` | ui.debug (intern) |
| `ui/debug/task_graph_view.py` | ui.debug (intern) |
| `ui/debug/tool_execution_view.py` | ui.debug (intern) |

### Überschneidungen

- **AgentDebugPanel**: Wird von ui.sidepanel (ChatSidePanel) genutzt. ChatSidePanel ist Legacy (chat_widget).
- gui hat AgentActivityWorkspace, AgentActivityStreamPanel – andere Architektur.

### Kanonischer Zielort

`gui/domains/runtime_debug/debug_views/` oder Integration in bestehende runtime_debug-Panels

### Aktionen pro Datei

| ui-Datei | Aktion | Begründung |
|----------|--------|------------|
| agent_debug_panel.py | **keep_temporarily** | Nur via Legacy sidepanel; nach Sidepanel-Migration move |
| agent_activity_view.py | **move** | |
| event_timeline_view.py | **move** | |
| model_usage_view.py | **move** | |
| task_graph_view.py | **move** | |
| tool_execution_view.py | **move** | |

---

## Querschnitts-Domains

### ui/events

| Modul | Importiert von |
|-------|----------------|
| `ui/events/project_events.py` | gui (chat, knowledge, prompt_studio, agent_tasks, session_explorer, library_panel, knowledge_source_explorer), ui (viele), core/project_context_manager |

**Aktion:** **move** nach `gui/events/` – zentral für Projekt-Kontext-Updates. Hohe Priorität.

### ui/widgets

| Modul | Importiert von |
|-------|----------------|
| `ui/widgets/empty_state_widget.py` | gui, ui |

**Aktion:** **move** – gui hat kein EmptyStateWidget; ui.widgets ist einzige Quelle. Nach gui/widgets/ verschieben.

### ui/sidepanel

| Modul | Importiert von |
|-------|----------------|
| `ui/sidepanel/chat_side_panel.py` | chat_widget (Legacy) |
| `ui/sidepanel/model_settings_panel.py` | ui.sidepanel (intern) |
| `ui/sidepanel/prompt_manager_panel.py` | ui.sidepanel (intern) |

**Aktion:** **keep_temporarily** – nur Legacy. Nach Legacy-Abschaltung **move** nach `gui/sidepanel/`.

---

## Priorisierte Reihenfolge (ohne physische Umsetzung)

1. **ui/events** → gui/events (Querschnitt, viele Abhängigkeiten)
2. **ui/widgets** → gui/widgets (EmptyStateWidget)
3. **ui/chat** (ChatNavigationPanel, ChatDetailsPanel) → gui/domains/operations/chat/panels/
4. **ui/project** (ProjectSwitcherButton, ProjectHubPage) → gui/project_switcher, gui/domains/project_hub/
5. **ui/settings** → gui/domains/settings/
6. **ui/prompts** → gui/domains/operations/prompt_studio/
7. **ui/knowledge** → ✓ Phase A.10 (2026-03-16)
8. **ui/agents** → Audit abgeschlossen (AGENTS_UI_ARCHITECTURE_AUDIT.md); Strategy C
9. **ui/command_center** → keep_temporarily (Legacy)
10. **ui/debug** → keep_temporarily / move nach Legacy-Abschaltung
11. **ui/sidepanel** → keep_temporarily (Legacy)

---

## Legende Aktionen

| Aktion | Bedeutung |
|--------|------------|
| **move** | Datei nach gui verschieben (Zielort im Plan) |
| **merge** | Mit bestehender gui-Datei zusammenführen; API vereinheitlichen |
| **keep_temporarily** | Bleibt in ui; nach Legacy-Abschaltung move/remove |
| **remove_later** | Nach Migration entfernen (nicht von gui genutzt) |
| **manual_review** | Manuelle Prüfung nötig (Duplikate, Feature-Vergleich) |
