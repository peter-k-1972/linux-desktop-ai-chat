"""Regression: Critic-Modus darf bei enabled=True nicht still fehlschlagen."""

import logging

import pytest

from app.critic import CriticConfig, review_response
from app.core.models.roles import ModelRole


@pytest.mark.asyncio
async def test_review_response_disabled_returns_unchanged() -> None:
    cfg = CriticConfig(enabled=False)
    out = await review_response("hello", cfg, chat_fn=None)
    assert out == "hello"


@pytest.mark.asyncio
async def test_review_response_enabled_logs_and_returns_primary(caplog: pytest.LogCaptureFixture) -> None:
    """Remediation: kein TODO-Stilleffekt — Warnung + gleiche Antwort."""
    cfg = CriticConfig(enabled=True, critic_role=ModelRole.THINK)
    caplog.set_level(logging.WARNING)
    out = await review_response("primary text", cfg, chat_fn=None)
    assert out == "primary text"
    assert any("app.critic.review_response" in r.message for r in caplog.records)
