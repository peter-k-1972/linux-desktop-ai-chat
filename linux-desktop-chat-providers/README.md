# linux-desktop-chat-providers

Eigenständige **Distribution** für die Ollama-Chat-Provider **Linux Desktop Chat** (Importpfad bleibt **`app.providers`** — Variante B).

Dieses Verzeichnis ist die **Commit-1-Repo-Vorlage**: vollständiger Quellbaum unter `src/app/providers/`, eingebettet im Host-Monorepo. Auslagerung als eigenes Git-Repository erfolgt später.

## Struktur

- `src/app/__init__.py` — minimales Paketmarken-Modul
- `src/app/providers/` — `OllamaClient`, Local/Cloud-Provider, Factory
- **`app.utils`** — aus Distribution **`linux-desktop-chat-utils`** (kein Spiegel unter diesem Baum); siehe `MIGRATION_CUT_LIST.md`
- `tests/` — minimale isolierte Tests ohne Host

## Installation (Entwicklung)

**Monorepo-Root** (zwei editables; `app.utils` liegt im Geschwisterpaket):

```bash
cd /path/to/Linux-Desktop-Chat
python3 -m venv .venv
.venv/bin/pip install -e ./linux-desktop-chat-utils -e "./linux-desktop-chat-providers[dev]"
.venv/bin/python -m pytest linux-desktop-chat-providers/tests
```

**Nur im Providers-Ordner** (Geschwister-`utils` per relativem Pfad):

```bash
cd linux-desktop-chat-providers
python3 -m venv .venv
.venv/bin/pip install -e ../linux-desktop-chat-utils -e ".[dev]"
.venv/bin/python -m pytest
```

## Build (Wheel / sdist)

```bash
.venv/bin/python -m build
```

Artefakte unter `dist/` (in `.gitignore`).

## Dokumentation (kanonisch im Host-Repo)

- Split-Readiness: `docs/architecture/PACKAGE_PROVIDERS_SPLIT_READY.md`
- Cut-Ready: `docs/architecture/PACKAGE_PROVIDERS_CUT_READY.md`
- Physischer Split & Execution: `docs/architecture/PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`
- Cut-Liste: `MIGRATION_CUT_LIST.md` (in diesem Verzeichnis)

## Hinweis

Nach **Commit 2 (Host-Cut)** ist **`app/providers/`** im Host **entfernt**; kanonische Quelle ist diese Vorlage bzw. die installierte Distribution (`linux-desktop-chat-providers` als `file:`-Abhängigkeit des Hosts). Historische Sync-Disziplin: `MIGRATION_CUT_LIST.md` §5.
