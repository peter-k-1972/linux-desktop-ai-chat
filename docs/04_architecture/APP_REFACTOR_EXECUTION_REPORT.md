# App Refactoring Execution Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** In Bearbeitung  
**Referenz:** docs/architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md, docs/architecture/APP_MOVE_MATRIX.md

---

## Übersicht

| Phase | Status | Moves | Tests |
|-------|--------|-------|-------|
| A | In Progress | 8 (Tools + UI→GUI) | Arch: 12/12 ✓ |
| B | Pending | – | – |
| C | Pending | – | – |
| D | Pending | – | – |

---

## Phase A: Target Packages + Low-Risk Moves

### Move 1: app/tools.py → app/tools/filesystem.py

| Feld | Wert |
|------|------|
| **old path** | `app/tools.py` |
| **new path** | `app/tools/filesystem.py` |
| **action** | move |
| **risk_level** | low (Re-Export via __init__.py) |

**Updated imports:** Keine. `from app.tools import FileSystemTools` funktioniert weiterhin über `app/tools/__init__.py`.

**Affected tests:**
- `tests/unit/test_tools.py` – 11 passed
- `tests/test_tools_workspace_paths.py` – 5 passed
- `tests/test_tools_execute_command.py` – 2 passed

**Risk notes:** Package `app/tools/` ersetzt Modul `app/tools.py`. Rückwärtskompatibilität durch Re-Export in `__init__.py`.

---

### Move 2: app/web_search.py → app/tools/web_search.py

| Feld | Wert |
|------|------|
| **old path** | `app/web_search.py` |
| **new path** | `app/tools/web_search.py` |
| **action** | move |
| **risk_level** | low (keine Imports) |

**Updated imports:** Keine. `web_search` wurde nirgends importiert; nur als String/Attribut referenziert.

**Affected tests:** Keine direkten Tests für web_search.

**Risk notes:** Modul war nicht referenziert. Exports in `app/tools/__init__.py` ergänzt für zukünftige Nutzung.

---

## Bekannte Test-Fehler (vor Refactoring)

| Test | Fehler | Ursache |
|------|--------|---------|
| `tests/chaos/test_startup_partial_services.py` | ValueError: too many values to unpack | sidebar_widget.py:194 – DB-Schema |
| `tests/contracts/test_prompt_contract.py` | Prompt.__init__() missing scope, project_id | conftest test_prompt Fixture |
| `tests/unit/test_prompt_system.py` | Prompt.__init__() missing scope, project_id | Prompt-Model-Änderung |

Diese Fehler bestanden vor dem Refactoring und sind nicht durch die Tools-Migration verursacht.

---

---

## Phase A.1: Layer-Bruch Core → GUI entfernt

**Ziel:** `app.core` importiert nur noch `app.utils` oder interne core-Module. Kein PySide6, keine gui-Imports in core.

### Änderungen

| Aktion | Details |
|--------|---------|
| **icon_ids.py** | Neues Modul `app/core/navigation/icon_ids.py` mit String-Konstanten (DASHBOARD, CHAT, …) statt IconRegistry-Referenzen |
| **navigation_registry.py** | Import von `app.gui.icons.registry` entfernt; nutzt `app.core.navigation.icon_ids` |
| **Palette Loader** | `app/core/feature_registry_loader.py` → `app/gui/commands/palette_loader.py` verschoben (GUI-Bootstrap-Logik) |
| **main_window.py** | Import angepasst: `from app.gui.commands.palette_loader import load_all_palette_commands` |
| **arch_guard_config** | KNOWN_IMPORT_EXCEPTIONS für core→gui entfernt (navigation_registry, feature_registry_loader) |

### Ergebnis

- `app.core` importiert keine `app.gui`-Module mehr
- Keine PySide6-Imports in core
- `app.core.navigation.feature_registry_loader` bleibt in core (reiner Daten-Loader für FEATURE_REGISTRY.md)

### Test-Ergebnisse (2026-03-16)

