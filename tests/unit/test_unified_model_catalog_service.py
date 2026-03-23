"""Unified Model Catalog: Registry + Ollama-Liste + ModelAsset."""

from __future__ import annotations

from contextlib import contextmanager

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.persistence.base import Base
from app.persistence.enums import ModelAssetType
from app.services.local_model_registry_service import LocalModelRegistryService
from app.services.model_service import ModelService
from app.services.result import ServiceResult
from app.services.unified_model_catalog_service import (
    UnifiedModelCatalogService,
    model_id_in_runtime_name_set,
)


@pytest.fixture
def memory_engine():
    eng = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def patch_catalog_session(memory_engine, monkeypatch):
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

    monkeypatch.setattr("app.services.unified_model_catalog_service.session_scope", scope)


@pytest.mark.asyncio
async def test_catalog_survives_missing_asset_tables(settings, monkeypatch):
    """Ohne model_storage_roots o. Ä.: Registry + Ollama-Zeilen bleiben erhalten."""

    async def fake_get_models_full(_self):
        return ServiceResult.ok([{"name": "phi3", "size": 1}])

    monkeypatch.setattr(ModelService, "get_models_full", fake_get_models_full)

    @contextmanager
    def broken_scope():
        raise OperationalError("SELECT", {}, Exception("no such table"))

    monkeypatch.setattr("app.services.unified_model_catalog_service.session_scope", broken_scope)

    svc = UnifiedModelCatalogService()
    cat = await svc.build_catalog_for_chat(settings)
    assert len(cat) >= 1
    ids = {e["selection_id"] for e in cat}
    assert "phi3" in ids


def test_model_id_in_runtime_name_set_matches_tagged_ollama():
    names = {"llama3:latest", "phi3:mini"}
    assert model_id_in_runtime_name_set(names, "llama3")
    assert model_id_in_runtime_name_set(names, "llama3:latest")
    assert model_id_in_runtime_name_set(names, "phi3:mini")
    assert not model_id_in_runtime_name_set(names, "llama3:70b")
    assert not model_id_in_runtime_name_set(names, "missing")


@pytest.fixture
def settings() -> AppSettings:
    s = AppSettings(backend=InMemoryBackend())
    s.cloud_escalation = False
    s.cloud_via_local = False
    s.ollama_api_key = ""
    return s


@pytest.mark.asyncio
async def test_ollama_only_and_unassigned_asset_row(
    patch_catalog_session, memory_engine, settings, monkeypatch
):
    async def fake_get_models_full(_self):
        return ServiceResult.ok([{"name": "custom:tag", "size": 2048}])

    monkeypatch.setattr(ModelService, "get_models_full", fake_get_models_full)

    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as s:
        r = LocalModelRegistryService().register_storage_root(
            session=s, name="ai", path_absolute="/tmp/ai", scan_enabled=False
        )
        s.flush()
        LocalModelRegistryService().upsert_asset_from_scan(
            session=s,
            path_absolute="/tmp/ai/weights.gguf",
            asset_type=ModelAssetType.GGUF.value,
            storage_root_id=r.id,
            path_relative="weights.gguf",
            display_name="weights.gguf",
            file_size_bytes=99,
            suggested_model_id=None,
            match_confidence="none",
        )
        s.commit()

    svc = UnifiedModelCatalogService()
    cat = await svc.build_catalog_for_chat(settings)
    ids = {e["selection_id"] for e in cat}
    assert "custom:tag" in ids
    assert any(x.startswith("local-asset:") for x in ids)
    unassigned = next(x for x in cat if x["selection_id"].startswith("local-asset:"))
    assert unassigned["chat_selectable"] is False
    assert unassigned["assignment_state"] == "unassigned"


@pytest.mark.asyncio
async def test_management_rows_have_selection_key(settings, monkeypatch, patch_catalog_session):
    async def fake_get_models_full(_self):
        return ServiceResult.ok([{"name": "m1", "size": 1}])

    monkeypatch.setattr(ModelService, "get_models_full", fake_get_models_full)

    svc = UnifiedModelCatalogService()
    cat = await svc.build_catalog_for_chat(settings)
    rows = svc.to_management_rows(cat)
    assert rows
    assert all("selection_key" in r and "display_name" in r for r in rows)


@pytest.mark.asyncio
async def test_assigned_asset_chat_selectable_when_base_id_matches_ollama_tag(
    patch_catalog_session, memory_engine, settings, monkeypatch
):
    """model_id in DB ohne :tag, Ollama listet name:tag — weiterhin runtime-fähig / chat_selectable."""

    async def fake_get_models_full(_self):
        return ServiceResult.ok([{"name": "mybase:latest", "size": 100}])

    monkeypatch.setattr(ModelService, "get_models_full", fake_get_models_full)

    S = sessionmaker(bind=memory_engine, autoflush=False, expire_on_commit=False, future=True)
    with S() as s:
        r = LocalModelRegistryService().register_storage_root(
            session=s, name="ai", path_absolute="/tmp/ai", scan_enabled=False
        )
        s.flush()
        LocalModelRegistryService().upsert_asset_from_scan(
            session=s,
            path_absolute="/tmp/ai/mybase.gguf",
            asset_type=ModelAssetType.GGUF.value,
            storage_root_id=r.id,
            path_relative="mybase.gguf",
            display_name="mybase.gguf",
            file_size_bytes=1000,
            suggested_model_id="mybase",
            match_confidence="high",
        )
        s.commit()

    svc = UnifiedModelCatalogService()
    cat = await svc.build_catalog_for_chat(settings)
    row = next((x for x in cat if x.get("selection_id") == "mybase"), None)
    assert row is not None
    assert row.get("chat_selectable") is True
    assert row.get("has_local_asset") is True
    assert (row.get("usage_summary") or "").strip() != ""
