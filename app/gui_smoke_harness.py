"""
Einheitlicher Smoke-Lauf für registrierte GUIs (QA / Release).

Kein Voll-E2E: Registrierung, Manifest/Kompatibilität, Entrypoint, kontrollierter Kurzstart.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from app.gui_registry import (
    GUI_ID_DEFAULT_WIDGET,
    GUI_ID_LIBRARY_QML,
    get_gui_descriptor,
    list_registered_gui_ids,
    resolve_repo_root,
)
from app.gui_smoke_constants import GUI_SMOKE_ENV
from app.qml_alternative_gui_validator import (
    assert_descriptor_matches_manifest_paths,
    validate_library_qml_gui_launch_context,
)


@dataclass(frozen=True, slots=True)
class GuiSmokeStep:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True, slots=True)
class GuiSmokeResult:
    gui_id: str
    ok: bool
    steps: tuple[GuiSmokeStep, ...]


def _step(name: str, ok: bool, detail: str) -> GuiSmokeStep:
    return GuiSmokeStep(name=name, ok=ok, detail=detail)


def check_manifest_path_exists(gui_id: str, repo_root: Path) -> GuiSmokeStep:
    """Prüft ``manifest_path`` laut Deskriptor (falls gesetzt)."""
    desc = get_gui_descriptor(gui_id)
    try:
        assert_descriptor_matches_manifest_paths(desc, repo_root)
    except FileNotFoundError as e:
        return _step("manifest_valid", False, str(e))
    if not desc.manifest_path:
        return _step("manifest_valid", True, "n/a (no manifest)")
    return _step("manifest_valid", True, desc.manifest_path)


def check_manifest_runtime_compatible(gui_id: str, repo_root: Path) -> GuiSmokeStep:
    """Kompatibilitätslisten / Shape wie beim Produktstart (nur bekannte qt_quick-GUIs)."""
    desc = get_gui_descriptor(gui_id)
    if desc.gui_type != "qt_quick":
        return _step("runtime_compatible", True, "n/a (not qt_quick)")
    if gui_id != GUI_ID_LIBRARY_QML:
        return _step(
            "runtime_compatible",
            False,
            f"no harness validator registered for qt_quick gui_id={gui_id!r}",
        )
    try:
        validate_library_qml_gui_launch_context(repo_root, expected_gui_id=gui_id)
    except Exception as e:
        return _step("runtime_compatible", False, str(e))
    return _step("runtime_compatible", True, "library_qml manifest OK")


def run_subprocess_smoke(gui_id: str, repo_root: Path, *, timeout_s: float = 120.0) -> GuiSmokeStep:
    """Startet den kanonischen Entrypoint mit Smoke-Env und offscreen Qt."""
    desc = get_gui_descriptor(gui_id)
    script = repo_root / desc.entrypoint
    if not script.is_file():
        return _step("subprocess_smoke", False, f"entrypoint missing: {script}")

    env = os.environ.copy()
    env["LINUX_DESKTOP_CHAT_SINGLE_INSTANCE"] = "0"
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env[GUI_SMOKE_ENV] = "1"

    cmd: list[str]
    if gui_id == GUI_ID_DEFAULT_WIDGET:
        cmd = [sys.executable, str(script), "--gui", GUI_ID_DEFAULT_WIDGET]
    else:
        cmd = [sys.executable, str(script)]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            env=env,
            timeout=timeout_s,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired:
        return _step("subprocess_smoke", False, f"timeout after {timeout_s}s")
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-500:]
        return _step(
            "subprocess_smoke",
            False,
            f"exit {proc.returncode}: {tail}",
        )
    return _step("subprocess_smoke", True, "exit 0")


def run_gui_smoke(
    gui_id: str,
    *,
    repo_root: Path | None = None,
    run_subprocess: bool = True,
    subprocess_timeout_s: float = 120.0,
) -> GuiSmokeResult:
    """
    Führt die Smoke-Kette für eine ``gui_id`` aus.

    Args:
        repo_root: Repo-Wurzel; Standard: ``resolve_repo_root()``.
        run_subprocess: Wenn False, entfällt der Kurzstart (nur statische Checks).
    """
    root = repo_root or resolve_repo_root()
    steps: list[GuiSmokeStep] = []

    try:
        desc = get_gui_descriptor(gui_id)
    except KeyError as e:
        return GuiSmokeResult(
            gui_id=gui_id,
            ok=False,
            steps=(_step("registered", False, str(e)),),
        )

    steps.append(_step("registered", True, f"{desc.display_name} ({desc.gui_type})"))

    ep = root / desc.entrypoint
    steps.append(
        _step(
            "entrypoint_exists",
            ep.is_file(),
            str(ep) if ep.is_file() else f"missing: {ep}",
        )
    )

    steps.append(check_manifest_path_exists(gui_id, root))
    steps.append(check_manifest_runtime_compatible(gui_id, root))

    if run_subprocess:
        steps.append(run_subprocess_smoke(gui_id, root, timeout_s=subprocess_timeout_s))

    ok = all(s.ok for s in steps)
    return GuiSmokeResult(gui_id=gui_id, ok=ok, steps=tuple(steps))


def run_all_registered_gui_smokes(
    *,
    repo_root: Path | None = None,
    run_subprocess: bool = True,
    subprocess_timeout_s: float = 120.0,
) -> tuple[GuiSmokeResult, ...]:
    """Smoke für alle ``list_registered_gui_ids()`` (deterministisch sortiert)."""
    results = [
        run_gui_smoke(
            gid,
            repo_root=repo_root,
            run_subprocess=run_subprocess,
            subprocess_timeout_s=subprocess_timeout_s,
        )
        for gid in sorted(list_registered_gui_ids())
    ]
    return tuple(results)
