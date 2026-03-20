# App-Package Architektur-Assessment

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Analyse – keine Refactoring-Umsetzung  
**Referenz:** docs/04_architecture/GUI_REPOSITORY_ARCHITECTURE.md, docs/00_map_of_the_system.md

---

## 1. Executive Summary

Das `app/`-Package enthält **20 Python-Dateien im Root** sowie **19 Subpackages**. Es existieren mehrere architektonische Herausforderungen:

| Thema | Befund |
|-------|--------|
| **Parallele UI-Strukturen** | `gui/` (210 Dateien) und `ui/` (89 Dateien) existieren nebeneinander. `gui` ist die neue Domain-basierte Shell; `ui` enthält ältere Workspace-Implementierungen, die teils von `gui` importiert werden. |
| **Doppelte Navigation** | `core/navigation/nav_areas.py` (kanonisch) und `gui/navigation/nav_areas.py` (Re-Export). Zusätzlich: domain-spezifische Navigation in `ui/` (Settings, Chat, Knowledge, Agents, Prompts). |
| **Fehlplatzierte Root-Dateien** | 17 von 20 Root-Dateien gehören fachlich in Subpackages (core, gui, services, providers, tools, utils, debug). |
| **Legacy-Komponenten** | `main.py` ist explizit als LEGACY markiert. `chat_widget.py`, `sidebar_widget.py`, `project_chat_list_widget.py`, `message_widget.py`, `file_explorer_widget.py` werden primär von Legacy-GUI und Tests genutzt. |
| **Redundante Implementierungen** | Zwei `critic.py` (Root vs. `agents/`). Zwei `source_list_item`-Varianten (gui vs. ui). Parallele Workspace-Implementierungen (gui/domains vs. ui). |
| **Import-Risiken** | `core` importiert `gui.icons.registry`. `gui` importiert `ui` (Settings, Chat, Project). Potenzielle zirkuläre Abhängigkeiten bei Umstrukturierung. |

**Empfehlung:** Vor Refactoring eine klare Zielarchitektur festlegen. `gui/` als primäre UI-Schicht; `ui/` schrittweise in `gui/domains/` migrieren oder als Legacy-Backend für spezifische Panels belassen.

---

## 2. App-Root-Inventar

### 2.1 Dateien direkt im `app/`-Root

| Datei | Typ | Zeilen (ca.) | Zweck |
|-------|-----|--------------|-------|
| `__init__.py` | Python | 2 | Package-Marker |
| `__main__.py` | Python | 12 | Einstieg `python -m app` → run_gui_shell |
| `main.py` | Python | ~320 | **LEGACY** – alte MainWindow, ChatWidget, CommandCenter |
| `chat_widget.py` | Python | ~866 | Chat-Hauptbereich (Legacy + Tests) |
| `sidebar_widget.py` | Python | ~300 | Sidebar (Legacy) |
| `project_chat_list_widget.py` | Python | ~130 | Projekt-Chat-Liste (Legacy) |
| `message_widget.py` | Python | ~170 | Einzelne Nachricht (Legacy) |
| `file_explorer_widget.py` | Python | ~70 | Datei-Explorer (Legacy) |
| `settings.py` | Python | ~87 | AppSettings (QSettings-Wrapper) |
| `db.py` | Python | ~700 | DatabaseManager (SQLite) |
| `ollama_client.py` | Python | ~220 | Low-Level Ollama API-Client |
| `model_orchestrator.py` | Python | ~220 | Modell-Orchestrierung |
| `model_registry.py` | Python | ~300 | Modell-Registry |
| `model_roles.py` | Python | ~70 | ModelRole, Rollen-Mapping |
| `model_router.py` | Python | ~150 | Prompt-Routing |
| `escalation_manager.py` | Python | ~75 | Eskalation zwischen Modellen |
| `response_filter.py` | Python | ~10 | Response-Filter (Platzhalter) |
| `tools.py` | Python | ~226 | FileSystemTools |
| `web_search.py` | Python | ~80 | Web-Suche (DuckDuckGo) |
| `critic.py` | Python | ~45 | Critic-Modus (Platzhalter, inaktiv) |
| `resources_rc.py` | Python | auto | Qt-Ressourcen (aus resources.qrc) |
| `resources.qrc` | QRC | – | Qt-Ressourcen-Definition |

### 2.2 Nicht im Root (aber relevant)

- `run_gui_shell.py` (Projekt-Root) – Standard-Einstieg
- `archive/run_legacy_gui.py` – Legacy-GUI-Start

---

## 3. Existierende Packages

