# Cut-Liste: `linux-desktop-chat-features` (Commit 1 → späterer Host-Cut)

**Stand:** Vorlage im Host-Monorepo unter `linux-desktop-chat-features/`. Nach Auslagerung als eigenes Repo bleibt diese Datei im Features-Repo; der Host verweist in seiner Doku auf die veröffentlichte Version.

---

## 1. 1:1 aus `app/features/` ins Features-Repo (`src/app/features/`)

Alle aktuellen Python-Module und Pakete — **ohne Importpfad-Änderung** (weiter `app.features.*` intern):

| Bereich | Pfade |
|---------|--------|
| Root-Module | `__init__.py`, `entry_point_contract.py`, `descriptors.py`, `registrar.py`, `registry.py`, `feature_registry.py`, `builtins.py`, `feature_discovery.py`, … (vollständiger Spiegel des Host-`app/features/`) |
| Unterpakete | `editions/`, `dependency_groups/` |

**Repo-spezifische Anpassungen am Code:** keine für Commit 1 (Quelle = Spiegel des Hosts). Später ggf. Versionsstrings oder README-only-Links.

**Zusätzlich im Features-Repo (nicht im Host-`app/features/`):**

- `src/app/__init__.py` — eine Zeile Paketmarker (wie Host-`app/__init__.py`), damit `app.features` installierbar ist.

---

## 2. Dokumentation

| Mit ins Features-Repo | Bleibt / primär im Host |
|------------------------|-------------------------|
| `README.md`, `MIGRATION_CUT_LIST.md`, `pyproject.toml` | `docs/architecture/PACKAGE_FEATURES_CUT_READY.md`, `PACKAGE_FEATURES_PHYSICAL_SPLIT.md`, `PACKAGE_MAP.md`, `PACKAGE_SPLIT_PLAN.md`, `PLUGIN_AUTHORING_GUIDE.md` |
| Kurzverweise in README auf Host-Doku-URLs nach Split | Vollständige Architekturlandkarte |

Nach eigenständigem Repo: Kopie oder Auszug der **plugin-relevanten** Abschnitte aus `PLUGIN_AUTHORING_GUIDE.md` ins Features-`README` oder `docs/` optional ergänzen.

---

## 3. Tests

### Im Features-Repo vorhanden (`tests/unit/`) — minimale **isolierte** Suite

Diese Tests laufen **ohne** installierten Host (`app.gui`, Host-`pyproject`, `tools/ci`):

| Datei | Inhalt |
|-------|--------|
| `test_package_exports.py` | Smoke: `import app.features`, `ENTRY_POINT_GROUP` |
| `test_dependency_packaging.py` | Packaging-Policies/Registry (ohne PEP-621-Vollabgleich) — `test_pep621_pyproject_alignment_clean` → **skipped** |
| `test_release_matrix.py` | Matrix-/Edition-/Overlay-Logik — **ohne** `validate_release_matrix_consistency()` (Pfad-Check gegen Host-`tests/unit/features/`) und **ohne** Subprozess zu `tools/ci/release_matrix_ci.py` |

### Nur im Host (`tests/unit/features/`) — volle Suite

| Testdatei / Muster | Grund |
|--------------------|--------|
| `test_edition_and_dependency_manifests.py`, Tests die `build_default_feature_registry()` bis zu GUI-Builtins auflösen | `feature_discovery` importiert `app.gui.registration.feature_builtins` |
| `test_plugin_release_configuration.py` | benötigt **PyYAML** + Host-Kontext für YAML-Configs |
| `test_release_matrix.py` — entfernte Fälle: `test_validate_release_matrix_clean`, `test_ci_script_print_matrix_json_exit_zero` | verweisen auf Host-Pfade / `tools/ci` |
| `test_feature_registry.py`, `test_feature_registrar.py`, `test_feature_discovery.py`, `test_feature_validation.py`, `test_entry_point_plugin_integration.py`, `test_plugin_product_activation.py`, `test_dependency_availability.py`, `test_bootstrap_edition.py` | `app.gui` / builtins |
| `test_internal_plugin_release_positioning.py` | Subprozess `tools/ci/release_matrix_ci.py`, `cwd=Host-Repo` |

### Architektur-Guards (`tests/architecture/`)

Bleiben **vollständig im Host**, bis Commit 4 (Umstellung auf `find_spec` / installiertes Paket). Optional später Duplikat schlanker Vertrags-Tests im Features-Repo.

---

## 4. Nicht mitwandern

- `app/gui/**`, `run_gui_shell.py`, Host-`pyproject.toml`, `.github/workflows/` (Commit 2–3 des Execution Plans).
- `tools/ci/release_matrix_ci.py` — bleibt Host; importiert weiter `app.features.*` nach Installation der Distribution.

---

## 5. Sync-Hinweis (bis zum Host-Cut)

Solange beide Bäume existieren: Änderungen an `app/features/` im Host sollten in die Vorlage `linux-desktop-chat-features/src/app/features/` **übernommen** werden (manuell oder Skript), sonst driftet die Vorlage.
