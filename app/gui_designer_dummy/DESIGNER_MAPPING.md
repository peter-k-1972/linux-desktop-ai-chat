
# Designer Mapping – Python-Architektur zu .ui-Dateien

Zuordnung zwischen der PySide6-GUI-Codebasis und den Qt Designer .ui-Dummy-Dateien.

**Abbildungsgrade:**
- `exact_visual_shell` – Shell-Struktur 1:1 abgebildet
- `strong_visual_match` – Layout und Zonen klar erkennbar
- `approximated_visual_match` – Struktur approximiert, Details vereinfacht
- `not_representable_in_ui_only` – Logik/State, nicht als reine UI abbildbar

---

## A. SHELL / APP-RAHMEN

| Python-Datei | Widget-Typ / Rolle | .ui-Datei | Abbildungsgrad | Offene dynamische Elemente | Python-Anbindung |
|--------------|--------------------|-----------|----------------|----------------------------|------------------|
| gui/shell/main_window.py | QMainWindow, Shell | shell/shell_main_window.ui | exact_visual_shell | TopBar-Actions, Docks | ja |
| gui/shell/docking_config.py | QDockWidget-Setup | In shell_main_window.ui | strong_visual_match | Dock-Sizes, Visibility | ja |
| gui/workspace/workspace_host.py | QStackedWidget | shell/workspace_host.ui | strong_visual_match | Screen-Registry, show_area | ja |
| gui/inspector/inspector_host.py | QWidget, QStackedWidget | shell/inspector_host.ui | strong_visual_match | set_content, prepare_for_setup | ja |
| gui/monitors/bottom_panel_host.py | QWidget, QTabWidget | shell/bottom_panel_host.ui | strong_visual_match | Tab-Inhalte (Logs, Events, etc.) | ja |
| gui/breadcrumbs/bar.py | QFrame | shell/breadcrumbs_bar.ui | approximated_visual_match | set_path, navigate_requested | ja |
| gui/navigation/command_palette.py | QDialog | dialogs/command_palette.ui | strong_visual_match | Suchergebnisse, Execute | ja |
| gui/navigation/workspace_graph.py | QDialog | dialogs/workspace_graph_dialog.ui | approximated_visual_match | Graph-Visualisierung | ja |
| gui/project_switcher/project_switcher_dialog.py | QDialog | dialogs/project_switcher_dialog.ui | strong_visual_match | Projektlisten, Suche | ja |

---

## B. DOMAIN-SCREENS

| Python-Datei | Widget-Typ / Rolle | .ui-Datei | Abbildungsgrad | Offene dynamische Elemente | Python-Anbindung |
|--------------|--------------------|-----------|----------------|----------------------------|------------------|
| gui/domains/dashboard/dashboard_screen.py | BaseScreen | screens/dashboard_screen.ui | strong_visual_match | Panel-Daten | ja |
| gui/domains/project_hub/project_hub_screen.py | BaseScreen | screens/project_hub_screen.ui | strong_visual_match | Stats, Activity | ja |
| gui/domains/operations/operations_screen.py | BaseScreen | screens/operations_screen.ui | strong_visual_match | Workspace-Stack | ja |
| gui/domains/control_center/control_center_screen.py | BaseScreen | screens/control_center_screen.ui | strong_visual_match | Workspace-Stack | ja |
| gui/domains/qa_governance/qa_governance_screen.py | BaseScreen | screens/qa_governance_screen.ui | strong_visual_match | Workspace-Stack | ja |
| gui/domains/runtime_debug/runtime_debug_screen.py | BaseScreen | screens/runtime_debug_screen.ui | strong_visual_match | Workspace-Stack | ja |
| gui/domains/settings/settings_screen.py | BaseScreen | screens/settings_screen.ui | strong_visual_match | Category-Stack | ja |
| gui/domains/settings/settings_workspace.py | QWidget | screens/settings_workspace.ui | strong_visual_match | Category-Widgets | ja |
| gui/domains/command_center/command_center_view.py | QWidget | screens/command_center_view.ui | approximated_visual_match | View-Inhalte | ja |

---

## C. DASHBOARD-PANELS

