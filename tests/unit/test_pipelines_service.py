"""Unit-Tests für Pipeline-Service."""

import pytest
from app.pipelines.models import PipelineDefinition, PipelineStepDefinition, PipelineStatus
from app.pipelines.services.pipeline_service import PipelineService


def test_create_run():
    """Service erstellt Run und speichert ihn."""
    steps = [PipelineStepDefinition("s1", "shell", {"command": "echo ok"})]
    defn = PipelineDefinition("p1", steps)
    svc = PipelineService()
    run = svc.create_run(defn)
    assert run.status == PipelineStatus.PENDING
    assert svc.get_run(run.run_id) is run


def test_start_run():
    """Service startet Run und führt aus."""
    steps = [PipelineStepDefinition("s1", "shell", {"command": "echo done"})]
    defn = PipelineDefinition("p1", steps)
    svc = PipelineService()
    svc.register_definition(defn)
    run = svc.create_run(defn)
    svc.start_run(run)
    assert run.status == PipelineStatus.COMPLETED


def test_start_run_with_explicit_definition():
    """start_run akzeptiert explizite Definition."""
    steps = [PipelineStepDefinition("s1", "shell", {"command": "true"})]
    defn = PipelineDefinition("p1", steps)
    svc = PipelineService()
    run = svc.create_run(defn)
    svc.start_run(run, definition=defn)
    assert run.status == PipelineStatus.COMPLETED


def test_start_run_unknown_pipeline_fails():
    """start_run ohne Definition und ohne Registrierung schlägt fehl."""
    defn = PipelineDefinition("unknown", [PipelineStepDefinition("s1", "shell", {"command": "true"})])
    svc = PipelineService()
    run = svc.create_run(defn)
    svc.start_run(run)  # Keine Definition registriert
    assert run.status == PipelineStatus.FAILED
    assert "unknown" in (run.error or "")


def test_list_runs():
    """list_runs liefert gespeicherte Runs."""
    defn = PipelineDefinition("p1", [PipelineStepDefinition("s1", "shell", {"command": "true"})])
    svc = PipelineService()
    r1 = svc.create_run(defn, run_id="r1")
    r2 = svc.create_run(defn, run_id="r2")
    runs = svc.list_runs()
    assert len(runs) >= 2
    ids = {r.run_id for r in runs}
    assert "r1" in ids
    assert "r2" in ids


def test_list_runs_filter_by_pipeline_id():
    """list_runs filtert nach pipeline_id."""
    defn1 = PipelineDefinition("p1", [PipelineStepDefinition("s1", "shell", {"command": "true"})])
    defn2 = PipelineDefinition("p2", [PipelineStepDefinition("s1", "shell", {"command": "true"})])
    svc = PipelineService()
    svc.create_run(defn1, run_id="r1")
    svc.create_run(defn2, run_id="r2")
    runs = svc.list_runs(pipeline_id="p1")
    assert all(r.pipeline_id == "p1" for r in runs)


def test_cancel_run():
    """cancel_run setzt Abbruch-Flag (Run muss existieren)."""
    defn = PipelineDefinition("p1", [PipelineStepDefinition("s1", "shell", {"command": "sleep 10"})])
    svc = PipelineService()
    run = svc.create_run(defn, run_id="cancel_test")
    ok = svc.cancel_run("cancel_test")
    assert ok is True
    assert svc.cancel_run("nonexistent") is False
