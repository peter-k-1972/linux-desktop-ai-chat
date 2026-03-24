# GUI Launch Watchdog & Auto Safe Mode

## Role

The watchdog is a **product function**: it observes GUI launch outcomes (from launcher entrypoints), persists a short failure history in **QSettings**, and may schedule **one-shot Safe Mode** for the next process start. It does **not** repair GUIs or load themes.

## Heuristic

| Parameter | Value |
|-----------|--------|
| Failure threshold | **3** failed launches |
| Rolling window | **10 seconds** (wall-clock `time.time()`) |

Each failure appends a timestamp; entries older than the window are dropped. If, after recording a failure, the list length is ≥ threshold, the watchdog:

1. Sets `safe_mode_next_launch` (existing one-shot key in `gui_bootstrap`).
2. Sets `safe_mode_watchdog_banner` so the overlay can show the recovery message until cleared.

## Persisted keys (QSettings)

| Key | Meaning |
|-----|---------|
| `watchdog_failure_times_json` | JSON array of Unix timestamps for failures in the window |
| `watchdog_last_gui_start_unix` | Last `note_gui_launch_attempt()` time |
| `watchdog_gui_start_attempts` | Monotonic attempt counter (reset on successful launch) |
| `watchdog_last_successful_start_unix` | Last successful GUI completion |
| `safe_mode_next_launch` | One-shot safe boot (existing) |
| `safe_mode_watchdog_banner` | Show “repeated GUI failures” overlay hint until cleared |

## Launch integration

| Location | Calls |
|----------|--------|
| `run_gui_shell.py` `main()` | `note_gui_launch_attempt()` after argument parse |
| `run_gui_shell.py` `_try_start_qt_quick_gui` | `note_failed_gui_launch()` on validation / missing entrypoint / non-zero subprocess |
| `run_qml_shell.py` `main()` | `note_gui_launch_attempt()` early; `note_failed_gui_launch()` on manifest or runtime activation failure |
| `run_gui_shell.py` `_run_widget_gui` / `run_qml_shell.py` | `note_successful_gui_launch()` after overlay host install (existing pattern) |

## Safe Mode behaviour

When `consume_safe_mode_next_launch()` returns true at the start of `run_gui_shell.py` (existing logic):

- Preferred GUI reset to `default_widget_gui` unless `--gui` is present on the command line.
- Theme reset to product default unless `--theme` is present.

The **watchdog banner** remains set until:

- **Disable Safe Mode** in the standard or emergency overlay (`rescue_disable_safe_mode_watchdog`), or  
- A **successful GUI switch** via `apply_gui_switch_via_product` (clears banner before relaunch).

Successful GUI completion calls `note_successful_gui_launch()`, which clears failure timestamps and attempt counters but **does not** clear the watchdog banner (user acknowledgement / switch).

## Fail-closed on corruption

Invalid `watchdog_failure_times_json` is treated as **no failures** (empty list). Reads and writes are wrapped so corrupt data does not crash the product; spurious Safe Mode from garbage data is avoided.

## Recovery workflow

1. Repeated failures → next start in Safe Mode (default GUI/theme) + banner.  
2. User stabilises (default widget), reads diagnostics, optionally switches GUI again.  
3. User clears state with **Disable Safe Mode** or switches GUI via the product relaunch path.

## Tests

See `tests/global_overlay/test_gui_watchdog_safe_mode.py`.

## Possible improvements

- Per-`gui_id` failure buckets.  
- Metrics export for operations.  
- Configurable threshold/window via settings (governance).
