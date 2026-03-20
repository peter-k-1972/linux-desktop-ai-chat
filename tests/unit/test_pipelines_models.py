"""Unit-Tests für Pipeline-Kernmodelle."""

import pytest
from datetime import datetime, timezone

from app.pipelines.models import (
    PipelineDefinition,
    PipelineStepDefinition,
    PipelineRun,
    PipelineStepRun,
    PipelineArtifact,
    PipelineStatus,
    StepStatus,
)


def test_pipeline_step_definition_default_name():
    """Step-Definition setzt name aus step_id wenn leer."""
    step = PipelineStepDefinition(step_id="s1", executor_type="shell")
    assert step.name == "s1"


def test_pipeline_step_definition_explicit_name():
    """Step-Definition behält expliziten name."""
    step = PipelineStepDefinition(step_id="s1", executor_type="shell", name="My Step")
    assert step.name == "My Step"


def test_pipeline_definition_default_name():
    """Pipeline-Definition setzt name aus pipeline_id wenn leer."""
    defn = PipelineDefinition(pipeline_id="p1", steps=[])
    assert defn.name == "p1"


def test_pipeline_definition_with_steps():
    """Pipeline-Definition enthält geordnete Schritte."""
    steps = [
        PipelineStepDefinition("s1", "shell", {"command": "echo 1"}),
        PipelineStepDefinition("s2", "python_callable", {"callable": "foo.bar"}),
    ]
    defn = PipelineDefinition("p1", steps, name="Test Pipeline")
    assert len(defn.steps) == 2
    assert defn.steps[0].step_id == "s1"
    assert defn.steps[1].step_id == "s2"


def test_pipeline_step_run_add_log():
    """StepRun sammelt Logs."""
    sr = PipelineStepRun(step_id="s1")
    sr.add_log("line 1")
    sr.add_log("line 2")
    assert sr.logs == ["line 1", "line 2"]


def test_pipeline_step_run_add_artifact():
    """StepRun sammelt Artefakte."""
    sr = PipelineStepRun(step_id="s1")
    sr.add_artifact(PipelineArtifact(step_id="s1", key="out", value="/tmp/out.png"))
    assert len(sr.artifacts) == 1
    assert sr.artifacts[0].key == "out"


def test_pipeline_run_get_step_run():
    """PipelineRun findet StepRun nach step_id."""
    sr1 = PipelineStepRun(step_id="s1")
    sr2 = PipelineStepRun(step_id="s2")
    run = PipelineRun(run_id="r1", pipeline_id="p1", step_runs=[sr1, sr2])
    assert run.get_step_run("s1") is sr1
    assert run.get_step_run("s2") is sr2
    assert run.get_step_run("s3") is None


def test_pipeline_run_get_all_artifacts():
    """PipelineRun aggregiert Artefakte aller Schritte."""
    sr1 = PipelineStepRun(step_id="s1")
    sr1.add_artifact(PipelineArtifact("s1", "a1", "v1"))
    sr2 = PipelineStepRun(step_id="s2")
    sr2.add_artifact(PipelineArtifact("s2", "a2", "v2"))
    run = PipelineRun(run_id="r1", pipeline_id="p1", step_runs=[sr1, sr2])
    arts = run.get_all_artifacts()
    assert len(arts) == 2
    assert arts[0].key == "a1"
    assert arts[1].key == "a2"


def test_pipeline_status_enum():
    """PipelineStatus hat erwartete Werte."""
    assert PipelineStatus.PENDING.value == "pending"
    assert PipelineStatus.RUNNING.value == "running"
    assert PipelineStatus.COMPLETED.value == "completed"
    assert PipelineStatus.FAILED.value == "failed"
    assert PipelineStatus.CANCELLED.value == "cancelled"


def test_step_status_enum():
    """StepStatus hat erwartete Werte."""
    assert StepStatus.PENDING.value == "pending"
    assert StepStatus.SKIPPED.value == "skipped"
