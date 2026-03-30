# Architektur-Guard-Regeln

**Projekt:** Linux Desktop Chat  
**Tests:** `tests/architecture/test_app_package_guards.py`  
**Config:** `tests/architecture/arch_guard_config.py`

---

## Übersicht

Die Guard-Tests prüfen die Package-Struktur und Import-Richtungen. Bei Verletzung schlagen die Tests fehl – keine stillen Drifts.

---

## Regeln (kurz)

### 1. app.core importiert keine app.gui

- **Test:** `test_core_no_gui_imports`
- **Regel:** `app.core` darf keine Module aus `app.gui` importieren.
- **Ziel:** Core ist ohne Qt/GUI testbar.

### 2. app.utils importiert keine Feature- oder UI-Module

- **Test:** `test_utils_no_feature_or_ui_imports`
- **Regel:** `app.utils` darf nur stdlib nutzen. Kein core, gui, agents, rag, prompts, providers, services, debug, metrics, tools, ui.
- **Ziel:** Utils bleibt reine Infrastruktur (Paths, Datetime, Env).

### 3. app.ui nur von erlaubten Übergangsmodulen importiert

- **Test:** `test_ui_only_imported_by_allowed_transition_modules`
- **Regel:** `app.ui` darf nur importiert werden von: `gui/`, `main.py`, `chat_widget.py`, `core/context/project_context_manager.py`.
- **Ziel:** ui → gui Migration; keine neuen ui-Abhängigkeiten.
- **Config:** `ALLOWED_UI_IMPORTER_PATTERNS`

### 4. Neue Root-Dateien werden erkannt

- **Test:** `test_app_root_only_allowed_files`
- **Regel:** Jede Datei im `app/` Root muss in `ALLOWED_APP_ROOT_FILES` oder `TEMPORARILY_ALLOWED_ROOT_FILES` stehen.
- **Ziel:** Keine neuen Root-Dateien ohne Architektur-Review.

### 5. Navigation klar getrennt (global vs. domain)

- **Tests:** `test_global_navigation_only_in_gui_navigation`, `test_domain_nav_panels_not_in_global_navigation`
- **Regeln:**
  - **Globale Navigation** (NavigationSidebar, CommandPalette) nur in `app/gui/navigation/`.
  - **Domain-Nav-Panels** (ChatNavigationPanel, SettingsNavigation, …) in `gui/domains/*/` oder `ui/`, nicht in `gui/navigation/`.
- **Ziel:** Klare Trennung: Sidebar/Palette zentral; Domain-Nav in Domains.

### 6. gui/events und gui/widgets als kanonisch

- **Kanonisch:** `app.gui.events` (Projekt-Events) und `app.gui.widgets` (EmptyStateWidget).
- **app.ui.events** und **app.ui.widgets** wurden entfernt (2026-03-16); keine Konsumenten.

### 7. Legacy-Widgets in gui/legacy

- **app.gui.legacy** enthält ChatWidget, SidebarWidget, ProjectChatListWidget, MessageWidget, FileExplorerWidget.
- Diese wurden aus dem app-Root verschoben (2026-03-16). Keine Root-Re-Exports für Legacy-Widgets.

### 8. gui/domains/operations/chat/panels als kanonisch (2026-03-16)

- **Kanonisch:** Chat-Panels unter `app.gui.domains.operations.chat.panels/`:
  - ChatNavigationPanel, ChatDetailsPanel, ChatMessageWidget
  - topic_editor_dialog, topic_actions, chat_item_context_menu
- **app.ui.chat** enthält nur noch Re-Exports für Legacy-Konsumenten und keep_temporarily-Dateien (conversation_view, chat_composer_widget, chat_header_widget, chat_list_item, chat_topic_section).

### 9. gui/domains/settings als kanonisch (2026-03-16)

- **Kanonisch:** Settings unter `app.gui.domains.settings/`:
  - SettingsWorkspace, SettingsNavigation, SettingsHelpPanel
  - categories: Application, Appearance, AIModels, Data, Privacy, Advanced, Project, Workspace
  - workspaces: appearance, models, agents, system, advanced
- **app.ui.settings** enthält nur Re-Exports für Übergang. Keine neuen Imports von app.ui.settings.

### 10. gui/domains/operations/prompt_studio als kanonisch (2026-03-16)

- **Kanonisch:** Prompt Studio unter `app.gui.domains.operations.prompt_studio/`:
  - PromptStudioWorkspace, PromptNavigationPanel, PromptListPanel, PromptListItem
  - PromptEditorPanel, PromptTemplatesPanel, PromptTestLab, PromptVersionPanel
  - library_panel, editor_panel, preview_panel
- **app.ui.prompts** enthält nur Re-Exports für Übergang. Keine neuen Imports von app.ui.prompts.

### 11. gui/domains/operations/knowledge als kanonisch (2026-03-16)

