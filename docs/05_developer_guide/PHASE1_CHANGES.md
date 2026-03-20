# Phase 1 — Repository Cleanup (Completed)

**Date:** 2026-03-16

## Summary

- Created target directory structure
- Moved legacy entry point to archive
- Consolidated assets into `assets/`
- main.py now delegates via `run_gui_shell`

## Changes

### Directories Created

| Directory | Purpose |
|-----------|---------|
| `src/` | (bereinigt 2026-03-16: main.py delegiert direkt an run_gui_shell) |
| `help/` | Help content (single source of truth) |
| `assets/` | Icons, themes, media |
| `assets/icons/` | SVG icons (svg/ + legacy flat icons) |
| `assets/themes/` | QSS themes (base/, legacy/) |
| `assets/media/` | Media files |
| `tools/` | Dev tooling |
| `archive/` | Deprecated code |

### Files Moved

| From | To |
|------|-----|
| `run_legacy_gui.py` | `archive/run_legacy_gui.py` |

### Assets Consolidated

| Source | Destination |
|--------|-------------|
| `app/gui/icons/svg/*` | `assets/icons/svg/` |
| `app/resources/icons/*.svg` | `assets/icons/` |
| `app/gui/themes/base/*.qss` | `assets/themes/base/` |
| `app/resources/light.qss`, `dark.qss` | `assets/themes/legacy/` |

**Note:** Original files in `app/` remain for now. Code reads from `assets/`. Remove originals in a later cleanup.

### Code Updates

| File | Change |
|------|--------|
| `app/utils/paths.py` | New: `get_project_root()`, `get_assets_dir()`, `get_icons_dir()`, `get_themes_dir()` |
| `app/gui/icons/manager.py` | `_icons_base_path()` → `get_icons_dir() / "svg"` |
| `app/gui/themes/loader.py` | QSS paths → `get_themes_dir() / "base"` |
| `app/settings.py` | Default `icons_path` → `"assets/icons"` |
| `app/chat_widget.py` | Fallback `icons_path` → `"assets/icons"` |
| `main.py` | Delegates to `run_gui_shell.main` |

### Backwards Compatibility

- `run_gui_shell.py` unchanged; still runnable directly
- Legacy GUI: `python archive/run_legacy_gui.py`
- Existing `icons_path` in QSettings preserved; new installs use `assets/icons`
