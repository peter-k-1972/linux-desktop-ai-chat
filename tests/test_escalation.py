"""Tests für die Eskalationslogik."""

import pytest
from app.core.models.escalation_manager import get_next_escalation_role, get_escalation_model
from app.core.models.roles import ModelRole
from app.core.models.registry import get_registry


def test_local_escalation():
    assert get_next_escalation_role(ModelRole.FAST, cloud_enabled=False) == ModelRole.DEFAULT
    assert get_next_escalation_role(ModelRole.DEFAULT, cloud_enabled=False) == ModelRole.THINK
    assert get_next_escalation_role(ModelRole.CHAT, cloud_enabled=False) == ModelRole.DEFAULT
    assert get_next_escalation_role(ModelRole.CODE, cloud_enabled=False) == ModelRole.THINK
    assert get_next_escalation_role(ModelRole.THINK, cloud_enabled=False) is None


def test_cloud_escalation():
    assert get_next_escalation_role(ModelRole.THINK, cloud_enabled=True) == ModelRole.OVERKILL
    assert get_next_escalation_role(ModelRole.CODE, cloud_enabled=True) == ModelRole.OVERKILL
    assert get_next_escalation_role(ModelRole.DEFAULT, cloud_enabled=True) == ModelRole.OVERKILL


def test_get_escalation_model_local():
    reg = get_registry()
    # Mit verfügbaren lokalen Modellen
    model = get_escalation_model(
        ModelRole.FAST,
        registry=reg,
        available_local={"mistral:latest", "qwen2.5:latest"},
        cloud_enabled=False,
    )
    assert model == "qwen2.5:latest"


def test_get_escalation_model_none():
    model = get_escalation_model(
        ModelRole.THINK,
        cloud_enabled=False,
    )
    assert model is None
