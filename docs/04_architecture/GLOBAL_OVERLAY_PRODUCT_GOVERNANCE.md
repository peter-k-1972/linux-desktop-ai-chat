# Global Overlay — Produkt-Governance (Shortcuts, Launcher, Host-Status)

Dieses Dokument schließt QA-Minor-Findings zu **Semantik**, **Synchronisation** und **zentrale Produktannahmen** — keine neue Feature-Schicht.

## 1. Global Overlay: Produkt vs. GUI


| Begriff                                         | Zugehörigkeit                                                                                          |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Global Overlay** (Alt+Z / Alt+Shift+Z)        | **Produktfunktion** — installiert durch die Shell-Entrypoints nach laufender `QApplication`.           |
| **GuiCapabilities** (`app/gui_capabilities.py`) | Beschreibt Fähigkeiten **der gewählten GUI-Shell** (Chat, Theme-Switching, …).                         |
| **Entfernt:** `supports_global_overlay`         | War semantisch irreführend („GUI stellt Overlay bereit“). Das Overlay stellt **nicht** die GUI bereit. |


**Diagnostics:** Zeile „Global overlay (product)“ = `active (this session)` wenn `get_overlay_host()` gesetzt ist, sonst `not loaded` / `unavailable`.

## 2. Reservierte Overlay-Shortcuts

**Kanonical source:** `app/global_overlay/overlay_product_shortcuts.py`


| Logischer Name             | QKeySequence-String |
| -------------------------- | ------------------- |
| `toggle_system_overlay`    | `Alt+Z`             |
| `toggle_emergency_overlay` | `Alt+Shift+Z`       |


- `GlobalOverlayHost` und Overlay-Doku-Texte beziehen die Sequenzen **nur** aus diesem Modul (keine verstreuten Literale im Host).
- **Konfliktprüfung:** `assert_reserved_overlay_sequences_are_unique()` (Tests) stellt sicher, dass die Registry keine Duplikate enthält. Eine vollständige App-weite Shortcut-Kollisionsmatrix ist **nicht** Ziel dieser Phase — weitere Shortcuts sollten künftig dieselbe zentrale Liste erweitern oder dagegen geprüft werden.

## 3. Kanonischer GUI-Launcher (Recovery / Relaunch)

**Module:** `app/global_overlay/product_launcher.py`

- `**CANONICAL_GUI_LAUNCHER_SCRIPT`:** `run_gui_shell.py`
- `**resolve_canonical_gui_launcher_path()`:** `resolve_repo_root() / run_gui_shell.py` (absolut)
- **Nutzer:** `overlay_gui_port` (GUI-Switching, Snapshot „launcher missing“), `relaunch_via_run_gui_shell`

### Produktannahmen

- **Repo-Layout:** Die Repository-Wurzel (Verzeichnis, das `run_gui_shell.py` enthält) ist dieselbe wie `resolve_repo_root()` liefert.
- **Portable / CI:** Fehlt der Launcher, setzt `build_gui_overlay_snapshot` `gui_switching_available=False` mit klarem Grund — **kein** stiller Switch.
- **Manueller Retter:** Nutzer startet weiterhin explizit `python run_gui_shell.py` (siehe Betriebsdoku).

Ein konfigurierbarer Launcher-Pfad außerhalb des Repos ist **bewusst nicht** Teil dieser Härtungsphase.

## 4. Overlay-Host — `active_gui_id`

- `**GlobalOverlayHost.active_gui_id`:** Kontext für Ports, Dialoge und Diagnostics.
- `**install_global_overlay_host(..., active_gui_id=…)`:** Bei bereits installiertem Host wird `**set_active_gui_id`** aufgerufen — vermeidet eingefrorenen Zustand bei wiederholter Installation (Tests, zukünftige Orchestrierung).
- `**StandardOverlayDialog` / `EmergencyOverlayDialog`:** `set_active_gui_id` aktualisiert den Kontext und `refresh_content()`.

**Hinweis:** Nach „Reset preferred GUI“ ohne Relaunch kann die **gespeicherte** Präferenz von der **laufenden** Shell abweichen — das ist produktintentional; der Host spiegelt die **Shell-Installation**, nicht automatisch immer QSettings.

## Verwandte Dokumente

- [GLOBAL_OVERLAY_SLICE1_RUNTIME.md](GLOBAL_OVERLAY_SLICE1_RUNTIME.md)
- [GLOBAL_OVERLAY_SLICE3_GUI.md](GLOBAL_OVERLAY_SLICE3_GUI.md)
- [GUI_REGISTRY.md](../architecture/GUI_REGISTRY.md)

