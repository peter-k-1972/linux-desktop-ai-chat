"""Minimale Laufzeit-Checks ohne laufenden Ollama-Server."""

import pytest


@pytest.mark.asyncio
async def test_ollama_client_close_idempotent():
    from app.providers.ollama_client import OllamaClient

    c = OllamaClient()
    await c.close()
    await c.close()


@pytest.mark.asyncio
async def test_local_provider_close():
    from app.providers import LocalOllamaProvider

    p = LocalOllamaProvider()
    await p.close()


def test_create_default_orchestrator_providers():
    from app.providers import OllamaClient
    from app.providers.orchestrator_provider_factory import create_default_orchestrator_providers

    client = OllamaClient()
    local, cloud = create_default_orchestrator_providers(ollama_client=client, api_key=None)
    assert local.provider_id == "local"
    assert cloud.provider_id == "ollama_cloud"


@pytest.mark.asyncio
async def test_fetch_cloud_chat_model_names_empty_without_key():
    from app.providers.orchestrator_provider_factory import fetch_cloud_chat_model_names

    names = await fetch_cloud_chat_model_names(None)
    assert names == set()
