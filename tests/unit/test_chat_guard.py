"""
Unit Tests: Chat Guard v1 und v2.

Prüft:
- Slash/Command wird erkannt
- formale Frage wird als formal_reasoning markiert
- Coding-Frage wird passend erkannt
- riskante Wissensfrage erhält sanity-/mismatch-Flag
- Prompt-Härtung wird korrekt angewendet
- normale Chatfrage bleibt normal
- v2: Fusion, Feature-Flag, niedrige Confidence
"""

import pytest

from app.core.chat_guard.heuristics import assess_intent
from app.core.chat_guard.intent_model import ChatIntent, GuardResult
from app.core.chat_guard.sanity_check import run_sanity_check
from app.core.chat_guard.prompt_hardening import apply_prompt_hardening
from app.core.chat_guard.service import ChatGuardService


class TestHeuristics:
    def test_slash_command_recognized(self):
        intent, flags = assess_intent("/think Erkläre mir das")
        assert intent == ChatIntent.COMMAND
        assert "command_unrecognized" not in flags

    def test_slash_unknown_command_risk(self):
        intent, flags = assess_intent("/xyz unbekannter Befehl")
        assert intent == ChatIntent.COMMAND
        assert "command_unrecognized" in flags

    def test_formal_reasoning_recognized(self):
        intent, _ = assess_intent("Beweise, dass 2+2=4 ist.")
        assert intent == ChatIntent.FORMAL_REASONING

    def test_formal_axiom_recognized(self):
        intent, _ = assess_intent("Was ist das Axiom der Vollständigkeit?")
        assert intent == ChatIntent.FORMAL_REASONING

    def test_coding_recognized(self):
        intent, _ = assess_intent("Wie debugge ich einen Python Stacktrace?")
        assert intent == ChatIntent.CODING

    def test_knowledge_query_recognized(self):
        intent, flags = assess_intent("Wer schrieb Faust?")
        assert intent == ChatIntent.KNOWLEDGE_QUERY

    def test_knowledge_with_attribution_risk(self):
        intent, flags = assess_intent("Wer schrieb das Gedicht von Goethe über den Erlkönig?")
        assert intent == ChatIntent.KNOWLEDGE_QUERY
        assert "attribution_risk" in flags or "mismatch_risk" in flags

    def test_normal_chat_unchanged(self):
        intent, flags = assess_intent("Hallo, wie geht es dir?")
        assert intent == ChatIntent.CHAT
        assert not flags


class TestSanityCheck:
    def test_verify_assumptions_on_knowledge_attribution(self):
        flags = run_sanity_check(
            "Wer schrieb das Werk von Schiller?",
            "knowledge_query",
            ["mismatch_risk", "attribution_risk"],
        )
        assert "verify_assumptions" in flags

    def test_no_sanity_on_normal_chat(self):
        flags = run_sanity_check("Hallo", "chat", [])
        assert not flags


class TestPromptHardening:
    def test_formal_gets_hint(self):
        result = GuardResult(intent=ChatIntent.FORMAL_REASONING)
        result = apply_prompt_hardening(result)
        assert result.system_hint is not None
        assert "formal" in result.system_hint.lower() or "struktur" in result.system_hint.lower()

    def test_coding_gets_hint(self):
        result = GuardResult(intent=ChatIntent.CODING)
        result = apply_prompt_hardening(result)
        assert result.system_hint is not None
        assert "technisch" in result.system_hint.lower() or "präzise" in result.system_hint.lower()

    def test_knowledge_verify_gets_hint(self):
        result = GuardResult(
            intent=ChatIntent.KNOWLEDGE_QUERY,
            sanity_flags=["verify_assumptions"],
        )
        result = apply_prompt_hardening(result)
        assert result.system_hint is not None
        assert "prüfe" in result.system_hint.lower() or "annahmen" in result.system_hint.lower()

    def test_chat_no_hint(self):
        result = GuardResult(intent=ChatIntent.CHAT)
        result = apply_prompt_hardening(result)
        assert result.system_hint is None


class TestChatGuardService:
    def test_assess_normal_chat(self):
        guard = ChatGuardService()
        result = guard.assess("Hallo, was machst du?")
        assert result.intent == ChatIntent.CHAT
        assert result.system_hint is None

    def test_assess_formal_gets_hint(self):
        guard = ChatGuardService()
        result = guard.assess("Beweise den Satz des Pythagoras.")
        assert result.intent == ChatIntent.FORMAL_REASONING
        assert result.system_hint is not None

    def test_apply_to_messages_adds_system_when_hint(self):
        guard = ChatGuardService()
        result = guard.assess("Beweise dass 1+1=2.")
        messages = [{"role": "user", "content": "Beweise dass 1+1=2."}]
        out = guard.apply_to_messages(messages, result)
        assert len(out) == 2
        assert out[0]["role"] == "system"
        assert out[1]["role"] == "user"

    def test_apply_to_messages_unchanged_when_no_hint(self):
        guard = ChatGuardService()
        result = guard.assess("Hallo")
        messages = [{"role": "user", "content": "Hallo"}]
        out = guard.apply_to_messages(messages, result)
        assert out == messages


