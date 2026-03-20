"""
RAG-Subsystem – Retrieval Augmented Generation.

Modulares, lokales RAG-System ohne LangChain.
Komponenten: Document Loader → Chunker → Embeddings → Vector Store → Retriever → Context Builder → LLM
"""

from app.rag.models import Chunk, Document
from app.rag.document_loader import (
    load_document,
    load_documents_from_directory,
    DocumentLoadError,
)
from app.rag.chunker import Chunker
from app.rag.embedding_service import EmbeddingService, EmbeddingError
from app.rag.vector_store import VectorStore, VectorStoreError
from app.rag.retriever import Retriever
from app.rag.context_builder import ContextBuilder
from app.rag.rag_pipeline import RAGPipeline
from app.rag.knowledge_space import KnowledgeSpaceManager
from app.rag.knowledge_models import KnowledgeEntry
from app.rag.knowledge_extractor import KnowledgeExtractor
from app.rag.knowledge_validator import KnowledgeValidator
from app.rag.knowledge_updater import KnowledgeUpdater
from app.rag.service import RAGService

__all__ = [
    "Document",
    "Chunk",
    "load_document",
    "load_documents_from_directory",
    "DocumentLoadError",
    "Chunker",
    "EmbeddingService",
    "EmbeddingError",
    "VectorStore",
    "VectorStoreError",
    "Retriever",
    "ContextBuilder",
    "RAGPipeline",
    "KnowledgeSpaceManager",
    "KnowledgeEntry",
    "KnowledgeExtractor",
    "KnowledgeValidator",
    "KnowledgeUpdater",
    "RAGService",
]
