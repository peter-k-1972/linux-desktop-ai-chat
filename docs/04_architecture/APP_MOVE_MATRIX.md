# App Move Matrix

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Plan – keine Umsetzung  
**Referenz:** docs/architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md, docs/architecture/APP_PACKAGE_ARCHITECTURE_ASSESSMENT.md

---

## Legende

| Spalte | Bedeutung |
|--------|-----------|
| **action** | `move` = Verschieben, `remove` = Entfernen, `merge` = Zusammenführen, `keep` = Bleibt |
| **risk_level** | `low`, `medium`, `high` |
| **requires_import_update** | `yes` = Alle Importe in app/ und tests/ müssen angepasst werden |
| **requires_merge** | `yes` = Inhalt in andere Datei integrieren |
| **requires_manual_review** | `yes` = Manuelle Prüfung vor/nach Move nötig |

---

## 1. Root-Dateien

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/__init__.py | app/__init__.py | keep | Package-Marker | low | no | no | no |
| app/__main__.py | app/__main__.py | keep | Einstieg python -m app | low | no | no | no |
| app/main.py | app/main.py | keep | Einstiegspunkt (Legacy + Delegation) | low | no | no | yes |
| app/chat_widget.py | app/gui/legacy/chat_widget.py | move | Legacy-Widget, Tests nutzen | high | yes | no | yes | ✓ 2026-03-16 |
| app/sidebar_widget.py | app/gui/legacy/sidebar_widget.py | move | Legacy-Widget | high | yes | no | yes | ✓ 2026-03-16 |
| app/project_chat_list_widget.py | app/gui/legacy/project_chat_list_widget.py | move | Legacy-Widget | high | yes | no | yes | ✓ 2026-03-16 |
| app/message_widget.py | app/gui/legacy/message_widget.py | move | Legacy-Widget | high | yes | no | yes | ✓ 2026-03-16 |
| app/file_explorer_widget.py | app/gui/legacy/file_explorer_widget.py | move | Legacy-Widget | medium | yes | no | yes | ✓ 2026-03-16 |
| app/settings.py | app/core/config/settings.py | move | App-Konfiguration | high | yes | no | no |
| app/db.py | app/core/db/database_manager.py | move | Datenbank-Kern | high | yes | no | no |
| app/ollama_client.py | app/providers/ollama_client.py | move | Low-Level Provider-Client | high | yes | no | no |
| app/model_orchestrator.py | app/core/models/orchestrator.py | move | Modell-Orchestrierung | high | yes | no | no |
| app/model_registry.py | app/core/models/registry.py | move | Modell-Registry | high | yes | no | no |
| app/model_roles.py | app/core/models/roles.py | move | Modell-Rollen | high | yes | no | no |
| app/model_router.py | app/core/models/router.py | move | Prompt-Routing | high | yes | no | no |
| app/escalation_manager.py | app/core/models/escalation_manager.py | move | Modell-Eskalation | high | yes | no | no |
| app/response_filter.py | app/core/llm/response_filter.py | move | LLM-Output-Filter | medium | yes | no | yes |
| app/tools.py | app/tools/filesystem.py | move | FileSystemTools | high | yes | no | no |
| app/web_search.py | app/tools/web_search.py | move | Web-Suche Tool | medium | yes | no | no |
| app/critic.py | app/agents/critic.py | merge | In CriticAgent integrieren, Root entfernen | medium | yes | yes | yes |
| app/resources_rc.py | app/resources_rc.py | keep | Qt-generiert, Root oder gui/resources | low | no | no | no |
| app/resources.qrc | app/resources.qrc | keep | Qt-Ressource | low | no | no | no |

---

## 2. Package commands → core/commands

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/commands/__init__.py | app/core/commands/__init__.py | move | Chat-Commands in Core | medium | yes | no | no |
| app/commands/chat_commands.py | app/core/commands/chat_commands.py | move | Slash-Command-Parsing | medium | yes | no | no |

---

