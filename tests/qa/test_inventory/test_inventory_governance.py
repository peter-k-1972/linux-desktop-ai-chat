"""
QA Test Inventory – Governance-Sicherheit.

- Generator verändert keine anderen QA-Artefakte
- incidents/* bleibt unverändert
- Keine Replay-/Regression-Dateien werden angefasst
"""

from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_build_test_inventory

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DOCS_QA = _PROJECT_ROOT / "docs" / "qa"
INCIDENTS_DIR = DOCS_QA / "incidents"


def _get_mtime(path: Path) -> float:
    """Modifikationszeit oder 0 wenn nicht existiert."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


@pytest.mark.unit
def test_dry_run_writes_no_files(minimal_catalog_path: Path, tmp_path: Path) -> None:
    """Dry-Run schreibt keine Dateien."""
    out_path = tmp_path / "QA_TEST_INVENTORY.json"
    exit_code, _, _ = run_build_test_inventory(
        [
            "--dry-run",
            "--output", str(out_path),
            "--catalog", str(minimal_catalog_path),
        ],
    )
    assert exit_code == 0
    assert not out_path.exists()


@pytest.mark.unit
def test_output_only_writes_specified_file(minimal_catalog_path: Path, tmp_path: Path) -> None:
    """Nur die angegebene Output-Datei wird geschrieben."""
    out_path = tmp_path / "inventory_output.json"
    before_incidents = _get_mtime(INCIDENTS_DIR / "index.json") if (INCIDENTS_DIR / "index.json").exists() else 0
    before_analytics = _get_mtime(INCIDENTS_DIR / "analytics.json") if (INCIDENTS_DIR / "analytics.json").exists() else 0

    exit_code, _, _ = run_build_test_inventory(
        [
            "--output", str(out_path),
            "--catalog", str(minimal_catalog_path),
        ],
    )
    assert exit_code == 0
    assert out_path.exists()

    after_incidents = _get_mtime(INCIDENTS_DIR / "index.json") if (INCIDENTS_DIR / "index.json").exists() else 0
    after_analytics = _get_mtime(INCIDENTS_DIR / "analytics.json") if (INCIDENTS_DIR / "analytics.json").exists() else 0

    assert before_incidents == after_incidents, "incidents/index.json wurde verändert"
    assert before_analytics == after_analytics, "incidents/analytics.json wurde verändert"


@pytest.mark.unit
def test_incidents_directory_not_modified(minimal_catalog_path: Path, tmp_path: Path) -> None:
    """incidents/ wird nicht modifiziert."""
    if not INCIDENTS_DIR.exists():
        pytest.skip("incidents/ existiert nicht")
    before = {}
    for f in INCIDENTS_DIR.rglob("*"):
        if f.is_file():
            before[str(f)] = _get_mtime(f)

    out_path = tmp_path / "inv.json"
    run_build_test_inventory(
        ["--output", str(out_path), "--catalog", str(minimal_catalog_path)],
    )

    for path_str, mtime_before in before.items():
        mtime_after = _get_mtime(Path(path_str))
        assert mtime_before == mtime_after, f"{path_str} wurde verändert"


@pytest.mark.unit
def test_no_replay_or_bindings_written(minimal_catalog_path: Path, tmp_path: Path) -> None:
    """Keine replay.yaml oder bindings.json werden im Output-Verzeichnis erzeugt."""
    out_path = tmp_path / "inv.json"
    run_build_test_inventory(
        ["--output", str(out_path), "--catalog", str(minimal_catalog_path)],
    )
    for name in ["replay.yaml", "bindings.json"]:
        for f in tmp_path.rglob(name):
            pytest.fail(f"Unerwartet erzeugt: {f}")


@pytest.mark.unit
def test_regression_catalog_not_modified(minimal_catalog_path: Path, tmp_path: Path) -> None:
    """REGRESSION_CATALOG wird nur gelesen, nicht geschrieben."""
    real_catalog = DOCS_QA / "REGRESSION_CATALOG.md"
    if not real_catalog.exists():
        pytest.skip("REGRESSION_CATALOG.md existiert nicht")
    before = _get_mtime(real_catalog)

    out_path = tmp_path / "inv.json"
    run_build_test_inventory(
        ["--output", str(out_path)],
    )

    after = _get_mtime(real_catalog)
    assert before == after, "REGRESSION_CATALOG.md wurde verändert"
