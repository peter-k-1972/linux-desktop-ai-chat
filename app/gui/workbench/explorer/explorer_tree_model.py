"""
QStandardItemModel factory for the Workbench explorer.

Top-level orientation: Favorites, Recent, Projects, Library, Runtime, System.
Leaf rows carry :class:`ExplorerItemRef` for routing into canvas tabs (never “screen switches”).
"""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from app.gui.workbench.explorer.explorer_items import ExplorerItemRef, ExplorerNodeKind, ExplorerSection


class ExplorerTreeRoles:
    """Roles used by :class:`ExplorerRouter` and selection handlers."""

    KIND = Qt.ItemDataRole.UserRole + 1
    PAYLOAD = Qt.ItemDataRole.UserRole + 2
    REF = Qt.ItemDataRole.UserRole + 3
    PINNED = Qt.ItemDataRole.UserRole + 4


def ref_from_index(index: QModelIndex) -> ExplorerItemRef | None:
    if not index.isValid():
        return None
    ref = index.data(ExplorerTreeRoles.REF)
    return ref if isinstance(ref, ExplorerItemRef) else None


def is_pinned_favorite(index: QModelIndex) -> bool:
    if not index.isValid():
        return False
    v = index.data(ExplorerTreeRoles.PINNED)
    return v is True


def _item(
    label: str,
    *,
    kind: str,
    payload: str | None,
    section: ExplorerSection,
    path: tuple[str, ...],
    pinned: bool = False,
) -> QStandardItem:
    it = QStandardItem(label)
    ref = ExplorerItemRef(section=section, kind=kind, payload=payload, path_labels=path)
    it.setData(kind, ExplorerTreeRoles.KIND)
    it.setData(payload, ExplorerTreeRoles.PAYLOAD)
    it.setData(ref, ExplorerTreeRoles.REF)
    it.setData(pinned, ExplorerTreeRoles.PINNED)
    it.setEditable(False)
    return it


def _folder(
    label: str,
    section: ExplorerSection,
    path: tuple[str, ...],
) -> QStandardItem:
    return _item(label, kind=ExplorerNodeKind.FOLDER, payload=None, section=section, path=path)


def _project_branch(project_name: str, project_id: str) -> QStandardItem:
    base_path = ("Projects", project_name)
    sec = ExplorerSection.PROJECTS
    root = _folder(project_name, sec, base_path)
    root.setData(project_id, ExplorerTreeRoles.PAYLOAD)

    children: list[tuple[str, str, str | None]] = [
        ("Overview", ExplorerNodeKind.PROJECT_OVERVIEW, f"{project_id}/overview"),
        ("Agents", ExplorerNodeKind.PROJECT_AGENTS, f"{project_id}/agents"),
        ("Workflows", ExplorerNodeKind.PROJECT_WORKFLOWS, f"{project_id}/workflows"),
        ("Chains", ExplorerNodeKind.PROJECT_CHAINS, f"{project_id}/chains"),
        ("Files", ExplorerNodeKind.PROJECT_FILES, f"{project_id}/files"),
        ("Datasets", ExplorerNodeKind.PROJECT_DATASETS, f"{project_id}/datasets"),
        ("Runs", ExplorerNodeKind.PROJECT_RUNS, f"{project_id}/runs"),
    ]
    for title, kind, pl in children:
        path = base_path + (title,)
        root.appendRow(_item(title, kind=kind, payload=pl, section=sec, path=path))
    return root


def _favorite_row(ref: ExplorerItemRef) -> QStandardItem:
    label = ref.path_labels[-1] if ref.path_labels else ref.kind
    path = ("Favorites", label)
    it = _item(label, kind=ref.kind, payload=ref.payload, section=ref.section, path=path, pinned=True)
    return it


def _recent_row(ref: ExplorerItemRef) -> QStandardItem:
    label = ref.path_labels[-1] if ref.path_labels else ref.kind
    path = ("Recent", label)
    return _item(label, kind=ref.kind, payload=ref.payload, section=ref.section, path=path)


