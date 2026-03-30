"""
Qt Quick / QML runtime — loads repository ``qml/AppRoot.qml`` and shell bridge.

Rules:
- No service objects on the QML context.
- QGuiApplication must exist before ``activate``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from app.ui_runtime.base_runtime import BaseRuntime
from app.ui_runtime.qml.shell_bridge_facade import ShellBridgeFacade

logger = logging.getLogger(__name__)


def _repository_root() -> Path:
    """Product tree root containing ``qml/AppRoot.qml`` (monorepo or legacy host layout)."""
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "qml" / "AppRoot.qml").is_file():
            return p
    raise FileNotFoundError(
        "Could not locate QML product root: no qml/AppRoot.qml found among parents of "
        f"{here}"
    )


class QmlRuntime(BaseRuntime):
    """Binds ``QQmlApplicationEngine`` to the workspace ``qml/`` tree."""

    def __init__(self, manifest) -> None:
        super().__init__(manifest)
        self._engine: QQmlApplicationEngine | None = None
        self._shell_bridge: ShellBridgeFacade | None = None
        self._chat_viewmodel: Any = None
        self._prompt_studio_viewmodel: Any = None
        self._agent_studio_viewmodel: Any = None
        self._deployment_studio_viewmodel: Any = None
        self._settings_studio_viewmodel: Any = None
        self._workflow_studio_viewmodel: Any = None
        self._project_studio_viewmodel: Any = None

    def activate(self, context: dict[str, Any] | None = None) -> None:
        ctx = dict(context or {})
        if QGuiApplication.instance() is None:
            raise RuntimeError("QmlRuntime.activate requires an existing QGuiApplication instance.")

        from app.core.startup_contract import resolve_qml_root

        qml_root = resolve_qml_root()
        if not (qml_root / "AppRoot.qml").is_file():
            raise FileNotFoundError(f"QML root not found: {qml_root}")

        engine = QQmlApplicationEngine()
        engine.addImportPath(str(qml_root))

        bridge = ShellBridgeFacade(qml_root)
        bridge.initialize()
        engine.rootContext().setContextProperty("shell", bridge)
        self._shell_bridge = bridge

        chat_vm = ctx.get("chat")
        if chat_vm is not None:
            engine.rootContext().setContextProperty("chat", chat_vm)
            self._chat_viewmodel = chat_vm

        prompt_vm = ctx.get("promptStudio")
        if prompt_vm is not None:
            engine.rootContext().setContextProperty("promptStudio", prompt_vm)
            self._prompt_studio_viewmodel = prompt_vm

        agent_vm = ctx.get("agentStudio")
        if agent_vm is not None:
            engine.rootContext().setContextProperty("agentStudio", agent_vm)
            self._agent_studio_viewmodel = agent_vm

        dep_vm = ctx.get("deploymentStudio")
        if dep_vm is not None:
            engine.rootContext().setContextProperty("deploymentStudio", dep_vm)
            self._deployment_studio_viewmodel = dep_vm

        set_vm = ctx.get("settingsStudio")
        if set_vm is not None:
            engine.rootContext().setContextProperty("settingsStudio", set_vm)
            self._settings_studio_viewmodel = set_vm

        wf_vm = ctx.get("workflowStudio")
        if wf_vm is not None:
            engine.rootContext().setContextProperty("workflowStudio", wf_vm)
            self._workflow_studio_viewmodel = wf_vm

        pr_vm = ctx.get("projectStudio")
        if pr_vm is not None:
            engine.rootContext().setContextProperty("projectStudio", pr_vm)
            self._project_studio_viewmodel = pr_vm

        main_qml = qml_root / "AppRoot.qml"
        engine.load(QUrl.fromLocalFile(str(main_qml.resolve())))

        if not engine.rootObjects():
            # PySide6: ``warnings`` is a signal, not ``errors()`` — keep message minimal.
            msg = "unknown QML error (check Qt warning output)"
            if engine.hasError():
                msg = "QML load failed (engine.hasError() is true; see stderr)"
            logger.error("QML load failed: %s", msg)
            self._shell_bridge = None
            self._chat_viewmodel = None
            self._prompt_studio_viewmodel = None
            self._agent_studio_viewmodel = None
            self._deployment_studio_viewmodel = None
            self._settings_studio_viewmodel = None
            self._workflow_studio_viewmodel = None
            self._project_studio_viewmodel = None
            engine.deleteLater()
            raise RuntimeError(f"QML load failed: {msg}")

        self._engine = engine
        logger.info("QML shell loaded from %s", main_qml)

    def primary_root_object(self):
        """Erstes QML-Root-Objekt (z. B. Fenster) — für produktweite Shell-Anbindung."""
        e = self._engine
        if e is None:
            return None
        roots = e.rootObjects()
        return roots[0] if roots else None

    def deactivate(self) -> None:
        if self._engine is not None:
            self._engine.deleteLater()
            self._engine = None
        self._shell_bridge = None
        self._chat_viewmodel = None
        self._prompt_studio_viewmodel = None
        self._agent_studio_viewmodel = None
        self._deployment_studio_viewmodel = None
        self._settings_studio_viewmodel = None
        self._workflow_studio_viewmodel = None
        self._project_studio_viewmodel = None
