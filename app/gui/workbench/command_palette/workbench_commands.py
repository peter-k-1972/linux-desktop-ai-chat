"""
Default Workbench palette commands (navigation, actions, create, system).

Handlers stay thin: they only touch the Workbench shell and canvas router.
"""

from __future__ import annotations

from PySide6.QtWidgets import QInputDialog

from app.gui.themes import get_theme_manager
from app.gui.workbench.command_palette.command_context import WorkbenchCommandContext
from app.gui.workbench.command_palette.command_item import CommandCategory, CommandDefinition
from app.gui.workbench.command_palette.command_registry import WorkbenchCommandRegistry
from app.gui.workbench.focus.active_object import (
    OBJECT_AGENT,
    OBJECT_AI_CANVAS,
    OBJECT_KNOWLEDGE_BASE,
    OBJECT_MODEL_COMPARE,
    OBJECT_PROMPT,
    OBJECT_WORKFLOW,
)
from app.gui.workbench.focus.contextual_actions import contextual_action_tuples


def _palette_ctx_run_primary(ctx: WorkbenchCommandContext) -> None:
    acts = contextual_action_tuples(ctx.window, ctx.active_object)
    if acts:
        acts[0][1]()


def _palette_ctx_action(ctx: WorkbenchCommandContext, label: str) -> None:
    for lbl, fn in contextual_action_tuples(ctx.window, ctx.active_object):
        if lbl == label:
            fn()
            return