def create_explorer_tree_model(
    project_names: Sequence[tuple[str, str]] | None = None,
    *,
    favorites: Sequence[ExplorerItemRef] | None = None,
    recent: Sequence[ExplorerItemRef] | None = None,
) -> QStandardItemModel:
    """
    Build the explorer model.

    Args:
        project_names: ``(display_name, stable_id)`` pairs; defaults to one sample project.
        favorites: Pinned refs (same shape as tree leaves for routing).
        recent: Last opened refs (newest first).

    Injection point: load projects from settings or DB and pass them here.
    """
    if project_names is None:
        project_names = (("Project A", "project-a"),)
    if favorites is None:
        favorites = ()
    if recent is None:
        recent = ()

    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Name"])

    fav_root = _folder("Favorites", ExplorerSection.FAVORITES, ("Favorites",))
    for r in favorites:
        fav_root.appendRow(_favorite_row(r))

    recent_root = _folder("Recent", ExplorerSection.RECENT, ("Recent",))
    for r in recent:
        recent_root.appendRow(_recent_row(r))

    projects = _folder("Projects", ExplorerSection.PROJECTS, ("Projects",))
    for name, pid in project_names:
        projects.appendRow(_project_branch(name, pid))

    library = _folder("Library", ExplorerSection.LIBRARY, ("Library",))
    workflows = _folder("Workflows", ExplorerSection.LIBRARY, ("Library", "Workflows"))
    task_nodes: list[tuple[str, str, str]] = [
        ("Test Agent", ExplorerNodeKind.WF_TEST_AGENT, "demo-agent"),
        ("Knowledge Base", ExplorerNodeKind.WF_KNOWLEDGE_BASE, "new-kb"),
        ("Build Workflow", ExplorerNodeKind.WF_BUILD_WORKFLOW, "draft"),
        ("Develop Prompt", ExplorerNodeKind.WF_PROMPT_DEV, "draft"),
        ("Compare Models", ExplorerNodeKind.WF_MODEL_COMPARE, "session-1"),
    ]
    for title, kind, payload in task_nodes:
        path = ("Library", "Workflows", title)
        workflows.appendRow(_item(title, kind=kind, payload=payload, section=ExplorerSection.LIBRARY, path=path))
    library.appendRow(workflows)

    lib_nodes = [
        ("Models", ExplorerNodeKind.LIB_MODELS, "library/models"),
        ("Prompts", ExplorerNodeKind.LIB_PROMPTS, "library/prompts"),
        ("Tools", ExplorerNodeKind.LIB_TOOLS, "library/tools"),
        ("Templates", ExplorerNodeKind.LIB_TEMPLATES, "library/templates"),
        ("Knowledge Bases", ExplorerNodeKind.LIB_KNOWLEDGE, "library/knowledge"),
    ]
    for title, kind, payload in lib_nodes:
        path = ("Library", title)
        library.appendRow(_item(title, kind=kind, payload=payload, section=ExplorerSection.LIBRARY, path=path))

    runtime = _folder("Runtime", ExplorerSection.RUNTIME, ("Runtime",))
    rt_nodes = [
        ("Active Sessions", ExplorerNodeKind.RT_SESSIONS, "runtime/sessions"),
        ("Agent Runs", ExplorerNodeKind.RT_AGENT_RUNS, "runtime/agent-runs"),
        ("Workflow Runs", ExplorerNodeKind.RT_WORKFLOW_RUNS, "runtime/workflow-runs"),
        ("Background Tasks", ExplorerNodeKind.RT_BACKGROUND, "runtime/background"),
        ("Logs", ExplorerNodeKind.RT_LOGS, "runtime/logs"),
    ]
    for title, kind, payload in rt_nodes:
        path = ("Runtime", title)
        runtime.appendRow(_item(title, kind=kind, payload=payload, section=ExplorerSection.RUNTIME, path=path))

    system = _folder("System", ExplorerSection.SYSTEM, ("System",))
    sys_nodes = [
        ("Settings", ExplorerNodeKind.SYS_SETTINGS, "system/settings"),
        ("Providers", ExplorerNodeKind.SYS_PROVIDERS, "system/providers"),
        ("Debug", ExplorerNodeKind.SYS_DEBUG, "system/debug"),
        ("Health", ExplorerNodeKind.SYS_HEALTH, "system/health"),
    ]
    for title, kind, payload in sys_nodes:
        path = ("System", title)
        system.appendRow(_item(title, kind=kind, payload=payload, section=ExplorerSection.SYSTEM, path=path))

    model.appendRow(fav_root)
    model.appendRow(recent_root)
    model.appendRow(projects)
    model.appendRow(library)
    model.appendRow(runtime)
    model.appendRow(system)
    return model
