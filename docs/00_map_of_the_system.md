# Map of the System – Linux Desktop Chat

**Purpose:** Quick human-readable overview of the entire system.  
**Audience:** New team members, architects, anyone needing orientation.

---

## 1. What Is This?

**Linux Desktop Chat** is a local AI desktop platform. It is not a single chat tool but an **AI-Operations-Plattform** with multiple workspaces:

- **Chat** — Conversations with local/cloud LLMs
- **Knowledge** — RAG: context from indexed documents
- **Prompt Studio** — Reusable prompts and templates
- **Agents** — Specialized personas (Code, Research, Media, …)
- **Projects** — Project-scoped data and workspaces
- **Control Center** — Models, providers, agents, tools, data stores
- **QA & Governance** — Test inventory, coverage, incidents, replay
- **Runtime / Debug** — EventBus, logs, metrics, LLM calls, agent activity
- **Settings** — Application, appearance, AI models, data, privacy

---

## 2. Global vs Project-Scoped

| Scope | What | Examples |
|-------|------|----------|
| **Global** | App-wide, not tied to a project | Settings, Control Center (models, providers, agents), Runtime/Debug, QA Governance |
| **Project-scoped** | Data belongs to the active project | Chat conversations, Knowledge sources, Prompts, Agent tasks, Project list |

The **active project** is selected in the Project Hub or sidebar. Chat, Knowledge, Prompt Studio, and Agent Tasks show project-specific data when a project is active; otherwise they operate in a global/default context.

---

## 3. Workspace Overview

| Workspace | Location | Purpose |
|-----------|----------|---------|
| **Command Center** | Dashboard | System status, active work, QA status, quick actions |
| **Project Hub** | Project Hub | Project overview, switching |
| **Operations** | Main area | Chat, Agent Tasks, Knowledge, Prompt Studio, Projects |
| **Control Center** | Main area | Models, Providers, Agents, Tools, Data Stores |
| **QA & Governance** | Main area | Test Inventory, Coverage Map, Gap Analysis, Incidents, Replay Lab |
| **Runtime / Debug** | Main area | EventBus, Logs, Metrics, LLM Calls, Agent Activity, System Graph |
| **Settings** | Main area | Application, Appearance, AI Models, Data, Privacy, Advanced, Project, Workspace |

---

## 4. Navigation Structure

```
Sidebar (left)
├── Kommandozentrale (Command Center)
├── Operations
│   ├── Chat
│   ├── Agent Tasks
│   ├── Knowledge
│   ├── Prompt Studio
│   └── Projects
├── Control Center
│   ├── Models
│   ├── Providers
│   ├── Agents
│   ├── Tools
│   └── Data Stores
├── QA & Governance
│   ├── Test Inventory
│   ├── Coverage Map
│   ├── Gap Analysis
│   ├── Incidents
│   └── Replay Lab
├── Runtime / Debug
│   ├── EventBus
│   ├── Logs
│   ├── Metrics
│   ├── LLM Calls
│   ├── Agent Activity
│   └── System Graph
└── Settings
```

---

## 5. Major Subsystems

| Subsystem | Location | Role |
|-----------|----------|------|
| **Shell** | `app/gui/shell/` | Main window, docking, top bar |
| **Navigation** | `app/gui/navigation/` | Sidebar, breadcrumbs, command palette |
| **Workspace Host** | `app/gui/workspace/` | Screen registry, area switching |
| **Domains** | `app/gui/domains/` | Operations, Control Center, QA, Runtime, Settings |
| **Chat Backend** | `app/gui/chat_backend.py` | Chat service integration |
| **Knowledge Backend** | `app/gui/knowledge_backend.py` | RAG, indexing |
| **Inspector** | `app/gui/inspector/` | Right panel: context for Chat, Prompt Studio |
| **Monitors** | `app/gui/monitors/` | Bottom panel: logs, events, metrics |
| **Agents** | `app/agents/` | Agent profiles, repository, service |
| **RAG** | `app/rag/` | Retriever, ChromaDB, context builder |
| **Prompts** | `app/prompts/` | Prompt storage, templates |
| **LLM** | `app/llm/` | Completion, output pipeline |
| **Providers** | `app/providers/` | Local/Cloud Ollama |
| **QA** | `app/qa/` | QA adapters, DTOs |

