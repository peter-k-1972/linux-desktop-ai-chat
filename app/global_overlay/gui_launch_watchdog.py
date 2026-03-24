"""
GUI-Launch-Watchdog: wiederholte Startfehler in kurzem Fenster → Auto-Safe-Mode (nächster Start).

Persistiert in QSettings (produktneutral, ohne Domänenlogik). Keine GUI-Reparatur —
nur Entscheidung: instabile Starts → ``safe_mode_next_launch`` + Hinweis-Banner.

Bei beschädigten Watchdog-Daten: fail-closed ohne Absturz (kein Auto-Safe-Mode aus Korruptem).
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Final

logger = logging.getLogger(__name__)

LAUNCH_FAILURE_THRESHOLD: Final[int] = 3
LAUNCH_FAILURE_WINDOW_SEC: Final[float] = 10.0

# QSettings-Schlüssel (Org/App wie gui_bootstrap)
_FAILURE_TIMES_JSON_KEY = "watchdog_failure_times_json"
_LAST_GUI_START_UNIX_KEY = "watchdog_last_gui_start_unix"
_GUI_START_ATTEMPTS_KEY = "watchdog_gui_start_attempts"
_LAST_SUCCESS_UNIX_KEY = "watchdog_last_successful_start_unix"


@dataclass
class GuiLaunchWatchdogState:
    """Laufzeitspiegel (Tests / Telemetrie); Schwelle liegt in Persistenz."""

    session_started_monotonic: float = field(default_factory=time.monotonic)
    last_gui_launch_monotonic: float | None = None
    consecutive_gui_launch_failures: int = 0
    successful_launch_count: int = 0


_state = GuiLaunchWatchdogState()


def _qsettings():
    from app.gui_bootstrap import product_qsettings

    return product_qsettings()


def _read_failure_times_unsafe() -> list[float]:
    try:
        from app.gui_bootstrap import ensure_qsettings_core_application

        ensure_qsettings_core_application()
        raw = _qsettings().value(_FAILURE_TIMES_JSON_KEY, "")
        if not raw:
            return []
        data = json.loads(str(raw))
        if not isinstance(data, list):
            return []
        out: list[float] = []
        for x in data:
            try:
                out.append(float(x))
            except (TypeError, ValueError):
                continue
        return out
    except Exception:
        return []


def _write_failure_times(times: list[float]) -> None:
    try:
        from app.gui_bootstrap import ensure_qsettings_core_application

        ensure_qsettings_core_application()
        qs = _qsettings()
        if not times:
            qs.remove(_FAILURE_TIMES_JSON_KEY)
        else:
            qs.setValue(_FAILURE_TIMES_JSON_KEY, json.dumps(times))
        qs.sync()
    except Exception as exc:
        logger.debug("watchdog: could not persist failure times: %s", exc)


def _prune_failure_times(now: float, times: list[float]) -> list[float]:
    cutoff = now - LAUNCH_FAILURE_WINDOW_SEC
    return [t for t in times if t >= cutoff]


def _trigger_auto_safe_mode() -> None:
    try:
        from app.gui_bootstrap import write_safe_mode_next_launch_flag, write_safe_mode_watchdog_banner

        write_safe_mode_next_launch_flag(True)
        write_safe_mode_watchdog_banner(True)
        logger.warning(
            "GUI launch watchdog: %s failures within %.1fs — safe mode scheduled for next launch.",
            LAUNCH_FAILURE_THRESHOLD,
            LAUNCH_FAILURE_WINDOW_SEC,
        )
    except Exception as exc:
        logger.debug("watchdog: could not set safe mode flags: %s", exc)


def note_gui_launch_attempt() -> None:
    """
    Ein GUI-Startversuch (Produkt-Launcher / Shell-Einstieg).

    Erhöht Attempt-Zähler und Zeitstempel — ohne Erfolg/Fehler zu präjudizieren.
    """
    now = time.time()
    try:
        from app.gui_bootstrap import ensure_qsettings_core_application

        ensure_qsettings_core_application()
        qs = _qsettings()
        raw_prev = qs.value(_GUI_START_ATTEMPTS_KEY, 0)
        try:
            prev = int(raw_prev) if raw_prev is not None else 0
        except (TypeError, ValueError):
            prev = 0
        qs.setValue(_GUI_START_ATTEMPTS_KEY, prev + 1)
        qs.setValue(_LAST_GUI_START_UNIX_KEY, float(now))
        qs.sync()
    except Exception as exc:
        logger.debug("watchdog: note_gui_launch_attempt persist failed: %s", exc)


def note_failed_gui_launch() -> None:
    """Persistierter Fehlversuch; bei Schwellenüberschreitung Auto-Safe-Mode."""
    st = _state
    st.last_gui_launch_monotonic = time.monotonic()
    now = time.time()
    times = _prune_failure_times(now, _read_failure_times_unsafe())
    times.append(now)
    _write_failure_times(times)
    st.consecutive_gui_launch_failures = len(times)
    if len(times) >= LAUNCH_FAILURE_THRESHOLD:
        _trigger_auto_safe_mode()


def note_successful_gui_launch() -> None:
    """Erfolgreiche GUI-Initialisierung: Fehlerhistorie und Versuchszähler zurücksetzen."""
    st = _state
    st.last_gui_launch_monotonic = time.monotonic()
    st.consecutive_gui_launch_failures = 0
    st.successful_launch_count += 1
    _write_failure_times([])
    now = time.time()
    try:
        from app.gui_bootstrap import ensure_qsettings_core_application

        ensure_qsettings_core_application()
        qs = _qsettings()
        qs.setValue(_GUI_START_ATTEMPTS_KEY, 0)
        qs.setValue(_LAST_SUCCESS_UNIX_KEY, float(now))
        qs.sync()
    except Exception as exc:
        logger.debug("watchdog: note_successful persist failed: %s", exc)


def clear_watchdog_failure_persistence() -> None:
    """Löscht persistierte Watchdog-Fehlerdaten (Rescue „Disable Safe Mode“ / Tests)."""
    _write_failure_times([])
    try:
        from app.gui_bootstrap import ensure_qsettings_core_application

        ensure_qsettings_core_application()
        qs = _qsettings()
        qs.remove(_GUI_START_ATTEMPTS_KEY)
        qs.remove(_LAST_GUI_START_UNIX_KEY)
        qs.remove(_LAST_SUCCESS_UNIX_KEY)
        qs.sync()
    except Exception as exc:
        logger.debug("watchdog: clear persistence failed: %s", exc)


def reset_watchdog_for_tests() -> None:
    """Setzt Speicher- und QSettings-Watchdog-Felder zurück."""
    global _state
    _state = GuiLaunchWatchdogState()
    clear_watchdog_failure_persistence()
    try:
        from app.gui_bootstrap import (
            ensure_qsettings_core_application,
            write_safe_mode_next_launch_flag,
            write_safe_mode_watchdog_banner,
        )

        ensure_qsettings_core_application()
        write_safe_mode_next_launch_flag(False)
        write_safe_mode_watchdog_banner(False)
        qs = _qsettings()
        qs.remove(_FAILURE_TIMES_JSON_KEY)
        qs.remove(_GUI_START_ATTEMPTS_KEY)
        qs.remove(_LAST_GUI_START_UNIX_KEY)
        qs.remove(_LAST_SUCCESS_UNIX_KEY)
        qs.sync()
    except Exception:
        pass


def get_gui_launch_watchdog_state() -> GuiLaunchWatchdogState:
    return _state


def read_persisted_watchdog_snapshot_for_diagnostics() -> dict[str, str]:
    """
    Read-only Kurzabbild für Overlay (keine Secrets).

    Bei Lesefehlern: leere / „unavailable“-Werte (fail-closed).
    """
    try:
        from app.gui_bootstrap import ensure_qsettings_core_application

        ensure_qsettings_core_application()
        qs = _qsettings()
        times = _read_failure_times_unsafe()
        now = time.time()
        pruned = _prune_failure_times(now, times)
        attempts = qs.value(_GUI_START_ATTEMPTS_KEY, 0)
        try:
            ac = int(attempts) if attempts is not None else 0
        except (TypeError, ValueError):
            ac = 0
        last_start = qs.value(_LAST_GUI_START_UNIX_KEY, "")
        last_ok = qs.value(_LAST_SUCCESS_UNIX_KEY, "")
        return {
            "failures_in_window": str(len(pruned)),
            "gui_start_attempts": str(ac),
            "last_gui_start_unix": str(last_start) if last_start != "" else "unavailable",
            "last_successful_start_unix": str(last_ok) if last_ok != "" else "unavailable",
        }
    except Exception:
        return {
            "failures_in_window": "unavailable",
            "gui_start_attempts": "unavailable",
            "last_gui_start_unix": "unavailable",
            "last_successful_start_unix": "unavailable",
        }


def on_app_session_start() -> None:
    """Einmal pro QApplication-Start: nur Session-Speicher zurücksetzen (Persistenz bleibt)."""
    st = _state
    st.session_started_monotonic = time.monotonic()
    st.last_gui_launch_monotonic = None
    st.consecutive_gui_launch_failures = 0
    st.successful_launch_count = 0
