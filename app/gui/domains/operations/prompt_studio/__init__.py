"""Prompt Studio – Operations Prompt Studio Workspace.

``PromptStudioWorkspace`` wird erst bei Zugriff geladen, damit
``inspector → prompt_version_panel → package`` nicht mit
``workspace → prompt_inspector_panel → PromptStudioInspector`` kollidiert.
"""

from __future__ import annotations

__all__ = ["PromptStudioWorkspace"]


def __getattr__(name: str):
    if name == "PromptStudioWorkspace":
        from app.gui.domains.operations.prompt_studio.prompt_studio_workspace import (
            PromptStudioWorkspace,
        )

        return PromptStudioWorkspace
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
