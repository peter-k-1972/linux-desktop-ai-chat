# linux-desktop-chat-ui-runtime

Embedded distribution: **theme manifest handling, QML runtime, shell bridge, chat QML viewmodel** (`app.ui_runtime`). Namespace merges with host `app` via `pkgutil.extend_path`.

## Runtime notes

- **`QmlRuntime`** resolves the product tree by walking parents of this package until it finds **`qml/AppRoot.qml`** (monorepo root or legacy layout). A wheel-only install without that tree cannot activate the shell.
- Imports **`app.ui_contracts`**, **`app.core.navigation.nav_areas`**, **`app.ui_application.*`** — these come from the **host** (or other embedded wheels) when the full product is installed; this wheel alone is not a standalone app distribution.
- Pair with **`linux-desktop-chat-ui-contracts`** (and **`linux-desktop-chat-ui-themes`**) for QML/theme smoke work.

## Development (monorepo root)

```bash
pip install -e ./linux-desktop-chat-ui-contracts -e ./linux-desktop-chat-ui-themes -e ./linux-desktop-chat-ui-runtime
pytest linux-desktop-chat-ui-runtime/tests -q
```

Canonical: [`docs/architecture/PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md`](../docs/architecture/PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md).
