#!/usr/bin/env python3
"""
QA Test Inventory Generator – Linux Desktop Chat.

Discovert die pytest-Landschaft, erzeugt maschinenlesbares Inventar.
Phase 1 – Learning-QA-Architektur.

Output: docs/qa/artifacts/json/QA_TEST_INVENTORY.json

Verwendung:
  python scripts/qa/build_test_inventory.py
  python scripts/qa/build_test_inventory.py --dry-run
  python scripts/qa/build_test_inventory.py --output -
"""

from __future__ import annotations

import argparse
from typing import Any
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

from scripts.qa.qa_paths import DOCS_QA, ARTIFACTS_JSON, GOVERNANCE

DEFAULT_DOCS_QA = DOCS_QA
DEFAULT_OUTPUT = ARTIFACTS_JSON / "QA_TEST_INVENTORY.json"


def _collect_pytest_items() -> list:
    """Sammelt pytest-Test-Items via Plugin."""
    try:
        import io
        import pytest
    except ImportError:
        LOG.warning("pytest nicht installiert – Fallback auf Datei-Discovery")
        return []

    class CollectPlugin:
        def __init__(self) -> None:
            self.items: list[Any] = []

        def pytest_collection_modifyitems(self, session: Any, config: Any, items: list[Any]) -> None:
            self.items = list(items)

    plugin = CollectPlugin()
    # Pytest --collect-only schreibt auf stdout; umleiten, damit --output - sauberes JSON liefert
    _old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        exit_code = pytest.main(
            ["--collect-only", "-q", str(_PROJECT_ROOT / "tests")],
            plugins=[plugin],
        )
    finally:
        sys.stdout = _old_stdout
    if exit_code != 0:
        LOG.warning("pytest collection exit code %s", exit_code)
    return plugin.items


def _fallback_collect_tests() -> list[tuple[str, str, str]]:
    """
    Fallback: Datei-Walk + einfache test_*-Funktion-Erkennung.
    Returns [(nodeid, file_path, test_name), ...]
    """
    tests_dir = _PROJECT_ROOT / "tests"
    if not tests_dir.exists():
        return []

    results: list[tuple[str, str, str]] = []
    for py_file in tests_dir.rglob("test_*.py"):
        if "conftest" in str(py_file) or "__pycache__" in str(py_file):
            continue
        rel = py_file.relative_to(_PROJECT_ROOT)
        try:
            content = py_file.read_text(encoding="utf-8")
            import ast
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    nodeid = f"{rel}::{node.name}"
                    results.append((str(nodeid), str(rel), node.name))
        except (SyntaxError, OSError):
            continue
    return results


def _get_markers_from_item(item: Any) -> list[str]:
    """Extrahiert Marker-Namen von pytest Item."""
    markers = []
    try:
        for m in item.iter_markers():
            markers.append(m.name)
    except Exception:
        pass
    return markers


