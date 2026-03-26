# MIGRATION_CUT_LIST — linux-desktop-chat-utils

## Nach Host-Cut (Welle 6)

- Host-Tree **`app/utils/`** entfernt; kanonische Quelle nur noch `linux-desktop-chat-utils/src/app/utils/`.
- **`linux-desktop-chat-providers`**: vormals gespiegeltes `src/app/utils/env_loader.py` entfernt; Laufzeit-Import **`app.utils`** — Installation siehe Host-`pyproject.toml` bzw. [`linux-desktop-chat-providers/README.md`](../linux-desktop-chat-providers/README.md) (kein `file:`-Eintrag in Provider-`pyproject.toml`, pip/CWD).

## Abgleich bei Änderungen an `app.utils.*`

- Öffentliche Oberfläche: `tests/architecture/test_utils_public_surface_guard.py` im Host-Repo.