| Python-Datei | Widget-Typ / Rolle | .ui-Datei | Abbildungsgrad | Offene dynamische Elemente | Python-Anbindung |
|--------------|--------------------|-----------|----------------|----------------------------|------------------|
| gui/domains/dashboard/panels/active_work_panel.py | BasePanel | panels/active_work_panel.ui | approximated_visual_match | Laufende Aufgaben | ja |
| gui/domains/dashboard/panels/incidents_panel.py | BasePanel | panels/incidents_panel.ui | approximated_visual_match | Incident-Liste | ja |
| gui/domains/dashboard/panels/qa_status_panel.py | BasePanel | panels/qa_status_panel.ui | approximated_visual_match | QA-Status | ja |
| gui/domains/dashboard/panels/system_status_panel.py | BasePanel | panels/system_status_panel.ui | approximated_visual_match | System-Status | ja |

---

## D. OPERATIONS-WORKSPACES

### Chat

| Python-Datei | .ui-Datei | Abbildungsgrad | Python-Anbindung |
|--------------|-----------|----------------|------------------|
| chat/chat_workspace.py | workspaces/chat/chat_workspace.ui | strong_visual_match | ja |
| chat/panels/chat_navigation_panel.py | workspaces/chat/chat_navigation_panel.ui | strong_visual_match | ja |
| chat/panels/conversation_panel.py | workspaces/chat/conversation_panel.ui | strong_visual_match | ja |
| chat/panels/input_panel.py | workspaces/chat/input_panel.ui | strong_visual_match | ja |
| chat/panels/chat_side_panel.py | workspaces/chat/chat_side_panel.ui | approximated_visual_match | ja |
| chat/panels/chat_header_widget.py | workspaces/chat/chat_header_widget.ui | approximated_visual_match | ja |
| chat/panels/chat_context_bar.py | workspaces/chat/chat_context_bar.ui | strong_visual_match | ja |
| chat/panels/chat_details_panel.py | workspaces/chat/chat_details_panel.ui | strong_visual_match | ja |
| chat/panels/topic_editor_dialog.py | dialogs/topic_create_dialog.ui, topic_rename_dialog.ui, topic_delete_confirm_dialog.ui | approximated_visual_match | ja |

### Knowledge

| Python-Datei | .ui-Datei | Abbildungsgrad | Python-Anbindung |
|--------------|-----------|----------------|------------------|
| knowledge/knowledge_workspace.py | workspaces/knowledge/knowledge_workspace.ui | strong_visual_match | ja |
| knowledge/panels/knowledge_navigation_panel.py | workspaces/knowledge/knowledge_navigation_panel.ui | approximated_visual_match | ja |
| knowledge/panels/knowledge_overview_panel.py | workspaces/knowledge/knowledge_overview_panel.ui | strong_visual_match | ja |
| knowledge/panels/knowledge_source_explorer_panel.py | workspaces/knowledge/knowledge_source_explorer_panel.ui | strong_visual_match | ja |
| knowledge/panels/knowledge_sources_panel.py | workspaces/knowledge/knowledge_sources_panel.ui | strong_visual_match | ja |
| knowledge/panels/knowledge_collections_panel.py | workspaces/knowledge/knowledge_collections_panel.ui | strong_visual_match | ja |
| knowledge/panels/knowledge_bases_panel.py | workspaces/knowledge/knowledge_bases_panel.ui | strong_visual_match | ja |
| knowledge/panels/retrieval_status_panel.py | workspaces/knowledge/retrieval_status_panel.ui | strong_visual_match | ja |
| knowledge/panels/retrieval_test_panel.py | workspaces/knowledge/retrieval_test_panel.ui | strong_visual_match | ja |
| knowledge/panels/source_details_panel.py | workspaces/knowledge/source_details_panel.ui | strong_visual_match | ja |
| knowledge/panels/chunk_viewer_panel.py | workspaces/knowledge/chunk_viewer_panel.ui | strong_visual_match | ja |
| knowledge/panels/collection_panel.py | workspaces/knowledge/collection_panel.ui | strong_visual_match | ja |
| knowledge/panels/index_overview_panel.py | workspaces/knowledge/index_overview_panel.ui | strong_visual_match | ja |
| knowledge/panels/index_status_page.py | workspaces/knowledge/index_status_page.ui | strong_visual_match | ja |
| knowledge/panels/collection_dialog.py | dialogs/create_collection_dialog.ui, rename_collection_dialog.ui, assign_sources_dialog.ui | strong_visual_match | ja |

