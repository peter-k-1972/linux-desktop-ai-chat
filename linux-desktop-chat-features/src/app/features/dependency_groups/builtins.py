"""
Eingebaute Dependency-Gruppen — orientiert an requirements.txt / späteren extras.
"""

from __future__ import annotations

from app.features.dependency_groups.models import DependencyGroupDescriptor
from app.features.dependency_groups.registry import DependencyGroupRegistry
from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES

_ALL = ALL_BUILTIN_FEATURE_NAMES


def register_builtin_dependency_groups(registry: DependencyGroupRegistry) -> None:
    registry.register_group(
        DependencyGroupDescriptor(
            name="core",
            description="GUI-Shell, Async, HTTP-Client, ORM/Migrationen.",
            python_packages=(
                "linux-desktop-chat-features",
                "linux-desktop-chat-ui-contracts",
                "linux-desktop-chat-pipelines",
                "linux-desktop-chat-providers",
                "linux-desktop-chat-cli",
                "PySide6",
                "qasync",
                "aiohttp",
                "SQLAlchemy",
                "alembic",
                "jsonschema",
                "deepdiff",
                "PyYAML",
            ),
            required_for_features=_ALL,
            optional=False,
            platform_notes="Linux-Desktop primär; Wayland/GNOME siehe Doku.",
        )
    )
    registry.register_group(
        DependencyGroupDescriptor(
            name="rag",
            description="Vektorstore / Chroma für Knowledge.",
            python_packages=("chromadb",),
            required_for_features=frozenset({"knowledge_rag"}),
            optional=True,
            platform_notes="Native wheels je Plattform beachten.",
        )
    )
    registry.register_group(
        DependencyGroupDescriptor(
            name="agents",
            description="Agent-Laufzeit (derzeit keine Extra-Pakete über core hinaus).",
            python_packages=(),
            required_for_features=frozenset({"operations_hub"}),
            optional=True,
            platform_notes="Agent-UI liegt im Operations-Hub.",
        )
    )
    registry.register_group(
        DependencyGroupDescriptor(
            name="workflows",
            description="Workflow-/Pipeline-Orchestrierung (Standardbibliothek + bestehende App-Module).",
            python_packages=(),
            required_for_features=frozenset({"workflow_automation"}),
            optional=False,
            platform_notes="Kein separates PyPI-Paket in Phase Manifest.",
        )
    )
    registry.register_group(
        DependencyGroupDescriptor(
            name="ops",
            description="Deployment/Ops-Oberflächen (informative Gruppe).",
            python_packages=(),
            required_for_features=frozenset({"operations_hub"}),
            optional=True,
            platform_notes="Rollouts u. Ä. unter Operations.",
        )
    )
    registry.register_group(
        DependencyGroupDescriptor(
            name="qml",
            description="Alternative Qt-Quick-Shell (library_qml_gui).",
            python_packages=(),
            required_for_features=frozenset(),
            optional=True,
            platform_notes="Oft gemeinsame PySide6-Basis; separates Manifest möglich.",
        )
    )
    registry.register_group(
        DependencyGroupDescriptor(
            name="governance",
            description="QA-Governance-Service und zugehörige App-Schicht (Monolith-Modul).",
            python_packages=(),
            required_for_features=frozenset({"qa_governance"}),
            optional=True,
            platform_notes="Technische Probe: Import app.services.qa_governance_service.",
        )
    )
    registry.register_group(
        DependencyGroupDescriptor(
            name="dev",
            description="Tests und QA-Tooling.",
            python_packages=("pytest", "pytest-asyncio", "pytest-qt"),
            required_for_features=frozenset(),
            optional=True,
            platform_notes="Nicht für Endnutzer-Wheels.",
        )
    )
