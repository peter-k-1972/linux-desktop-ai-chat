#!/usr/bin/env python3
"""
Generate docs/FEATURE_REGISTRY.md – system-wide index of features and their implementation.

Uses: app/gui/domains, help/, tests/, docs/qa to map each feature to:
- Workspace
- Code modules
- Services
- Help articles
- Tests
- QA documentation (when applicable)

Run: python3 tools/generate_feature_registry.py
"""

from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "docs" / "FEATURE_REGISTRY.md"

# Feature structure: area_title -> [(display_name, workspace_id), ...]
FEATURES = [
    ("Operations", [
        ("Chat", "operations_chat"),
        ("Knowledge", "operations_knowledge"),
        ("Prompt Studio", "operations_prompt_studio"),
        ("Workflows", "operations_workflows"),
        ("Agent Tasks", "operations_agent_tasks"),
        ("Projects", "operations_projects"),
    ]),
    ("Control Center", [
        ("Models", "cc_models"),
        ("Providers", "cc_providers"),
        ("Agents", "cc_agents"),
        ("Tools", "cc_tools"),
        ("Data Stores", "cc_data_stores"),
    ]),
    ("QA & Governance", [
        ("Test Inventory", "qa_test_inventory"),
        ("Coverage Map", "qa_coverage_map"),
        ("Gap Analysis", "qa_gap_analysis"),
        ("Incidents", "qa_incidents"),
        ("Replay Lab", "qa_replay_lab"),
    ]),
    ("Runtime / Debug", [
        ("EventBus", "rd_eventbus"),
        ("Logs", "rd_logs"),
        ("Metrics", "rd_metrics"),
        ("LLM Calls", "rd_llm_calls"),
        ("Agent Activity", "rd_agent_activity"),
        ("System Graph", "rd_system_graph"),
    ]),
    ("Settings", [
        ("Application", "settings_application"),
        ("Appearance", "settings_appearance"),
        ("AI / Models", "settings_ai_models"),
        ("Data", "settings_data"),
        ("Privacy", "settings_privacy"),
        ("Advanced", "settings_advanced"),
        ("Project", "settings_project"),
        ("Workspace", "settings_workspace"),
    ]),
]

# Workspace -> relevant services (inferred)
WORKSPACE_SERVICES = {
    "operations_chat": ["chat_service", "llm", "model_service", "provider_service"],
    "operations_knowledge": ["knowledge_service", "rag"],
    "operations_prompt_studio": ["prompts", "topic_service"],
    "operations_workflows": ["workflow_service", "schedule_service", "workflows"],
    "operations_agent_tasks": ["agent_service", "agents"],
    "operations_projects": ["project_service"],
    "cc_models": ["model_service", "provider_service"],
    "cc_providers": ["provider_service"],
    "cc_agents": ["agent_service", "agents"],
    "cc_tools": [],
    "cc_data_stores": ["rag"],
    "qa_test_inventory": ["qa_governance_service"],
    "qa_coverage_map": ["qa_governance_service"],
    "qa_gap_analysis": ["qa_governance_service"],
    "qa_incidents": ["qa_governance_service"],
    "qa_replay_lab": ["qa_governance_service"],
    "rd_eventbus": [],
    "rd_logs": [],
    "rd_metrics": [],
    "rd_llm_calls": [],
    "rd_agent_activity": ["agent_service"],
    "rd_system_graph": [],
    "settings_application": ["infrastructure"],
    "settings_appearance": [],
    "settings_ai_models": ["model_service", "provider_service"],
    "settings_data": ["rag"],
    "settings_privacy": [],
    "settings_advanced": [],
    "settings_project": ["project_service"],
    "settings_workspace": [],
}

# Keywords for test file matching: workspace_id -> [keywords]
WORKSPACE_TEST_KEYWORDS = {
    "operations_chat": ["chat", "composer", "conversation"],
    "operations_knowledge": ["knowledge", "rag", "embedding", "retrieval"],
    "operations_prompt_studio": ["prompt", "prompt_manager"],
    "operations_workflows": ["workflow"],
    "operations_agent_tasks": ["agent", "agent_task"],
    "operations_projects": ["project"],
    "cc_models": ["model", "provider"],
    "cc_providers": ["provider"],
    "cc_agents": ["agent"],
    "cc_tools": ["tool"],
    "cc_data_stores": ["data_store", "rag", "chroma"],
    "qa_test_inventory": ["test_inventory", "qa", "coverage"],
    "qa_coverage_map": ["coverage", "qa"],
    "qa_gap_analysis": ["gap", "qa"],
    "qa_incidents": ["incident", "qa"],
    "qa_replay_lab": ["replay", "qa"],
    "rd_eventbus": ["eventbus", "event"],
    "rd_logs": ["log"],
    "rd_metrics": ["metric"],
    "rd_llm_calls": ["llm", "trace"],
    "rd_agent_activity": ["agent_activity"],
    "rd_system_graph": ["system_graph", "graph"],
    "settings_application": ["settings", "startup"],
    "settings_appearance": ["theme", "appearance"],
    "settings_ai_models": ["model", "settings"],
    "settings_data": ["data", "settings"],
    "settings_privacy": ["privacy"],
    "settings_advanced": ["advanced", "settings"],
    "settings_project": ["project", "settings"],
    "settings_workspace": ["workspace", "settings"],
}


