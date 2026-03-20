#!/usr/bin/env python3
"""
CLI zum Indexieren von Dokumenten für das RAG-System.

Beispiel:
    python scripts/index_rag.py --space documentation ./docs
    python scripts/index_rag.py --space code ./src
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Projekt-Root für Imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.rag.service import RAGService


async def main():
    parser = argparse.ArgumentParser(description="RAG-Dokumente indexieren")
    parser.add_argument(
        "path",
        type=str,
        help="Datei oder Verzeichnis zum Indexieren",
    )
    parser.add_argument(
        "--space",
        type=str,
        default="default",
        help="Knowledge Space (default, documentation, code, notes, ...)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Unterverzeichnisse durchsuchen (Default: True)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Nur oberstes Verzeichnis",
    )
    args = parser.parse_args()

    service = RAGService()
    manager = service.get_manager()

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"Fehler: Pfad existiert nicht: {path}")
        sys.exit(1)

    if path.is_file():
        try:
            n = await manager.index_document(args.space, str(path))
            print(f"Indexiert: {path.name} -> {n} Chunks in Space '{args.space}'")
        except Exception as e:
            print(f"Fehler: {e}")
            sys.exit(1)
    else:
        try:
            n = await manager.index_directory(
                args.space, str(path), recursive=args.recursive
            )
            print(f"Indexiert: {n} Chunks aus {path} in Space '{args.space}'")
        except Exception as e:
            print(f"Fehler: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
