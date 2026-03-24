"""
Filter- und Listenlogik für das QML Prompt-Regal.

Persistenz ausschließlich über :class:`QmlPromptShelfOperationsPort` (Standard: Service-Adapter).
"""

from __future__ import annotations

import logging

from app.prompts.prompt_models import Prompt
from app.ui_application.adapters.service_qml_prompt_shelf_adapter import ServiceQmlPromptShelfAdapter
from app.ui_application.ports.qml_prompt_shelf_port import QmlPromptShelfOperationsPort

logger = logging.getLogger(__name__)


class PromptPresenterFacade:
    def __init__(self, port: QmlPromptShelfOperationsPort | None = None) -> None:
        self._port: QmlPromptShelfOperationsPort = port or ServiceQmlPromptShelfAdapter()

    def list_prompts(self, filter_text: str = "") -> list[Prompt]:
        try:
            return self._port.list_prompts(filter_text=filter_text or "")
        except Exception:
            logger.exception("list_prompts")
            return []

    def get(self, prompt_id: int) -> Prompt | None:
        try:
            return self._port.get_prompt(prompt_id)
        except Exception:
            logger.exception("get prompt %s", prompt_id)
            return None

    def create(self, prompt: Prompt) -> Prompt | None:
        try:
            return self._port.create_prompt(prompt)
        except Exception:
            logger.exception("create prompt")
            return None

    def update(self, prompt: Prompt) -> bool:
        try:
            return self._port.update_prompt(prompt)
        except Exception:
            logger.exception("update prompt")
            return False

    def list_versions(self, prompt_id: int) -> list[dict]:
        try:
            return self._port.list_prompt_versions(prompt_id)
        except Exception:
            logger.exception("list_versions")
            return []

    @staticmethod
    def unique_collections(prompts: list[Prompt]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for p in prompts:
            c = (p.category or "").strip() or "—"
            if c not in seen:
                seen.add(c)
                out.append(c)
        out.sort(key=str.lower)
        return out

    @staticmethod
    def unique_tags(prompts: list[Prompt]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for p in prompts:
            for t in p.tags or []:
                tt = (t or "").strip()
                if tt and tt not in seen:
                    seen.add(tt)
                    out.append(tt)
        out.sort(key=str.lower)
        return out

    @staticmethod
    def filter_prompts(
        prompts: list[Prompt],
        *,
        collection: str,
        tag: str,
    ) -> list[Prompt]:
        out = prompts
        if collection:
            key = collection.strip()
            out = [p for p in out if ((p.category or "").strip() or "—") == key]
        if tag:
            key = tag.strip()
            out = [p for p in out if key in [((x or "").strip()) for x in (p.tags or [])]]
        return out
