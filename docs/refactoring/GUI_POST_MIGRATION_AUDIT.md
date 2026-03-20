# GUI Post-Migration Audit

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Kontext:** Post-Migration Hardening nach vollständiger Eliminierung von `app/ui/`

---

## 1. Ausgangslage

- `app/ui/` vollständig entfernt
- `app/gui/` ist die einzige kanonische UI-Schicht
- Architekturguard gegen `gui -> ui` ist grün
- Legacy-Subsysteme (agents, chat, sidepanel, debug, settings, project, prompts, knowledge, command_center) migriert

---

## 2. GUI-Strukturübersicht

```
app/gui/
├── bootstrap.py              # Screen-Registry, register_all_screens()
├── qsettings_backend.py      # Settings-Backend für Shell
├── commands/
│   └── bootstrap.py          # Command-Registry (nav, system)
├── shell/
│   ├── main_window.py
│   ├── top_bar.py
│   └── layout_constants.py
├── workspace/
│   ├── workspace_host.py
│   └── screen_registry.py
├── navigation/
│   ├── nav_areas.py
│   ├── sidebar.py
│   ├── command_palette.py
│   ├── sidebar_config.py
│   ├── workspace_graph.py
│   └── workspace_graph_resolver.py
├── shared/                   # BaseScreen, BasePanel, Layout-Helfer
├── domains/
│   ├── dashboard/            # DashboardScreen (Kommandozentrale)
│   ├── project_hub/
│   ├── operations/           # OperationsScreen + Workspaces
│   │   ├── chat/
│   │   ├── knowledge/
│   │   ├── prompt_studio/
│   │   ├── projects/
│   │   └── agent_tasks/
│   ├── control_center/
│   ├── qa_governance/
│   ├── runtime_debug/
│   ├── settings/
│   └── command_center/       # CommandCenterView (Legacy MainWindow)
├── legacy/                   # ChatWidget, SidebarWidget, etc.
├── project_switcher/
├── breadcrumbs/
├── inspector/
├── icons/
├── themes/
├── widgets/
└── events/
```

---

## 3. Audit-Befunde (klassifiziert)

### 3.1 REMOVE_DEAD

| Fund | Ort | Begründung |
|------|-----|------------|
| **ChatSessionExplorerPanel** | `domains/operations/chat/panels/session_explorer_panel.py` | Nie importiert außer in `__init__.py`. ChatWorkspace nutzt `ChatNavigationPanel`. Alternativ-Implementierung, ungenutzt. |
| **SettingsNav** | `domains/settings/settings_nav.py` + Re-Export in `__init__.py` | Nur in `__init__.py` exportiert. `SettingsWorkspace` nutzt `SettingsNavigation` (aus `navigation.py`). SettingsNav = sekundäre Bereichsleiste, nie eingebaut. |

### 3.2 CONSOLIDATE (empfohlen, nicht automatisch)

| Fund | Ort | Begründung |
|------|-----|------------|
| **Doppelte Chat-Frontends** | `legacy/chat_widget.py` vs `domains/operations/chat/chat_workspace.py` | Zwei parallele Chat-UIs: Legacy (ConversationView, ChatComposerWidget) vs Domain (ChatConversationPanel, ChatInputPanel). Beide aktiv – Legacy für `run_legacy_gui`, Domain für Shell. Kein Feature-Change, nur strukturelle Klarheit. |
| **Re-Export-Kette chat/panels** | `domains/operations/chat/panels/__init__.py` | Exportiert 20+ Symbole. Viele werden direkt aus Untermodulen importiert. Re-Export sinnvoll für einheitlichen Zugriff; keine unnötige Kette. |

### 3.3 MOVE (optional, risikoarm)

| Fund | Ort | Begründung |
|------|-----|------------|
| **qsettings_backend.py** | `app/gui/` Root | Backend für Settings; könnte nach `app/core/` oder `app/gui/settings_backend.py`. Aktuell von `run_gui_shell.py` importiert. Geringe Priorität. |

### 3.4 KEEP

