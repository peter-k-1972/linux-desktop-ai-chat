# Full System Restpoint Remediation – Abschlussreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Rolle:** Principal Software Architect, Governance Engineer, Refactoring Reviewer

---

## Executive Summary

Die im Full System Checkup identifizierten Restpunkte wurden gezielt, minimal-invasiv und governance-konform bereinigt. **5 von 8 Restpunkten** wurden behoben oder dokumentiert; **3 Restpunkte** bleiben bewusst als Übergangslösungen.

---

## 1. Bearbeitete Restpunkte

### CRITICAL – behoben

| Restpunkt | Maßnahme | Ergebnis |
|-----------|----------|----------|
| **docs_path** | DOCS_ARCH auf `docs/04_architecture` umgestellt | arch_guard_config, architecture_drift_radar nutzen kanonischen Pfad; governance_files = true |

**Architekturentscheidung:** [DOCS_ARCHITECTURE_PATH_DECISION.md](./DOCS_ARCHITECTURE_PATH_DECISION.md)

---

### HIGH – dokumentiert

| Restpunkt | Maßnahme | Ergebnis |
|-----------|----------|----------|
| **app_main_legacy** | Governance-Dokumentation erstellt | LEGACY_MAIN_GOVERNANCE.md; bewusste Übergangslösung bis Archivierung |

**Architekturentscheidung:** [LEGACY_MAIN_GOVERNANCE.md](./LEGACY_MAIN_GOVERNANCE.md)

---

### MEDIUM – behoben / dokumentiert

| Restpunkt | Maßnahme | Ergebnis |
|-----------|----------|----------|
| **llm_duplication** | Struktur dokumentiert | LLM_MODULE_STRUCTURE.md; app/llm ist Re-Export, keine Duplikation |
| **tools_registry** | Bewusste Entscheidung dokumentiert | TOOLS_GOVERNANCE_DECISION.md; keine formale Registry nötig |
| **settings_dialog_providers** | Entkopplung implementiert | settings_dialog nutzt ModelService/ProviderService; KNOWN_GUI_PROVIDER_EXCEPTIONS bereinigt |

---

### LOW – dokumentiert / angepasst

| Restpunkt | Maßnahme | Ergebnis |
|-----------|----------|----------|
| **temp_root_files** | Unverändert | db.py, critic.py in TEMPORARILY_ALLOWED; Phase D (APP_MOVE_MATRIX) |
| **ui_parallel_package** | Kommentar aktualisiert | FORBIDDEN_PARALLEL_PACKAGES: „ui migriert; Neuaufbau verboten“ |
| **gui_import_ui_test** | Test behalten, Kommentar angepasst | Sentinel gegen Drift; app.ui entfernt, Guard bleibt |

---

## 2. Implementierte Korrekturen

### Code-Änderungen

| Datei | Änderung |
|-------|----------|
| `tests/architecture/arch_guard_config.py` | DOCS_ARCH = docs/04_architecture; KNOWN_GUI_PROVIDER_EXCEPTIONS ohne settings_dialog; FORBIDDEN_PARALLEL_PACKAGES Kommentar |
| `scripts/architecture/architecture_drift_radar.py` | DOCS_ARCH = docs/04_architecture |
| `app/services/provider_service.py` | get_ollama_api_key_from_env(), validate_cloud_api_key() |
| `app/gui/domains/settings/settings_dialog.py` | Keine Provider-Imports; nutzt ModelService, ProviderService |
| `app/main.py` | SettingsDialog(settings, orchestrator) – client entfernt |
| `tests/architecture/test_gui_does_not_import_ui.py` | Kommentar aktualisiert |

### Neue Dokumentation

| Datei | Inhalt |
|-------|--------|
| `docs/04_architecture/DOCS_ARCHITECTURE_PATH_DECISION.md` | Kanonischer Pfad docs/04_architecture |
| `docs/04_architecture/LEGACY_MAIN_GOVERNANCE.md` | app.main Legacy-Status |
| `docs/04_architecture/LLM_MODULE_STRUCTURE.md` | app/llm vs core/llm |
| `docs/04_architecture/TOOLS_GOVERNANCE_DECISION.md` | Bewusst keine Tools-Registry |
| `docs/architecture/README.md` | Redirect auf docs/04_architecture |

---

## 3. Aktualisierte Guards

- **Service Governance:** settings_dialog aus KNOWN_GUI_PROVIDER_EXCEPTIONS entfernt – erfüllt jetzt GUI→Services-Regel
- **Architecture Drift Radar:** governance_files werden korrekt gefunden (alle true)
- **test_gui_does_not_import_ui:** Bleibt als Drift-Sentinel aktiv

---

## 4. Verbleibende Restpunkte

| Restpunkt | Status | Begründung |
|-----------|--------|------------|
| **app_main_legacy** | Bewusst | Nur für archive/run_legacy_gui; bei Archivierung entfernen |
| **temp_root_files** | Phase D | db.py, critic.py, ollama_client.py – APP_MOVE_MATRIX |
| **gui_import_ui_test** | Behalten | Sentinel; app.ui existiert nicht, Guard verhindert Drift |

---

## 5. Freigabeempfehlung

**Freigabe für laufenden Betrieb**

- Docs-Pfad konsolidiert
- settings_dialog von Providers entkoppelt
- Alle Governance-Blöcke funktionsfähig
- Verbleibende Restpunkte dokumentiert und priorisiert

---

## 6. Referenzen

- [Full System Checkup Report](./FULL_SYSTEM_CHECKUP_REPORT.md)
- [DOCS_ARCHITECTURE_PATH_DECISION.md](./DOCS_ARCHITECTURE_PATH_DECISION.md)
- [LEGACY_MAIN_GOVERNANCE.md](./LEGACY_MAIN_GOVERNANCE.md)
- [LLM_MODULE_STRUCTURE.md](./LLM_MODULE_STRUCTURE.md)
- [TOOLS_GOVERNANCE_DECISION.md](./TOOLS_GOVERNANCE_DECISION.md)