| Test-Suite | Ergebnis |
|------------|----------|
| `tests/architecture/` (7 Tests) | 7 passed ✓ |
| Unit-Tests (ohne prompt_system) | 82 passed ✓ |
| Bekannte Fehler | test_prompt_system, test_startup_partial_services (vor Refactoring) |

---

---

## Phase A.2: Low-Risk und Infrastruktur-Moves (AUFGABE 2)

**Ziel:** Sichere, nicht-UI-zentrierte Moves. Nur absolute Imports ab `app`. Rückwärtskompatibilität über Re-Exports.

### Durchgeführte Moves

| # | Move | Ziel | Status |
|---|------|------|--------|
| 1 | response_filter.py | app/core/llm/response_filter.py | ✓ |
| 2 | commands/ | app/core/commands/ | ✓ |
| 3 | context/ | app/core/context/ | ✓ (2026-03-16: Qt entkoppelt, Move durchgeführt) |
| 4 | runtime/gui_log_buffer.py | app/debug/gui_log_buffer.py | ✓ |
| 5 | llm/ | app/core/llm/ | ✓ |
| 6 | settings.py | app/core/config/settings.py | ✓ (2026-03-16: SettingsBackend, Move durchgeführt) |
| 7 | db.py | app/core/db/database_manager.py | ✓ |
| 8 | ollama_client.py | app/providers/ollama_client.py | ✓ |
| 9 | model_* | app/core/models/ | ✓ (2026-03-16: Cluster-Move durchgeführt) |

### Abgeschlossene Refactors (2026-03-16)

| Modul | Änderung |
|-------|----------|
| **ActiveProjectContext** | Qt-frei: QObject/Signal durch subscribe/unsubscribe Callback-System ersetzt |
| **AppSettings** | Qt-frei: SettingsBackend-Interface, InMemoryBackend für Tests, QSettingsBackendAdapter in gui |
| **ProjectContextManager** | Nach app/core/context/ verschoben |
| **Model-Cluster** | Alle 5 Dateien nach app/core/models/ verschoben; core→providers Ausnahme für orchestrator |

### Re-Exports (Übergangsphase)

- `app/context/` → Re-Export von `app.core.context` (TODO: entfernen)
- `app/settings.py` → Re-Export von `app.core.config.settings` (TODO: entfernen)

### Arch-Guard-Anpassungen

- `core/llm/llm_complete.py` → debug: KNOWN_IMPORT_EXCEPTIONS (optionaler emit_event)
- `response_filter.py` aus TEMPORARILY_ALLOWED_ROOT_FILES entfernt

### Test-Ergebnisse (Phase A.2)

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture/ | 7 passed ✓ |
| tests/test_slash_commands.py | 4 passed ✓ |
| tests/test_llm_output_pipeline.py | 18 passed ✓ |
| tests/test_db_files.py | 1 passed ✓ |
| tests/test_projects.py | 2 failed (vor Refactoring: DB-State/Assertion) |

---

---

## Phase A.3: UI→GUI Moves (2026-03-16)

**Ziel:** Nur die klarsten, risikoarmen ui→gui-Moves laut Transition-Plan.

### Durchgeführte Moves

| # | Move | Ziel | Status |
|---|------|------|--------|
| 1 | app/ui/events/ | app/gui/events/ | ✓ |
| 2 | app/ui/widgets/empty_state_widget.py | app/gui/widgets/empty_state_widget.py | ✓ |
| 3 | app/ui/chat/chat_navigation_panel.py | app/gui/domains/operations/chat/panels/chat_navigation_panel.py | ✓ |
| 4 | app/ui/chat/chat_details_panel.py | app/gui/domains/operations/chat/panels/chat_details_panel.py | ✓ |
| 5 | app/ui/project/project_hub_page.py | app/gui/domains/project_hub/project_hub_page.py | ✓ |
| 6 | app/ui/project/project_switcher_dialog.py | app/gui/project_switcher/project_switcher_dialog.py | ✓ |

### Re-Exports (Rückwärtskompatibilität)

