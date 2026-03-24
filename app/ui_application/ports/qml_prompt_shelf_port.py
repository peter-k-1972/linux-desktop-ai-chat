"""
QML Prompt Studio (Regal/Lesepult) — schmale Port-Schnittstelle.

Qt-frei; arbeitet mit :class:`app.prompts.prompt_models.Prompt`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.prompts.prompt_models import Prompt


@runtime_checkable
class QmlPromptShelfOperationsPort(Protocol):
    def list_prompts(self, filter_text: str = "") -> list[Prompt]:
        ...

    def get_prompt(self, prompt_id: int) -> Prompt | None:
        ...

    def create_prompt(self, prompt: Prompt) -> Prompt | None:
        ...

    def update_prompt(self, prompt: Prompt) -> bool:
        ...

    def list_prompt_versions(self, prompt_id: int) -> list[dict]:
        ...