## 3. Package context → core/context

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/context/__init__.py | app/core/context/__init__.py | move | Projekt-Kontext in Core | medium | yes | no | no |
| app/context/active_project.py | app/core/context/active_project.py | move | ActiveProjectContext | medium | yes | no | no |
| app/core/project_context_manager.py | app/core/context/project_context_manager.py | move | ✓ 2026-03-16 | medium | yes | no | no |

---

## 4. Package help → gui/help

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/help/__init__.py | app/gui/help/__init__.py | move | Help ist UI | medium | yes | no | no |
| app/help/help_index.py | app/gui/help/help_index.py | move | Help-Index | medium | yes | no | no |
| app/help/help_window.py | app/gui/help/help_window.py | move | Help-Fenster | medium | yes | no | no |
| app/help/doc_generator.py | app/gui/help/doc_generator.py | move | Doc-Generator | medium | yes | no | no |
| app/help/guided_tour.py | app/gui/help/guided_tour.py | move | Guided Tour | medium | yes | no | no |
| app/help/tooltip_helper.py | app/gui/help/tooltip_helper.py | move | Tooltip-Helper | medium | yes | no | no |

---

## 5. Package llm → core/llm

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/llm/__init__.py | app/core/llm/__init__.py | move | LLM in Core | high | yes | no | no |
| app/llm/llm_complete.py | app/core/llm/llm_complete.py | move | Completion | high | yes | no | no |
| app/llm/llm_output_pipeline.py | app/core/llm/llm_output_pipeline.py | move | Output-Pipeline | high | yes | no | no |
| app/llm/llm_response_cleaner.py | app/core/llm/llm_response_cleaner.py | move | Response-Cleaner | high | yes | no | no |
| app/llm/llm_response_result.py | app/core/llm/llm_response_result.py | move | Response-Result | high | yes | no | no |
| app/llm/llm_retry_policy.py | app/core/llm/llm_retry_policy.py | move | Retry-Policy | high | yes | no | no |

---

## 6. Package models → remove

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/models/ | – | remove | Leeres Package | low | no | no | no |

---

## 7. Package qa → services / debug

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/qa/__init__.py | app/services/qa/__init__.py | move | QA-Adapter zu Services | medium | yes | no | no |
| app/qa/dashboard_adapter.py | app/services/qa/dashboard_adapter.py | move | Dashboard-Adapter | medium | yes | no | no |
| app/qa/drilldown_models.py | app/services/qa/drilldown_models.py | move | Drilldown-Modelle | medium | yes | no | no |
| app/qa/operations_adapter.py | app/services/qa/operations_adapter.py | move | Operations-Adapter | medium | yes | no | no |
| app/qa/operations_models.py | app/services/qa/operations_models.py | move | Operations-Modelle | medium | yes | no | no |

---

## 8. Package resources → gui/resources

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/resources/styles.py | app/gui/resources/styles.py | move | Styles in GUI | medium | yes | no | no |

---

## 9. Package runtime → debug

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/runtime/__init__.py | app/debug/__init__.py | merge | Runtime in Debug | medium | yes | no | no |
| app/runtime/gui_log_buffer.py | app/debug/gui_log_buffer.py | move | Log-Buffer zu Debug | medium | yes | no | no |

---

## 10. Package ui → gui (Migration)

### 10.1 ui/agents → gui/domains/control_center/agents_ui ✓ (2026-03-16 Phase 1)

**Audit:** docs/architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md (2026-03-16). Strategy C (Hybrid).

