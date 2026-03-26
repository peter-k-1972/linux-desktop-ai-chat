# linux-desktop-chat-utils

**Distribution:** gemeinsame Hilfsmodule (`app.utils`, Variante B). Eingebettete Vorlage im Monorepo; Host `pyproject.toml` bindet `file:./linux-desktop-chat-utils`.

**Inhalt:** Projekt-Pfad-Auflösung (`paths`), Datetime-Helfer (`datetime_utils`), einmaliges `.env`-Laden (`env_loader`). Nur Stdlib in diesen Modulen.

## Projektroot

`get_project_root()` nutzt optional `LDC_REPO_ROOT` (CI), sonst die erste Elternverzeichnis-Kette, die `linux-desktop-chat-features/` als Geschwister enthält (Monorepo-Marker), sonst den Legacy-Dreisprung aus `app/utils/paths.py`.

## Installation (Entwicklung)

```bash
cd linux-desktop-chat-utils
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest
```

## Dokumentation (kanonisch im Host-Repo)

- [`docs/architecture/PACKAGE_MAP.md`](../docs/architecture/PACKAGE_MAP.md)
- [`docs/architecture/PACKAGE_SPLIT_PLAN.md`](../docs/architecture/PACKAGE_SPLIT_PLAN.md)
- [`docs/architecture/PACKAGE_UTILS_PHYSICAL_SPLIT.md`](../docs/architecture/PACKAGE_UTILS_PHYSICAL_SPLIT.md)
