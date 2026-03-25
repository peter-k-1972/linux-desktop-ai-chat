# Welle 1: Extraktionsvorbereitung (Monorepo, ohne physischen Cut)

**Projekt:** Linux Desktop Chat  
**Status:** Operative Checkliste und Ist-Analyse — **keine** Verschiebung von Dateien, **keine** neuen GitHub-Repos  
**Bezug:** [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md), [`PACKAGE_MAP.md`](PACKAGE_MAP.md), [`PACKAGE_FEATURES_CUT_READY.md`](PACKAGE_FEATURES_CUT_READY.md) (verbindliche API + DoR), [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md) (physischer Cut), `app/features/__init__.py` (`__all__`), `app/features/entry_point_contract.py`

---

## 1. `app/features` → zukünftiges `linux-desktop-chat-features` (Arbeitsname)

### 1.1 Ist-Zustand (Extraktionsrelevanz)

- **Keine** Imports aus `app.features` nach `app.<anderes Segment>` in den Modulen unter `app/features/` (nur stdlib + `app.features.*`).  
- Segment-Guard: `features` → `gui` / `services` / `ui_application` / `ui_runtime` ist verboten (`segment_dependency_rules.py`).  
- **Externe** Plugin-Autoren sollen ohnehin nur den Vertrag in `entry_point_contract.py` und z. B. `FeatureDescriptor` / `FeatureRegistrar` nutzen (`examples/plugins/ldc_plugin_example`).

### 1.2 Öffentliche API — Kandidaten

| Ebene | Symbole / Module | Bemerkung |
|-------|------------------|-----------|
| **Paket-Root (unterstützt)** | Alles in `app.features.__all__` | Soll nach Extraktion `ldc_features` (oder gewählter Importpfad) **`__all__`** bleiben. |
| **Entry-Point-Vertrag** | `ENTRY_POINT_GROUP`, `ENTRY_POINT_PRIMARY_CALLABLE`, `ENTRY_POINT_LEGACY_REGISTRARS_ATTR` | Stabil für **alle** externen Wheels; Gruppenname `linux_desktop_chat.features` beibehalten. |
| **Plugin-Autoren (minimal)** | `FeatureDescriptor`, `FeatureRegistrar` | Wie Beispiel-Plugin. |
| **Host / GUI-Orchestrierung (erweitert)** | `get_feature_registry`, `set_feature_registry`, `build_feature_registry_for_edition`, `resolve_active_edition_name`, `apply_feature_screen_registrars`, `FeatureRegistry`, Edition-/Dependency-Registry-Getter/Setter | Bereits über `app.features` root exportiert. |
| **Navigation/Commands-Anbindung** | `collect_active_navigation_entry_ids`, `collect_active_gui_command_ids` in `nav_binding` | **Nicht** in `app.features.__all__` — Host importiert Submodule; für semver: als **stabile Host-API** dokumentieren oder in Root-API aufnehmen. |
| **Built-in-Registrare (GUI)** | `app.gui.registration.feature_builtins` nutzt `FeatureDescriptor`, `FeatureRegistry`, `is_feature_technically_available` | `dependency_availability` ist Host-relevante Tiefe — siehe „Interna“. |
| **CI / Release** | `release_matrix.build_release_matrix`, `plugin_validation_profiles_to_json_dict`, `build_internal_plugin_github_actions_matrix_payload`, `PLUGIN_VALIDATION_SMOKE_PROFILES`; `dependency_packaging.validate_pep621_pyproject_alignment` | Werden von `tools/ci/release_matrix_ci.py` und Architekturtests genutzt — gehören zur **Produkt-Buildkette**, nicht zur Plugin-Minimal-API. |

### 1.3 Intern / nicht für externe Plugin-Autoren

| Bereich | Beispiele | Risiko bei „Leak“ als öffentlich |
|---------|-----------|-----------------------------------|
| Discovery-Implementierung | `feature_discovery._iter_entry_point_registrars`, `_iter_env_module_registrars` | Tests importieren privat — bricht bei Umbenennung. |
| Verfügbarkeits-Probes | `dependency_availability._GROUP_PROBES` (von `dependency_packaging` referenziert) | Internes Probing-Modell. |
| Validierung / Planung | `feature_validation.plan_registration_order`, interne Manifest-Helfer | Für Host/CI ok, nicht semver-„public“ für Plugins. |
| Katalog-Konstanten | `feature_name_catalog.ALL_BUILTIN_FEATURE_NAMES` | Host + Tests; Änderung = Produktmanifest, nicht generische Library. |