| Package | Dateien (ca.) | Zweck |
|---------|---------------|-------|
| `agents` | 22 | Agent-Profile, Registry, Service, Research, Critic |
| `commands` | 2 | Chat-Commands (Slash-Commands) |
| `context` | 2 | Active Project Context |
| `core` | 10+ | Navigation, Command Registry, Feature Registry Loader |
| `debug` | 6 | EventBus, Emitter, AgentEvent, QA Cockpit |
| `gui` | 210 | Shell, Navigation, Domains, Workspaces, Themes, Icons |
| `help` | 5 | Help Index, Help Window, Doc Generator |
| `llm` | 6 | LLM Complete, Output Pipeline, Retry Policy |
| `metrics` | 5 | Metrics Collector, Store, Service |
| `models` | – | (Leer oder nur __init__) |
| `prompts` | 5 | Prompt Storage, Repository, Service |
| `providers` | 4 | Local/Cloud Ollama Provider |
| `qa` | 5 | QA Operations, Dashboard Adapter |
| `rag` | – | RAG Service, Retriever |
| `resources` | – | Styles, QSS |
| `runtime` | 2 | GUI Log Buffer |
| `services` | 11 | Chat, Knowledge, Agent, Provider, Project, Topic |
| `ui` | 89 | Ältere UI: Command Center, Settings, Chat, Agents, Knowledge, Prompts |
| `utils` | 4 | Paths, Datetime, Env Loader |

---

## 4. Doppelte / Parallele Strukturen

### 4.1 GUI vs. UI

| Aspekt | `gui/` | `ui/` |
|--------|--------|-------|
| **Struktur** | Domain-basiert (`domains/operations/`, `domains/settings/`, …) | Feature-basiert (`chat/`, `settings/`, `agents/`, …) |
| **Rolle** | Shell, Navigation, Workspace-Host, Screens | Workspace-Views, Panels, Navigation-Panels |
| **Abhängigkeit** | Importiert `ui` für Settings, Chat, Project | Importiert `gui` (Icons, ggf. andere) |

**Konkrete Überlappungen:**

| Konzept | gui | ui |
|---------|-----|-----|
| **Settings** | `gui/domains/settings/settings_screen.py` → nutzt `ui.settings.settings_workspace.SettingsWorkspace` | `ui/settings/settings_workspace.py`, `settings_navigation.py` |
| **Chat** | `gui/domains/operations/chat/chat_workspace.py` nutzt `ui.chat.ChatNavigationPanel`, `ChatDetailsPanel` | `ui/chat/` – ChatNavigationPanel, ChatDetailsPanel, ConversationView, … |
| **Knowledge** | `gui/domains/operations/knowledge/` – eigene Panels, `SourceListItemWidget` | `ui/knowledge/` – `SourceListPanel`, `SourceListItem` |
| **Prompt Studio** | `gui/domains/operations/prompt_studio/` | `ui/prompts/` – prompt_studio_workspace, prompt_navigation_panel |
| **Agents** | `gui/domains/control_center/panels/agents_panels.py` | `ui/agents/` – agent_workspace, agent_navigation_panel, agent_editor_panel |
| **Project** | `gui/domains/project_hub/` | `ui/project/` – project_switcher_button, project_hub_page |

**Fazit:** `gui` ist die neue Shell; `ui` liefert wiederverwendbare Panels/Workspaces, die von `gui` eingebunden werden. Es gibt keine klare Trennung „Legacy vs. aktiv“ – beide werden aktiv genutzt.

### 4.2 Navigation – mehrfach vorhanden

| Ort | Typ | Funktion |
|-----|-----|----------|
| `core/navigation/nav_areas.py` | Kanonisch | `NavArea` – Bereichs-IDs |
| `gui/navigation/nav_areas.py` | Re-Export | `from app.core.navigation.nav_areas import NavArea` |
| `core/navigation/navigation_registry.py` | Registry | `get_all_entries`, `get_sidebar_sections` |
| `gui/navigation/sidebar_config.py` | Nutzt Registry | Delegiert an `core.navigation.navigation_registry` |
| `ui/settings/settings_navigation.py` | Domain-spezifisch | Links-Navigation für Settings-Kategorien |
| `ui/chat/chat_navigation_panel.py` | Domain-spezifisch | Links-Navigation für Chats |
| `ui/knowledge/knowledge_navigation_panel.py` | Domain-spezifisch | Links-Navigation für Knowledge |
| `ui/agents/agent_navigation_panel.py` | Domain-spezifisch | Links-Navigation für Agents |
| `ui/prompts/prompt_navigation_panel.py` | Domain-spezifisch | Links-Navigation für Prompt Studio |

**Bewertung:** `core` + `gui` für Haupt-Navigation sind konsistent. Die `ui/*_navigation_panel` sind **domain-spezifische** linke Panels (Workspace-intern), nicht die globale Sidebar – daher keine echte Redundanz, aber Namenskonflikt „Navigation“.

