# linux-desktop-chat-infra

Embedded distribution: **EventBus / debug store**, **agent metrics**, **headless tools** (`app.debug`, `app.metrics`, `app.tools`). Namespace merges with host `app` via `pkgutil.extend_path`.

## Runtime notes

- **`app.metrics`** imports **`app.utils`** — install **`linux-desktop-chat-utils`** (or the full host product) alongside this wheel.
- **`app.debug.qa_cockpit_panel`** uses **PySide6**; the rest of `app.debug` is Qt-free aside from that module.

## Development (monorepo root)

```bash
pip install -e ./linux-desktop-chat-utils -e ./linux-desktop-chat-infra
pytest linux-desktop-chat-infra/tests -q
```

Canonical: [`docs/architecture/PACKAGE_INFRA_PHYSICAL_SPLIT.md`](../docs/architecture/PACKAGE_INFRA_PHYSICAL_SPLIT.md).
