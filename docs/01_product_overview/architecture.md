# Architektur (Produktüberblick)

**Kanonische technische Beschreibung:** [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) · Orientierung Screens/Navigation: [`docs/00_map_of_the_system.md`](../00_map_of_the_system.md).

Die frühere flache `app/`-Baumdarstellung mit `app/ui/` und Root-`settings.py` entspricht nicht dem aktuellen Stand. GUI liegt unter **`app/gui/`**, Einstellungslogik unter **`app/core/config/`**.

## Inhalt

- [Kurz: Schichten](#kurz-schichten)
- [Datenfluss (unverändert gültig)](#datenfluss-unverändert-gültig)
- [Persistenz](#persistenz)

**Siehe auch**

- [ARCHITECTURE.md](../ARCHITECTURE.md) — vollständige Schichten, Verantwortlichkeiten, Kontext/Settings/Provider  
- [Feature: Chat](../FEATURES/chat.md) · [Feature: Context](../FEATURES/context.md) · [Feature: RAG](../FEATURES/rag.md) · [Feature: Agents](../FEATURES/agents.md)  
- [Workflows](../../docs_manual/workflows/chat_usage.md) · [Kontext](../../docs_manual/workflows/context_control.md)

**Konzept → Umsetzung**

| Thema | Vertiefung |
|-------|------------|
| Chat-Pfad | [Feature: Chat](../FEATURES/chat.md), `app/services/chat_service.py` |
| Kontext / Modus | [Feature: Context](../FEATURES/context.md), `app/chat/context.py` |
| RAG | [Feature: RAG](../FEATURES/rag.md), `app/rag/` |
| Agenten / Delegation | [Feature: Agents](../FEATURES/agents.md), `app/agents/` |

## Kurz: Schichten

| Schicht | Pfad |
|---------|------|
| GUI | `app/gui/` |
| Services | `app/services/` |
| Kontext / Chat-Helfer | `app/chat/`, `app/context/` |
| Settings (Konfiguration) | `app/core/config/settings.py` |
| Provider | `app/providers/` |
| LLM | `app/llm/` |
| Agenten | `app/agents/` |
| RAG | `app/rag/` |

## Datenfluss (unverändert gültig)

### Chat

```
User Input → Slash-Command-Parser (app/core/commands/) → Modell-Router / Orchestrator
    → Provider (Local/Cloud) → Ollama → Stream (optional) → Output-Pipeline → GUI
```

### RAG

```
User Query → RAG-/Knowledge-Service → Retriever (ChromaDB) → erweiterter Prompt → LLM
```

### Agenten

```
Agentenwahl → AgentProfile (system prompt, Modell) → gleicher Chat-Pfad wie oben
```

### Delegation

```
/delegate → Agenten-Pipeline (Planner, Delegation Engine, Execution Engine) in app/agents/
```

## Persistenz

- Einstellungen: `QSettings` über `SettingsBackend` (Keys in `AppSettings`)
- Chat-Historie: SQLite (`chat_history.db`)
- Prompts: Datenbank oder Verzeichnis (`prompt_storage_type`)
- RAG: ChromaDB (lokales Verzeichnis, typisch `./chroma_db`)
