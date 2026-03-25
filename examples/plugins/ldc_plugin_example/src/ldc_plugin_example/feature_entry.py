"""
Entry target for ``[project.entry-points."linux_desktop_chat.features"]``.

Nur ``app.features.*`` importieren — kein ``app.gui`` (Governance / AST-Guards).
"""

from __future__ import annotations

from typing import Any, List

from app.features.descriptors import FeatureDescriptor


class ExamplePluginRegistrar:
    """No-op registrar: demonstrates discovery, validation, and edition gating."""

    def get_descriptor(self) -> FeatureDescriptor:
        return FeatureDescriptor(
            name="ldc.plugin.example",
            description="Example external plugin feature (no screens; discovery demo only).",
            enabled_by_default=True,
            optional_dependencies=(),
        )

    def register_screens(self, screen_registry: Any) -> None:
        return None

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return True


def get_feature_registrars() -> List[ExamplePluginRegistrar]:
    """Primary entry-point contract: callable returning one or more registrars."""
    return [ExamplePluginRegistrar()]
