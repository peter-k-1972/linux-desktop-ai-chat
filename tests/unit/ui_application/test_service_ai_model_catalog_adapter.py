"""ServiceAiModelCatalogAdapter — Delegation, Fehlerpfade (ohne echte DB)."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")
from sqlalchemy.exc import OperationalError

from app.ui_application.adapters.service_ai_model_catalog_adapter import ServiceAiModelCatalogAdapter
from app.ui_contracts.workspaces.settings_ai_model_catalog import (
    AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE,
    AI_MODEL_CATALOG_PLACEHOLDER_GENERIC,
    AI_MODEL_CATALOG_PLACEHOLDER_OPERATIONAL_ERROR,
    AI_MODEL_CATALOG_PLACEHOLDER_SCHEMA_HEURISTIC,
)


def _patch_infra(monkeypatch, *, model: str = "pref") -> None:
    class S:
        def __init__(self) -> None:
            self.model = model

    class Inf:
        def __init__(self) -> None:
            self.settings = S()

    monkeypatch.setattr(
        "app.ui_application.adapters.service_ai_model_catalog_adapter.get_infrastructure",
        lambda: Inf(),
    )


def _row(sid: str = "m1") -> dict:
    return {
        "selection_id": sid,
        "display_short": sid,
        "display_detail": "",
        "chat_selectable": True,
        "asset_type": "",
        "storage_root_name": "",
        "path_hint": "",
        "usage_summary": "",
        "quota_summary": "",
        "usage_quality_note": "",
    }


@pytest.mark.asyncio
async def test_adapter_success_entries(monkeypatch) -> None:
    _patch_infra(monkeypatch, model="m1")

    class Svc:
        async def build_catalog_for_chat(self, settings) -> list:  # noqa: ANN001
            del settings
            return [_row("m1")]

    monkeypatch.setattr(
        "app.services.unified_model_catalog_service.get_unified_model_catalog_service",
        lambda: Svc(),
    )
    ad = ServiceAiModelCatalogAdapter()
    out = await ad.load_chat_selectable_catalog_for_settings()
    assert out.status == "success_entries"
    assert len(out.entries) == 1
    assert out.entries[0].selection_id == "m1"
    assert out.default_selection_id == "m1"


@pytest.mark.asyncio
async def test_adapter_empty_usable(monkeypatch) -> None:
    _patch_infra(monkeypatch)

    class Svc:
        async def build_catalog_for_chat(self, settings) -> list:  # noqa: ANN001
            del settings
            return [_row("x") | {"chat_selectable": False}]

    monkeypatch.setattr(
        "app.services.unified_model_catalog_service.get_unified_model_catalog_service",
        lambda: Svc(),
    )
    out = await ServiceAiModelCatalogAdapter().load_chat_selectable_catalog_for_settings()
    assert out.status == "success_empty_usable"
    assert out.placeholder_line == AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE


@pytest.mark.asyncio
async def test_adapter_operational_error(monkeypatch) -> None:
    _patch_infra(monkeypatch)

    class Svc:
        async def build_catalog_for_chat(self, settings) -> list:  # noqa: ANN001
            del settings
            raise OperationalError("stmt", None, Exception("x"))

    monkeypatch.setattr(
        "app.services.unified_model_catalog_service.get_unified_model_catalog_service",
        lambda: Svc(),
    )
    out = await ServiceAiModelCatalogAdapter().load_chat_selectable_catalog_for_settings()
    assert out.status == "failure_operational_error"
    assert out.placeholder_line == AI_MODEL_CATALOG_PLACEHOLDER_OPERATIONAL_ERROR


@pytest.mark.asyncio
async def test_adapter_no_such_table_heuristic(monkeypatch) -> None:
    _patch_infra(monkeypatch)

    class Svc:
        async def build_catalog_for_chat(self, settings) -> list:  # noqa: ANN001
            del settings
            raise RuntimeError("no such table: foo")

    monkeypatch.setattr(
        "app.services.unified_model_catalog_service.get_unified_model_catalog_service",
        lambda: Svc(),
    )
    out = await ServiceAiModelCatalogAdapter().load_chat_selectable_catalog_for_settings()
    assert out.status == "failure_schema_missing"
    assert out.placeholder_line == AI_MODEL_CATALOG_PLACEHOLDER_SCHEMA_HEURISTIC


@pytest.mark.asyncio
async def test_adapter_generic_failure(monkeypatch) -> None:
    _patch_infra(monkeypatch)

    class Svc:
        async def build_catalog_for_chat(self, settings) -> list:  # noqa: ANN001
            del settings
            raise RuntimeError("ollama down")

    monkeypatch.setattr(
        "app.services.unified_model_catalog_service.get_unified_model_catalog_service",
        lambda: Svc(),
    )
    out = await ServiceAiModelCatalogAdapter().load_chat_selectable_catalog_for_settings()
    assert out.status == "failure_generic"
    assert out.placeholder_line == AI_MODEL_CATALOG_PLACEHOLDER_GENERIC


def test_persist_default_model_id(monkeypatch) -> None:
    class S:
        def __init__(self) -> None:
            self.model = ""
            self.saved = False

        def save(self) -> None:
            self.saved = True

    s = S()

    class Inf:
        settings = s

    monkeypatch.setattr(
        "app.ui_application.adapters.service_ai_model_catalog_adapter.get_infrastructure",
        lambda: Inf(),
    )
    ServiceAiModelCatalogAdapter().persist_default_chat_model_id("mid")
    assert s.model == "mid"
    assert s.saved is True
