# RAG

## Verwandte Themen

- [Chat](../chat/README.md) · [Settings](../settings/README.md) · [Provider](../providers/README.md) (Embeddings/Modelle)  
- [Feature: RAG](../../../docs/FEATURES/rag.md) · [Hilfe: Knowledge](../../../help/operations/knowledge_overview.md)

## 1. Fachsicht

**RAG** (Retrieval-Augmented Generation) liefert **Chunks aus indexierten Dokumenten** als zusätzlichen Kontext für Modellanfragen. Implementierung im Paket **`app/rag/`** mit ChromaDB-Anbindung (`vector_store.py`, `retriever.py`, `context_builder.py`, `rag_pipeline.py`, …). Die GUI pflegt Quellen und Indexierung unter **Operations → Knowledge**; Schalter wie `rag_enabled` und `rag_space` liegen in **`AppSettings`**.

## 2. Rollenmatrix

| Rolle | Nutzung |
|-------|---------|
| **Fachanwender** | Knowledge-Workspace; RAG in Chat aktivieren (wenn UI/Settings es erlauben). |
| **Admin** | `chromadb`-Installation, Verzeichnis `./chroma_db` (typisch), Embedding-Modell in Ollama. |
| **Entwickler** | `app/rag/*.py`, `app/services/knowledge_service.py`, `app/gui/knowledge_backend.py`. |
| **Business** | „Wissensbasierte Antworten“. |

## 3. Prozesssicht

```
User-Query (Chat)
        │
        ▼
KnowledgeService / RAG-Pfad (wenn rag_enabled)
        │
        ▼
Retriever → Vector Store (ChromaDB)
        │
        ▼
context_builder / rag_pipeline → angereicherter Prompt
        │
        ▼
LLM (gleicher Pfad wie Chat)
```

**Wichtige Module:** `service.py`, `retriever.py`, `vector_store.py`, `context_builder.py`, `embedding_service.py`, `document_loader.py`, `chunker.py`, `knowledge_space.py`.

## 4. Interaktionssicht

**UI**

- `operations_knowledge` → `KnowledgeWorkspace` (`operations_screen.py`)
- Backend-Brücke: `app/gui/knowledge_backend.py`

**Services**

- `app/services/knowledge_service.py`
- Registrierter Service-Name `rag` / `knowledge_service` (siehe `docs/SYSTEM_MAP.md`)

**Settings (`AppSettings`)**

- `rag_enabled`, `rag_space`, `rag_top_k`, `self_improving_enabled`, `chat_mode` (RAG-bezogen je nach Verwendung im Code)

**Externe Abhängigkeit**

- Paket `chromadb` in `requirements.txt`
- Optional: `scripts/index_rag.py` für Indexierung (referenziert in `help/troubleshooting/troubleshooting.md`)

## 5. Fehler- / Eskalationssicht

| Problem | Ursache |
|---------|---------|
| Keine Treffer | Leerer Index, falscher `rag_space`, Embedding-Modell fehlt. |
| ChromaDB-Fehler | Paket nicht installiert, korruptes Datenverzeichnis. |
| Hohe Latenz | Großes `rag_top_k` oder große Sammlung. |

## 6. Wissenssicht

| Begriff | Ort |
|---------|-----|
| `KnowledgeWorkspace` | `app/gui/domains/operations/knowledge/knowledge_workspace.py` |
| `operations_knowledge` | Workspace-ID |
| `vector_store`, `retriever` | `app/rag/` |
| `rag_enabled`, `rag_space`, `rag_top_k` | `app/core/config/settings.py` |

## 7. Perspektivwechsel

| Perspektive | Fokus |
|-------------|--------|
| **User** | Knowledge-Workspace, RAG-Toggle in Chat/Settings. |
| **Admin** | Index-Pipeline, Speicherplatz, Ollama-Embeddings. |
| **Dev** | Kontrakttests RAG, Failure-Mode-Tests unter `tests/failure_modes/`. |
