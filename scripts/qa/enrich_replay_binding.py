#!/usr/bin/env python3
"""
Phase 3 – Replay-Binding-Enrichment.

Liest incidents/index.json, bindings.json, QA_TEST_INVENTORY.json.
Schreibt NUR covers_replay und replay_ids in QA_TEST_INVENTORY.
Additiv; keine Änderung an Incidents, Replay oder Regression.

Verwendung:
  python scripts/qa/enrich_replay_binding.py
  python scripts/qa/enrich_replay_binding.py --dry-run
  python scripts/qa/enrich_replay_binding.py --output -
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.qa.coverage_map_loader import (
    load_bindings_by_incident,
    load_inventory,
    load_json,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

DEFAULT_QA_DIR = _PROJECT_ROOT / "docs" / "qa"


def _regression_test_to_test_id(regression_test: str) -> str:
    """Konvertiert regression_test (path::test_name) zu test_id."""
    return regression_test.replace("/", "_").replace("::", "__")


def _build_binding_map(bindings_by_incident: dict) -> dict[str, tuple[str, str]]:
    """
    Baut Map: regression_test (nodeid) -> (replay_id, incident_id).
    Nur Bindings mit regression_test und replay_id.
    """
    result: dict[str, tuple[str, str]] = {}
    for incident_id, b in bindings_by_incident.items():
        identity = b.get("identity") or {}
        replay_id = identity.get("replay_id")
        reg_cat = b.get("regression_catalog") or {}
        regression_test = reg_cat.get("regression_test")
        if not regression_test or not replay_id:
            continue
        if not str(regression_test).strip():
            continue
        result[regression_test] = (replay_id, incident_id)
    return result


def enrich_inventory(
    inventory: dict,
    bindings_by_incident: dict,
) -> tuple[dict, list[dict]]:
    """
    Reichert Inventory an: covers_replay, replay_ids pro Test.
    Returns (enriched_inventory, trace_entries).
    """
    binding_map = _build_binding_map(bindings_by_incident)
    if not binding_map:
        return inventory, []

    nodeid_to_binding = binding_map
    test_id_to_binding = {
        _regression_test_to_test_id(rt): (replay_id, inc_id)
        for rt, (replay_id, inc_id) in binding_map.items()
    }

    trace: list[dict] = []
    tests = inventory.get("tests") or []
    enriched_tests = []
    for t in tests:
        t = dict(t)
        test_id = t.get("test_id")
        pytest_nodeid = t.get("pytest_nodeid") or ""

        replay_id, incident_id = None, None
        if pytest_nodeid in nodeid_to_binding:
            replay_id, incident_id = nodeid_to_binding[pytest_nodeid]
        elif test_id and test_id in test_id_to_binding:
            replay_id, incident_id = test_id_to_binding[test_id]

        if replay_id and incident_id:
            t["covers_replay"] = "yes"
            t["replay_ids"] = [replay_id]
            trace.append({
                "test_id": test_id,
                "pytest_nodeid": pytest_nodeid,
                "replay_id": replay_id,
                "incident_id": incident_id,
                "source": "binding",
            })
        else:
            if t.get("covers_replay") != "yes":
                t["covers_replay"] = t.get("covers_replay", "unknown")
            if "replay_ids" not in t:
                t["replay_ids"] = t.get("replay_ids")

        enriched_tests.append(t)

    out = dict(inventory)
    out["tests"] = enriched_tests
    return out, trace


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 3 – Replay-Binding in Inventory anreichern"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output-Pfad (default: docs/qa/QA_TEST_INVENTORY.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Keine Datei schreiben, nur anreichern und ausgeben",
    )
    parser.add_argument(
        "--trace",
        type=Path,
        default=None,
        help="Optional: Audit-Trace schreiben (qa_replay_binding_trace.json)",
    )
    parser.add_argument(
        "--qa-dir",
        type=Path,
        default=None,
        help="Pfad zu docs/qa",
    )
    args = parser.parse_args()

    qa_dir = args.qa_dir or DEFAULT_QA_DIR

    try:
        inventory = load_inventory(qa_dir)
    except FileNotFoundError as e:
        LOG.error("%s", e)
        return 1

    bindings_by_incident = load_bindings_by_incident(qa_dir)
    enriched, trace = enrich_inventory(inventory, bindings_by_incident)

    if trace:
        LOG.info("Replay-Binding-Enrichment: %d Tests angereichert", len(trace))
    else:
        LOG.info("Replay-Binding-Enrichment: Keine Bindings mit regression_test+replay_id")

    if args.trace and trace:
        trace_path = args.trace if args.trace.is_absolute() else qa_dir / str(args.trace)
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_data = {
            "schema_version": "1.0",
            "enriched_count": len(trace),
            "entries": trace,
        }
        trace_path.write_text(json.dumps(trace_data, indent=2, ensure_ascii=False), encoding="utf-8")
        LOG.info("Trace geschrieben: %s", trace_path)

    if args.dry_run:
        print(json.dumps(enriched, indent=2, ensure_ascii=False))
        return 0

    out_path = args.output or (qa_dir / "artifacts" / "json" / "QA_TEST_INVENTORY.json")
    if str(out_path) == "-":
        print(json.dumps(enriched, indent=2, ensure_ascii=False))
        return 0

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")
    LOG.info("Inventory geschrieben: %s", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
