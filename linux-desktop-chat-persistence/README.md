# linux-desktop-chat-persistence

**Status: Scaffold only — no physical cut yet.**

This directory is the **wheel skeleton** for the future embedded distribution `linux-desktop-chat-persistence`. The **canonical Python sources for `app.persistence` still live in the host tree** (`app/persistence/` at the monorepo root). Nothing has been moved or deleted on the host.

**Python import path (target, Variante B):** `app.persistence` — same namespace segment as today, via `src/app/persistence/` in this package once the cut is performed.

**Runtime dependency:** This wheel declares **SQLAlchemy** (PEP 621 / PyPI); there is **no** redundant `file:` dependency on other monorepo wheels here.

Further planning context: [`docs/architecture/PACKAGE_PERSISTENCE_PHYSICAL_SPLIT.md`](../docs/architecture/PACKAGE_PERSISTENCE_PHYSICAL_SPLIT.md) and [`docs/architecture/ADR_PERSISTENCE_DB_ROOT_RESOLUTION.md`](../docs/architecture/ADR_PERSISTENCE_DB_ROOT_RESOLUTION.md).

## Local install (isolated development of the wheel)

```bash
cd linux-desktop-chat-persistence
python3 -m pip install -e ".[dev]"
python3 -c "import app.persistence; print('ok', app.persistence.__doc__[:40])"
python3 -m build
```

Until the physical split, the host application should keep using **`app/persistence` from the host tree**; installing this scaffold in the same environment as the full host would duplicate the `app.persistence` package — use isolated venvs for wheel-only checks.
