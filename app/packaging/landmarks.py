"""
Maschinenlesbare Landmarken für Repo- und Paketstruktur.

Pflege: Bei neuen Repo-Top-Level-Artefakten oder neuen app/*-Paketen mit __init__.py
die entsprechenden Konstanten und docs/architecture/PACKAGE_MAP.md aktualisieren.

Siehe: docs/architecture/PACKAGE_MAP.md, tests/architecture/test_package_map_contract.py
"""

from __future__ import annotations

from typing import Final

# --- Plugin-Vertrag (muss zu app.features.entry_point_contract passen) ---
PLUGIN_ENTRY_POINT_GROUP: Final[str] = "linux_desktop_chat.features"

# --- Repo-Dateien / Verzeichnisse (relativ zum Projektroot), die die Paketstory sichtbar machen ---
REPO_LANDMARK_FILES: Final[tuple[str, ...]] = (
    "pyproject.toml",
    "docs/architecture/PACKAGE_MAP.md",
    "docs/architecture/PACKAGE_SPLIT_PLAN.md",
    "docs/architecture/PACKAGE_WAVE1_PREP.md",
    "docs/architecture/PACKAGE_FEATURES_CUT_READY.md",
    "docs/architecture/PACKAGE_FEATURES_PHYSICAL_SPLIT.md",
    "docs/architecture/GIT_QA_GOVERNANCE.md",
    "docs/architecture/SEGMENT_HYBRID_COUPLING_NOTES.md",
    "docs/developer/PACKAGE_GUIDE.md",
    "linux-desktop-chat-features/src/app/features/entry_point_contract.py",
    "linux-desktop-chat-features/src/app/features/release_matrix.py",
    "linux-desktop-chat-features/src/app/features/edition_resolution.py",
    "linux-desktop-chat-ui-contracts/pyproject.toml",
    "linux-desktop-chat-ui-contracts/src/app/ui_contracts/__init__.py",
    "linux-desktop-chat-pipelines/pyproject.toml",
    "linux-desktop-chat-pipelines/src/app/pipelines/__init__.py",
    "tools/ci/release_matrix_ci.py",
    "scripts/dev/print_git_qa_provenance.py",
    "scripts/dev/print_git_qa_report.py",
    "app/qa/git_qa_report.py",
    ".github/workflows/edition-smoke-matrix.yml",
    ".github/workflows/plugin-validation-smoke.yml",
    "examples/plugins/ldc_plugin_example/pyproject.toml",
    "tests/architecture/arch_guard_config.py",
    "tests/architecture/segment_dependency_rules.py",
    "tests/architecture/test_segment_dependency_rules.py",
)

# --- App-Root-Module, die Brücken/Legacy sind (keine neuen ohne Review) ---
BRIDGE_APP_ROOT_MODULES: Final[frozenset[str]] = frozenset({
    "db",
    "ollama_client",
    "critic",
})

# --- Top-Level-Pakete unter app/ mit __init__.py, die NICHT in arch_guard_config.TARGET_PACKAGES ---
# stehen, aber produktiv sind. Neu? Hier + PACKAGE_MAP.md eintragen.
EXTENDED_APP_TOP_PACKAGES: Final[frozenset[str]] = frozenset({
    "chat",
    "chats",
    "cli",
    "commands",
    "context",
    "devtools",
    "extensions",
    "global_overlay",
    "help",
    "llm",
    "packaging",
    "persistence",
    "plugins",
    "projects",
    "qa",
    "runtime",
    "workflows",
    "workspace_presets",
})