### Projects

| Python-Datei | .ui-Datei | Abbildungsgrad | Python-Anbindung |
|--------------|-----------|----------------|------------------|
| projects/projects_workspace.py | workspaces/projects/projects_workspace.ui | strong_visual_match | ja |
| projects/panels/project_list_panel.py | workspaces/projects/project_list_panel.ui | strong_visual_match | ja |
| projects/panels/project_header_card.py | workspaces/projects/project_header_card.ui | strong_visual_match | ja |
| projects/panels/project_overview_panel.py | workspaces/projects/project_overview_panel.ui | strong_visual_match | ja |
| projects/panels/project_stats_panel.py | workspaces/projects/project_stats_panel.ui | strong_visual_match | ja |
| projects/panels/project_activity_panel.py | workspaces/projects/project_activity_panel.ui | strong_visual_match | ja |
| projects/panels/project_quick_actions_panel.py | workspaces/projects/project_quick_actions_panel.ui | strong_visual_match | ja |
| projects/projects_workspace.NewProjectDialog | dialogs/new_project_dialog.ui | strong_visual_match | ja |

### Prompt Studio

| Python-Datei | .ui-Datei | Abbildungsgrad | Python-Anbindung |
|--------------|-----------|----------------|------------------|
| prompt_studio/prompt_studio_workspace.py | workspaces/prompt_studio/prompt_studio_workspace.ui | strong_visual_match | ja |
| prompt_studio/panels/prompt_navigation_panel.py | workspaces/prompt_studio/prompt_navigation_panel.ui | strong_visual_match | ja |
| prompt_studio/panels/prompt_manager_panel.py | workspaces/prompt_studio/prompt_manager_panel.ui | strong_visual_match | ja |
| prompt_studio/panels/prompt_list_panel.py | workspaces/prompt_studio/prompt_list_panel.ui | strong_visual_match | ja |
| prompt_studio/panels/prompt_editor_panel.py | workspaces/prompt_studio/prompt_editor_panel.ui | strong_visual_match | ja |
| prompt_studio/panels/editor_panel.py | workspaces/prompt_studio/editor_panel.ui | strong_visual_match | ja |
| prompt_studio/panels/preview_panel.py | workspaces/prompt_studio/preview_panel.ui | strong_visual_match | ja |
| prompt_studio/panels/library_panel.py | workspaces/prompt_studio/library_panel.ui | strong_visual_match | ja |
| prompt_studio/panels/prompt_templates_panel.py | workspaces/prompt_studio/prompt_templates_panel.ui | strong_visual_match | ja |
| prompt_studio/panels/prompt_test_lab.py | workspaces/prompt_studio/prompt_test_lab.ui | strong_visual_match | ja |
| – | dialogs/new_prompt_dialog.ui | approximated_visual_match | ja |
| – | dialogs/template_edit_dialog.ui | approximated_visual_match | ja |

### Agent Tasks

| Python-Datei | .ui-Datei | Abbildungsgrad | Python-Anbindung |
|--------------|-----------|----------------|------------------|
| agent_tasks/agent_tasks_workspace.py | workspaces/agent_tasks/agent_tasks_workspace.ui | strong_visual_match | ja |
| agent_tasks/panels/overview_panel.py | workspaces/agent_tasks/overview_panel.ui | strong_visual_match | ja |
| agent_tasks/panels/status_panel.py | workspaces/agent_tasks/status_panel.ui | strong_visual_match | ja |
| agent_tasks/panels/queue_panel.py | workspaces/agent_tasks/queue_panel.ui | strong_visual_match | ja |
| agent_tasks/panels/result_panel.py | workspaces/agent_tasks/result_panel.ui | strong_visual_match | ja |
| agent_tasks/panels/active_agents_panel.py | workspaces/agent_tasks/active_agents_panel.ui | strong_visual_match | ja |
| agent_tasks/panels/agent_registry_panel.py | workspaces/agent_tasks/agent_registry_panel.ui | strong_visual_match | ja |
| agent_tasks/panels/agent_summary_panel.py | workspaces/agent_tasks/agent_summary_panel.ui | strong_visual_match | ja |
| agent_tasks/panels/agent_task_panel.py | workspaces/agent_tasks/agent_task_panel.ui | strong_visual_match | ja |

---

## E. CONTROL CENTER

