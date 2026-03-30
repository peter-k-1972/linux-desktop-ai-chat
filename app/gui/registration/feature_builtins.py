"""
Eingebaute FeatureRegistrare — Integrationsgrenze Qt/GUI.

Kontrakt: app.features.registrar.FeatureRegistrar

Screen-Reihenfolge entspricht der historischen register_all_navigation_area_screens-Reihenfolge.
"""

from __future__ import annotations

from typing import Any

from app.features import (
    FeatureDescriptor,
    FeatureRegistry,
    is_feature_technically_available,
)
from app.gui.registration import screen_registrar as area
from app.gui.workspace.screen_registry import ScreenRegistry


def _builtin_is_available(registrar: Any) -> bool:
    """Technische Verfügbarkeit über Dependency-Gruppen (siehe dependency_availability)."""
    return is_feature_technically_available(registrar.get_descriptor())


class CommandCenterFeatureRegistrar:
    def get_descriptor(self) -> FeatureDescriptor:
        return FeatureDescriptor(
            name="command_center",
            description="Kommandozentrale / Systemübersicht.",
            enabled_by_default=True,
            screens=("command_center",),
            navigation_entries=("command_center",),
            commands=("nav.dashboard",),
            services=(),
            optional_dependencies=(),
            experimental=False,
            packages=("gui", "core"),
            dependencies=("core", "gui"),
        )

    def register_screens(self, screen_registry: ScreenRegistry) -> None:
        area.register_command_center_screen(screen_registry)

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return _builtin_is_available(self)


class OperationsHubFeatureRegistrar:
    """Chat, Knowledge, Prompt Studio, Workflows u. a. unter einem Operations-Screen."""

    def get_descriptor(self) -> FeatureDescriptor:
        # navigation_entries kann breiter sein als generator-FEATURES:
        # Deployment/Betrieb sind navigierbar, aber bewusst kein eigenes Workspace-Feature dort.
        return FeatureDescriptor(
            name="operations_hub",
            description=(
                "Operations-Hub: Projekte, Chat, Knowledge/RAG, Prompt Studio, Workflows, "
                "Agent Tasks, Deployment, Audit."
            ),
            enabled_by_default=True,
            screens=("operations",),
            navigation_entries=(
                "operations_projects",
                "operations_chat",
                "operations_agent_tasks",
                "operations_deployment",
                "operations_audit_incidents",
            ),
            commands=(
                "nav.projects",
                "nav.chat",
                "nav.agent_tasks",
            ),
            services=("ChatService", "KnowledgeService", "TopicService", "PipelineService"),
            optional_dependencies=(),
            experimental=False,
            packages=("chat", "chats", "rag", "prompts", "workflows", "gui", "services"),
            dependencies=("core", "gui"),
        )

    def register_screens(self, screen_registry: ScreenRegistry) -> None:
        area.register_operations_screen(screen_registry)

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return _builtin_is_available(self)


class ControlCenterFeatureRegistrar:
    def get_descriptor(self) -> FeatureDescriptor:
        return FeatureDescriptor(
            name="control_center",
            description="Control Center: Modelle, Provider, Agenten-Katalog, Tools, Data Stores.",
            enabled_by_default=True,
            screens=("control_center",),
            navigation_entries=(
                "cc_models",
                "cc_providers",
                "cc_agents",
                "cc_tools",
                "cc_data_stores",
            ),
            commands=(
                "nav.control_center",
                "nav.cc_models",
                "nav.cc_providers",
                "nav.cc_agents",
                "nav.cc_tools",
                "nav.cc_data_stores",
            ),
            services=("ModelService", "ProviderService"),
            optional_dependencies=(),
            experimental=False,
            packages=("gui", "services"),
            dependencies=("core", "gui"),
        )

    def register_screens(self, screen_registry: ScreenRegistry) -> None:
        area.register_control_center_screen(screen_registry)

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return _builtin_is_available(self)


class QAGovernanceFeatureRegistrar:
    def get_descriptor(self) -> FeatureDescriptor:
        return FeatureDescriptor(
            name="qa_governance",
            description="QA & Governance: Test Inventory, Coverage, Incidents, Replay-Lab.",
            enabled_by_default=True,
            screens=("qa_governance",),
            navigation_entries=(
                "qa_governance",
                "qa_test_inventory",
                "qa_coverage_map",
                "qa_gap_analysis",
                "qa_incidents",
                "qa_replay_lab",
            ),
            commands=("nav.qa_governance",),
            services=("QAGovernanceService",),
            optional_dependencies=("governance",),
            experimental=False,
            packages=("services", "qa", "gui"),
            dependencies=("core",),
        )

    def register_screens(self, screen_registry: ScreenRegistry) -> None:
        area.register_qa_governance_screen(screen_registry)

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return _builtin_is_available(self)


