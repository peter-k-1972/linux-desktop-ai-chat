# Knowledge / RAG Workspace – Implementierung

**Status:** Produktiv nutzbar  
**Datum:** 2026-03-15

## Startanweisung

```bash
python main.py
```

Navigation: Operations → Knowledge / RAG

Voraussetzungen:
- Ollama läuft (für Embeddings: nomic-embed-text)
- ChromaDB installiert (`pip install chromadb`)

## Architektur

### Klassen

| Klasse | Zweck |
|--------|-------|
| **KnowledgeBackend** | Service-Schicht: RAGService, Source-Registry, Retrieval |
| **KnowledgeWorkspace** | Orchestriert Collections, Quellen, Retrieval |
| **KnowledgeCollectionsPanel** | Liste der Spaces, Auswahl |
| **KnowledgeSourcesPanel** | Quellen eines Space, Hinzufügen (Datei/Ordner) |
| **KnowledgeOverviewPanel** | Übersicht: Spaces, Chunks, Quellen |
| **RetrievalTestPanel** | Query-Eingabe, Suchen, Treffer |
| **KnowledgeInspector** | Collection, Quelle, letzter Retrieval |

### Datenfluss

```
CollectionsPanel.collection_selected(space) ──► SourcesPanel.set_space()
                                              OverviewPanel.refresh()

SourcesPanel.add_source_requested(path) ──► Workspace._run_add_source()
                                            Backend.add_document/add_directory
                                            → ChromaDB, sources.json

RetrievalPanel.retrieval_requested(query) ──► Workspace._run_retrieval()
                                               Backend.retrieve()
                                               → Retriever → Treffer
```

### Backend

- **RAGService** – KnowledgeSpaceManager, Pipeline
- **Source-Registry** – `{base_path}/{space}/sources.json`
- **ChromaDB** – Vektor-Speicher pro Space
- **EmbeddingService** – Ollama nomic-embed-text

## Unterstützte Formate

- `.md`, `.txt`, `.py`, `.json`

## Fehlerbehandlung

- Keine Collection gewählt: Hinweis im Status
- Ungültige Datei: Fehlermeldung
- ChromaDB/Embedding-Fehler: Fehlermeldung im Status
