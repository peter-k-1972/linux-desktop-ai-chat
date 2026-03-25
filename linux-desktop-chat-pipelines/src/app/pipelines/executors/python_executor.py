"""Python-Callable-Executor – führt Python-Callables aus."""

import logging
from typing import Any, Callable, Dict

from app.pipelines.executors.base import StepExecutor, StepResult
from app.pipelines.models import PipelineArtifact

logger = logging.getLogger(__name__)


class PythonCallableExecutor(StepExecutor):
    """
    Führt ein Python-Callable aus.

    Config:
    - callable: Modulpfad oder Callable (z.B. "mymodule.myfunc")
    - args: Positionale Argumente
    - kwargs: Keyword-Argumente
    """

    def execute(
        self,
        step_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> StepResult:
        callable_ref = config.get("callable")
        if callable_ref is None:
            return StepResult(
                success=False,
                error="Python executor requires 'callable' in config",
                logs=[],
            )

        fn = self._resolve_callable(callable_ref)
        if fn is None:
            return StepResult(
                success=False,
                error=f"Cannot resolve callable: {callable_ref}",
                logs=[],
            )

        args = [context] + list(config.get("args", []))
        kwargs = dict(config.get("kwargs", {}))

        logs: list[str] = []
        logs.append(f"Calling {callable_ref}")

        try:
            result = fn(*args, **kwargs)
            if isinstance(result, StepResult):
                return result
            if isinstance(result, tuple):
                success, *rest = result
                error = rest[0] if len(rest) > 0 else None
                return StepResult(success=bool(success), error=error, logs=logs)
            return StepResult(success=True, logs=logs, output={"result": result})
        except Exception as e:
            logs.append(str(e))
            return StepResult(
                success=False,
                error=str(e),
                logs=logs,
            )

    def _resolve_callable(self, ref: Any) -> Callable[..., Any] | None:
        if callable(ref):
            return ref
        if isinstance(ref, str):
            parts = ref.rsplit(".", 1)
            if len(parts) != 2:
                return None
            mod_path, attr = parts
            try:
                import importlib
                mod = importlib.import_module(mod_path)
                return getattr(mod, attr, None)
            except (ImportError, AttributeError):
                return None
        return None