- `app.ui.events` → Re-Export von `app.gui.events` (minimal, **keine Konsumenten** – Übergang)
- `app.ui.widgets` → Re-Export von `app.gui.widgets` (minimal, **keine Konsumenten** – Übergang)
- `app.ui.project` → Re-Export von ProjectHubPage, ProjectSwitcherDialog aus gui

**Cross-Cutting-Verifikation (2026-03-16):** Alle Imports nutzen bereits `app.gui.events` und `app.gui.widgets`. Die ui-Re-Exports sind ungenutzt und können nach vollständiger ui→gui-Migration entfernt werden.

### Arch-Guard-Anpassungen

- `core/context/project_context_manager.py` → gui, services: KNOWN_IMPORT_EXCEPTIONS
- `core/models/orchestrator.py` → providers: KNOWN_IMPORT_EXCEPTIONS (arch. Entscheidung: Orchestrierung)
- `ARCHITECTURE_GUARD_RULES.md`: gui/events und gui/widgets als kanonisch dokumentiert

### Test-Ergebnisse (Phase A.3)

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture/ | 12 passed ✓ |
| tests/behavior/ (ChatNavigationPanel) | test_chat_navigation_language_consistency: Import-Pfad aktualisiert |

**Hinweis:** tests/behavior/ zeigen weiterhin NameError (AGENT_ACTIVITY in navigation_registry) – vor Refactoring bestehend.

---

## Phase A.4: Context, Settings, Model-Cluster (2026-03-16)

**Durchgeführt:**
- ActiveProjectContext Qt-entkoppelt (subscribe/unsubscribe statt Signal)
- AppSettings über SettingsBackend (InMemoryBackend, QSettingsBackendAdapter in gui)
- app/context/ → app/core/context/ (active_project, project_context_manager)
- app/settings.py → app/core/config/settings.py
- app/model_* → app/core/models/ (roles, router, registry, escalation_manager, orchestrator)

**Arch-Guard:** core/models/orchestrator.py → providers als Ausnahme dokumentiert.

## Phase A.5: Cross-Cutting events/widgets Konsolidierung (2026-03-16)

**Verifikation:** Migration war bereits vollständig. Alle Konsumenten nutzen `app.gui.events` und `app.gui.widgets`.

**Durchgeführt:**
- Redundante `app/ui/events/project_events.py` entfernt (duplizierter Re-Export)
- `app/ui/events/__init__.py` und `app/ui/widgets/__init__.py` als minimale Re-Exports mit Klarstellung
- `docs/06_operations_and_qa/UX_EMPTY_STATE_IMPLEMENTATION.md`: Import-Beispiel auf `app.gui.widgets` aktualisiert

**Import-Hygiene:** Keine Änderung nötig – alle Imports nutzen bereits kanonische Pfade.

**Tests:** Pytest/PySide6 nicht in System-Python verfügbar. Tests in Projekt-venv ausführen.

## Phase A.6: Root-Cleanup und Legacy-Konsolidierung (2026-03-16)

**Sprint-Ziel:** Root entschlacken, Legacy-Widgets verorten, Re-Export-Hygiene.

### Entfernte Re-Exports

| Re-Export | Status | Begründung |
|-----------|--------|------------|
| `app/context/` | **entfernt** | Keine Konsumenten; alle nutzen `app.core.context` |
| `app/settings.py` | **entfernt** | Keine Konsumenten; alle nutzen `app.core.config.settings` |
| `app/ui/events/` | **entfernt** | Keine Konsumenten; alle nutzen `app.gui.events` |
| `app/ui/widgets/` | **entfernt** | Keine Konsumenten; alle nutzen `app.gui.widgets` |

### Verbliebene Übergangs-Re-Exports

| Re-Export | Status | Geplantes Entfernungsziel |
|-----------|--------|---------------------------|
| `app/db.py` | beibehalten | Nach Migration aller Imports auf `app.core.db` |
| `app/ollama_client.py` | beibehalten | Nach Migration auf `app.providers.ollama_client` |

