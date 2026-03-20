# RAG-System – Architektur

## Übersicht

Das RAG-Subsystem (Retrieval Augmented Generation) erweitert den Chat um Kontext aus indexierten Dokumenten. Es läuft vollständig lokal ohne LangChain.

Erweiterungen:
- **Self-Improving Knowledge**: Wissen aus LLM-Antworten extrahieren und in den Knowledge Store aufnehmen
- **Research Agent**: Planner → RAG → LLM → Critic Workflow für tiefgehende Recherche

## Datenfluss

```
Documents → Chunking → Embeddings → Vector Database → Retriever → Context Builder → LLM Prompt
```

## Komponenten

| Modul | Aufgabe |
|-------|---------|
| `document_loader.py` | Lädt .md, .txt, .py, .json (PDF optional) |
| `chunker.py` | Zerlegt Dokumente in Chunks (500 Tokens, 50 Overlap) |
| `embedding_service.py` | Ollama nomic-embed-text für Vektoren |
| `vector_store.py` | ChromaDB für persistente Speicherung |
| `retriever.py` | Similarity Search, Top-K |
| `context_builder.py` | Formatiert Chunks für den Prompt |
| `rag_pipeline.py` | Verbindet Retriever + Context + Prompt-Template |
| `knowledge_space.py` | Verwaltet Spaces (projects, code, documentation, notes) |
| `service.py` | Fassade für Chat-Integration |

## Knowledge Spaces

Jeder Space hat einen eigenen Dokumentpool und eine eigene Vektordatenbank:

- `default` – allgemeiner Kontext
- `documentation` – Doku
- `code` – Quellcode
- `notes` – Notizen
- `projects` – Projekt-spezifisch

## Verwendung

### 1. Dokumente indexieren

```bash
# Einzelne Datei
python scripts/index_rag.py --space documentation ./README.md

# Verzeichnis rekursiv
python scripts/index_rag.py --space code ./src

# Nur oberste Ebene
python scripts/index_rag.py --space notes ./notes --no-recursive
```

### 2. RAG im Chat aktivieren

- **Header**: Checkbox „RAG“ aktivieren
- **Einstellungen**: RAG aktiv, Space wählen, Top-K anpassen

### 3. Beispiel-RAG-Query

User: „Wie funktioniert die Chat-Integration?“

1. Retriever sucht relevante Chunks
2. Context Builder formatiert sie
3. Prompt: „Nutze ausschließlich den folgenden Kontext …“
4. LLM antwortet auf Basis des Kontexts

Ohne Treffer: normaler Chat (kein Kontext).

## Abhängigkeiten

- **Ollama** mit `nomic-embed-text`: `ollama pull nomic-embed-text`
- **chromadb**: `pip install chromadb`

## Self-Improving Knowledge

Workflow: LLM Answer → Knowledge Extraction → Validation → Vector DB Update

Module:
- `knowledge_extractor.py`: Extrahiert KnowledgeEntries aus Antworten (LLM-gestützt)
- `knowledge_validator.py`: Heuristische und optionale LLM-Validierung
- `knowledge_updater.py`: Speichert in Space `self_improving`

Aktivierung: Checkbox „Self-Improve“ im Header oder in den Einstellungen.

## Research Agent

Workflow: User Prompt → Planner (qwen2.5) → RAG Retriever → LLM Analysis (gpt-oss) → Critic (mistral) → Final Answer

Aktivierung: Rolle „Research“ im Header oder `/research` im Chat.

## Fehlerbehandlung

- Fehlende Dokumente → DocumentLoadError
- Embedding-Fehler → Fallback: leere Ergebnisse, normaler Chat
- DB-Fehler → geloggt, Chat läuft weiter
- Leere Retrieval-Ergebnisse → kein RAG-Kontext, normaler Chat
