"""Shell-Executor – führt Shell-Befehle aus."""

import logging
import subprocess
from typing import Any, Dict

from app.pipelines.executors.base import StepExecutor, StepResult
from app.pipelines.models import PipelineArtifact

logger = logging.getLogger(__name__)


class ShellExecutor(StepExecutor):
    """Führt einen Shell-Befehl aus."""

    def execute(
        self,
        step_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> StepResult:
        command = config.get("command", "")
        if not command:
            return StepResult(
                success=False,
                error="Shell executor requires 'command' in config",
                logs=[],
            )
        cwd = config.get("cwd")
        env = config.get("env")
        shell = config.get("shell", True)

        logs: list[str] = []
        logs.append(f"Executing: {command}")

        try:
            result = subprocess.run(
                command,
                shell=shell,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=config.get("timeout", 300),
            )
            if result.stdout:
                logs.append(result.stdout.strip())
            if result.stderr:
                logs.append(f"stderr: {result.stderr.strip()}")

            if result.returncode != 0:
                return StepResult(
                    success=False,
                    error=f"Command exited with code {result.returncode}",
                    logs=logs,
                )

            artifacts: list[PipelineArtifact] = []
            if config.get("capture_stdout_as") and result.stdout:
                artifacts.append(
                    PipelineArtifact(
                        step_id=step_id,
                        key=config["capture_stdout_as"],
                        value=result.stdout.strip(),
                        artifact_type="text",
                    )
                )

            return StepResult(success=True, logs=logs, artifacts=artifacts)

        except subprocess.TimeoutExpired:
            return StepResult(
                success=False,
                error="Command timed out",
                logs=logs,
            )
        except Exception as e:
            logs.append(str(e))
            return StepResult(
                success=False,
                error=str(e),
                logs=logs,
            )
