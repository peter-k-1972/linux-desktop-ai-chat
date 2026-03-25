"""Unit-Tests für Pipeline-Engine."""

import pytest
from app.pipelines import (
    PipelineDefinition,
    PipelineEngine,
    PipelineRun,
    PipelineStatus,
    PipelineStepDefinition,
    StepStatus,
)


def test_create_run():
    """Engine erstellt Run mit PENDING-Status."""
    steps = [
        PipelineStepDefinition("s1", "shell", {"command": "echo ok"}),
    ]
    defn = PipelineDefinition("p1", steps)
    engine = PipelineEngine()
    run = engine.create_run(defn)
    assert run.status == PipelineStatus.PENDING
    assert run.pipeline_id == "p1"
    assert len(run.step_runs) == 1
    assert run.step_runs[0].step_id == "s1"
    assert run.step_runs[0].status == StepStatus.PENDING


def test_execute_success():
    """Engine führt Schritte sequentiell aus und setzt COMPLETED."""
    steps = [
        PipelineStepDefinition("s1", "shell", {"command": "echo step1"}),
        PipelineStepDefinition("s2", "shell", {"command": "echo step2"}),
    ]
    defn = PipelineDefinition("p1", steps)
    engine = PipelineEngine()
    run = engine.create_run(defn)
    engine.execute(defn, run)
    assert run.status == PipelineStatus.COMPLETED
    assert run.step_runs[0].status == StepStatus.COMPLETED
    assert run.step_runs[1].status == StepStatus.COMPLETED
    assert run.started_at is not None
    assert run.completed_at is not None


def test_execute_failure_stops_pipeline():
    """Bei Fehler stoppt die Engine und setzt FAILED."""
    steps = [
        PipelineStepDefinition("s1", "shell", {"command": "echo ok"}),
        PipelineStepDefinition("s2", "shell", {"command": "exit 1"}),
        PipelineStepDefinition("s3", "shell", {"command": "echo never"}),
    ]
    defn = PipelineDefinition("p1", steps)
    engine = PipelineEngine()
    run = engine.create_run(defn)
    engine.execute(defn, run)
    assert run.status == PipelineStatus.FAILED
    assert run.step_runs[0].status == StepStatus.COMPLETED
    assert run.step_runs[1].status == StepStatus.FAILED
    assert run.step_runs[2].status == StepStatus.PENDING
    assert run.error is not None


def test_execute_unknown_executor_fails():
    """Unbekannter Executor-Typ führt zu FAILED."""
    steps = [
        PipelineStepDefinition("s1", "unknown_executor_type", {}),
    ]
    defn = PipelineDefinition("p1", steps)
    engine = PipelineEngine()
    run = engine.create_run(defn)
    engine.execute(defn, run)
    assert run.status == PipelineStatus.FAILED
    assert "unknown_executor_type" in (run.error or "")


def test_execute_collects_logs():
    """Engine sammelt Logs pro Schritt und gesamt."""
    steps = [
        PipelineStepDefinition("s1", "shell", {"command": "echo hello"}),
    ]
    defn = PipelineDefinition("p1", steps)
    engine = PipelineEngine()
    run = engine.create_run(defn)
    engine.execute(defn, run)
    assert len(run.logs) > 0
    assert any("hello" in log or "step" in log.lower() for log in run.logs)
    assert len(run.step_runs[0].logs) > 0


def test_execute_capture_artifact():
    """Engine erfasst Artefakte aus StepResult."""
    steps = [
        PipelineStepDefinition(
            "s1",
            "shell",
            {"command": "echo /tmp/out.png", "capture_stdout_as": "output_path"},
        ),
    ]
    defn = PipelineDefinition("p1", steps)
    engine = PipelineEngine()
    run = engine.create_run(defn)
    engine.execute(defn, run)
    assert run.status == PipelineStatus.COMPLETED
    arts = run.get_all_artifacts()
    assert len(arts) == 1
    assert arts[0].key == "output_path"
    assert "/tmp/out.png" in str(arts[0].value)


def test_create_run_with_custom_id():
    """create_run akzeptiert optionalen run_id."""
    defn = PipelineDefinition("p1", [PipelineStepDefinition("s1", "shell", {"command": "true"})])
    engine = PipelineEngine()
    run = engine.create_run(defn, run_id="custom_run_123")
    assert run.run_id == "custom_run_123"
