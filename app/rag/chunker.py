"""
Chunker – zerlegt Dokumente in sinnvolle Text-Chunks.

Token-basierte Chunking mit konfigurierbarer Größe und Overlap.
"""

import hashlib
import re
from typing import List

from app.rag.models import Chunk, Document

# Grobe Abschätzung: ~4 Zeichen pro Token für Deutsch/Englisch
CHARS_PER_TOKEN = 4


def _estimate_tokens(text: str) -> int:
    """Schätzt die Token-Anzahl (grob)."""
    return max(1, len(text) // CHARS_PER_TOKEN)


def _split_into_sentences(text: str) -> List[str]:
    """Teilt Text in Sätze (einfache Heuristik)."""
    # Sätze an . ! ? oder Zeilenumbrüchen
    parts = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [p.strip() for p in parts if p.strip()]


def _chunk_by_tokens(
    text: str,
    chunk_size_tokens: int,
    overlap_tokens: int,
) -> List[str]:
    """
    Teilt Text in Chunks mit Overlap.
    Versucht, an Satzgrenzen zu schneiden.
    """
    target_chars = chunk_size_tokens * CHARS_PER_TOKEN
    overlap_chars = overlap_tokens * CHARS_PER_TOKEN

    sentences = _split_into_sentences(text)
    if not sentences:
        # Fallback: feste Zeichenlänge
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + target_chars, len(text))
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap_chars if end < len(text) else len(text)
        return chunks

    chunks: List[str] = []
    current: List[str] = []
    current_tokens = 0

    for sent in sentences:
        sent_tokens = _estimate_tokens(sent)
        if current_tokens + sent_tokens > chunk_size_tokens and current:
            chunk_text = " ".join(current)
            chunks.append(chunk_text)
            # Overlap: letzte Sätze behalten
            overlap_remaining = overlap_tokens
            new_current: List[str] = []
            for s in reversed(current):
                t = _estimate_tokens(s)
                if overlap_remaining >= t:
                    new_current.insert(0, s)
                    overlap_remaining -= t
                else:
                    break
            current = new_current
            current_tokens = sum(_estimate_tokens(s) for s in current)
        current.append(sent)
        current_tokens += sent_tokens

    if current:
        chunks.append(" ".join(current))

    return chunks


class Chunker:
    """
    Zerlegt Dokumente in Chunks mit konfigurierbarer Größe und Overlap.
    """

    def __init__(
        self,
        chunk_size_tokens: int = 500,
        overlap_tokens: int = 50,
    ):
        """
        Args:
            chunk_size_tokens: Zielgröße pro Chunk in Tokens
            overlap_tokens: Überlappung zwischen benachbarten Chunks
        """
        self.chunk_size_tokens = max(50, chunk_size_tokens)
        self.overlap_tokens = max(0, min(overlap_tokens, self.chunk_size_tokens // 2))

    def chunk_document(self, document: Document) -> List[Chunk]:
        """
        Zerlegt ein Dokument in Chunks.

        Args:
            document: Das zu chunkende Dokument

        Returns:
            Liste von Chunk-Objekten mit document_id und position
        """
        text_chunks = _chunk_by_tokens(
            document.content,
            self.chunk_size_tokens,
            self.overlap_tokens,
        )

        result: List[Chunk] = []
        for i, content in enumerate(text_chunks):
            chunk_id = _compute_chunk_id(document.id, i, content)
            metadata = {
                **document.metadata,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
            }
            result.append(
                Chunk(
                    id=chunk_id,
                    document_id=document.id,
                    content=content,
                    metadata=metadata,
                    position=i,
                )
            )
        return result


def _compute_chunk_id(document_id: str, position: int, content: str) -> str:
    """Erzeugt eine stabile Chunk-ID."""
    raw = f"{document_id}:{position}:{content[:200]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
