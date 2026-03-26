# Physischer Split `app.debug` / `app.metrics` / `app.tools` (Variante B)

**Projekt:** Linux Desktop Chat  
**Status:** Umgesetzt (Welle 9) — eingebettete Distribution `linux-desktop-chat-infra`, Importe **`app.debug`**, **`app.metrics`**, **`app.tools`** unverändert.

## §0 Entscheidung

| Feld | Inhalt |
|------|--------|
| **Distribution** | `linux-desktop-chat-infra` (Repo-Root) |
| **Importpfad** | Unverändert **`app.debug.*`**, **`app.metrics.*`**, **`app.tools.*`** (Public-Surface-Guard: `test_infra_public_surface_guard.py`) |
| **Host** | Verzeichnisse **`app/debug/`**, **`app/metrics/`**, **`app/tools/`** entfernt; Namespace über Host-`app/__init__.py` (`extend_path`) + `file:./linux-desktop-chat-infra` |
| **Abhängigkeiten (Wheel)** | **`PySide6`** (QA-Cockpit unter `app.debug`); **keine** `file:`-Abhängigkeit auf `linux-desktop-chat-utils` (pip/CWD) — Metriken brauchen utils zur Laufzeit |
| **Laufzeit** | `app.metrics` → `app.utils`; Produkt-Host bindet utils + infra |

## Verweise

- Landkarte: [`PACKAGE_MAP.md`](PACKAGE_MAP.md)  
- Split-Plan: [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md)  
- Public-Surface-Guard: `tests/architecture/test_infra_public_surface_guard.py`