class TestNoRegression:
    """Keine Regression im bestehenden Chatpfad."""

    def test_guard_does_not_block_normal_chat(self):
        """Normale Chatfrage wird nicht blockiert, kein Hint."""
        guard = ChatGuardService()
        result = guard.assess("Erzähl mir einen Witz.")
        assert result.intent == ChatIntent.CHAT
        assert result.system_hint is None

    def test_guard_apply_empty_messages_unchanged(self):
        """Leere Message-Liste bleibt unverändert."""
        guard = ChatGuardService()
        result = GuardResult(intent=ChatIntent.FORMAL_REASONING, system_hint="Test")
        out = guard.apply_to_messages([], result)
        assert out == []


class TestFusion:
    """Entscheidungsfusion: Heuristik + ML."""

    def test_heuristic_command_wins_over_ml(self):
        """Command von Heuristik gewinnt immer."""
        from app.core.chat_guard.fusion import fuse
        final, source = fuse(
            ChatIntent.COMMAND,
            [],
            ChatIntent.CODING,
            0.9,
            True,
        )
        assert final == ChatIntent.COMMAND
        assert source == "heuristic"

    def test_low_ml_confidence_fallback_to_heuristic(self):
        """Niedrige ML-Confidence → Heuristik."""
        from app.core.chat_guard.fusion import fuse
        final, source = fuse(
            ChatIntent.CODING,
            [],
            ChatIntent.CHAT,
            0.3,
            True,
        )
        assert final == ChatIntent.CODING
        assert source == "fallback"

    def test_heuristic_chat_ml_high_confidence_uses_ml(self):
        """Heuristik chat, ML hohe Confidence → ML."""
        from app.core.chat_guard.fusion import fuse
        final, source = fuse(
            ChatIntent.CHAT,
            [],
            ChatIntent.CODING,
            0.8,
            True,
        )
        assert final == ChatIntent.CODING
        assert source == "ml"

    def test_conflict_heuristic_wins(self):
        """Widerspruch: Heuristik gewinnt."""
        from app.core.chat_guard.fusion import fuse
        final, source = fuse(
            ChatIntent.FORMAL_REASONING,
            [],
            ChatIntent.CODING,
            0.7,
            True,
        )
        assert final == ChatIntent.FORMAL_REASONING
        assert source == "fusion"

    def test_ml_disabled_uses_heuristic(self):
        """ML deaktiviert → nur Heuristik."""
        from app.core.chat_guard.fusion import fuse
        final, source = fuse(
            ChatIntent.CODING,
            [],
            ChatIntent.CHAT,
            0.9,
            False,
        )
        assert final == ChatIntent.CODING
        assert source == "heuristic"


class TestMLClassifier:
    """ML-Intent-Klassifikator (ohne echte Embeddings)."""

    @pytest.mark.asyncio
    async def test_classifier_fails_gracefully_without_embedding(self):
        """Ohne Embedding-Service: (CHAT, 0.0)."""
        from app.core.chat_guard.ml_intent_classifier import MLIntentClassifier

        class FailingEmbedding:
            async def embed(self, text):
                raise Exception("no embedding")

            async def embed_batch(self, texts):
                raise Exception("no embedding")

        classifier = MLIntentClassifier(embedding_service=FailingEmbedding())
        intent, conf = await classifier.classify("Beweise dass 2+2=4")
        assert intent == ChatIntent.CHAT
        assert conf == 0.0


class TestGuardResultDebug:
    """Debug-Metadaten."""

    def test_guard_result_to_debug_dict(self):
        """Debug-Dict enthält heuristic_intent, ml_intent, decision_source."""
        from app.core.chat_guard.debug import guard_result_to_debug_dict

        result = GuardResult(
            intent=ChatIntent.CODING,
            heuristic_intent=ChatIntent.CHAT,
            ml_intent=ChatIntent.CODING,
            ml_confidence=0.85,
            decision_source="ml",
        )
        d = guard_result_to_debug_dict(result)
        assert d["intent"] == "coding"
        assert d["heuristic_intent"] == "chat"
        assert d["ml_intent"] == "coding"
        assert d["ml_confidence"] == 0.85
        assert d["decision_source"] == "ml"


class TestChatServiceGuardIntegration:
    """ChatService ruft Guard vor Modellaufruf auf."""

    @pytest.mark.asyncio
    async def test_chat_service_applies_guard_async(self):
        """_apply_chat_guard (async) fügt System-Hint bei formaler Frage hinzu."""
        from unittest.mock import MagicMock
        from app.services.chat_service import ChatService
        from app.services.infrastructure import set_infrastructure
        from app.core.config.settings import AppSettings

        async def fake_chat(*a, **k):
            yield {"message": {"content": "ok", "thinking": ""}, "done": True}

        infra = MagicMock()
        infra.ollama_client = MagicMock()
        infra.ollama_client.chat = fake_chat
        infra.database = MagicMock()
        infra.settings = AppSettings()

        set_infrastructure(infra)
        try:
            svc = ChatService()
            messages = [{"role": "user", "content": "Beweise dass 2+2=4."}]
            out = await svc._apply_chat_guard(messages)
            assert len(out) >= 2
            assert out[0]["role"] == "system"
            assert "formal" in out[0]["content"].lower() or "struktur" in out[0]["content"].lower()
        finally:
            set_infrastructure(None)