| current_path | target_path | action | reason | risk_level | status |
|--------------|-------------|--------|--------|------------|--------|
| app/ui/agents/agent_manager_panel.py | agents_ui/agent_manager_panel.py | move | Kanonisch; main.py + Control Center | high | ✓ migriert |
| app/ui/agents/agent_list_panel.py | agents_ui/agent_list_panel.py | move | Von AgentManagerPanel | medium | ✓ migriert |
| app/ui/agents/agent_list_item.py | agents_ui/agent_list_item.py | move | Von AgentListPanel | low | ✓ migriert |
| app/ui/agents/agent_profile_panel.py | agents_ui/agent_profile_panel.py | move | Von AgentManagerPanel | medium | ✓ migriert |
| app/ui/agents/agent_avatar_widget.py | agents_ui/agent_avatar_widget.py | move | Von AgentProfilePanel | low | ✓ migriert |
| app/ui/agents/agent_form_widgets.py | agents_ui/agent_form_widgets.py | move | Von AgentProfilePanel | low | ✓ migriert |
| app/ui/agents/agent_performance_tab.py | agents_ui/agent_performance_tab.py | move | Von AgentProfilePanel | low | ✓ migriert |
| app/ui/agents/agent_workspace.py | – | remove | Nie instanziiert | low | remove_later |
| app/ui/agents/agent_navigation_panel.py | – | remove | Nur von AgentWorkspace | low | remove_later |
| app/ui/agents/agent_library_panel.py | – | remove | Nur von AgentWorkspace | low | remove_later |
| app/ui/agents/agent_editor_panel.py | – | manual_review | Andere API als AgentProfileForm | – | – |
| app/ui/agents/agent_runs_panel.py | agents_ui/ (Phase 3) | manual_review | Migrieren optional | – | – |
| app/ui/agents/agent_activity_panel.py | agents_ui/ (Phase 3) | manual_review | Migrieren optional | – | – |
| app/ui/agents/agent_skills_panel.py | agents_ui/ (Phase 3) | manual_review | Migrieren optional | – | – |

**ui/agents:** 7 Dateien Re-Export von agents_ui. 7 Dateien bleiben (remove_later / manual_review).

### 10.2 ui/chat → gui/domains/operations/chat (ergänzt)

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/ui/chat/__init__.py | app/gui/domains/operations/chat/__init__.py | merge | Chat-UI in gui | high | yes | yes | yes |
| app/ui/chat/chat_composer_widget.py | app/gui/domains/operations/chat/panels/chat_composer_widget.py | move | Widget | high | yes | no | no |
| app/ui/chat/chat_details_panel.py | app/gui/domains/operations/chat/panels/chat_details_panel.py | move | Panel (bereits genutzt) | high | yes | no | no | ✓ |
| app/ui/chat/chat_header_widget.py | app/gui/domains/operations/chat/panels/chat_header_widget.py | move | Widget | high | yes | no | no |
| app/ui/chat/chat_item_context_menu.py | app/gui/domains/operations/chat/panels/chat_item_context_menu.py | move | Context-Menu | high | yes | no | no | ✓ |
| app/ui/chat/chat_list_item.py | app/gui/domains/operations/chat/panels/chat_list_item.py | merge | Prüfen: gui hat chat_list_item | high | yes | yes | yes |
| app/ui/chat/chat_message_widget.py | app/gui/domains/operations/chat/panels/chat_message_widget.py | move | Widget | high | yes | no | no | ✓ |
| app/ui/chat/chat_navigation_panel.py | app/gui/domains/operations/chat/panels/chat_navigation_panel.py | move | Navigation-Panel | high | yes | no | no | ✓ |
| app/ui/chat/chat_topic_section.py | app/gui/domains/operations/chat/panels/chat_topic_section.py | move | Topic-Section | high | yes | no | no |
| app/ui/chat/conversation_view.py | app/gui/domains/operations/chat/panels/conversation_view.py | move | Conversation-View | high | yes | no | no |
| app/ui/chat/topic_actions.py | app/gui/domains/operations/chat/panels/topic_actions.py | move | Topic-Actions | high | yes | no | no | ✓ |
| app/ui/chat/topic_editor_dialog.py | app/gui/domains/operations/chat/panels/topic_editor_dialog.py | move | Dialog | high | yes | no | no | ✓ |