### 1.4 Zulässige direkte Abhängigkeiten (Zielpaket)

Heute: **keine** Runtime-Abhängigkeiten auf andere `app.*`-Pakete. Ziel-`pyproject` für das extrahierte Paket:

- `requires-python`: wie Host (≥ 3.10).  
- `dependencies`: leer oder nur zukünftig explizit benötigte kleine Libraries (aktuell **stdlib ausreichend** für den Kern).  
- **Nicht** deklarieren: PySide6, `app.gui`, `app.services`.

### 1.5 `pyproject.toml`-Skizze (Zielpaket, nach Cut)

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "linux-desktop-chat-features"
version = "0.1.0"  # SemVer separat vom Host; Release-Prozess definieren
description = "Feature platform: descriptors, registries, edition resolution, entry-point contract for linux_desktop_chat.features"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]   # oder flache Struktur — nach physischem Layout
include = ["ldc_features*"]   # Empfehlung: neuer Top-Level-Name statt app.features im Wheel

# Optional: Metadaten nur für Host/CI, keine Plugin-Einträge im Library-Wheel
# [project.entry-points."linux_desktop_chat.features"]
```

**Hinweis:** Solange das Monorepo `app.features` heißt, bleibt der **Importpfad** `app.features`. Beim echten Cut: entweder **Namespace-Paket** `linux_desktop_chat/features` unter der Distribution `linux-desktop-chat-features` oder Umbenennung zu `ldc_features` mit **Shim** im Host (`app.features` re-exportiert) für eine Übergangsphase.

### 1.6 Minimaler Test-/CI-Scope (für extrahiertes Paket)

| Scope | Kommandos / Pfade |
|-------|-------------------|
| **Unit-Feature-Kern** | `pytest tests/unit/features/ -q` |
| **Entry-Point-/Vertrags-Guards** | `pytest tests/architecture/test_entry_point_contract_guard.py tests/architecture/test_package_map_contract.py -q` |
| **Edition-/Manifest-Guards** | `pytest tests/architecture/test_edition_manifest_guards.py -q` |
| **Release-Matrix-Validierung** | `python tools/ci/release_matrix_ci.py` (oder wie im Workflow dokumentiert) |
| **Plugin-Beispiel** | Build + Smoke aus `.github/workflows/plugin-validation-smoke.yml` |

Alles unter `tests/unit/gui/test_navigation_feature_binding.py` und ähnliche **bleiben Host-Tests**, die **`ldc-features` als Dependency** installieren (editable) oder weiter im Monorepo gegen `app.features` laufen bis zum Cut.

### 1.7 Offene Blocker (features)

| Blocker | Maßnahme |
|---------|----------|
| Importpfad `app.features` vs. neuer Paketname | Shim-Layer oder Namespace-Entscheidung vor dem ersten Release. |
| `nav_binding` außerhalb `__all__` | Entweder in öffentliche Host-API aufnehmen oder explizit als „stabil für Host, nicht für Plugins“ dokumentieren. |
| Tests greifen auf `_iter_entry_point_registrars` zu | Öffentliche Test-Hilfe exportieren oder Tests ins Paket-Repo verschieben und nur öffentliche Discovery testen. |
| `release_matrix_ci` importiert aus `app.features` | Nach Cut: Host `pyproject` → `linux-desktop-chat-features>=x` als **dev**/CI-Abhängigkeit oder Monorepo-Workspace-Tool (uv/poetry) festlegen. |
| Zwei Quellen für Entry-Point-Gruppe | `PLUGIN_ENTRY_POINT_GROUP` in `landmarks.py` muss mit `entry_point_contract.ENTRY_POINT_GROUP` bleiben (bereits per Test abgesichert). |

---

## 2. `app/ui_contracts` → zukünftiges `linux-desktop-chat-ui-contracts` (optional Welle 1)

**Vertiefung nach API-Härtung (Welle 2):** [`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md) — Consumer-Matrix, Split-Reifegrad, harte Blocker, empfohlene Extraktionsreihenfolge. **Cut-Ready / DoR:** [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md). Der folgende Abschnitt bleibt als **kurze historische Skizze** erhalten.

### 2.1 Ist-Zustand

- Alle Imports unter `app/ui_contracts/` sind **nur** `app.ui_contracts.*` (kein `gui`, `services`, `features`).  
- Viele **Host-Verbraucher**: `app.gui.domains.*`, `app.ui_application.*`, `tests/contracts`, Smoke-Tests — typischerweise **Workspace-DTOs und Commands**.

### 2.2 Öffentliche API — Kandidaten

