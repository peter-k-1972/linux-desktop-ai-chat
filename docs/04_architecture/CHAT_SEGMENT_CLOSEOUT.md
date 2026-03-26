# Chat-Segment — Architekturabschluss (Qt-freie Stream-Domain)

Kurzreferenz nach der Chat-Segmentierungswelle; keine neue Pipeline.

## Kanonische Schicht

- Stream-Parsing, Akkumulator, Finalisierung, zentrale Consume-Orchestrierung: **`app/chat/`** (keine Imports von `app.gui`, `app.ui_application`, PySide; Guard: `tests/architecture/test_chat_domain_governance_guards.py`).
- Eine Streaming-Pipeline: **`consume_chat_model_stream`**; weder Presenter noch Workspace führen eigene Chunk-Schleifen.

## Sendeinstieg GUI

- **Standard:** `ChatWorkspace` -> `SendMessageCommand` -> **`ChatPresenter.run_send_async`** (Contract-Patches, optional **Project Butler**).
- **Deprecated:** `LINUX_DESKTOP_CHAT_LEGACY_CHAT_SEND=1` -> **`ChatWorkspace._run_send_legacy`**: gleicher Port und Consume, aber **ohne** Butler und **ohne** Streaming-`ChatStatePatch` am Workspace-State. Nur fuer Diagnostik; Entfernung in einer spaeteren Version moeglich.

## Butler

- Butler laeuft nur im Presenter-Pfad. Legacy-Send umgeht ihn weiterhin (siehe `docs/FEATURES/agents.md`). Statt Legacy: Standardpfad + `LINUX_DESKTOP_CHAT_DISABLE_BUTLER=1`, wenn Butler komplett abgeschaltet werden soll.

## Absichtlich ausserhalb dieser Notiz

- Globale Port-DI, `cancel_generation` (No-Op), QML-Shell, andere Workspaces.
