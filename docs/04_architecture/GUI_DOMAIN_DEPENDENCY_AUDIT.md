# GUI Domain Dependency Audit

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Kontext:** Domain-Dependency-Guard-System für `app/gui/`

---

## 1. Domain-Inventar

### 1.1 Domains unter `app/gui/domains/`

| Domain | Pfad | Beschreibung |
|--------|------|--------------|
| `command_center` | `domains/command_center/` | Kommandozentrale, QA-Drilldown, Governance, Incidents, Audit |
| `control_center` | `domains/control_center/` | Agents, Models, Providers, Tools, Data Stores |
| `dashboard` | `domains/dashboard/` | Dashboard mit System-Status, QA-Status, Incidents |
| `operations` | `domains/operations/` | Meta-Screen; enthält Subdomains |
| `project_hub` | `domains/project_hub/` | Projekt-Übersicht, Quick Actions |
| `qa_governance` | `domains/qa_governance/` | Coverage, Gap Analysis, Replay Lab, Test Inventory |
| `runtime_debug` | `domains/runtime_debug/` | Agent Activity, EventBus, LLM Calls, Logs, Metrics |
| `settings` | `domains/settings/` | Einstellungen, Kategorien, Workspaces |

### 1.2 Operations-Subdomains

| Subdomain | Pfad | Beschreibung |
|-----------|------|--------------|
| `operations.chat` | `domains/operations/chat/` | Chat-Workspace, Panels |
| `operations.knowledge` | `domains/operations/knowledge/` | Knowledge-Workspace |
| `operations.prompt_studio` | `domains/operations/prompt_studio/` | Prompt-Verwaltung |
| `operations.agent_tasks` | `domains/operations/agent_tasks/` | Agent-Tasks-Workspace |
| `operations.projects` | `domains/operations/projects/` | Projekt-Operations |

### 1.3 Orchestrierung und Infrastruktur

| Bereich | Pfad | Rolle |
|---------|------|-------|
| `bootstrap` | `bootstrap.py` | Registrierung aller Screens bei App-Start |
| `shell` | `shell/` | MainWindow, TopBar, Docking |
| `workspace` | `workspace/` | ScreenRegistry, WorkspaceHost |
| `navigation` | `navigation/` | NavAreas, Sidebar, CommandPalette |
| `commands` | `commands/` | Command Registry, Palette |
| `breadcrumbs` | `breadcrumbs/` | BreadcrumbManager, Bar |
| `events` | `events/` | Projekt-Events |
| `shared` | `shared/` | Base-Workspaces, Layout-Konstanten |
| `inspector` | `inspector/` | Domain-spezifische Inspectoren (Agent, Chat, etc.) |
| `themes` | `themes/` | Theme-Infrastruktur |
| `icons` | `icons/` | IconManager, Registry |
| `project_switcher` | `project_switcher/` | Projekt-Switcher-Button |
| `monitors` | `monitors/` | Monitoring |

---

## 2. Import-Matrix (kompakt)

### 2.1 Domain → Domain (Cross-Domain)

| Quelle | Ziel | Dateien | Klassifikation |
|--------|------|---------|----------------|
| `operations.chat` | `settings` | chat_side_panel.py | DISCOURAGE |
| `operations.chat` | `runtime_debug` | chat_side_panel.py | DISCOURAGE |
| `operations.chat` | `operations.prompt_studio` | chat_side_panel.py | ALLOW |
| `settings` | `operations.prompt_studio` | model_settings_panel.py | DISCOURAGE |
| `project_hub` | `operations` | project_hub_page.py | ALLOW |

### 2.2 Domain → Infrastruktur (erwartet)

| Quelle | Ziel | Zweck |
|--------|------|-------|
| Alle Domains | `shared` | Base-Workspaces, Layout |
| Alle Domains | `navigation` | NavAreas |
| Alle Domains | `icons` | Icons |
| `control_center` | `inspector` | Agent/Model/Provider/Tool/DataStore Inspectoren |
| `operations.agent_tasks` | `inspector` | AgentTasksInspector |
| `operations.chat` | `inspector` | ChatContextInspector |

