# Provider-Orchestrator-Governance – Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Kontext:** Registry-Governance hat gezeigt: keine formale Provider-Registry; Provider implizit geregelt.

---

## 1. Beteiligte Module

| Modul | Pfad | Verantwortlichkeit |
|-------|------|--------------------|
| **ModelRegistry** | `app/core/models/registry.py` | Zentrale Modellkonfiguration; ModelEntry.provider ∈ {"local", "ollama_cloud"} |
| **ModelOrchestrator** | `app/core/models/orchestrator.py` | Modellauswahl, Provider-Zuordnung, Chat-Aufrufe; einziger Ort mit Provider-Import in core |
| **EscalationManager** | `app/core/models/escalation_manager.py` | Eskalationspfade (Rolle → nächste Rolle); nutzt Registry, keine Provider |
| **ModelService** | `app/services/model_service.py` | Modellliste von Ollama, Standardmodell; nutzt Infrastructure, nicht Registry |
| **ProviderService** | `app/services/provider_service.py` | Ollama-Status, Erreichbarkeit; nutzt Infrastructure, keine Provider-Klassen |
| **LocalOllamaProvider** | `app/providers/local_ollama_provider.py` | provider_id="local", source_type="local" |
| **CloudOllamaProvider** | `app/providers/cloud_ollama_provider.py` | provider_id="ollama_cloud", source_type="cloud" |
| **BaseChatProvider** | `app/providers/base_provider.py` | Abstraktion: provider_id, source_type, chat, get_models |
| **OllamaClient** | `app/providers/ollama_client.py` | Low-Level Ollama API; von LocalOllamaProvider genutzt |

---

## 2. Verantwortlichkeiten

### 2.1 ModelRegistry

- Speichert ModelEntry mit `provider` und `source_type`
- `provider`: "local" | "ollama_cloud" (Provider-ID für Zuordnung)
- `source_type`: "local" | "cloud" (Routing-Dimension)
- Keine Kenntnis von Provider-Klassen; nur Strings

### 2.2 ModelOrchestrator

- **Auflösung:** `get_provider_for_model(model_id)` → nutzt `entry.source_type`, nicht `entry.provider`
- Lokale Modelle → LocalOllamaProvider
- Cloud-Modelle → CloudOllamaProvider (oder Local bei cloud_via_local)
- Fest verdrahtet: `LocalOllamaProvider`, `CloudOllamaProvider` im Konstruktor
- Keine dynamische Provider-Registry

### 2.3 EscalationManager

- Nutzt nur `ModelRole` und `ModelRegistry.get_best_model_for_role()`
- Keine direkte Provider-Kenntnis
- Eskalationspfade: LOCAL_ESCALATION_MAP, CLOUD_ESCALATION_MAP

### 2.4 ModelService / ProviderService

- ModelService: `get_models()` von OllamaClient (Infrastructure)
- ProviderService: `get_provider_status()` von OllamaClient
- Keine ModelRegistry-Nutzung; keine Provider-Klassen-Importe

---

## 3. Auflösungswege

| Von | Nach | Weg |
|-----|------|-----|
| model_id | Provider | ModelOrchestrator.get_provider_for_model() → entry.source_type → _local oder _cloud |
| model_id | ModelEntry | ModelRegistry.get(model_id) |
| role | model_id | ModelRegistry.get_best_model_for_role() |
| role | model_id | ModelOrchestrator.resolve_model() → get_best_model_for_role |
| provider-String | Provider-Klasse | Implizit: "local"→LocalOllamaProvider, "ollama_cloud"→CloudOllamaProvider (nur in main.py Verdrahtung) |

**Kritisch:** Die Zuordnung provider-String → Provider-Klasse erfolgt nicht zentral. main.py instanziiert beide Provider und übergibt sie an ModelOrchestrator. Der Orchestrator nutzt `source_type` für die Auswahl, nicht `provider`.

---

## 4. Implizite Verträge

