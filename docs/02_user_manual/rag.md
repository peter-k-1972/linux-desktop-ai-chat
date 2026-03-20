# RAG-Wissenssystem

## Übersicht

**RAG** (Retrieval Augmented Generation) erweitert den Chat um Kontext aus indexierten Dokumenten. Vollständig lokal, ohne LangChain.

## Datenfluss

```
Documents → Chunking → Embeddings → ChromaDB → Retriever → Context Builder → LLM Prompt
```

## Knowledge Spaces

| Space | Verwendung |
|-------|------------|
| default | Allgemeiner Kontext |
| documentation | Doku, README |
| code | Quellcode |
| notes | Notizen |
| projects | Projekt-spezifisch |

## Dokumente indexieren

```bash
# Einzelne Datei
python scripts/index_rag.py --space documentation ./README.md

# Verzeichnis rekursiv
python scripts/index_rag.py --space code ./src

# Nur oberste Ebene
python scripts/index_rag.py --space notes ./notes --no-recursive
```

## RAG im Chat aktivieren

- **Header**: Checkbox „RAG“ aktivieren
- **Einstellungen**: RAG aktiv, Space wählen, Top-K anpassen (Standard: 5)

## Self-Improving Knowledge

Wissen aus LLM-Antworten wird extrahiert und in den Knowledge Store aufgenommen.

- **Aktivierung**: Checkbox „Self-Improve“ im Header oder Einstellungen
- **Workflow**: LLM Answer → Knowledge Extractor → Validator → Vector DB
- **Space**: `self_improving`

## Abhängigkeiten

- Ollama mit `nomic-embed-text`: `ollama pull nomic-embed-text`
- chromadb: `pip install chromadb`

## Research Agent

Rolle „Research“ oder `/research` startet den Research-Workflow:

Planner (qwen2.5) → RAG Retriever → LLM (gpt-oss) → Critic (mistral) → Finale Antwort
