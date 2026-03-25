"""
Eingebaute Editionen — deklarativ; Aktivierung erfolgt im Bootstrap (siehe edition_resolution).
"""

from __future__ import annotations

from app.features.editions.models import EditionDescriptor
from app.features.editions.registry import EditionRegistry
from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES

_ALL_FEATURES = ALL_BUILTIN_FEATURE_NAMES


def register_builtin_editions(registry: EditionRegistry) -> None:
    minimal = frozenset({"command_center", "operations_hub", "settings"})
    standard = minimal | frozenset(
        {"control_center", "prompt_studio", "knowledge_rag"}
    )
    automation = standard | frozenset({"workflow_automation", "runtime_observability"})
    full = _ALL_FEATURES

    registry.register_edition(
        EditionDescriptor(
            name="minimal",
            description="Chat-fokussierter Einstieg: Kommandozentrale, Operations-Hub, Einstellungen.",
            enabled_features=minimal,
            disabled_features=frozenset(),
            dependency_groups=("core",),
            default_shell="default_widget_gui",
            experimental_allowed=False,
            visibility_profile="public",
            notes="Kein QA-/Runtime-Debug-Schwerpunkt; Capability-Metadaten-Features ausgeschlossen.",
            support_level="community",
        )
    )
    registry.register_edition(
        EditionDescriptor(
            name="standard",
            description="Desktop-Nutzung mit Control Center, Prompt Studio und Knowledge-Metadaten.",
            enabled_features=standard,
            disabled_features=frozenset(),
            dependency_groups=("core", "rag"),
            default_shell="default_widget_gui",
            experimental_allowed=False,
            visibility_profile="public",
            notes="Ohne QA-Governance- und Runtime-Observability-Features.",
            support_level="community",
        )
    )
    registry.register_edition(
        EditionDescriptor(
            name="automation",
            description="Wie Standard plus Workflows- und Runtime-Metadaten.",
            enabled_features=automation,
            disabled_features=frozenset(),
            dependency_groups=("core", "rag", "workflows"),
            default_shell="default_widget_gui",
            experimental_allowed=False,
            visibility_profile="public",
            notes="QA-Governance weiterhin ausgeschlossen.",
            support_level="community",
        )
    )
    registry.register_edition(
        EditionDescriptor(
            name="full",
            description="Alle eingebauten Features inkl. QA & Governance.",
            enabled_features=full,
            disabled_features=frozenset(),
            dependency_groups=("core", "rag", "workflows", "agents", "ops", "qml", "governance"),
            default_shell="default_widget_gui",
            experimental_allowed=True,
            visibility_profile="public",
            notes="Entspricht der vollen aktuellen Feature-Fläche.",
            support_level="community",
        )
    )
    _example_plugin = frozenset({"ldc.plugin.example"})
    registry.register_edition(
        EditionDescriptor(
            name="plugin_example",
            description=(
                "Demonstrations-Edition: minimale Builtin-Fläche plus "
                "``ldc.plugin.example``, sofern installiert und produktfreigegeben."
            ),
            enabled_features=minimal | _example_plugin,
            disabled_features=frozenset(),
            released_plugin_features=_example_plugin,
            dependency_groups=("core",),
            default_shell="default_widget_gui",
            experimental_allowed=True,
            visibility_profile="internal",
            notes=(
                "Host-seitige Produktfreigabe für das Beispiel-Plugin; kein Release-Build-Ziel. "
                "Siehe docs/architecture/PLUGIN_FEATURE_PRODUCT_ACTIVATION.md."
            ),
            support_level="community",
        )
    )