### 4.3 Source-List-Item – zwei Implementierungen

| Ort | Klasse | Verwendung |
|-----|--------|------------|
| `gui/domains/operations/knowledge/panels/source_list_item.py` | `SourceListItemWidget` | `knowledge_source_explorer_panel.py` |
| `ui/knowledge/source_list_item.py` | `SourceListItem` | `ui/knowledge/source_list_panel.py` |

Unterschiedliche APIs (path/name/type/status vs. source_id/name/type/chunk_count/collection). Keine gemeinsame Basis.

### 4.4 Critic – zwei Implementierungen

| Ort | Inhalt |
|-----|--------|
| `app/critic.py` | Platzhalter, `review_response()` – aktuell inaktiv |
| `app/agents/critic.py` | `CriticAgent` – aktiv, überprüft Research-Antworten |

Verschiedene Konzepte: Root = generischer Review-Modus; Agents = spezialisierter Critic. Namenskonflikt.

---

## 5. Legacy- / Remove-Kandidaten

### 5.1 Explizit Legacy

| Datei | Status | Nutzung |
|-------|--------|---------|
| `main.py` | LEGACY (Docstring) | `run_legacy_gui.py`, Tests (MainWindow, main) |
| `archive/run_legacy_gui.py` | Legacy | Startet alte GUI |

### 5.2 Legacy-Widgets (von main.py genutzt)

| Datei | Nutzung |
|-------|---------|
| `chat_widget.py` | main.py, viele Tests |
| `sidebar_widget.py` | main.py |
| `project_chat_list_widget.py` | main.py |
| `message_widget.py` | Vermutlich von chat_widget |
| `file_explorer_widget.py` | Vermutlich von chat/sidebar |

### 5.3 Platzhalter / Inaktiv

| Datei | Befund |
|-------|--------|
| `app/critic.py` | Platzhalter, `enabled=False` |
| `response_filter.py` | Kleiner Filter, evtl. ungenutzt |

### 5.4 Backup / Experiment

- Keine Dateien mit `.bak`, `_old`, `_backup`, `experiment` im Namen gefunden.

---

## 6. Move-Matrix

| Root-Datei | Empfohlene Kategorie | Begründung |
|------------|---------------------|------------|
| `__init__.py` | **keep_in_root** | Package-Marker |
| `__main__.py` | **keep_in_root** | Einstiegspunkt |
| `main.py` | **review** | Legacy – evtl. nach `archive/` oder `gui/legacy/` |
| `chat_widget.py` | **move_to_gui** | GUI-Widget; Legacy-Chat, aber von Tests genutzt |
| `sidebar_widget.py` | **move_to_gui** | GUI-Widget, Legacy |
| `project_chat_list_widget.py` | **move_to_gui** | GUI-Widget, Legacy |
| `message_widget.py` | **move_to_gui** | GUI-Widget, Legacy |
| `file_explorer_widget.py` | **move_to_gui** | GUI-Widget, Legacy |
| `settings.py` | **move_to_core** | App-weite Konfiguration; evtl. `core/config` |
| `db.py` | **move_to_services** | `services/database/` oder `core/db/` |
| `ollama_client.py` | **move_to_providers** | Low-Level Provider-Client |
| `model_orchestrator.py` | **move_to_core** | Kern-Orchestrierung |
| `model_registry.py` | **move_to_core** | Kern-Registry |
| `model_roles.py` | **move_to_core** | Kern-Konstanten |
| `model_router.py` | **move_to_core** | Kern-Routing |
| `escalation_manager.py` | **move_to_core** | Modell-Eskalation |
| `response_filter.py` | **move_to_llm** oder **merge** | LLM-Output-Pipeline |
| `tools.py` | **move_to_tools** | `app/tools/` Package (FileSystemTools) |
| `web_search.py` | **move_to_tools** | Tool für Web-Suche |
| `critic.py` | **merge** | In `agents/critic.py` integrieren oder umbenennen |
| `resources_rc.py` | **keep_in_root** | Qt-generiert; oder `resources/` |
| `resources.qrc` | **keep_in_root** | Qt-Ressource |

---

## 7. Import-Risiken

### 7.1 Cross-Layer-Imports

| Von | Nach | Risiko |
|-----|------|--------|
| ~~`core/navigation/navigation_registry.py`~~ | ~~`app.gui.icons.registry`~~ | **Behoben:** icon_ids.py (String-IDs) |
| ~~`core/feature_registry_loader.py`~~ | ~~`app.gui`~~ | **Behoben:** palette_loader nach gui/commands verschoben |
| ~~`gui/domains/settings/settings_screen.py`~~ | ~~`app.ui.settings.settings_workspace`~~ | **Behoben:** nutzt gui |
| `gui/domains/operations/chat/chat_workspace.py` | `app.ui.chat` | gui → ui |
| `gui/shell/top_bar.py` | `app.ui.project.project_switcher_button` | gui → ui |