def build_inventory(
    optional_timestamp: str | None = None,
    catalog_path: Path | None = None,
) -> tuple[dict[str, Any], dict[str, int]]:
    """
    Baut das vollständige Inventar.
    Returns (output_dict, summary_counts).
    """
    from scripts.qa.test_inventory_models import InventoryOutput, TestEntry
    from scripts.qa.test_inventory_rules import (
        derive_execution_mode,
        derive_guard_types,
        derive_subsystem,
        derive_test_domain,
        derive_test_type,
        lookup_failure_classes,
        parse_regression_catalog,
        requires_manual_review,
    )

    generated_at = (
        optional_timestamp
        if optional_timestamp is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    input_sources = ["pytest"]
    catalog: dict[tuple[str, str], dict[str, list[str]]] = {}
    catalog_path = catalog_path or GOVERNANCE / "REGRESSION_CATALOG.md"
    if catalog_path.exists():
        catalog = parse_regression_catalog(catalog_path.read_text(encoding="utf-8"))
        try:
            input_sources.append(str(catalog_path.resolve().relative_to(_PROJECT_ROOT.resolve())))
        except ValueError:
            input_sources.append(str(catalog_path))

    items = _collect_pytest_items()
    use_fallback = not items

    if use_fallback:
        fallback_items = _fallback_collect_tests()
        input_sources.append("fallback_file_walk")
    else:
        fallback_items = []

    tests: list[TestEntry] = []
    summary_counts: dict[str, int] = {
        "by_test_type": {},
        "by_test_domain": {},
        "by_subsystem": {},
        "manual_review_required": 0,
        "covers_regression": 0,
        "catalog_bound_failure_class": 0,
    }

    def process_test(nodeid: str, file_path: str, test_name: str, markers: list[str]) -> None:
        test_domain = derive_test_domain(file_path)
        test_type, type_source = derive_test_type(markers, test_domain)
        subsystem, sub_source = derive_subsystem(file_path, test_name)
        guard_types = derive_guard_types(test_type)
        execution_mode = derive_execution_mode(markers)
        covers_regression = "regression" in markers or test_domain == "regression"

        file_stem = Path(file_path).stem
        failure_classes, fc_source = lookup_failure_classes(
            catalog, test_domain, file_stem, test_name
        )
        if failure_classes:
            summary_counts["catalog_bound_failure_class"] += 1

        manual_review = requires_manual_review(
            test_domain, test_type, subsystem, file_path, test_name
        )
        if manual_review:
            summary_counts["manual_review_required"] += 1
        if covers_regression:
            summary_counts["covers_regression"] += 1

        inference_confidence: dict[str, str] = {}
        inference_sources: dict[str, str] = {}
        inference_confidence["test_type"] = "high" if type_source == "discovered" else "medium"
        inference_sources["test_type"] = type_source
        inference_confidence["subsystem"] = "high" if sub_source == "inferred" else "low"
        inference_sources["subsystem"] = sub_source
        inference_confidence["failure_class"] = "high" if fc_source == "catalog_bound" else "low"
        inference_sources["failure_class"] = fc_source

        summary_counts["by_test_type"][test_type] = summary_counts["by_test_type"].get(test_type, 0) + 1
        summary_counts["by_test_domain"][test_domain] = summary_counts["by_test_domain"].get(test_domain, 0) + 1
        sub_key = subsystem or "unknown"
        summary_counts["by_subsystem"][sub_key] = summary_counts["by_subsystem"].get(sub_key, 0) + 1

        test_id = nodeid.replace("::", "__").replace("/", "_").replace("\\", "_")
        if not test_id.startswith("tests_"):
            test_id = "tests_" + test_id

        entry = TestEntry(
            test_id=test_id,
            test_name=test_name,
            pytest_nodeid=nodeid,
            file_path=file_path,
            test_type=test_type,
            execution_mode=execution_mode,
            test_domain=test_domain,
            markers=markers,
            subsystem=subsystem,
            component=None,
            failure_classes=failure_classes,
            guard_types=guard_types,
            covers_regression=covers_regression,
            covers_replay="unknown",
            regression_ids=[],
            replay_ids=[],
            inference_confidence=inference_confidence,
            inference_sources=inference_sources,
            manual_review_required=manual_review,
            notes=None,
        )
        tests.append(entry)

    if items:
        for item in items:
            nodeid = getattr(item, "nodeid", "")
            if not nodeid:
                continue
            if "::" in nodeid:
                path_part, name_part = nodeid.rsplit("::", 1)
                file_path = path_part
                test_name = name_part
            else:
                file_path = nodeid
                test_name = ""
            if not test_name or not test_name.startswith("test_"):
                continue
            markers = _get_markers_from_item(item)
            process_test(nodeid, file_path, test_name, markers)
    else:
        for nodeid, file_path, test_name in fallback_items:
            process_test(nodeid, file_path, test_name, [])

    tests.sort(key=lambda t: (t.file_path, t.test_name))

    summary = {
        "test_count": len(tests),
        "by_test_type": summary_counts["by_test_type"],
        "by_test_domain": summary_counts["by_test_domain"],
        "by_subsystem": summary_counts["by_subsystem"],
        "manual_review_required_count": summary_counts["manual_review_required"],
        "covers_regression_count": summary_counts["covers_regression"],
        "catalog_bound_failure_class_count": summary_counts["catalog_bound_failure_class"],
    }

    output = InventoryOutput(
        schema_version="1.0",
        generated_at=generated_at,
        input_sources=input_sources,
        summary=summary,
        tests=tests,
    )
    output_dict = output.to_dict()
    # Phase 3: Semantische Anreicherung (failure_class hints, guard_type overrides)
    try:
        from scripts.qa.semantic_enrichment import apply_semantic_enrichment
        qa_dir = DOCS_QA  # Config files in docs/qa/config/
        enrich_stats = apply_semantic_enrichment(output_dict, qa_dir)
        if any(v > 0 for v in enrich_stats.values()):
            summary["manual_review_required_count"] = output_dict.get("summary", {}).get("manual_review_required_count", summary["manual_review_required_count"])
    except Exception:
        pass
    return output_dict, summary_counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="QA Test Inventory – Discovert pytest-Landschaft, erzeugt QA_TEST_INVENTORY.json"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output-Pfad (use '-' for stdout)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Keine Datei schreiben, nur berechnen und ausgeben",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Nur Summary-Statistiken ausgeben",
    )
    parser.add_argument(
        "--timestamp",
        type=str,
        default=None,
        help="Optional: ISO-Format für Reproduzierbarkeit",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="Pfad zu REGRESSION_CATALOG.md",
    )
    args = parser.parse_args()

    try:
        output_dict, summary_counts = build_inventory(
            optional_timestamp=args.timestamp,
            catalog_path=args.catalog,
        )

        if args.stats:
            print("=== Test Inventory Summary ===")
            print(f"Total tests: {output_dict['test_count']}")
            print("By test_type:", json.dumps(summary_counts["by_test_type"], indent=2))
            print("By test_domain:", json.dumps(summary_counts["by_test_domain"], indent=2))
            print("By subsystem:", json.dumps(summary_counts["by_subsystem"], indent=2))
            print(f"Manual review required: {summary_counts['manual_review_required']}")
            print(f"Covers regression: {summary_counts['covers_regression']}")
            print(f"Catalog-bound failure_class: {summary_counts['catalog_bound_failure_class']}")
            return 0

        if args.dry_run:
            print(json.dumps(output_dict, indent=2, ensure_ascii=False, sort_keys=True))
            return 0

        if str(args.output) == "-":
            print(json.dumps(output_dict, indent=2, ensure_ascii=False, sort_keys=True))
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(output_dict, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            LOG.info("QA Test Inventory geschrieben: %s", args.output)

        print(
            f"Test Inventory: {output_dict['test_count']} Tests, "
            f"{summary_counts['manual_review_required']} manual review, "
            f"{summary_counts['catalog_bound_failure_class']} catalog-bound failure_class"
        )
        return 0

    except Exception as e:
        LOG.exception("Generator fehlgeschlagen: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
