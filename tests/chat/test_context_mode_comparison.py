"""
Test Harness: Vergleichbarkeit der Kontextmodi.

Gleicher Input → unterschiedliche Modi → vergleichbare Outputs.
Mock Provider verwenden.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.config.settings import ChatContextDetailLevel, ChatContextMode
from app.chat.context import (
    ChatRequestContext,
    inject_chat_context_into_messages,
)


# Fester Input für alle Modi
MESSAGES = [
    {"role": "user", "content": "Erkläre mir die Architektur dieses Systems"}
]

CONTEXT = ChatRequestContext(
    project_name="Linux-Desktop-Chat",
    chat_title="Architektur-Diskussion",
    topic_name="Backend-Services",
)


def _produce_output_off() -> list:
    """OFF: Keine Injektion."""
    return list(MESSAGES)


def _produce_output_neutral() -> list:
    """NEUTRAL: Nüchternes Fragment injizieren."""
    fragment = CONTEXT.to_system_prompt_fragment(ChatContextMode.NEUTRAL)
    return inject_chat_context_into_messages(list(MESSAGES), fragment)


def _produce_output_semantic() -> list:
    """SEMANTIC FULL: Semantisch angereichertes Fragment injizieren."""
    fragment = CONTEXT.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC,
        ChatContextDetailLevel.FULL,
    )
    return inject_chat_context_into_messages(list(MESSAGES), fragment)


def test_context_mode_comparison_same_input_different_outputs():
    """
    Gleicher Input → unterschiedliche Modi → messbar unterschiedliche Outputs.
    """
    output_off = _produce_output_off()
    output_neutral = _produce_output_neutral()
    output_semantic = _produce_output_semantic()

    # OFF enthält KEIN Kontextfragment
    assert len(output_off) == 1
    assert output_off[0]["role"] == "user"
    assert "Kontext:" not in str(output_off)
    assert "Arbeitskontext" not in str(output_off)
    assert "Berücksichtige" not in str(output_off)

    # NEUTRAL enthält KEINE semantischen Zusätze
    assert len(output_neutral) == 2
    content_neutral = output_neutral[0].get("content", "")
    assert "Kontext:" in content_neutral
    assert "Arbeitskontext" not in content_neutral
    assert "Themenbereich" not in content_neutral
    assert "Berücksichtige diesen Kontext" not in content_neutral

    # SEMANTIC enthält Arbeitskontext und Berücksichtige
    assert len(output_semantic) == 2
    content_semantic = output_semantic[0].get("content", "")
    assert "Arbeitskontext" in content_semantic
    assert "Berücksichtige diesen Kontext" in content_semantic


def test_context_mode_comparison_with_mock_provider():
    """
    Mit Mock-Settings: ChatService-Flow liefert vergleichbare Modi.
    """
    from app.services.infrastructure import set_infrastructure, _ServiceInfrastructure
    from app.core.config.settings import AppSettings
    from app.core.config.settings_backend import InMemoryBackend
    from app.services.chat_service import ChatService

    infra = MagicMock(spec=_ServiceInfrastructure)
    backend = InMemoryBackend()

    def _inject_for_mode(mode: str):
        backend.setValue("chat_context_mode", mode)
        backend.setValue("chat_context_detail_level", "full")
        settings = AppSettings(backend=backend)
        infra.settings = settings
        infra._settings = settings
        set_infrastructure(infra)
        svc = ChatService()
        svc._infra = infra
        return svc._inject_chat_context(
            [{"role": "user", "content": "Erkläre mir die Architektur dieses Systems"}],
            chat_id=1,
        )

    # Mock build_chat_context to return our fixed context
    with patch("app.chat.context.build_chat_context", return_value=CONTEXT):
        out_off = _inject_for_mode("off")
        out_neutral = _inject_for_mode("neutral")
        out_semantic = _inject_for_mode("semantic")

    assert len(out_off) == 1
    assert "Kontext:" not in str(out_off)
    assert "Arbeitskontext" not in str(out_off)

    assert "Kontext:" in out_neutral[0]["content"]
    assert "Arbeitskontext" not in out_neutral[0]["content"]

    assert "Arbeitskontext" in out_semantic[0]["content"]
    assert "Berücksichtige diesen Kontext" in out_semantic[0]["content"]
