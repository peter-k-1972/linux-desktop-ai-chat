# Architektur

## Modulstruktur

```
app/
├── main.py              # MainWindow, App-Bootstrap
├── chat_widget.py       # Chat-Bereich (Conversation, Composer, Header)
├── sidebar_widget.py    # Chat-Liste, Datei-Explorer
├── settings.py          # QSettings-basierte Konfiguration
├── ollama_client.py     # Ollama API-Client
├── model_registry.py    # Modell-Metadaten
├── model_roles.py       # Semantische Rollen (FAST, THINK, CODE, …)
├── model_orchestrator.py # Modell-Routing, Provider-Aggregation
├── model_router.py      # route_prompt() – Rollen-Mapping
├── escalation_manager.py # Cloud-Eskalation
├── tools.py             # FileSystemTools (Workspace-sicher)
├── agents/              # Agenten-Subsystem
├── rag/                 # RAG-Subsystem
├── prompts/             # Prompt-Verwaltung
├── llm/                 # LLM-Completion, Output-Pipeline
├── commands/            # Slash-Commands
├── providers/           # Local/Cloud Ollama
├── ui/                  # UI-Komponenten
└── resources/           # Styles, Icons
```

## Datenfluss

### Chat-Flow

```
User Input → Slash-Command-Parser → Modell-Router → Orchestrator
    → Provider (Local/Cloud) → Ollama API → Stream → Output-Pipeline → UI
```

### RAG-Flow

```
User Query → RAGService.augment_if_enabled() → Retriever → Context Builder
    → Erweiterter Prompt → LLM
```

### Agenten-Flow

```
User wählt Agent → AgentProfile.system_prompt als System-Nachricht
    → Modell aus assigned_model / assigned_model_role
    → Chat wie gewohnt
```

## Delegation Engine

Für komplexe Aufgaben: Task Planner → Task Graph → Delegation Engine → Execution Engine.

- **Task Planner**: Zerlegt Anfrage in Tasks
- **Delegation Engine**: Ordnet Tasks Agenten zu
- **Execution Engine**: Führt Tasks aus, sammelt Ergebnisse

## Update-System

- Einstellungen: `QSettings` (OllamaChat/LinuxDesktopChat)
- Chat-Historie: SQLite (`chat_history.db`)
- Prompts: SQLite oder Verzeichnis (konfigurierbar)
- RAG: ChromaDB (persistente Vektordatenbank)
