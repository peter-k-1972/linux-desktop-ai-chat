# linux-desktop-chat-persistence

**Status: Physical split completed.**

This directory is the embedded distribution for `app.persistence`. The canonical Python sources now live in `linux-desktop-chat-persistence/src/app/persistence/`, and the former host tree `app/persistence/` has been removed.

**Python import path (Variante B):** `app.persistence` — unchanged, now provided from `src/app/persistence/` in this package.

**Runtime dependency:** This wheel declares **SQLAlchemy** (PEP 621 / PyPI); there is **no** redundant `file:` dependency on other monorepo wheels here.

Further planning and implementation context: [`docs/architecture/PACKAGE_PERSISTENCE_PHYSICAL_SPLIT.md`](../docs/architecture/PACKAGE_PERSISTENCE_PHYSICAL_SPLIT.md) and [`docs/architecture/ADR_PERSISTENCE_DB_ROOT_RESOLUTION.md`](../docs/architecture/ADR_PERSISTENCE_DB_ROOT_RESOLUTION.md).

## Local install (isolated development of the wheel)

```bash
cd linux-desktop-chat-persistence
python3 -m pip install -e ".[dev]"
python3 -c "import app.persistence; print('ok', app.persistence.__doc__[:40])"
python3 -m build
```

In the host installation, `app.persistence` is bound via the host `pyproject.toml` to this embedded distribution. For isolated wheel-only checks, use a dedicated virtual environment.
