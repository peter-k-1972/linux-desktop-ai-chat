#!/usr/bin/env python3
"""
Startet die Qt-Quick-QML-Shell inkl. Chat-Domäne (Slice 2).

Bindet dieselbe Service-Infrastruktur wie die Widget-GUI (Chat-Port / DB), damit
Senden und Streaming funktionieren.

Parallel zur Standard-GUI: ``LINUX_DESKTOP_CHAT_SINGLE_INSTANCE`` standardmäßig 0.

Smoke-Kurzlauf (QA): ``LINUX_DESKTOP_CHAT_GUI_SMOKE=1`` beendet nach kurzer Verzögerung (Basis-Oberfläche geladen).

Usage:
    python run_qml_shell.py
    QT_QPA_PLATFORM=offscreen python run_qml_shell.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

_LOG = logging.getLogger(__name__)


def main() -> None:
    from app.utils.env_loader import load_env

    load_env()
    os.environ.setdefault("LINUX_DESKTOP_CHAT_SINGLE_INSTANCE", "0")

    try:
        from app.global_overlay.gui_launch_watchdog import note_gui_launch_attempt

        note_gui_launch_attempt()
    except Exception:
        pass

    from app.gui_bootstrap import (
        consume_safe_mode_next_launch,
        read_safe_mode_next_launch_pending,
        write_preferred_gui_id_to_qsettings,
        write_product_theme_defaults_to_qsettings,
    )
    from app.gui_registry import GUI_ID_DEFAULT_WIDGET
    from app.global_overlay.overlay_gui_port import relaunch_via_run_gui_shell

    if read_safe_mode_next_launch_pending():
        write_preferred_gui_id_to_qsettings(GUI_ID_DEFAULT_WIDGET)
        write_product_theme_defaults_to_qsettings()
        if relaunch_via_run_gui_shell(GUI_ID_DEFAULT_WIDGET):
            consume_safe_mode_next_launch()
            sys.exit(0)
        print(
            "Safe mode: could not relaunch via run_gui_shell.py; flag left set for retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        from app.workspace_presets.preset_startup import (
            sync_workspace_preset_preferences_before_gui_resolution,
        )

        sync_workspace_preset_preferences_before_gui_resolution(sys.argv)
    except Exception:
        _LOG.exception(
            "workspace preset: sync_workspace_preset_preferences_before_gui_resolution failed (QML entry); continuing",
        )

    repo = Path(__file__).resolve().parent
    from app.qml_alternative_gui_validator import validate_library_qml_gui_launch_context

    try:
        validate_library_qml_gui_launch_context(repo)
    except Exception as exc:
        print(f"QML theme manifest validation failed: {exc}", file=sys.stderr)
        try:
            from app.global_overlay.gui_launch_watchdog import note_failed_gui_launch

            note_failed_gui_launch()
        except Exception:
            pass
        sys.exit(2)

    from app.debug.gui_log_buffer import install_gui_log_handler
    from app.metrics.metrics_collector import get_metrics_collector

    install_gui_log_handler()
    get_metrics_collector()

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

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("linux-desktop-chat-qml")
    app.setDesktopFileName("linux-desktop-chat-qml")
    app.setQuitOnLastWindowClosed(True)

    from app.runtime.lifecycle import register_shutdown_hooks

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

    from app.gui.chat_backend import ChatBackend, set_chat_backend
    from app.gui.knowledge_backend import KnowledgeBackend, set_knowledge_backend
    from app.gui.qsettings_backend import create_qsettings_backend
    from app.services.infrastructure import get_infrastructure, init_infrastructure

    init_infrastructure(settings_backend=create_qsettings_backend())
    set_chat_backend(ChatBackend())
    set_knowledge_backend(KnowledgeBackend())

    try:
        from app.gui_registry import GUI_ID_LIBRARY_QML
        from app.workspace_presets.preset_startup import (
            apply_workspace_preset_runtime_after_infrastructure,
        )

        infra = get_infrastructure()
        tid = getattr(infra.settings, "theme_id", None)
        apply_workspace_preset_runtime_after_infrastructure(
            running_gui_id=GUI_ID_LIBRARY_QML,
            running_theme_id=tid,
        )
    except Exception:
        _LOG.exception(
            "workspace preset: apply_workspace_preset_runtime_after_infrastructure failed (QML shell); continuing",
        )

    def schedule_coro(coro):
        try:
            asyncio.get_running_loop().create_task(coro)
        except RuntimeError:
            pass

    from app.ui_runtime.qml.chat.chat_qml_viewmodel import build_chat_qml_viewmodel
    from python_bridge.agents.agent_viewmodel import build_agent_viewmodel
    from python_bridge.deployment.deployment_viewmodel import build_deployment_viewmodel
    from python_bridge.prompts.prompt_viewmodel import build_prompt_viewmodel
    from python_bridge.settings.settings_viewmodel import build_settings_viewmodel
    from python_bridge.projects.project_viewmodel import build_project_viewmodel
    from python_bridge.operations.operations_read_viewmodel import build_operations_read_viewmodel
    from python_bridge.workflows.workflow_viewmodel import build_workflow_viewmodel

    chat_vm = build_chat_qml_viewmodel(schedule_coro)
    prompt_vm = build_prompt_viewmodel()
    agent_vm = build_agent_viewmodel()
    deployment_vm = build_deployment_viewmodel()
    settings_vm = build_settings_viewmodel()
    workflow_vm = build_workflow_viewmodel()
    project_vm = build_project_viewmodel()
    operations_read_vm = build_operations_read_viewmodel()
    try:
        chat_vm.apply_runtime_context_hints(get_infrastructure().settings.chat_context_mode)
    except Exception:
        chat_vm.apply_runtime_context_hints(None)

    import app.ui_themes

    manifest_path = (
        Path(app.ui_themes.__file__).resolve().parent
        / "builtins"
        / "light_default"
        / "manifest.json"
    )
    if not manifest_path.is_file():
        print(f"Theme-Manifest fehlt: {manifest_path}", file=sys.stderr)
        sys.exit(2)

    from app.ui_runtime.qml.qml_runtime import QmlRuntime
    from app.ui_runtime.theme_loader import load_theme_manifest_from_path

    manifest = load_theme_manifest_from_path(manifest_path)
    runtime = QmlRuntime(manifest)
    try:
        runtime.activate(
            context={
                "chat": chat_vm,
                "promptStudio": prompt_vm,
                "agentStudio": agent_vm,
                "deploymentStudio": deployment_vm,
                "settingsStudio": settings_vm,
                "workflowStudio": workflow_vm,
                "projectStudio": project_vm,
                "operationsRead": operations_read_vm,
            }
        )
    except (FileNotFoundError, RuntimeError) as e:
        print(f"QML-Shell-Start fehlgeschlagen: {e}", file=sys.stderr)
        try:
            from app.global_overlay.gui_launch_watchdog import note_failed_gui_launch

            note_failed_gui_launch()
        except Exception:
            pass
        sys.exit(1)

    chat_vm.start_async_loaders()

    from app.gui_smoke_constants import is_gui_smoke_mode

    if not is_gui_smoke_mode():
        try:
            from app.global_overlay import install_global_overlay_host
            from app.global_overlay.gui_launch_watchdog import note_successful_gui_launch
            from app.gui_registry import GUI_ID_LIBRARY_QML

            install_global_overlay_host(app, active_gui_id=GUI_ID_LIBRARY_QML, primary_window=None)
            note_successful_gui_launch()
        except Exception:
            pass

    if is_gui_smoke_mode():
        from PySide6.QtCore import QTimer

        QTimer.singleShot(150, app.quit)

    app.aboutToQuit.connect(runtime.deactivate)

    if using_qasync and loop is not None:
        with loop:
            sys.exit(loop.run_forever() or 0)
    else:
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
