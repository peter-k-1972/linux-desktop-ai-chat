# Dependency-Gruppen → pip-Extras / Basisinstallation

## Zweck

Die eingebauten `DependencyGroupDescriptor`-Einträge (`app.features.dependency_groups.builtins`)
beschreiben fachlich und technisch **Installations-Cluster**. Diese Datei fasst zusammen, wie sie
in eine spätere **PEP 621**-Struktur (`project.dependencies` / `project.optional-dependencies`)
übergehen. `pyproject.toml` ist eingeführt; Drift-Checks binden Manifest und Datei zusammen.

Die ausführbare Quelle für Policies ist `app.features.dependency_packaging` (`CANONICAL_GROUP_POLICIES`,
Hilfsfunktionen und Validierung).

## Namensdisziplin

- **Eine** Namenswelt: Gruppenname im Registry = Key unter `optional-dependencies`, sofern publiziert.
- Keine Alias-Tabelle für Extras; Abweichungen wären ein Architekturbruch und werden von
  `validate_packaging_alignment` nicht unterstützt.

## Klassifikation der Builtin-Gruppen

| Gruppe | Rolle | Basisinstall (`project.dependencies`) | pip-Extra | Endnutzer-kommuniziert |
|--------|--------|----------------------------------------|-----------|-------------------------|
| `core` | GUI, Async, ORM, HTTP, … | Ja (alle `python_packages` von `core`) | Nein | N/A (Pflichtbasis) |
| `workflows` | Logische Zuordnung Workflow-Feature, keine extra Wheels | Nein | Nein | Nein |
| `rag` | Chroma / RAG | Nein | Ja (`rag`) | Ja |
| `agents` | Agent-UI (derzeit leere Extra-Liste) | Nein | Ja (`agents`) | Ja |
| `ops` | Ops-Oberflächen (leere Liste, informativ) | Nein | Ja (`ops`) | Nein (intern/Metapaket) |
| `qml` | Qt-Quick-Pfad (leere Liste, optional) | Nein | Ja (`qml`) | Ja |
| `governance` | QA-Governance (leere Liste, Import-Monolith) | Nein | Ja (`governance`) | Ja |
| `dev` | pytest / Qt-Test | Nein | Ja (`dev`) | Nein (nur CI/Entwicklung) |

**Überlappung:** Alle Runtime-Extras setzen implizit eine funktionierende Basis voraus; `core` ist
nicht wiederholbar als Extra. Leere Extra-Listen (`[]`) sind bewusst erlaubt — sie dokumentieren
Slice/Metapaket und reservieren den Namen für spätere Pins.

## Availability

`app.features.dependency_availability` prüft dieselben Gruppennamen (`_GROUP_PROBES`).  
`validate_availability_probe_names_align(registry)` stellt Registry ↔ Probes deckungsgleich sicher.

Später können installierte Extras die gleichen Namen tragen; die Probes bleiben die Laufzeitwahrheit,
bis ein Installer die Umgebung anders modelliert (ohne API-Bruch an den Gruppen-Strings).

## Export / pyproject (produktiv)

- `pyproject.toml` im Repo-Root: `[project.dependencies]` = core, `[project.optional-dependencies]` = Ziel-Dict aus dem Packaging-Mapping.
- `optional_dependencies_target_dict(registry)` und `validate_pep621_pyproject_alignment(Path("pyproject.toml"))` — Drift-Check auf Distributionsnamen (normalisiert).
- `pyproject_optional_dependencies_snippet(registry)` — nur noch Hilfstext; Quelle der Wahrheit ist die echte `pyproject.toml`.

## Drift-Kontrolle

- `validate_packaging_alignment(registry)`: Registry-Keys = Policy-Keys; inhaltliche Regeln (z. B. nur
  `core` mit `include_in_default_install`, `workflows` ohne `python_packages`).
- Tests und Architektur-Guards rufen die Validierung auf dem Default-Registry auf.

## Bewusst noch nicht umgesetzt

- Kein Lockfile (pip-tools/uv); Pins stehen in `pyproject.toml`.
- Keine pro-Edition-Wheels / Release-Splitting.

## Nächster Schritt

Optional Lockfile erzeugen; weitere Pakete in Extras heben. Siehe [PEP621_OPTIONAL_DEPENDENCIES.md](PEP621_OPTIONAL_DEPENDENCIES.md).
