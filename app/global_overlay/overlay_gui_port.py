"""
Produkt-Adapter: GUI-Status und -Wechsel für das Overlay (Slice 3).

- Registry: ``app.gui_registry``
- Validierung: Manifest-/Launch-Kontext wie ``run_gui_shell`` (fail-closed)
- Persistenz: ``write_preferred_gui_id_to_qsettings`` / ``read_preferred_gui_id_from_qsettings``
- Relaunch: kanonischer Launcher ``run_gui_shell.py`` mit ``--gui <gui_id>`` (wie Produktstart)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from app.global_overlay.product_launcher import (
    CANONICAL_GUI_LAUNCHER_SCRIPT,
    canonical_gui_launcher_is_present,
    resolve_canonical_gui_launcher_path,
)
from app.gui_registry import (
    GUI_ID_LIBRARY_QML,
    get_default_fallback_gui_id,
    get_gui_descriptor,
    list_registered_gui_ids,
    resolve_repo_root,
)

_GUI_RELAUNCH_HINT: Final[str] = (
    "After a successful switch, the app relaunches via run_gui_shell.py with your choice; "
    "this is the same path as a normal product start."
)


@dataclass(frozen=True, slots=True)
class GuiOverlaySnapshot:
    """GUI-Bezug fürs Overlay (von Registry / QSettings), getrennt vom Theme-Block."""

    active_gui_id: str
    active_display_name: str
    active_gui_type: str
    default_fallback_gui_id: str
    preferred_gui_id_stored: str
    gui_switching_available: bool
    gui_switching_block_reason: str | None
    registered_entries: tuple[tuple[str, str, str], ...]
    """(gui_id, display_name, gui_type) — nur ``list_registered_gui_ids()``."""

    relaunch_required_hint: str


@dataclass(frozen=True, slots=True)
class GuiApplyResult:
    ok: bool
    message: str
    relaunch_scheduled: bool = False


def _read_preferred_safe() -> str:
    try:
        from app.gui_bootstrap import read_preferred_gui_id_from_qsettings

        return read_preferred_gui_id_from_qsettings()
    except Exception:
        return "unavailable"


def build_gui_overlay_snapshot(active_gui_id: str) -> GuiOverlaySnapshot:
    desc = get_gui_descriptor(active_gui_id)
    preferred = _read_preferred_safe()
    entries = tuple(
        (gid, get_gui_descriptor(gid).display_name, get_gui_descriptor(gid).gui_type)
        for gid in sorted(list_registered_gui_ids())
    )
    block: str | None = None
    available = True
    repo = resolve_repo_root()
    launcher = resolve_canonical_gui_launcher_path()
    if not canonical_gui_launcher_is_present():
        available = False
        block = f"Product launcher missing ({CANONICAL_GUI_LAUNCHER_SCRIPT}): {launcher}"

    return GuiOverlaySnapshot(
        active_gui_id=desc.gui_id,
        active_display_name=desc.display_name,
        active_gui_type=desc.gui_type,
        default_fallback_gui_id=get_default_fallback_gui_id(),
        preferred_gui_id_stored=preferred,
        gui_switching_available=available,
        gui_switching_block_reason=block,
        registered_entries=entries,
        relaunch_required_hint=_GUI_RELAUNCH_HINT,
    )


def validate_gui_switch_target(target_gui_id: str, *, repo_root: Path | None = None) -> tuple[bool, str]:
    """
    Fail-closed Prüfung vor Persistenz (Manifest, Kompatibilität, Entrypoint).

    Returns:
        (True, "") bei Erfolg, sonst (False, Nutzerhinweis).
    """
    root = repo_root or resolve_repo_root()
    tid = (target_gui_id or "").strip()
    if not tid:
        return False, "No GUI selected."

    try:
        desc = get_gui_descriptor(tid)
    except KeyError:
        return False, f"Unknown GUI: {tid!r} (not in registry)."

    ep = (root / desc.entrypoint).resolve()
    if not ep.is_file():
        return False, f"Entrypoint missing for {tid!r}: {ep}"

    try:
        from app.qml_alternative_gui_validator import (
            assert_descriptor_matches_manifest_paths,
            validate_library_qml_gui_launch_context,
        )

        assert_descriptor_matches_manifest_paths(desc, root)
        if desc.gui_type == "qt_quick":
            if tid == GUI_ID_LIBRARY_QML:
                validate_library_qml_gui_launch_context(root, expected_gui_id=tid)
            else:
                return (
                    False,
                    f"No manifest validator registered for qt_quick gui_id={tid!r} (fail-closed).",
                )
    except FileNotFoundError as e:
        return False, str(e)
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"GUI validation failed: {e}"

    return True, ""


def relaunch_via_run_gui_shell(gui_id: str) -> bool:
    """
    Startet den kanonischen Produkt-Launcher detached (gleicher Mechanismus wie manueller Start).

    Args:
        gui_id: Kanonische ID (z. B. ``default_widget_gui``).
    """
    try:
        from PySide6.QtCore import QProcess
    except Exception:
        return False

    launcher = resolve_canonical_gui_launcher_path()
    if not launcher.is_file():
        return False
    repo = resolve_repo_root()
    return bool(
        QProcess.startDetached(
            sys.executable,
            [str(launcher), "--gui", gui_id],
            str(repo),
        )
    )


def apply_gui_switch_via_product(active_gui_id: str, target_gui_id: str) -> GuiApplyResult:
    """
    Validiert, persistiert ``preferred_gui``, startet Relaunch über ``run_gui_shell.py``.

    Bei fehlgeschlagenem Relaunch wird ``preferred_gui`` auf den vorherigen Wert zurückgesetzt.
    """
    from app.gui_bootstrap import read_preferred_gui_id_from_qsettings, write_preferred_gui_id_to_qsettings

    target = (target_gui_id or "").strip()
    ok, err = validate_gui_switch_target(target)
    if not ok:
        return GuiApplyResult(False, err)

    if target == active_gui_id:
        write_preferred_gui_id_to_qsettings(target)
        return GuiApplyResult(
            True,
            "This GUI is already active. Preference saved; no relaunch.",
            relaunch_scheduled=False,
        )

    previous = read_preferred_gui_id_from_qsettings()
    write_preferred_gui_id_to_qsettings(target)

    def _clear_watchdog_recovery_banner() -> None:
        try:
            from app.gui_bootstrap import write_safe_mode_watchdog_banner

            write_safe_mode_watchdog_banner(False)
        except Exception:
            pass

    if not relaunch_via_run_gui_shell(target):
        write_preferred_gui_id_to_qsettings(previous)
        return GuiApplyResult(
            False,
            "Could not start the product launcher (run_gui_shell.py). Preference was reverted.",
            relaunch_scheduled=False,
        )

    _clear_watchdog_recovery_banner()

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is not None:
        app.quit()

    return GuiApplyResult(
        True,
        f"Switching to {target!r}; relaunching via run_gui_shell.py …",
        relaunch_scheduled=True,
    )


def revert_to_default_gui_via_product(active_gui_id: str) -> GuiApplyResult:
    """Setzt bevorzugte GUI auf Registry-Default und relauncht wie ``apply_gui_switch_via_product``."""
    return apply_gui_switch_via_product(active_gui_id, get_default_fallback_gui_id())
