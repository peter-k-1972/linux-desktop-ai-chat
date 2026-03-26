# Physischer Split `app.ui_themes` (Variante B)

**Projekt:** Linux Desktop Chat  
**Status:** Umgesetzt (Welle 7) — eingebettete Distribution `linux-desktop-chat-ui-themes`, Import **`app.ui_themes`** unverändert.

## §0 Entscheidung

| Feld | Inhalt |
|------|--------|
| **Distribution** | `linux-desktop-chat-ui-themes` (Repo-Root) |
| **Importpfad** | `app.ui_themes` — nur `__init__.py`; Assets unter `builtins/**` (package-data) |
| **Host** | Verzeichnis **`app/ui_themes/`** entfernt; Namespace über Host-`app/__init__.py` (`extend_path`) + `file:./linux-desktop-chat-ui-themes` in Host-`pyproject.toml` |
| **Runtime-Anker** | `app.ui_runtime.theme_registry.default_builtin_registry()` lädt `builtins/` über `Path(app.ui_themes.__file__).parent` |
| **Abhängigkeiten** | Keine Python-Abhängigkeiten (reine Assets + Paketmarker) |

## Verweise

- Landkarte: [`PACKAGE_MAP.md`](PACKAGE_MAP.md)  
- Split-Plan: [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.6  
- Public-Surface-Guard: `tests/architecture/test_ui_themes_public_surface_guard.py`