---

## 6. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Shell (MainWindow, Docking, Top Bar)                              │
├─────────────────────────────────────────────────────────────────┤
│  Sidebar │ Main Workspace (Screens) │ Inspector │ Bottom Panel   │
├──────────┼──────────────────────────┼───────────┼────────────────┤
│  Nav     │  OperationsScreen       │  Chat     │  Logs          │
│  Areas   │  ControlCenterScreen    │  Context │  Events        │
│          │  QAGovernanceScreen     │  Prompt  │  Metrics       │
│          │  RuntimeDebugScreen     │  Studio  │  Agent         │
│          │  SettingsScreen        │          │  Activity      │
└──────────┴──────────────────────────┴───────────┴────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Services: ChatBackend, KnowledgeBackend, Infrastructure         │
├─────────────────────────────────────────────────────────────────┤
│  RAG (ChromaDB) │ Agents │ Prompts │ LLM │ Providers (Ollama)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Relationships Between Key Areas

| From | To | Relationship |
|------|-----|--------------|
| **Chat** | **Knowledge (RAG)** | Chat can augment prompts with RAG context when enabled |
| **Chat** | **Prompts** | Chat uses prompts from Prompt Studio; can apply templates |
| **Chat** | **Agents** | User selects agent → system prompt + model for conversation |
| **Chat** | **Settings** | Theme, model, RAG toggle, temperature, etc. |
| **Knowledge** | **RAG** | Knowledge workspace manages sources; RAG indexes and retrieves |
| **Prompt Studio** | **Chat** | Prompts can be applied to Chat composer |
| **Agents** | **Control Center** | Agent definitions live in Control Center; used in Operations |
| **QA & Governance** | **Runtime** | Incidents, replay; Runtime shows events, logs |
| **Settings** | **All** | Global configuration affects all workspaces |

---

## 8. Data Flow (Simplified)

- **Chat:** User input → Slash commands / Router → Orchestrator → Provider → Ollama → Stream → UI
- **RAG:** User query → RAGService.augment_if_enabled() → Retriever (ChromaDB) → Context Builder → Augmented prompt → LLM
- **Agents:** User selects agent → AgentProfile (system prompt, model) → Chat flow

---

## 9. Entry Points

| Command | Purpose |
|---------|---------|
| `python main.py` | Standard start (delegates to GUI shell) |
| `python run_gui_shell.py` | Direct GUI shell start |
| `python archive/run_legacy_gui.py` | Legacy GUI (deprecated) |

---

## 10. Where to Look First

| Role | Start Here |
|------|------------|
| **New developer** | [Architecture](01_product_overview/architecture.md), [GUI Repository](04_architecture/GUI_REPOSITORY_ARCHITECTURE.md), [TRACE_MAP](TRACE_MAP.md) |
| **Maintainer** | [SYSTEM_MAP](SYSTEM_MAP.md), [TRACE_MAP](TRACE_MAP.md), `app/gui/domains/` |
| **UX / QA** | [UX Concept](01_product_overview/UX_CONCEPT.md), [06_operations_and_qa](06_operations_and_qa/) |
| **End user** | In-app Help (Help button), [Introduction](01_product_overview/introduction.md) |

---

## 11. Map Documents (Orientation)

| Document | Role |
|----------|------|
| **00_map_of_the_system.md** (this file) | Human-readable orientation map |
| **SYSTEM_MAP.md** | Generated structural map (app, workspaces, services) |
| **TRACE_MAP.md** | Code ↔ Help ↔ Tests traceability map |
| **FEATURE_REGISTRY.md** | Feature → implementation index (workspace, code, services, help, tests, QA) |

---

## 12. Further Reading

- [Architecture](01_product_overview/architecture.md)
- [UX Concept](01_product_overview/UX_CONCEPT.md)
- [GUI Repository Architecture](04_architecture/GUI_REPOSITORY_ARCHITECTURE.md)
- [Introduction](01_product_overview/introduction.md)