### 10.3 ui/command_center → gui/domains/dashboard/command_center

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/ui/command_center/__init__.py | app/gui/domains/dashboard/command_center/__init__.py | move | Command Center in Dashboard | high | yes | no | yes |
| app/ui/command_center/audit_operations_view.py | app/gui/domains/dashboard/command_center/audit_operations_view.py | move | View | high | yes | no | no |
| app/ui/command_center/command_center_view.py | app/gui/domains/dashboard/command_center/command_center_view.py | move | Haupt-View | high | yes | no | no |
| app/ui/command_center/governance_view.py | app/gui/domains/dashboard/command_center/governance_view.py | move | View | high | yes | no | no |
| app/ui/command_center/incident_operations_view.py | app/gui/domains/dashboard/command_center/incident_operations_view.py | move | View | high | yes | no | no |
| app/ui/command_center/qa_drilldown_view.py | app/gui/domains/dashboard/command_center/qa_drilldown_view.py | move | View | high | yes | no | no |
| app/ui/command_center/qa_operations_view.py | app/gui/domains/dashboard/command_center/qa_operations_view.py | move | View | high | yes | no | no |
| app/ui/command_center/review_operations_view.py | app/gui/domains/dashboard/command_center/review_operations_view.py | move | View | high | yes | no | no |
| app/ui/command_center/runtime_debug_view.py | app/gui/domains/dashboard/command_center/runtime_debug_view.py | move | View | high | yes | no | no |
| app/ui/command_center/subsystem_detail_view.py | app/gui/domains/dashboard/command_center/subsystem_detail_view.py | move | View | high | yes | no | no |

### 10.4 ui/debug → gui/domains/runtime_debug/debug_views

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/ui/debug/__init__.py | app/gui/domains/runtime_debug/debug_views/__init__.py | move | Debug-Views | medium | yes | no | no |
| app/ui/debug/agent_activity_view.py | app/gui/domains/runtime_debug/debug_views/agent_activity_view.py | move | View | medium | yes | no | no |
| app/ui/debug/agent_debug_panel.py | app/gui/domains/runtime_debug/debug_views/agent_debug_panel.py | move | Panel | medium | yes | no | no |
| app/ui/debug/event_timeline_view.py | app/gui/domains/runtime_debug/debug_views/event_timeline_view.py | move | View | medium | yes | no | no |
| app/ui/debug/model_usage_view.py | app/gui/domains/runtime_debug/debug_views/model_usage_view.py | move | View | medium | yes | no | no |
| app/ui/debug/task_graph_view.py | app/gui/domains/runtime_debug/debug_views/task_graph_view.py | move | View | medium | yes | no | no |
| app/ui/debug/tool_execution_view.py | app/gui/domains/runtime_debug/debug_views/tool_execution_view.py | move | View | medium | yes | no | no |

### 10.5 ui/events → gui/events ✓ (2026-03-16)

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/ui/events/__init__.py | app/gui/events/__init__.py | move | UI-Events | high | yes | no | no |
| app/ui/events/project_events.py | app/gui/events/project_events.py | move | Projekt-Events | high | yes | no | no |
**Status:** Erledigt. gui/events kanonisch. ui/events nur noch __init__.py als minimaler Re-Export (project_events.py entfernt, redundant). Keine Konsumenten von app.ui.events.

### 10.6 ui/knowledge → gui/domains/operations/knowledge ✓ (2026-03-16)

| current_path | target_path | action | status |
|--------------|-------------|--------|--------|
| app/ui/knowledge/__init__.py | – | merge | ✓ Re-Export von gui |
| app/ui/knowledge/chunk_viewer_panel.py | gui/.../panels/chunk_viewer_panel.py | move | ✓ migriert |
| app/ui/knowledge/collection_dialog.py | gui/.../panels/collection_dialog.py | move | ✓ migriert |
| app/ui/knowledge/collection_panel.py | gui/.../panels/collection_panel.py | move | ✓ migriert |
| app/ui/knowledge/index_status_page.py | gui/.../panels/index_status_page.py | move | ✓ migriert |
| app/ui/knowledge/knowledge_navigation_panel.py | gui/.../panels/knowledge_navigation_panel.py | move | ✓ migriert |
| app/ui/knowledge/knowledge_workspace.py | – | remove_later | ✓ gui kanonisch |
| app/ui/knowledge/source_details_panel.py | gui/.../panels/source_details_panel.py | move | ✓ migriert |
| app/ui/knowledge/source_list_item.py | gui/.../panels/source_list_item.py | merge | ✓ in SourceListItemWidget |
| app/ui/knowledge/source_list_panel.py | – | remove_later | ✓ gui hat KnowledgeSourceExplorerPanel |

**Kanonisch:** app/gui/domains/operations/knowledge/. operations_screen importiert aus gui. ui/knowledge nur Re-Exports.