| Ebene | Inhalt |
|-------|--------|
| **Paket-Root** | `app.ui_contracts.__all__` — Chat-DTOs, Enums, `ChatUiEvent`. |
| **Workspace-Verträge** | Module unter `app.ui_contracts.workspaces.*` — faktisch **öffentlich**, weil GUI und Presenter direkt importieren; für Extraktion: semver auf **diesen** Modulen führen oder in Unterpakete mit eigener Versionierung gliedern. |

### 2.3 Intern

- Keine versteckten `_`-Heavy Internals in gleichem Maß wie bei features; die „API-Fläche“ ist **breit** durch die vielen Workspace-Dateien.  
- Risiko: **Jede** Änderung an DTO-Feldern bricht Mapper in `ui_application` und Sinks in `gui`.

### 2.4 Zulässige Abhängigkeiten

- Stdlib + `typing` / `dataclasses` / `enum` — **keine** PySide6, keine `app.services` (bereits Policy im Paket-Docstring).

### 2.5 `pyproject.toml`-Skizze

**Verbindlich überholt:** Importpfad **`app.ui_contracts`**, Wheel **`linux-desktop-chat-ui-contracts`** — vollständige Skizze und Execution Plan in [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) §3.

```toml
[project]
name = "linux-desktop-chat-ui-contracts"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
include = ["app*"]   # nur app/ui_contracts/ im Tree — siehe PHYSICAL_SPLIT §3.1
```

### 2.6 Test-/CI-Scope

| Scope | Pfade |
|-------|--------|
| Contract-Tests | `pytest tests/contracts/ -q` (subset markieren, falls zu groß) |
| UI-Application-Tests | `pytest tests/unit/ui_application/ -q` (hängen an Contracts) |
| Rauch-Imports | `tests/smoke/test_*_import.py`, die `ui_contracts` anfassen |

### 2.7 Blocker

| Blocker | Maßnahme |
|---------|----------|
| Breite öffentliche Fläche | API-Guide: welche Module „stabil 1.x“, welche noch experimentell. |
| Host importiert tiefe Pfade | Akzeptabel kurzfristig; mittelfristig optional Re-Exports in `ui_contracts.workspaces.__init__` für häufige Bundles (nur wenn Lesbarkeit leidet). |

---

## 3. Produktions-Code: Consumer von `app.features` (außerhalb `app/features/`)

| Datei | Importierte Symbole (Ist) |
|-------|---------------------------|
| `run_gui_shell.py` | `build_feature_registry_for_edition`, `resolve_active_edition_name`, `set_feature_registry` via **`from app.features import …`** |
| `app/gui/bootstrap.py` | `apply_feature_screen_registrars`, `get_feature_registry` via **`from app.features import …`** |
| `app/gui/commands/bootstrap.py` | `get_feature_registry`, `collect_active_gui_command_ids` |
| `app/gui/commands/palette_loader.py` | lazy: `get_feature_registry`, `collect_active_gui_command_ids` |
| `app/gui/navigation/sidebar_config.py` | lazy: `FeatureRegistry`, `get_feature_registry`, `collect_active_navigation_entry_ids` |
| `app/gui/navigation/nav_context.py` | `get_feature_registry`, `collect_active_navigation_entry_ids` |
| `app/gui/registration/feature_builtins.py` | `FeatureDescriptor`, `FeatureRegistry`, `is_feature_technically_available` |
| `app/gui/domains/runtime_debug/runtime_debug_nav.py` | lazy: `get_feature_registry`, `collect_active_gui_command_ids` |
| `tools/ci/release_matrix_ci.py` | `validate_pep621_pyproject_alignment`, `build_release_matrix`, `plugin_validation_profiles_to_json_dict`, `build_internal_plugin_github_actions_matrix_payload` |

**Plugins (extern):** `examples/plugins/ldc_plugin_example/...` → `FeatureDescriptor` (Referenz-Verbraucher).

Keiner dieser Pfade importiert `app.gui` **aus** `app/features` — Extraktion verletzt keine Schichtregel in die andere Richtung.

---

## 4. Produktions-Code: Consumer von `app.ui_contracts` (Auszug nach Volumen)

**Hauptkategorien:**

- **`app/gui/domains/...`**: Settings, Prompt Studio, Agent Tasks, Deployment, Chat — viele `from app.ui_contracts.workspaces.<mod> import ...`.  
- **`app/ui_application/...`**: Presenter, Adapter, Ports — gleiche Workspace-Module.  
- **`tests/contracts/`**, **`tests/unit/gui/`**, **`tests/unit/ui_application/`**, **`tests/smoke/`** — Vertrags- und Import-Smokes.

