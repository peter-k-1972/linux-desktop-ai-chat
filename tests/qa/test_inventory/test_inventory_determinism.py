"""
QA Test Inventory – Determinismus.

- Gleicher Input => gleicher Output
- --timestamp macht reproduzierbar
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from .conftest import run_build_test_inventory


def _get_stdout_json(exit_code: int, stdout: str, stderr: str) -> dict:
    """Parst stdout als JSON. Assert bei Fehler."""
    assert exit_code == 0, f"stderr: {stderr}"
    return json.loads(stdout)


@pytest.mark.unit
def test_same_timestamp_same_output(minimal_catalog_path: Path) -> None:
    """Zwei Läufe mit gleichem --timestamp liefern identischen Output."""
    args = [
        "--dry-run",
        "--output", "-",
        "--catalog", str(minimal_catalog_path),
        "--timestamp", "2026-01-01T00:00:00Z",
    ]
    ec1, out1, err1 = run_build_test_inventory(args)
    ec2, out2, err2 = run_build_test_inventory(args)

    data1 = _get_stdout_json(ec1, out1, err1)
    data2 = _get_stdout_json(ec2, out2, err2)

    json1 = json.dumps(data1, sort_keys=True)
    json2 = json.dumps(data2, sort_keys=True)
    assert json1 == json2, "Determinismus verletzt: gleicher Input liefert unterschiedlichen Output"


@pytest.mark.unit
def test_determinism_hash_stable(minimal_catalog_path: Path) -> None:
    """Output-Hash ist bei gleichem Timestamp stabil."""
    args = [
        "--dry-run",
        "--output", "-",
        "--catalog", str(minimal_catalog_path),
        "--timestamp", "2026-01-01T00:00:00Z",
    ]
    hashes = []
    for _ in range(2):
        ec, out, err = run_build_test_inventory(args)
        assert ec == 0, err
        data = json.loads(out)
        canonical = json.dumps(data, sort_keys=True)
        hashes.append(hashlib.sha256(canonical.encode()).hexdigest())
    assert hashes[0] == hashes[1]


@pytest.mark.unit
def test_tests_sorted_deterministically(minimal_catalog_path: Path) -> None:
    """Tests sind nach (file_path, test_name) sortiert."""
    args = [
        "--dry-run",
        "--output", "-",
        "--catalog", str(minimal_catalog_path),
        "--timestamp", "2026-01-01T00:00:00Z",
    ]
    ec, out, err = run_build_test_inventory(args)
    data = _get_stdout_json(ec, out, err)
    tests = data.get("tests", [])
    sorted_ref = sorted(tests, key=lambda t: (t["file_path"], t["test_name"]))
    assert tests == sorted_ref
