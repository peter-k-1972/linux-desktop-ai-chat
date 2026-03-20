"""
Context Builder – erzeugt den RAG-Kontext für den LLM-Prompt.

Kombiniert relevante Chunks, begrenzt die Größe, formatiert für den Prompt.
"""

from typing import List, Optional

from app.rag.models import Chunk

DEFAULT_MAX_CONTEXT_TOKENS = 2000
CHARS_PER_TOKEN = 4


class ContextBuilder:
    """
    Baut den Kontext-String aus retrieved Chunks für das LLM.
    """

    def __init__(
        self,
        max_context_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS,
        include_metadata: bool = False,
        separator: str = "\n\n---\n\n",
    ):
        """
        Args:
            max_context_tokens: Maximale Kontextgröße in Tokens
            include_metadata: Quell-Datei etc. in den Kontext einfügen
            separator: Trennzeichen zwischen Chunks
        """
        self.max_context_tokens = max_context_tokens
        self.include_metadata = include_metadata
        self.separator = separator

    def build(self, chunks: List[Chunk]) -> str:
        """
        Erzeugt den formatierten Kontext aus Chunks.

        Args:
            chunks: Relevante Chunks vom Retriever

        Returns:
            Formatierter Kontext-String
        """
        if not chunks:
            return ""

        parts: List[str] = []
        used_tokens = 0
        max_chars = self.max_context_tokens * CHARS_PER_TOKEN

        for chunk in chunks:
            if self.include_metadata:
                source = chunk.metadata.get("filename", chunk.document_id)
                prefix = f"[Quelle: {source}]\n"
            else:
                prefix = ""

            block = prefix + chunk.content
            block_len = len(block)
            if used_tokens * CHARS_PER_TOKEN + block_len > max_chars:
                # Kürzen, falls nötig
                remaining = max_chars - used_tokens * CHARS_PER_TOKEN - len(self.separator)
                if remaining > 100:
                    block = (prefix + chunk.content)[:remaining] + "..."
                else:
                    break

            parts.append(block)
            used_tokens += len(block) // CHARS_PER_TOKEN
            if used_tokens >= self.max_context_tokens:
                break

        return self.separator.join(parts)