| Python-Datei | .ui-Datei | Abbildungsgrad | Python-Anbindung |
|--------------|-----------|----------------|------------------|
| control_center_nav.py | workspaces/control_center/control_center_nav.ui | strong_visual_match | ja |
| workspaces/agents_workspace.py | workspaces/control_center/agents_workspace.ui | strong_visual_match | ja |
| workspaces/models_workspace.py | workspaces/control_center/models_workspace.ui | strong_visual_match | ja |
| workspaces/providers_workspace.py | workspaces/control_center/providers_workspace.ui | strong_visual_match | ja |
| workspaces/tools_workspace.py | workspaces/control_center/tools_workspace.ui | strong_visual_match | ja |
| workspaces/data_stores_workspace.py | workspaces/control_center/data_stores_workspace.ui | strong_visual_match | ja |
| agents_ui/agent_manager_panel.py | workspaces/control_center/agent_manager_panel.ui | strong_visual_match | ja |
| agents_ui/agent_profile_panel.py | workspaces/control_center/agent_profile_panel.ui | strong_visual_match | ja |
| agents_ui/agent_list_panel.py | workspaces/control_center/agent_list_panel.ui | strong_visual_match | ja |
| agents_ui/agent_performance_tab.py | workspaces/control_center/agent_performance_tab.ui | strong_visual_match | ja |
| panels/agents_panels.py | workspaces/control_center/agents_panels.ui | approximated_visual_match | ja |
| panels/models_panels.py | workspaces/control_center/models_panels.ui | approximated_visual_match | ja |
| panels/providers_panels.py | workspaces/control_center/providers_panels.ui | approximated_visual_match | ja |
| panels/tools_panels.py | workspaces/control_center/tools_panels.ui | approximated_visual_match | ja |
| panels/data_stores_panels.py | workspaces/control_center/data_stores_panels.ui | approximated_visual_match | ja |
| agents_ui/agent_manager_panel.AgentManagerDialog | dialogs/agent_manager_dialog.ui | strong_visual_match | ja |

---

## F. COMMAND CENTER / QA / GOVERNANCE / RUNTIME

| Python-Datei | .ui-Datei | Abbildungsgrad | Python-Anbindung |
|--------------|-----------|----------------|------------------|
| command_center/audit_operations_view.py | screens/audit_operations_view.ui | approximated_visual_match | ja |
| command_center/governance_view.py | screens/governance_view.ui | approximated_visual_match | ja |
| command_center/incident_operations_view.py | screens/incident_operations_view.ui | approximated_visual_match | ja |
| command_center/qa_drilldown_view.py | screens/qa_drilldown_view.ui | approximated_visual_match | ja |
| command_center/qa_operations_view.py | screens/qa_operations_view.ui | approximated_visual_match | ja |
| command_center/review_operations_view.py | screens/review_operations_view.ui | approximated_visual_match | ja |
| command_center/runtime_debug_view.py | screens/runtime_debug_view.ui | approximated_visual_match | ja |
| command_center/subsystem_detail_view.py | screens/subsystem_detail_view.ui | approximated_visual_match | ja |
| debug/context_inspection_panel.py | panels/context_inspection_panel.ui | approximated_visual_match | ja |
| runtime_debug/panels/agent_debug_panel.py | panels/agent_debug_panel.ui | approximated_visual_match | ja |
| runtime_debug/workspaces/introspection_workspace.py | panels/introspection_workspace.ui | approximated_visual_match | ja |

---

## G. WEITERE DIALOGE

| Python-Datei | .ui-Datei | Abbildungsgrad | Python-Anbindung |
|--------------|-----------|----------------|------------------|
| gui/domains/settings/settings_dialog.py | dialogs/settings_dialog.ui | strong_visual_match | ja |

---

## Nicht sinnvoll in Designer abbildbar (not_representable_in_ui_only)

| Komponente | Grund |
|------------|-------|
| ScreenRegistry, CommandRegistry | Reine Logik, keine UI |
| BreadcrumbManager | State-Management |
| IconManager, IconRegistry | Laufzeit-Icons |
| setup_inspector(), set_content() | Dynamischer Widget-Austausch |
| project_context_changed, navigate_requested | Event-System |
| Kleine Hilfswidgets (chat_list_item, prompt_list_item, etc.) | Geringe visuelle Relevanz |
