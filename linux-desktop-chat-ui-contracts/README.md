# linux-desktop-chat-ui-contracts

Eingebettete **Commit-1-Vorlage** im Monorepo „Linux Desktop Chat“ — Distribution `linux-desktop-chat-ui-contracts`, Python-Import **`app.ui_contracts`** (Variante B, analog zu `linux-desktop-chat-features`).

## Inhalt

- `src/app/ui_contracts/` — Qt-freie UI-Verträge (DTOs, Commands, States, Enums, Events)
- Minimale Tests unter `tests/unit/` (Smoke, ohne Host/`app.gui`)

Öffentliche API und SemVer-Zonen: Host-Doku [`docs/architecture/PACKAGE_UI_CONTRACTS_SPLIT_READY.md`](../docs/architecture/PACKAGE_UI_CONTRACTS_SPLIT_READY.md), Cut-Ready: [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](../docs/architecture/PACKAGE_UI_CONTRACTS_CUT_READY.md).

## Entwicklung

```bash
cd linux-desktop-chat-ui-contracts
python3 -m venv .venv && . .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e ".[dev]"
pytest
python3 -m build
python3 -c "from app.ui_contracts import ChatWorkspaceState, SettingsErrorInfo; print('ok')"
```

## Sync mit dem Host

Nach **Commit 2** im Monorepo ist die kanonische Quelle **diese Vorlage**; der Host-Tree enthält kein `app/ui_contracts/` mehr. Änderungen nur hier (oder im späteren eigenen Contracts-Repo), dann Host neu installieren — siehe [`MIGRATION_CUT_LIST.md`](MIGRATION_CUT_LIST.md) und [`docs/architecture/PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](../docs/architecture/PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md).

## Status

Commits 1–4 im Monorepo (Vorlage, Host-Cut, CI, Welle-2-Abschluss) — siehe [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](../docs/architecture/PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md).
