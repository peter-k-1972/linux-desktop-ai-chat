"""
ChatBackend – Kompatibilitätswrapper für ChatService und ModelService.

Delegiert an app.services. Neue Code sollte get_chat_service() / get_model_service() nutzen.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional


class ChatBackend:
    """
    Deprecated. Delegiert an ChatService und ModelService.
    """

    def __init__(self, *args, **kwargs):
        from app.services.chat_service import get_chat_service
        from app.services.model_service import get_model_service
        from app.services.infrastructure import get_infrastructure
        self._chat = get_chat_service()
        self._model = get_model_service()
        self._infra = get_infrastructure()

    @property
    def db(self):
        return self._infra.database

    @property
    def settings(self):
        return self._infra.settings

    def list_chats(self, filter_text: str = "") -> List[Dict[str, Any]]:
        return self._chat.list_chats(filter_text)

    def create_chat(self, title: str = "Neuer Chat") -> int:
        return self._chat.create_chat(title)

    def load_chat(self, chat_id: int) -> List[tuple]:
        return self._chat.load_chat(chat_id)

    def save_message(self, chat_id: int, role: str, content: str) -> None:
        self._chat.save_message(chat_id, role, content)

    def save_chat_title(self, chat_id: int, title: str) -> None:
        self._chat.save_chat_title(chat_id, title)

    async def get_models(self) -> List[str]:
        import asyncio
        result = await self._model.get_models()
        return result.data if result.success else []

    async def get_models_full(self) -> List[Dict[str, Any]]:
        import asyncio
        result = await self._model.get_models_full()
        return result.data if result.success else []

    def get_default_model(self) -> str:
        return self._model.get_default_model()

    def set_default_model(self, model_name: str) -> None:
        self._model.set_default_model(model_name)

    async def get_ollama_status(self) -> Dict[str, Any]:
        from app.services.provider_service import get_provider_service
        result = await get_provider_service().get_provider_status()
        return result.data if result.success else {"online": False, "models": [], "model_count": 0}

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = True,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        async for chunk in self._chat.chat(model, messages, temperature, max_tokens, stream):
            yield chunk

    async def close(self) -> None:
        await self._chat.close()


_backend: Optional[ChatBackend] = None


def get_chat_backend() -> ChatBackend:
    global _backend
    if _backend is None:
        _backend = ChatBackend()
    return _backend


def set_chat_backend(backend: Optional[ChatBackend]) -> None:
    global _backend
    _backend = backend