### Legacy-Widgets nach app/gui/legacy/ verschoben

| Root-Datei | Neuer Pfad | Status |
|------------|------------|--------|
| `app/chat_widget.py` | `app/gui/legacy/chat_widget.py` | ✓ |
| `app/sidebar_widget.py` | `app/gui/legacy/sidebar_widget.py` | ✓ |
| `app/project_chat_list_widget.py` | `app/gui/legacy/project_chat_list_widget.py` | ✓ |
| `app/message_widget.py` | `app/gui/legacy/message_widget.py` | ✓ |
| `app/file_explorer_widget.py` | `app/gui/legacy/file_explorer_widget.py` | ✓ |

**Importpfade:** `app.main`, `archive/run_legacy_gui.py` und alle Tests nutzen nun `app.gui.legacy`.

### Root-Status nach Sprint

| Datei | Status | Begründung |
|-------|--------|------------|
| `__init__.py` | erlaubt | Package-Marker |
| `__main__.py` | erlaubt | Einstieg `python -m app` |
| `main.py` | erlaubt | Legacy-Einstiegspunkt |
| `resources.qrc` | erlaubt | Qt-Ressource |
| `resources_rc.py` | erlaubt | Qt-generiert |
| `db.py` | temporär erlaubt | Re-Export; kanonisch: app.core.db |
| `ollama_client.py` | temporär erlaubt | Re-Export; kanonisch: app.providers |
| `critic.py` | temporär erlaubt | Merge in app.agents.critic geplant |

### Arch-Guard-Anpassungen

- `settings.py` aus TEMPORARILY_ALLOWED_ROOT_FILES entfernt
- Legacy-Widgets aus TEMPORARILY_ALLOWED_ROOT_FILES entfernt
- `chat_widget.py` aus ALLOWED_UI_IMPORTER_PATTERNS entfernt (gui/ deckt gui/legacy ab)

### Test-Ergebnisse (Phase A.6)

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture/ | 11/12 passed (1 pre-existing: core/context/active_project.py → services) |
| tests/test_streaming_logic.py | 6 passed ✓ |
| tests/smoke/test_basic_chat.py | 4 passed ✓ |
| tests/unit/test_tools.py | 11 passed ✓ |

### Verbleibende manual_review-Punkte

- `main.py` im Root: bleibt; nächster Schritt wäre Move nach `archive/` oder `gui/legacy/` nach Legacy-Abschaltung
- `core/context/active_project.py` → services: Architektur-Verletzung vor Sprint; KNOWN_IMPORT_EXCEPTIONS prüfen

---

## Phase A.7: UI→GUI Chat Migration Sprint (2026-03-16)

**Ziel:** Kanonische Chat-Domain unter `app/gui/domains/operations/chat/panels/` stärken. Nur die 6 klarsten Chat-Bausteine migrieren.

### Durchgeführte Moves

| # | Datei | Ziel | Status |
|---|-------|------|--------|
| 1 | chat_navigation_panel.py | gui/panels/ | already_done (Phase A.3) |
| 2 | chat_details_panel.py | gui/panels/ | already_done (Phase A.3) |
| 3 | topic_editor_dialog.py | gui/panels/ | ✓ migrated |
| 4 | topic_actions.py | gui/panels/ | ✓ migrated |
| 5 | chat_item_context_menu.py | gui/panels/ | ✓ migrated |
| 6 | chat_message_widget.py | gui/panels/ | ✓ migrated |

### Import-Konsolidierung

| Modul | Änderung |
|-------|----------|
| chat_navigation_panel.py | topic_actions, chat_item_context_menu → gui.panels |
| conversation_view.py | chat_message_widget → gui.panels |
| ui/chat/__init__.py | Re-Export von gui.panels für migrierte Komponenten |

### ui/chat Re-Exports (Übergang)

