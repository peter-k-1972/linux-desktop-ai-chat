"""Executor-Registry – Auflösung executor_type → Executor-Instanz."""

from typing import Dict, Optional

from app.pipelines.executors.base import StepExecutor
from app.pipelines.executors.shell_executor import ShellExecutor
from app.pipelines.executors.python_executor import PythonCallableExecutor
from app.pipelines.executors.placeholder_executors import (
    PlaceholderComfyUIExecutor,
    PlaceholderMediaExecutor,
)
from app.pipelines.executors.cursor_light import CursorLightExecutor


class ExecutorRegistry:
    """
    Registry für Step-Executors.

    Mappt executor_type (str) auf Executor-Instanzen.
    Erweiterbar ohne Änderung der Engine.
    """

    def __init__(self) -> None:
        self._executors: Dict[str, StepExecutor] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register("shell", ShellExecutor())
        self.register("python_callable", PythonCallableExecutor())
        self.register("comfyui", PlaceholderComfyUIExecutor())
        self.register("media", PlaceholderMediaExecutor())
        self.register("cursor_light", CursorLightExecutor())

    def register(self, executor_type: str, executor: StepExecutor) -> None:
        """Registriert einen Executor für den gegebenen Typ."""
        self._executors[executor_type] = executor

    def get(self, executor_type: str) -> Optional[StepExecutor]:
        """Liefert den Executor für den Typ oder None."""
        return self._executors.get(executor_type)

    def get_or_raise(self, executor_type: str) -> StepExecutor:
        """Liefert den Executor oder wirft ValueError."""
        ex = self.get(executor_type)
        if ex is None:
            raise ValueError(f"Unknown executor type: {executor_type}")
        return ex


_default_registry: Optional[ExecutorRegistry] = None


def get_executor_registry() -> ExecutorRegistry:
    """Singleton-Zugriff auf die Executor-Registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = ExecutorRegistry()
    return _default_registry