### 2.3 Orchestrierung → Domains

| Quelle | Ziel | Zweck |
|--------|------|-------|
| `bootstrap` | Alle Domain-Screens | Screen-Registrierung |
| `shell` | bootstrap, workspace, navigation, commands | MainWindow-Komposition |

---

## 3. Verdächtige Cross-Domain-Imports

### 3.1 DISCOURAGE – Sollten refaktoriert werden

| Datei | Import | Begründung |
|-------|--------|------------|
| `domains/operations/chat/panels/chat_side_panel.py` | `app.gui.domains.settings.panels.model_settings_panel` | Chat importiert Settings-Panel direkt. Besser: über Shell/Registry oder shared Panel-Factory. |
| `domains/operations/chat/panels/chat_side_panel.py` | `app.gui.domains.runtime_debug.panels.agent_debug_panel` | Chat importiert Runtime-Debug-Panel direkt. Besser: über Inspector-Host. |
| `domains/settings/panels/model_settings_panel.py` | `app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel` | Settings importiert Prompt-Studio (nur `_PROMPTS_PANEL_FIXED_WIDTH`). Besser: Konstante in shared. |

### 3.2 ALLOW – Legitim

| Import | Begründung |
|--------|------------|
| `operations.chat` → `operations.prompt_studio` | Chat-Side-Panel zeigt Prompt-Manager; beide unter operations. |
| `project_hub` → `operations.operations_context` | Hub→Workspace-Navigation; operations_context ist schlanker Kontext-Broker. |
| Domains → `inspector` | Inspector ist shared Infrastruktur; Domains registrieren ihre Inspectoren. |
| Domains → `shared`, `navigation`, `icons`, `events` | Erwartete Infrastruktur-Nutzung. |

### 3.3 INVESTIGATE – Follow-up

| Thema | Details |
|-------|---------|
| `_PROMPTS_PANEL_FIXED_WIDTH` | Wird von settings und chat_side_panel genutzt. Kandidat für `shared/layout_constants` oder `shared/panel_constants`. |
| Chat-Side-Panel-Komposition | ChatSidePanel bündelt ModelSettingsPanel, PromptManagerPanel, AgentDebugPanel. Alternative: Factory/Registry im Shell-Bereich. |

---

## 4. Vorgeschlagene Guard-Kategorien

| Kategorie | Bedeutung | Beispiel |
|-----------|-----------|----------|
| `ALLOW` | Explizit erlaubt | project_hub → operations.operations_context |
| `ALLOW_ORCHESTRATOR_ONLY` | Nur bootstrap, shell, workspace, navigation | bootstrap → alle Domains |
| `DISCOURAGE` | Erlaubt, aber dokumentiert; Ziel: Refactor | chat → settings, chat → runtime_debug |
| `FORBID` | Verboten; Test schlägt fehl | settings → chat, settings → agents |
| `INVESTIGATE` | Manuell prüfen | Neue Cross-Domain-Imports |

---

## 5. Zusammenfassung

- **8 Top-Level-Domains** + **5 Operations-Subdomains**
- **3 verdächtige Cross-Domain-Imports** (DISCOURAGE)
- **1 klare erlaubte Cross-Domain-Kopplung** (project_hub → operations)
- **Inspector** und **shared** sind bewusst von allen Domains nutzbar
- **Bootstrap** ist einziger zentraler Orchestrator für Screen-Registrierung

---

## 6. Nächste Schritte

1. Policy-Dokument (`GUI_DOMAIN_DEPENDENCY_POLICY.md`) mit konkreten Regeln
2. pytest-basierte Guards für FORBID-Regeln
3. DISCOURAGE als dokumentierte Ausnahmen (keine Test-Fehler, aber sichtbar)
4. ~~Follow-up: `_PROMPTS_PANEL_FIXED_WIDTH` nach shared verschieben~~ **Erledigt (2026-03-16):** `app/gui/shared/panel_constants.py`