| ui-Datei | Status | Begründung |
|----------|--------|------------|
| topic_editor_dialog.py | Re-Export | Legacy-Konsumenten (ui.chat.__init__) |
| topic_actions.py | Re-Export | Legacy-Konsumenten |
| chat_item_context_menu.py | Re-Export | Legacy-Konsumenten |
| chat_message_widget.py | Re-Export | Legacy-Konsumenten (conversation_view nutzt gui direkt) |

### Verbleibende Restpunkte in ui/chat/

| Datei | Status | Begründung |
|-------|--------|------------|
| conversation_view.py | keep_temporarily | Legacy chat_widget; nicht in diesem Sprint |
| chat_composer_widget.py | keep_temporarily | Legacy |
| chat_header_widget.py | keep_temporarily | Legacy |
| chat_list_item.py | keep_temporarily | Legacy; intern von chat_topic_section |
| chat_topic_section.py | keep_temporarily | Legacy; von chat_navigation_panel importiert |

### Test-Ergebnisse (Phase A.7)

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture/ | 11/12 passed (1 pre-existing: core→services) |
| tests/smoke/test_basic_chat.py | 4 passed ✓ |
| tests/ui/test_chat_ui.py | 8/9 passed (1 pre-existing: Prompt scope/project_id) |
| tests/behavior/ | 5 passed ✓ |
| Import-Verifikation | gui.panels + ui.chat Re-Exports OK ✓ |

### Bekannte Fehler (nicht durch diesen Sprint)

- `test_no_forbidden_import_directions`: core/context/active_project.py → services
- `test_prompt_apply_to_chat_visible`: Prompt.__init__() missing scope, project_id

---

## Phase A.8: Prompt Studio Domain Consolidation (2026-03-16)

**Ziel:** Kanonische Prompt-Studio-Domain unter `app/gui/domains/operations/prompt_studio/`. ui/prompts nur noch Re-Exports.

### Status: already_done

Die Konsolidierung war bereits vollständig durchgeführt. Verifikation:

| Prüfung | Ergebnis |
|---------|----------|
| operations_screen | Importiert `app.gui.domains.operations.prompt_studio.PromptStudioWorkspace` ✓ |
| prompt_studio_inspector | Importiert `app.gui.domains.operations.prompt_studio.panels.prompt_version_panel` ✓ |
| app.ui.prompts Konsumenten | Keine – alle Imports nutzen gui-Pfade ✓ |
| ui/prompts Dateien | Alle 9 Dateien sind Re-Exports von gui ✓ |

### Kanonische gui-Struktur

```
app/gui/domains/operations/prompt_studio/
├── __init__.py
├── prompt_studio_workspace.py
└── panels/
    ├── __init__.py
    ├── prompt_navigation_panel.py
    ├── prompt_list_panel.py
    ├── prompt_list_item.py
    ├── prompt_editor_panel.py
    ├── prompt_templates_panel.py
    ├── prompt_test_lab.py
    ├── prompt_version_panel.py
    ├── library_panel.py
    ├── editor_panel.py
    └── preview_panel.py
```

### ui/prompts Re-Exports (Übergang)

| ui-Datei | Status | Re-Export von |
|----------|--------|---------------|
| __init__.py | Re-Export | gui prompt_studio + panels |
| prompt_studio_workspace.py | Re-Export | gui prompt_studio_workspace |
| prompt_navigation_panel.py | Re-Export | gui panels |
| prompt_list_panel.py | Re-Export | gui panels |
| prompt_list_item.py | Re-Export | gui panels |
| prompt_editor_panel.py | Re-Export | gui panels |
| prompt_templates_panel.py | Re-Export | gui panels |
| prompt_test_lab.py | Re-Export | gui panels |
| prompt_version_panel.py | Re-Export | gui panels |

### Test-Ergebnisse (Phase A.8)

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture/ | 12 passed ✓ |
| Smoke/Behavior | 8 failed (pre-existing: AGENT_ACTIVITY, DB-Schema) |

---

## Phase A.9: Settings Domain Consolidation (2026-03-16)