### 10.7 ui/project → gui/project_switcher (bereits teilweise in gui)

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/ui/project/__init__.py | app/gui/project_switcher/__init__.py | merge | Projekt-UI | high | yes | yes | yes |
| app/ui/project/project_hub_page.py | app/gui/domains/project_hub/project_hub_page.py | move | Page | high | yes | no | no | ✓ |
| app/ui/project/project_switcher_button.py | app/gui/project_switcher/project_switcher_button.py | merge | gui hat bereits project_switcher_button | high | yes | yes | yes |
| app/ui/project/project_switcher_dialog.py | app/gui/project_switcher/project_switcher_dialog.py | move | Dialog | high | yes | no | no | ✓ |

### 10.8 ui/prompts → gui/domains/operations/prompt_studio ✓ (2026-03-16)

| current_path | target_path | action | status |
|--------------|-------------|--------|--------|
| app/ui/prompts/__init__.py | – | merge | ✓ Re-Export von gui |
| app/ui/prompts/prompt_editor_panel.py | gui/.../panels/prompt_editor_panel.py | move | ✓ Re-Export |
| app/ui/prompts/prompt_list_item.py | gui/.../panels/prompt_list_item.py | merge | ✓ Re-Export |
| app/ui/prompts/prompt_list_panel.py | gui/.../panels/prompt_list_panel.py | move | ✓ Re-Export |
| app/ui/prompts/prompt_navigation_panel.py | gui/.../panels/prompt_navigation_panel.py | move | ✓ Re-Export |
| app/ui/prompts/prompt_studio_workspace.py | gui/.../prompt_studio_workspace.py | merge | ✓ Re-Export |
| app/ui/prompts/prompt_templates_panel.py | gui/.../panels/prompt_templates_panel.py | move | ✓ Re-Export |
| app/ui/prompts/prompt_test_lab.py | gui/.../panels/prompt_test_lab.py | move | ✓ Re-Export |
| app/ui/prompts/prompt_version_panel.py | gui/.../panels/prompt_version_panel.py | move | ✓ Re-Export |

**Kanonisch:** app/gui/domains/operations/prompt_studio/. operations_screen und prompt_studio_inspector importieren aus gui.

### 10.9 ui/settings → gui/domains/settings ✓ (2026-03-16)

