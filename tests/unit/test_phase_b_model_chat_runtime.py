"""
Phase B: Preflight, Usage-Commit, Aggregation über model_chat_runtime (In-Memory-DB).
"""

from __future__ import annotations

import asyncio
from contextlib import contextmanager
from typing import Any, AsyncGenerator, Dict, List

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.models.orchestrator import ModelOrchestrator
from app.persistence.base import Base
from app.persistence.enums import QuotaMode, QuotaScopeType, QuotaSource, UsageStatus, UsageType
from app.persistence.orm.models import ModelQuotaPolicy, ModelUsageAggregate, ModelUsageRecord
from app.runtime.model_invocation import MODEL_INVOCATION_CHUNK_KEY
from app.services.model_chat_runtime import ERROR_KIND_POLICY_BLOCK, stream_instrumented_model_chat

pytestmark = pytest.mark.model_usage_gate


class _DummyLocalProvider:
    provider_id = "local"
    source_type = "local"

    async def get_models(self) -> List[Dict[str, Any]]:
        return []

    async def chat(self, **kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        if False:
            yield {}

    async def close(self) -> None:
        return None


class _DummyCloudProvider:
    provider_id = "ollama_cloud"
    source_type = "cloud"

    def __init__(self) -> None:
        self._api_key: str | None = None

    def has_api_key(self) -> bool:
        return bool((self._api_key or "").strip())

    def set_api_key(self, key: str | None) -> None:
        self._api_key = (key or "").strip() or None

    async def get_models(self) -> List[Dict[str, Any]]:
        return []

    async def chat(self, **kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        if False:
            yield {}

    async def close(self) -> None:
        return None


def _make_orchestrator() -> ModelOrchestrator:
    return ModelOrchestrator(
        local_provider=_DummyLocalProvider(),
        cloud_provider=_DummyCloudProvider(),
    )


@pytest.fixture
def memory_engine():
    eng = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def patch_runtime_session(memory_engine, monkeypatch):
    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)

    @contextmanager
    def scope():
        s = S()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    monkeypatch.setattr("app.services.model_chat_runtime.session_scope", scope)


def _settings_tracking_on() -> AppSettings:
    s = AppSettings(backend=InMemoryBackend())
    s.model_usage_tracking_enabled = True
    return s


@pytest.mark.asyncio
async def test_preflight_block_no_provider_call(patch_runtime_session, memory_engine):
    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as s:
        s.add(
            ModelQuotaPolicy(
                scope_type=QuotaScopeType.GLOBAL.value,
                scope_ref=None,
                mode=QuotaMode.HARD_BLOCK.value,
                source=QuotaSource.MANUAL.value,
                is_enabled=True,
                limit_total_tokens=3,
                priority=100,
            )
        )
        s.commit()

    orch = _make_orchestrator()

    async def must_not_run(**kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        raise AssertionError("Provider stream must not run when preflight blocks")
        yield {}  # pragma: no cover

    orch.stream_raw_chat = must_not_run  # type: ignore[method-assign]

    chunks: List[Dict[str, Any]] = []
    async for ch in stream_instrumented_model_chat(
        orch,
        settings=_settings_tracking_on(),
        model_id="llama2",
        messages=[{"role": "user", "content": "hello world"}],
        temperature=0.7,
        max_tokens=4096,
        stream=True,
        think=None,
        cloud_via_local=False,
        chat_id=None,
        usage_type=UsageType.CHAT.value,
    ):
        chunks.append(ch)

    assert len(chunks) == 1
    assert chunks[0].get("error_kind") == ERROR_KIND_POLICY_BLOCK
    inv = chunks[0].get(MODEL_INVOCATION_CHUNK_KEY) or {}
    assert inv.get("outcome") == "policy_block"

    with S() as s:
        rows = list(s.scalars(select(ModelUsageRecord)))
        assert len(rows) == 1
        assert rows[0].status == UsageStatus.BLOCKED.value
        assert rows[0].total_tokens == 0
        ag = list(s.scalars(select(ModelUsageAggregate)))
        assert len(ag) >= 1
        assert sum(a.blocked_count for a in ag) >= 1


@pytest.mark.asyncio
async def test_success_persists_exact_tokens_from_provider(patch_runtime_session, memory_engine):
    orch = _make_orchestrator()

    async def fake_stream(**kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        yield {
            "message": {"content": "ok", "thinking": ""},
            "done": True,
            "prompt_eval_count": 12,
            "eval_count": 34,
        }

    orch.stream_raw_chat = fake_stream  # type: ignore[method-assign]

    chunks: List[Dict[str, Any]] = []
    async for ch in stream_instrumented_model_chat(
        orch,
        settings=_settings_tracking_on(),
        model_id="llama2",
        messages=[{"role": "user", "content": "ping"}],
        temperature=0.7,
        max_tokens=128,
        stream=True,
        think=None,
        cloud_via_local=False,
        chat_id=None,
        usage_type=UsageType.CHAT.value,
    ):
        chunks.append(ch)

    assert len(chunks) == 1
    inv = chunks[0].get(MODEL_INVOCATION_CHUNK_KEY) or {}
    assert inv.get("usage_record_id") is not None
    assert inv.get("token_counts_exact") is True
    assert inv.get("prompt_tokens") == 12
    assert inv.get("completion_tokens") == 34

    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as s:
        row = s.scalars(select(ModelUsageRecord)).first()
        assert row is not None
        assert row.status == UsageStatus.SUCCESS.value
        assert row.prompt_tokens == 12
        assert row.completion_tokens == 34
        assert row.total_tokens == 46
        assert row.estimated_tokens is False


@pytest.mark.asyncio
async def test_success_estimated_when_no_provider_usage(patch_runtime_session, memory_engine):
    orch = _make_orchestrator()

    async def fake_stream(**kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"message": {"content": "abc", "thinking": ""}, "done": True}

    orch.stream_raw_chat = fake_stream  # type: ignore[method-assign]

    chunks: List[Dict[str, Any]] = []
    async for ch in stream_instrumented_model_chat(
        orch,
        settings=_settings_tracking_on(),
        model_id="llama2",
        messages=[{"role": "user", "content": "x" * 40}],
        temperature=0.7,
        max_tokens=64,
        stream=True,
        think=None,
        cloud_via_local=False,
        chat_id=None,
        usage_type=UsageType.CHAT.value,
    ):
        chunks.append(ch)

    inv = chunks[-1].get(MODEL_INVOCATION_CHUNK_KEY) or {}
    assert inv.get("token_counts_exact") is False

    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as s:
        row = s.scalars(select(ModelUsageRecord)).first()
        assert row.estimated_tokens is True
        assert row.total_tokens > 0


@pytest.mark.asyncio
async def test_provider_error_no_fake_tokens(patch_runtime_session, memory_engine):
    orch = _make_orchestrator()

    async def fake_stream(**kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"error": "boom"}

    orch.stream_raw_chat = fake_stream  # type: ignore[method-assign]

    n = 0
    async for _ in stream_instrumented_model_chat(
        orch,
        settings=_settings_tracking_on(),
        model_id="llama2",
        messages=[{"role": "user", "content": "x"}],
        temperature=0.7,
        max_tokens=32,
        stream=True,
        think=None,
        cloud_via_local=False,
        chat_id=None,
        usage_type=UsageType.CHAT.value,
    ):
        n += 1
    assert n >= 2

    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as s:
        row = s.scalars(select(ModelUsageRecord)).first()
        assert row.status == UsageStatus.FAILED.value
        assert row.total_tokens == 0


@pytest.mark.asyncio
async def test_allow_with_warn_policy(patch_runtime_session, memory_engine):
    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as s:
        s.add(
            ModelQuotaPolicy(
                scope_type=QuotaScopeType.GLOBAL.value,
                scope_ref=None,
                mode=QuotaMode.WARN.value,
                source=QuotaSource.MANUAL.value,
                is_enabled=True,
                limit_total_tokens=200,
                warn_percent=0.5,
                priority=50,
            )
        )
        s.commit()

    orch = _make_orchestrator()

    async def fake_stream(**kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"message": {"content": "y", "thinking": ""}, "done": True, "prompt_eval_count": 1, "eval_count": 1}

    orch.stream_raw_chat = fake_stream  # type: ignore[method-assign]

    chunks: List[Dict[str, Any]] = []
    long_user = "word " * 80
    async for ch in stream_instrumented_model_chat(
        orch,
        settings=_settings_tracking_on(),
        model_id="llama2",
        messages=[{"role": "user", "content": long_user}],
        temperature=0.7,
        max_tokens=128,
        stream=True,
        think=None,
        cloud_via_local=False,
        chat_id=None,
        usage_type=UsageType.CHAT.value,
    ):
        chunks.append(ch)

    inv = chunks[-1].get(MODEL_INVOCATION_CHUNK_KEY) or {}
    assert inv.get("warning_active") is True
    assert inv.get("preflight_decision") == "allow_with_warning"


@pytest.mark.asyncio
async def test_cancel_mid_stream_single_cancelled_record(patch_runtime_session, memory_engine):
    """Abbruch während des Streams: genau ein Ledger-Eintrag CANCELLED, kein SUCCESS."""
    orch = _make_orchestrator()

    async def slow_stream(**kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        # Zwei Chunks: erst danach wird der erste an den Consumer weitergereicht (siehe Runtime-Pufferlogik).
        yield {"message": {"content": "partial", "thinking": ""}, "done": False}
        yield {"message": {"content": "more", "thinking": ""}, "done": False}
        await asyncio.sleep(3600)
        yield {"done": True, "prompt_eval_count": 1, "eval_count": 1}

    orch.stream_raw_chat = slow_stream  # type: ignore[method-assign]

    chunks: List[Dict[str, Any]] = []

    async def consumer() -> None:
        async for ch in stream_instrumented_model_chat(
            orch,
            settings=_settings_tracking_on(),
            model_id="llama2",
            messages=[{"role": "user", "content": "hi"}],
            temperature=0.7,
            max_tokens=64,
            stream=True,
            think=None,
            cloud_via_local=False,
            chat_id=None,
            usage_type=UsageType.CHAT.value,
        ):
            chunks.append(ch)

    task = asyncio.create_task(consumer())
    await asyncio.sleep(0)
    for _ in range(100):
        await asyncio.sleep(0.02)
        if chunks:
            break
    assert chunks, "expected first streaming chunk"
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as s:
        rows = list(s.scalars(select(ModelUsageRecord)))
        assert len(rows) == 1
        assert rows[0].status == UsageStatus.CANCELLED.value


@pytest.mark.asyncio
async def test_offline_hard_block_offline_default_policy(patch_runtime_session, memory_engine):
    """Lokaler Lauf (is_online=False): OFFLINE_DEFAULT mit HARD_BLOCK greift."""
    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as s:
        s.add(
            ModelQuotaPolicy(
                scope_type=QuotaScopeType.OFFLINE_DEFAULT.value,
                scope_ref=None,
                mode=QuotaMode.HARD_BLOCK.value,
                source=QuotaSource.MANUAL.value,
                is_enabled=True,
                limit_total_tokens=1,
                priority=100,
            )
        )
        s.commit()

    orch = _make_orchestrator()

    async def must_not_run(**kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        raise AssertionError("Provider stream must not run when offline quota blocks")
        yield {}  # pragma: no cover

    orch.stream_raw_chat = must_not_run  # type: ignore[method-assign]

    chunks: List[Dict[str, Any]] = []
    async for ch in stream_instrumented_model_chat(
        orch,
        settings=_settings_tracking_on(),
        model_id="llama2",
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.7,
        max_tokens=4096,
        stream=True,
        think=None,
        cloud_via_local=False,
        chat_id=None,
        usage_type=UsageType.CHAT.value,
    ):
        chunks.append(ch)

    assert len(chunks) == 1
    assert chunks[0].get("error_kind") == ERROR_KIND_POLICY_BLOCK
    with S() as s:
        rows = list(s.scalars(select(ModelUsageRecord)))
        assert len(rows) == 1
        assert rows[0].status == UsageStatus.BLOCKED.value
