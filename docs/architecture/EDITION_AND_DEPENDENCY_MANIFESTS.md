# Edition- und Dependency-Manifeste (Phase Manifest)

## Drei Ebenen

| Ebene | Bedeutung | Beispiel |
|--------|-----------|----------|
| **Feature** | Produktfähigkeit, Bootstrap-Anteil (Registrar) | `operations_hub`, `knowledge_rag` |
| **Edition** | Auswahl **welche** Features zur Produktlinie gehören | `minimal`, `standard`, `full`, … |
| **Dependency Group** | Technische **Installations-/Extra-Gruppe** (pip später) | `core`, `rag`, `dev` |

**Python-Pakete** (`app/rag`, …) sind **nicht** Editionen und **nicht** pip-extras — sie liefern Code, den **Features** nutzen.

## Warum `extras` ≠ Edition

- **pip extra** (z. B. `[rag]`) beschreibt *installierte* Python-Abhängigkeiten.
- **Edition** beschreibt *aktivierte Produktlogik* (Feature-Menge). Dieselbe extra kann mehreren Features dienen; eine Edition kann mehrere Gruppen referenzieren.
- Mapping ist **n:m**; `pyproject.toml` optional-dependencies spiegeln die Dependency-Gruppen (siehe [PEP621_OPTIONAL_DEPENDENCIES.md](PEP621_OPTIONAL_DEPENDENCIES.md)).

## Warum Editionen Features aktivieren, nicht Pakete

- Pakete kennen keine Edition (Architekturregel).
- Features sind die bereits eingeführte vertikale Aktivierungseinheit (Registrar).
- Editionen sind eine **zweite Wahrheitsebene darüber**: „welche Registrare/Bootstrap-Teile gehören zur Produktlinie“.

## Code-Ort

- `app/features/editions/` — `EditionDescriptor`, `EditionRegistry`, `builtins`
- `app/features/dependency_groups/` — `DependencyGroupDescriptor`, `DependencyGroupRegistry`, `builtins`
- **Technische Verfügbarkeit (Laufzeit):** [DEPENDENCY_GROUP_AVAILABILITY.md](DEPENDENCY_GROUP_AVAILABILITY.md) — `dependency_availability.py`, angebunden an `FeatureRegistrar.is_available()`
- **Registrar-Discovery:** [FEATURE_PLUGIN_DISCOVERY.md](FEATURE_PLUGIN_DISCOVERY.md) — `feature_discovery.py` erweitert die Registry neben Builtins
- **Produktfreigabe externer Features:** [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](PLUGIN_FEATURE_PRODUCT_ACTIVATION.md) — `feature_product_release.py`, `effective_activation_features` (Builtins unverändert; Externe nur mit Freigabe); optional YAML [PLUGIN_FEATURE_RELEASE_CONFIGURATION.md](PLUGIN_FEATURE_RELEASE_CONFIGURATION.md)
- `app/features/feature_name_catalog.py` — kanonische Feature-Namen (Synchron mit `feature_builtins`)
- `app/features/manifest_resolution.py` — Mengenlogik (effektive Features, **Aktivierungsmenge** inkl. Freigabe, implizierte Gruppen, Validierung)

## Eingebaute Editionen

| name | Kurzidee |
|------|-----------|
| `minimal` | Kommandozentrale, Operations-Hub, Einstellungen |
| `standard` | + Control Center, Prompt Studio, Knowledge-Metadaten |
| `automation` | + Workflows- und Runtime-Observability-Metadaten |
| `full` | alle neun eingebauten Features inkl. QA & Governance |
| `plugin_example` | intern: Minimal-Set + Demo-Plugin `ldc.plugin.example` mit Produktfreigabe (kein Release-Matrix-Ziel) |

**Bootstrap (Phase Aktivierung):** ``run_gui_shell`` setzt die ``FeatureRegistry`` über ``build_feature_registry_for_edition(resolve_active_edition_name(...))``. Die effektive Aktivierungsmenge nutzt ``effective_activation_features`` (Externe nur bei Host-Freigabe). Default-Edition ist ``full``. Siehe [BOOTSTRAP_EDITION_ACTIVATION.md](BOOTSTRAP_EDITION_ACTIVATION.md), [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](PLUGIN_FEATURE_PRODUCT_ACTIVATION.md).

Die **zentrale Navigation** (ID-Registry) ist unverändert; **Sichtbarkeit** der Sidebar und der `nav.*`-Commands ist edition-/feature-gefiltert — siehe [NAVIGATION_FEATURE_BINDING.md](NAVIGATION_FEATURE_BINDING.md).

## Eingebaute Dependency-Gruppen

`core`, `rag`, `agents`, `workflows`, `ops`, `qml`, `dev` — mit informativen `python_packages` und `required_for_features` für **implizite** Ableitung (siehe `dependency_groups_implied_by_features`).

## Spätere GitHub-/Release-Artefakte (Ableitbarkeit)

- **Build-/Release-Matrix (Ist-Modul):** [EDITION_RELEASE_MATRIX.md](EDITION_RELEASE_MATRIX.md) — `app.features.release_matrix` leitet Gruppen, pip-Runtime-Extras, Smoke-Pfade und Artefaktnamen aus Editionen ab (JSON-exportierbar).
- **Wheel-Tags / Build-Matrix:** aus `EditionDescriptor.dependency_groups` ∪ implizierte Gruppen (siehe Matrix-Validierung).
- **Smoke-Tests pro Edition:** siehe `EDITION_SMOKE_PROFILES` in `release_matrix.py`.
- **Kompatibilitäts-Matrix:** Plugin deklariert benötigte Feature-Namen → Edition muss Obermenge sein.

## Bewusst nicht implementiert

- Kein automatischer Generator „Manifest → pyproject“ (manuelles Update + `validate_pep621_pyproject_alignment`).
- Kein CLI `--edition` mit Wirkung auf `FeatureRegistry`.
- Kein Entfernen von UI zur Laufzeit.
- `core` importiert keine Edition-Module (bestehende Package-Guards).

## Verweise

- [FEATURE_REGISTRAR_ARCHITECTURE.md](FEATURE_REGISTRAR_ARCHITECTURE.md)
- [FEATURE_SYSTEM.md](FEATURE_SYSTEM.md)
- `tests/unit/features/test_edition_and_dependency_manifests.py`
- `tests/architecture/test_edition_manifest_guards.py`
