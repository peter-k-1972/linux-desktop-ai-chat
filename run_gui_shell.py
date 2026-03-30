#!/usr/bin/env python3
"""
Startet die GUI-Shell (Standard-GUI der Anwendung).

Verwendung:
    python main.py
    python run_gui_shell.py
    python run_gui_shell.py --theme dark_default
    python run_gui_shell.py --gui library_qml_gui
    python run_gui_shell.py --gui default_widget_gui

``--gui`` akzeptiert Aliase (``default``, ``library_qml``, ``qml``, …) und kanonische ``gui_id``.

``--edition`` / ``LDC_EDITION``: Produktedition (u. a. ``minimal``, ``standard``, ``automation``, ``full``;
intern auch ``plugin_example`` für Demo-Plugin-Aktivierung). Default ``full``. Siehe
``docs/architecture/BOOTSTRAP_EDITION_ACTIVATION.md``, ``docs/architecture/PLUGIN_FEATURE_PRODUCT_ACTIVATION.md``.

Alternative GUI: ``docs/architecture/GUI_REGISTRY.md``.

Smoke-Kurzlauf (QA): ``LINUX_DESKTOP_CHAT_GUI_SMOKE=1`` beendet die Shell kurz nach dem Laden der Basis-Oberfläche.
"""

import argparse
import asyncio
import logging
import subprocess
import sys
from pathlib import Path

from app.services.infrastructure import get_infrastructure

_LOG = logging.getLogger(__name__)

_FALLBACK_MSG = "Alternative GUI failed, reverting to default widget GUI."


def _try_start_qt_quick_gui(repo_root: Path, desc) -> bool:
    """
    Validiert Manifest (fail-closed) und startet den Entrypoint der Qt-Quick-GUI.

    Returns:
        True wenn Subprozess Exit 0 — Aufrufer beendet dann das Programm.
        False bei Fehler — Aufrufer startet Widget-GUI (Fallback).
    """
    from app.core.startup_contract import (
        GUI_ID_DEFAULT_WIDGET,
        GUI_ID_LIBRARY_QML,
        write_preferred_gui_id_to_qsettings,
    )
    from app.qml_alternative_gui_validator import (
        assert_descriptor_matches_manifest_paths,
        validate_library_qml_gui_launch_context,
    )

    try:
        assert_descriptor_matches_manifest_paths(desc, repo_root)
        if desc.gui_id == GUI_ID_LIBRARY_QML:
            validate_library_qml_gui_launch_context(repo_root)
        else:
            raise ValueError(f"No qt_quick launch validator registered for gui_id={desc.gui_id!r}")
    except Exception as exc:
        _LOG.error("Alternative GUI validation failed: %s", exc)
        print(_FALLBACK_MSG, file=sys.stderr)
        write_preferred_gui_id_to_qsettings(GUI_ID_DEFAULT_WIDGET)
        try:
            from app.global_overlay.gui_launch_watchdog import note_failed_gui_launch

            note_failed_gui_launch()
        except Exception:
            pass
        return False

    script = repo_root / desc.entrypoint
    if not script.is_file():
        _LOG.error("GUI entrypoint missing: %s", script)
        print(_FALLBACK_MSG, file=sys.stderr)
        write_preferred_gui_id_to_qsettings(GUI_ID_DEFAULT_WIDGET)
        try:
            from app.global_overlay.gui_launch_watchdog import note_failed_gui_launch

            note_failed_gui_launch()
        except Exception:
            pass
        return False

    proc = subprocess.run([sys.executable, str(script)], cwd=str(repo_root))
    if proc.returncode != 0:
        _LOG.error("GUI subprocess exited with code %s", proc.returncode)
        print(_FALLBACK_MSG, file=sys.stderr)
        write_preferred_gui_id_to_qsettings(GUI_ID_DEFAULT_WIDGET)
        try:
            from app.global_overlay.gui_launch_watchdog import note_failed_gui_launch

            note_failed_gui_launch()
        except Exception:
            pass
        return False

    write_preferred_gui_id_to_qsettings(desc.gui_id)
    return True


