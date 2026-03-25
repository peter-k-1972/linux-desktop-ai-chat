# Plugin-Editionen vs. öffentliche Release-/Smoke-Architektur

## Ziel

Interne Plugin-Validierung (z. B. Edition `plugin_example`, Demo-Registrar `ldc.plugin.example`) soll **testbar** und **maschinenlesbar** beschrieben sein, ohne die **öffentliche** Build-/Release-Matrix zu vergrößern oder still zu vermischen.

## Zwei Ebenen

| Ebene | Konstante / Modell | CI | Artefakt / „Release“ |
|-------|-------------------|----|----------------------|
| **Öffentlich** | `OFFICIAL_BUILD_RELEASE_EDITION_NAMES`, `EDITION_SMOKE_PROFILES`, `build_release_matrix()` | `edition-smoke-matrix.yml` | Ja — intendiertes Produktziel |
| **Intern / Plugin-Validierung** | `INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES`, `PLUGIN_VALIDATION_SMOKE_PROFILES` | `plugin-validation-smoke.yml` (separat, „internal“) | **Nein** |

## `plugin_example` (Referenz)

- Registriert in `EditionRegistry` mit `visibility_profile: internal`.
- **Nicht** in `OFFICIAL_BUILD_RELEASE_EDITION_NAMES` → kein `EditionBuildTarget` in `ReleaseMatrix`, `resolve_build_target("plugin_example")` ist `None`.
- **Profil:** `PLUGIN_VALIDATION_SMOKE_PROFILES["plugin_example"]` — `scope_id`, Marker-Vorschlag, **Unit-/Feature-Testpfade** (kein Ersatz für die großen GUI-Smokes der offiziellen Editionen).
- Operativer Hinweis: Demo-Plugin per `pip install -e examples/plugins/...`, `LDC_EDITION=plugin_example`; optional YAML siehe [PLUGIN_FEATURE_RELEASE_CONFIGURATION.md](PLUGIN_FEATURE_RELEASE_CONFIGURATION.md).

## Maschinenlesbarer Export

- Öffentliche Matrix: `tools/ci/release_matrix_ci.py print-matrix-json`
- Interne Plugin-Profile (vollständig, lesbar): `tools/ci/release_matrix_ci.py print-internal-plugin-json`
- Interne Plugin-**CI-Matrix** (`{"include": [...]}`): `tools/ci/release_matrix_ci.py print-internal-plugin-matrix-json`  
  (Quelle: dieselben `PLUGIN_VALIDATION_SMOKE_PROFILES`-Einträge; vor Ausgabe läuft dieselbe `validate` wie bei der offiziellen Matrix.)

## Internal Plugin Smoke Workflow

**Datei:** `.github/workflows/plugin-validation-smoke.yml`  
**Name:** „Plugin Validation Smoke (internal)“

**Warum:** Die offizielle `edition-smoke-matrix.yml` soll **nur** `OFFICIAL_BUILD_RELEASE_EDITION_NAMES` abdecken. Interne Plugin-Editionen (Referenz: `plugin_example`) brauchen einen **separaten**, klar beschrifteten Pfad — ohne Artefakte, ohne Release, ohne Vermischung mit der Produktmatrix.

**Unterschied zu `edition-smoke-matrix`:**

| | Edition Smoke (Release Matrix) | Plugin Validation (internal) |
|---|-------------------------------|----------------------------|
| Matrix-Export | `print-matrix-json` | `print-internal-plugin-matrix-json` |
| Editionen | `minimal` … `full` | nur `INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES` |
| Zweck | Öffentliches Produkt-Smoke | Entry-Point / Freigabe / Feature-Unit-Tests |

**Trigger:** `workflow_dispatch` und `pull_request` bei Änderungen unter `app/features/**`, `examples/plugins/**`, diesem Workflow oder `tools/ci/release_matrix_ci.py`.

**Ablauf:** `prepare` validiert die Gesamt-Release-Matrix (inkl. interner Profil-Konsistenz), schreibt die **interne** Matrix nach `GITHUB_OUTPUT`. `plugin-smoke` installiert `pip install -e ".[${{ matrix.pip_extras }}]"` (Werte aus Profil, z. B. `rag,dev`), optional das Demo-Plugin (`install_demo_plugin`), setzt `LDC_EDITION=${{ matrix.edition }}`, führt `pytest` mit `smoke_paths` aus.

### Lokal simulieren

```bash
pip install -e ".[dev]"
python tools/ci/release_matrix_ci.py validate
python tools/ci/release_matrix_ci.py print-internal-plugin-matrix-json | python -m json.tool
pip install -e ".[rag,dev]"
pip install -e examples/plugins/ldc_plugin_example
export LDC_EDITION=plugin_example
pytest -q --tb=short tests/unit/features/test_plugin_product_activation.py \
  tests/unit/features/test_plugin_release_configuration.py \
  tests/unit/features/test_entry_point_plugin_integration.py
```

## Governance

- `validate_release_matrix_consistency()` prüft weiter die **offizielle** Matrix **und** ruft `validate_internal_plugin_smoke_consistency()` auf (Profil ↔ Registry, keine Schnittmenge mit offiziellen Namen, `visibility_profile=internal`, Testdateien vorhanden).

## Verweise

- `app/features/release_matrix.py`
- [EDITION_RELEASE_MATRIX.md](EDITION_RELEASE_MATRIX.md)
- [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](PLUGIN_FEATURE_PRODUCT_ACTIVATION.md)
- [PLUGIN_PACKAGES_ENTRY_POINTS.md](PLUGIN_PACKAGES_ENTRY_POINTS.md)
