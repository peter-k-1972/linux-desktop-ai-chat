# Edition → Build-/Release-Matrix

## Zweck

Editionen waren bisher **Produkt-Manifeste** (Feature-Menge, deklarierte Dependency-Gruppen).
Diese Datei beschreibt die **Build-/Release-Zielschicht** in `app.features.release_matrix`:
welche Editionen offiziell gebaut/getestet werden, welche technischen Anforderungen und Smoke-Pfade
sich daraus ergeben — **ohne** GitHub-Actions-Umbau oder Artefakt-Splitting.

## Offizielle Build-/Release-Ziele

| Edition | Rolle | Referenz? |
|---------|--------|-----------|
| `minimal` | Kern-Desktop (Kommandozentrale, Operations-Hub, Einstellungen) | nein |
| `standard` | + Control Center, Prompt Studio, Knowledge-Metadaten | nein |
| `automation` | + Workflows, Runtime-Observability | nein |
| `full` | Alle eingebauten Features inkl. QA/Governance | **ja** (Default-Bootstrap) |

Die Menge ist in Code als `OFFICIAL_BUILD_RELEASE_EDITION_NAMES` fixiert. Weitere Einträge im
`EditionRegistry` (z. B. `plugin_example`) sind **architektonisch** möglich, werden aber **nicht**
automatisch Release-Ziele: interne Plugin-Validierung nutzt `INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES`
und `PLUGIN_VALIDATION_SMOKE_PROFILES` — siehe [PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md](PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md).

**Referenzedition:** `REFERENCE_BUILD_EDITION_NAME` (`full`) muss mit `DEFAULT_DESKTOP_EDITION` in
`edition_resolution.py` übereinstimmen (Governance-Test).

## Architektonisch vs. offiziell

- **EditionRegistry / builtins:** kanonische Produkteditionen (derzeit alle `visibility_profile=public`).
- **Release-Matrix:** explizite Teilmenge, die CI/Release/Smoke **offiziell** adressieren soll.
- Nicht jede künftige Edition muss sofort ein Release-Artefakt erhalten.

## Dependencies und pip-Extras (keine Doppelwahrheit)

Pro Build-Target:

1. **dependency_groups:** `edition_declared_and_implied_dependency_groups` aus
   `manifest_resolution.py` (Vereinigung Manifest + Feature-Implikation).
2. **pip_runtime_extras:** Schnitt mit `dependency_packaging.packaging_target_for`: nur Gruppen mit
   publiziertem pip-Extra, **ohne** `dev`. Gruppen wie `core` (Basisinstall) und `workflows`
   (LOGICAL_MARKER) erscheinen hier nicht als Extra.
3. **pip_ci_extras:** empfohlen für Testjobs — standardmäßig `("dev",)` (Tooling-Extra).

Version-Pins stehen in `pyproject.toml`; die Matrix liefert **Namen**
und **Gruppenlogik**.

## Smoke- und Test-Scope

### Offizielle Editionen

`EDITION_SMOKE_PROFILES` pro offizieller Edition:

- **scope_id** — maschinenlesbarer Kurzname (`minimal_core`, `standard_desktop`, …).
- **pytest_markers** — Konvention für spätere Selektion (z. B. `smoke`, `edition_full`); Marker
  müssen in der Test-Infrastruktur noch registriert werden, wenn sie strikt genutzt werden sollen.
- **suggested_smoke_paths** — relative Pfade unter `tests/smoke/` (und für `full` ergänzend
  Architektur-Guards als Konsistenzanker).

Kein Ersatz für die bestehende Pytest-Sammlung — nur **Zielvertrag** für künftige Matrix-Jobs.

### Interne Plugin-Validierung (nicht in der öffentlichen Matrix)

- `PLUGIN_VALIDATION_SMOKE_PROFILES` — maschinenlesbarer Vertrag für Editionen wie `plugin_example` (Unit-/Feature-Pfade, Env-/Install-Hinweise).
- Export: `python tools/ci/release_matrix_ci.py print-internal-plugin-json`
- Konsistenz: Teil von `validate_release_matrix_consistency()` über `validate_internal_plugin_smoke_consistency()`.

## Artefaktnamen

Konvention:

`linux-desktop-chat-<edition>`

Editionen ohne Unterstriche (`minimal`, `standard`, `automation`, `full`) → stabile, PEP-503-freundliche Slugs.

## Release-Kanal

Abgeleitet aus `EditionDescriptor.visibility_profile`:

| visibility_profile | release_channel |
|--------------------|-----------------|
| `public` | `stable` |
| `internal` | `internal` |
| `partner` | `experimental` |

## Maschinenlesbarer Export

- `build_release_matrix()` → `ReleaseMatrix`
- `release_matrix_to_json_dict(matrix)` → JSON-taugliches `dict`
- `validate_release_matrix_consistency()` → leere Liste bei Erfolg

Geeignet als Eingabe für spätere Skripte (GitHub Actions, Smoke-Runner, Release-Notes-Generator).

## Bewusst noch nicht automatisiert

- Keine Wheel-Builds pro Edition, kein Marketplace.
- Kein CI-Job für **interne** Plugin-Editionen (nur offizielle Matrix in `edition-smoke-matrix.yml`).
- Marker in `EDITION_SMOKE_PROFILES` sind dokumentiert/vertraglich — keine globale pytest.ini-Änderung in dieser Phase.

## Nächster Schritt

Siehe [CI_EDITION_SMOKE_SKELETON.md](CI_EDITION_SMOKE_SKELETON.md) — GitHub Actions Workflows
`edition-smoke-matrix.yml` (öffentlich) und `plugin-validation-smoke.yml` (interne Plugin-Validierung,
Matrix nur über `print-internal-plugin-matrix-json`). Tool: `tools/ci/release_matrix_ci.py`. Ausbau: echte
`optional-dependencies` + schlankere Basis-Install pro Edition.

## Verwandte Doku

- [PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md](PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md)
- [CI_EDITION_SMOKE_SKELETON.md](CI_EDITION_SMOKE_SKELETON.md)
- [EDITION_AND_DEPENDENCY_MANIFESTS.md](EDITION_AND_DEPENDENCY_MANIFESTS.md)
- [DEPENDENCY_GROUPS_TO_EXTRAS.md](DEPENDENCY_GROUPS_TO_EXTRAS.md)
- [BOOTSTRAP_EDITION_ACTIVATION.md](BOOTSTRAP_EDITION_ACTIVATION.md)
