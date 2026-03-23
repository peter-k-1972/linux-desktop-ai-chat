# Feature: RAG

## Inhalt

- [Zweck](#zweck)
- [Funktionsweise](#funktionsweise)
- [Konfiguration](#konfiguration)
- [Beispiel](#beispiel)
- [Typische Fehler](#typische-fehler)

**Siehe auch**

- [Feature: Chat](chat.md) · [Feature: Providers](providers.md) · [Architektur – RAG](../ARCHITECTURE.md#22-rag)  
- [Benutzerhandbuch – RAG-Workflow](../USER_GUIDE.md#52-chat-mit-rag)

**Typische Nutzung**

- [RAG-Hilfe](../../help/operations/knowledge_overview.md) · [RAG-Einstellungen](../../help/settings/settings_rag.md)

## Zweck

Abfrage indexierter Dokumente zur Anreicherung von Chat-Anfragen (Retrieval-Augmented Generation).

RAG ergänzt den Chat dort, wo Antworten **faktenbasiert** an Ihre eigenen Texte, Notizen oder Projektdokumentation gebunden sein sollen. Statt nur aus dem Modellgewicht zu schöpfen, werden vor der Antwortgeneration relevante Ausschnitte aus einem Vektorindex geholt und dem Prompt beigefügt. Das ist unabhängig vom **Chat-Kontext** (Projekt-/Session-Metadaten): Beide Mechanismen können parallel aktiv sein.

## Funktionsweise

Der Ablauf ist grob: Indexierung legt Chunks und Embeddings in ChromaDB ab; zur Anfragezeit wählt der Retriever passende Stücke aus; der Knowledge-/Chat-Pfad fügt sie in die Modellanfrage ein. Die genaue Verdrahtung sitzt in `app/rag/`, `app/services/knowledge_service.py` und den Knowledge-Oberflächen unter Operations.

- **Paket:** `app/rag/` – Retriever, Einbindung ChromaDB, Kontextaufbau für Prompts.  
- **Service:** `app/services/knowledge_service.py` – Orchestrierung aus der GUI (`knowledge_backend.py`).  
- **UI:** Operations → **Knowledge** (`knowledge_workspace.py`).  
- **Indexierung:** Skripte unter `scripts/` (z. B. `scripts/index_rag.py` – wie in `help/troubleshooting/troubleshooting.md` referenziert).

## Konfiguration

| Schlüssel (`AppSettings`) | Bedeutung |
|---------------------------|-----------|
| `rag_enabled` | RAG global an/aus |
| `rag_space` | logischer Space (z. B. default, documentation, code, notes, projects – wie in Settings gespeichert) |
| `rag_top_k` | Anzahl der Chunks |
| `self_improving_enabled` | Zusatzpfad Self-Improving (siehe `AppSettings`) |

Abhängigkeit: `chromadb` in `requirements.txt`.

## Beispiel

**Beispiel** — Indexierung per Skript:

```bash
# Index (Beispiel aus Hilfe troubleshooting)
python scripts/index_rag.py --space default ./docs
```

In der App: RAG aktivieren, Space wählen, im Chat eine Frage stellen, die dokumentbasiert beantwortbar ist.

## Typische Fehler

| Problem | Ursache |
|---------|---------|
| Keine Treffer | Index leer, falscher Space, Embedding-Modell fehlt |
| ChromaDB-Fehler | Paket nicht installiert oder korruptes Datenverzeichnis (`./chroma_db`) |
| Langsame Antworten | hohes `rag_top_k` oder große Sammlung |
