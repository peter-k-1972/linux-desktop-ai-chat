# Global Overlay — Slice 5: Diagnostics & Polish

## Purpose

The product-wide overlay (`Alt+Z` / `Alt+Shift+Z`) remains a **product layer** above all GUIs: it must not embed domain or theme-engine logic. Slice 5 adds **read-only diagnostics**, **compatibility hints**, and **interaction/visual polish** without a debug console or secrets.

## Diagnostics data (read-only)

Collected in `app/global_overlay/overlay_diagnostics.py` via `collect_overlay_diagnostics(active_gui_id)` and rendered as Rich HTML in `StandardOverlayDialog`.

| Area | Content |
|------|---------|
| Versions | `APP_RELEASE_VERSION`, `BACKEND_BUNDLE_VERSION`, `UI_CONTRACTS_RELEASE_VERSION`, `BRIDGE_INTERFACE_VERSION` from `app.application_release_info` |
| Runtime | Active `gui_id`, current theme/style hint (via existing overlay status paths), registry fallback GUI, safe-mode-next-launch flag (`QSettings`, best-effort → `unavailable`) |
| Manifest | For `library_qml_gui`: short line from `qml/theme_manifest.json` + runtime allow-list check; for widget GUI: explicit *not applicable* (no QML manifest) |
| Compatibility | GUI definition check via `validate_gui_switch_target` (registry, entrypoint, QML rules); QML manifest/runtime lists when the active GUI is QML |
| Product actions | Theme switching support and GUI switching support mirror `overlay_theme_port` / `overlay_gui_port` snapshots (reasons may appear, truncated, HTML-escaped) |
| Capabilities | Rows from `GuiCapabilities` for the **active** GUI (`get_capabilities_for_gui_id`): chat, projects, workflows, prompts, agents, deployment, settings, theme switching, global overlay |

### Why read-only

Diagnostics are **display-only**: no log tail, no tokens, no editable fields. That keeps the overlay safe for support contexts and avoids turning it into a second settings surface.

## Focus & shortcuts

| Input | Behaviour |
|-------|-----------|
| `Alt+Z` | Toggle standard overlay (`GlobalOverlayHost`) |
| `Alt+Shift+Z` | Toggle emergency overlay; opening one surface closes the other |
| `Esc` | `reject()` on both dialogs (explicit handler; consistent close) |
| Tab order | Standard: GUI combo → switch/revert → theme combo → apply → rescue row → Close. Emergency: rescue stack → Quit → Close |
| Initial focus | Standard: first enabled GUI combo, else theme combo, else Close. Emergency: Revert if enabled, else Close |

## Visual polish vs. theme

Overlay dialogs use **fixed neutral QSS** on dialog object names (`LdcStandardOverlay`, `LdcEmergencyOverlay`): light gray backgrounds, simple borders, blue (standard) or red-accent (emergency) **focus** borders. They do **not** read `ThemeManager` or QML tokens, so the overlay stays readable even when the active GUI’s theme fails.

## Tests

See `tests/global_overlay/test_overlay_slice5_diagnostics.py` (diagnostics aggregation, capability rows, `Esc`, host mutual exclusion, smoke).

## Watchdog / Safe Mode (follow-up slice)

Diagnostics also show **Safe mode (status)** and **Watchdog failures (10s window)** when the GUI launch watchdog is active. See [GLOBAL_OVERLAY_GUI_WATCHDOG_SAFE_MODE.md](GLOBAL_OVERLAY_GUI_WATCHDOG_SAFE_MODE.md).

**Global overlay (product):** read-only line reflecting whether `GlobalOverlayHost` is installed in this session (not a GUI capability). See [GLOBAL_OVERLAY_PRODUCT_GOVERNANCE.md](GLOBAL_OVERLAY_PRODUCT_GOVERNANCE.md).