def _list_dirs(parent: Path) -> list[Path]:
    if not parent.exists():
        return []
    return sorted([p for p in parent.iterdir() if p.is_dir() and not p.name.startswith("_")])


def _list_files(parent: Path, ext: str = ".py") -> list[Path]:
    if not parent.exists():
        return []
    return sorted([p for p in parent.iterdir() if p.is_file() and p.suffix == ext])


def _parse_frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
        if text.strip().startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                import yaml
                return yaml.safe_load(parts[1]) or {}
    except Exception:
        pass
    return {}


def _scan_workspace_to_code() -> dict[str, list[str]]:
    """workspace_id -> [code paths]"""
    domains = PROJECT_ROOT / "app" / "gui" / "domains"
    result: dict[str, list[str]] = {}
    if not domains.exists():
        return result

    # Map domain/workspace to workspace_id
    domain_to_ws = {
        "operations": {
            "chat": "operations_chat",
            "knowledge": "operations_knowledge",
            "prompt_studio": "operations_prompt_studio",
            "workflows": "operations_workflows",
            "agent_tasks": "operations_agent_tasks",
            "projects": "operations_projects",
        },
        "control_center": {"agents_workspace": "cc_agents", "models_workspace": "cc_models", "providers_workspace": "cc_providers",
                          "tools_workspace": "cc_tools", "data_stores_workspace": "cc_data_stores"},
        "qa_governance": {"test_inventory_workspace": "qa_test_inventory", "coverage_map_workspace": "qa_coverage_map",
                         "gap_analysis_workspace": "qa_gap_analysis", "incidents_workspace": "qa_incidents", "replay_lab_workspace": "qa_replay_lab"},
        "runtime_debug": {"eventbus_workspace": "rd_eventbus", "logs_workspace": "rd_logs", "metrics_workspace": "rd_metrics",
                         "llm_calls_workspace": "rd_llm_calls", "agent_activity_workspace": "rd_agent_activity", "system_graph_workspace": "rd_system_graph"},
        "settings": {"appearance_workspace": "settings_appearance", "system_workspace": "settings_application",
                    "models_workspace": "settings_ai_models", "agents_workspace": "settings_agents", "advanced_workspace": "settings_advanced"},
    }

    # Settings categories (app/gui/domains/settings/categories)
    settings_categories = PROJECT_ROOT / "app" / "gui" / "domains" / "settings" / "categories"
    if settings_categories.exists():
        cat_to_ws = {
            "application_category": "settings_application", "appearance_category": "settings_appearance",
            "ai_models_category": "settings_ai_models", "data_category": "settings_data",
            "privacy_category": "settings_privacy", "advanced_category": "settings_advanced",
            "project_category": "settings_project", "workspace_category": "settings_workspace",
        }
        for f in _list_files(settings_categories, ".py"):
            if f.name.startswith("_") or "base" in f.name:
                continue
            ws_id = cat_to_ws.get(f.stem)
            if ws_id:
                path = f"app/gui/domains/settings/categories/{f.name}"
                result.setdefault(ws_id, []).append(path)

    for domain_dir in _list_dirs(domains):
        domain_name = domain_dir.name
        mapping = domain_to_ws.get(domain_name, {})

        # Workspaces subdir
        workspaces_dir = domain_dir / "workspaces"
        if workspaces_dir.exists():
            for f in _list_files(workspaces_dir, ".py"):
                if f.name.startswith("_") or "base" in f.name:
                    continue
                ws_id = mapping.get(f.stem)
                if ws_id:
                    path = f"app/gui/domains/{domain_name}/workspaces/{f.name}"
                    result.setdefault(ws_id, []).append(path)

        # Direct subdirs (operations/chat, etc.)
        for sub in _list_dirs(domain_dir):
            if sub.name == "workspaces":
                continue
            ws_id = domain_to_ws.get(domain_name, {}).get(sub.name)
            if ws_id:
                for f in _list_files(sub, ".py"):
                    if not f.name.startswith("_") and "workspace" in f.name.lower():
                        path = f"app/gui/domains/{domain_name}/{sub.name}/{f.name}"
                        result.setdefault(ws_id, []).append(path)

    return result


