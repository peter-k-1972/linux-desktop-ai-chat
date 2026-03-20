"""
Help Topic Resolver – resolve workspace/area to help topic.

Uses: HelpIndex (help/ with workspace frontmatter), TRACE_MAP fallback.
"""

from typing import Optional


def resolve_help_topic(workspace_id: str) -> Optional[str]:
    """
    Resolve workspace_id to help topic id.
    Returns topic id or None.
    """
    # HelpIndex (primary): help articles with workspace frontmatter
    try:
        from app.help.help_index import HelpIndex
        index = HelpIndex()
        topic = index.get_topic_by_workspace(workspace_id)
        if topic:
            return topic.id
    except Exception:
        pass

    # Trace map fallback
    try:
        from app.core.navigation.trace_map_loader import load_workspace_to_help
        return load_workspace_to_help().get(workspace_id)
    except Exception:
        pass

    return None


def resolve_help_topic_with_title(workspace_id: str) -> Optional[tuple[str, str]]:
    """
    Resolve workspace_id to (topic_id, title).
    Returns (topic_id, title) or None.
    """
    try:
        from app.help.help_index import HelpIndex
        index = HelpIndex()
        topic = index.get_topic_by_workspace(workspace_id)
        if topic:
            return (topic.id, topic.title)
    except Exception:
        pass

    topic_id = resolve_help_topic(workspace_id)
    if topic_id:
        try:
            from app.help.help_index import HelpIndex
            index = HelpIndex()
            topic = index.get_topic(topic_id)
            if topic:
                return (topic.id, topic.title)
        except Exception:
            pass
        return (topic_id, topic_id.replace("_", " ").title())

    return None
