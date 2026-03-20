# Provider-Orchestrator-Governance – Policy

**Projekt:** Linux Desktop Chat  
**Referenz:** `docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_ANALYSIS.md`  
**Tests:** `tests/architecture/test_provider_orchestrator_governance_guards.py`

---

## 1. Ziel

Provider- und Modell-Orchestrierung governance-seitig absichern: Konsistenz zwischen ModelRegistry und Provider-Auflösung, klare Trennung der Schichten, Verhinderung stiller Drift.

---

## 2. Erlaubte Provider-Auflösungsorte

| Ort | Modul | Funktion | Beschreibung |
|-----|-------|----------|--------------|
| **Einziger Auflösungsort** | `app/core/models/orchestrator.py` | `get_provider_for_model(model_id)` | model_id → BaseChatProvider; nutzt ModelRegistry.get() und source_type |
| **Verdrahtung** | `app/main.py` | main() | Instanziert LocalOllamaProvider, CloudOllamaProvider, übergibt an ModelOrchestrator |

**Regel:** Kein anderer Ort darf model_id → Provider auflösen. Services (ModelService, ProviderService) nutzen Infrastructure/OllamaClient, nicht Provider-Klassen.

---

## 3. Wer Provider kennen darf

| Schicht | Darf kennen | Darf NICHT kennen |
|---------|-------------|-------------------|
| **core/models/orchestrator** | ModelRegistry, LocalOllamaProvider, CloudOllamaProvider, BaseChatProvider | — |
| **main.py** | LocalOllamaProvider, CloudOllamaProvider, ModelOrchestrator | — |
| **app/providers/** | BaseChatProvider, OllamaClient, eigene Implementierung | app.gui |
| **app/services/** | Infrastructure (OllamaClient) | LocalOllamaProvider, CloudOllamaProvider (als Typen) |
| **app/gui/** | ModelOrchestrator (injiziert), ProviderService, ModelService | LocalOllamaProvider, CloudOllamaProvider (außer dokumentierte Ausnahmen) |

---

## 4. Wer Provider NICHT kennen darf

| Modul/Pattern | Verbot |
|---------------|--------|
| `app/services/*.py` | Import von `LocalOllamaProvider`, `CloudOllamaProvider` (außer über Infrastructure: OllamaClient) |
| `app/core/models/registry.py` | Import von providers |
| `app/core/models/escalation_manager.py` | Import von providers |
| `app/core/models/roles.py`, `router.py` | Import von providers |
| `app/gui/**` (außer Ausnahmen) | Import von `app.providers` (LocalOllamaProvider, CloudOllamaProvider, ollama_client) |
| `app/providers/**` | Import von `app.gui` |

**Dokumentierte Ausnahmen:** main.py, gui/domains/settings/settings_dialog.py (Legacy).

---

## 5. Erlaubte Provider-Strings / Provider-IDs

| String | Bedeutung | Implementierung |
|--------|-----------|-----------------|
| `local` | Lokale Ollama-Instanz | LocalOllamaProvider |
| `ollama_cloud` | Ollama Cloud API | CloudOllamaProvider |

**Regel:** ModelEntry.provider ∈ {"local", "ollama_cloud"}.  
**Quelle:** `arch_guard_config.KNOWN_MODEL_PROVIDER_STRINGS`

Neue Provider-Strings nur nach:
1. Erweiterung von KNOWN_MODEL_PROVIDER_STRINGS
2. Neuer Provider-Implementierung mit provider_id
3. Anpassung ModelOrchestrator + main.py
4. Architektur-Review

---

## 6. Regeln für ModelRegistry.provider

- Jeder ModelEntry.provider muss in KNOWN_MODEL_PROVIDER_STRINGS liegen.
- provider und source_type müssen konsistent sein: "local" ↔ source_type="local", "ollama_cloud" ↔ source_type="cloud".
- Keine neuen Provider-Strings ohne vorherige Erweiterung der Governance-Konfiguration.

---

## 7. Regeln für Fallbacks

| Situation | Erlaubtes Verhalten |
|-----------|---------------------|
| Unbekannte model_id | get_provider_for_model → LocalOllamaProvider (Fallback) |
| entry = None | LocalOllamaProvider |
| source_type="cloud", cloud_via_local=True | LocalOllamaProvider (ollama signin) |
| source_type="cloud", cloud_via_local=False | CloudOllamaProvider |

---

## 8. Regeln für unbekannte Modelle / unbekannte Provider

| Fall | Verhalten |
|------|-----------|
| model_id nicht in Registry | get_provider_for_model → _local (sicherer Fallback) |
| entry.provider nicht in KNOWN_MODEL_PROVIDER_STRINGS | Guard schlägt fehl (Registry-Governance) |
| Provider-Implementierung fehlt für provider-String | Architektur-Risiko; Guard prüft Konsistenz |

---

## 9. Regeln für lokale vs. Cloud-Provider

| Typ | provider | source_type | Provider-Klasse |
|-----|---------|-------------|-----------------|
| Lokal | "local" | "local" | LocalOllamaProvider |
| Cloud | "ollama_cloud" | "cloud" | CloudOllamaProvider |

**Regel:** source_type darf nur "local" oder "cloud" sein.

---

## 10. Regeln gegen harte Verdrahtungsdrift

| Regel | Umsetzung |
|-------|-----------|
| Provider-Strings nur an definierten Orten | Registry._load_defaults; arch_guard_config.KNOWN_MODEL_PROVIDER_STRINGS |
| Kein Hardcoding außerhalb | Guard: Suche nach "local", "ollama_cloud" in String-Literalen außerhalb erlaubter Dateien |
| Provider.provider_id = Registry.provider | Guard: Alle KNOWN_MODEL_PROVIDER_STRINGS sind durch Provider-Implementierung abgedeckt |
| Einziger Orchestrator-Provider-Import | core/models/orchestrator.py (dokumentierte Ausnahme) |

---

## 11. Ausnahmen

| Ausnahme | Begründung |
|----------|------------|
| core/models/orchestrator.py → providers | Orchestrierung ist Kernlogik; Provider sind Infrastruktur. Architektur-Entscheidung. |
| main.py → providers | Bootstrap; instanziiert Provider. |
| gui/domains/settings/settings_dialog.py → providers | Legacy-Settings-Dialog; Follow-up: ProviderService erweitern. |

Neue Ausnahmen nur nach Architektur-Review.
