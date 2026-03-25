"""
Prompt Studio — Workspace: Neuanlage / Kontext-Öffnen (Batch 3, Qt-frei).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.ui_contracts.workspaces.prompt_studio_editor import PromptStudioPromptSnapshotDto


@dataclass(frozen=True, slots=True)
class PromptStudioWorkspaceOpResult:
    """Ergebnis von create/open über den Port (Presenter gibt an Workspace zurück)."""

    ok: bool
    error_message: str | None = None
    snapshot: PromptStudioPromptSnapshotDto | None = None


__all__ = ["PromptStudioWorkspaceOpResult"]
