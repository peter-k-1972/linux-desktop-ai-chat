"""Tests für GUI-Registry, QML-Manifest-Governance, Validator und CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app import application_release_info
from app.core.startup_contract import (
    CANONICAL_GUI_CAPABILITIES,
    GUI_ID_DEFAULT_WIDGET,
    GUI_ID_LIBRARY_QML,
    REGISTERED_GUIS_BY_ID,
    get_capabilities_for_gui_id,
    get_gui_descriptor,
    gui_supports,
    list_registered_gui_ids,
    list_valid_gui_cli_tokens,
    resolve_active_gui_id,
    resolve_repo_root,
    resolve_user_gui_choice,
    validate_registered_gui_capabilities,
)
from app.gui_smoke_harness import (
    check_manifest_path_exists,
    check_manifest_runtime_compatible,
    run_gui_smoke,
)
from app.qml_alternative_gui_validator import validate_library_qml_gui_launch_context
from app.qml_theme_governance import (
    assert_qml_theme_runtime_compatible,
    validate_qml_theme_for_repo,
    validate_qml_theme_manifest_shape,
)


def test_registry_contains_default_and_library_qml():
    ids = list_registered_gui_ids()
    assert GUI_ID_DEFAULT_WIDGET in ids
    assert GUI_ID_LIBRARY_QML in ids
    d0 = get_gui_descriptor(GUI_ID_DEFAULT_WIDGET)
    assert d0.is_default_fallback is True
    assert d0.gui_type == "pyside6"
    dq = get_gui_descriptor(GUI_ID_LIBRARY_QML)
    assert dq.manifest_path == "qml/theme_manifest.json"
    assert dq.gui_type == "qt_quick"


def test_registry_capabilities_match_canonical():
    validate_registered_gui_capabilities(REGISTERED_GUIS_BY_ID)
    for gid, caps in CANONICAL_GUI_CAPABILITIES.items():
        assert get_gui_descriptor(gid).capabilities == caps


def test_gui_supports_api():
    assert gui_supports(GUI_ID_DEFAULT_WIDGET, "supports_command_palette") is True
    assert gui_supports(GUI_ID_LIBRARY_QML, "supports_command_palette") is False
    assert gui_supports(GUI_ID_LIBRARY_QML, "supports_chat") is True
    assert get_capabilities_for_gui_id(GUI_ID_DEFAULT_WIDGET).supports_theme_switching is True
    with pytest.raises(ValueError, match="Unknown GUI capability"):
        gui_supports(GUI_ID_DEFAULT_WIDGET, "supports_not_a_real_flag")
    with pytest.raises(KeyError):
        gui_supports("nonexistent_gui_xyz", "supports_chat")


def test_registry_entrypoints_exist():
    root = resolve_repo_root()
    for desc in REGISTERED_GUIS_BY_ID.values():
        ep = root / desc.entrypoint
        assert ep.is_file(), f"Missing entrypoint {ep}"


def test_resolve_user_gui_choice_accepts_aliases_and_ids():
    assert resolve_user_gui_choice("default") == GUI_ID_DEFAULT_WIDGET
    assert resolve_user_gui_choice("library_qml_gui") == GUI_ID_LIBRARY_QML
    assert resolve_user_gui_choice("bogus") is None


def test_qml_theme_manifest_in_repo_validates():
    root = resolve_repo_root()
    data = validate_qml_theme_for_repo(
        root,
        app_version=application_release_info.APP_RELEASE_VERSION,
        backend_version=application_release_info.BACKEND_BUNDLE_VERSION,
        contract_version=application_release_info.UI_CONTRACTS_RELEASE_VERSION,
        bridge_version=application_release_info.BRIDGE_INTERFACE_VERSION,
    )
    assert data["theme_id"] == GUI_ID_LIBRARY_QML
    assert data["theme_version"] == "0.1.0"


def test_validate_library_qml_launch_context_matches_registry():
    root = resolve_repo_root()
    data = validate_library_qml_gui_launch_context(root)
    assert data["theme_id"] == GUI_ID_LIBRARY_QML


def test_qml_theme_manifest_rejects_wrong_app_version(tmp_path: Path):
    mf = tmp_path / "theme_manifest.json"
    mf.write_text(
        json.dumps(
            {
                "theme_id": GUI_ID_LIBRARY_QML,
                "theme_name": "x",
                "theme_version": "1.0.0",
                "foundation_version": "1",
                "shell_version": "1",
                "bridge_version": "1",
                "domain_versions": {
                    "chat": "1",
                    "projects": "1",
                    "workflows": "1",
                    "prompts": "1",
                    "agents": "1",
                    "deployment": "1",
                    "settings": "1",
                },
                "compatible_app_versions": ["99.0.0"],
                "compatible_backend_versions": [application_release_info.BACKEND_BUNDLE_VERSION],
                "compatible_contract_versions": [application_release_info.UI_CONTRACTS_RELEASE_VERSION],
                "compatible_bridge_versions": [application_release_info.BRIDGE_INTERFACE_VERSION],
                "release_status": "draft",
            }
        ),
        encoding="utf-8",
    )
    qml_dir = tmp_path / "qml"
    qml_dir.mkdir()
    import shutil

    shutil.copy(mf, qml_dir / "theme_manifest.json")
    with pytest.raises(ValueError, match="not in compatible_app_versions"):
        validate_qml_theme_for_repo(
            tmp_path,
            app_version=application_release_info.APP_RELEASE_VERSION,
            backend_version=application_release_info.BACKEND_BUNDLE_VERSION,
            contract_version=application_release_info.UI_CONTRACTS_RELEASE_VERSION,
            bridge_version=application_release_info.BRIDGE_INTERFACE_VERSION,
        )


def test_qml_theme_manifest_rejects_theme_id_mismatch(tmp_path: Path):
    mf = tmp_path / "qml" / "theme_manifest.json"
    mf.parent.mkdir(parents=True)
    mf.write_text(
        json.dumps(
            {
                "theme_id": "wrong_id",
                "theme_name": "x",
                "theme_version": "0.1.0",
                "foundation_version": "0.1.0",
                "shell_version": "0.1.0",
                "bridge_version": "0.1.0",
                "domain_versions": {
                    "chat": "0.1.0",
                    "projects": "0.1.0",
                    "workflows": "0.1.0",
                    "prompts": "0.1.0",
                    "agents": "0.1.0",
                    "deployment": "0.1.0",
                    "settings": "0.1.0",
                },
                "compatible_app_versions": [application_release_info.APP_RELEASE_VERSION],
                "compatible_backend_versions": [application_release_info.BACKEND_BUNDLE_VERSION],
                "compatible_contract_versions": [application_release_info.UI_CONTRACTS_RELEASE_VERSION],
                "compatible_bridge_versions": [application_release_info.BRIDGE_INTERFACE_VERSION],
                "release_status": "candidate",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="theme_id mismatch"):
        validate_library_qml_gui_launch_context(tmp_path)


def test_resolve_active_gui_id_cli_wins(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("LINUX_DESKTOP_CHAT_GUI", raising=False)
    assert resolve_active_gui_id(cli_gui="default") == GUI_ID_DEFAULT_WIDGET
    assert resolve_active_gui_id(cli_gui="library_qml") == GUI_ID_LIBRARY_QML


def test_resolve_active_gui_id_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LINUX_DESKTOP_CHAT_GUI", "library_qml")
    assert resolve_active_gui_id(cli_gui=None) == GUI_ID_LIBRARY_QML


def test_run_gui_shell_help_lists_gui_flag():
    root = resolve_repo_root()
    proc = subprocess.run(
        [sys.executable, str(root / "run_gui_shell.py"), "--help"],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0
    assert "--gui" in proc.stdout


def test_run_gui_shell_unknown_gui_exits_nonzero():
    root = resolve_repo_root()
    proc = subprocess.run(
        [sys.executable, str(root / "run_gui_shell.py"), "--gui", "not_a_real_gui_xyz"],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 2


def test_try_start_qt_quick_subprocess_invocation(monkeypatch: pytest.MonkeyPatch):
    root = resolve_repo_root()
    calls: list[list[str]] = []

    def fake_run(cmd, cwd=None, **kwargs):
        calls.append(list(cmd))

        class R:
            returncode = 0

        return R()

    import run_gui_shell

    monkeypatch.setattr(run_gui_shell.subprocess, "run", fake_run)
    desc = get_gui_descriptor(GUI_ID_LIBRARY_QML)
    assert run_gui_shell._try_start_qt_quick_gui(root, desc) is True
    assert calls and str(root / "run_qml_shell.py") in calls[0][1]


def test_manifest_shape_requires_domain_keys():
    base = {
        "theme_id": "t",
        "theme_name": "t",
        "theme_version": "0.1.0",
        "foundation_version": "0.1.0",
        "shell_version": "0.1.0",
        "bridge_version": "0.1.0",
        "domain_versions": {"chat": "0.1.0"},
        "compatible_app_versions": ["0.9.1"],
        "compatible_backend_versions": ["0.9.1"],
        "compatible_contract_versions": ["0.9.1"],
        "compatible_bridge_versions": ["0.1.0"],
        "release_status": "candidate",
    }
    with pytest.raises(ValueError, match="domain_versions missing"):
        validate_qml_theme_manifest_shape(base)


def test_assert_runtime_compatible_requires_bridge():
    data = {
        "theme_id": "t",
        "theme_name": "t",
        "theme_version": "0.1.0",
        "foundation_version": "0.1.0",
        "shell_version": "0.1.0",
        "bridge_version": "0.1.0",
        "domain_versions": {
            "chat": "0.1.0",
            "projects": "0.1.0",
            "workflows": "0.1.0",
            "prompts": "0.1.0",
            "agents": "0.1.0",
            "deployment": "0.1.0",
            "settings": "0.1.0",
        },
        "compatible_app_versions": ["0.9.1"],
        "compatible_backend_versions": ["0.9.1"],
        "compatible_contract_versions": ["0.9.1"],
        "compatible_bridge_versions": ["0.1.0"],
        "release_status": "candidate",
    }
    validate_qml_theme_manifest_shape(data)
    assert_qml_theme_runtime_compatible(
        data,
        app_version="0.9.1",
        backend_version="0.9.1",
        contract_version="0.9.1",
        bridge_version="0.1.0",
    )
    with pytest.raises(ValueError, match="compatible_bridge_versions"):
        assert_qml_theme_runtime_compatible(
            data,
            app_version="0.9.1",
            backend_version="0.9.1",
            contract_version="0.9.1",
            bridge_version="99.0.0",
        )


def test_list_valid_gui_cli_tokens_nonempty():
    assert "default" in list_valid_gui_cli_tokens()
    assert "library_qml_gui" in list_valid_gui_cli_tokens()


def test_smoke_harness_static_steps():
    root = resolve_repo_root()
    for gid in list_registered_gui_ids():
        r = run_gui_smoke(gid, repo_root=root, run_subprocess=False)
        assert r.ok, r.steps
        names = [s.name for s in r.steps]
        assert "registered" in names
        assert "manifest_valid" in names
        assert "runtime_compatible" in names


def test_smoke_manifest_steps_for_widget_vs_qml():
    root = resolve_repo_root()
    w_manifest = check_manifest_path_exists(GUI_ID_DEFAULT_WIDGET, root)
    assert w_manifest.ok and "n/a" in w_manifest.detail
    q_manifest = check_manifest_path_exists(GUI_ID_LIBRARY_QML, root)
    assert q_manifest.ok
    w_rt = check_manifest_runtime_compatible(GUI_ID_DEFAULT_WIDGET, root)
    assert w_rt.ok and "n/a" in w_rt.detail
    q_rt = check_manifest_runtime_compatible(GUI_ID_LIBRARY_QML, root)
    assert q_rt.ok


@pytest.mark.gui_smoke
def test_smoke_subprocess_all_registered():
    root = resolve_repo_root()
    results = [
        run_gui_smoke(gid, repo_root=root, run_subprocess=True, subprocess_timeout_s=180.0)
        for gid in sorted(list_registered_gui_ids())
    ]
    for r in results:
        assert r.ok, (r.gui_id, r.steps)
