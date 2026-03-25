"""Minimale Laufzeit-Smokes — nur wenn Host ``app.context`` installiert ist."""

from __future__ import annotations

import pytest


def test_context_replay_api_when_host_installed() -> None:
    try:
        from app.cli.context_replay import run_replay
    except ImportError as exc:
        pytest.skip(f"app.context nicht verfügbar (isolierter CLI-Test): {exc}")
    assert callable(run_replay)


def test_context_repro_apis_when_host_installed() -> None:
    try:
        from app.cli.context_repro_batch import run_repro_batch
        from app.cli.context_repro_run import run_repro
    except ImportError as exc:
        pytest.skip(f"app.context nicht verfügbar (isolierter CLI-Test): {exc}")
    assert callable(run_repro)
    assert callable(run_repro_batch)


def test_registry_cli_apis_when_host_installed() -> None:
    try:
        from app.cli.context_repro_registry_list import run_registry_list
        from app.cli.context_repro_registry_rebuild import run_registry_rebuild
        from app.cli.context_repro_registry_set_status import run_registry_set_status
    except ImportError as exc:
        pytest.skip(f"app.context nicht verfügbar (isolierter CLI-Test): {exc}")
    assert callable(run_registry_list)
    assert callable(run_registry_rebuild)
    assert callable(run_registry_set_status)
