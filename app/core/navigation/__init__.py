"""
Navigation – central registry and resolvers.

Single source of truth for all navigable entities.
"""

from app.core.navigation.navigation_registry import (
    NavEntry,
    NavSectionDef,
    get_all_entries,
    get_entry,
    get_sidebar_sections,
)
from app.core.navigation.feature_registry_loader import load_feature_registry, get_feature_for_workspace
from app.core.navigation.help_topic_resolver import resolve_help_topic, resolve_help_topic_with_title
from app.core.navigation.trace_map_loader import load_workspace_to_help, load_workspace_to_code, load_services

__all__ = [
    "NavEntry",
    "NavSectionDef",
    "get_all_entries",
    "get_entry",
    "get_sidebar_sections",
    "load_feature_registry",
    "get_feature_for_workspace",
    "resolve_help_topic",
    "resolve_help_topic_with_title",
    "load_workspace_to_help",
    "load_workspace_to_code",
    "load_services",
]
