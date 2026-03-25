"""Smoke: installiertes Paket app.providers ist importierbar (ohne Host)."""


def test_root_exports():
    from app.providers import (
        BaseChatProvider,
        CloudOllamaProvider,
        LocalOllamaProvider,
        OLLAMA_URL,
        OllamaClient,
    )

    assert OllamaClient is not None
    assert OLLAMA_URL.startswith("http")
    assert issubclass(LocalOllamaProvider, BaseChatProvider)
    assert issubclass(CloudOllamaProvider, BaseChatProvider)


def test_submodules_for_cut_ready_surface():
    from app.providers.orchestrator_provider_factory import (
        create_default_orchestrator_providers,
        fetch_cloud_chat_model_names,
    )
    from app.providers.cloud_ollama_provider import get_ollama_api_key

    assert callable(create_default_orchestrator_providers)
    assert callable(fetch_cloud_chat_model_names)
    assert callable(get_ollama_api_key)
