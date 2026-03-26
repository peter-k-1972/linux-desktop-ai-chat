# Physischer Split `app.runtime` / `app.extensions` (Variante B)

**Projekt:** Linux Desktop Chat  
**Status:** Umgesetzt (Welle 10) — eingebettete Distribution `linux-desktop-chat-runtime`, Importe **`app.runtime`**, **`app.extensions`** unverändert.

## §0 Entscheidung

| Feld | Inhalt |
|------|--------|
| **Distribution** | `linux-desktop-chat-runtime` (Repo-Root) |
| **Importpfad** | Unverändert **`app.runtime.*`**, **`app.extensions`** (Public-Surface-Guard: `test_runtime_public_surface_guard.py`) |
| **Host** | Verzeichnisse **`app/runtime/`**, **`app/extensions/`** entfernt; Namespace über Host-`app/__init__.py` (`extend_path`) + `file:./linux-desktop-chat-runtime` |
| **Abhängigkeiten (Wheel)** | **`PySide6`** (Single-Instance-Lock, Shutdown); **keine** `file:`-Abhängigkeit auf `linux-desktop-chat-infra` — Shutdown importiert `app.metrics` / `app.services` lazy (vollständiger Host) |
| **Laufzeit** | Produkt-Host bindet Infra + Runtime + Services |

## Verweise

- Landkarte: [`PACKAGE_MAP.md`](PACKAGE_MAP.md)  
- Split-Plan: [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md)  
- Public-Surface-Guard: `tests/architecture/test_runtime_public_surface_guard.py`
