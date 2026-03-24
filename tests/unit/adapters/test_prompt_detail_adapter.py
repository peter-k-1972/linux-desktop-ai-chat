"""ServicePromptStudioAdapter — load_prompt_detail (Slice 2)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.prompts.prompt_models import Prompt
from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter


@pytest.fixture
def adapter() -> ServicePromptStudioAdapter:
    return ServicePromptStudioAdapter()


def test_load_prompt_detail_empty_raises(adapter: ServicePromptStudioAdapter) -> None:
    with pytest.raises(ValueError):
        adapter.load_prompt_detail("", None)


def test_load_prompt_detail_maps_prompt(monkeypatch: pytest.MonkeyPatch, adapter: ServicePromptStudioAdapter) -> None:
    now = datetime.now(timezone.utc)
    pr = Prompt(
        id=3,
        title="Hi",
        category="general",
        description="d",
        content="body",
        tags=[],
        prompt_type="user",
        scope="global",
        project_id=None,
        created_at=now,
        updated_at=now,
    )

    class _S:
        def get(self, pid: int):
            assert pid == 3
            return pr

        def list_versions(self, pid: int):
            assert pid == 3
            return [{"version": 1}]

        def count_versions(self, pid: int):
            return 2

    monkeypatch.setattr(
        "app.prompts.prompt_service.get_prompt_service",
        lambda: _S(),
    )
    dto = adapter.load_prompt_detail("3", None)
    assert dto.prompt_id == "3"
    assert dto.name == "Hi"
    assert dto.version_count == 2
    assert dto.last_modified is not None


def test_load_prompt_detail_not_found(monkeypatch: pytest.MonkeyPatch, adapter: ServicePromptStudioAdapter) -> None:
    class _S:
        def get(self, pid: int):
            return None

    monkeypatch.setattr(
        "app.prompts.prompt_service.get_prompt_service",
        lambda: _S(),
    )
    with pytest.raises(LookupError):
        adapter.load_prompt_detail("99", None)
