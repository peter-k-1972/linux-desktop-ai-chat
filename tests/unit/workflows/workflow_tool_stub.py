"""Sync-Stubs für tool_call / python_callable in Workflow-Tests."""

from __future__ import annotations

from typing import Any, Dict

from app.pipelines.executors.base import StepResult


def stub_concat_tool(context: Dict[str, Any]) -> StepResult:
    a = context.get("a", "")
    b = context.get("b", "")
    return StepResult(success=True, output={"tool_result": f"{a}{b}"})


def stub_fail_tool(context: Dict[str, Any]) -> StepResult:
    return StepResult(success=False, error="stub_absichtlich_fehlgeschlagen")
