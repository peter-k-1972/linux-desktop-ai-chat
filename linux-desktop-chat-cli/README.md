# linux-desktop-chat-cli

**Distribution:** kopflose Kontext-CLI (`app.cli`, Variante B). **Commit 1:** eingebettete Vorlage; Host-`pyproject` bleibt unverändert, Host-Cut folgt später.

**Laufzeit:** Module importieren `app.context.replay.*` — nur sinnvoll mit installiertem Host `linux-desktop-chat`.

## Abhängigkeit vom Host

Die Module unter `app.cli.*` importieren **`app.context.replay.*`**. Ein isoliertes `pip install -e .` **ohne** den Host `linux-desktop-chat` liefert keine lauffähigen CLI-Läufe. Für Entwicklung: Host-Repo mit vollständiger Installation; die Tests in diesem Paket prüfen nur **Paketlayout** (ohne Domänen-Import).

## Struktur

- `src/app/__init__.py` — Namespace-Markierung
- `src/app/cli/` — Kontext-Replay/Repro/Registry-CLIs
- `MIGRATION_CUT_LIST.md` — Cut-/Sync-Checkliste (Host ↔ Vorlage)
- `tests/test_imports.py` — Paketmarker + erwartete Module auf der Platte
- `tests/test_basic_runtime.py` — `run_*`-Smoke **nur**, wenn `app.context` installiert ist (sonst Skip)

## Installation (Entwicklung, isoliert — nur Layout-Tests)

```bash
cd linux-desktop-chat-cli
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest
```

## Build (Wheel / sdist)

Benötigt das Paket **`build`** (nicht in `[project.optional-dependencies].dev`):

```bash
.venv/bin/pip install build
.venv/bin/python -m build
```

Artefakte unter `dist/` (in `.gitignore`).

## Dokumentation (kanonisch im Host-Repo)

- Technische Readiness: `docs/architecture/PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`
- Wellenkontext: `docs/architecture/PACKAGE_WAVE5_CLI_DECISION_MEMO.md`, `docs/architecture/PACKAGE_SPLIT_PLAN.md` §6.4
