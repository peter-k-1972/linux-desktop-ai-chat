# `app.features` — Definition of Ready for Cut

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche API- und Reife-Definition für einen **physischen** Split (noch nicht durchgeführt)  
**Bezug:** [`PACKAGE_WAVE1_PREP.md`](PACKAGE_WAVE1_PREP.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md), [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md) (physischer Cut), [`PACKAGE_FEATURES_COMMIT2_LOCAL.md`](PACKAGE_FEATURES_COMMIT2_LOCAL.md) (Commit 2 im Monorepo), [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md) (Commit 3 CI), [`PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md`](PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md) (Welle 1 Abschluss Guards/Tests), `tests/architecture/test_features_public_surface_guard.py`

---

## 1. Verbindliche öffentliche API

### 1.1 Plugin-Minimal-API

Externe Wheels nutzen die Entry-Point-Gruppe `linux_desktop_chat.features` und implementieren den Vertrag in `entry_point_contract.py`.

| Symbol / Konzept | Import |
|------------------|--------|
| Feature-Beschreibung | `from app.features import FeatureDescriptor` |
| Registrar-Typ | `from app.features import FeatureRegistrar` |
| Entry-Point-Gruppe (String) | `from app.features import ENTRY_POINT_GROUP` |
| Primär-Callable-Name (Doku/Konvention) | `ENTRY_POINT_PRIMARY_CALLABLE` |
| Legacy-Attributname | `ENTRY_POINT_LEGACY_REGISTRARS_ATTR` |

Plugins sollen **keine** tieferen `app.features.<submodul>`-Importe nutzen (außer dokumentierte Ausnahmen durch den Host — es gibt keine).

### 1.2 Host-API (PySide-Shell und Einstieg)

Alles in `app.features.__all__` ist für den Host stabil gedacht:

| Kategorie | Symbole (Auszug) |
|-----------|-------------------|
| Registry / Edition | `FeatureRegistry`, `get_feature_registry`, `set_feature_registry`, `build_feature_registry_for_edition`, `resolve_active_edition_name`, `DEFAULT_DESKTOP_EDITION`, `build_default_feature_registry`, `apply_feature_screen_registrars`, `register_builtin_registrars`, `iter_default_feature_descriptors` |
| Edition- & Dependency-Registry | `EditionDescriptor`, `EditionRegistry`, `build_default_edition_registry`, `get_edition_registry`, `set_edition_registry`, `DependencyGroupDescriptor`, `DependencyGroupRegistry`, … |
| Navigation / Commands | `collect_active_navigation_entry_ids`, `collect_active_gui_command_ids` |
| Builtin-Verfügbarkeit | `is_feature_technically_available` |

Host-Code unter `app/` importiert **`from app.features import …`** (durchgesetzt durch `test_features_public_surface_guard`).

### 1.3 CI- / Build-API

| Modul | Verwendung |
|-------|------------|
| `app.features.dependency_packaging` | PEP-621-/Extras-Abgleich (`validate_pep621_pyproject_alignment`, …) |
| `app.features.release_matrix` | Edition-Matrix, Plugin-Smoke-Payloads (`build_release_matrix`, `PLUGIN_VALIDATION_SMOKE_PROFILES`, …) |

Diese beiden Submodule sind die **einzigen** zulässigen direkten Submodul-Importe **außerhalb** `app/features/` — und nur aus `tools/ci/*` (Guard).

### 1.4 Intern / nicht exportiert, keine semver-Garantie

| Bereich | Beispiele |
|---------|-----------|
| Discovery-Implementierung | `feature_discovery._iter_entry_point_registrars`, `_iter_env_module_registrars` |
| Verfügbarkeits-Probes | `dependency_availability._GROUP_PROBES` |
| Validierung / Manifeste | `feature_validation`, `manifest_resolution`, `plugin_release_config`, … |

