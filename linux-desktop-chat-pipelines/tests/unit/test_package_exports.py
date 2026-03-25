"""Smoke: installiertes Paket app.pipelines ist importierbar (ohne Host)."""


def test_root_exports():
    from app.pipelines import (
        PipelineArtifact,
        PipelineDefinition,
        PipelineEngine,
        PipelineRun,
        PipelineService,
        PipelineStatus,
        PipelineStepDefinition,
        PipelineStepRun,
        StepStatus,
        get_executor_registry,
    )

    assert PipelineEngine is not None
    assert get_executor_registry() is not None
    assert PipelineStatus.PENDING.value == "pending"
    _ = PipelineArtifact("s", "k", "v")
