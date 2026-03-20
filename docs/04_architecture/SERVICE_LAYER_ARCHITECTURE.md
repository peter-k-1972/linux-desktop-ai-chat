# Service-Layer-Architektur

## Übersicht

Die GUI spricht ausschließlich mit **Services**, nicht mit Providern, DB oder Chroma direkt.

```
GUI / Workspace / Panel
    ↓
Service Layer (app/services/)
    ↓
Backend / Provider / Storage / Runtime
```

## Services

| Service | Verantwortung | Backend |
|---------|---------------|---------|
| **ChatService** | Sessions, Nachrichten, Chat senden | DatabaseManager, OllamaClient |
| **ModelService** | Modellliste, Standardmodell | OllamaClient, AppSettings |
| **ProviderService** | Provider-Status, Ollama-Erreichbarkeit | OllamaClient |
| **KnowledgeService** | Collections, Quellen, Retrieval | RAGService, ChromaDB |
| **AgentService** | Agentenliste, Agent starten, Status | AgentService (CRUD), AgentTaskRunner, DebugStore |

## Zugriff

```python
from app.services import (
    get_chat_service,
    get_model_service,
    get_provider_service,
    get_knowledge_service,
    get_agent_service,
)
```

## Fehler- und Statusmodell

Services nutzen `ServiceResult[T]` für einheitliche Rückgaben:

```python
from app.services.result import ServiceResult, OperationStatus

# Erfolg
result = ServiceResult.ok(data)
# result.success == True, result.data == data

# Fehler
result = ServiceResult.fail("Fehlermeldung")
# result.success == False, result.error == "Fehlermeldung"

# Laufend
result = ServiceResult.running("Läuft…")
# result.status == OperationStatus.RUNNING
```

## Datenflüsse

### Chat
1. `ChatWorkspace` → `get_chat_service()` → `load_chat()`, `chat()`, `save_message()`
2. `ChatSessionExplorerPanel` → `get_chat_service()` → `list_chats()`, `create_chat()`
3. `ChatInputPanel` → `get_model_service()` → `get_default_model()` (für Modellauswahl)

### Modelle
1. `ModelsWorkspace` → `get_model_service()` → `get_models_full()`, `get_default_model()`, `set_default_model()`
2. `ChatWorkspace` → `get_model_service()` → `get_models()` (für ComboBox)

### Provider
1. `ProvidersWorkspace` → `get_provider_service()` → `get_provider_status()`

### Knowledge
1. `KnowledgeWorkspace` → `get_knowledge_service()` → `add_document()`, `add_directory()`, `retrieve()`
2. `KnowledgeCollectionsPanel` → `get_knowledge_service()` → `list_spaces()`
3. `KnowledgeOverviewPanel` → `get_knowledge_service()` → `get_overview()`
4. `KnowledgeSourcesPanel` → `get_knowledge_service()` → `list_sources()`

### Agenten
1. `AgentTasksWorkspace` → `get_agent_service()` → `list_agents()`, `start_agent_task()`
2. `AgentRegistryPanel` → `get_agent_service()` → `list_agents()`
3. `AgentTaskRunner` (intern) → `get_chat_service()`, `get_model_service()` für Modellaufrufe

## Infrastruktur

`get_infrastructure()` liefert die gemeinsame Instanz von:
- `OllamaClient`
- `DatabaseManager`
- `AppSettings`

Services nutzen diese Infrastruktur, um doppelte Instanzen zu vermeiden.

## Initialisierung

In `run_gui_shell.py`:
```python
from app.services.infrastructure import get_infrastructure
get_infrastructure()  # Initialisiert Ollama, DB, Settings
```

Services werden lazy erstellt beim ersten `get_*_service()`-Aufruf.

## Async / Hintergrundarbeit

- Lange laufende Aufrufe (Ollama, Retrieval, Agent Tasks) sind `async`
- GUI nutzt `asyncio.create_task()` mit qasync Event-Loop
- Keine Blockierung der GUI

## Deprecated

- `app.gui.chat_backend` → `app.services.chat_service` + `app.services.model_service`
- `app.gui.knowledge_backend` → `app.services.knowledge_service`

Die alten Backends existieren noch als Kompatibilitätswrapper und delegieren an die Services.
