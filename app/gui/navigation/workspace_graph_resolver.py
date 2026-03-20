"""
Workspace Graph Resolver – metadata for workspace nodes.

Resolves: description, help topic, feature registry, trace map, related workspaces.
Uses app.core.navigation loaders; no duplicated parsing.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class WorkspaceNodeMetadata:
    """Resolved metadata for a workspace/area node."""

    workspace_id: str
    area_id: str
    title: str
    short_description: str = ""
    help_topic_id: Optional[str] = None
    help_topic_title: Optional[str] = None
    help_article_path: Optional[str] = None
    feature_names: list[str] = field(default_factory=list)
    code_module_paths: list[str] = field(default_factory=list)
    service_paths: list[str] = field(default_factory=list)
    test_paths: list[str] = field(default_factory=list)
    related_workspace_ids: list[str] = field(default_factory=list)


# Related workspaces: workspace_id -> [related workspace_ids]
RELATED_WORKSPACES: dict[str, list[str]] = {
    "operations_chat": ["operations_knowledge", "operations_prompt_studio", "operations_agent_tasks", "cc_models"],
    "operations_knowledge": ["operations_chat", "cc_data_stores"],
    "operations_prompt_studio": ["operations_chat", "operations_agent_tasks"],
    "operations_agent_tasks": ["operations_chat", "cc_agents"],
    "operations_projects": ["operations_chat", "operations_knowledge"],
    "cc_models": ["cc_providers", "operations_chat"],
    "cc_providers": ["cc_models"],
    "cc_agents": ["operations_agent_tasks", "rd_agent_activity"],
    "cc_tools": ["operations_agent_tasks"],
    "cc_data_stores": ["operations_knowledge"],
    "qa_test_inventory": ["qa_coverage_map", "rd_logs"],
    "qa_coverage_map": ["qa_test_inventory", "qa_gap_analysis"],
    "qa_gap_analysis": ["qa_coverage_map", "qa_test_inventory"],
    "qa_incidents": ["qa_test_inventory", "rd_logs"],
    "qa_replay_lab": ["qa_test_inventory"],
    "rd_logs": ["rd_metrics", "rd_llm_calls", "qa_incidents"],
    "rd_metrics": ["rd_logs"],
    "rd_llm_calls": ["rd_logs", "operations_chat"],
    "rd_agent_activity": ["cc_agents", "operations_agent_tasks"],
    "rd_eventbus": ["rd_logs"],
    "rd_system_graph": ["rd_eventbus", "rd_logs"],
    "settings_application": [],
    "settings_appearance": [],
    "settings_ai_models": ["cc_models"],
    "settings_data": ["cc_data_stores"],
    "settings_privacy": [],
    "settings_advanced": [],
    "settings_project": ["operations_projects"],
    "settings_workspace": [],
}


def _get_feature_registry() -> dict[str, dict]:
    """Workspace_id -> {code, services, help, tests, feature_name} from app.core.navigation."""
    from app.core.navigation.feature_registry_loader import load_feature_registry
    return load_feature_registry()


def _find_help_article_path(topic_id: str) -> Optional[str]:
    """Find help/ path for a topic id."""
    help_dir = _PROJECT_ROOT / "help"
    if not help_dir.exists():
        return None
    for md in help_dir.rglob("*.md"):
        rel = md.relative_to(_PROJECT_ROOT)
        if md.stem == topic_id or (md.stem.replace("-", "_") == topic_id.replace("-", "_")):
            return str(rel).replace("\\", "/")
    return None


def _get_help_index_topic(workspace_id: str):
    """Get HelpTopic for workspace from HelpIndex."""
    try:
        from app.help.help_index import HelpIndex
        index = HelpIndex()
        return index.get_topic_by_workspace(workspace_id)
    except Exception:
        return None


def resolve_metadata(
    workspace_id: Optional[str],
    area_id: str,
    title: str,
    description: str = "",
) -> WorkspaceNodeMetadata:
    """
    Resolve full metadata for a workspace node.

    Uses: FEATURE_REGISTRY, TRACE_MAP, HelpIndex, sidebar/breadcrumb info.
    Graceful fallback when sources are missing.
    """
    nav_key = workspace_id or area_id
    meta = WorkspaceNodeMetadata(
        workspace_id=nav_key,
        area_id=area_id,
        title=title,
        short_description=description or title,
    )

    # Feature registry (primary source for code, services, help, tests)
    _feature_cache = _get_feature_registry()
    feat = _feature_cache.get(nav_key) if workspace_id else None
    if feat:
        meta.feature_names = [feat.get("feature_name", "")] if feat.get("feature_name") else []
        meta.code_module_paths = feat.get("code", []) or []
        meta.service_paths = [f"app/services/{s}.py" for s in feat.get("services", []) if s]
        meta.test_paths = feat.get("tests", []) or []
        if feat.get("help"):
            meta.help_topic_id = feat["help"]

    # Help: HelpIndex (has workspace mapping) > feature registry > trace map
    topic = _get_help_index_topic(nav_key) if workspace_id else None
    if topic:
        meta.help_topic_id = topic.id
        meta.help_topic_title = topic.title
        meta.help_article_path = _find_help_article_path(topic.id)
    elif meta.help_topic_id and not meta.help_topic_title:
        topic_obj = None
        try:
            from app.help.help_index import HelpIndex
            index = HelpIndex()
            topic_obj = index.get_topic(meta.help_topic_id)
        except Exception:
            pass
        if topic_obj:
            meta.help_topic_title = topic_obj.title
            meta.help_article_path = _find_help_article_path(meta.help_topic_id)

    # Trace map fallback for help
    if not meta.help_topic_id and workspace_id:
        from app.core.navigation.trace_map_loader import load_workspace_to_help
        trace_help = load_workspace_to_help()
        meta.help_topic_id = trace_help.get(nav_key)
        if meta.help_topic_id:
            try:
                from app.help.help_index import HelpIndex
                index = HelpIndex()
                t = index.get_topic(meta.help_topic_id)
                if t:
                    meta.help_topic_title = t.title
            except Exception:
                pass

    # Related workspaces
    meta.related_workspace_ids = RELATED_WORKSPACES.get(nav_key, []) if workspace_id else []

    return meta
