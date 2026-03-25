"""Placeholder-Executors für ComfyUI und Media – noch keine echte Implementierung."""

from typing import Any, Dict

from app.pipelines.executors.base import StepExecutor, StepResult


class PlaceholderComfyUIExecutor(StepExecutor):
    """
    Placeholder für ComfyUI-Executor.

    In Phase 1: Gibt einen Hinweis zurück, dass ComfyUI noch nicht integriert ist.
    Später: Echte ComfyUI-API-Anbindung.
    """

    def execute(
        self,
        step_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> StepResult:
        return StepResult(
            success=False,
            error="ComfyUI executor not yet implemented (placeholder)",
            logs=[f"Placeholder ComfyUI step '{step_id}' – config keys: {list(config.keys())}"],
        )


class PlaceholderMediaExecutor(StepExecutor):
    """
    Placeholder für Media-Executor (Voice, Musik, Subtitles, Merge).

    In Phase 1: Gibt einen Hinweis zurück.
    Später: Echte Media-Tool-Anbindung.
    """

    def execute(
        self,
        step_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> StepResult:
        return StepResult(
            success=False,
            error="Media executor not yet implemented (placeholder)",
            logs=[f"Placeholder Media step '{step_id}' – config keys: {list(config.keys())}"],
        )
