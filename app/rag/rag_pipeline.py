"""
RAG Pipeline – verbindet Retriever, Context Builder und LLM-Prompt.

Flow: User Prompt → Retriever → Context Builder → Prompt Template → LLM
"""

import logging
from typing import List, Optional

from app.rag.context_builder import ContextBuilder
from app.rag.models import Chunk
from app.rag.retriever import Retriever

logger = logging.getLogger(__name__)

DEFAULT_RAG_PROMPT_TEMPLATE = """Nutze ausschließlich den folgenden Kontext, um die Frage zu beantworten. Wenn der Kontext die Antwort nicht enthält, sage das ehrlich.

Kontext:
{context}

Frage: {query}

Antwort:"""


class RAGPipeline:
    """
    Zentrale RAG-Pipeline: Retrieval → Context → Prompt.
    """

    def __init__(
        self,
        retriever: Retriever,
        context_builder: Optional[ContextBuilder] = None,
        prompt_template: Optional[str] = None,
    ):
        """
        Args:
            retriever: Retriever für Similarity Search
            context_builder: Optionaler Context Builder (Default verwendet)
            prompt_template: Optionales Prompt-Template mit {context} und {query}
        """
        self.retriever = retriever
        self.context_builder = context_builder or ContextBuilder()
        self.prompt_template = prompt_template or DEFAULT_RAG_PROMPT_TEMPLATE

    async def get_context(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Holt relevanten Kontext für eine Query (ohne LLM-Aufruf).

        Returns:
            Formatierter Kontext-String oder leer bei keinen Treffern
        """
        chunks = await self.retriever.retrieve(query, top_k=top_k)
        return self.context_builder.build(chunks)

    async def get_context_and_chunks(
        self, query: str, top_k: Optional[int] = None
    ) -> tuple[str, List[Chunk]]:
        """
        Holt Kontext und die zugehörigen Chunks.

        Returns:
            (context_string, chunks)
        """
        chunks = await self.retriever.retrieve(query, top_k=top_k)
        context = self.context_builder.build(chunks)
        return context, chunks

    def build_rag_prompt(self, query: str, context: str) -> str:
        """
        Baut den finalen Prompt mit Kontext.

        Args:
            query: User-Anfrage
            context: RAG-Kontext vom Context Builder

        Returns:
            Vollständiger Prompt für das LLM
        """
        return self.prompt_template.format(context=context, query=query)

    async def augment_prompt(
        self,
        user_prompt: str,
        top_k: Optional[int] = None,
    ) -> tuple[str, bool]:
        """
        Erweitert einen User-Prompt mit RAG-Kontext, falls Treffer vorhanden.

        Args:
            user_prompt: Originale User-Anfrage
            top_k: Optionale Override für Retrieval-Anzahl

        Returns:
            (augmentierter_prompt, rag_was_used)
            - Wenn Kontext gefunden: (RAG-Prompt mit Kontext, True)
            - Wenn kein Kontext: (user_prompt unverändert, False)
        """
        context = await self.get_context(user_prompt, top_k=top_k)
        if not context or not context.strip():
            return user_prompt, False
        augmented = self.build_rag_prompt(user_prompt, context)
        return augmented, True
