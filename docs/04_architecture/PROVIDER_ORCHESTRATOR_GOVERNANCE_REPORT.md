# Provider-Orchestrator-Governance – Abschlussreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Freigabe

---

## 1. Analysierter Ist-Zustand

### 1.1 Beteiligte Module

| Modul | Verantwortlichkeit |
|-------|--------------------|
| ModelRegistry | ModelEntry mit provider, source_type; keine Provider-Klassen |
| ModelOrchestrator | Einziger Auflösungsort model_id → Provider; nutzt source_type |
| EscalationManager | Eskalationspfade; nutzt Registry, keine Provider |
| ModelService / ProviderService | OllamaClient via Infrastructure; keine Provider-Klassen |
| LocalOllamaProvider / CloudOllamaProvider | provider_id="local" / "ollama_cloud" |

### 1.2 Auflösungsweg

- `model_id` → ModelRegistry.get() → entry.source_type → _local oder _cloud
- Orchestrator nutzt **source_type**, nicht provider-String; beide sind konsistent
- Verdrahtung: main.py instanziiert Provider, übergibt an ModelOrchestrator

### 1.3 Bereits abgesichert (Registry-Governance)

- KNOWN_MODEL_PROVIDER_STRINGS = {"local", "ollama_cloud"}
- test_model_registry_provider_strings_valid
- test_model_provider_strings_resolvable

---

## 2. Gefundene Risiken

| Risiko | Bewertung | Maßnahme |
|--------|-----------|----------|
| Provider-String-Drift (Registry ≠ Provider.provider_id) | Mittel | Guard: provider_id ∈ KNOWN_MODEL_PROVIDER_STRINGS |
| Neuer Provider ohne Mapping | Hoch bei Erweiterung | Policy + Guard: alle KNOWN_STRINGS haben Implementierung |
| Hardcoding außerhalb definierter Orte | Mittel | Guard: provider="local"|"ollama_cloud" nur in erlaubten Dateien |
| core → providers (Orchestrator) | Dokumentiert | KNOWN_IMPORT_EXCEPTIONS; keine Änderung |
| Services → Provider-Klassen | Niedrig | Guard: Services importieren nicht LocalOllamaProvider/CloudOllamaProvider |
| Provider → gui | Verboten | Guard: Provider importieren nicht gui |
| Zyklus services ↔ providers | Keiner | Guard: Provider importieren nicht services |

---

## 3. Implementierte Guards

| Guard | Test | Beschreibung |
|-------|------|--------------|
| **A1** | test_provider_implementations_match_known_strings | provider_id aller Provider ∈ KNOWN_MODEL_PROVIDER_STRINGS |
| **A2** | test_all_known_provider_strings_have_implementation | Jeder KNOWN_STRING hat Provider-Implementierung |
| **B** | test_only_orchestrator_in_core_imports_providers | Nur orchestrator.py in core importiert providers |
| **C** | test_providers_do_not_import_gui | Provider importieren nicht gui |
| **D** | test_services_do_not_import_provider_classes | Services importieren nicht LocalOllamaProvider/CloudOllamaProvider |
| **E** | test_orchestrator_unknown_model_fallback_to_local | Unbekannte model_id → LocalOllamaProvider |
| **F** | test_no_provider_string_hardcoding_outside_allowed_files | provider="local"|"ollama_cloud" nur in ALLOWED_PROVIDER_STRING_FILES |
| **G** | test_no_cyclic_import_services_providers | Provider importieren nicht services |

**Datei:** `tests/architecture/test_provider_orchestrator_governance_guards.py`  
**Markierung:** `@pytest.mark.architecture`, `@pytest.mark.contract`

---

## 4. Minimal-invasive Korrekturen

| Änderung | Datei | Beschreibung |
|----------|-------|--------------|
| ALLOWED_PROVIDER_STRING_FILES | arch_guard_config.py | Zentrale Konfiguration für Hardcoding-Guard |
| — | — | Keine weiteren Änderungen am Produktivcode |

**Keine Feature-Umbauten, keine UI-Änderungen.**

---

## 5. Verbleibende Risiken

| Risiko | Status | Empfehlung |
|--------|--------|------------|
| settings_dialog.py importiert CloudOllamaProvider | Dokumentierte Ausnahme | Follow-up: ProviderService erweitern, GUI umstellen |
| main.py importiert Provider | Dokumentierte Ausnahme | Bootstrap; akzeptabel |
| Erweiterung um neuen Provider | Manuell | Policy definiert Prozess: KNOWN_STRINGS + Implementierung + Orchestrator + main.py |

---

## 6. Freigabe

**Provider-Orchestrator-Governance ist implementiert und abgesichert.**

- Analyse: `docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_ANALYSIS.md`
- Policy: `docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md`
- Guards: `tests/architecture/test_provider_orchestrator_governance_guards.py` (8 Tests)
- Config: `arch_guard_config.ALLOWED_PROVIDER_STRING_FILES`

**Restpunkte:** Keine blockierenden. settings_dialog.py-Follow-up ist in Service-Governance bereits dokumentiert.
