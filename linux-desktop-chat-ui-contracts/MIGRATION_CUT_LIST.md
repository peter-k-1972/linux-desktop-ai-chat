# Cut-Liste: `linux-desktop-chat-ui-contracts` (Commit 1 → späterer Host-Cut)

**Stand:** Eingebettete Vorlage im Host-Monorepo unter `linux-desktop-chat-ui-contracts/`. Nach Host-Cut: Host pinnt `linux-desktop-chat-ui-contracts>=…`; Quelle `app/ui_contracts` nur noch aus dem Wheel (Host-Ordner entfernt).

---

## 1. 1:1 aus Host `app/ui_contracts/` → `src/app/ui_contracts/`

Alle `.py`-Dateien des Host-Baums — **ohne Importpfad-Änderung** (weiter `app.ui_contracts.*` intern).

**Repo-spezifisch zusätzlich:** `src/app/__init__.py` (Paketmarker), nicht aus dem Host kopiert.

---

## 2. Dokumentation

| Mit in dieser Vorlage | Primär im Host |
|------------------------|----------------|
| `README.md`, diese Datei, `pyproject.toml` | `docs/architecture/PACKAGE_UI_CONTRACTS_*.md`, `PACKAGE_MAP.md`, `PACKAGE_SPLIT_PLAN.md` |

---

## 3. Tests

### In dieser Vorlage (`tests/unit/`) — minimale isolierte Suite

| Datei | Inhalt |
|-------|--------|
| `test_package_exports.py` | Smoke: Root-API (`app.ui_contracts`) |
| `test_workspace_import_smoke.py` | Stichprobe `workspaces.*` |

### Nur im Host

- `tests/architecture/test_ui_layer_guardrails.py` (bis `find_spec`-Migration)
- `tests/architecture/test_ui_contracts_public_surface_guard.py`
- Alle `tests/contracts/test_*`, die `app.ui_contracts` nutzen
- `tests/unit/gui/`, `tests/unit/ui_application/`, `tests/smoke/`, `tests/qml_chat/`, `tests/global_overlay/`, … mit `ui_contracts`-Bezug

---

## 4. Nicht mitwandern (Commit 1)

- `app/gui/**`, `app/ui_application/**`, Host-`pyproject.toml`, CI-Workflows
- Architektur-Guards (bis späterer Anpassung)

---

## 5. Sync-Hinweis (Monorepo nach Commit 2)

Kanonische Quelle ist **`linux-desktop-chat-ui-contracts/src/app/ui_contracts/`**; der Host hat kein paralleles `app/ui_contracts/` mehr. Nach Änderungen: `pip install -e ./linux-desktop-chat-ui-contracts` (oder Host `pip install -e .`) erneut ausführen.
