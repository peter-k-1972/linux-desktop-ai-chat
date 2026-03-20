# Service Governance Audit

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Kontext:** UI→GUI-Migration abgeschlossen; Erweiterung der Governance auf Service-/Backend-Struktur

---

## 1. Zusammenfassung

| Kategorie | Anzahl | Status |
|-----------|--------|--------|
| Services | 11 | OK |
| Provider | 4 | OK |
| Registries/Factories | 5 | OK |
| Layer-Verletzungen | 3 | GUARD_NEEDED / FIX_NOW |
| GUI→Provider Direktzugriffe | 3 | FIX_NOW / INVESTIGATE |
| Services→GUI | 1 | INVESTIGATE |

---

## 2. Inventar

### 2.1 Services (`app/services/`)

| Modul | Typ | Verantwortung | Nutzung |
|-------|-----|---------------|---------|
| `chat_service` | Fach-Service | Sessions, Nachrichten, Chat-Kontext | GUI (chat, prompt_test_lab, metrics) |
| `model_service` | Fach-Service | Modelle, Standardmodell, Modellstatus | GUI (models_workspace, input_panel, chat) |
| `provider_service` | Fach-Service | Provider-Status, Ollama-Erreichbarkeit | GUI (providers_workspace, chat_backend) |
| `knowledge_service` | Fach-Service | Collections, Quellen, Retrieval | GUI (knowledge panels), project_service |
| `agent_service` | Fassade | Agentenliste, Agent starten (delegiert an agents/) | GUI (agent_tasks, control_center) |
| `topic_service` | Fach-Service | Topics pro Projekt | GUI (chat panels, topic_actions) |
| `project_service` | Fach-Service | Projekte, Zuordnungen, Statistiken | GUI, core/context |
| `qa_governance_service` | Fach-Service | QA-Artefakte (Test Inventory, Coverage, Incidents) | GUI (qa_governance panels) |
| `infrastructure` | Infrastruktur | OllamaClient, DB, AppSettings Singleton | Alle Services |
| `result` | Infrastruktur | ServiceResult, OperationStatus | Services |
| `provider_service` | Fach-Service | siehe oben | — |

**Klassifikation:** OK – klare Trennung, keine toten Services.

**Hinweis:** `app/services/agent_service` ist Fassade über `app/agents/agent_service` (CRUD) und `agent_task_runner`. Keine Duplikation, sondern korrekte Schichtung.

### 2.2 Provider (`app/providers/`)

| Modul | Typ | Verantwortung | Nutzung |
|-------|-----|---------------|---------|
| `base_provider` | Abstraktion | BaseChatProvider | Orchestrator, Local/Cloud |
| `local_ollama_provider` | Implementierung | Lokale Ollama-Instanz | Orchestrator |
| `cloud_ollama_provider` | Implementierung | Ollama Cloud API | Orchestrator, main, settings_dialog |
| `ollama_client` | Low-Level | Ollama HTTP API | Services (via infrastructure), main, settings_dialog |

**Klassifikation:** OK – keine toten Provider.

### 2.3 Registries / Factories / Locator

| Modul | Typ | Keys/IDs | Governance-relevant |
|-------|-----|----------|---------------------|
| `app/core/navigation/navigation_registry` | Registry | workspace_id, area_id | Ja – NavEntry.id |
| `app/core/models/registry` | Registry | model_id | Ja – ModelEntry.id |
| `app/agents/agent_registry` | Registry | agent_id, slug, name | Ja |
| `app/agents/agent_factory` | Factory | — | Nein (intern) |
| `app/core/command_registry` | Registry | command_id | Ja (GUI Governance) |

**Klassifikation:** OK – keine offensichtlichen Kollisionen, eindeutige IDs.

### 2.4 Tools / Events / Agents

| Bereich | Service-Charakter | Nutzung |
|---------|-------------------|---------|
| `app/tools` | Adapter (FileSystemTools, WebSearch) | chat_widget, agents |
| `app/agents` | Domain (agent_service, agent_registry, research_service, orchestration_service) | GUI, services |
| `app/debug` | Infrastruktur (emit_event, DebugStore) | GUI, core/llm, metrics |
| `app/rag` | Service (RAGService) | main, chat_widget, knowledge |

**Klassifikation:** OK – klare Ownership, keine versteckten Cross-Layer-Abkürzungen außer dokumentierten.

---

## 3. Layer-Beziehungen (Ist-Zustand)

### 3.1 Erwartete Richtungen

- `gui` → `services` ✓
- `services` → `core`, `providers` ✓
- `providers` → `core` (nur base, ollama_client) ✓
- `core` → (nichts außer core) ✓

### 3.2 Gefundene Verletzungen

| Quelle | Ziel | Klassifikation | Beschreibung |
|--------|------|----------------|---------------|
| ~~`app/services/infrastructure.py`~~ | ~~`app.gui.qsettings_backend`~~ | **BEHOBEN** | Dependency Inversion (2026-03-16): Backend wird von GUI-Bootstrap injiziert. |
| `app/main.py` | `app.providers` (OllamaClient, LocalOllamaProvider, CloudOllamaProvider) | **FIX_NOW** | Legacy MainWindow; GUI-Root importiert Provider direkt. Sollte über Services/Orchestrator laufen. |
| `app/gui/domains/settings/settings_dialog.py` | `app.providers.ollama_client` | **FIX_NOW** | Settings-Dialog importiert OllamaClient direkt. ProviderService existiert. |
| `app/gui/domains/settings/settings_dialog.py` | `app.providers.cloud_ollama_provider` | **FIX_NOW** | Cloud-API-Key, CloudOllamaProvider direkt. |

