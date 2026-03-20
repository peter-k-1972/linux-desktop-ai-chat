"""
Failure Injection: Prompt-Service Save/Load/Delete schlägt fehl.

Simuliert: Storage-Backend wirft Exception (DB-Fehler, Dateisystem-Fehler).
Erwartung: Fehler wird abgefangen, Service gibt None/False/[] zurück,
UI-State bleibt konsistent, kein Crash.
"""

from unittest.mock import MagicMock

import pytest

from app.prompts.prompt_models import Prompt
from app.prompts.prompt_service import PromptService
from app.prompts.storage_backend import PromptStorageBackend


class FailingBackend(PromptStorageBackend):
    """Backend das bei allen Operationen Exception wirft."""

    def create(self, prompt):
        raise OSError("Disk full")

    def update(self, prompt):
        raise RuntimeError("Storage unavailable")

    def delete(self, prompt_id):
        raise PermissionError("Access denied")

    def get(self, prompt_id):
        raise ValueError("Corrupted data")

    def list_all(self, filter_text="", category=None):
        raise ConnectionError("Database unreachable")


@pytest.mark.failure_mode
def test_prompt_service_create_handles_failure():
    """Save (create) schlägt fehl → Service gibt None zurück, kein Crash."""
    service = PromptService(backend=FailingBackend())
    prompt = Prompt.empty()
    prompt.title = "Test"
    prompt.content = "x"

    result = service.create(prompt)

    assert result is None


@pytest.mark.failure_mode
def test_prompt_service_update_handles_failure():
    """Update schlägt fehl → Service gibt False zurück, kein Crash."""
    service = PromptService(backend=FailingBackend())
    prompt = Prompt.empty()
    prompt.id = 1
    prompt.title = "Test"
    prompt.content = "x"

    result = service.update(prompt)

    assert result is False


@pytest.mark.failure_mode
def test_prompt_service_delete_handles_failure():
    """Delete schlägt fehl → Service gibt False zurück, kein Crash."""
    service = PromptService(backend=FailingBackend())

    result = service.delete(123)

    assert result is False


@pytest.mark.failure_mode
def test_prompt_service_get_handles_failure():
    """Load (get) schlägt fehl → Service gibt None zurück, kein Crash."""
    service = PromptService(backend=FailingBackend())

    result = service.get(1)

    assert result is None


@pytest.mark.failure_mode
def test_prompt_service_list_all_handles_failure():
    """list_all schlägt fehl → Service gibt [] zurück, kein Crash."""
    service = PromptService(backend=FailingBackend())

    result = service.list_all()

    assert result == []
