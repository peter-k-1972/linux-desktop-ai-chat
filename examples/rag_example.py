#!/usr/bin/env python3
"""
Beispiel: RAG-Pipeline ohne Chat-UI.

Voraussetzungen:
  - Ollama läuft mit nomic-embed-text: ollama pull nomic-embed-text
  - pip install chromadb aiohttp
"""

import asyncio
import sys
from pathlib import Path

# Projekt-Root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag import (
    load_document,
    Chunker,
    EmbeddingService,
    VectorStore,
    Retriever,
    ContextBuilder,
    RAGPipeline,
)


async def main():
    # 1. Dokument laden und chunkieren
    doc_path = Path(__file__).parent / "sample_doc.md"
    if not doc_path.exists():
        doc_path.write_text(
            "# Beispiel-Dokument\n\n"
            "Dieser Text beschreibt die Chat-Integration. "
            "Der Chat nutzt den ModelOrchestrator für die Modellauswahl. "
            "RAG erweitert den Prompt mit Kontext aus indexierten Dokumenten.\n\n"
            "## Architektur\n\n"
            "Documents → Chunking → Embeddings → Vector DB → Retriever → Context → LLM",
            encoding="utf-8",
        )
    doc = load_document(str(doc_path))
    chunker = Chunker(chunk_size_tokens=100, overlap_tokens=20)
    chunks = chunker.chunk_document(doc)

    # 2. Embeddings und Vector Store
    embed_svc = EmbeddingService()
    store = VectorStore(persist_directory="/tmp/rag_example_db", collection_name="example")
    embeddings = await embed_svc.embed_batch([c.content for c in chunks])
    store.add_chunks(
        [c.id for c in chunks],
        embeddings,
        [c.content for c in chunks],
        [c.metadata for c in chunks],
    )

    # 3. Retriever und Pipeline
    retriever = Retriever(store, embed_svc, top_k=3)
    pipeline = RAGPipeline(retriever, ContextBuilder())

    # 4. Query
    query = "Wie funktioniert die Chat-Integration?"
    context, retrieved = await pipeline.get_context_and_chunks(query, top_k=3)
    print("Query:", query)
    print("Gefundene Chunks:", len(retrieved))
    for i, c in enumerate(retrieved):
        print(f"  [{i+1}] {c.content[:80]}...")
    print("\nKontext für LLM:")
    print("-" * 40)
    print(context[:500] + "..." if len(context) > 500 else context)


if __name__ == "__main__":
    asyncio.run(main())
