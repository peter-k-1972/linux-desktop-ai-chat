# Architektur – Linux Desktop Chat

Stand der Beschreibung: abgeleitet aus Paketen unter `app/` (GUI, Services, Context, Settings, Provider). Verweise auf Code sind Pfadangaben im Repository.

Im ersten Abschnitt folgt ein Schichtenmodell; danach werden typische Datenflüsse (Chat, RAG, Agenten) und die Zuordnung zentraler Pakete beschrieben.

## Inhalt

- [1. Schichtenmodell](#1-schichtenmodell)
- [2. Datenfluss](#2-datenfluss)
- [3. Verantwortlichkeiten](#3-verantwortlichkeiten)
- [4. Zentrale Systeme](#4-zentrale-systeme)
- [5. Weiterlesen](#5-weiterlesen)

**Siehe auch**

- [Release-Systemkarte (Operations, O1–O4, R1–R4)](introduction/architecture.md) — Ist-Stand, Schichten, Mermaid, Modultabelle  
- [Benutzerhandbuch](USER_GUIDE.md) · [Entwicklerhandbuch](DEVELOPER_GUIDE.md) · [Systemkarte](00_map_of_the_system.md)  
- [Feature: Context](FEATURES/context.md) · [Feature: Chat](FEATURES/chat.md) · [Feature: Settings](FEATURES/settings.md) · [Feature: RAG](FEATURES/rag.md)  
- [Workflow Kontext](../docs_manual/workflows/context_control.md) · [Workflow Chat](../docs_manual/workflows/chat_usage.md)

**Konzept → Umsetzung (Kontext)**

| Konzept | Code / Feature |
|---------|----------------|
| Kontextfragment (Projekt/Chat/Topic) | `app/chat/context.py` — `ChatRequestContext`, `to_system_prompt_fragment` |
| Auflösung Modus/Detail/Overrides | `app/services/chat_service.py` — `_resolve_context_configuration` |
| Persistierte Schalter | `app/core/config/settings.py` — `AppSettings`, `chat_context_*` |
| Governance (optional) | [`04_architecture/CHAT_CONTEXT_GOVERNANCE.md`](04_architecture/CHAT_CONTEXT_GOVERNANCE.md) |

---

## 1. Schichtenmodell

```
GUI (PySide6)     app/gui/
       │
       ▼
Services          app/services/     (ChatService, KnowledgeService, ModelService, ProviderService, …)
       │
       ├──► Context / Chat-Helfer   app/chat/, app/context/
       ├──► Settings (Konfiguration) app/core/config/settings.py, settings_backend.py
       ├──► Agents                  app/agents/
       ├──► RAG                     app/rag/
       ├──► LLM / Output            app/llm/
       └──► Provider (HTTP)         app/providers/
```

- **GUI** sendet Nutzeraktionen an Services oder liest über Backends (`app/gui/chat_backend.py`, `knowledge_backend.py`).  
- **Services** orchestrieren Persistenz, Provider-Aufrufe und Kontextaufbau; sie enthalten die Entscheidung, **ob** Kontext injiziert wird (Context Mode `off` schließt Injektion aus).  
- **Context-Rendering** (`app/chat/context.py`) formatiert Projekt-/Chat-/Topic-Metadaten zu Textfragmenten; es importiert **kein** Settings-Modul für Geschäftslogik der App (Enums liegen in `app/core/config/chat_context_enums.py`).  
- **Settings** speichern Schlüssel/Werte (u. a. `chat_context_mode`, `chat_context_detail_level`, `chat_context_include_*`, `chat_context_profile*`, RAG, Modell).  
- **Provider** kapseln Ollama-API (lokal/cloud); sie erhalten fertige Message-Listen, keine UI.

---

## 2. Datenfluss

### 2.1 Chat-Anfrage (vereinfacht)

1. Nutzer sendet Text im Chat-Workspace.  
2. Slash-Commands werden in `app/core/commands/chat_commands.py` geparst (Rollen, `/auto`, `/cloud`, `/delegate`).  
3. `ChatService` baut Nachrichtenliste, löst Kontext-Konfiguration auf, injiziert ggf. Systemfragment (`app/services/chat_service.py`, `app/chat/context.py`).  
4. Modellwahl / Routing über Model-Service und Rollen (`app/core/models/`, Orchestrator/Router in `app/`).  
5. `app/providers/*` führt Completion gegen Ollama aus; Streaming optional (`chat_streaming_enabled` in `AppSettings`).  
6. Antwort fließt zurück in die GUI-Konversation.

### 2.2 RAG

1. Knowledge-Workspace / Service pflegt Quellen und Index.  
2. Bei aktivem RAG wendet der Pfad in `app/rag/` und `app/services/knowledge_service.py` Retrieval an.  
3. Angereicherter Prompt geht in dieselbe LLM-Pipeline wie der normale Chat.

### 2.3 Agenten und Delegation

- Agentenprofile: `app/agents/` (u. a. Repository, Tasks).  
- `/delegate` setzt in der Command-Verarbeitung `use_delegation=True`; die weitere Ausführung liegt in den Agenten-/Chat-Pfaden (Planner, Delegation, Execution in `app/agents/`).

---

## 3. Verantwortlichkeiten

| Bereich | Verantwortung |
|---------|----------------|
| **`app/gui/domains/operations/`** | Chat, Knowledge, Prompt Studio, Projects, Agent Tasks |
| **`app/gui/domains/control_center/`** | Modelle, Provider, Agenten-Verwaltung, Tools, Data Stores |
| **`app/gui/domains/settings/`** | SettingsScreen, Kategorien, Navigation (`navigation.py`, `settings_workspace.py`) |
| **`app/services/chat_service.py`** | Sendepfad, Kontextauflösung, Guard, Streaming-Koordination |
| **`app/chat/context_profiles.py`** | Profile → Mode/Detail/Felder; Hint- und Policy-Zuordnung zu Profilen |
| **`app/context/replay/`** | Deterministischer Replay/Repro von Kontextausgaben |
| **`app/cli/`** | Kopfloser Aufruf von Replay/Repro/Registry ohne GUI |

---

## 4. Zentrale Systeme

### 4.1 Context

- **Context Mode** (`ChatContextMode`): `off` – keine Injektion; `neutral` / `semantic` – unterschiedliche Textdarstellung in `ChatRequestContext.to_system_prompt_fragment()`.  
- **Detail Level** (`ChatContextDetailLevel`): `minimal`, `standard`, `full` – steuert Umfang der Felder/Darstellung.  
- **Profile** (`ChatContextProfile` in `settings.py`): `strict_minimal`, `balanced`, `full_guidance` – Auflösung über `resolve_chat_context_profile()` in `app/chat/context_profiles.py`.  
- **Override / Auflösungsreihenfolge** in `ChatService._resolve_context_configuration()`:  
  `profile_enabled` → `explicit_context_policy` → `chat_default_context_policy` → `project_default_context_policy` → `request_context_hint` → `individual_settings` (direkte Settings-Keys).  
- **Render-Limits:** `app/chat/context_limits.py` (Zeichen-/Zeilenbudgets).  
- **Erklärbarkeit:** `app/context/explainability/`, `app/services/context_explain_service.py` (u. a. policy chain in serialisierten Traces).

### 4.2 Settings

- Klasse **`AppSettings`** in `app/core/config/settings.py`, Persistenz über **`SettingsBackend`** (`settings_backend.py`; in der GUI typischerweise Qt/QSettings).  
- Schlüssel für Kontext siehe Abschnitt 4.1; weitere: Modell, Temperatur, RAG, Prompt-Speicher, Routing-Flags, Streaming.  
- **GUI:** acht Kategorien, registriert in `app/gui/domains/settings/settings_workspace.py` und `navigation.py`.

### 4.3 Provider

- **`app/providers/base_provider.py`** – Schnittstelle.  
- **`local_ollama_provider.py`**, **`cloud_ollama_provider.py`** – konkrete Implementierungen.  
- **`ollama_client.py`** – HTTP-Details.  
- Control Center **ProvidersWorkspace** zeigt Status/Endpunkt; Modelle werden über Model-Service und Backend geladen.

---

## 5. Weiterlesen

- [`00_map_of_the_system.md`](00_map_of_the_system.md) – Navigation und Screens  
- [`SYSTEM_MAP.md`](SYSTEM_MAP.md) – generierte Baumansicht (Regeneration: `python3 tools/generate_system_map.py`)  
- [`FEATURE_REGISTRY.md`](FEATURE_REGISTRY.md) – Feature → Code/Tests/Help  
- [`04_architecture/CHAT_CONTEXT_GOVERNANCE.md`](04_architecture/CHAT_CONTEXT_GOVERNANCE.md) – Governance Kontext (falls vorhanden)
