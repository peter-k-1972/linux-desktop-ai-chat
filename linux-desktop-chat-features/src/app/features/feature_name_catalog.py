"""
Kanonische Namen eingebauter Features (FeatureRegistrar.name).

Muss mit ``iter_builtin_feature_registrars`` / eingebauten Deskriptor-Namen übereinstimmen —
Test: ``test_feature_name_catalog_matches_builtin_registrars`` (Registry-Obermenge durch Discovery möglich).
"""

from __future__ import annotations

ALL_BUILTIN_FEATURE_NAMES: frozenset[str] = frozenset(
    {
        "command_center",
        "operations_hub",
        "control_center",
        "qa_governance",
        "runtime_observability",
        "settings",
        "prompt_studio",
        "knowledge_rag",
        "workflow_automation",
    }
)
