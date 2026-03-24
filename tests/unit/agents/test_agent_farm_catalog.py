"""Agentenfarm-Katalog: Laden und Validierung."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.agents.farm import (
    ActivationState,
    FarmRoleKind,
    ScopeLevel,
    get_agent_farm_catalog,
    load_agent_farm_catalog_from_path,
    reset_agent_farm_catalog_cache,
)
from app.agents.farm.loader import default_catalog_path


@pytest.fixture(autouse=True)
def _reset_catalog_cache():
    reset_agent_farm_catalog_cache()
    yield
    reset_agent_farm_catalog_cache()


def test_default_catalog_loads():
    cat = get_agent_farm_catalog()
    assert cat.schema_version == 1
    assert cat.catalog_id == "default_v1"
    assert len(cat.roles) == 7
    by_id = cat.by_role_id()
    assert "farm.project.butler" in by_id
    b = by_id["farm.project.butler"]
    assert b.scope_level == ScopeLevel.PROJECT
    assert b.farm_role_kind == FarmRoleKind.PROJECT_BUTLER
    assert b.activation == ActivationState.DRAFT
    assert b.is_standard is True


def test_default_path_points_to_existing_file():
    p = default_catalog_path()
    assert p.is_file()


def test_duplicate_role_id_rejected(tmp_path: Path):
    data = {
        "schema_version": 1,
        "catalog_id": "x",
        "description": "",
        "roles": [
            {
                "agent_role_id": "dup",
                "scope_level": "project",
                "farm_role_kind": "specialist",
                "display_name": "A",
                "functional_role": "a",
                "responsibility_scope": "x",
                "input_types": [],
                "output_types": [],
                "allowed_workflow_ids": [],
                "escalation_target_role_id": None,
                "activation": "draft",
                "is_standard": True,
            },
            {
                "agent_role_id": "dup",
                "scope_level": "project",
                "farm_role_kind": "qa_review",
                "display_name": "B",
                "functional_role": "b",
                "responsibility_scope": "y",
                "input_types": [],
                "output_types": [],
                "allowed_workflow_ids": [],
                "escalation_target_role_id": None,
                "activation": "draft",
                "is_standard": False,
            },
        ],
    }
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="doppelte agent_role_id"):
        load_agent_farm_catalog_from_path(path)


def test_unknown_root_key_rejected(tmp_path: Path):
    path = tmp_path / "bad2.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "catalog_id": "x",
                "description": "",
                "roles": [],
                "extra": 1,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Root-Schlüssel"):
        load_agent_farm_catalog_from_path(path)
