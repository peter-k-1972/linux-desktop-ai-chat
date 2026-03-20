# Chat Guard v2 – Abschlussreport

**Stand:** 2026-03-17  
**Ziel:** Hybrid-Guard mit optionaler ML-/Embedding-Intent-Erkennung.

---

## 1. Gewählte Hybrid-Architektur

```
User-Input
    ↓
Heuristik v1 (assess_intent)
    ↓
[optional] MLIntentClassifier (Embedding + Nearest-Neighbor)
    ↓
Fusion (fuse)
    ↓
Sanity + Prompt-Härtung
```

- **Heuristik:** Immer aktiv, primär
- **ML:** Optional über `chat_guard_ml_enabled` (default: False)
- **Fusion:** Klare Regeln, Heuristik gewinnt bei starken Signalen

---

## 2. Verwendete ML-/Embedding-Strategie

- **EmbeddingService** (Ollama nomic-embed-text) – vorhandene RAG-Infrastruktur
- **Nearest-Neighbor** auf Intent-Beispielen (INTENT_EXAMPLES)
- **Cosine-Similarity** für Ähnlichkeit, Confidence = normalisierte Similarity
- **Kein Chroma** für Intent – nur in-memory Vergleich
- **Fallback:** Bei Embedding-Fehler → (CHAT, 0.0), Fusion nutzt Heuristik

---

## 3. Entscheidungsfusion

| Bedingung | Ergebnis |
|-----------|----------|
| Heuristik = command | Heuristik gewinnt |
| ML-Confidence < 0.5 | Heuristik |
| Heuristik = chat, ML hohe Confidence | ML |
| Heuristik ≠ ML (beide nicht chat) | Heuristik (fusion) |
| Übereinstimmung | Beide (fusion) |
| ML deaktiviert | Heuristik |

---

## 4. Feature-Flag / Aktivierung

- **Setting:** `chat_guard_ml_enabled` (bool)
- **Default:** False
- **Speicherung:** AppSettings (QSettings / InMemoryBackend)
- **Aktivierung:** Über Einstellungen (wenn UI vorhanden) oder programmatisch

---

## 5. Intent-Beispielset

- **Datei:** `app/core/chat_guard/intent_examples.py`
- **Format:** Liste von (text, ChatIntent)
- **Umfang:** ~35 Beispiele über 6 Intents
- **Beispiele:** command, formal_reasoning, coding, knowledge_query, possibly_ambiguous, chat

---

## 6. Debugbarkeit

- **GuardResult:** heuristic_intent, ml_intent, ml_confidence, decision_source
- **guard_result_to_debug_dict():** Für Runtime/Inspector/QA
- Kein Log-Spam, nur bei Bedarf abrufbar

---

## 7. Tests

- **Fusion:** 5 Tests (command wins, low confidence fallback, ML bei chat, conflict, ML disabled)
- **ML-Classifier:** 1 Test (graceful failure ohne Embedding)
- **Debug:** 1 Test (guard_result_to_debug_dict)
- **Bestehende v1-Tests:** Unverändert bestanden

---

## 8. Grenzen von v2

- ML erfordert Ollama + nomic-embed-text
- Kein Training, nur vordefinierte Beispiele
- Keine UI für chat_guard_ml_enabled (nur programmatisch/Settings)
- Legacy ChatWidget nutzt eigenen Pfad (kein Guard)

---

## 9. Empfohlene nächste Ausbaustufe

1. **UI-Toggle** für chat_guard_ml_enabled in Einstellungen
2. **Intent-Beispiele erweitern** basierend auf Nutzung
3. **Routing v2:** routing_hint für Modellwahl nutzen
4. **Debug-Panel:** Guard-Metadaten anzeigen
5. **Agenten-Integration:** Guard in AgentTaskRunner-Pfad
