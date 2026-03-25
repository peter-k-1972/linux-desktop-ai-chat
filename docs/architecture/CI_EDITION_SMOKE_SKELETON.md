# CI: Edition-Smoke-Skelett (Release-Matrix)

## Zweck

Die Build-/Release-Matrix in `app.features.release_matrix` wird in GitHub Actions **ohne** duplizierte
Editionslisten genutzt: ein Vorbereitungsjob validiert die Matrix und schreibt eine JSON-Matrix; der
Smoke-Job läuft pro offizieller Edition mit `LDC_EDITION` und den `suggested_smoke_paths` aus dem Code.

Workflow (öffentlich): `.github/workflows/edition-smoke-matrix.yml`  
Workflow (interne Plugin-Validierung, separat): `.github/workflows/plugin-validation-smoke.yml`  
Helfer: `tools/ci/release_matrix_ci.py`

## Ablauf

1. **prepare**
   - `pip install -e ".[dev]"` (kernfähiges Projekt + Test-Tooling für Validierung)
   - `python tools/ci/release_matrix_ci.py validate` — Release-Matrix, JSON-Sanity **und** `validate_pep621_pyproject_alignment`
   - JSON für `strategy.matrix`: `print-matrix-json` → `GITHUB_OUTPUT` (`matrix`)

2. **edition-smoke** (Matrix über `fromJson(needs.prepare.outputs.matrix)`)
   - **Install:** `pip install -e ".[${{ matrix.pip_extras }}]"` — `pip_extras` ist komma-separierte Liste der PEP-621-Extra-Namen (Runtime + `dev`), aus der Release-Matrix abgeleitet, keine hart kodierte Editionsliste im YAML.
   - **Edition:** `LDC_EDITION=${{ matrix.edition }}`
   - **Tests:** `pytest ${{ matrix.smoke_paths }}` (Pfade aus `EDITION_SMOKE_PROFILES`)

## Welche Editionen laufen

Genau `OFFICIAL_BUILD_RELEASE_EDITION_NAMES` aus `release_matrix.py` — derzeit `minimal`, `standard`,
`automation`, `full`. Änderungen nur dort (+ Smoke-Profile), nicht im Workflow.

**Interne Plugin-Editionen** (z. B. `plugin_example`) laufen **nicht** in dieser Matrix. Profil und
empfohlene Unit-Pfade: `PLUGIN_VALIDATION_SMOKE_PROFILES`, Export `print-internal-plugin-json` — siehe
[PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md](PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md).

### Lokaler Plugin-Validierungslauf (optional)

Kein separater CI-Job in dieser Phase; reproduzierbar lokal:

```bash
pip install -e ".[dev]"
pip install -e examples/plugins/ldc_plugin_example
export LDC_EDITION=plugin_example
pytest -q \
  tests/unit/features/test_plugin_product_activation.py \
  tests/unit/features/test_plugin_release_configuration.py \
  tests/unit/features/test_entry_point_plugin_integration.py
```

Pfade und Metadaten sind auch in `plugin_validation_profiles_to_json_dict()` bzw. `print-internal-plugin-json` abgebildet.

## Installation / Extras

- **PEP 621:** `pyproject.toml` mit `[project.dependencies]` (core) und `[project.optional-dependencies]` (siehe `PEP621_OPTIONAL_DEPENDENCIES.md`).
- **`requirements.txt`:** `-e .[rag,dev]` — bequemer Einstieg, keine zweite Paketliste.
- **Edition-Smoke:** `pip install -e ".[matrix.pip_extras]"` pro Matrixzeile.

## Bewusst nicht automatisiert

- Keine Multi-OS-Matrix, keine Wheels, kein Release-Artefakt-Split.
- Keine strikte Isolation „nur Minimal-Pakete“ pro Edition (dafür später: echte Extras + Lockfile).
- Pytest-Marker aus `EDITION_SMOKE_PROFILES` werden hier nicht als `-m` gefiltert — es werden die
  **Dateipfade** aus der Matrix ausgeführt.

## Lokale Nachnutzung

```bash
# Matrix-Drift / Konsistenz (inkl. pyproject ↔ Packaging-Mapping)
python tools/ci/release_matrix_ci.py validate

# Maschinenlesbare Matrix (wie in CI)
python tools/ci/release_matrix_ci.py print-matrix-json | python -m json.tool

# Einzelne Edition (Beispiel full)
export LDC_EDITION=full
export LDC_IGNORE_TECHNICAL_AVAILABILITY=1
export QT_QPA_PLATFORM=offscreen
pip install -e ".[rag,agents,governance,ops,qml,dev]"
pytest -q tests/smoke/test_app_startup.py tests/smoke/test_navigation_consistency.py tests/architecture/test_edition_manifest_guards.py
```

Pfade und Editionen stammen aus `build_release_matrix()` / `resolve_build_target("<edition>")`.

## Nächste Ausbauphase

- Optional-dependencies aus `dependency_packaging` produktiv machen; CI dann `pip install .[rag,...]`
  statt nur Overlay-Strings.
- Marker-gesteuerte Smoke-Subset (`pytest -m "smoke and edition_full"`) nach Registrierung der Marker.

## Verwandte Doku

- [EDITION_RELEASE_MATRIX.md](EDITION_RELEASE_MATRIX.md)
- [EDITION_AND_DEPENDENCY_MANIFESTS.md](EDITION_AND_DEPENDENCY_MANIFESTS.md)
