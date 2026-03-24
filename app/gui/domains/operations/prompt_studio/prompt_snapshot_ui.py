"""
Snapshot-DTO → ``Prompt`` für reine UI-Konstruktion (Batch 8).

Kein Service, kein Qt, keine Workspace-/Panel-Imports — vermeidet Importzyklen.
"""

from __future__ import annotations

from app.prompts.prompt_models import Prompt
from app.ui_contracts.workspaces.prompt_studio_editor import PromptStudioPromptSnapshotDto


def prompt_from_snapshot(dto: PromptStudioPromptSnapshotDto) -> Prompt:
    return Prompt(
        id=dto.prompt_id,
        title=dto.title,
        category=dto.category,
        description=dto.description,
        content=dto.content,
        tags=list(dto.tags),
        prompt_type=dto.prompt_type,
        scope=dto.scope,
        project_id=dto.project_id,
        created_at=None,
        updated_at=None,
    )
