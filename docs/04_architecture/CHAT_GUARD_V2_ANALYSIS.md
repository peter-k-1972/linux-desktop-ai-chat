# Chat Guard v2 – Analyse

**Stand:** 2026-03-17  
**Ziel:** Hybrid-Guard mit optionaler ML-/Embedding-Intent-Erkennung.

---

## 1. Aktueller Stand v1

- **Heuristik:** `assess_intent()` → (ChatIntent, risk_flags)
- **Sanity:** `run_sanity_check()` → sanity_flags
- **Prompt-Härtung:** `apply_prompt_hardening()` → system_hint
- **Service:** `ChatGuardService.assess()` → GuardResult
- **Integration:** ChatService.chat() ruft `_apply_chat_guard()` vor ollama_client.chat()

---

## 2. Vorhandene Embedding-/RAG-Infrastruktur

| Komponente | Pfad | Nutzung |
|------------|------|---------|
| EmbeddingService | app/rag/embedding_service.py | Ollama nomic-embed-text, async embed() |
| VectorStore | app/rag/vector_store.py | ChromaDB, query(embedding, n_results) |
| Retriever | app/rag/retriever.py | embed(query) → vector_store.query() |
| RAGService | app/rag/service.py | KnowledgeSpaceManager, Pipeline |

**EmbeddingService:** Lokal über Ollama, kein Online-Zwang. Voraussetzung: `ollama pull nomic-embed-text`.

---

## 3. Empfohlener Hybrid-Ansatz

```
User-Input
    ↓
Heuristik v1 (assess_intent)
    ↓
[optional] ML: Embedding + Nearest-Neighbor auf Intent-Beispielen
    ↓
Fusion: heuristic_intent + ml_intent + ml_confidence → final_intent
    ↓
Sanity + Prompt-Härtung (wie v1)
```

**Regeln:**
- Heuristik stark/eindeutig (z.B. command) → Heuristik gewinnt
- ML hohe Confidence, Heuristik schwach → ML kann helfen
- Widerspruch → Heuristik / possibly_ambiguous
- Beide schwach → chat oder possibly_ambiguous
- ML deaktiviert → reines v1

---

## 4. Mögliche ML-/Embedding-Quellen

| Option | Vor-/Nachteile |
|--------|----------------|
| **EmbeddingService (Ollama)** | Bereits da, lokal, async. Erfordert nomic-embed-text. |
| ChromaDB für Intent-Examples | Wiederverwendung, aber zusätzliche Collection. |
| Reine Python Cosine auf Embeddings | Kein Chroma nötig, nur EmbeddingService. |

**Empfehlung:** EmbeddingService + in-memory Nearest-Neighbor. Kein Chroma für Intent – nur für RAG. Einfache Cosine-Similarity in Python (ohne numpy).

---

## 5. Risiken

- **Ollama nicht erreichbar:** Embedding schlägt fehl → Fallback auf Heuristik
- **nomic-embed-text nicht installiert:** Gleicher Fallback
- **ML overrides Heuristik falsch:** Fusion-Regeln müssen konservativ sein
- **Latenz:** Embedding-API-Call pro Anfrage – akzeptabel, da vor Modellaufruf

---

## 6. Kleinste sinnvolle Ausbaustufe

1. Hybrid-Intent-Modell (heuristic_intent, ml_intent, final_intent, ml_confidence, decision_source)
2. Intent-Beispielset (5–8 Beispiele pro Intent, im Code)
3. MLIntentClassifier: embed + nearest-neighbor, Confidence = Cosine-Similarity
4. Fusion-Logik mit klaren Regeln
5. Feature-Flag `chat_guard_ml_enabled` (default: False für Stabilität)
6. GuardResult erweitern, Debug-Metadaten
7. ChatGuardService v2: assess() ruft Heuristik + optional ML + Fusion