**Bei Extraktion brechen:** alle genannten Importe, sofern der Paketname/Pfad wechselt **ohne** Shim. Lösung: editable install + gleicher Namespace oder einheitlicher Migrations-PR.

---

## 5. Problematische Direktimporte (für semver / Cut)

### 5.1 `features`

| Von wo | Was | Problem |
|--------|-----|---------|
| `tests/unit/features/test_entry_point_plugin_integration.py` | `_iter_entry_point_registrars` | Privat-API |
| `tests/unit/features/test_feature_discovery.py` | `_iter_entry_point_registrars`, `_iter_env_module_registrars` | Privat-API |
| `app/features/dependency_packaging.py` | `_GROUP_PROBES` aus `dependency_availability` | Internes Detail im gleichen Paket — ok bis Cut; im extrahierten Repo weiterhin intern |

### 5.2 `ui_contracts`

- Keine durchgängigen `_`-Privatimporte von außen identisch wie bei features; Hauptthema ist **Volumen** der Workspace-Imports, nicht Einzelverstöße.

---

## 6. Checkliste: vor Extraktion

- [ ] Öffentliche API für **Plugin-Autoren** dokumentiert (`FeatureDescriptor`, `FeatureRegistrar`, Entry-Point-Gruppe).  
- [ ] Öffentliche API für **Host** dokumentiert (`app.features.__all__` + `nav_binding` + CI-Module).  
- [ ] Entscheidung: neuer Import-Top-Level (`ldc_features`) vs. Namespace `linux_desktop_chat.features` + Shim im Host.  
- [ ] SemVer- und Release-Prozess (unabhängig vom Host oder gekoppelt).  
- [ ] `tools/ci/release_matrix_ci.py` und Workflows: Plan, wie `linux-desktop-chat-features` eingebunden wird (Version-Pin / editable).  
- [ ] Tests mit `_iter_*`: umbauen oder dokumentiert als Paket-intern lassen.  
- [ ] Für `ui_contracts` (optional): „Stabilitäts“-Klassifizierung der Workspace-Module.

---

## 7. Checkliste: beim Cut (Repo-/Packaging-Operation, später)

- [ ] Neues `pyproject.toml` im Features-Repo gemäß Skizze; Paket bauen (`python -m build`).  
- [ ] Host-`pyproject`: Abhängigkeit `linux-desktop-chat-features>=…` (oder Monorepo-Tool).  
- [ ] Importpfad-Migration oder Shim committed.  
- [ ] Entry-Point-Gruppe `linux_desktop_chat.features` unverändert in der Doku; Wheels von Plugins weiter kompatibel.  
- [ ] CI: Feature-Tests und `release_matrix_ci` auf neues Paket umstellen.  
- [ ] Optional gleiches für `ui_contracts` mit Contract-Test-Pipeline.

---

## 8. Checkliste: nach dem Cut verifizieren

- [ ] `pytest tests/unit/features/` grün (gegen installiertes Paket oder Shim).  
- [ ] `pytest tests/architecture/test_entry_point_contract_guard.py tests/architecture/test_package_map_contract.py` grün.  
- [ ] `python tools/ci/release_matrix_ci.py` grün.  
- [ ] Plugin-Example-Build + Validation-Workflow grün.  
- [ ] Kein `from app.features` in Host-Code ohne dass `app.features` ein re-exportierter Shim ist (oder Host komplett auf `ldc_features` umgestellt).  
- [ ] Für `ui_contracts`: `pytest tests/contracts/` (oder Kern-Subset) grün.

---

## 9. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: features + ui_contracts, Consumer-Matrix, Blocker, Checklisten |
| 2026-03-25 | Host: `run_gui_shell.py`, `app/gui/bootstrap.py` nutzen öffentliche `app.features`-Root-Importe |
| 2026-03-25 | Verweis auf `PACKAGE_FEATURES_CUT_READY.md`; Host-GUI auf Root-API vereinheitlicht; Oberflächen-Guard |
| 2026-03-25 | Verweis auf `PACKAGE_FEATURES_PHYSICAL_SPLIT.md` (physischer Cut, Empfehlung B) |
| 2026-03-25 | `ui_contracts`: Verweis auf `PACKAGE_UI_CONTRACTS_WAVE2_PREP.md` (Split-Prep vertieft) |
| 2026-03-25 | `ui_contracts`: Verweis auf `PACKAGE_UI_CONTRACTS_CUT_READY.md` (DoR) |
| 2026-03-25 | §2.5 `pyproject`-Skizze an [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) (Variante B) ausgerichtet |