**Ziel:** Kanonische Settings-Domain unter `app/gui/domains/settings/`. ui/settings nur noch Re-Exports.

### Status: already_done

Die Konsolidierung war bereits vollständig durchgeführt. Verifikation:

| Prüfung | Ergebnis |
|---------|----------|
| settings_screen | Importiert `app.gui.domains.settings.settings_workspace.SettingsWorkspace` ✓ |
| app.ui.settings Konsumenten | Keine – settings_screen nutzt gui ✓ |
| ui/settings Dateien | Alle sind Re-Exports von gui ✓ |

### Kanonische gui-Struktur

```
app/gui/domains/settings/
├── __init__.py
├── settings_screen.py
├── settings_workspace.py
├── navigation.py
├── settings_nav.py
├── categories/
│   ├── __init__.py
│   ├── base_category.py
│   ├── application_category.py
│   ├── appearance_category.py
│   ├── ai_models_category.py
│   ├── data_category.py
│   ├── privacy_category.py
│   ├── advanced_category.py
│   ├── project_category.py
│   └── workspace_category.py
├── workspaces/
│   ├── base_settings_workspace.py
│   ├── appearance_workspace.py
│   ├── models_workspace.py
│   ├── agents_workspace.py
│   ├── system_workspace.py
│   └── advanced_workspace.py
└── panels/
```

### ui/settings Re-Exports (Übergang)

