# linux-desktop-chat-ui-themes

Embedded distribution: **builtin theme packs** (JSON manifests, QSS, layout maps). Import path remains **`app.ui_themes`** (namespace package merge with host `app`).

## Layout

- `src/app/ui_themes/__init__.py` — package marker
- `src/app/ui_themes/builtins/` — versioned theme directories (e.g. `light_default/`)

## Development

From monorepo root:

```bash
pip install -e ./linux-desktop-chat-ui-themes
```

## Validate manifest

```bash
python tools/validate_ui_theme_manifest.py \
  linux-desktop-chat-ui-themes/src/app/ui_themes/builtins/light_default/manifest.json
```

Canonical reference: `docs/architecture/PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md`.
