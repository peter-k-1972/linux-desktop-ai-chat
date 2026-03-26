#!/usr/bin/env python3
"""
Architecture Map – Linux Desktop Chat.

Erzeugt eine kompakte, automatisch generierbare Architektur-Übersicht.
Nutzt arch_guard_config und Baseline-Dokumente.

Verwendung:
  python scripts/dev/architecture_map.py
  python scripts/dev/architecture_map.py --json

Ausgabe:
  docs/04_architecture/ARCHITECTURE_MAP.md
  docs/04_architecture/ARCHITECTURE_MAP.json (optional)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_ARCH = PROJECT_ROOT / "docs" / "04_architecture"
OUTPUT_MD = DOCS_ARCH / "ARCHITECTURE_MAP.md"
OUTPUT_JSON = DOCS_ARCH / "ARCHITECTURE_MAP.json"

# Python-Pfad für arch_guard_config
sys.path.insert(0, str(PROJECT_ROOT))


def _load_arch_config() -> dict:
    """Lädt arch_guard_config (ohne pytest)."""
    import importlib.util
    path = PROJECT_ROOT / "tests" / "architecture" / "arch_guard_config.py"
    spec = importlib.util.spec_from_file_location("arch_guard_config", path)
    if spec is None or spec.loader is None:
        return {}
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {
        "target_packages": sorted(mod.TARGET_PACKAGES),
        "allowed_app_root": sorted(mod.ALLOWED_APP_ROOT_FILES),
        "temporarily_allowed_root": sorted(mod.TEMPORARILY_ALLOWED_ROOT_FILES),
        "forbidden_parallel": sorted(mod.FORBIDDEN_PARALLEL_PACKAGES),
        "root_entrypoints": sorted(mod.ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS),
        "canonical_gui_entrypoints": sorted(mod.CANONICAL_GUI_ENTRY_POINTS),
        "canonical_services": sorted(mod.CANONICAL_SERVICE_MODULES),
        "provider_strings": sorted(mod.KNOWN_MODEL_PROVIDER_STRINGS),
        "allowed_provider_files": sorted(mod.ALLOWED_PROVIDER_STRING_FILES),
        "gui_screen_workspace_map": {
            k: sorted(v) if isinstance(v, (set, frozenset)) else v
            for k, v in mod.GUI_SCREEN_WORKSPACE_MAP.items()
        },
        "expected_drift_categories": sorted(mod.EXPECTED_DRIFT_CATEGORIES),
        "expected_governance_domains": sorted(mod.EXPECTED_GOVERNANCE_DOMAINS),
    }


def _build_map_data(config: dict) -> dict:
    """Baut die vollständige Map-Datenstruktur."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "project": "Linux Desktop Chat",
        "generated_at": ts,
        "status": "Governance gehärtet, Baseline 2026",
        "layers": [
            {"name": "GUI", "path": "app/gui/", "role": "Shell, Domains, Workspace, Navigation, Commands, Inspector"},
            {"name": "Services", "path": "app/services/", "role": "Chat, Model, Provider, Knowledge, Agent, Project, Topic, QA-Governance, Infrastructure"},
            {
                "name": "Providers",
                "path": "linux-desktop-chat-providers/src/app/providers/",
                "role": "LocalOllamaProvider, CloudOllamaProvider (Import app.providers)",
            },
            {
                "name": "CLI",
                "path": "linux-desktop-chat-cli/src/app/cli/",
                "role": "Context replay/repro/registry headless tools (Import app.cli)",
            },
            {
                "name": "Utils",
                "path": "linux-desktop-chat-utils/src/app/utils/",
                "role": "Paths, datetime, env loader (Import app.utils)",
            },
            {
                "name": "UI themes (builtins)",
                "path": "linux-desktop-chat-ui-themes/src/app/ui_themes/",
                "role": "Theme manifests/QSS/JSON (Import app.ui_themes)",
            },
            {
                "name": "UI runtime (QML/widgets)",
                "path": "linux-desktop-chat-ui-runtime/src/app/ui_runtime/",
                "role": "Theme manifest validation, QmlRuntime, shell bridge (Import app.ui_runtime)",
            },
            {
                "name": "Product runtime",
                "path": "linux-desktop-chat-runtime/src/app/runtime/",
                "role": "Single-instance lock, shutdown hooks, model_invocation DTOs (Import app.runtime); app.extensions discovery root",
            },
            {"name": "Core", "path": "app/core/", "role": "Models, Navigation, Context, DB, Commands, LLM, Config"},
        ],
        "domains": [
            {"name": "agents", "path": "app/agents/", "role": "AgentProfile, Registry, Repository, TaskRunner"},
            {"name": "rag", "path": "app/rag/", "role": "Retriever, Embedding, Service, VectorStore"},
            {
                "name": "tools",
                "path": "linux-desktop-chat-infra/src/app/tools/",
                "role": "FileSystemTools, web_search (keine Registry; Import app.tools)",
            },
            {
                "name": "debug",
                "path": "linux-desktop-chat-infra/src/app/debug/",
                "role": "Emitter, EventBus, DebugStore, AgentEvent (Import app.debug)",
            },
            {
                "name": "metrics",
                "path": "linux-desktop-chat-infra/src/app/metrics/",
                "role": "MetricsCollector, Agent-Metriken (Import app.metrics)",
            },
            {"name": "qa", "path": "app/qa/", "role": "Operations-Adapter, Dashboard-Adapter"},
            {"name": "prompts", "path": "app/prompts/", "role": "Prompt-Modelle, Service, Repository"},
            {"name": "utils", "path": "linux-desktop-chat-utils/src/app/utils/", "role": "Paths, Env-Loader, Datetime (nur stdlib; Import app.utils)"},
        ],
        "entrypoints": {
            "canonical": [
                {"cmd": "python -m app", "path": "app/__main__.py", "delegation": "run_gui_shell.main"},
                {"cmd": "python run_gui_shell.py", "path": "run_gui_shell.py", "delegation": "—"},
                {"cmd": "python main.py", "path": "main.py", "delegation": "run_gui_shell.main"},
                {"cmd": "start.sh", "path": "start.sh", "delegation": "python -m app"},
            ],
            "legacy": [
                {"cmd": "python archive/run_legacy_gui.py", "path": "archive/run_legacy_gui.py", "delegation": "app.main.main"},
            ],
        },
        "registries": [
            {"name": "Model Registry", "path": "app/core/models/registry.py", "lifecycle": "Statisch"},
            {"name": "Navigation Registry", "path": "app/core/navigation/navigation_registry.py", "lifecycle": "Statisch"},
            {"name": "Screen Registry", "path": "app/gui/workspace/screen_registry, gui/bootstrap", "lifecycle": "Bootstrap"},
            {"name": "Command Registry", "path": "app/gui/commands/registry, palette_loader", "lifecycle": "Bootstrap"},
            {"name": "Agent Registry", "path": "app/agents/agent_registry.py", "lifecycle": "Lazy"},
        ],
        "tools_no_registry": "linux-desktop-chat-infra/src/app/tools/ listet explizit; bewusste Entscheidung (TOOLS_GOVERNANCE_DECISION.md)",
        "services": config.get("canonical_services", []),
        "providers": {
            "strings": config.get("provider_strings", []),
            "implementations": ["LocalOllamaProvider", "CloudOllamaProvider"],
        },
        "governance_blocks": [
            {"block": "GUI Governance", "policy": "GUI_GOVERNANCE_POLICY.md", "test": "test_gui_governance_guards"},
            {"block": "GUI Domain Dependency", "policy": "GUI_DOMAIN_DEPENDENCY_POLICY.md", "test": "test_gui_domain_dependency_guards"},
            {"block": "Service Governance", "policy": "SERVICE_GOVERNANCE_POLICY.md", "test": "test_service_governance_guards"},
            {"block": "Startup Governance", "policy": "STARTUP_GOVERNANCE_POLICY.md", "test": "test_startup_governance_guards"},
            {"block": "Registry Governance", "policy": "REGISTRY_GOVERNANCE_POLICY.md", "test": "test_registry_governance_guards"},
            {"block": "Provider Orchestrator", "policy": "PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md", "test": "test_provider_orchestrator_governance_guards"},
            {"block": "EventBus Governance", "policy": "EVENTBUS_GOVERNANCE_POLICY.md", "test": "test_eventbus_governance_guards"},
            {"block": "Feature Governance", "policy": "FEATURE_GOVERNANCE_POLICY.md", "test": "test_feature_governance_guards"},
            {"block": "App Package", "policy": "APP_TARGET_PACKAGE_ARCHITECTURE", "test": "test_app_package_guards"},
            {"block": "Architecture Drift Radar", "policy": "ARCHITECTURE_DRIFT_RADAR_POLICY.md", "test": "test_architecture_drift_radar"},
            {"block": "Root Entrypoint", "policy": "ROOT_ENTRYPOINT_POLICY.md", "test": "test_root_entrypoint_guards"},
            {"block": "Lifecycle", "policy": "RUNTIME_LIFECYCLE_POLICY.md", "test": "test_lifecycle_guards"},
        ],
        "legacy_transitional": {
            "app_main": "Legacy MainWindow; nur archive/run_legacy_gui.py",
            "temporarily_allowed_root": config.get("temporarily_allowed_root", []),
            "forbidden_parallel": config.get("forbidden_parallel", []),
        },
        "_config_source": "arch_guard_config.py",
    }


