# PEP 621 optional-dependencies (Ist-Stand)

## Quelle der Wahrheit

| Schicht | Rolle |
|---------|--------|
| `DependencyGroupDescriptor` + `CANONICAL_GROUP_POLICIES` | Welche Gruppe existiert, welche PyPI-Namen sie trägt, ob ein pip-Extra vorgesehen ist |
| `pyproject.toml` | Produktive `[project.dependencies]` (nur **core**) und `[project.optional-dependencies]` |
| `validate_pep621_pyproject_alignment(pyproject.toml)` | Drift-Check: Keys und Distributionsnamen (normalisiert) |

Keine zweite Namenswelt: Extra-Key = `DependencyGroupDescriptor.name` (z. B. `rag`, `dev`).

## Was in der Basisinstallation liegt (`[project.dependencies]`)

Entspricht der Dependency-Gruppe **core** (inkl. Context-Replay-Bibliotheken, die historisch in der monolithischen `requirements.txt` standen):

- PySide6, qasync, aiohttp, SQLAlchemy, alembic, jsonschema, deepdiff, PyYAML

**Kein** pip-Extra für `core`.

## Welche optional-dependencies existieren

| Extra | Inhalt | Rolle |
|-------|--------|--------|
| `rag` | chromadb | Runtime, Endnutzer-relevant |
| `agents` | *(leer)* | Platzhalter / Metapaket-Slice |
| `ops` | *(leer)* | intern/informativ |
| `qml` | *(leer)* | Qt-Quick-Pfad, oft nur PySide6-Basis |
| `governance` | *(leer)* | Monolith-Importe |
| `dev` | pytest, pytest-asyncio, pytest-qt | nur CI/Entwicklung |

## Bewusst kein eigenes Extra

- **workflows** — `PackagingExtraKind.LOGICAL_MARKER`, keine zusätzlichen PyPI-Zeilen; kein `[project.optional-dependencies.workflows]`.
- **core** — immer in `project.dependencies`, kein Extra.

## Lokale Installation

```bash
# Nur Basis (GUI-Shell-Pfad, ohne chromadb / ohne pytest)
pip install -e .

# Wie bisher übliches Entwickler-Setup (Basis + RAG + Tests)
pip install -e ".[rag,dev]"

# Mehrere Extras
pip install -e ".[rag,agents,dev]"
```

`requirements.txt` enthält `-e .[rag,dev]` und verweist auf dieses Manifest.

## CI

- Workflows nutzen `pip install -e ".[rag,dev]"` bzw. im Edition-Smoke-Job `pip install -e ".[${{ matrix.pip_extras }}]"` (Werte aus `tools/ci/release_matrix_ci.py`, abgeleitet aus der Release-Matrix).
- `tools/ci/release_matrix_ci.py validate` prüft Release-Matrix **und** `validate_pep621_pyproject_alignment`.

## Hybrid / Grenzen

- Keine pro-Edition-Wheels und kein schlankes „nur minimal ohne deepdiff“-Produktartefakt — Editionen steuern weiter **Features**, nicht separate Basis-Wheels.
- Leere Extras dokumentieren reservierte Slices; später können Pakete ergänzt werden, ohne Extra-Namen zu ändern.

## Nächster Schritt

- Optional: `pypdf` o. Ä. als weiteres Extra aus Manifest heben.
- Schlankere „Minimal-Desktop“-Basis nur nach Architekturreview (viele Module setzen heute noch die volle Basis voraus).

## Verwandte Doku

- [DEPENDENCY_GROUPS_TO_EXTRAS.md](DEPENDENCY_GROUPS_TO_EXTRAS.md)
- [CI_EDITION_SMOKE_SKELETON.md](CI_EDITION_SMOKE_SKELETON.md)
- [EDITION_RELEASE_MATRIX.md](EDITION_RELEASE_MATRIX.md)
