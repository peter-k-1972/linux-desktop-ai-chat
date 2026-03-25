# linux-desktop-chat-features

Eigenständige **Distribution** für die Feature-Plattform **Linux Desktop Chat** (Importpfad bleibt **`app.features`** — Variante B).

Dieses Verzeichnis ist die **Commit-1-Repo-Vorlage**: vollständiger Quellbaum unter `src/app/features/`. Es ist absichtlich noch im Host-Monorepo eingebettet, bis das Verzeichnis als eigenes Git-Repository ausgecheckt oder per `git subtree split` ausgelagert wird.

## Struktur

- `src/app/__init__.py` — minimales Paketmarken-Modul (nur `app`, nicht der gesamte Host-`app`-Baum)
- `src/app/features/` — Feature-Plattform (Deskriptoren, Registry, Editionen, Release-Matrix, …)
- `tests/unit/` — Teilmenge der Host-Unit-Tests ohne Abhängigkeit von `app.gui`

## Installation (Entwicklung)

Empfohlen mit virtueller Umgebung (PEP 668):

```bash
cd linux-desktop-chat-features
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest
```

## Build (Wheel / sdist)

```bash
.venv/bin/pip install build
.venv/bin/python -m build
```

Artefakte liegen unter `dist/` (in `.gitignore`).

## Dokumentation (kanonisch im Host-Repo)

- API & DoR: `docs/architecture/PACKAGE_FEATURES_CUT_READY.md`
- Physischer Split & Execution Plan: `docs/architecture/PACKAGE_FEATURES_PHYSICAL_SPLIT.md`
- Cut-Liste (Dateien / Tests): `MIGRATION_CUT_LIST.md` (in diesem Verzeichnis)

## Hinweis

- **Kein** eigener `[project.entry-points."linux_desktop_chat.features"]` hier nötig — externe Plugins deklarieren ihre Entry Points weiterhin in **ihren** `pyproject.toml`.
- PEP-621-Drift gegen den **vollständigen Host**-`pyproject.toml` bleibt Aufgabe des Host-Repos (`tools/ci/release_matrix_ci.py`).