def _render_markdown(data: dict) -> str:
    """Rendert die Map als Markdown."""
    lines = [
        "# Architecture Map",
        "",
        f"**Projekt:** {data['project']}  ",
        f"**Generiert:** {data['generated_at']}  ",
        f"**Status:** {data['status']}",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        f"- Projekt: {data['project']}",
        f"- Generierungszeitpunkt: {data['generated_at']}",
        f"- Statushinweis: {data['status']}",
        "",
        "---",
        "",
        "## 2. Layers",
        "",
        "| Schicht | Pfad | Rolle |",
        "|---------|------|-------|",
    ]
    for l in data["layers"]:
        lines.append(f"| {l['name']} | {l['path']} | {l['role']} |")
    lines.extend([
        "",
        "---",
        "",
        "## 3. Domains",
        "",
        "| Domäne | Pfad | Rolle |",
        "|--------|------|-------|",
    ])
    for d in data["domains"]:
        lines.append(f"| {d['name']} | {d['path']} | {d['role']} |")
    lines.extend([
        "",
        "---",
        "",
        "## 4. Canonical Entrypoints",
        "",
        "### Kanonisch",
        "",
        "| Befehl | Pfad | Delegation |",
        "|--------|------|------------|",
    ])
    for e in data["entrypoints"]["canonical"]:
        lines.append(f"| {e['cmd']} | {e['path']} | {e['delegation']} |")
    lines.extend([
        "",
        "### Legacy",
        "",
        "| Befehl | Pfad | Delegation |",
        "|--------|------|------------|",
    ])
    for e in data["entrypoints"]["legacy"]:
        lines.append(f"| {e['cmd']} | {e['path']} | {e['delegation']} |")
    lines.extend([
        "",
        "---",
        "",
        "## 5. Registries",
        "",
        "| Registry | Ort | Lifecycle |",
        "|----------|-----|-----------|",
    ])
    for r in data["registries"]:
        lines.append(f"| {r['name']} | {r['path']} | {r['lifecycle']} |")
    lines.extend([
        "",
        f"**Tools:** {data['tools_no_registry']}",
        "",
        "---",
        "",
        "## 6. Services",
        "",
    ])
    for s in data["services"]:
        lines.append(f"- {s}")
    lines.extend([
        "",
        "---",
        "",
        "## 7. Providers",
        "",
        f"- **Provider-Strings:** {', '.join(data['providers']['strings'])}",
        f"- **Implementierungen:** {', '.join(data['providers']['implementations'])}",
        "",
        "---",
        "",
        "## 8. Governance Blocks",
        "",
        "| Block | Policy | Guard |",
        "|-------|--------|-------|",
    ])
    for g in data["governance_blocks"]:
        lines.append(f"| {g['block']} | {g['policy']} | {g['test']} |")
    lines.extend([
        "",
        "---",
        "",
        "## 9. Known Legacy / Transitional",
        "",
        f"- **app.main:** {data['legacy_transitional']['app_main']}",
        f"- **Temporär erlaubt (app/ Root):** {', '.join(data['legacy_transitional']['temporarily_allowed_root'])}",
        f"- **Verboten (Parallelstrukturen):** {', '.join(data['legacy_transitional']['forbidden_parallel'])}",
        "",
        "---",
        "",
        f"*Quelle: arch_guard_config, ARCHITECTURE_BASELINE_2026. Generiert von scripts/dev/architecture_map.py*",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Architecture Map Generator")
    parser.add_argument("--json", action="store_true", help="JSON zusätzlich ausgeben")
    args = parser.parse_args()

    DOCS_ARCH.mkdir(parents=True, exist_ok=True)

    try:
        config = _load_arch_config()
    except Exception as e:
        print(f"Warnung: arch_guard_config nicht ladbar: {e}", file=sys.stderr)
        config = {}

    data = _build_map_data(config)

    md = _render_markdown(data)
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(f"Erzeugt: {OUTPUT_MD}")

    if args.json:
        # JSON-serialisierbar machen (keine frozenset etc.)
        json_data = json.loads(json.dumps(data, default=lambda x: list(x) if hasattr(x, "__iter__") and not isinstance(x, (str, dict)) else str(x)))
        OUTPUT_JSON.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Erzeugt: {OUTPUT_JSON}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
