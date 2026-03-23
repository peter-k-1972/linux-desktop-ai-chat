"""ModelUsageGuiService mit In-Memory-DB."""

from __future__ import annotations

from contextlib import contextmanager

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.persistence.base import Base
from app.persistence.enums import QuotaMode, QuotaScopeType, QuotaSource
from app.persistence.orm.models import ModelQuotaPolicy, ModelUsageAggregate
from app.domain.model_usage.periods import period_starts
from app.persistence.enums import PeriodType

pytestmark = pytest.mark.model_usage_gate


@pytest.fixture
def memory_engine():
    eng = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def patch_gui_session(memory_engine, monkeypatch):
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

    monkeypatch.setattr("app.services.model_usage_gui_service.session_scope", scope)


def test_bundle_empty_db(patch_gui_session, memory_engine):
    from app.services.model_usage_gui_service import ModelUsageGuiService

    svc = ModelUsageGuiService()
    s = AppSettings(backend=InMemoryBackend())
    b = svc.get_model_operational_bundle("any-model", s)
    assert b.get("db_error") is None
    assert b["usage_tokens"]["total"] == 0


def test_save_policy_updates(patch_gui_session, memory_engine):
    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as sess:
        p = ModelQuotaPolicy(
            scope_type=QuotaScopeType.GLOBAL.value,
            mode=QuotaMode.WARN.value,
            source=QuotaSource.MANUAL.value,
            is_enabled=True,
            limit_total_tokens=99,
            priority=1,
        )
        sess.add(p)
        sess.commit()
        pid = p.id

    from app.services.model_usage_gui_service import ModelUsageGuiService

    svc = ModelUsageGuiService()
    r = svc.save_policy(
        pid,
        is_enabled=True,
        mode="hard_block",
        warn_percent=0.9,
        limit_hour=None,
        limit_day=None,
        limit_week=None,
        limit_month=None,
        limit_total=50,
        notes="t",
    )
    assert r["ok"] is True
    assert r["policy"]["mode"] == "hard_block"
    assert r["policy"]["limit_total"] == 50


def test_provider_summary(patch_gui_session, memory_engine):
    from app.services.model_usage_gui_service import ModelUsageGuiService

    ps = period_starts()["total"]
    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as sess:
        sess.add(
            ModelUsageAggregate(
                model_id="m1",
                provider_id_key="local",
                provider_credential_id_key=-1,
                scope_type="global",
                scope_ref_key="",
                period_type=PeriodType.TOTAL.value,
                period_start=ps,
                total_tokens=42,
                prompt_tokens=10,
                completion_tokens=32,
            )
        )
        sess.commit()

    svc = ModelUsageGuiService()
    s = svc.provider_token_summary("local")
    assert s.get("total_tokens") == 42