class RuntimeObservabilityFeatureRegistrar:
    def get_descriptor(self) -> FeatureDescriptor:
        # Einige Runtime-Ziele bleiben bewusst außerhalb der generator-FEATURES
        # und werden nur als Navigation-/Observability-Einträge geführt.
        return FeatureDescriptor(
            name="runtime_observability",
            description="Runtime / Debug: Logs, Metriken, Eventbus, LLM-Calls, QA-Cockpit.",
            enabled_by_default=True,
            screens=("runtime_debug",),
            navigation_entries=(
                "runtime_debug",
                "rd_introspection",
                "rd_qa_cockpit",
                "rd_qa_observability",
                "rd_markdown_demo",
                "rd_eventbus",
                "rd_logs",
                "rd_llm_calls",
                "rd_agent_activity",
                "rd_metrics",
                "rd_system_graph",
            ),
            commands=(
                "nav.runtime_debug",
                "nav.rd_qa_cockpit",
                "nav.rd_qa_observability",
                "nav.rd_system_graph",
                "nav.rd_markdown_demo",
                "nav.rd_theme_visualizer",
            ),
            services=(),
            optional_dependencies=(),
            experimental=False,
            packages=("debug", "metrics", "gui"),
            dependencies=("core",),
        )

    def register_screens(self, screen_registry: ScreenRegistry) -> None:
        area.register_runtime_debug_screen(screen_registry)

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return _builtin_is_available(self)


class SettingsFeatureRegistrar:
    def get_descriptor(self) -> FeatureDescriptor:
        return FeatureDescriptor(
            name="settings",
            description="Globale und projektbezogene Einstellungen.",
            enabled_by_default=True,
            screens=("settings",),
            navigation_entries=(
                "settings",
                "settings_application",
                "settings_appearance",
                "settings_ai_models",
                "settings_data",
                "settings_privacy",
                "settings_advanced",
                "settings_project",
                "settings_workspace",
            ),
            commands=("nav.settings",),
            services=(),
            optional_dependencies=(),
            experimental=False,
            packages=("gui", "core", "services"),
            dependencies=("core", "gui"),
        )

    def register_screens(self, screen_registry: ScreenRegistry) -> None:
        area.register_settings_screen(screen_registry)

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return _builtin_is_available(self)


class PromptStudioCapabilityRegistrar:
    """Prompt Studio — Workspace unter Operations-Hub."""

    def get_descriptor(self) -> FeatureDescriptor:
        return FeatureDescriptor(
            name="prompt_studio",
            description="Prompt Studio und wiederverwendbare Vorlagen (Workspace unter Operations).",
            enabled_by_default=True,
            screens=(),
            navigation_entries=("operations_prompt_studio",),
            commands=("nav.prompt_studio",),
            services=(),
            optional_dependencies=(),
            experimental=False,
            packages=("prompts", "services", "gui"),
            dependencies=("core",),
        )

    def register_screens(self, screen_registry: ScreenRegistry) -> None:
        return None

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return _builtin_is_available(self)


class KnowledgeRAGCapabilityRegistrar:
    """Fachliche Klammer RAG — Screen liegt im Operations-Hub."""

    def get_descriptor(self) -> FeatureDescriptor:
        return FeatureDescriptor(
            name="knowledge_rag",
            description="Knowledge / RAG-Fähigkeit (Workspace unter Operations; optional chromadb).",
            enabled_by_default=True,
            screens=(),
            navigation_entries=("operations_knowledge",),
            commands=("nav.knowledge",),
            services=("KnowledgeService",),
            optional_dependencies=("rag",),
            experimental=False,
            packages=("rag", "services"),
            dependencies=("core",),
        )

    def register_screens(self, screen_registry: ScreenRegistry) -> None:
        return None

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return _builtin_is_available(self)


class WorkflowAutomationCapabilityRegistrar:
    def get_descriptor(self) -> FeatureDescriptor:
        return FeatureDescriptor(
            name="workflow_automation",
            description="Workflows und Pipeline-Ausführung (Workspace unter Operations).",
            enabled_by_default=True,
            screens=(),
            navigation_entries=("operations_workflows",),
            commands=("nav.workflows",),
            services=("PipelineService",),
            optional_dependencies=("workflows",),
            experimental=False,
            packages=("workflows", "pipelines", "services"),
            dependencies=("core",),
        )

    def register_screens(self, screen_registry: ScreenRegistry) -> None:
        return None

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return _builtin_is_available(self)


def iter_builtin_feature_registrars():
    """Iterable der eingebauten Registrare (kanonische Reihenfolge)."""
    for cls in (
        CommandCenterFeatureRegistrar,
        OperationsHubFeatureRegistrar,
        ControlCenterFeatureRegistrar,
        QAGovernanceFeatureRegistrar,
        RuntimeObservabilityFeatureRegistrar,
        SettingsFeatureRegistrar,
        PromptStudioCapabilityRegistrar,
        KnowledgeRAGCapabilityRegistrar,
        WorkflowAutomationCapabilityRegistrar,
    ):
        yield cls()


def register_builtin_feature_registrars(registry: FeatureRegistry) -> None:
    """Registriert nur Builtins (Discovery nutzt ``iter_builtin_feature_registrars``)."""
    for r in iter_builtin_feature_registrars():
        registry.register_registrar(r)