### 7.2 Potenzielle zirkuläre Abhängigkeiten

- `app.chat_widget` → `app.ui.chat`, `app.ui.sidepanel`, `app.tools`, `app.commands`, `app.model_*`, `app.agents`, `app.llm`, `app.rag`, `app.debug`  
  → ChatWidget ist stark vernetzt; Move würde viele Imports erfordern.

- `app.main` → `app.chat_widget`, `app.sidebar_widget`, `app.project_chat_list_widget`, `app.ui.command_center`, `app.ollama_client`, `app.settings`, `app.db`, …  
  → Main ist zentraler Legacy-Hub.

### 7.3 Empfehlungen

1. **Core von GUI entkoppeln:** `IconRegistry` aus `core.navigation` entfernen – Icons als String-IDs oder Registry-Injection.
2. **ui-Konsolidierung:** Entweder `ui` vollständig in `gui/domains/` migrieren oder als klar dokumentiertes „Legacy-Panel-Repository“ belassen.
3. **Move schrittweise:** Erst wenig vernetzte Module (z.B. `utils`, `response_filter`) verschieben, dann komplexere.

---

## 8. Empfohlene Zielstruktur

```
app/
├── __init__.py
├── __main__.py
├── resources.qrc
├── resources_rc.py
│
├── core/                    # Kernlogik, keine GUI
│   ├── config/              # settings.py → app.core.config
│   ├── db/                  # db.py → app.core.db
│   ├── models/              # model_*, escalation_manager
│   ├── navigation/
│   └── command_registry/
│
├── gui/                     # Primäre UI-Schicht
│   ├── shell/
│   ├── navigation/
│   ├── domains/
│   ├── legacy/               # Optional: chat_widget, sidebar_widget, …
│   └── ...
│
├── ui/                      # Phase 1: Belassen, Phase 2: Migration nach gui
│   └── ...
│
├── providers/               # ollama_client, Local/Cloud
├── services/
├── agents/
├── llm/
├── rag/
├── prompts/
├── tools/                   # tools.py, web_search.py
├── utils/
├── debug/
├── metrics/
└── ...
```

---

## 9. Refactoring-Risiken

| Risiko | Mitigation |
|--------|------------|
| **Tests brechen** | Viele Tests importieren `app.chat_widget`, `app.main`, `app.db`, `app.settings`. Nach Move: Import-Pfade in Tests aktualisieren. |
| **Legacy-GUI nicht mehr startbar** | `run_legacy_gui.py` und `main.py` müssen weiterhin funktionieren; Move von Legacy-Widgets erst nach Abschaltung der Legacy-GUI. |
| **Zirkuläre Imports** | Core → GUI trennen; Move in Reihenfolge: zuerst Blatt-Module, dann abhängige. |
| **ui-Abhängigkeiten** | gui importiert ui; bei ui-Move müssen alle gui-Imports angepasst werden. |
| **PyInstaller / Packaging** | `resources_rc.qrc` und Pfade in `utils/paths.py` prüfen. |

---

## Anhang: Übersicht Root-Dateien

| Datei | Zeilen | Move-Kategorie |
|-------|--------|----------------|
| `__init__.py` | 2 | keep_in_root |
| `__main__.py` | 12 | keep_in_root |
| `main.py` | ~320 | review |
| `chat_widget.py` | ~866 | move_to_gui |
| `sidebar_widget.py` | ~300 | move_to_gui |
| `project_chat_list_widget.py` | ~130 | move_to_gui |
| `message_widget.py` | ~170 | move_to_gui |
| `file_explorer_widget.py` | ~70 | move_to_gui |
| `settings.py` | ~87 | move_to_core |
| `db.py` | ~700 | move_to_services |
| `ollama_client.py` | ~220 | move_to_providers |
| `model_orchestrator.py` | ~220 | move_to_core |
| `model_registry.py` | ~300 | move_to_core |
| `model_roles.py` | ~70 | move_to_core |
| `model_router.py` | ~150 | move_to_core |
| `escalation_manager.py` | ~75 | move_to_core |
| `response_filter.py` | ~10 | merge / move_to_llm |
| `tools.py` | ~226 | move_to_tools |
| `web_search.py` | ~80 | move_to_tools |
| `critic.py` | ~45 | merge |
| `resources_rc.py` | auto | keep_in_root |
| `resources.qrc` | – | keep_in_root |