- **Kanonisch:** Knowledge unter `app.gui.domains.operations.knowledge/`:
  - KnowledgeWorkspace, KnowledgeSourceExplorerPanel, KnowledgeOverviewPanel, RetrievalTestPanel
  - SourceListItemWidget (SourceListItem), SourceDetailsPanel, CollectionPanel, IndexStatusPage
  - ChunkViewerPanel, KnowledgeNavigationPanel, collection_dialog
- **app.ui.knowledge** enthält nur Re-Exports von gui. Keine neuen Imports von app.ui.knowledge.

### 12. gui/domains/control_center/agents_ui als kanonisch (2026-03-16)

- **Kanonisch:** Agent Manager flow unter `app.gui.domains.control_center.agents_ui/`:
  - AgentManagerPanel, AgentManagerDialog, AgentListPanel, AgentListItem
  - AgentProfilePanel, AgentAvatarWidget, AgentFormWidgets, AgentPerformanceTab
- **app.ui.agents** enthält Re-Exports für die 7 migrierten Komponenten; 7 Dateien (remove_later / manual_review) bleiben in ui.
- **AgentsWorkspace** (Control Center) hostet AgentManagerPanel aus agents_ui.

### 13. gui darf nicht ui importieren (2026-03-16 Phase 3)

- **Test:** `test_gui_layer_does_not_import_ui_layer` in `tests/architecture/test_gui_does_not_import_ui.py`
- **Regel:** Kein Modul unter `app/gui/` darf `app.ui.*` importieren.
- **Bekannte Ausnahmen (Legacy):** chat_widget.py, chat_navigation_panel.py (Chat-Migration ausstehend).

### 14. GUI Domain Dependency Guards (2026-03-16)

- **Test:** `test_no_forbidden_gui_domain_imports` in `tests/architecture/test_gui_domain_dependency_guards.py`
- **Regel:** Keine verbotenen Cross-Domain-Imports zwischen `app/gui/domains/`.
- **Policy:** `docs/architecture/GUI_DOMAIN_DEPENDENCY_POLICY.md`
- **Config:** `FORBIDDEN_GUI_DOMAIN_PAIRS`, `KNOWN_GUI_DOMAIN_EXCEPTIONS` in `arch_guard_config.py`

### 15. GUI Governance Guards (2026-03-16)

- **Tests:** `tests/architecture/test_gui_governance_guards.py`
- **Regeln:** Screen Registry (keine doppelten area_ids), Navigation (gültige Targets), Commands (eindeutige IDs), Bootstrap (konsistente Registrierung)
- **Policy:** `docs/architecture/GUI_GOVERNANCE_POLICY.md`
- **Config:** `GUI_SCREEN_WORKSPACE_MAP` in `arch_guard_config.py`

### 16. Feature Governance Guards (2026-03-16)

- **Tests:** `tests/architecture/test_feature_governance_guards.py`
- **Regeln:** Feature-IDs eindeutig, Erreichbarkeit (Navigation, Screen-Map), Registry-Integrität, Generator-Konsistenz
- **Policy:** `docs/architecture/FEATURE_GOVERNANCE_POLICY.md`
- **Source of Truth:** `FEATURES` in `tools/generate_feature_registry.py`

---

## Erweiterte Regeln (bereits vorhanden)

| Test | Regel |
|------|-------|
| `test_no_forbidden_import_directions` | Keine verbotenen Import-Richtungen (FORBIDDEN_IMPORT_RULES) |
| `test_central_navigation_exists` | Zentrale Navigation unter `gui/navigation/` |
| `test_no_duplicate_global_navigation_outside_gui` | NavigationSidebar, CommandPalette nur in gui/navigation/ |
| `test_feature_packages_no_gui_imports` | Feature-Packages importieren kein gui |
| `test_feature_packages_no_root_legacy_imports` | Feature-Packages importieren kein Root-Legacy |
| `test_forbidden_parallel_packages_have_import_rules` | ui/ hat Import-Regeln |

---

## core/models → providers

**Stand 2026-03-30:** `app.core.models` importiert `app.providers` nicht.

- **Regel:** Provider-Verdrahtung liegt außerhalb von `core`; der Orchestrator nutzt nur einen kleinen provider-neutralen Contract.
- **Config:** Kein `KNOWN_IMPORT_EXCEPTIONS`-Eintrag mehr für `core/models/orchestrator.py` → `providers`.

## Konfiguration anpassen

Änderungen nur nach Architektur-Review. Relevante Konstanten in `arch_guard_config.py`:

- `KNOWN_IMPORT_EXCEPTIONS` – temporäre Ausnahmen (mit Behebungsdatum)
- `ALLOWED_UI_IMPORTER_PATTERNS` – wer darf ui importieren
- `ALLOWED_IN_GUI_NAVIGATION` – erlaubte Klassen in gui/navigation/ (Daten, Helper)
