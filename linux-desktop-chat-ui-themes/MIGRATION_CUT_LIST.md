# MIGRATION_CUT_LIST — linux-desktop-chat-ui-themes

**Welle 7:** Host tree `app/ui_themes/` removed; canonical source is this distribution only.

## Sync

- Theme assets change only under `src/app/ui_themes/builtins/`.
- `app.ui_runtime.theme_registry.default_builtin_registry()` resolves `builtins/` via `import app.ui_themes` (not host `app/` layout).
