# Service Governance Guards – Abschlussreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Klassifikation:** `SERVICE_GOVERNANCE_ACTIVE_WITH_EXCEPTIONS`

---

## 1. Zusammenfassung

Das Service-Governance-System wurde eingeführt. Es umfasst:

- **Audit:** Vollständige Inventarisierung von Services, Providern, Registries
- **Policy:** Klare Layer-Regeln, Service-Identity, Provider-Usage
- **Guards:** 8 pytest-basierte Tests in `test_service_governance_guards.py`
- **Erweiterung:** `arch_guard_config.py` um Service-Governance-Regeln ergänzt
- **Korrekturen:** `app.services.__init__` um ProjectService, QAGovernanceService erweitert

---

## 2. Analysierte Bereiche

| Bereich | Pfad | Ergebnis |
|---------|------|----------|
| Services | `app/services/` | 11 Module, klare Trennung |
| Provider | `app/providers/` | 4 Module, keine toten Provider |
| Core | `app/core/` | Keine unerwünschten Imports (außer dokumentiert) |
| GUI | `app/gui/` | Nutzt primär Services |
| Tools | `app/tools/` | Keine Layer-Verletzungen |
| Agents | `app/agents/` | Klare Ownership |
| Registries | navigation_registry, models/registry, agent_registry | Eindeutige IDs |

---

## 3. Eingeführte Guard-Typen

### A. Layer Guards

| Guard | Datei | Regel |
|-------|-------|-------|
| `test_services_do_not_import_gui` | test_service_governance_guards.py | services → gui verboten (Ausnahme: infrastructure.py) |
| `test_gui_does_not_import_providers_directly` | test_service_governance_guards.py | gui/main → providers verboten (Ausnahmen: main.py, settings_dialog.py) |

Zusätzlich in `test_app_package_guards.py` (FORBIDDEN_IMPORT_RULES):

- `(services, gui)` – services darf gui nicht importieren
- `(gui, providers)` – gui darf providers nicht importieren
- `(_root, providers)` – app-Root darf providers nicht importieren

### B. Service / Provider Identity Guards

| Guard | Regel |
|-------|-------|
| `test_canonical_services_exist` | Alle CANONICAL_SERVICE_MODULES existieren unter app/services/ |
| `test_navigation_registry_entries_unique` | NavEntry-IDs eindeutig |

### C. Usage Guards (Smoke)

| Guard | Regel |
|-------|-------|
| `test_central_services_importable` | chat, model, provider, knowledge, agent_service importierbar |
| `test_providers_importable` | BaseChatProvider, LocalOllamaProvider, CloudOllamaProvider, OllamaClient importierbar |
| `test_gui_service_kernpaths_smoke` | GUI kann alle zentralen Service-Getter importieren |

### D. Registry / Trace Map Guards

| Guard | Regel |
|-------|-------|
| `test_trace_map_services_match_canonical` | TRACE_MAP.md Sektion 2 enthält kritische Services |

---

## 4. Gefundene Verstöße

| Verstoß | Quelle | Ziel | Status |
|---------|--------|------|--------|
| ~~services → gui~~ | ~~infrastructure.py~~ | ~~app.gui.qsettings_backend~~ | **BEHOBEN** (2026-03-16) Dependency Inversion |
| gui/main → providers | main.py | OllamaClient, LocalOllamaProvider, CloudOllamaProvider | **Ausnahme dokumentiert** |
| gui → providers | settings_dialog.py | OllamaClient, get_ollama_api_key, CloudOllamaProvider | **Ausnahme dokumentiert** |
| _root → providers | ollama_client.py | app.providers.ollama_client | **Ausnahme dokumentiert** (Re-Export) |

---

## 5. Direkt korrigierte Verstöße

| Korrektur | Beschreibung |
|-----------|--------------|
| `app.services.__init__` | ProjectService, QAGovernanceService in __all__ und Import ergänzt – Konsistenz mit TRACE_MAP/FEATURE_REGISTRY |
| `arch_guard_config.py` | KNOWN_IMPORT_EXCEPTIONS um ollama_client.py erweitert (Root-Re-Export) |

---

## 6. Dokumentierte Ausnahmen

| Ausnahme | Config-Eintrag | Follow-up |
|----------|----------------|-----------|
| ~~services/infrastructure.py → gui~~ | **Entfernt** | **BEHOBEN** – Dependency Inversion umgesetzt |
| main.py → providers | KNOWN_IMPORT_EXCEPTIONS, KNOWN_GUI_PROVIDER_EXCEPTIONS | Legacy MainWindow; Umstellung auf Services |
| settings_dialog.py → providers | KNOWN_IMPORT_EXCEPTIONS, KNOWN_GUI_PROVIDER_EXCEPTIONS | ProviderService/ModelService erweitern |
| ollama_client.py → providers | KNOWN_IMPORT_EXCEPTIONS | Root-Re-Export; TEMPORARILY_ALLOWED_ROOT_FILES |

---

## 7. Offene Follow-ups

1. ~~**infrastructure → gui:**~~ **BEHOBEN** – Dependency Inversion umgesetzt (2026-03-16)
2. **main.py, settings_dialog.py:** GUI von Provider-Direktimporten auf ProviderService/ModelService umstellen
3. **ollama_client.py:** Root-Modul in app/providers/ oder app/services/ integrieren (APP_MOVE_MATRIX)

---

## 8. Validierungsergebnis

```
tests/architecture/test_gui_does_not_import_ui.py    1 passed
tests/architecture/test_app_package_guards.py      12 passed
tests/architecture/test_gui_domain_dependency_guards.py  2 passed
tests/architecture/test_gui_governance_guards.py    8 passed
tests/architecture/test_feature_governance_guards.py  6 passed
tests/architecture/test_service_governance_guards.py  8 passed
------------------------------------------------------------
37 passed
```

- Keine Funktionsänderung (außer erweiterter app.services.__all__)
- Keine unerwarteten Seiteneffekte
- Smoke-Tests für zentrale Services/Provider bestanden

---

## 9. Konsole-Zusammenfassung

```
=== Service Governance – Abschluss ===

Neue Guard-Tests:     8 (test_service_governance_guards.py)
Erkannte Verstöße:    4 (services→gui, gui→providers, root→providers)
Korrigierte Verstöße: 1 (app.services.__all__ erweitert)
Verbleibende Ausnahmen: 4 (dokumentiert in arch_guard_config.KNOWN_IMPORT_EXCEPTIONS)
Follow-ups:           3 (infrastructure DI, main/settings_dialog Umstellung, ollama_client Move)

Klassifikation: SERVICE_GOVERNANCE_ACTIVE_WITH_EXCEPTIONS
```
