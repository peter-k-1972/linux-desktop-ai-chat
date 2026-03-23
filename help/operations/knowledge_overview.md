---
id: knowledge_overview
title: RAG-Wissenssystem
category: operations
tags: [rag, knowledge, chromadb, indexierung]
related: [chat_overview, settings_rag]
workspace: operations_knowledge
screen: operations
order: 30
---

# RAG-Wissenssystem

## Inhalt

- [Übersicht](#übersicht)
- [Datenfluss](#datenfluss)
- [Knowledge Spaces](#knowledge-spaces)
- [Dokumente indexieren](#dokumente-indexieren)
- [RAG im Chat aktivieren](#rag-im-chat-aktivieren)
- [Self-Improving Knowledge](#self-improving-knowledge)
- [Abhängigkeiten](#abhängigkeiten)
- [Research Agent](#research-agent)

**Siehe auch (Repository)**

- [Feature: RAG](../../docs/FEATURES/rag.md) · [Benutzerhandbuch – RAG-Workflow](../../docs/USER_GUIDE.md#52-chat-mit-rag) · [Modul RAG](../../docs_manual/modules/rag/README.md)

## Übersicht

**RAG** (Retrieval Augmented Generation) erweitert den Chat um Kontext aus indexierten Dokumenten. Vollständig lokal, ohne LangChain.

## Datenfluss

Grobweg von Dokument bis Prompt:

```
Documents → Chunking → Embeddings → ChromaDB → Retriever → Context Builder → LLM Prompt
```

Dokumente werden einem **Space** zugeordnet; der aktive Space in den Einstellungen muss zu Ihren indexierten Daten passen.

## Knowledge Spaces

| Space | Verwendung |
|-------|------------|
| default | Allgemeiner Kontext |
| documentation | Doku, README |
| code | Quellcode |
| notes | Notizen |
| projects | Projekt-spezifisch |

## Dokumente indexieren

**Beispiel — Kommandozeile**

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