def _scan_workspace_to_help() -> dict[str, str]:
    """workspace_id -> help topic id"""
    help_dir = PROJECT_ROOT / "help"
    result = {}
    if not help_dir.exists():
        return result
    for md in help_dir.rglob("*.md"):
        meta = _parse_frontmatter(md)
        ws = meta.get("workspace")
        if ws:
            topic_id = meta.get("id") or md.stem
            result[ws] = topic_id
    return result


def _scan_tests_for_workspace(workspace_id: str) -> list[str]:
    """Find test files relevant to a workspace."""
    keywords = WORKSPACE_TEST_KEYWORDS.get(workspace_id, [])
    if not keywords:
        return []
    tests_dir = PROJECT_ROOT / "tests"
    if not tests_dir.exists():
        return []
    result = []
    for py in tests_dir.rglob("test_*.py"):
        name_lower = py.name.lower()
        for kw in keywords:
            if kw in name_lower:
                rel = py.relative_to(PROJECT_ROOT)
                result.append(str(rel).replace("\\", "/"))
                break
    return sorted(set(result))[:10]  # Limit per feature


def _scan_qa_docs() -> list[str]:
    """List QA docs relevant to QA & Governance."""
    qa_dir = PROJECT_ROOT / "docs" / "qa"
    if not qa_dir.exists():
        return []
    result = []
    for f in qa_dir.iterdir():
        if f.is_file() and f.suffix in (".md", ".json"):
            result.append(f"docs/qa/{f.name}")
    return sorted(result)[:25]


def generate() -> str:
    ws_to_code = _scan_workspace_to_code()
    ws_to_help = _scan_workspace_to_help()
    qa_docs = _scan_qa_docs()

    lines = [
        "# Feature Registry – Linux Desktop Chat",
        "",
        f"*Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "Run `python3 tools/generate_feature_registry.py` to regenerate.",
        "",
        "System-wide index of features and their implementation. Each feature references:",
        "- **Workspace** | **Code modules** | **Services** | **Help articles** | **Tests** | **QA documentation**",
        "",
        "---",
        "",
    ]

    for area_title, features in FEATURES:
        lines.append(f"## {area_title}")
        lines.append("")

        for display_name, workspace_id in features:
            lines.append(f"### {display_name}")
            lines.append("")
            lines.append(f"| Attribute | Value |")
            lines.append("|-----------|-------|")

            # Workspace
            lines.append(f"| Workspace | `{workspace_id}` |")

            # Code
            code_paths = ws_to_code.get(workspace_id, [])
            code_str = ", ".join(f"`{p}`" for p in code_paths[:5]) if code_paths else "—"
            if len(code_paths) > 5:
                code_str += f" (+{len(code_paths) - 5} more)"
            lines.append(f"| Code | {code_str} |")

            # Services
            services = WORKSPACE_SERVICES.get(workspace_id, [])
            svc_str = ", ".join(f"`{s}`" for s in services) if services else "—"
            lines.append(f"| Services | {svc_str} |")

            # Help
            help_id = ws_to_help.get(workspace_id)
            help_str = f"`{help_id}`" if help_id else "—"
            lines.append(f"| Help | {help_str} |")

            # Tests
            tests = _scan_tests_for_workspace(workspace_id)
            test_str = ", ".join(f"`{t}`" for t in tests[:5]) if tests else "—"
            if len(tests) > 5:
                test_str += f" (+{len(tests) - 5} more)"
            lines.append(f"| Tests | {test_str} |")

            # QA (for QA & Governance area)
            qa_str = "—"
            if area_title == "QA & Governance":
                qa_str = ", ".join(f"`{d}`" for d in qa_docs[:5])
                if len(qa_docs) > 5:
                    qa_str += f" (+{len(qa_docs) - 5} more)"
            lines.append(f"| QA docs | {qa_str} |")

            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Related Documents")
    lines.append("")
    lines.append("- [00_map_of_the_system.md](00_map_of_the_system.md) — Human-readable orientation")
    lines.append("- [SYSTEM_MAP.md](SYSTEM_MAP.md) — Structural map")
    lines.append("- [TRACE_MAP.md](TRACE_MAP.md) — Code/help/test traceability")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    content = generate()
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
