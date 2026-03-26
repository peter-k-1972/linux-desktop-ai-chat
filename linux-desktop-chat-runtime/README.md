# linux-desktop-chat-runtime

Embedded distribution: **product lifecycle** (`app.runtime`) and **optional extensions root** (`app.extensions`). Namespace merges with host `app` via `pkgutil.extend_path`.

## Runtime notes

- **`app.runtime.lifecycle`** calls **`app.metrics`** and **`app.services`** during shutdown — install the full host product (or at least **`linux-desktop-chat-infra`** + host `app/services`) alongside this wheel.
- **`model_invocation`** is stdlib-only; **`lifecycle`** needs **PySide6** for single-instance lock and shutdown orchestration.

## Development (monorepo root)

```bash
pip install -e ./linux-desktop-chat-runtime
pytest linux-desktop-chat-runtime/tests -q
```

Canonical: [`docs/architecture/PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](../docs/architecture/PACKAGE_RUNTIME_PHYSICAL_SPLIT.md).
