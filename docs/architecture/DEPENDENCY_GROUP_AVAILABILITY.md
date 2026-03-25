# Dependency-Gruppen: technische Verfügbarkeit (Laufzeit)

## Begriffe

| Begriff | Bedeutung |
|--------|------------|
| **Edition aktiv** | Edition-Deskriptor wählt eine Feature-**Menge** (`enabled_features` ∖ `disabled_features`). |
| **Feature aktiviert** | Name liegt in dieser Menge; `FeatureRegistry.apply_active_feature_mask` setzt `enabled`. |
| **Dependency-Gruppe technisch verfügbar** | Zentrale Probe (z. B. repräsentativer Import) in `dependency_availability` meldet `AvailabilityResult.available`. |
| **Feature effektiv verfügbar** | `enabled` **und** `FeatureRegistrar.is_available()` **True** — letzteres prüft u. a. `optional_dependencies` gegen Gruppen-Verfügbarkeit **und** implizit `core`. |

**Reihenfolge im Produktfluss:** Edition → aktivierte Features → technische Availability → Screens / Nav / Commands (bereits fail-soft in Registry, `nav_binding`, Bootstrap).

## Wo im Code

- **Modelle:** `app/features/availability_types.py` — `AvailabilityResult`, `FeatureAvailabilityResult`
- **Proben & API:** `app/features/dependency_availability.py`
  - **Packaging-Zielmodell (PEP 621–fähig):** `app.features.dependency_packaging` und `DEPENDENCY_GROUPS_TO_EXTRAS.md` — dieselben Gruppennamen; Drift-Check `validate_availability_probe_names_align`.
  - `is_module_importable(module_name)`
  - `check_dependency_group_availability(group_name, dep_registry=...)`
  - `check_feature_availability(descriptor, ...)`
  - `is_feature_technically_available(descriptor, ...)` — von `feature_builtins._builtin_is_available` genutzt
- **Registrare:** `app/gui/registration/feature_builtins.py` — `is_available()` delegiert an `is_feature_technically_available`
- **Deskriptor:** `FeatureDescriptor.optional_dependencies` — **harte** technische Gruppen-Tags (Namen wie `rag`, `workflows`, `governance`), keine lose Marketing-Tags im Operations-Hub (der Hub bleibt ohne `rag`-Pflicht).

## Gruppen und Proben (Ist-Stand)

| Gruppe | Probe (minimal) |
|--------|------------------|
| `core` | `PySide6.QtCore`, `aiohttp` |
| `rag` | `chromadb` |
| `agents` | `app.agents` |
| `workflows` | `app.workflows` |
| `governance` | `app.services.qa_governance_service` |
| `qml` | `PySide6.QtQml` |
| `dev` | `pytest` |
| `ops` | keine Modulprobe (Monolith) — immer verfügbar |

Gruppen ohne Eintrag in `_GROUP_PROBES`: als verfügbar gewertet (`reason_code=no_probe`), bis eine Probe ergänzt wird.

## Ohne pyproject-Extras

Probes sind **Importfähigkeit** am laufenden Interpreter — dasselbe Umgebungsbild wie bei `pip install -e .` ohne gesonderte extras. Später können Probes durch „Wheel enthält extra X“ oder Manifest-Dateien ersetzt werden, ohne die `AvailabilityResult`-API zu brechen.

## Tests vs. Produktion

In `tests/conftest.py` ist standardmäßig `LDC_IGNORE_TECHNICAL_AVAILABILITY=1` gesetzt, damit Edition-/Manifest-Tests nicht von fehlendem `chromadb` o. Ä. abhängen. **`tests/unit/features/test_dependency_availability.py`** setzt die Prüfung wieder an (Fixture mit `LDC_IGNORE_TECHNICAL_AVAILABILITY=0`).

## Bewusst nicht

- Kein Umbau von `pyproject.toml` / extras
- Keine erzwungene Installation optionaler Pakete
- Keine verteilten Import-Probes in GUI-Modulen

## Nächster Schritt

- Proben mit Wheel-/Build-Manifest koppeln
- `LDC_IGNORE_TECHNICAL_AVAILABILITY` in CI nur dort setzen, wo nötig

## Verweise

- [EDITION_AND_DEPENDENCY_MANIFESTS.md](EDITION_AND_DEPENDENCY_MANIFESTS.md)
- `app/features/dependency_availability.py`
