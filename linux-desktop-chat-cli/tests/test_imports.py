"""Smoke: Paket ``app.cli`` und erwarteter Quellbaum (ohne Host-Domäne)."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_CLI = _ROOT / "src" / "app" / "cli"

_EXPECTED_PY = frozenset(
    {
        "__init__.py",
        "context_replay.py",
        "context_repro_run.py",
        "context_repro_batch.py",
        "context_repro_registry_list.py",
        "context_repro_registry_rebuild.py",
        "context_repro_registry_set_status.py",
    }
)


def test_cli_package_importable() -> None:
    import app.cli

    assert hasattr(app.cli, "__path__")


def test_cli_source_tree_has_expected_modules() -> None:
    names = {p.name for p in _CLI.glob("*.py")}
    assert _EXPECTED_PY <= names