### 3.3 Bekannte Ausnahmen (arch_guard_config.KNOWN_IMPORT_EXCEPTIONS)

- `core/context/project_context_manager.py` → services (ProjectService für Projekt-Load)
- `core/models/orchestrator.py` → providers (Orchestrierung, arch. Entscheidung)
- `core/llm/llm_complete.py` → debug
- `metrics/metrics_collector.py` → debug

---

## 4. GUI-Zugriffe auf Services vs. Provider

### 4.1 Korrekte Service-Nutzung (GUI → services)

- `chat_service`, `model_service`, `provider_service`, `knowledge_service`, `agent_service`, `topic_service`, `project_service`, `qa_governance_service`, `infrastructure` – alle werden von GUI über `get_*_service()` genutzt.

### 4.2 Unerwünschte Direktzugriffe (GUI → providers)

| Datei | Import | Klassifikation |
|-------|--------|----------------|
| `app/main.py` | OllamaClient, LocalOllamaProvider, CloudOllamaProvider | **FIX_NOW** – Legacy, dokumentieren |
| `app/gui/domains/settings/settings_dialog.py` | OllamaClient, get_ollama_api_key, CloudOllamaProvider | **FIX_NOW** – ProviderService existiert |

### 4.3 GUI → agents (erlaubt)

- `agent_manager_panel`, `agent_list_panel`, `chat_widget` importieren `app.agents.*` (AgentProfile, agent_registry, agent_service, research_service, orchestration_service).
- **Klassifikation:** OK – agents ist Domain-Layer, GUI darf Domain nutzen wenn kein Service-Fassade existiert. `app.services.agent_service` ist Fassade; GUI nutzt teils `app.agents` direkt (z.B. AgentProfile, get_agent_registry). Das ist akzeptabel, da AgentProfile/Registry Datenmodelle sind.

---

## 5. Tote Services / Provider / Registrierungen

- **Keine toten Services** – alle Services werden von GUI oder anderen Services genutzt.
- **Keine toten Provider** – alle Provider werden genutzt.
- **project_service, qa_governance_service** – nicht in `app.services.__all__`, aber korrekt über `app.services.project_service` bzw. `app.services.qa_governance_service` importiert. **GUARD_NEEDED:** Prüfen, ob zentrale Service-Liste konsistent ist.

---

## 6. Doppelte Verantwortlichkeiten

- **agent_service:** `app/services/agent_service` (Fassade) vs. `app/agents/agent_service` (CRUD). Keine Kollision – klare Delegation.
- **Keine weiteren Duplikate** erkennbar.

---

## 7. Root-Legacy und Sonderfälle

| Modul | Beschreibung | Klassifikation |
|-------|--------------|----------------|
| `app/ollama_client.py` | Re-Export von `app.providers.ollama_client` | **OK** – TEMPORARILY_ALLOWED_ROOT_FILES |
| `app/db.py` | Legacy | TEMPORARILY_ALLOWED_ROOT_FILES |
| `app/critic.py` | Legacy | TEMPORARILY_ALLOWED_ROOT_FILES |

---

## 8. Empfehlungen

### 8.1 Sofort (FIX_NOW)

1. **GUI → Provider:** `main.py` und `settings_dialog.py` nutzen Provider direkt. Optionen:
   - **Minimal:** Als dokumentierte Ausnahme in Service-Governance-Config aufnehmen (Legacy, Follow-up geplant).
   - **Korrektur:** ProviderService/ModelService erweitern, GUI umstellen. (Größerer Eingriff – nicht in Phase 4.)

### 8.2 Guards (GUARD_NEEDED)

1. **Layer Guards:** services darf nicht gui importieren (außer dokumentierte Ausnahme infrastructure→qsettings_backend).
2. **GUI→Provider Guards:** GUI darf nicht `app.providers` importieren, außer explizit dokumentierte Ausnahmen.
3. **Service-Liste Guards:** Zentrale Service-Liste (z.B. TRACE_MAP, FEATURE_REGISTRY) mit tatsächlichen Modulen abgleichen.

### 8.3 Follow-up (INVESTIGATE)

1. ~~**infrastructure → gui:**~~ **BEHOBEN** (2026-03-16): Dependency Inversion umgesetzt.
2. **project_service, qa_governance_service** in `app.services.__all__` ergänzen für Konsistenz.

---

## 9. Klassifikation pro Fund

| Fund | Klassifikation |
|------|----------------|
| Services-Struktur, Provider-Struktur | OK |
| Registries (navigation, models, agents) | OK |
| GUI → services (korrekt) | OK |
| core → gui (KNOWN_IMPORT_EXCEPTIONS) | OK |
| GUI → providers (main, settings_dialog) | FIX_NOW |
| services → gui (infrastructure) | INVESTIGATE |
| project_service, qa_governance_service nicht in __all__ | GUARD_NEEDED |
| Zentrale Service-Liste vs. Code | GUARD_NEEDED |