def register_workbench_commands(registry: WorkbenchCommandRegistry) -> None:
    registry.register(
        CommandDefinition(
            id="nav.agent_manager",
            label="Open Agent Manager",
            category=CommandCategory.NAVIGATION,
            handler=lambda ctx: ctx.canvas_router.open_feature_page("nav/agent-manager", "Agent Manager"),
            keywords=("agents", "registry"),
        )
    )
    registry.register(
        CommandDefinition(
            id="nav.workflow_editor",
            label="Open Workflow Builder",
            category=CommandCategory.NAVIGATION,
            handler=lambda ctx: ctx.canvas_router.open_workflow_builder(),
            keywords=("flows", "automation", "graph"),
        )
    )
    registry.register(
        CommandDefinition(
            id="nav.prompt_library",
            label="Open Prompt Library",
            category=CommandCategory.NAVIGATION,
            handler=lambda ctx: ctx.canvas_router.open_prompt_development(),
            keywords=("prompts", "templates", "library"),
        )
    )
    registry.register(
        CommandDefinition(
            id="nav.logs",
            label="Open Logs",
            category=CommandCategory.NAVIGATION,
            handler=lambda ctx: ctx.window.focus_console(),
            keywords=("console", "output", "runtime"),
        )
    )
    registry.register(
        CommandDefinition(
            id="nav.ai_canvas",
            label="Open AI Canvas",
            category=CommandCategory.NAVIGATION,
            handler=lambda ctx: ctx.canvas_router.open_ai_flow_editor(),
            keywords=("graph", "langflow", "nodes", "experimental"),
        )
    )

    registry.register(
        CommandDefinition(
            id="wf.test_agent",
            label="Test Agent",
            category=CommandCategory.WORKFLOWS,
            handler=lambda ctx: ctx.canvas_router.open_agent_test(),
            keywords=("agent", "chat", "try"),
        )
    )
    registry.register(
        CommandDefinition(
            id="wf.create_knowledge_base",
            label="Create Knowledge Base",
            category=CommandCategory.WORKFLOWS,
            handler=lambda ctx: _palette_create_knowledge_base(ctx),
            keywords=("rag", "index", "embeddings"),
        )
    )
    registry.register(
        CommandDefinition(
            id="wf.build_workflow",
            label="Build Workflow",
            category=CommandCategory.WORKFLOWS,
            handler=lambda ctx: ctx.canvas_router.open_workflow_builder(),
            keywords=("nodes", "canvas", "design"),
        )
    )
    registry.register(
        CommandDefinition(
            id="wf.develop_prompt",
            label="Develop Prompt",
            category=CommandCategory.WORKFLOWS,
            handler=lambda ctx: ctx.canvas_router.open_prompt_development(),
            keywords=("iterate", "template"),
        )
    )
    registry.register(
        CommandDefinition(
            id="wf.compare_models",
            label="Compare Models",
            category=CommandCategory.WORKFLOWS,
            handler=lambda ctx: ctx.canvas_router.open_model_compare(),
            keywords=("benchmark", "side", "by", "side"),
        )
    )

    registry.register(
        CommandDefinition(
            id="action.run_agent",
            label="Run Agent",
            category=CommandCategory.ACTIONS,
            handler=_palette_ctx_run_primary,
            enabled_when=lambda ctx: ctx.active_object.object_type == OBJECT_AGENT,
            keywords=("execute", "agent", "run"),
        )
    )
    registry.register(
        CommandDefinition(
            id="action.run_workflow",
            label="Execute Workflow",
            category=CommandCategory.ACTIONS,
            handler=_palette_ctx_run_primary,
            enabled_when=lambda ctx: ctx.active_object.object_type
            in (OBJECT_WORKFLOW, OBJECT_AI_CANVAS),
            keywords=("run", "workflow", "execute"),
        )
    )
    registry.register(
        CommandDefinition(
            id="ctx.run_primary",
            label="Run · Primary action (active object)",
            category=CommandCategory.ACTIONS,
            handler=_palette_ctx_run_primary,
            enabled_when=lambda ctx: not ctx.active_object.is_empty()
            and len(contextual_action_tuples(ctx.window, ctx.active_object)) > 0,
            keywords=("f5", "execute", "context"),
        )
    )
    registry.register(
        CommandDefinition(
            id="ctx.agent.reset_context",
            label="Agent: Reset Context",
            category=CommandCategory.ACTIONS,
            handler=lambda ctx: _palette_ctx_action(ctx, "Reset Context"),
            enabled_when=lambda ctx: ctx.active_object.object_type == OBJECT_AGENT,
            keywords=("clear", "session"),
        )
    )
    registry.register(
        CommandDefinition(
            id="ctx.workflow.validate",
            label="Workflow: Validate",
            category=CommandCategory.ACTIONS,
            handler=lambda ctx: _palette_ctx_action(ctx, "Validate"),
            enabled_when=lambda ctx: ctx.active_object.object_type == OBJECT_WORKFLOW,
            keywords=("check", "graph"),
        )
    )
    registry.register(
        CommandDefinition(
            id="ctx.prompt.save",
            label="Prompt: Save",
            category=CommandCategory.ACTIONS,
            handler=lambda ctx: _palette_ctx_action(ctx, "Save"),
            enabled_when=lambda ctx: ctx.active_object.object_type == OBJECT_PROMPT,
            keywords=("draft", "write"),
        )
    )
    registry.register(
        CommandDefinition(
            id="ctx.kb.add_files",
            label="Knowledge Base: Add Files",
            category=CommandCategory.ACTIONS,
            handler=lambda ctx: _palette_ctx_action(ctx, "Add Files"),
            enabled_when=lambda ctx: ctx.active_object.object_type == OBJECT_KNOWLEDGE_BASE,
            keywords=("upload", "documents"),
        )
    )
    registry.register(
        CommandDefinition(
            id="ctx.kb.reindex",
            label="Knowledge Base: Reindex",
            category=CommandCategory.ACTIONS,
            handler=lambda ctx: _palette_ctx_action(ctx, "Reindex"),
            enabled_when=lambda ctx: ctx.active_object.object_type == OBJECT_KNOWLEDGE_BASE,
            keywords=("embed", "index"),
        )
    )
    registry.register(
        CommandDefinition(
            id="ctx.compare.run",
            label="Compare Models: Run Comparison",
            category=CommandCategory.ACTIONS,
            handler=_palette_ctx_run_primary,
            enabled_when=lambda ctx: ctx.active_object.object_type == OBJECT_MODEL_COMPARE,
            keywords=("benchmark", "side"),
        )
    )
    registry.register(
        CommandDefinition(
            id="action.clear_console",
            label="Clear Console",
            category=CommandCategory.ACTIONS,
            handler=lambda ctx: ctx.window.console_panel.clear(),
            keywords=("terminal", "output"),
        )
    )

    registry.register(
        CommandDefinition(
            id="create.agent",
            label="Create Agent",
            category=CommandCategory.CREATE,
            handler=lambda ctx: ctx.canvas_router.open_agent("new-agent"),
            keywords=("new",),
        )
    )
    registry.register(
        CommandDefinition(
            id="create.workflow",
            label="Create Workflow",
            category=CommandCategory.CREATE,
            handler=lambda ctx: ctx.canvas_router.open_workflow_builder("new-workflow"),
            keywords=("new", "graph"),
        )
    )
    registry.register(
        CommandDefinition(
            id="create.chain",
            label="Create Chain",
            category=CommandCategory.CREATE,
            handler=lambda ctx: ctx.canvas_router.open_feature_page("create/chain", "New Chain"),
            keywords=("new",),
        )
    )
    registry.register(
        CommandDefinition(
            id="create.project",
            label="Create Project",
            category=CommandCategory.CREATE,
            handler=lambda ctx: ctx.canvas_router.open_feature_page("create/project", "New Project"),
            keywords=("new",),
        )
    )

    registry.register(
        CommandDefinition(
            id="system.settings",
            label="Open Settings",
            category=CommandCategory.SYSTEM,
            handler=lambda ctx: ctx.canvas_router.open_feature_page("system/settings", "Settings"),
            keywords=("preferences",),
        )
    )
    registry.register(
        CommandDefinition(
            id="system.toggle_inspector",
            label="Toggle Inspector",
            category=CommandCategory.SYSTEM,
            handler=lambda ctx: ctx.window.toggle_inspector(),
            keywords=("sidebar", "right"),
        )
    )
    registry.register(
        CommandDefinition(
            id="system.toggle_console",
            label="Toggle Console",
            category=CommandCategory.SYSTEM,
            handler=lambda ctx: ctx.window.toggle_console(),
            keywords=("panel", "bottom"),
        )
    )
    registry.register(
        CommandDefinition(
            id="system.reload_theme",
            label="Reload Theme",
            category=CommandCategory.SYSTEM,
            handler=lambda ctx: _reload_theme(ctx),
            keywords=("style", "css", "appearance"),
        )
    )


def _palette_create_knowledge_base(ctx: WorkbenchCommandContext) -> None:
    name, ok = QInputDialog.getText(ctx.window, "Knowledge base", "Name:")
    if not ok:
        return
    label = name.strip() or "New knowledge base"
    slug = label.lower().replace(" ", "-")[:48] or "new-kb"
    ctx.canvas_router.open_knowledge_base_workflow(kb_id=slug, display_name=label)


def _reload_theme(ctx: WorkbenchCommandContext) -> None:
    mgr = get_theme_manager()
    mgr.set_theme(mgr.get_current_id())
    ctx.window.console_panel.log_output("Theme reloaded.")
