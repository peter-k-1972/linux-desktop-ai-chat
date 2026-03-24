"""Adapter: :class:`QmlPromptShelfOperationsPort` → :class:`app.prompts.prompt_service.PromptService`."""

from __future__ import annotations

from app.prompts.prompt_models import Prompt


class ServiceQmlPromptShelfAdapter:
    def list_prompts(self, filter_text: str = "") -> list[Prompt]:
        from app.prompts.prompt_service import get_prompt_service

        return get_prompt_service().list_all(filter_text=filter_text or "")

    def get_prompt(self, prompt_id: int) -> Prompt | None:
        from app.prompts.prompt_service import get_prompt_service

        return get_prompt_service().get(prompt_id)

    def create_prompt(self, prompt: Prompt) -> Prompt | None:
        from app.prompts.prompt_service import get_prompt_service

        return get_prompt_service().create(prompt)

    def update_prompt(self, prompt: Prompt) -> bool:
        from app.prompts.prompt_service import get_prompt_service

        return get_prompt_service().update(prompt)

    def list_prompt_versions(self, prompt_id: int) -> list[dict]:
        from app.prompts.prompt_service import get_prompt_service

        return get_prompt_service().list_versions(prompt_id)
