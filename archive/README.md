# Archive – Deprecated and Legacy Code

This directory contains deprecated code that has been moved out of the active codebase.

**Do not import from archive.** These files are kept for reference only.

## Contents

| File/Directory | Deprecated | Replacement |
|----------------|------------|--------------|
| `run_legacy_gui.py` | 2026-03-16 | `main.py` → `run_gui_shell` (new GUI Shell) |

## Restoring Legacy GUI

To run the legacy GUI for reference:

```bash
python archive/run_legacy_gui.py
```

Note: This requires `app.main` to remain in the codebase (it is still present for now).