def _run_widget_gui(args: argparse.Namespace) -> None:
    import os

    from PySide6.QtWidgets import QApplication

    from app.gui.chat_backend import ChatBackend, set_chat_backend
    from app.gui.knowledge_backend import KnowledgeBackend, set_knowledge_backend
    from app.gui.qsettings_backend import create_qsettings_backend
    from app.gui.shell import ShellMainWindow
    from app.gui.themes import get_theme_manager
    from app.gui.themes.theme_id_utils import is_registered_theme_id, registered_theme_ids
    from app.runtime.lifecycle import try_acquire_single_instance_lock, register_shutdown_hooks
    from app.services.infrastructure import get_infrastructure, init_infrastructure

    if not try_acquire_single_instance_lock():
        print("Linux Desktop Chat läuft bereits. Nur eine Instanz ist erlaubt.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("ollama-desktop-chat")  # StartupWMClass für Taskleisten-Gruppierung
    app.setDesktopFileName("linux-desktop-chat")  # Desktop-Integration (Wayland/GNOME)
    app.setQuitOnLastWindowClosed(True)  # Standard: Fenster schließen → App beenden
    register_shutdown_hooks(app)

    try:
        from app.global_overlay.gui_launch_watchdog import on_app_session_start

        on_app_session_start()
    except Exception:
        pass

    using_qasync = False
    loop = None
    try:
        from qasync import QEventLoop

        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        using_qasync = True
    except ImportError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    init_infrastructure(settings_backend=create_qsettings_backend())

    from app.features import (
        build_feature_registry_for_edition,
        resolve_active_edition_name,
        set_feature_registry,
    )

    _edition = resolve_active_edition_name(getattr(args, "edition", None))
    set_feature_registry(build_feature_registry_for_edition(_edition))

    infra = get_infrastructure()
    set_chat_backend(ChatBackend())
    set_knowledge_backend(KnowledgeBackend())

    default_theme = os.environ.get("LINUX_DESKTOP_CHAT_THEME", "light_default")
    theme_to_apply = getattr(infra.settings, "theme_id", "") or args.theme
    if not is_registered_theme_id(theme_to_apply):
        theme_to_apply = args.theme if is_registered_theme_id(args.theme) else "light_default"
    manager = get_theme_manager()
    if not manager.set_theme(theme_to_apply):
        print(f"Warnung: Theme '{theme_to_apply}' nicht gefunden, nutze light_default.")
        manager.set_theme("light_default")

    try:
        from app.core.startup_contract import GUI_ID_DEFAULT_WIDGET as _WIDGET_GUI
        from app.workspace_presets.preset_startup import (
            apply_workspace_preset_runtime_after_infrastructure,
        )

        apply_workspace_preset_runtime_after_infrastructure(
            running_gui_id=_WIDGET_GUI,
            running_theme_id=manager.get_current_id(),
        )
    except Exception:
        _LOG.exception(
            "workspace preset: apply_workspace_preset_runtime_after_infrastructure failed (widget shell); continuing",
        )

    win = ShellMainWindow()
    win.show()

    from app.core.startup_contract import GUI_ID_DEFAULT_WIDGET
    from app.gui_smoke_constants import is_gui_smoke_mode

    if not is_gui_smoke_mode():
        try:
            from app.global_overlay import install_global_overlay_host
            from app.global_overlay.gui_launch_watchdog import note_successful_gui_launch

            install_global_overlay_host(app, active_gui_id=GUI_ID_DEFAULT_WIDGET, primary_window=win)
            note_successful_gui_launch()
        except Exception:
            pass

    if is_gui_smoke_mode():
        from PySide6.QtCore import QTimer

        QTimer.singleShot(150, app.quit)

    if using_qasync and loop is not None:
        with loop:
            sys.exit(loop.run_forever())
    else:
        sys.exit(app.exec())


def main():
    import os

    from app.core.startup_contract import (
        argv_has_long_option,
        consume_safe_mode_next_launch,
        get_gui_descriptor,
        list_valid_gui_cli_tokens,
        resolve_active_gui_id,
        resolve_user_gui_choice,
        write_preferred_gui_id_to_qsettings,
        write_product_theme_defaults_to_qsettings,
    )
    from app.debug.gui_log_buffer import install_gui_log_handler
    from app.gui.qsettings_backend import create_qsettings_backend
    from app.gui.themes.theme_id_utils import registered_theme_ids
    from app.metrics.metrics_collector import get_metrics_collector
    from app.services.infrastructure import init_infrastructure
    from app.utils.env_loader import load_env

    load_env()
    install_gui_log_handler()
    get_metrics_collector()
    # Produktiver GUI-Bootstrap: QSettings-Backend vor jedem Infrastrukturzugriff setzen.
    init_infrastructure(settings_backend=create_qsettings_backend())

    try:
        import sqlalchemy  # noqa: F401
    except ImportError:
        print(
            "Fehlende Abhängigkeit: SQLAlchemy (ORM). "
            "Virtuelle Umgebung aktivieren und ausführen:\n"
            "  .venv/bin/pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    default_theme = os.environ.get("LINUX_DESKTOP_CHAT_THEME", "light_default")
    _tokens_help = ", ".join(list_valid_gui_cli_tokens())
    parser = argparse.ArgumentParser(description="Linux Desktop Chat – GUI Shell")
    _theme_choices = sorted(registered_theme_ids())
    parser.add_argument(
        "--theme",
        default=default_theme,
        choices=_theme_choices,
        help=f"Theme id ({', '.join(_theme_choices)}). Env: LINUX_DESKTOP_CHAT_THEME",
    )
    parser.add_argument(
        "--gui",
        default=None,
        metavar="GUI",
        help=(
            "Registered GUI: aliases or gui_id (e.g. default, library_qml_gui). "
            f"Allowed tokens: {_tokens_help}. Overrides env LINUX_DESKTOP_CHAT_GUI and QSettings."
        ),
    )
    parser.add_argument(
        "--edition",
        default=None,
        metavar="NAME",
        help=(
            "Product edition: minimal, standard, automation, full, plugin_example (default: full). "
            "Overrides env LDC_EDITION when set. See BOOTSTRAP_EDITION_ACTIVATION.md, "
            "PLUGIN_FEATURE_PRODUCT_ACTIVATION.md."
        ),
    )
    args = parser.parse_args()

    try:
        from app.global_overlay.gui_launch_watchdog import note_gui_launch_attempt

        note_gui_launch_attempt()
    except Exception:
        pass

    from app.core.startup_contract import GUI_ID_DEFAULT_WIDGET as _SAFE_DEFAULT_GUI

    if consume_safe_mode_next_launch():
        if not argv_has_long_option(sys.argv, "--gui"):
            write_preferred_gui_id_to_qsettings(_SAFE_DEFAULT_GUI)
        if not argv_has_long_option(sys.argv, "--theme"):
            write_product_theme_defaults_to_qsettings()
            args.theme = "light_default"

    if args.gui is not None:
        active_gui_id = resolve_user_gui_choice(args.gui)
        if active_gui_id is None:
            print(
                f"Unbekannte --gui {args.gui!r}. Erlaubt: {_tokens_help} "
                "oder kanonische gui_id (default_widget_gui, library_qml_gui).",
                file=sys.stderr,
            )
            sys.exit(2)
        write_preferred_gui_id_to_qsettings(active_gui_id)
    else:
        try:
            from app.workspace_presets.preset_startup import (
                sync_workspace_preset_preferences_before_gui_resolution,
            )

            sync_workspace_preset_preferences_before_gui_resolution(sys.argv)
        except Exception:
            _LOG.exception(
                "workspace preset: sync_workspace_preset_preferences_before_gui_resolution failed; "
                "continuing with existing QSettings / env GUI resolution",
            )
        active_gui_id = resolve_active_gui_id(cli_gui=None)

    repo_root = Path(__file__).resolve().parent
    desc = get_gui_descriptor(active_gui_id)

    if desc.gui_type == "qt_quick":
        if _try_start_qt_quick_gui(repo_root, desc):
            sys.exit(0)
        _run_widget_gui(args)
        return

    _run_widget_gui(args)


if __name__ == "__main__":
    main()
