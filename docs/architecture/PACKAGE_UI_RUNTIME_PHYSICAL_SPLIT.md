# Physischer Split `app.ui_runtime` (Variante B)

**Projekt:** Linux Desktop Chat  
**Status:** Umgesetzt (Welle 8) — eingebettete Distribution `linux-desktop-chat-ui-runtime`, Import **`app.ui_runtime`** unverändert.

## §0 Entscheidung

| Feld | Inhalt |
|------|--------|
| **Distribution** | `linux-desktop-chat-ui-runtime` (Repo-Root) |
| **Importpfad** | Unverändert **`app.ui_runtime`** und dokumentierte Submodule (siehe `test_ui_runtime_public_surface_guard.py`) |
| **Host** | Verzeichnis **`app/ui_runtime/`** entfernt; Namespace über Host-`app/__init__.py` (`extend_path`) + `file:./linux-desktop-chat-ui-runtime` in Host-`pyproject.toml` |
| **Abhängigkeiten (Wheel)** | `jsonschema`, `PySide6` — **keine** `file:`-Abhängigkeit auf `ui_contracts` im Wheel-`pyproject.toml` (pip/CWD); Host installiert `linux-desktop-chat-ui-contracts` separat |
| **Laufzeit** | Module importieren **`app.ui_contracts`**, **`app.core`**, **`app.ui_application`** — verfügbar über vollständige Host-/Monorepo-Installation; **`QmlRuntime`** findet das **`qml/`**-Verzeichnis über Elternpfade bis **`qml/AppRoot.qml`** (Monorepo-Wurzel, nicht nur Paketroot) |

**Dateipfade / veraltete Verweise:** Produktiver Python-Code zu **`app.ui_runtime`** liegt **ausschließlich** unter **`linux-desktop-chat-ui-runtime/src/app/ui_runtime/`** (nach Installation weiterhin Import **`app.ui_runtime`**). Im Host-Baum **`app/`** gibt es **kein** Verzeichnis **`ui_runtime/`** mehr. Dokumentation oder Tests, die noch **`app/ui_runtime/...`** als **Repo-Pfad unter `app/`** behaupten oder `APP_ROOT / "ui_runtime"` erwarten, sind **inkonsistent** — stattdessen Distribution-Pfad bzw. `app_ui_runtime_source_root()` (Guards) verwenden.

## Verweise

- Landkarte: [`PACKAGE_MAP.md`](PACKAGE_MAP.md)  
- Split-Plan: [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.7  
- Public-Surface-Guard: `tests/architecture/test_ui_runtime_public_surface_guard.py`