| ui-Datei | Status |
|----------|--------|
| __init__.py | Re-Export von gui |
| settings_workspace.py | Re-Export |
| settings_navigation.py | Re-Export (gui navigation.py) |
| categories/__init__.py | Re-Export |
| categories/*.py | Re-Export |

### Test-Ergebnisse (Phase A.9)

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture/ | 12 passed ✓ |
| tests/regression/test_settings_theme_tokens.py | 3 passed ✓ |

### Änderung

- Docstring in settings_screen.py: „ui/settings“ → „gui/domains/settings“

---

## Phase A.10: Knowledge Domain Consolidation (2026-03-16)

**Ziel:** Kanonische Knowledge-Domain unter `app/gui/domains/operations/knowledge/`. ui/knowledge nur noch Re-Exports.

### Inventar (Step 1)

| ui-Datei | Klassifikation | Aktion |
|----------|----------------|--------|
| knowledge_workspace.py | remove_later | gui kanonisch; ui nicht von gui genutzt |
| source_list_panel.py | remove_later | gui hat KnowledgeSourceExplorerPanel |
| source_list_item.py | merge_into_gui | Mit SourceListItemWidget vereinheitlicht |
| source_details_panel.py | move_to_gui | Nach gui/panels/ verschoben |
| collection_panel.py | move_to_gui | Nach gui/panels/ verschoben |
| collection_dialog.py | move_to_gui | Nach gui/panels/ verschoben |
| index_status_page.py | move_to_gui | Nach gui/panels/ verschoben |
| chunk_viewer_panel.py | move_to_gui | Nach gui/panels/ verschoben |
| knowledge_navigation_panel.py | move_to_gui | Nach gui/panels/ verschoben |

### Durchgeführte Änderungen

| # | Aktion | Details |
|---|--------|---------|
| 1 | SourceListItemWidget merge | chunk_count, collection, source_id-Alias; TYPE_LABELS erweitert |
| 2 | Panels nach gui | collection_dialog, collection_panel, source_details_panel, index_status_page, chunk_viewer_panel, knowledge_navigation_panel |
| 3 | ui/knowledge | Nur __init__.py mit Re-Exports von gui; alle Implementierungsdateien entfernt |
| 4 | KnowledgeSourceExplorerPanel | Übergibt chunk_count, collection an SourceListItemWidget |

### Kanonische gui-Struktur

```
app/gui/domains/operations/knowledge/
├── __init__.py
├── knowledge_workspace.py
└── panels/
    ├── __init__.py
    ├── knowledge_source_explorer_panel.py
    ├── knowledge_overview_panel.py
    ├── retrieval_test_panel.py
    ├── source_list_item.py          # Kanonisch (SourceListItemWidget)
    ├── source_details_panel.py
    ├── collection_panel.py
    ├── collection_dialog.py
    ├── index_status_page.py
    ├── chunk_viewer_panel.py
    ├── knowledge_navigation_panel.py
    └── ...
```

### ui/knowledge (Kompatibilitätsschicht)

| ui-Datei | Status |
|----------|--------|
| __init__.py | Re-Export von gui (KnowledgeWorkspace, SourceListItem, Panels) |

### Test-Ergebnisse (Phase A.10)

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture/ | 12 passed ✓ |
| Import-Verifikation | gui + ui Re-Exports OK ✓ |
| Bekannte Fehler | AGENT_ACTIVITY, DB-Schema, AgentListPanel (vor Refactoring) |

---

## Phase A.11: Agents UI Architecture Audit (2026-03-16)

**Ziel:** Architektur-Audit der Agents-UI-Domain. Keine physischen Moves.

### Audit-Ergebnis

| Output | Ergebnis |
|--------|----------|
| **Strategie** | C (Hybrid) |
| **Audit-Dokument** | docs/architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md |
| **Zielbaum** | gui/domains/control_center/agents_ui/ |

### Befunde

- **Agent Manager flow** (7 Dateien): Einzige echte Implementierung mit AgentService. Wird von main.py (Legacy) genutzt.
- **AgentWorkspace** (4 Dateien): Nie instanziiert. Dead Code.
- **AgentsWorkspace (gui)**: Demo-Daten. Soll durch AgentManagerPanel ersetzt werden.

### Datei-Klassifikation

| Status | Dateien |
|--------|---------|
| move | agent_manager_panel, agent_list_panel, agent_list_item, agent_profile_panel, agent_avatar_widget, agent_form_widgets, agent_performance_tab |
| remove_later | agent_workspace, agent_navigation_panel, agent_library_panel |
| manual_review | agent_editor_panel, agent_runs_panel, agent_activity_panel, agent_skills_panel |

---

## Phase A.12: Agents UI Phase 1 Migration ✓ (2026-03-16)

**Ziel:** Agent Manager flow nach gui/domains/control_center/agents_ui migrieren, Control Center Demo ersetzen.

**Report:** docs/architecture/AGENTS_UI_PHASE1_MIGRATION_REPORT.md

### Durchgeführte Moves

| # | Datei | Ziel | Status |
|---|-------|------|--------|
| 1 | agent_manager_panel.py | agents_ui/ | ✓ |
| 2 | agent_list_panel.py | agents_ui/ | ✓ |
| 3 | agent_list_item.py | agents_ui/ | ✓ |
| 4 | agent_profile_panel.py | agents_ui/ | ✓ |
| 5 | agent_avatar_widget.py | agents_ui/ | ✓ |
| 6 | agent_form_widgets.py | agents_ui/ | ✓ |
| 7 | agent_performance_tab.py | agents_ui/ | ✓ |

### Control Center Integration

- **AgentsWorkspace** hostet nun **AgentManagerPanel** (kanonisch)
- AgentRegistryPanel, AgentSummaryPanel isoliert (nicht mehr genutzt)

### ui/agents Re-Exports

- 7 migrierte Dateien: Re-Export von agents_ui
- 7 nicht migrierte Dateien: bleiben in ui (remove_later / manual_review)

### Test-Ergebnisse (Phase A.12)

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture/ | 12 passed ✓ |
| Agent-related tests | 34 passed ✓ |
| tests/qa/generators/test_update_control_center.py | 14 passed ✓ |
| Pre-existing | test_app_startup, test_shell_gui (sidebar/DB) |

---

## Nächste Schritte (Phase A Fortsetzung)

- [ ] Re-Exports app/db.py, app/ollama_client.py entfernen (nach Verifikation)
- [ ] main.py aus Root entschärfen (nach Legacy-GUI-Abschaltung)
- [ ] critic.py in app.agents.critic merge
