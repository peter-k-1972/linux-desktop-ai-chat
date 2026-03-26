"""Integrationstests für alle cl.* Tools (CursorLightExecutor)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from app.pipelines.executors.cursor_light import CursorLightExecutor


def _run(ex: CursorLightExecutor, tmp: Path, tool_id: str, inp: dict):
    return ex.execute(
        "step",
        {"workspace_root": str(tmp), "tool_id": tool_id, "input": inp},
        {},
    )


def test_cl_file_read_max_lines_and_metadata(tmp_path):
    (tmp_path / "a.txt").write_text("a\nb\nc\nd\n", encoding="utf-8")
    ex = CursorLightExecutor()
    sr = _run(ex, tmp_path, "cl.file.read", {"path": "a.txt", "max_lines": 2})
    assert sr.output["success"] is True
    assert "a\n" in sr.output["data"]["content"]
    assert "c" not in sr.output["data"]["content"]
    assert sr.output["data"]["truncated"] is True
    md = sr.output["metadata"]
    assert md.get("tool_id") == "cl.file.read"
    assert md.get("cwd")
    assert md.get("target_path") == "a.txt"
    assert md.get("truncated") is True
    assert "duration_ms" in md


def test_cl_file_read_max_bytes(tmp_path):
    (tmp_path / "b.txt").write_text("ü" * 100, encoding="utf-8")
    ex = CursorLightExecutor()
    sr = _run(ex, tmp_path, "cl.file.read", {"path": "b.txt", "max_bytes": 4})
    assert sr.output["success"] is True
    assert sr.output["data"]["truncated"] is True


def test_cl_file_write_and_read_roundtrip(tmp_path):
    ex = CursorLightExecutor()
    w = _run(
        ex,
        tmp_path,
        "cl.file.write",
        {"path": "sub/x.txt", "content": "ok\n", "create_dirs": True},
    )
    assert w.output["success"] is True
    assert w.output["data"]["bytes_written"] >= 3
    r = _run(ex, tmp_path, "cl.file.read", {"path": "sub/x.txt"})
    assert r.output["data"]["content"] == "ok\n"


def test_cl_file_write_path_escape(tmp_path):
    ex = CursorLightExecutor()
    sr = _run(
        ex,
        tmp_path,
        "cl.file.write",
        {"path": "../outside.txt", "content": "x"},
    )
    assert sr.output["success"] is False
    assert sr.output["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def test_cl_patch_replace_block_success(tmp_path):
    (tmp_path / "f.txt").write_text("hello world\n", encoding="utf-8")
    ex = CursorLightExecutor()
    sr = _run(
        ex,
        tmp_path,
        "cl.file.patch",
        {
            "mode": "replace_block",
            "path": "f.txt",
            "old_text": "world",
            "new_text": "there",
        },
    )
    assert sr.output["success"] is True
    assert (tmp_path / "f.txt").read_text() == "hello there\n"


def test_cl_patch_replace_block_ambiguous(tmp_path):
    (tmp_path / "a.txt").write_text("x\nx\n", encoding="utf-8")
    ex = CursorLightExecutor()
    sr = _run(
        ex,
        tmp_path,
        "cl.file.patch",
        {
            "mode": "replace_block",
            "path": "a.txt",
            "old_text": "x",
            "new_text": "y",
        },
    )
    assert sr.output["success"] is False
    assert sr.output["error"]["code"] == "AMBIGUOUS_MATCH"


def test_cl_patch_replace_block_no_match(tmp_path):
    (tmp_path / "a.txt").write_text("abc\n", encoding="utf-8")
    ex = CursorLightExecutor()
    sr = _run(
        ex,
        tmp_path,
        "cl.file.patch",
        {
            "mode": "replace_block",
            "path": "a.txt",
            "old_text": "zzz",
            "new_text": "y",
        },
    )
    assert sr.output["success"] is False
    assert sr.output["error"]["code"] == "NO_MATCH"


def test_cl_repo_search_literal(tmp_path):
    (tmp_path / "p").mkdir()
    (tmp_path / "p" / "one.py").write_text("foo = 1\n", encoding="utf-8")
    (tmp_path / "p" / "two.py").write_text("bar\n", encoding="utf-8")
    ex = CursorLightExecutor()
    sr = _run(
        ex,
        tmp_path,
        "cl.repo.search",
        {"pattern": "foo", "literal": True, "include_glob": ["*.py"]},
    )
    assert sr.output["success"] is True
    m = sr.output["data"]["matches"]
    assert len(m) == 1
    assert m[0]["path"].replace("\\", "/").endswith("one.py")


def test_cl_test_run_pytest(tmp_path):
    (tmp_path / "test_cl.py").write_text(
        "def test_ok():\n    assert 1 == 1\n",
        encoding="utf-8",
    )
    ex = CursorLightExecutor()
    sr = _run(
        ex,
        tmp_path,
        "cl.test.run",
        {"command_key": "pytest", "args": ["-q", "test_cl.py"], "timeout_sec": 120},
    )
    assert sr.output["success"] is True
    assert sr.output["data"]["exit_code"] == 0
    assert sr.output["metadata"].get("exit_code") == 0


def test_cl_test_run_unknown_key(tmp_path):
    ex = CursorLightExecutor()
    sr = _run(
        ex,
        tmp_path,
        "cl.test.run",
        {"command_key": "rm_rf", "args": []},
    )
    assert sr.output["success"] is False
    assert sr.output["error"]["code"] == "POLICY_DENIED"


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(path), check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "cl@test.local"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "cl test"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )


@pytest.mark.skipif(
    subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
    reason="git not available",
)
def test_cl_git_status_and_diff(tmp_path):
    _git_init(tmp_path)
    (tmp_path / "tracked.txt").write_text("v1\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(tmp_path),
        check=True,
        capture_output=True,
    )
    (tmp_path / "tracked.txt").write_text("v2\n", encoding="utf-8")

    ex = CursorLightExecutor()
    st = _run(ex, tmp_path, "cl.git.status", {"porcelain": True})
    assert st.output["success"] is True
    assert st.output["metadata"]["cwd"] == str(tmp_path.resolve())
    assert st.output["data"]["clean"] is False

    df = _run(ex, tmp_path, "cl.git.diff", {"scope": "working"})
    assert df.output["success"] is True
    assert "v2" in df.output["data"]["diff"] or "v1" in df.output["data"]["diff"]
    assert "truncated" in df.output["metadata"]


@pytest.mark.skipif(
    subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
    reason="git not available",
)
def test_cl_git_patch_unified_rejected(tmp_path):
    _git_init(tmp_path)
    (tmp_path / "a.txt").write_text("line1\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "c"],
        cwd=str(tmp_path),
        check=True,
        capture_output=True,
    )
    bad_patch = "this is not a valid unified diff"
    ex = CursorLightExecutor()
    sr = _run(ex, tmp_path, "cl.file.patch", {"patch": bad_patch, "strip": 1})
    assert sr.output["success"] is False
    assert sr.output["error"]["code"] in ("PATCH_REJECTED", "PATCH_FAILED", "PATCH_UNAVAILABLE")