Nutzbare Tests: `tests/unit/features/` darf Interna importieren; übrige Tests und Produktcode nicht (Guard: keine `_*`-Imports aus `app.features`).

---

## 2. Cut-Blocker (aktuell)

| Blocker | Stand |
|---------|--------|
| Tiefe Host-Importe außerhalb `app.features` | **Erledigt** für `app/*` außer `app/features` (Root-API + CI-Ausnahme). |
| Unklare öffentliche Symbole | **Gebunden** durch erweitertes `__all__` und dieses Dokument. |
| Private API aus Tests außerhalb `tests/unit/features` | **Geblockt** durch `test_features_public_surface_guard`. |
| Import-Pfad nach physischem Split | **Entschieden:** Distribution `linux-desktop-chat-features` liefert **`app.features`** (Variante B in [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md)). |
| Host `pyproject` ohne Version-Pin für extrahiertes Paket | **Offen** bis Commit 2 im Execution Plan (phys. Split). |
| `landmarks.PLUGIN_ENTRY_POINT_GROUP` ↔ `ENTRY_POINT_GROUP` | **Erfüllt** (`test_package_map_contract`). |

Unabhängig von `features`: `test_app_package_guards` meldet weiterhin **App-Root-Datei-Drift** — kein Blocker für die *logische* features-Schnittstelle, aber für Gesamt-Repo-Sauberkeit.

---

## 3. Definition of Ready for Cut

### 3.1 Bereits erfüllt (Monorepo)

- [x] Keine `app.features` → `gui` / `services` / `ui_application` / `ui_runtime`-Importe (Segment-Guard).  
- [x] Keine `app.features` → andere `app.*`-Pakete (Runtime).  
- [x] Host unter `app/` nutzt `from app.features import …` (pytest-Guard).  
- [x] CI nutzt nur erlaubte Submodule (`release_matrix`, `dependency_packaging`).  
- [x] `__all__` deckt Plugin-, Host- und Entry-Point-Konstanten ab.  
- [x] Beispiel-Plugin importiert `FeatureDescriptor` über Paket-Root.

### 3.2 Zwingend vor physischem Split

- [ ] Eigenes `pyproject.toml` / Paketname / Version (SemVer) für das Features-Wheel (`linux-desktop-chat-features`).  
- [x] Importpfad: **`app.features`** im Wheel (kein `ldc_features` in Welle 1) — siehe [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md) § 2.  
- [ ] Host-Abhängigkeit deklarieren (`linux-desktop-chat-features>=x` oder Workspace-Äquivalent).  
- [ ] Guards/Tests, die `APP_ROOT / "features"` lesen, auf installiertes Paket umstellen (§ 4.3 PHYSICAL_SPLIT).  
- [ ] CI-Workflows auf installiertes Paket oder Monorepo-Workspace umstellen.  
- [ ] Release-Notes / API-Changelog für `__all__` etablieren.

### 3.3 Nach dem Cut zu verifizieren

- [ ] `pytest tests/unit/features/ tests/architecture/test_features_public_surface_guard.py tests/architecture/test_entry_point_contract_guard.py tests/architecture/test_package_map_contract.py`  
- [ ] `python tools/ci/release_matrix_ci.py`  
- [ ] Plugin-Validation-Workflow  
- [ ] Kein regressiver Import von entfernten Submodul-Pfaden im Host

---

## 4. Pytest-Kommandos (Kurzset)

```bash
pytest tests/architecture/test_features_public_surface_guard.py \
  tests/architecture/test_entry_point_contract_guard.py \
  tests/architecture/test_package_map_contract.py \
  tests/architecture/test_edition_manifest_guards.py -q

pytest tests/unit/features/ -q
```

---

## 5. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: API-Schichten, DoR, Blocker, pytest-Kommandos |
| 2026-03-25 | Verweis PHYSICAL_SPLIT; Importpfad-Entscheidung B; DoR § 3.2 aktualisiert |
