#!/usr/bin/env python3
"""
Build a Chroma vector index from data/doc_index.json (documentation search).

1. Load chunks from doc_index.json
2. Compute embeddings (Ollama, same stack as app.rag.embedding_service)
3. Persist to Chroma: collection name "documentation"

Prerequisites:
  - Run: python3 tools/build_doc_index.py
  - Ollama running with an embedding model (default: nomic-embed-text)

Run: python3 tools/build_doc_embeddings.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_INDEX = PROJECT_ROOT / "data" / "doc_index.json"
DEFAULT_CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_documentation"
COLLECTION_NAME = "documentation"
CHROMA_ADD_BATCH = 128


class _SupportsEmbed(Protocol):
    async def embed(self, text: str) -> list[float]: ...


def _truncate(s: str, limit: int) -> str:
    if not s:
        return ""
    if len(s) <= limit:
        return s
    return s[: limit - 1] + "…"


def _chunk_document_for_embedding(chunk: dict[str, Any]) -> str:
    title = (chunk.get("title") or "").strip()
    section = (chunk.get("section") or "").strip()
    body = (chunk.get("content") or "").strip()
    parts = [p for p in (title, section, body) if p]
    return "\n\n".join(parts) if parts else " "


def _chunk_metadata(
    chunk: dict[str, Any],
    chunk_index: int,
    embedding_model: str,
) -> dict[str, Any]:
    tags = chunk.get("tags") or []
    if isinstance(tags, list):
        tags_s = ",".join(str(t) for t in tags)
    else:
        tags_s = str(tags)
    return {
        "file_path": _truncate(str(chunk.get("file_path") or ""), 1024),
        "anchor": _truncate(str(chunk.get("anchor") or ""), 512),
        "title": _truncate(str(chunk.get("title") or ""), 2000),
        "section": _truncate(str(chunk.get("section") or ""), 2000),
        "tags": _truncate(tags_s, 2000),
        "embedding_model": _truncate(embedding_model, 256),
        "chunk_index": int(chunk_index),
    }


def _load_chunks(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks = data.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError("doc_index.json: missing or invalid 'chunks' array")
    return [c for c in chunks if isinstance(c, dict)]


async def _embed_texts_limited(
    svc: _SupportsEmbed,
    texts: list[str],
    concurrency: int,
) -> list[list[float]]:
    """Strict embeddings (no zero-vector fallback). Bounded parallelism for Ollama."""
    sem = asyncio.Semaphore(max(1, concurrency))

    async def _one(t: str) -> list[float]:
        async with sem:
            return await svc.embed(t)

    return await asyncio.gather(*[_one(t) for t in texts])


async def _embed_and_upsert(
    chunks: list[dict[str, Any]],
    embedding_model: str,
    base_url: str,
    embed_concurrency: int,
    chroma_dir: Path,
) -> None:
    from app.rag.embedding_service import EmbeddingService

    import chromadb
    from chromadb.config import Settings

    embed_svc = EmbeddingService(model=embedding_model, base_url=base_url, batch_size=32)

    chroma_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(chroma_dir),
        settings=Settings(anonymized_telemetry=False),
    )

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine",
            "embedding_model": embedding_model,
            "source": "doc_index.json",
            "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )

    total = len(chunks)
    for start in range(0, total, CHROMA_ADD_BATCH):
        end = min(start + CHROMA_ADD_BATCH, total)
        batch = chunks[start:end]
        texts = [_chunk_document_for_embedding(c) for c in batch]
        embeddings = await _embed_texts_limited(embed_svc, texts, embed_concurrency)
        if not embeddings:
            continue
        dim = len(embeddings[0])
        for e in embeddings:
            if len(e) != dim:
                raise RuntimeError("Inconsistent embedding dimensions in batch")

        ids = [f"doc:{start + i:07d}" for i in range(len(batch))]
        documents = texts
        metadatas = [_chunk_metadata(batch[i], start + i, embedding_model) for i in range(len(batch))]
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"Indexed {end}/{total} chunks", flush=True)

    print(f"Collection '{COLLECTION_NAME}' now has {collection.count()} vectors at {chroma_dir}")


def main(argv: list[str] | None = None) -> int:
    from app.rag.embedding_service import DEFAULT_EMBEDDING_MODEL

    parser = argparse.ArgumentParser(description="Build Chroma documentation vector index from doc_index.json.")
    parser.add_argument(
        "--index",
        type=Path,
        default=DEFAULT_INDEX,
        help=f"Path to doc_index.json (default: {DEFAULT_INDEX})",
    )
    parser.add_argument(
        "--chroma-dir",
        type=Path,
        default=DEFAULT_CHROMA_DIR,
        help=f"Chroma persist directory (default: {DEFAULT_CHROMA_DIR})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_EMBEDDING_MODEL,
        help=f"Ollama embedding model (default: {DEFAULT_EMBEDDING_MODEL})",
    )
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama base URL",
    )
    parser.add_argument(
        "--embed-concurrency",
        type=int,
        default=6,
        help="Parallel Ollama embedding requests (default: 6)",
    )
    args = parser.parse_args(argv)

    index_path = args.index.resolve()
    if not index_path.is_file():
        print(f"Index file not found: {index_path}", file=sys.stderr)
        print("Run: python3 tools/build_doc_index.py", file=sys.stderr)
        return 1

    try:
        chunks = _load_chunks(index_path)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"Failed to read index: {e}", file=sys.stderr)
        return 1

    if not chunks:
        print("No chunks in index.", file=sys.stderr)
        return 1

    try:
        asyncio.run(
            _embed_and_upsert(
                chunks,
                embedding_model=args.model,
                base_url=args.ollama_url,
                embed_concurrency=max(1, args.embed_concurrency),
                chroma_dir=args.chroma_dir.resolve(),
            )
        )
    except ImportError as e:
        print(f"Missing dependency: {e}", file=sys.stderr)
        print("Install: pip install chromadb aiohttp", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Build failed: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
