# MIGRATION_CUT_LIST — linux-desktop-chat-ui-runtime

**Welle 8:** Host tree `app/ui_runtime/` removed; canonical source is this distribution only.

## Consumers

- **`run_qml_shell.py`**, **`app/ui_application`**, tests under `tests/ui_runtime/`, etc. — unchanged import strings (`app.ui_runtime.*`).