| Bereich | Begründung |
|---------|------------|
| **bootstrap.py** vs **commands/bootstrap.py** | Unterschiedliche Verantwortung: Screens vs Commands. Keine Redundanz. |
| **DashboardScreen** vs **CommandCenterView** | Unterschiedliche Kontexte: Shell-Kommandozentrale vs Legacy-Stacked-Widget. Keine Duplikation. |
| **settings/navigation.py** vs **settings/settings_nav.py** | `SettingsNavigation` = Kategorien-Sidebar (genutzt). `SettingsNav` = ungenutzt (REMOVE_DEAD). |
| **shared/** | Zentrale Basisklassen; saubere Nutzung. |
| **workspace/** | Klare Registry + Host. |
| **navigation/** | NavAreas, Sidebar, CommandPalette – konsistent. |
| **domains/**-Struktur | Klar geschnitten: dashboard, project_hub, operations, control_center, qa_governance, runtime_debug, settings, command_center. |

### 3.5 INVESTIGATE_LATER

| Fund | Ort | Begründung |
|------|-----|------------|
| **Legacy-Widgets** | `legacy/` | ChatWidget, SidebarWidget, etc. werden von `main.py` (Legacy) und Tests genutzt. Deprecation-Pfad prüfen, wenn Shell Standard wird. |
| **IndexOverviewPanel / RetrievalStatusPanel** | `knowledge/panels/__init__.py` | Aliase für `KnowledgeOverviewPanel` / `RetrievalTestPanel`. Prüfen ob Aliase noch benötigt werden. |

---

## 4. Import-Analyse

### 4.1 Relative Imports innerhalb `app/gui`

| Datei | Import | Bewertung |
|-------|--------|-----------|
| `legacy/sidebar_widget.py` | `from .file_explorer_widget import FileExplorerWidget` | KEEP – Sibling-Import, akzeptabel. |

### 4.2 Querlaufende Domain-Imports

- `chat/panels/chat_side_panel.py` → settings, prompt_studio, runtime_debug (Panel-Zusammenführung)
- `settings/panels/model_settings_panel.py` → prompt_studio (`_PROMPTS_PANEL_FIXED_WIDTH`)
- `project_hub/project_hub_page.py` → operations_context

Bewertung: Domainübergreifende Imports sind fachlich begründet (Side-Panel hostet mehrere Bereiche). Kein God-Modul.

### 4.3 Re-Export-Ketten

- `domains/command_center/__init__.py` – Re-Export aller Views. Sinnvoll für `from app.gui.domains.command_center import CommandCenterView`.
- `domains/settings/__init__.py` – Re-Export SettingsScreen, SettingsNav, SettingsDialog. SettingsNav entfernen (REMOVE_DEAD).
- `domains/operations/chat/panels/__init__.py` – Umfangreich, aber alle Symbole werden genutzt (außer ChatSessionExplorerPanel).

---

## 5. Bootstrap / Navigation / Registry

| Komponente | Status |
|------------|--------|
| **bootstrap.register_all_screens()** | Nutzt ScreenRegistry, NavArea, alle Domain-Screens. Konsistent. |
| **commands/bootstrap.register_commands()** | NavArea-Callbacks, System-Commands. Keine Redundanz. |
| **ScreenRegistry** | Zentrale Registrierung. |
| **WorkspaceHost** | Zeigt Bereiche, resolved Workspaces. |
| **NavigationSidebar** | NavArea-basiert. |

---

## 6. Zusammenfassung

| Klassifikation | Anzahl |
|----------------|--------|
| REMOVE_DEAD | 2 (ChatSessionExplorerPanel + Modul, SettingsNav + Re-Export) |
| CONSOLIDATE | 1 (Chat-Dualität – Follow-up) |
| MOVE | 1 (qsettings_backend – optional) |
| KEEP | Alle übrigen Bereiche |
| INVESTIGATE_LATER | 2 (Legacy, Knowledge-Aliase) |

---

## 7. Empfohlene Sofortmaßnahmen (Phase 2)

1. **ChatSessionExplorerPanel** entfernen: Modul + Re-Export aus `chat/panels/__init__.py`
2. **SettingsNav** entfernen: Modul + Re-Export aus `settings/__init__.py`
3. Keine weiteren Änderungen in Phase 2 (kein funktionaler Umbau)
