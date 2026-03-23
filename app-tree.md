.
├── app
│   ├── agents
│   │   ├── agent_base.py
│   │   ├── agent_factory.py
│   │   ├── agent_profile.py
│   │   ├── agent_registry.py
│   │   ├── agent_repository.py
│   │   ├── agent_router.py
│   │   ├── agent_service.py
│   │   ├── agent_task_runner.py
│   │   ├── capabilities.py
│   │   ├── critic.py
│   │   ├── delegation_engine.py
│   │   ├── departments.py
│   │   ├── execution_engine.py
│   │   ├── __init__.py
│   │   ├── orchestration_service.py
│   │   ├── planner.py
│   │   ├── __pycache__
│   │   │   ├── agent_base.cpython-312.pyc
│   │   │   ├── agent_factory.cpython-312.pyc
│   │   │   ├── agent_profile.cpython-312.pyc
│   │   │   ├── agent_registry.cpython-312.pyc
│   │   │   ├── agent_repository.cpython-312.pyc
│   │   │   ├── agent_router.cpython-312.pyc
│   │   │   ├── agent_service.cpython-312.pyc
│   │   │   ├── agent_task_runner.cpython-312.pyc
│   │   │   ├── capabilities.cpython-312.pyc
│   │   │   ├── critic.cpython-312.pyc
│   │   │   ├── delegation_engine.cpython-312.pyc
│   │   │   ├── departments.cpython-312.pyc
│   │   │   ├── execution_engine.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── orchestration_service.cpython-312.pyc
│   │   │   ├── planner.cpython-312.pyc
│   │   │   ├── research_agent.cpython-312.pyc
│   │   │   ├── research_service.cpython-312.pyc
│   │   │   ├── seed_agents.cpython-312.pyc
│   │   │   ├── task.cpython-312.pyc
│   │   │   ├── task_graph.cpython-312.pyc
│   │   │   └── task_planner.cpython-312.pyc
│   │   ├── research_agent.py
│   │   ├── research_service.py
│   │   ├── seed_agents.py
│   │   ├── task_graph.py
│   │   ├── task_planner.py
│   │   └── task.py
│   ├── commands
│   │   ├── chat_commands.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── chat_commands.cpython-312.pyc
│   │       └── __init__.cpython-312.pyc
│   ├── context
│   │   └── __pycache__
│   │       ├── active_project.cpython-312.pyc
│   │       └── __init__.cpython-312.pyc
│   ├── core
│   │   ├── command_registry.py
│   │   ├── commands
│   │   │   ├── chat_commands.py
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       ├── chat_commands.cpython-312.pyc
│   │   │       └── __init__.cpython-312.pyc
│   │   ├── config
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── settings_backend.cpython-312.pyc
│   │   │   │   └── settings.cpython-312.pyc
│   │   │   ├── settings_backend.py
│   │   │   └── settings.py
│   │   ├── context
│   │   │   ├── active_project.py
│   │   │   ├── __init__.py
│   │   │   ├── project_context_manager.py
│   │   │   └── __pycache__
│   │   │       ├── active_project.cpython-312.pyc
│   │   │       ├── __init__.cpython-312.pyc
│   │   │       └── project_context_manager.cpython-312.pyc
│   │   ├── db
│   │   │   ├── database_manager.py
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       ├── database_manager.cpython-312.pyc
│   │   │       └── __init__.cpython-312.pyc
│   │   ├── __init__.py
│   │   ├── llm
│   │   │   ├── __init__.py
│   │   │   ├── llm_complete.py
│   │   │   ├── llm_output_pipeline.py
│   │   │   ├── llm_response_cleaner.py
│   │   │   ├── llm_response_result.py
│   │   │   ├── llm_retry_policy.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── llm_complete.cpython-312.pyc
│   │   │   │   ├── llm_output_pipeline.cpython-312.pyc
│   │   │   │   ├── llm_response_cleaner.cpython-312.pyc
│   │   │   │   ├── llm_response_result.cpython-312.pyc
│   │   │   │   ├── llm_retry_policy.cpython-312.pyc
│   │   │   │   └── response_filter.cpython-312.pyc
│   │   │   └── response_filter.py
│   │   ├── models
│   │   │   ├── escalation_manager.py
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py
│   │   │   ├── __pycache__
│   │   │   │   ├── escalation_manager.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── orchestrator.cpython-312.pyc
│   │   │   │   ├── registry.cpython-312.pyc
│   │   │   │   ├── roles.cpython-312.pyc
│   │   │   │   └── router.cpython-312.pyc
│   │   │   ├── registry.py
│   │   │   ├── roles.py
│   │   │   └── router.py
│   │   ├── navigation
│   │   │   ├── feature_registry_loader.py
│   │   │   ├── help_topic_resolver.py
│   │   │   ├── icon_ids.py
│   │   │   ├── __init__.py
│   │   │   ├── nav_areas.py
│   │   │   ├── navigation_registry.py
│   │   │   ├── __pycache__
│   │   │   │   ├── feature_registry_loader.cpython-312.pyc
│   │   │   │   ├── help_topic_resolver.cpython-312.pyc
│   │   │   │   ├── icon_ids.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── nav_areas.cpython-312.pyc
│   │   │   │   ├── navigation_registry.cpython-312.pyc
│   │   │   │   └── trace_map_loader.cpython-312.pyc
│   │   │   └── trace_map_loader.py
│   │   └── __pycache__
│   │       ├── command_registry.cpython-312.pyc
│   │       ├── feature_registry_loader.cpython-312.pyc
│   │       ├── __init__.cpython-312.pyc
│   │       └── project_context_manager.cpython-312.pyc
│   ├── critic.py
│   ├── db.py
│   ├── debug
│   │   ├── agent_event.py
│   │   ├── debug_store.py
│   │   ├── emitter.py
│   │   ├── event_bus.py
│   │   ├── gui_log_buffer.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── agent_event.cpython-312.pyc
│   │   │   ├── debug_store.cpython-312.pyc
│   │   │   ├── emitter.cpython-312.pyc
│   │   │   ├── event_bus.cpython-312.pyc
│   │   │   ├── gui_log_buffer.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── qa_artifact_loader.cpython-312.pyc
│   │   │   └── qa_cockpit_panel.cpython-312.pyc
│   │   ├── qa_artifact_loader.py
│   │   └── qa_cockpit_panel.py
│   ├── gui
│   │   ├── bootstrap.py
│   │   ├── breadcrumbs
│   │   │   ├── bar.py
│   │   │   ├── __init__.py
│   │   │   ├── manager.py
│   │   │   ├── model.py
│   │   │   └── __pycache__
│   │   │       ├── bar.cpython-312.pyc
│   │   │       ├── __init__.cpython-312.pyc
│   │   │       ├── manager.cpython-312.pyc
│   │   │       └── model.cpython-312.pyc
│   │   ├── chat_backend.py
│   │   ├── commands
│   │   │   ├── bootstrap.py
│   │   │   ├── __init__.py
│   │   │   ├── model.py
│   │   │   ├── palette_loader.py
│   │   │   ├── palette.py
│   │   │   ├── __pycache__
│   │   │   │   ├── bootstrap.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── model.cpython-312.pyc
│   │   │   │   ├── palette.cpython-312.pyc
│   │   │   │   ├── palette_loader.cpython-312.pyc
│   │   │   │   └── registry.cpython-312.pyc
│   │   │   └── registry.py
│   │   ├── domains
│   │   │   ├── command_center
│   │   │   │   ├── audit_operations_view.py
│   │   │   │   ├── command_center_view.py
│   │   │   │   ├── governance_view.py
│   │   │   │   ├── incident_operations_view.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── __pycache__
│   │   │   │   │   ├── audit_operations_view.cpython-312.pyc
│   │   │   │   │   ├── command_center_view.cpython-312.pyc
│   │   │   │   │   ├── governance_view.cpython-312.pyc
│   │   │   │   │   ├── incident_operations_view.cpython-312.pyc
│   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   ├── qa_drilldown_view.cpython-312.pyc
│   │   │   │   │   ├── qa_operations_view.cpython-312.pyc
│   │   │   │   │   ├── review_operations_view.cpython-312.pyc
│   │   │   │   │   ├── runtime_debug_view.cpython-312.pyc
│   │   │   │   │   └── subsystem_detail_view.cpython-312.pyc
│   │   │   │   ├── qa_drilldown_view.py
│   │   │   │   ├── qa_operations_view.py
│   │   │   │   ├── review_operations_view.py
│   │   │   │   ├── runtime_debug_view.py
│   │   │   │   └── subsystem_detail_view.py
│   │   │   ├── control_center
│   │   │   │   ├── agents_ui
│   │   │   │   │   ├── agent_avatar_widget.py
│   │   │   │   │   ├── agent_form_widgets.py
│   │   │   │   │   ├── agent_list_item.py
│   │   │   │   │   ├── agent_list_panel.py
│   │   │   │   │   ├── agent_manager_panel.py
│   │   │   │   │   ├── agent_performance_tab.py
│   │   │   │   │   ├── agent_profile_panel.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── __pycache__
│   │   │   │   │       ├── agent_avatar_widget.cpython-312.pyc
│   │   │   │   │       ├── agent_form_widgets.cpython-312.pyc
│   │   │   │   │       ├── agent_list_item.cpython-312.pyc
│   │   │   │   │       ├── agent_list_panel.cpython-312.pyc
│   │   │   │   │       ├── agent_manager_panel.cpython-312.pyc
│   │   │   │   │       ├── agent_performance_tab.cpython-312.pyc
│   │   │   │   │       ├── agent_profile_panel.cpython-312.pyc
│   │   │   │   │       └── __init__.cpython-312.pyc
│   │   │   │   ├── control_center_nav.py
│   │   │   │   ├── control_center_screen.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── panels
│   │   │   │   │   ├── agents_panels.py
│   │   │   │   │   ├── data_stores_panels.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── models_panels.py
│   │   │   │   │   ├── providers_panels.py
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   │   ├── agents_panels.cpython-312.pyc
│   │   │   │   │   │   ├── data_stores_panels.cpython-312.pyc
│   │   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   │   ├── models_panels.cpython-312.pyc
│   │   │   │   │   │   ├── providers_panels.cpython-312.pyc
│   │   │   │   │   │   └── tools_panels.cpython-312.pyc
│   │   │   │   │   └── tools_panels.py
│   │   │   │   ├── __pycache__
│   │   │   │   │   ├── control_center_nav.cpython-312.pyc
│   │   │   │   │   ├── control_center_screen.cpython-312.pyc
│   │   │   │   │   └── __init__.cpython-312.pyc
│   │   │   │   └── workspaces
│   │   │   │       ├── agents_workspace.py
│   │   │   │       ├── base_management_workspace.py
│   │   │   │       ├── data_stores_workspace.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── models_workspace.py
│   │   │   │       ├── providers_workspace.py
│   │   │   │       ├── __pycache__
│   │   │   │       │   ├── agents_workspace.cpython-312.pyc
│   │   │   │       │   ├── base_management_workspace.cpython-312.pyc
│   │   │   │       │   ├── data_stores_workspace.cpython-312.pyc
│   │   │   │       │   ├── __init__.cpython-312.pyc
│   │   │   │       │   ├── models_workspace.cpython-312.pyc
│   │   │   │       │   ├── providers_workspace.cpython-312.pyc
│   │   │   │       │   └── tools_workspace.cpython-312.pyc
│   │   │   │       └── tools_workspace.py
│   │   │   ├── dashboard
│   │   │   │   ├── dashboard_screen.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── panels
│   │   │   │   │   ├── active_work_panel.py
│   │   │   │   │   ├── incidents_panel.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   │   ├── active_work_panel.cpython-312.pyc
│   │   │   │   │   │   ├── incidents_panel.cpython-312.pyc
│   │   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   │   ├── qa_status_panel.cpython-312.pyc
│   │   │   │   │   │   └── system_status_panel.cpython-312.pyc
│   │   │   │   │   ├── qa_status_panel.py
│   │   │   │   │   └── system_status_panel.py
│   │   │   │   └── __pycache__
│   │   │   │       ├── dashboard_screen.cpython-312.pyc
│   │   │   │       └── __init__.cpython-312.pyc
│   │   │   ├── __init__.py
│   │   │   ├── operations
│   │   │   │   ├── agent_tasks
│   │   │   │   │   ├── agent_tasks_workspace.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── panels
│   │   │   │   │   │   ├── active_agents_panel.py
│   │   │   │   │   │   ├── agent_registry_panel.py
│   │   │   │   │   │   ├── agent_summary_panel.py
│   │   │   │   │   │   ├── agent_task_panel.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── overview_panel.py
│   │   │   │   │   │   ├── __pycache__
│   │   │   │   │   │   │   ├── active_agents_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── agent_registry_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── agent_summary_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── agent_task_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   │   │   ├── overview_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── queue_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── result_panel.cpython-312.pyc
│   │   │   │   │   │   │   └── status_panel.cpython-312.pyc
│   │   │   │   │   │   ├── queue_panel.py
│   │   │   │   │   │   ├── result_panel.py
│   │   │   │   │   │   └── status_panel.py
│   │   │   │   │   └── __pycache__
│   │   │   │   │       ├── agent_tasks_workspace.cpython-312.pyc
│   │   │   │   │       └── __init__.cpython-312.pyc
│   │   │   │   ├── chat
│   │   │   │   │   ├── chat_workspace.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── panels
│   │   │   │   │   │   ├── chat_composer_widget.py
│   │   │   │   │   │   ├── chat_details_panel.py
│   │   │   │   │   │   ├── chat_header_widget.py
│   │   │   │   │   │   ├── chat_item_context_menu.py
│   │   │   │   │   │   ├── chat_list_item.py
│   │   │   │   │   │   ├── chat_message_widget.py
│   │   │   │   │   │   ├── chat_navigation_panel.py
│   │   │   │   │   │   ├── chat_side_panel.py
│   │   │   │   │   │   ├── chat_topic_section.py
│   │   │   │   │   │   ├── conversation_panel.py
│   │   │   │   │   │   ├── conversation_view.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── input_panel.py
│   │   │   │   │   │   ├── __pycache__
│   │   │   │   │   │   │   ├── chat_composer_widget.cpython-312.pyc
│   │   │   │   │   │   │   ├── chat_details_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── chat_header_widget.cpython-312.pyc
│   │   │   │   │   │   │   ├── chat_item_context_menu.cpython-312.pyc
│   │   │   │   │   │   │   ├── chat_list_item.cpython-312.pyc
│   │   │   │   │   │   │   ├── chat_message_widget.cpython-312.pyc
│   │   │   │   │   │   │   ├── chat_navigation_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── chat_side_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── chat_topic_section.cpython-312.pyc
│   │   │   │   │   │   │   ├── conversation_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── conversation_view.cpython-312.pyc
│   │   │   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   │   │   ├── input_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── session_explorer_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── topic_actions.cpython-312.pyc
│   │   │   │   │   │   │   └── topic_editor_dialog.cpython-312.pyc
│   │   │   │   │   │   ├── topic_actions.py
│   │   │   │   │   │   └── topic_editor_dialog.py
│   │   │   │   │   └── __pycache__
│   │   │   │   │       ├── chat_workspace.cpython-312.pyc
│   │   │   │   │       └── __init__.cpython-312.pyc
│   │   │   │   ├── __init__.py
│   │   │   │   ├── knowledge
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── knowledge_workspace.py
│   │   │   │   │   ├── panels
│   │   │   │   │   │   ├── chunk_viewer_panel.py
│   │   │   │   │   │   ├── collection_dialog.py
│   │   │   │   │   │   ├── collection_panel.py
│   │   │   │   │   │   ├── index_overview_panel.py
│   │   │   │   │   │   ├── index_status_page.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── knowledge_bases_panel.py
│   │   │   │   │   │   ├── knowledge_collections_panel.py
│   │   │   │   │   │   ├── knowledge_navigation_panel.py
│   │   │   │   │   │   ├── knowledge_overview_panel.py
│   │   │   │   │   │   ├── knowledge_source_explorer_panel.py
│   │   │   │   │   │   ├── knowledge_sources_panel.py
│   │   │   │   │   │   ├── __pycache__
│   │   │   │   │   │   │   ├── chunk_viewer_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── collection_dialog.cpython-312.pyc
│   │   │   │   │   │   │   ├── collection_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── index_overview_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── index_status_page.cpython-312.pyc
│   │   │   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   │   │   ├── knowledge_bases_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── knowledge_collections_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── knowledge_navigation_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── knowledge_overview_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── knowledge_source_explorer_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── knowledge_sources_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── retrieval_status_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── retrieval_test_panel.cpython-312.pyc
│   │   │   │   │   │   │   ├── source_details_panel.cpython-312.pyc
│   │   │   │   │   │   │   └── source_list_item.cpython-312.pyc
│   │   │   │   │   │   ├── retrieval_status_panel.py
│   │   │   │   │   │   ├── retrieval_test_panel.py
│   │   │   │   │   │   ├── source_details_panel.py
│   │   │   │   │   │   └── source_list_item.py
│   │   │   │   │   └── __pycache__
│   │   │   │   │       ├── __init__.cpython-312.pyc
│   │   │   │   │       └── knowledge_workspace.cpython-312.pyc
│   │   │   │   ├── operations_context.py
│   │   │   │   ├── operations_nav.py
│   │   │   │   ├── operations_screen.py
│   │   │   │   ├── projects
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── panels
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── project_activity_panel.py
│   │   │   │   │   │   ├── project_header_card.py
│   │   │   │   │   │   ├── project_list_panel.py
│   │   │   │   │   │   ├── project_overview_panel.py
│   │   │   │   │   │   ├── project_quick_actions_panel.py
│   │   │   │   │   │   ├── project_stats_panel.py
│   │   │   │   │   │   └── __pycache__
│   │   │   │   │   │       ├── __init__.cpython-312.pyc
│   │   │   │   │   │       ├── project_activity_panel.cpython-312.pyc
│   │   │   │   │   │       ├── project_header_card.cpython-312.pyc
│   │   │   │   │   │       ├── project_list_panel.cpython-312.pyc
│   │   │   │   │   │       ├── project_overview_panel.cpython-312.pyc
│   │   │   │   │   │       ├── project_quick_actions_panel.cpython-312.pyc
│   │   │   │   │   │       └── project_stats_panel.cpython-312.pyc
│   │   │   │   │   ├── projects_workspace.py
│   │   │   │   │   └── __pycache__
│   │   │   │   │       ├── __init__.cpython-312.pyc
│   │   │   │   │       └── projects_workspace.cpython-312.pyc
│   │   │   │   ├── prompt_studio
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── panels
│   │   │   │   │   │   ├── editor_panel.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── library_panel.py
│   │   │   │   │   │   ├── preview_panel.py
│   │   │   │   │   │   ├── prompt_editor_panel.py
│   │   │   │   │   │   ├── prompt_list_item.py
│   │   │   │   │   │   ├── prompt_list_panel.py
│   │   │   │   │   │   ├── prompt_manager_panel.py
│   │   │   │   │   │   ├── prompt_navigation_panel.py
│   │   │   │   │   │   ├── prompt_templates_panel.py
│   │   │   │   │   │   ├── prompt_test_lab.py
│   │   │   │   │   │   ├── prompt_version_panel.py
│   │   │   │   │   │   └── __pycache__
│   │   │   │   │   │       ├── editor_panel.cpython-312.pyc
│   │   │   │   │   │       ├── __init__.cpython-312.pyc
│   │   │   │   │   │       ├── library_panel.cpython-312.pyc
│   │   │   │   │   │       ├── preview_panel.cpython-312.pyc
│   │   │   │   │   │       ├── prompt_editor_panel.cpython-312.pyc
│   │   │   │   │   │       ├── prompt_list_item.cpython-312.pyc
│   │   │   │   │   │       ├── prompt_list_panel.cpython-312.pyc
│   │   │   │   │   │       ├── prompt_manager_panel.cpython-312.pyc
│   │   │   │   │   │       ├── prompt_navigation_panel.cpython-312.pyc
│   │   │   │   │   │       ├── prompt_templates_panel.cpython-312.pyc
│   │   │   │   │   │       ├── prompt_test_lab.cpython-312.pyc
│   │   │   │   │   │       └── prompt_version_panel.cpython-312.pyc
│   │   │   │   │   ├── prompt_studio_workspace.py
│   │   │   │   │   └── __pycache__
│   │   │   │   │       ├── __init__.cpython-312.pyc
│   │   │   │   │       └── prompt_studio_workspace.cpython-312.pyc
│   │   │   │   └── __pycache__
│   │   │   │       ├── __init__.cpython-312.pyc
│   │   │   │       ├── operations_context.cpython-312.pyc
│   │   │   │       ├── operations_nav.cpython-312.pyc
│   │   │   │       └── operations_screen.cpython-312.pyc
│   │   │   ├── project_hub
│   │   │   │   ├── __init__.py
│   │   │   │   ├── project_hub_page.py
│   │   │   │   ├── project_hub_screen.py
│   │   │   │   └── __pycache__
│   │   │   │       ├── __init__.cpython-312.pyc
│   │   │   │       ├── project_hub_page.cpython-312.pyc
│   │   │   │       └── project_hub_screen.cpython-312.pyc
│   │   │   ├── __pycache__
│   │   │   │   └── __init__.cpython-312.pyc
│   │   │   ├── qa_governance
│   │   │   │   ├── __init__.py
│   │   │   │   ├── panels
│   │   │   │   │   ├── coverage_map_panels.py
│   │   │   │   │   ├── gap_analysis_panels.py
│   │   │   │   │   ├── incidents_panels.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   │   ├── coverage_map_panels.cpython-312.pyc
│   │   │   │   │   │   ├── gap_analysis_panels.cpython-312.pyc
│   │   │   │   │   │   ├── incidents_panels.cpython-312.pyc
│   │   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   │   ├── replay_lab_panels.cpython-312.pyc
│   │   │   │   │   │   ├── test_inventory_panels.cpython-312.pyc
│   │   │   │   │   │   └── test_inventory_panels.cpython-312-pytest-9.0.2.pyc
│   │   │   │   │   ├── replay_lab_panels.py
│   │   │   │   │   └── test_inventory_panels.py
│   │   │   │   ├── __pycache__
│   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   ├── qa_governance_nav.cpython-312.pyc
│   │   │   │   │   └── qa_governance_screen.cpython-312.pyc
│   │   │   │   ├── qa_governance_nav.py
│   │   │   │   ├── qa_governance_screen.py
│   │   │   │   └── workspaces
│   │   │   │       ├── base_analysis_workspace.py
│   │   │   │       ├── coverage_map_workspace.py
│   │   │   │       ├── gap_analysis_workspace.py
│   │   │   │       ├── incidents_workspace.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── __pycache__
│   │   │   │       │   ├── base_analysis_workspace.cpython-312.pyc
│   │   │   │       │   ├── coverage_map_workspace.cpython-312.pyc
│   │   │   │       │   ├── gap_analysis_workspace.cpython-312.pyc
│   │   │   │       │   ├── incidents_workspace.cpython-312.pyc
│   │   │   │       │   ├── __init__.cpython-312.pyc
│   │   │   │       │   ├── replay_lab_workspace.cpython-312.pyc
│   │   │   │       │   ├── test_inventory_workspace.cpython-312.pyc
│   │   │   │       │   └── test_inventory_workspace.cpython-312-pytest-9.0.2.pyc
│   │   │   │       ├── replay_lab_workspace.py
│   │   │   │       └── test_inventory_workspace.py
│   │   │   ├── runtime_debug
│   │   │   │   ├── __init__.py
│   │   │   │   ├── panels
│   │   │   │   │   ├── activity_detail_panel.py
│   │   │   │   │   ├── agent_activity_panels.py
│   │   │   │   │   ├── agent_activity_stream_panel.py
│   │   │   │   │   ├── agent_activity_view.py
│   │   │   │   │   ├── agent_debug_panel.py
│   │   │   │   │   ├── agent_status_panel.py
│   │   │   │   │   ├── eventbus_panels.py
│   │   │   │   │   ├── event_timeline_view.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── llm_calls_panels.py
│   │   │   │   │   ├── logs_panels.py
│   │   │   │   │   ├── metrics_panels.py
│   │   │   │   │   ├── model_usage_view.py
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   │   ├── activity_detail_panel.cpython-312.pyc
│   │   │   │   │   │   ├── agent_activity_panels.cpython-312.pyc
│   │   │   │   │   │   ├── agent_activity_stream_panel.cpython-312.pyc
│   │   │   │   │   │   ├── agent_activity_view.cpython-312.pyc
│   │   │   │   │   │   ├── agent_debug_panel.cpython-312.pyc
│   │   │   │   │   │   ├── agent_status_panel.cpython-312.pyc
│   │   │   │   │   │   ├── eventbus_panels.cpython-312.pyc
│   │   │   │   │   │   ├── event_timeline_view.cpython-312.pyc
│   │   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   │   ├── llm_calls_panels.cpython-312.pyc
│   │   │   │   │   │   ├── logs_panels.cpython-312.pyc
│   │   │   │   │   │   ├── metrics_panels.cpython-312.pyc
│   │   │   │   │   │   ├── model_usage_view.cpython-312.pyc
│   │   │   │   │   │   ├── qa_observability_panel.cpython-312.pyc
│   │   │   │   │   │   ├── system_graph_panels.cpython-312.pyc
│   │   │   │   │   │   ├── task_graph_view.cpython-312.pyc
│   │   │   │   │   │   └── tool_execution_view.cpython-312.pyc
│   │   │   │   │   ├── qa_observability_panel.py
│   │   │   │   │   ├── system_graph_panels.py
│   │   │   │   │   ├── task_graph_view.py
│   │   │   │   │   └── tool_execution_view.py
│   │   │   │   ├── __pycache__
│   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   ├── runtime_debug_nav.cpython-312.pyc
│   │   │   │   │   └── runtime_debug_screen.cpython-312.pyc
│   │   │   │   ├── runtime_debug_nav.py
│   │   │   │   ├── runtime_debug_screen.py
│   │   │   │   └── workspaces
│   │   │   │       ├── agent_activity_workspace.py
│   │   │   │       ├── base_monitoring_workspace.py
│   │   │   │       ├── eventbus_workspace.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── introspection_workspace.py
│   │   │   │       ├── llm_calls_workspace.py
│   │   │   │       ├── logs_workspace.py
│   │   │   │       ├── metrics_workspace.py
│   │   │   │       ├── __pycache__
│   │   │   │       │   ├── agent_activity_workspace.cpython-312.pyc
│   │   │   │       │   ├── base_monitoring_workspace.cpython-312.pyc
│   │   │   │       │   ├── eventbus_workspace.cpython-312.pyc
│   │   │   │       │   ├── __init__.cpython-312.pyc
│   │   │   │       │   ├── introspection_workspace.cpython-312.pyc
│   │   │   │       │   ├── llm_calls_workspace.cpython-312.pyc
│   │   │   │       │   ├── logs_workspace.cpython-312.pyc
│   │   │   │       │   ├── metrics_workspace.cpython-312.pyc
│   │   │   │       │   ├── qa_cockpit_workspace.cpython-312.pyc
│   │   │   │       │   ├── qa_observability_workspace.cpython-312.pyc
│   │   │   │       │   └── system_graph_workspace.cpython-312.pyc
│   │   │   │       ├── qa_cockpit_workspace.py
│   │   │   │       ├── qa_observability_workspace.py
│   │   │   │       └── system_graph_workspace.py
│   │   │   └── settings
│   │   │       ├── categories
│   │   │       │   ├── advanced_category.py
│   │   │       │   ├── ai_models_category.py
│   │   │       │   ├── appearance_category.py
│   │   │       │   ├── application_category.py
│   │   │       │   ├── base_category.py
│   │   │       │   ├── data_category.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── privacy_category.py
│   │   │       │   ├── project_category.py
│   │   │       │   ├── __pycache__
│   │   │       │   │   ├── advanced_category.cpython-312.pyc
│   │   │       │   │   ├── ai_models_category.cpython-312.pyc
│   │   │       │   │   ├── appearance_category.cpython-312.pyc
│   │   │       │   │   ├── application_category.cpython-312.pyc
│   │   │       │   │   ├── base_category.cpython-312.pyc
│   │   │       │   │   ├── data_category.cpython-312.pyc
│   │   │       │   │   ├── __init__.cpython-312.pyc
│   │   │       │   │   ├── privacy_category.cpython-312.pyc
│   │   │       │   │   ├── project_category.cpython-312.pyc
│   │   │       │   │   └── workspace_category.cpython-312.pyc
│   │   │       │   └── workspace_category.py
│   │   │       ├── __init__.py
│   │   │       ├── navigation.py
│   │   │       ├── panels
│   │   │       │   ├── __init__.py
│   │   │       │   ├── model_settings_panel.py
│   │   │       │   ├── __pycache__
│   │   │       │   │   ├── __init__.cpython-312.pyc
│   │   │       │   │   ├── model_settings_panel.cpython-312.pyc
│   │   │       │   │   └── theme_selection_panel.cpython-312.pyc
│   │   │       │   └── theme_selection_panel.py
│   │   │       ├── __pycache__
│   │   │       │   ├── __init__.cpython-312.pyc
│   │   │       │   ├── navigation.cpython-312.pyc
│   │   │       │   ├── settings_dialog.cpython-312.pyc
│   │   │       │   ├── settings_nav.cpython-312.pyc
│   │   │       │   ├── settings_screen.cpython-312.pyc
│   │   │       │   └── settings_workspace.cpython-312.pyc
│   │   │       ├── settings_dialog.py
│   │   │       ├── settings_screen.py
│   │   │       ├── settings_workspace.py
│   │   │       └── workspaces
│   │   │           ├── advanced_workspace.py
│   │   │           ├── agents_workspace.py
│   │   │           ├── appearance_workspace.py
│   │   │           ├── base_settings_workspace.py
│   │   │           ├── __init__.py
│   │   │           ├── models_workspace.py
│   │   │           ├── __pycache__
│   │   │           │   ├── advanced_workspace.cpython-312.pyc
│   │   │           │   ├── agents_workspace.cpython-312.pyc
│   │   │           │   ├── appearance_workspace.cpython-312.pyc
│   │   │           │   ├── base_settings_workspace.cpython-312.pyc
│   │   │           │   ├── __init__.cpython-312.pyc
│   │   │           │   ├── models_workspace.cpython-312.pyc
│   │   │           │   └── system_workspace.cpython-312.pyc
│   │   │           └── system_workspace.py
│   │   ├── events
│   │   │   ├── __init__.py
│   │   │   ├── project_events.py
│   │   │   └── __pycache__
│   │   │       ├── __init__.cpython-312.pyc
│   │   │       └── project_events.cpython-312.pyc
│   │   ├── icons
│   │   │   ├── __init__.py
│   │   │   ├── manager.py
│   │   │   ├── nav_mapping.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── manager.cpython-312.pyc
│   │   │   │   ├── nav_mapping.cpython-312.pyc
│   │   │   │   └── registry.cpython-312.pyc
│   │   │   └── registry.py
│   │   ├── __init__.py
│   │   ├── inspector
│   │   │   ├── advanced_settings_inspector.py
│   │   │   ├── agent_inspector.py
│   │   │   ├── agents_settings_inspector.py
│   │   │   ├── agent_tasks_inspector.py
│   │   │   ├── appearance_inspector.py
│   │   │   ├── chat_context_inspector.py
│   │   │   ├── coverage_inspector.py
│   │   │   ├── data_store_inspector.py
│   │   │   ├── event_inspector.py
│   │   │   ├── gap_inspector.py
│   │   │   ├── incident_inspector.py
│   │   │   ├── __init__.py
│   │   │   ├── inspector_host.py
│   │   │   ├── knowledge_inspector.py
│   │   │   ├── llm_call_inspector.py
│   │   │   ├── log_inspector.py
│   │   │   ├── metrics_inspector.py
│   │   │   ├── model_inspector.py
│   │   │   ├── models_settings_inspector.py
│   │   │   ├── project_context_inspector.py
│   │   │   ├── prompt_studio_inspector.py
│   │   │   ├── provider_inspector.py
│   │   │   ├── __pycache__
│   │   │   │   ├── advanced_settings_inspector.cpython-312.pyc
│   │   │   │   ├── agent_inspector.cpython-312.pyc
│   │   │   │   ├── agents_settings_inspector.cpython-312.pyc
│   │   │   │   ├── agent_tasks_inspector.cpython-312.pyc
│   │   │   │   ├── appearance_inspector.cpython-312.pyc
│   │   │   │   ├── chat_context_inspector.cpython-312.pyc
│   │   │   │   ├── coverage_inspector.cpython-312.pyc
│   │   │   │   ├── data_store_inspector.cpython-312.pyc
│   │   │   │   ├── event_inspector.cpython-312.pyc
│   │   │   │   ├── gap_inspector.cpython-312.pyc
│   │   │   │   ├── incident_inspector.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── inspector_host.cpython-312.pyc
│   │   │   │   ├── knowledge_inspector.cpython-312.pyc
│   │   │   │   ├── llm_call_inspector.cpython-312.pyc
│   │   │   │   ├── log_inspector.cpython-312.pyc
│   │   │   │   ├── metrics_inspector.cpython-312.pyc
│   │   │   │   ├── model_inspector.cpython-312.pyc
│   │   │   │   ├── models_settings_inspector.cpython-312.pyc
│   │   │   │   ├── project_context_inspector.cpython-312.pyc
│   │   │   │   ├── prompt_studio_inspector.cpython-312.pyc
│   │   │   │   ├── provider_inspector.cpython-312.pyc
│   │   │   │   ├── replay_inspector.cpython-312.pyc
│   │   │   │   ├── runtime_agent_inspector.cpython-312.pyc
│   │   │   │   ├── system_node_inspector.cpython-312.pyc
│   │   │   │   ├── system_settings_inspector.cpython-312.pyc
│   │   │   │   ├── test_inspector.cpython-312.pyc
│   │   │   │   ├── test_inspector.cpython-312-pytest-9.0.2.pyc
│   │   │   │   └── tool_inspector.cpython-312.pyc
│   │   │   ├── replay_inspector.py
│   │   │   ├── runtime_agent_inspector.py
│   │   │   ├── system_node_inspector.py
│   │   │   ├── system_settings_inspector.py
│   │   │   ├── test_inspector.py
│   │   │   └── tool_inspector.py
│   │   ├── knowledge_backend.py
│   │   ├── legacy
│   │   │   ├── chat_widget.py
│   │   │   ├── file_explorer_widget.py
│   │   │   ├── __init__.py
│   │   │   ├── message_widget.py
│   │   │   ├── project_chat_list_widget.py
│   │   │   ├── __pycache__
│   │   │   │   ├── chat_widget.cpython-312.pyc
│   │   │   │   ├── file_explorer_widget.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── message_widget.cpython-312.pyc
│   │   │   │   ├── project_chat_list_widget.cpython-312.pyc
│   │   │   │   └── sidebar_widget.cpython-312.pyc
│   │   │   └── sidebar_widget.py
│   │   ├── monitors
│   │   │   ├── agent_activity_monitor.py
│   │   │   ├── bottom_panel_host.py
│   │   │   ├── events_monitor.py
│   │   │   ├── __init__.py
│   │   │   ├── llm_trace_monitor.py
│   │   │   ├── logs_monitor.py
│   │   │   ├── metrics_monitor.py
│   │   │   └── __pycache__
│   │   │       ├── agent_activity_monitor.cpython-312.pyc
│   │   │       ├── bottom_panel_host.cpython-312.pyc
│   │   │       ├── events_monitor.cpython-312.pyc
│   │   │       ├── __init__.cpython-312.pyc
│   │   │       ├── llm_trace_monitor.cpython-312.pyc
│   │   │       ├── logs_monitor.cpython-312.pyc
│   │   │       └── metrics_monitor.cpython-312.pyc
│   │   ├── navigation
│   │   │   ├── command_palette.py
│   │   │   ├── __init__.py
│   │   │   ├── nav_areas.py
│   │   │   ├── __pycache__
│   │   │   │   ├── command_palette.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── nav_areas.cpython-312.pyc
│   │   │   │   ├── sidebar_config.cpython-312.pyc
│   │   │   │   ├── sidebar.cpython-312.pyc
│   │   │   │   ├── workspace_graph.cpython-312.pyc
│   │   │   │   └── workspace_graph_resolver.cpython-312.pyc
│   │   │   ├── sidebar_config.py
│   │   │   ├── sidebar.py
│   │   │   ├── workspace_graph.py
│   │   │   └── workspace_graph_resolver.py
│   │   ├── project_switcher
│   │   │   ├── __init__.py
│   │   │   ├── project_switcher_button.py
│   │   │   ├── project_switcher_dialog.py
│   │   │   └── __pycache__
│   │   │       ├── __init__.cpython-312.pyc
│   │   │       ├── project_switcher_button.cpython-312.pyc
│   │   │       └── project_switcher_dialog.cpython-312.pyc
│   │   ├── __pycache__
│   │   │   ├── bootstrap.cpython-312.pyc
│   │   │   ├── chat_backend.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── knowledge_backend.cpython-312.pyc
│   │   │   └── qsettings_backend.cpython-312.pyc
│   │   ├── qsettings_backend.py
│   │   ├── shared
│   │   │   ├── base_operations_workspace.py
│   │   │   ├── base_panel.py
│   │   │   ├── base_screen.py
│   │   │   ├── __init__.py
│   │   │   ├── layout_constants.py
│   │   │   ├── panel_constants.py
│   │   │   ├── __pycache__
│   │   │   │   ├── base_operations_workspace.cpython-312.pyc
│   │   │   │   ├── base_panel.cpython-312.pyc
│   │   │   │   ├── base_screen.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── layout_constants.cpython-312.pyc
│   │   │   │   ├── panel_constants.cpython-312.pyc
│   │   │   │   └── shell_styles.cpython-312.pyc
│   │   │   └── shell_styles.py
│   │   ├── shell
│   │   │   ├── docking_config.py
│   │   │   ├── __init__.py
│   │   │   ├── layout_constants.py
│   │   │   ├── main_window.py
│   │   │   ├── __pycache__
│   │   │   │   ├── docking_config.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── layout_constants.cpython-312.pyc
│   │   │   │   ├── main_window.cpython-312.pyc
│   │   │   │   └── top_bar.cpython-312.pyc
│   │   │   └── top_bar.py
│   │   ├── themes
│   │   │   ├── base
│   │   │   │   ├── base.qss
│   │   │   │   └── shell.qss
│   │   │   ├── definition.py
│   │   │   ├── __init__.py
│   │   │   ├── loader.py
│   │   │   ├── manager.py
│   │   │   ├── __pycache__
│   │   │   │   ├── definition.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── loader.cpython-312.pyc
│   │   │   │   ├── manager.cpython-312.pyc
│   │   │   │   ├── registry.cpython-312.pyc
│   │   │   │   └── tokens.cpython-312.pyc
│   │   │   ├── registry.py
│   │   │   └── tokens.py
│   │   ├── widgets
│   │   │   ├── empty_state_widget.py
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       ├── empty_state_widget.cpython-312.pyc
│   │   │       └── __init__.cpython-312.pyc
│   │   └── workspace
│   │       ├── __init__.py
│   │       ├── __pycache__
│   │       │   ├── __init__.cpython-312.pyc
│   │       │   ├── screen_registry.cpython-312.pyc
│   │       │   └── workspace_host.cpython-312.pyc
│   │       ├── screen_registry.py
│   │       └── workspace_host.py
│   ├── help
│   │   ├── doc_generator.py
│   │   ├── guided_tour.py
│   │   ├── help_index.py
│   │   ├── help_window.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── doc_generator.cpython-312.pyc
│   │   │   ├── guided_tour.cpython-312.pyc
│   │   │   ├── help_index.cpython-312.pyc
│   │   │   ├── help_window.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── tooltip_helper.cpython-312.pyc
│   │   └── tooltip_helper.py
│   ├── __init__.py
│   ├── llm
│   │   ├── __init__.py
│   │   ├── llm_complete.py
│   │   ├── llm_output_pipeline.py
│   │   ├── llm_response_cleaner.py
│   │   ├── llm_response_result.py
│   │   ├── llm_retry_policy.py
│   │   └── __pycache__
│   │       ├── __init__.cpython-312.pyc
│   │       ├── llm_complete.cpython-312.pyc
│   │       ├── llm_output_pipeline.cpython-312.pyc
│   │       ├── llm_response_cleaner.cpython-312.pyc
│   │       ├── llm_response_result.cpython-312.pyc
│   │       └── llm_retry_policy.cpython-312.pyc
│   ├── __main__.py
│   ├── main.py
│   ├── metrics
│   │   ├── agent_metrics.py
│   │   ├── __init__.py
│   │   ├── metrics_collector.py
│   │   ├── metrics_service.py
│   │   ├── metrics_store.py
│   │   └── __pycache__
│   │       ├── agent_metrics.cpython-312.pyc
│   │       ├── __init__.cpython-312.pyc
│   │       ├── metrics_collector.cpython-312.pyc
│   │       ├── metrics_service.cpython-312.pyc
│   │       └── metrics_store.cpython-312.pyc
│   ├── models
│   ├── ollama_client.py
│   ├── prompts
│   │   ├── __init__.py
│   │   ├── prompt_models.py
│   │   ├── prompt_repository.py
│   │   ├── prompt_service.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── prompt_models.cpython-312.pyc
│   │   │   ├── prompt_repository.cpython-312.pyc
│   │   │   ├── prompt_service.cpython-312.pyc
│   │   │   └── storage_backend.cpython-312.pyc
│   │   └── storage_backend.py
│   ├── providers
│   │   ├── base_provider.py
│   │   ├── cloud_ollama_provider.py
│   │   ├── __init__.py
│   │   ├── local_ollama_provider.py
│   │   ├── ollama_client.py
│   │   └── __pycache__
│   │       ├── base_provider.cpython-312.pyc
│   │       ├── cloud_ollama_provider.cpython-312.pyc
│   │       ├── __init__.cpython-312.pyc
│   │       ├── local_ollama_provider.cpython-312.pyc
│   │       └── ollama_client.cpython-312.pyc
│   ├── __pycache__
│   │   ├── chat_widget.cpython-312.pyc
│   │   ├── db.cpython-312.pyc
│   │   ├── escalation_manager.cpython-312.pyc
│   │   ├── file_explorer_widget.cpython-312.pyc
│   │   ├── __init__.cpython-312.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── __main__.cpython-312.pyc
│   │   ├── main.cpython-312.pyc
│   │   ├── main.cpython-313.pyc
│   │   ├── message_widget.cpython-312.pyc
│   │   ├── model_orchestrator.cpython-312.pyc
│   │   ├── model_registry.cpython-312.pyc
│   │   ├── model_roles.cpython-312.pyc
│   │   ├── model_router.cpython-312.pyc
│   │   ├── ollama_client.cpython-312.pyc
│   │   ├── project_chat_list_widget.cpython-312.pyc
│   │   ├── resources_rc.cpython-312.pyc
│   │   ├── settings.cpython-312.pyc
│   │   ├── sidebar_widget.cpython-312.pyc
│   │   ├── tools.cpython-312.pyc
│   │   └── web_search.cpython-312.pyc
│   ├── qa
│   │   ├── dashboard_adapter.py
│   │   ├── drilldown_models.py
│   │   ├── __init__.py
│   │   ├── operations_adapter.py
│   │   ├── operations_models.py
│   │   └── __pycache__
│   │       ├── dashboard_adapter.cpython-312.pyc
│   │       ├── drilldown_models.cpython-312.pyc
│   │       ├── __init__.cpython-312.pyc
│   │       ├── operations_adapter.cpython-312.pyc
│   │       └── operations_models.cpython-312.pyc
│   ├── rag
│   │   ├── chunker.py
│   │   ├── context_builder.py
│   │   ├── document_loader.py
│   │   ├── embedding_service.py
│   │   ├── __init__.py
│   │   ├── knowledge_extractor.py
│   │   ├── knowledge_models.py
│   │   ├── knowledge_space.py
│   │   ├── knowledge_updater.py
│   │   ├── knowledge_validator.py
│   │   ├── models.py
│   │   ├── __pycache__
│   │   │   ├── chunker.cpython-312.pyc
│   │   │   ├── context_builder.cpython-312.pyc
│   │   │   ├── document_loader.cpython-312.pyc
│   │   │   ├── embedding_service.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── knowledge_extractor.cpython-312.pyc
│   │   │   ├── knowledge_models.cpython-312.pyc
│   │   │   ├── knowledge_space.cpython-312.pyc
│   │   │   ├── knowledge_updater.cpython-312.pyc
│   │   │   ├── knowledge_validator.cpython-312.pyc
│   │   │   ├── models.cpython-312.pyc
│   │   │   ├── rag_pipeline.cpython-312.pyc
│   │   │   ├── retriever.cpython-312.pyc
│   │   │   ├── service.cpython-312.pyc
│   │   │   └── vector_store.cpython-312.pyc
│   │   ├── rag_pipeline.py
│   │   ├── retriever.py
│   │   ├── service.py
│   │   └── vector_store.py
│   ├── resources
│   │   ├── dark.qss
│   │   ├── icons
│   │   │   ├── add_chat.svg
│   │   │   ├── delete.svg
│   │   │   ├── help.svg
│   │   │   ├── info.svg
│   │   │   ├── model.svg
│   │   │   ├── new_project.svg
│   │   │   ├── new.svg
│   │   │   ├── remove_chat.svg
│   │   │   ├── rename.svg
│   │   │   ├── save.svg
│   │   │   ├── search.svg
│   │   │   ├── send.svg
│   │   │   └── settings.svg
│   │   ├── light.qss
│   │   ├── __pycache__
│   │   │   └── styles.cpython-312.pyc
│   │   └── styles.py
│   ├── resources.qrc
│   ├── resources_rc.py
│   ├── runtime
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── gui_log_buffer.cpython-312.pyc
│   │       └── __init__.cpython-312.pyc
│   ├── services
│   │   ├── agent_service.py
│   │   ├── chat_service.py
│   │   ├── infrastructure.py
│   │   ├── __init__.py
│   │   ├── knowledge_service.py
│   │   ├── model_service.py
│   │   ├── project_service.py
│   │   ├── provider_service.py
│   │   ├── __pycache__
│   │   │   ├── agent_service.cpython-312.pyc
│   │   │   ├── chat_service.cpython-312.pyc
│   │   │   ├── infrastructure.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── knowledge_service.cpython-312.pyc
│   │   │   ├── model_service.cpython-312.pyc
│   │   │   ├── project_service.cpython-312.pyc
│   │   │   ├── provider_service.cpython-312.pyc
│   │   │   ├── qa_governance_service.cpython-312.pyc
│   │   │   ├── result.cpython-312.pyc
│   │   │   └── topic_service.cpython-312.pyc
│   │   ├── qa_governance_service.py
│   │   ├── result.py
│   │   └── topic_service.py
│   ├── tools
│   │   ├── filesystem.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── filesystem.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── web_search.cpython-312.pyc
│   │   └── web_search.py
│   └── utils
│       ├── datetime_utils.py
│       ├── env_loader.py
│       ├── __init__.py
│       ├── paths.py
│       └── __pycache__
│           ├── datetime_utils.cpython-312.pyc
│           ├── env_loader.cpython-312.pyc
│           ├── __init__.cpython-312.pyc
│           └── paths.cpython-312.pyc
├── app-tree.md
├── archive
│   ├── deprecated_docs
│   │   ├── CUTOVER_LEGACY.md
│   │   ├── CUTOVER_SUMMARY.md
│   │   ├── GUI_CUTOVER.md
│   │   ├── GUI_MIGRATION_ROADMAP.md
│   │   └── GUI_MIGRATION_SPRINTS.md
│   ├── README.md
│   └── run_legacy_gui.py
├── assets
│   ├── icons
│   │   ├── actions
│   │   │   ├── add.svg
│   │   │   ├── edit.svg
│   │   │   ├── filter.svg
│   │   │   ├── refresh.svg
│   │   │   ├── remove.svg
│   │   │   ├── run.svg
│   │   │   ├── search.svg
│   │   │   └── stop.svg
│   │   ├── add_chat.svg
│   │   ├── delete.svg
│   │   ├── help.svg
│   │   ├── info.svg
│   │   ├── model.svg
│   │   ├── new_project.svg
│   │   ├── new.svg
│   │   ├── remove_chat.svg
│   │   ├── rename.svg
│   │   ├── runtime
│   │   │   ├── agent_activity.svg
│   │   │   ├── eventbus.svg
│   │   │   ├── llm_calls.svg
│   │   │   ├── logs.svg
│   │   │   ├── metrics.svg
│   │   │   └── system_graph.svg
│   │   ├── save.svg
│   │   ├── search.svg
│   │   ├── send.svg
│   │   ├── settings.svg
│   │   ├── status
│   │   │   ├── error.svg
│   │   │   ├── idle.svg
│   │   │   ├── paused.svg
│   │   │   ├── running.svg
│   │   │   ├── success.svg
│   │   │   └── warning.svg
│   │   └── svg
│   │       ├── actions
│   │       │   ├── add.svg
│   │       │   ├── edit.svg
│   │       │   ├── filter.svg
│   │       │   ├── refresh.svg
│   │       │   ├── remove.svg
│   │       │   ├── run.svg
│   │       │   ├── search.svg
│   │       │   └── stop.svg
│   │       ├── navigation
│   │       │   ├── activity.svg
│   │       │   ├── chat.svg
│   │       │   ├── control.svg
│   │       │   ├── dashboard.svg
│   │       │   ├── gear.svg
│   │       │   └── shield.svg
│   │       ├── panels
│   │       │   ├── advanced.svg
│   │       │   ├── agents.svg
│   │       │   ├── appearance.svg
│   │       │   ├── coverage_map.svg
│   │       │   ├── data_stores.svg
│   │       │   ├── gap_analysis.svg
│   │       │   ├── incidents.svg
│   │       │   ├── knowledge.svg
│   │       │   ├── models.svg
│   │       │   ├── projects.svg
│   │       │   ├── prompt_studio.svg
│   │       │   ├── providers.svg
│   │       │   ├── replay_lab.svg
│   │       │   ├── system.svg
│   │       │   ├── test_inventory.svg
│   │       │   └── tools.svg
│   │       ├── runtime
│   │       │   ├── agent_activity.svg
│   │       │   ├── eventbus.svg
│   │       │   ├── llm_calls.svg
│   │       │   ├── logs.svg
│   │       │   ├── metrics.svg
│   │       │   └── system_graph.svg
│   │       └── status
│   │           ├── error.svg
│   │           ├── idle.svg
│   │           ├── paused.svg
│   │           ├── running.svg
│   │           ├── success.svg
│   │           └── warning.svg
│   ├── media
│   └── themes
│       ├── base
│       │   ├── base.qss
│       │   └── shell.qss
│       └── legacy
│           ├── dark.qss
│           └── light.qss
├── AUDIT_REPORT.md
├── chat_history.db
├── design_system.json
├── docs
│   ├── 00_map_of_the_system.md
│   ├── 01_product_overview
│   │   ├── architecture.md
│   │   ├── introduction.md
│   │   ├── README.md
│   │   └── UX_CONCEPT.md
│   ├── 02_user_manual
│   │   ├── agents.md
│   │   ├── ai_studio.md
│   │   ├── media_generation.md
│   │   ├── models.md
│   │   ├── prompts.md
│   │   ├── rag.md
│   │   ├── README.md
│   │   ├── settings.md
│   │   ├── tools.md
│   │   └── workflows.md
│   ├── 03_feature_reference
│   │   ├── CHAT_WORKSPACE.md
│   │   ├── KNOWLEDGE_WORKSPACE.md
│   │   ├── PROJECT_HUB_IMPLEMENTATION.md
│   │   ├── PROJECT_SWITCHER_AND_OVERVIEW.md
│   │   └── README.md
│   ├── 04_architecture
│   │   ├── AGENTS_UI_ARCHITECTURE_AUDIT.md
│   │   ├── AGENTS_UI_PHASE1_MIGRATION_REPORT.md
│   │   ├── AGENTS_UI_PHASE1_VALIDATION.md
│   │   ├── AGENTS_UI_PHASE2_ANALYSIS.md
│   │   ├── AGENTS_UI_PHASE2_EXECUTION.md
│   │   ├── AGENTS_UI_PHASE3_STABILIZATION.md
│   │   ├── APP_CORE_DECOUPLING_PLAN.md
│   │   ├── APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md
│   │   ├── APP_MOVE_MATRIX.md
│   │   ├── APP_PACKAGE_ARCHITECTURE_ASSESSMENT.md
│   │   ├── APP_REFACTOR_EXECUTION_REPORT.md
│   │   ├── APP_TARGET_PACKAGE_ARCHITECTURE.md
│   │   ├── APP_UI_TO_GUI_TRANSITION_PLAN.md
│   │   ├── ARCHITECTURE_BASELINE_2026.md
│   │   ├── ARCHITECTURE_BASELINE_2026_REPORT.md
│   │   ├── ARCHITECTURE_DRIFT_RADAR_ANALYSIS.md
│   │   ├── ARCHITECTURE_DRIFT_RADAR.json
│   │   ├── ARCHITECTURE_DRIFT_RADAR_POLICY.md
│   │   ├── ARCHITECTURE_DRIFT_RADAR_REPORT.md
│   │   ├── ARCHITECTURE_DRIFT_RADAR_STATUS.md
│   │   ├── ARCHITECTURE_GUARD_RULES.md
│   │   ├── BREADCRUMB_NAVIGATION.md
│   │   ├── CHAT_UI_PHASE1_ANALYSIS.md
│   │   ├── CHAT_UI_PHASE2_MIGRATION_REPORT.md
│   │   ├── CHAT_UI_PHASE3_MIGRATION_REPORT.md
│   │   ├── CHAT_UI_PHASE4_SIDEPANEL_REPORT.md
│   │   ├── COMMAND_CENTER_ARCHITECTURE.md
│   │   ├── COMMAND_PALETTE.md
│   │   ├── CONTROL_CENTER_ARCHITECTURE.md
│   │   ├── DESIGN_SYSTEM_LIGHT.md
│   │   ├── DOCS_ARCHITECTURE_PATH_DECISION.md
│   │   ├── EVENTBUS_GOVERNANCE_ANALYSIS.md
│   │   ├── EVENTBUS_GOVERNANCE_POLICY.md
│   │   ├── EVENTBUS_GOVERNANCE_REPORT.md
│   │   ├── FEATURE_GOVERNANCE_AUDIT.md
│   │   ├── FEATURE_GOVERNANCE_GUARDS_REPORT.md
│   │   ├── FEATURE_GOVERNANCE_POLICY.md
│   │   ├── FULL_SYSTEM_CHECKUP_ANALYSIS.md
│   │   ├── FULL_SYSTEM_CHECKUP.json
│   │   ├── FULL_SYSTEM_CHECKUP_REPORT.md
│   │   ├── FULL_SYSTEM_GOVERNANCE_MATRIX.md
│   │   ├── FULL_SYSTEM_RESTPOINT_REMEDIATION_REPORT.md
│   │   ├── GUI_ARCHITECTURE_GUARDRAILS.md
│   │   ├── GUI_DOMAIN_DEPENDENCY_AUDIT.md
│   │   ├── GUI_DOMAIN_DEPENDENCY_GUARDS_REPORT.md
│   │   ├── GUI_DOMAIN_DEPENDENCY_POLICY.md
│   │   ├── GUI_GOVERNANCE_AUDIT.md
│   │   ├── GUI_GOVERNANCE_GUARDS_REPORT.md
│   │   ├── GUI_GOVERNANCE_POLICY.md
│   │   ├── GUI_REPOSITORY_ARCHITECTURE.md
│   │   ├── ICON_SYSTEM.md
│   │   ├── LEGACY_MAIN_GOVERNANCE.md
│   │   ├── LLM_MODULE_STRUCTURE.md
│   │   ├── META_NAVIGATION_ARCHITECTURE.md
│   │   ├── PROMPT_STUDIO_CONSOLIDATION_REPORT.md
│   │   ├── PROVIDER_ORCHESTRATOR_GOVERNANCE_ANALYSIS.md
│   │   ├── PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md
│   │   ├── PROVIDER_ORCHESTRATOR_GOVERNANCE_REPORT.md
│   │   ├── PYSIDE6_UI_ARCHITECTURE.md
│   │   ├── QA_GOVERNANCE_ARCHITECTURE.md
│   │   ├── RAG_ARCHITEKTUR.md
│   │   ├── README.md
│   │   ├── REGISTRY_GOVERNANCE_ANALYSIS.md
│   │   ├── REGISTRY_GOVERNANCE_POLICY.md
│   │   ├── REGISTRY_GOVERNANCE_REPORT.md
│   │   ├── ROOT_CLEANUP_SPRINT_REPORT.md
│   │   ├── RUNTIME_DEBUG_ARCHITECTURE.md
│   │   ├── SCREEN_CLASS_ARCHITECTURE.md
│   │   ├── SERVICE_GOVERNANCE_AUDIT.md
│   │   ├── SERVICE_GOVERNANCE_GUARDS_REPORT.md
│   │   ├── SERVICE_GOVERNANCE_POLICY.md
│   │   ├── SERVICE_LAYER_ARCHITECTURE.md
│   │   ├── SETTINGS_ARCHITECTURE.md
│   │   ├── SETTINGS_BACKEND_DEPENDENCY_INVERSION_REPORT.md
│   │   ├── SETTINGS_CONSOLIDATION_REPORT.md
│   │   ├── SIDEPANEL_SUBTREE_ANALYSIS.md
│   │   ├── SIDEPANEL_SUBTREE_PHASEA_MIGRATION_REPORT.md
│   │   ├── SIDEPANEL_SUBTREE_PHASEB_MIGRATION_REPORT.md
│   │   ├── SIDEPANEL_SUBTREE_PHASEC_MIGRATION_REPORT.md
│   │   ├── STARTUP_GOVERNANCE_POLICY.md
│   │   ├── STARTUP_GOVERNANCE_REPORT.md
│   │   ├── THEME_ARCHITECTURE.md
│   │   ├── TOOLS_GOVERNANCE_DECISION.md
│   │   ├── TOPIC_STRUCTURE.md
│   │   ├── UI_COMPATIBILITY_CLEANUP_AUDIT.md
│   │   ├── UI_COMPATIBILITY_CLEANUP_EXECUTION_REPORT.md
│   │   ├── UI_MANUAL_REVIEW_FINAL_CLEANUP_REPORT.md
│   │   └── WORKSPACE_IMPLEMENTATION_PLAN.md
│   ├── 05_developer_guide
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   ├── MODELS_PROVIDERS_IMPLEMENTATION.md
│   │   ├── PHASE1_CHANGES.md
│   │   ├── PROMPT_STUDIO_IMPLEMENTATION.md
│   │   ├── QA_GOVERNANCE_IMPLEMENTATION.md
│   │   ├── README.md
│   │   └── RUNTIME_DEBUG_IMPLEMENTATION.md
│   ├── 06_operations_and_qa
│   │   ├── ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md
│   │   ├── CHAT_DELETE_BUG_FIX.md
│   │   ├── CHAT_GLOBAL_MODE.md
│   │   ├── CHAT_LIST_PROJECT_UX.md
│   │   ├── CONSOLIDATION_REPORT.md
│   │   ├── CONSOLIDATION_RULES.md
│   │   ├── DOCS_HELP_IMPLEMENTATION_REPORT.md
│   │   ├── HEADER_BUTTONS_UX.md
│   │   ├── INTROSPECTION_PANEL_IMPLEMENTATION.md
│   │   ├── KNOWLEDGE_SOURCE_EXPLORER_UX.md
│   │   ├── LAYOUT_RESIZE_AUDIT.md
│   │   ├── README.md
│   │   ├── SETTINGS_UX_AUDIT.md
│   │   ├── UX_ACCEPTANCE_REVIEW_PHASE1.md
│   │   ├── UX_ACCEPTANCE_REVIEW_REPORT.md
│   │   ├── UX_BREAK_IT_TEST_PHASE2.md
│   │   ├── UX_BUG_FIXES_PHASE3.md
│   │   ├── UX_DEFECTS_BEHAVIOR_AUDIT_2026-03-16.md
│   │   ├── UX_DEFECTS_BEHAVIOR_AUDIT_2_2026-03-16.md
│   │   ├── UX_DEFECTS_BEHAVIOR_TEST.md
│   │   ├── UX_DEFECTS_FINAL_KILL_SWEEP_2026-03-16.md
│   │   ├── UX_DEFECTS_MANUAL_TESTING.md
│   │   ├── UX_EMPTY_STATE_IMPLEMENTATION.md
│   │   ├── UX_FIXES_IMPLEMENTATION_SUMMARY.md
│   │   ├── UX_QA_VALIDATION_PHASE4.md
│   │   ├── UX_RELEASE_READINESS_REPORT.md
│   │   ├── UX_RELEASE_READINESS_REPORT_PHASE5.md
│   │   ├── UX_STABILIZATION_IMPLEMENTATION_LOG.md
│   │   ├── UX_STABILIZATION_PLAN.md
│   │   ├── UX_VISUAL_HIERARCHY_IMPLEMENTATION.md
│   │   └── WORKSPACE_GRAPH_IMPLEMENTATION.md
│   ├── 07_troubleshooting
│   │   └── README.md
│   ├── 08_glossary
│   │   └── README.md
│   ├── architecture
│   │   ├── FULL_SYSTEM_RESTPOINT_REMEDIATION_REPORT.md
│   │   └── README.md
│   ├── FEATURE_REGISTRY.md
│   ├── qa
│   │   ├── 00_map_of_qa_system.md
│   │   ├── architecture
│   │   │   ├── AGENT_UI_ARCHITECTURE_EVALUATION.md
│   │   │   ├── autopilot
│   │   │   │   ├── QA_AUTOPILOT_V2_ARCHITECTURE.md
│   │   │   │   ├── QA_AUTOPILOT_V2_PILOT_CONSTELLATIONS.md
│   │   │   │   └── QA_AUTOPILOT_V3_ARCHITECTURE.md
│   │   │   ├── COMMAND_CENTER_DASHBOARD_UNIFICATION.md
│   │   │   ├── coverage
│   │   │   │   ├── QA_COVERAGE_MAP_ARCHITECTURE.md
│   │   │   │   └── QA_COVERAGE_MAP_GENERATOR.md
│   │   │   ├── graphs
│   │   │   │   ├── QA_ARCHITECTURE_GRAPH.dot
│   │   │   │   ├── QA_ARCHITECTURE_GRAPH.md
│   │   │   │   ├── QA_ARCHITECTURE_GRAPH.mmd
│   │   │   │   ├── QA_ARCHITECTURE_GRAPH.svg
│   │   │   │   ├── QA_DEPENDENCY_GRAPH.dot
│   │   │   │   ├── QA_DEPENDENCY_GRAPH.md
│   │   │   │   ├── QA_DEPENDENCY_GRAPH.mmd
│   │   │   │   └── QA_DEPENDENCY_GRAPH.svg
│   │   │   ├── incident_replay
│   │   │   │   ├── QA_INCIDENT_INTEGRATION.md
│   │   │   │   ├── QA_INCIDENT_REPLAY_ARCHITECTURE.md
│   │   │   │   └── QA_INCIDENT_REPLAY_INTEGRATION.md
│   │   │   ├── inventory
│   │   │   │   ├── QA_TEST_INVENTORY_ARCHITECTURE.md
│   │   │   │   └── QA_TEST_INVENTORY_README.md
│   │   │   └── README.md
│   │   ├── artifacts
│   │   │   ├── csv
│   │   │   │   └── QA_HEATMAP.csv
│   │   │   ├── dashboards
│   │   │   │   ├── PHASE3_GAP_REPORT.md
│   │   │   │   ├── QA_ANOMALY_DETECTION.md
│   │   │   │   ├── QA_AUTOPILOT.md
│   │   │   │   ├── QA_CONTROL_CENTER.md
│   │   │   │   ├── QA_EVOLUTION_MAP.md
│   │   │   │   ├── QA_HEATMAP.md
│   │   │   │   ├── QA_LEVEL3_COVERAGE_MAP.md
│   │   │   │   ├── QA_PRIORITY_SCORE.md
│   │   │   │   ├── QA_RISK_RADAR.md
│   │   │   │   ├── QA_SELF_HEALING.md
│   │   │   │   ├── QA_STABILITY_INDEX.md
│   │   │   │   └── QA_STATUS.md
│   │   │   ├── json
│   │   │   │   ├── FEEDBACK_LOOP_REPORT.json
│   │   │   │   ├── PHASE3_GAP_REPORT.json
│   │   │   │   ├── QA_ANOMALY_DETECTION.json
│   │   │   │   ├── QA_AUTOPILOT.json
│   │   │   │   ├── QA_AUTOPILOT_V2.json
│   │   │   │   ├── QA_AUTOPILOT_V3.json
│   │   │   │   ├── QA_CONTROL_CENTER.json
│   │   │   │   ├── QA_COVERAGE_MAP.json
│   │   │   │   ├── QA_HEATMAP.json
│   │   │   │   ├── QA_KNOWLEDGE_GRAPH.json
│   │   │   │   ├── QA_PRIORITY_SCORE.json
│   │   │   │   ├── QA_RISK_RADAR.json
│   │   │   │   ├── QA_SELF_HEALING.json
│   │   │   │   ├── QA_STABILITY_HISTORY.json
│   │   │   │   ├── QA_STABILITY_INDEX.json
│   │   │   │   ├── QA_STATUS.json
│   │   │   │   ├── QA_TEST_INVENTORY.json
│   │   │   │   └── QA_TEST_STRATEGY.json
│   │   │   └── README.md
│   │   ├── config
│   │   │   ├── phase3_ci_build_order.md
│   │   │   ├── phase3_ci_config.json
│   │   │   ├── phase3_failure_class_hints.json
│   │   │   ├── phase3_gap_prioritization.json
│   │   │   ├── phase3_guard_type_overrides.json
│   │   │   ├── phase3_orphan_governance.json
│   │   │   └── README.md
│   │   ├── feedback_loop
│   │   │   ├── autopilot_v3_trace.json
│   │   │   ├── control_center_feedback_trace.json
│   │   │   ├── knowledge_graph_trace.json
│   │   │   ├── priority_score_feedback_trace.json
│   │   │   ├── README.md
│   │   │   ├── risk_radar_feedback_trace.json
│   │   │   └── test_strategy_trace.json
│   │   ├── governance
│   │   │   ├── ARCHITECTURE_DRIFT_SENTINELS.md
│   │   │   ├── CI_TEST_LEVELS.md
│   │   │   ├── incident_schemas
│   │   │   │   ├── BINDINGS_JSON_FIELD_STANDARD.md
│   │   │   │   ├── bindings.schema.json
│   │   │   │   ├── incident.schema.yaml
│   │   │   │   ├── INCIDENT_YAML_FIELD_STANDARD.md
│   │   │   │   ├── QA_INCIDENT_ANALYTICS.md
│   │   │   │   ├── QA_INCIDENT_ARTIFACT_STANDARD.md
│   │   │   │   ├── QA_INCIDENT_LIFECYCLE.md
│   │   │   │   ├── QA_INCIDENT_REGISTRY.md
│   │   │   │   ├── QA_INCIDENT_REPLAY_LIFECYCLE.md
│   │   │   │   ├── QA_INCIDENT_REPLAY_SCHEMA.json
│   │   │   │   ├── QA_INCIDENT_SCHEMA.md
│   │   │   │   ├── QA_INCIDENT_SCRIPTS_ARCHITECTURE.md
│   │   │   │   ├── QA_REPLAY_SCHEMA.md
│   │   │   │   ├── QA_VALIDATION_STANDARD.md
│   │   │   │   ├── replay.schema.yaml
│   │   │   │   └── REPLAY_YAML_FIELD_STANDARD.md
│   │   │   ├── README.md
│   │   │   ├── REGRESSION_CATALOG.md
│   │   │   ├── schemas
│   │   │   │   ├── qa_coverage_map.schema.json
│   │   │   │   ├── qa_test_inventory.schema.json
│   │   │   │   └── README.md
│   │   │   └── TEST_GOVERNANCE_RULES.md
│   │   ├── history
│   │   │   ├── phase3
│   │   │   │   ├── PHASE3_CI_INTEGRATION_PLAN.md
│   │   │   │   ├── PHASE3_GAP_PRIORITIZATION.md
│   │   │   │   ├── PHASE3_IMPLEMENTATION_REPORT.md
│   │   │   │   ├── PHASE3_ORPHAN_REVIEW_GOVERNANCE.md
│   │   │   │   ├── PHASE3_REPLAY_BINDING_ARCHITECTURE.md
│   │   │   │   ├── PHASE3_RESTRISIKEN_REPORT.md
│   │   │   │   ├── PHASE3_SEMANTIC_ENRICHMENT_PLAN.md
│   │   │   │   ├── PHASE3_SUMMARY.md
│   │   │   │   ├── PHASE3_TECHNICAL_DOCS.md
│   │   │   │   └── PHASE3_VERIFICATION_REVIEW.md
│   │   │   ├── QA_DOCUMENTATION_STRUCTURE_PROPOSAL.md
│   │   │   └── README.md
│   │   ├── incidents
│   │   │   ├── analytics.json
│   │   │   ├── INC-20260315-001
│   │   │   │   ├── bindings.json
│   │   │   │   └── incident.yaml
│   │   │   ├── INC-20260315-002
│   │   │   │   ├── bindings.json
│   │   │   │   └── incident.yaml
│   │   │   ├── index.json
│   │   │   ├── QA_INCIDENT_PILOT_ITERATION.md
│   │   │   └── templates
│   │   │       ├── bindings.template.json
│   │   │       ├── incident.template.yaml
│   │   │       ├── notes.template.md
│   │   │       ├── README.md
│   │   │       └── replay.template.yaml
│   │   ├── plans
│   │   │   ├── CHAOS_QA_PLAN.md
│   │   │   ├── QA_AUTOPILOT_V3_SANIERUNGSPLAN.md
│   │   │   └── README.md
│   │   ├── README.md
│   │   ├── reports
│   │   │   ├── QA_AUTOPILOT_V3_ARCHITECTURE_REVIEW.md
│   │   │   ├── QA_AUTOPILOT_V3_CHANGE_SUMMARY.md
│   │   │   ├── QA_AUTOPILOT_V3_FINAL_RELEASE_CHECK.md
│   │   │   ├── QA_AUTOPILOT_V3_GOVERNANCE_REVIEW.md
│   │   │   ├── QA_AUTOPILOT_V3_VERIFICATION_REPORT.md
│   │   │   ├── QA_COCKPIT_ITERATION2_REPORT.md
│   │   │   ├── QA_COVERAGE_MAP_MAPPING_RULES.md
│   │   │   ├── QA_COVERAGE_MAP_PHASE2_PROMPTS.md
│   │   │   ├── QA_COVERAGE_MAP_REVIEW.md
│   │   │   ├── QA_LEVEL3_REPORT.md
│   │   │   ├── QA_RISK_RADAR_ITERATION1_REPORT.md
│   │   │   ├── QA_TEST_INVENTORY_MAPPING_RULES.md
│   │   │   ├── QA_TEST_INVENTORY_REVIEW.md
│   │   │   ├── README.md
│   │   │   └── UX_DEFECTS_QA_GAP_ANALYSIS.md
│   │   └── RESTRUCTURING_IMPLEMENTATION_REPORT.md
│   ├── README.md
│   ├── refactoring
│   │   ├── COMMAND_CENTER_UI_TO_GUI_ANALYSIS.md
│   │   ├── COMMAND_CENTER_UI_TO_GUI_MIGRATION_REPORT.md
│   │   ├── GUI_POST_MIGRATION_AUDIT.md
│   │   ├── GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md
│   │   ├── KNOWLEDGE_UI_TO_GUI_ANALYSIS.md
│   │   ├── KNOWLEDGE_UI_TO_GUI_MIGRATION_REPORT.md
│   │   ├── PROJECT_UI_TO_GUI_ANALYSIS.md
│   │   ├── PROJECT_UI_TO_GUI_MIGRATION_REPORT.md
│   │   ├── PROMPTS_UI_TO_GUI_ANALYSIS.md
│   │   ├── PROMPTS_UI_TO_GUI_MIGRATION_REPORT.md
│   │   ├── SETTINGS_UI_TO_GUI_ANALYSIS.md
│   │   ├── SETTINGS_UI_TO_GUI_MIGRATION_REPORT.md
│   │   ├── UI_LEGACY_FINAL_AUDIT.md
│   │   └── UI_LEGACY_FINAL_CLEANUP_REPORT.md
│   ├── SYSTEM_MAP.md
│   └── TRACE_MAP.md
├── examples
│   └── rag_example.py
├── help
│   ├── control_center
│   │   ├── cc_data_stores.md
│   │   ├── cc_models.md
│   │   ├── cc_providers.md
│   │   ├── cc_tools.md
│   │   ├── control_center_agents.md
│   │   └── control_center_overview.md
│   ├── getting_started
│   │   └── introduction.md
│   ├── operations
│   │   ├── agents_overview.md
│   │   ├── chat_overview.md
│   │   ├── knowledge_overview.md
│   │   ├── projects_overview.md
│   │   └── prompt_studio_overview.md
│   ├── qa_governance
│   │   └── qa_overview.md
│   ├── runtime_debug
│   │   └── runtime_overview.md
│   ├── settings
│   │   ├── settings_overview.md
│   │   ├── settings_prompts.md
│   │   └── settings_rag.md
│   └── troubleshooting
│       └── troubleshooting.md
├── install-desktop.sh
├── linux-desktop-chat.desktop
├── main.py
├── __pycache__
│   ├── main.cpython-312.pyc
│   └── run_gui_shell.cpython-312.pyc
├── pytest.ini
├── requirements.txt
├── run_gui_shell.py
├── scripts
│   ├── architecture
│   │   ├── architecture_drift_radar.py
│   │   └── __init__.py
│   ├── index_rag.py
│   └── qa
│       ├── analyze_incidents.py
│       ├── autopilot_v3
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   ├── models.py
│       │   ├── projections.py
│       │   ├── __pycache__
│       │   │   ├── __init__.cpython-312.pyc
│       │   │   ├── loader.cpython-312.pyc
│       │   │   ├── models.cpython-312.pyc
│       │   │   ├── projections.cpython-312.pyc
│       │   │   ├── rules.cpython-312.pyc
│       │   │   └── traces.cpython-312.pyc
│       │   ├── rules.py
│       │   └── traces.py
│       ├── build_coverage_map.py
│       ├── build_test_inventory.py
│       ├── checks.py
│       ├── coverage_map_loader.py
│       ├── coverage_map_rules.py
│       ├── enrich_replay_binding.py
│       ├── feedback_loop
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   ├── models.py
│       │   ├── normalizer.py
│       │   ├── projections.py
│       │   ├── __pycache__
│       │   │   ├── __init__.cpython-312.pyc
│       │   │   ├── loader.cpython-312.pyc
│       │   │   ├── models.cpython-312.pyc
│       │   │   ├── normalizer.cpython-312.pyc
│       │   │   ├── projections.cpython-312.pyc
│       │   │   ├── rules.cpython-312.pyc
│       │   │   ├── thresholds.cpython-312.pyc
│       │   │   ├── traces.cpython-312.pyc
│       │   │   └── utils.cpython-312.pyc
│       │   ├── README.md
│       │   ├── rules.py
│       │   ├── thresholds.py
│       │   ├── traces.py
│       │   └── utils.py
│       ├── gap_prioritization.py
│       ├── generate_autopilot_v2.py
│       ├── generate_autopilot_v3.py
│       ├── generate_gap_report.py
│       ├── generate_knowledge_graph.py
│       ├── generate_qa_anomaly_detection.py
│       ├── generate_qa_autopilot.py
│       ├── generate_qa_control_center.py
│       ├── generate_qa_dependency_graph.py
│       ├── generate_qa_graph.py
│       ├── generate_qa_heatmap.py
│       ├── generate_qa_priority_score.py
│       ├── generate_qa_self_healing.py
│       ├── generate_qa_stability_index.py
│       ├── incidents
│       │   ├── analyze_incidents.py
│       │   ├── build_registry.py
│       │   ├── __init__.py
│       │   └── validate_incident.py
│       ├── __init__.py
│       ├── knowledge_graph
│       │   ├── builder.py
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   ├── models.py
│       │   ├── __pycache__
│       │   │   ├── builder.cpython-312.pyc
│       │   │   ├── __init__.cpython-312.pyc
│       │   │   ├── loader.cpython-312.pyc
│       │   │   ├── models.cpython-312.pyc
│       │   │   ├── rules.cpython-312.pyc
│       │   │   ├── serializer.cpython-312.pyc
│       │   │   └── utils.cpython-312.pyc
│       │   ├── rules.py
│       │   ├── serializer.py
│       │   └── utils.py
│       ├── __pycache__
│       │   ├── checks.cpython-312.pyc
│       │   ├── coverage_map_loader.cpython-312.pyc
│       │   ├── coverage_map_rules.cpython-312.pyc
│       │   ├── enrich_replay_binding.cpython-312.pyc
│       │   ├── gap_prioritization.cpython-312.pyc
│       │   ├── __init__.cpython-312.pyc
│       │   ├── qa_paths.cpython-312.pyc
│       │   ├── semantic_enrichment.cpython-312.pyc
│       │   ├── test_inventory_models.cpython-312.pyc
│       │   ├── test_inventory_rules.cpython-312.pyc
│       │   └── test_inventory_rules.cpython-312-pytest-9.0.2.pyc
│       ├── qa_cockpit.py
│       ├── qa_paths.py
│       ├── run_feedback_loop.py
│       ├── semantic_enrichment.py
│       ├── test_inventory_models.py
│       ├── test_inventory_rules.py
│       ├── test_strategy
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   ├── models.py
│       │   ├── projections.py
│       │   ├── __pycache__
│       │   │   ├── __init__.cpython-312.pyc
│       │   │   ├── loader.cpython-312.pyc
│       │   │   ├── models.cpython-312.pyc
│       │   │   ├── projections.cpython-312.pyc
│       │   │   ├── rules.cpython-312.pyc
│       │   │   ├── traces.cpython-312.pyc
│       │   │   └── utils.cpython-312.pyc
│       │   ├── rules.py
│       │   ├── traces.py
│       │   └── utils.py
│       ├── update_control_center.py
│       ├── update_priority_scores.py
│       ├── update_risk_radar.py
│       └── update_test_strategy.py
├── SIDEBAR_IMPLEMENTATION.md
├── src
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc
│   │   └── run.cpython-312.pyc
│   └── run.py
├── start.sh
├── static
│   ├── css
│   │   ├── admin.css
│   │   ├── backoffice.css
│   │   ├── styles.css
│   │   └── variants.css
│   ├── img
│   └── js
│       ├── app.js
│       ├── variants.js
│       └── vendor
├── test_projects_chats.db
├── test_projects.db
├── tests
│   ├── architecture
│   │   ├── arch_guard_config.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── arch_guard_config.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_app_package_guards.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_architecture_drift_radar.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_eventbus_governance_guards.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_feature_governance_guards.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_gui_does_not_import_ui.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_gui_domain_dependency_guards.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_gui_governance_guards.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_provider_orchestrator_governance_guards.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_registry_governance_guards.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_service_governance_guards.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_startup_governance_guards.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_app_package_guards.py
│   │   ├── test_architecture_drift_radar.py
│   │   ├── test_eventbus_governance_guards.py
│   │   ├── test_feature_governance_guards.py
│   │   ├── test_gui_does_not_import_ui.py
│   │   ├── test_gui_domain_dependency_guards.py
│   │   ├── test_gui_governance_guards.py
│   │   ├── test_provider_orchestrator_governance_guards.py
│   │   ├── test_registry_governance_guards.py
│   │   ├── test_service_governance_guards.py
│   │   └── test_startup_governance_guards.py
│   ├── async_behavior
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_agent_change_during_stream.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chatwidget_signal_after_destroy.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_debug_clear_during_refresh.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_rag_concurrent_retrieval.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_shutdown_during_task.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_signal_after_widget_destroy.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_agent_change_during_stream.py
│   │   ├── test_chatwidget_signal_after_destroy.py
│   │   ├── test_debug_clear_during_refresh.py
│   │   ├── test_rag_concurrent_retrieval.py
│   │   ├── test_shutdown_during_task.py
│   │   └── test_signal_after_widget_destroy.py
│   ├── AUDIT_MATRIX.md
│   ├── behavior
│   │   ├── __pycache__
│   │   │   ├── ux_behavior_simulation.cpython-312-pytest-9.0.2.pyc
│   │   │   └── ux_regression_tests.cpython-312-pytest-9.0.2.pyc
│   │   ├── ux_behavior_simulation.py
│   │   └── ux_regression_tests.py
│   ├── chaos
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_embedding_service_unreachable.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_persistence_failure_after_success.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_provider_timeout_chat.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_startup_partial_services.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_embedding_service_unreachable.py
│   │   ├── test_persistence_failure_after_success.py
│   │   ├── test_provider_timeout_chat.py
│   │   └── test_startup_partial_services.py
│   ├── conftest.py
│   ├── contracts
│   │   ├── event_type_registry.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── event_type_registry.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_agent_profile_contract.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chat_event_contract.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_debug_event_contract.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_llm_stream_contract.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_ollama_response_contract.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_prompt_contract.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_rag_retrieval_contract.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_tool_result_contract.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_agent_profile_contract.py
│   │   ├── test_chat_event_contract.py
│   │   ├── test_debug_event_contract.py
│   │   ├── test_llm_stream_contract.py
│   │   ├── test_ollama_response_contract.py
│   │   ├── test_prompt_contract.py
│   │   ├── test_rag_retrieval_contract.py
│   │   └── test_tool_result_contract.py
│   ├── cross_layer
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_debug_view_matches_failure_events.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_prompt_apply_affects_real_request.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_debug_view_matches_failure_events.py
│   │   └── test_prompt_apply_affects_real_request.py
│   ├── data
│   │   ├── sample_agents.json
│   │   ├── sample_documents
│   │   │   └── readme.md
│   │   └── sample_prompts.json
│   ├── failure_modes
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_chroma_import_failure.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chroma_unreachable.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_event_bus_listener_error.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_event_store_failure.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_llm_chunk_parsing_failure.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_metrics_on_failed_chat_or_task.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_ollama_broken_response.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_prompt_service_failure.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_rag_empty_results.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_rag_retrieval_failure.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_sqlite_lock.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_tool_failure.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_chroma_import_failure.py
│   │   ├── test_chroma_unreachable.py
│   │   ├── test_event_bus_listener_error.py
│   │   ├── test_event_store_failure.py
│   │   ├── test_llm_chunk_parsing_failure.py
│   │   ├── test_metrics_on_failed_chat_or_task.py
│   │   ├── test_ollama_broken_response.py
│   │   ├── test_prompt_service_failure.py
│   │   ├── test_rag_empty_results.py
│   │   ├── test_rag_retrieval_failure.py
│   │   ├── test_sqlite_lock.py
│   │   └── test_tool_failure.py
│   ├── fixtures
│   │   ├── autopilot_v3
│   │   │   ├── happy_path
│   │   │   │   ├── incidents
│   │   │   │   │   ├── analytics.json
│   │   │   │   │   └── index.json
│   │   │   │   ├── QA_AUTOPILOT_V2.json
│   │   │   │   ├── QA_CONTROL_CENTER.json
│   │   │   │   └── QA_PRIORITY_SCORE.json
│   │   │   └── README.md
│   │   └── feedback_loop
│   │       ├── incidents
│   │       │   ├── analytics.json
│   │       │   └── index.json
│   │       ├── QA_AUTOPILOT_V2.json
│   │       ├── QA_CONTROL_CENTER.json
│   │       ├── QA_PRIORITY_SCORE.json
│   │       └── QA_RISK_RADAR.md
│   ├── golden_path
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_agent_golden_path.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_agent_in_chat_golden_path.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chat_golden_path.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chat_rag_golden_path.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_debug_panel_golden_path.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_prompt_golden_path.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_rag_golden_path.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_agent_golden_path.py
│   │   ├── test_agent_in_chat_golden_path.py
│   │   ├── test_chat_golden_path.py
│   │   ├── test_chat_rag_golden_path.py
│   │   ├── test_debug_panel_golden_path.py
│   │   ├── test_prompt_golden_path.py
│   │   └── test_rag_golden_path.py
│   ├── helpers
│   │   ├── chaos_fixtures.py
│   │   ├── diagnostics.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── chaos_fixtures.cpython-312.pyc
│   │   │   ├── diagnostics.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── test_diagnostics.cpython-312-pytest-9.0.2.pyc
│   │   └── test_diagnostics.py
│   ├── integration
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_chat_prompt_integration.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chat_streaming_behavior.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chroma.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_event_bus.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_main_window_signals.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_model_settings_chat.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_rag_chat_integration.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_sqlite.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_chat_prompt_integration.py
│   │   ├── test_chat_streaming_behavior.py
│   │   ├── test_chroma.py
│   │   ├── test_event_bus.py
│   │   ├── test_main_window_signals.py
│   │   ├── test_model_settings_chat.py
│   │   ├── test_rag_chat_integration.py
│   │   └── test_sqlite.py
│   ├── live
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_agent_execution.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_ollama.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_rag_pipeline.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_agent_execution.py
│   │   ├── test_ollama.py
│   │   └── test_rag_pipeline.py
│   ├── meta
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_event_type_drift.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_marker_discipline.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_event_type_drift.py
│   │   └── test_marker_discipline.py
│   ├── P0_IMPLEMENTATION_PLAN.md
│   ├── P0_IMPLEMENTATION_REPORT.md
│   ├── P0_TESTPLAN.md
│   ├── __pycache__
│   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_agent_hr.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_agents.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_app.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_chat_history_filtering.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_chat_streaming.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_db_files.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_debug.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_escalation.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_llm_output_pipeline.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_metrics.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_model_router.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_model_settings_bindings.cpython-312.pyc
│   │   ├── test_model_settings_bindings.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_orchestration.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_projects.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_prompt_repository.cpython-312.pyc
│   │   ├── test_prompt_repository.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_rag.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_self_improving.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_slash_commands.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_streaming_logic.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_tools_execute_command.cpython-312-pytest-9.0.2.pyc
│   │   └── test_tools_workspace_paths.cpython-312-pytest-9.0.2.pyc
│   ├── qa
│   │   ├── autopilot_v3
│   │   │   ├── conftest.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── test_backlog.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_dry_run_determinism.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_gap_detection.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_happy_path.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_robustness.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_rules_unit.cpython-312-pytest-9.0.2.pyc
│   │   │   │   └── test_translation_gaps.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_backlog.py
│   │   │   ├── test_dry_run_determinism.py
│   │   │   ├── test_gap_detection.py
│   │   │   ├── test_happy_path.py
│   │   │   ├── test_robustness.py
│   │   │   ├── test_rules_unit.py
│   │   │   └── test_translation_gaps.py
│   │   ├── conftest.py
│   │   ├── coverage_map
│   │   │   ├── conftest.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── test_coverage_map_aggregation.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_coverage_map_gaps.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_coverage_map_governance.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_coverage_map_loader.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_coverage_map_strength.cpython-312-pytest-9.0.2.pyc
│   │   │   │   └── test_gap_prioritization.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_coverage_map_aggregation.py
│   │   │   ├── test_coverage_map_gaps.py
│   │   │   ├── test_coverage_map_governance.py
│   │   │   ├── test_coverage_map_loader.py
│   │   │   ├── test_coverage_map_strength.py
│   │   │   └── test_gap_prioritization.py
│   │   ├── feedback_loop
│   │   │   ├── conftest.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── test_determinism.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_feedback_loop_integration.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_feedback_loop_robustness.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_loader.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_normalizer.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_projections.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_rules.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_traces.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_update_control_center.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_update_priority_scores.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_update_risk_radar.cpython-312-pytest-9.0.2.pyc
│   │   │   │   └── test_utils.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_determinism.py
│   │   │   ├── test_feedback_loop_integration.py
│   │   │   ├── test_feedback_loop_robustness.py
│   │   │   ├── test_loader.py
│   │   │   ├── test_normalizer.py
│   │   │   ├── test_projections.py
│   │   │   ├── test_rules.py
│   │   │   ├── test_traces.py
│   │   │   ├── test_update_control_center.py
│   │   │   ├── test_update_priority_scores.py
│   │   │   ├── test_update_risk_radar.py
│   │   │   └── test_utils.py
│   │   ├── generators
│   │   │   ├── conftest.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── test_cli_io.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_update_control_center.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_update_priority_scores.cpython-312-pytest-9.0.2.pyc
│   │   │   │   └── test_update_risk_radar.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_cli_io.py
│   │   │   ├── test_update_control_center.py
│   │   │   ├── test_update_priority_scores.py
│   │   │   └── test_update_risk_radar.py
│   │   ├── golden
│   │   │   ├── expected
│   │   │   │   ├── control_center.json
│   │   │   │   ├── control_center_trace.json
│   │   │   │   ├── priority_score.json
│   │   │   │   ├── priority_score_trace.json
│   │   │   │   ├── risk_radar.json
│   │   │   │   └── risk_radar_trace.json
│   │   │   ├── __pycache__
│   │   │   │   └── test_golden_snapshots.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── README.md
│   │   │   └── test_golden_snapshots.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_enrich_replay_binding.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_semantic_enrichment.cpython-312-pytest-9.0.2.pyc
│   │   ├── QA_FEEDBACK_LOOP_TEST_REVIEW.md
│   │   ├── README.md
│   │   ├── test_enrich_replay_binding.py
│   │   ├── test_inventory
│   │   │   ├── conftest.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── test_inventory_determinism.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_inventory_governance.cpython-312-pytest-9.0.2.pyc
│   │   │   │   ├── test_inventory_happy_path.cpython-312-pytest-9.0.2.pyc
│   │   │   │   └── test_inventory_rules.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_inventory_determinism.py
│   │   │   ├── test_inventory_governance.py
│   │   │   ├── test_inventory_happy_path.py
│   │   │   └── test_inventory_rules.py
│   │   └── test_semantic_enrichment.py
│   ├── QA_FEEDBACK_LOOP_ACCEPTANCE_CHECKLIST.md
│   ├── QA_FEEDBACK_LOOP_ARCHITECTURE_REVIEW.md
│   ├── QA_FEEDBACK_LOOP_CLI_IO_REVIEW.md
│   ├── QA_FEEDBACK_LOOP_CONSOLIDATED_REMEDIATION_PLAN.md
│   ├── QA_FEEDBACK_LOOP_DETERMINISM_REVIEW.md
│   ├── QA_FEEDBACK_LOOP_FINAL_RELEASE_DECISION.md
│   ├── QA_FEEDBACK_LOOP_GOVERNANCE_REVIEW.md
│   ├── QA_FEEDBACK_LOOP_REMEDIATION_CHANGES.md
│   ├── QA_FEEDBACK_LOOP_REREVIEW_REPORT.md
│   ├── QA_LEVEL2_REPORT.md
│   ├── QA_LEVEL3_REPORT.md
│   ├── README.md
│   ├── regression
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_agent_delete_removes_from_list.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chat_composer_send_signal_actually_emits.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chat_delete_single.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chat_without_project.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_settings_theme_tokens.cpython-312-pytest-9.0.2.pyc
│   │   ├── README.md
│   │   ├── test_agent_delete_removes_from_list.py
│   │   ├── test_chat_composer_send_signal_actually_emits.py
│   │   ├── test_chat_delete_single.py
│   │   ├── test_chat_without_project.py
│   │   └── test_settings_theme_tokens.py
│   ├── smoke
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_agent_workflow.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_app_startup.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_basic_chat.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_full_workflow.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_shell_gui.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_agent_workflow.py
│   │   ├── test_app_startup.py
│   │   ├── test_basic_chat.py
│   │   ├── test_full_workflow.py
│   │   └── test_shell_gui.py
│   ├── startup
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_app_starts_with_optional_dependencies_missing.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_startup_without_ollama.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_app_starts_with_optional_dependencies_missing.py
│   │   └── test_startup_without_ollama.py
│   ├── state_consistency
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_agent_consistency.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_debug_consistency.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_prompt_consistency.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_agent_consistency.py
│   │   ├── test_debug_consistency.py
│   │   └── test_prompt_consistency.py
│   ├── test_agent_hr.py
│   ├── test_agents.py
│   ├── test_app.py
│   ├── TEST_AUDIT_REPORT.md
│   ├── test_chat_history_filtering.py
│   ├── test_chat_streaming.py
│   ├── test_db_files.py
│   ├── test_debug.py
│   ├── test_escalation.py
│   ├── test_llm_output_pipeline.py
│   ├── test_metrics.py
│   ├── test_model_router.py
│   ├── test_model_settings_bindings.py
│   ├── test_orchestration.py
│   ├── test_projects.py
│   ├── test_prompt_repository.py
│   ├── test_rag.py
│   ├── test_self_improving.py
│   ├── test_slash_commands.py
│   ├── test_streaming_logic.py
│   ├── test_tools_execute_command.py
│   ├── test_tools_workspace_paths.py
│   ├── ui
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── conftest.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── test_agent_hr_ui.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_agent_performance_tab.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_chat_ui.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_command_center_dashboard.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_debug_panel_ui.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_prompt_manager_ui.cpython-312-pytest-9.0.2.pyc
│   │   │   ├── test_rag_toggle.cpython-312-pytest-9.0.2.pyc
│   │   │   └── test_ui_behavior.cpython-312-pytest-9.0.2.pyc
│   │   ├── test_agent_hr_ui.py
│   │   ├── test_agent_performance_tab.py
│   │   ├── test_chat_ui.py
│   │   ├── test_command_center_dashboard.py
│   │   ├── test_debug_panel_ui.py
│   │   ├── test_prompt_manager_ui.py
│   │   ├── test_rag_toggle.py
│   │   └── test_ui_behavior.py
│   └── unit
│       ├── __init__.py
│       ├── __pycache__
│       │   ├── __init__.cpython-312.pyc
│       │   ├── test_agents.cpython-312-pytest-9.0.2.pyc
│       │   ├── test_metrics.cpython-312-pytest-9.0.2.pyc
│       │   ├── test_prompt_system.cpython-312-pytest-9.0.2.pyc
│       │   ├── test_rag.cpython-312-pytest-9.0.2.pyc
│       │   ├── test_router.cpython-312-pytest-9.0.2.pyc
│       │   └── test_tools.cpython-312-pytest-9.0.2.pyc
│       ├── test_agents.py
│       ├── test_metrics.py
│       ├── test_prompt_system.py
│       ├── test_rag.py
│       ├── test_router.py
│       └── test_tools.py
└── tools
    ├── generate_feature_registry.py
    ├── generate_system_map.py
    ├── generate_trace_map.py
    └── __pycache__
        └── generate_feature_registry.cpython-312.pyc

289 directories, 1862 files
