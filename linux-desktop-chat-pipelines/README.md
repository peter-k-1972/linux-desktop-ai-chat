# linux-desktop-chat-pipelines

Eigenständige **Distribution** für die Pipeline-Engine **Linux Desktop Chat** (Importpfad bleibt **`app.pipelines`** — Variante B).

Dieses Verzeichnis ist die **Commit-1-Repo-Vorlage**: vollständiger Quellbaum unter `src/app/pipelines/`, eingebettet im Host-Monorepo. Auslagerung als eigenes Git-Repository erfolgt später.

## Struktur

- `src/app/__init__.py` — minimales Paketmarken-Modul
- `src/app/pipelines/` — Engine, Modelle, Executors, Services, Registry
- `tests/unit/` — isolierte Unit-Tests ohne Host (`app.services`, `app.workflows`, …)

## Installation (Entwicklung)

```bash
cd linux-desktop-chat-pipelines
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest
```

## Build (Wheel / sdist)

```bash
.venv/bin/python -m build
```

Artefakte unter `dist/` (in `.gitignore`).

## Dokumentation (kanonisch im Host-Repo)

- Split-Readiness: `docs/architecture/PACKAGE_PIPELINES_SPLIT_READY.md`
- DoR: `docs/architecture/PACKAGE_PIPELINES_CUT_READY.md`
- Physischer Split & Execution: `docs/architecture/PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`
- Cut-Liste (Dateien / Tests): `MIGRATION_CUT_LIST.md` (in diesem Verzeichnis)

## Hinweis

Der Host-Monorepo hat **kein** `app/pipelines/` mehr (Commit 2); kanonische Produktquelle für `app.pipelines` ist diese Vorlage bzw. die installierte Distribution. Historische Sync-Regeln: `MIGRATION_CUT_LIST.md` §5.