| current_path | target_path | action | status |
|--------------|-------------|--------|--------|
| app/ui/settings/__init__.py | – | merge | ✓ Re-Export von gui |
| app/ui/settings/settings_navigation.py | gui/.../navigation.py | move | ✓ Re-Export |
| app/ui/settings/settings_workspace.py | gui/.../settings_workspace.py | move | ✓ Re-Export |
| app/ui/settings/categories/__init__.py | gui/.../categories/ | move | ✓ Re-Export |
| app/ui/settings/categories/*.py | gui/.../categories/*.py | move | ✓ Re-Export |

**Kanonisch:** app/gui/domains/settings/. settings_screen importiert aus gui. ui/settings nur Re-Exports.

### 10.10 ui/sidepanel → gui/sidepanel

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/ui/sidepanel/__init__.py | app/gui/sidepanel/__init__.py | move | Side-Panels | high | yes | no | no |
| app/ui/sidepanel/chat_side_panel.py | app/gui/sidepanel/chat_side_panel.py | move | Chat-Side-Panel | high | yes | no | no |
| app/ui/sidepanel/model_settings_panel.py | app/gui/sidepanel/model_settings_panel.py | move | Model-Settings | high | yes | no | no |
| app/ui/sidepanel/prompt_manager_panel.py | app/gui/sidepanel/prompt_manager_panel.py | move | Prompt-Manager | high | yes | no | no |

### 10.11 ui/widgets → gui/widgets ✓ (2026-03-16)

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/ui/widgets/__init__.py | app/gui/widgets/__init__.py | move | Wiederverwendbare Widgets | high | yes | no | no |
| app/ui/widgets/empty_state_widget.py | app/gui/widgets/empty_state_widget.py | move | EmptyStateWidget | high | yes | no | no |
**Status:** Erledigt. gui/widgets kanonisch. ui/widgets nur __init__.py als minimaler Re-Export. Keine Konsumenten von app.ui.widgets.

### 10.12 ui/settings_dialog.py

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/ui/settings_dialog.py | app/gui/domains/settings/settings_dialog.py | move | Legacy-Settings-Dialog | high | yes | no | yes |

---

## 11. Core-Anpassungen

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/core/navigation/nav_areas.py | app/core/navigation/nav_areas.py | keep | Kanonisch | low | no | no | no |
| app/core/navigation/navigation_registry.py | app/core/navigation/navigation_registry.py | keep | Registry | medium | no | no | yes |
| app/core/project_context_manager.py | app/core/context/project_context_manager.py | move | Kontext in core/context | medium | yes | no | no |

**Hinweis:** `core.navigation.navigation_registry` importiert `gui.icons.registry` – vor Move: Icon-Abhängigkeit entfernen (String-IDs oder Injection).

---

## 12. gui/navigation – zentrale Navigation

| current_path | target_path | action | reason | risk_level | requires_import_update | requires_merge | requires_manual_review |
|--------------|-------------|--------|--------|------------|------------------------|----------------|------------------------|
| app/gui/navigation/nav_areas.py | app/gui/navigation/nav_areas.py | keep | Re-Export von core | low | no | no | no |
| app/gui/navigation/sidebar.py | app/gui/navigation/sidebar.py | keep | Haupt-Sidebar | low | no | no | no |
| app/gui/navigation/sidebar_config.py | app/gui/navigation/sidebar_config.py | keep | Sidebar-Konfiguration | low | no | no | no |
| app/gui/navigation/command_palette.py | app/gui/navigation/command_palette.py | keep | Command Palette | low | no | no | no |
| app/gui/navigation/workspace_graph.py | app/gui/navigation/workspace_graph.py | keep | Workspace-Graph-Dialog | low | no | no | no |
| app/gui/navigation/workspace_graph_resolver.py | app/gui/navigation/workspace_graph_resolver.py | keep | Graph-Resolver | low | no | no | no |

---

## 13. Packages ohne Move (bleiben)

| Package | Aktion |
|---------|--------|
| app/agents/* | keep (außer critic merge) |
| app/rag/* | keep |
| app/prompts/* | keep |
| app/providers/* | keep (ollama_client wird ergänzt) |
| app/services/* | keep (qa wird ergänzt) |
| app/debug/* | keep (runtime wird ergänzt) |
| app/metrics/* | keep |
| app/utils/* | keep |

---

## 14. Zusammenfassung: Entfernen

| current_path | reason |
|--------------|--------|
| app/critic.py | Merge in app/agents/critic.py |
| app/response_filter.py | Optional: Prüfen ob genutzt; ggf. entfernen oder nach core/llm |
| app/models/ | Leeres Package |

---

## 15. Zusammenfassung: Merge

| Quell 1 | Quell 2 | Ziel |
|---------|---------|------|
| app/critic.py | app/agents/critic.py | app/agents/critic.py |
| app/ui/knowledge/source_list_item.py | app/gui/.../knowledge/panels/source_list_item.py | app/gui/domains/operations/knowledge/panels/source_list_item.py |
| app/ui/chat/chat_list_item.py | app/gui/.../chat/panels/chat_list_item.py | Prüfen: eine oder beide behalten |
| app/ui/project/project_switcher_button.py | app/gui/project_switcher/project_switcher_button.py | app/gui/project_switcher/project_switcher_button.py |

---

## 16. Empfohlene Reihenfolge

1. **Phase 1 – Low Risk:** utils, tools (neu), response_filter
2. **Phase 2 – Core:** core/config, core/db, core/models, core/llm, core/commands, core/context
3. **Phase 3 – Providers:** ollama_client
4. **Phase 4 – Services:** qa, runtime → debug
5. **Phase 5 – GUI:** help, resources
6. **Phase 6 – UI-Migration:** gui/widgets, gui/events, gui/sidepanel, dann Domains
7. **Phase 7 – Legacy:** chat_widget, sidebar_widget, etc. (erst nach Legacy-GUI-Abschaltung)
