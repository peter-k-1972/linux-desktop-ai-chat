"""Unit-Tests für Pipeline-Executors."""

import pytest
from app.pipelines import (
    ExecutorRegistry,
    PlaceholderComfyUIExecutor,
    PlaceholderMediaExecutor,
    PythonCallableExecutor,
    ShellExecutor,
    StepResult,
    get_executor_registry,
)


def test_shell_executor_success():
    """Shell-Executor führt Befehl aus und liefert Erfolg."""
    ex = ShellExecutor()
    result = ex.execute("s1", {"command": "echo hello"}, {})
    assert result.success
    assert any("hello" in log for log in result.logs)


def test_shell_executor_failure():
    """Shell-Executor liefert Fehler bei exit code != 0."""
    ex = ShellExecutor()
    result = ex.execute("s1", {"command": "exit 1"}, {})
    assert not result.success
    assert result.error is not None


def test_shell_executor_missing_command():
    """Shell-Executor liefert Fehler ohne command."""
    ex = ShellExecutor()
    result = ex.execute("s1", {}, {})
    assert not result.success
    assert "command" in (result.error or "").lower()


def test_shell_executor_capture_stdout():
    """Shell-Executor kann stdout als Artefakt erfassen."""
    ex = ShellExecutor()
    result = ex.execute(
        "s1",
        {"command": "echo /path/to/file", "capture_stdout_as": "output"},
        {},
    )
    assert result.success
    assert len(result.artifacts) == 1
    assert result.artifacts[0].key == "output"
    assert "/path/to/file" in str(result.artifacts[0].value)


def test_python_executor_callable_direct():
    """Python-Executor führt Callable direkt aus."""

    def my_step(context):
        return True

    ex = PythonCallableExecutor()
    result = ex.execute("s1", {"callable": my_step}, {})
    assert result.success


def test_python_executor_returns_step_result():
    """Python-Executor akzeptiert StepResult als Rückgabe."""

    def my_step(context):
        return StepResult(success=True, logs=["custom log"])

    ex = PythonCallableExecutor()
    result = ex.execute("s1", {"callable": my_step}, {})
    assert result.success
    assert "custom log" in result.logs


def test_python_executor_missing_callable():
    """Python-Executor liefert Fehler ohne callable."""
    ex = PythonCallableExecutor()
    result = ex.execute("s1", {}, {})
    assert not result.success
    assert "callable" in (result.error or "").lower()


def test_placeholder_comfyui_executor():
    """Placeholder ComfyUI-Executor liefert Hinweis."""
    ex = PlaceholderComfyUIExecutor()
    result = ex.execute("s1", {"workflow": "xyz"}, {})
    assert not result.success
    assert "placeholder" in result.error.lower() or "not yet" in result.error.lower()


def test_placeholder_media_executor():
    """Placeholder Media-Executor liefert Hinweis."""
    ex = PlaceholderMediaExecutor()
    result = ex.execute("s1", {}, {})
    assert not result.success
    assert "placeholder" in result.error.lower() or "not yet" in result.error.lower()


def test_executor_registry_default_types():
    """Registry enthält Standard-Executor-Typen."""
    reg = get_executor_registry()
    assert reg.get("shell") is not None
    assert reg.get("python_callable") is not None
    assert reg.get("comfyui") is not None
    assert reg.get("media") is not None
    assert reg.get("cursor_light") is not None


def test_cursor_light_file_read(tmp_path):
    from app.pipelines.executors.cursor_light import CursorLightExecutor

    (tmp_path / "hello.txt").write_text("line1\nline2\n", encoding="utf-8")
    ex = CursorLightExecutor()
    sr = ex.execute(
        "s1",
        {
            "workspace_root": str(tmp_path),
            "tool_id": "cl.file.read",
            "input": {"path": "hello.txt"},
        },
        {},
    )
    assert sr.success
    out = sr.output
    assert out["success"] is True
    assert "line1" in out["data"]["content"]


def test_cursor_light_path_traversal_blocked(tmp_path):
    from app.pipelines.executors.cursor_light import CursorLightExecutor

    ex = CursorLightExecutor()
    sr = ex.execute(
        "s1",
        {
            "workspace_root": str(tmp_path),
            "tool_id": "cl.file.read",
            "input": {"path": "../etc/passwd"},
        },
        {},
    )
    assert sr.success
    assert sr.output["success"] is False
    assert sr.output["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def test_cursor_light_unknown_tool(tmp_path):
    from app.pipelines.executors.cursor_light import CursorLightExecutor

    ex = CursorLightExecutor()
    sr = ex.execute(
        "s1",
        {
            "workspace_root": str(tmp_path),
            "tool_id": "cl.nonexistent",
            "input": {},
        },
        {},
    )
    assert sr.success
    assert sr.output["success"] is False
    assert sr.output["error"]["code"] == "UNKNOWN_TOOL"


def test_executor_registry_unknown_type():
    """Registry liefert None für unbekannten Typ."""
    reg = ExecutorRegistry()
    assert reg.get("unknown") is None


def test_executor_registry_get_or_raise():
    """get_or_raise wirft bei unbekanntem Typ."""
    reg = ExecutorRegistry()
    reg.get("shell")
    with pytest.raises(ValueError, match="Unknown executor type"):
        reg.get_or_raise("unknown")
