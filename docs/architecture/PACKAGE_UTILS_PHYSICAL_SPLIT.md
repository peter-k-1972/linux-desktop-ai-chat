# Physischer Split `app.utils` (Variante B)

**Projekt:** Linux Desktop Chat  
**Status:** Umgesetzt (Welle 6) — eingebettete Distribution `linux-desktop-chat-utils`, Import **`app.utils`** unverändert.

## §0 Entscheidung

| Feld | Inhalt |
|------|--------|
| **Distribution** | `linux-desktop-chat-utils` (Repo-Root) |
| **Importpfad** | `app.utils`, Submodule `app.utils.paths`, `app.utils.datetime_utils`, `app.utils.env_loader` |
| **Host** | Verzeichnis **`app/utils/`** entfernt; Namespace über Host-`app/__init__.py` (`extend_path`) + `file:./linux-desktop-chat-utils` in Host-`pyproject.toml` |
| **Abhängigkeiten** | Stdlib-only; **Consumer** `linux-desktop-chat-providers` importiert `app.utils` (Spiegel entfernt). PEP-508-`file:`-Abhängigkeit **nicht** in Provider-`pyproject.toml` (pip/CWD); Host listet `linux-desktop-chat-utils` und `linux-desktop-chat-providers` getrennt — siehe [`linux-desktop-chat-providers/README.md`](../../linux-desktop-chat-providers/README.md). |

## Verweise

- Landkarte: [`PACKAGE_MAP.md`](PACKAGE_MAP.md)  
- Split-Plan: [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md)  
- Public-Surface-Guard: `tests/architecture/test_utils_public_surface_guard.py`