| Vertrag | Beteiligte | Inhalt |
|---------|------------|--------|
| Provider-ID ↔ source_type | Registry, Provider | "local" ↔ source_type="local"; "ollama_cloud" ↔ source_type="cloud" |
| Provider-ID ↔ Implementierung | Registry, Provider-Klassen | LocalOllamaProvider.provider_id="local"; CloudOllamaProvider.provider_id="ollama_cloud" |
| Orchestrator-Provider-Zuordnung | ModelOrchestrator | source_type="local" → _local; source_type="cloud" → _cloud |
| Unbekanntes Modell | ModelOrchestrator | get(model_id)=None → Fallback auf _local (implizit via get_provider_for_model) |

---

## 5. Feste Verdrahtungen

| Ort | Verdrahtung | Risiko |
|-----|-------------|--------|
| `app/main.py` | LocalOllamaProvider(), CloudOllamaProvider() → ModelOrchestrator | Erweiterung neuer Provider erfordert main.py-Änderung |
| `app/core/models/orchestrator.py` | `from app.providers import LocalOllamaProvider, CloudOllamaProvider` | Architektur-Ausnahme (core→providers); dokumentiert |
| `app/core/models/orchestrator.py` | `self._local`, `self._cloud` fest | Kein dynamisches Provider-Mapping |
| `app/core/models/registry.py` | _load_defaults() mit provider="local"|"ollama_cloud" | Neue Provider-Strings nur hier + arch_guard_config |
| `app/providers/local_ollama_provider.py` | `return "local"` | Hardcoding |
| `app/providers/cloud_ollama_provider.py` | `return "ollama_cloud"` | Hardcoding |
| `app/gui/domains/settings/settings_dialog.py` | CloudOllamaProvider, get_ollama_api_key | Legacy; dokumentierte Ausnahme |

---

## 6. Mögliche Drift-Risiken

| Risiko | Beschreibung | Wahrscheinlichkeit |
|--------|--------------|--------------------|
| **Provider-String-Drift** | ModelRegistry.provider ≠ Provider.provider_id | Mittel – unterschiedliche Orte (registry, local_ollama, cloud_ollama) |
| **Neuer Provider vergessen** | Neuer Provider in Registry, aber kein Mapping im Orchestrator | Hoch bei Erweiterung |
| **source_type vs provider Inkonsistenz** | entry.provider="ollama_cloud" aber source_type="local" | Niedrig – beide in _load_defaults gesetzt |
| **Hardcoding außerhalb definierter Orte** | "local"/"ollama_cloud" in GUI, Services, anderen Modulen | Mittel |
| **Unbekannte model_id** | get_provider_for_model bei unbekanntem Modell → Fallback _local | Akzeptabel – definiertes Verhalten |

---

## 7. Mögliche Layerverletzungen

| Verletzung | Status |
|------------|--------|
| core → providers | ModelOrchestrator importiert providers – **dokumentierte Ausnahme** (Orchestrierung) |
| services → providers | Infrastructure importiert ollama_client (Low-Level); ProviderService/ModelService importieren keine Provider-Klassen |
| gui → providers | settings_dialog.py, main.py – **dokumentierte Ausnahmen** |
| providers → gui | Verboten in FORBIDDEN_IMPORT_RULES; Guards prüfen |

---

## 8. Mögliche zyklische Risiken

| Abhängigkeit | Zyklus? |
|--------------|---------|
| core/models → providers | Nein – providers importiert nicht core/models |
| providers → base_provider | Nein – Basisabstraktion |
| ModelOrchestrator → EscalationManager → Registry | Nein – lineare Kette |
| ModelService → Infrastructure → OllamaClient | Nein – services → providers (ollama_client) ist Infrastruktur, kein Provider-Orchestrator |

**Keine Zyklen identifiziert.**

---

## 9. Zusammenfassung

- **Orchestrierung:** ModelOrchestrator ist der einzige Ort, der Registry und Provider verbindet.
- **Auflösung:** Nutzt `source_type`, nicht `provider`; beide sind konsistent gesetzt.
- **Provider-Strings:** Nur "local" und "ollama_cloud"; in arch_guard_config.KNOWN_MODEL_PROVIDER_STRINGS.
- **Drift-Hebel:** Zentrale Provider-Konstanten, Guards für Konsistenz Registry ↔ Provider.provider_id, Verbot neuer Hardcodings außerhalb definierter Orte.
