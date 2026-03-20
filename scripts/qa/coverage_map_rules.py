"""
QA Coverage Map – Mapping-Regeln.

Aggregation, Coverage Strength, Coverage Quality, Gap Detection,
Orphan Tests, Semantic Binding Gaps.
Entspricht QA_COVERAGE_MAP_ARCHITECTURE.md und QA_COVERAGE_MAP_MAPPING_RULES.md.
Phase 3: Orphan-Governance (review_candidate, whitelist, exclusion).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Referenz: test_inventory_rules.VALID_FAILURE_CLASSES
VALID_FAILURE_CLASSES = {
    "ui_state_drift",
    "async_race",
    "late_signal_use_after_destroy",
    "request_context_loss",
    "rag_silent_failure",
    "debug_false_truth",
    "startup_ordering",
    "degraded_mode_failure",
    "contract_schema_drift",
    "metrics_false_success",
    "tool_failure_visibility",
    "optional_dependency_missing",
}

GUARD_TYPES = {"failure_replay_guard", "event_contract_guard", "startup_degradation_guard"}

# Phase 2: Legacy – alle Domains die als „meta“ galten
META_DOMAINS = {"root", "helpers", "qa"}

# Phase 3: Orphan-Governance Defaults (überschreibbar via Konfiguration)
DEFAULT_ORPHAN_WHITELIST_DOMAINS = {"qa", "helpers", "meta"}
DEFAULT_ORPHAN_EXCLUSION_PATHS = ("tests/qa/", "tests/helpers/", "tests/meta/")
DEFAULT_ORPHAN_CANDIDATE_DOMAINS = {"root"}


def _pytest_nodeid_to_test_id(nodeid: str) -> str:
    """Konvertiert pytest_nodeid zu test_id (Format aus Inventar)."""
    return nodeid.replace("/", "_").replace("::", "__")


def _regression_test_to_test_id(regression_test: str) -> str:
    """Konvertiert regression_test (path::test_name) zu test_id."""
    return regression_test.replace("/", "_").replace("::", "__")


def _test_has_catalog_bound_failure_class(test: dict[str, Any]) -> bool:
    return (test.get("inference_sources") or {}).get("failure_class") == "catalog_bound"


def aggregate_by_failure_class(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    failure_class → tests.
    Nur catalog_bound zählt.
    """
    result: dict[str, dict[str, list[str]]] = {fc: {"test_ids": [], "source": "catalog_defined"} for fc in sorted(VALID_FAILURE_CLASSES)}
    tests = inventory.get("tests") or []
    for t in tests:
        if not _test_has_catalog_bound_failure_class(t):
            continue
        for fc in t.get("failure_classes") or []:
            if fc in result:
                result[fc]["test_ids"].append(t.get("test_id") or _pytest_nodeid_to_test_id(t.get("pytest_nodeid", "")))
                result[fc]["source"] = "catalog_bound"
    out: dict[str, dict[str, Any]] = {}
    for fc in sorted(result.keys()):
        entry = result[fc]
        test_ids = sorted(set(entry["test_ids"]))
        count = len(test_ids)
        strength = _compute_coverage_strength(count, 1)
        out[fc] = {
            "test_ids": test_ids,
            "test_count": count,
            "coverage_strength": strength,
            "source": entry["source"],
        }
    return out


def aggregate_by_guard(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """guard → tests. Aus guard_types (inferiert)."""
    result: dict[str, list[str]] = {g: [] for g in sorted(GUARD_TYPES)}
    tests = inventory.get("tests") or []
    for t in tests:
        for g in t.get("guard_types") or []:
            if g in result:
                result[g].append(t.get("test_id") or _pytest_nodeid_to_test_id(t.get("pytest_nodeid", "")))
    out: dict[str, dict[str, Any]] = {}
    for g in sorted(result.keys()):
        test_ids = sorted(set(result[g]))
        count = len(test_ids)
        strength = _compute_coverage_strength(count, 1)
        out[g] = {
            "test_ids": test_ids,
            "test_count": count,
            "coverage_strength": strength,
            "source": "inferred",
        }
    return out


def aggregate_by_test_domain(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """test_domain → tests. Discovered."""
    result: dict[str, list[str]] = {}
    tests = inventory.get("tests") or []
    for t in tests:
        domain = t.get("test_domain") or "root"
        result.setdefault(domain, []).append(t.get("test_id") or _pytest_nodeid_to_test_id(t.get("pytest_nodeid", "")))
    out: dict[str, dict[str, Any]] = {}
    for d in sorted(result.keys()):
        test_ids = sorted(set(result[d]))
        out[d] = {
            "test_ids": test_ids,
            "test_count": len(test_ids),
            "coverage_strength": "n/a",
            "source": "discovered",
        }
    return out


def aggregate_regression_requirement(
    inventory: dict[str, Any],
    test_strategy: dict[str, Any],
    autopilot_v3: dict[str, Any],
    bindings_by_incident: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    regression_requirement → tests.
    Quelle: TEST_STRATEGY.regression_requirements, AUTOPILOT_V3.translation_gap_findings,
    bindings.regression_catalog.regression_test.
    """
    inventory_test_ids = {t.get("test_id") for t in (inventory.get("tests") or []) if t.get("test_id")}
    nodeid_to_test_id = {t.get("pytest_nodeid"): t.get("test_id") for t in (inventory.get("tests") or []) if t.get("pytest_nodeid") and t.get("test_id")}

    incidents: list[dict[str, Any]] = []
    req_ids: set[str] = set()

    def _add_incident(inc_id: str, req_id: str) -> None:
        regression_test = None
        if inc_id and inc_id in bindings_by_incident:
            reg_cat = (bindings_by_incident[inc_id].get("regression_catalog") or {})
            regression_test = reg_cat.get("regression_test")
        test_id = nodeid_to_test_id.get(regression_test) if regression_test else None
        if not test_id and regression_test:
            test_id = _regression_test_to_test_id(regression_test)
            if test_id not in inventory_test_ids:
                test_id = None
        covered = bool(test_id and test_id in inventory_test_ids)
        incidents.append({
            "incident_id": inc_id,
            "regression_requirement_id": req_id,
            "regression_required": True,
            "regression_test": regression_test,
            "test_id": test_id if covered else None,
            "covered": covered,
        })

    for r in test_strategy.get("regression_requirements") or []:
        inc_id = r.get("incident_id")
        req_id = r.get("id")
        if inc_id and req_id:
            req_ids.add(req_id)
            _add_incident(inc_id, req_id)

    for tr in autopilot_v3.get("translation_gap_findings") or []:
        if tr.get("gap_type") != "incident_not_bound_to_regression":
            continue
        inc_id = tr.get("incident_id")
        req_id = tr.get("id")
        if inc_id and req_id and req_id not in req_ids:
            req_ids.add(req_id)
            _add_incident(inc_id, req_id)

    covered_count = sum(1 for i in incidents if i.get("covered"))
    required_count = len(incidents)
    strength = "n/a" if required_count == 0 else ("covered" if covered_count >= required_count else ("partial" if covered_count > 0 else "gap"))

    return {
        "incidents": incidents,
        "covered_count": covered_count,
        "required_count": required_count,
        "coverage_strength": strength,
    }


def aggregate_replay_binding(
    inventory: dict[str, Any],
    bindings_by_incident: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """replay_binding → tests. Aus bindings.regression_catalog.regression_test."""
    test_ids_inventory = {t.get("test_id") for t in (inventory.get("tests") or []) if t.get("test_id")}
    nodeid_to_test_id = {t.get("pytest_nodeid"): t.get("test_id") for t in (inventory.get("tests") or []) if t.get("pytest_nodeid") and t.get("test_id")}
    bindings: list[dict[str, Any]] = []
    for inc_id, b in bindings_by_incident.items():
        reg_cat = b.get("regression_catalog") or {}
        regression_test = reg_cat.get("regression_test")
        test_id = None
        if regression_test:
            test_id = nodeid_to_test_id.get(regression_test) or _regression_test_to_test_id(regression_test)
            if test_id not in test_ids_inventory:
                test_id = None
        status = (b.get("status") or {}).get("binding_status", "")
        bindings.append({
            "incident_id": inc_id,
            "replay_id": (b.get("identity") or {}).get("replay_id"),
            "regression_test": regression_test,
            "test_id": test_id,
            "binding_status": status,
        })
    total_replays = len(bindings_by_incident)
    bound_count = sum(1 for b in bindings if b.get("test_id"))
    strength = "n/a" if total_replays == 0 else ("covered" if bound_count >= total_replays else ("partial" if bound_count > 0 else "gap"))
    return {
        "bindings": bindings,
        "bound_count": bound_count,
        "total_replays": total_replays,
        "coverage_strength": strength,
    }


def aggregate_autopilot_recommendation(
    inventory: dict[str, Any],
    autopilot_v3: dict[str, Any],
) -> dict[str, Any]:
    """autopilot_recommendation → tests. Abgleich subsystem + failure_class + guard_type."""
    backlog = autopilot_v3.get("recommended_test_backlog") or []
    tests = inventory.get("tests") or []
    backlog_items: list[dict[str, Any]] = []
    for item in backlog:
        subsystem = item.get("subsystem")
        failure_class = item.get("failure_class")
        guard_type = item.get("guard_type")
        covered_by: list[str] = []
        for t in tests:
            if subsystem and t.get("subsystem") != subsystem:
                continue
            if failure_class and failure_class not in (t.get("failure_classes") or []):
                continue
            if guard_type and guard_type not in (t.get("guard_types") or []):
                continue
            tid = t.get("test_id")
            if tid:
                covered_by.append(tid)
        covered = len(covered_by) > 0
        backlog_items.append({
            "id": item.get("id"),
            "subsystem": subsystem,
            "failure_class": failure_class,
            "guard_type": guard_type,
            "test_domain": item.get("test_domain"),
            "title": item.get("title"),
            "covered_by_test_ids": sorted(set(covered_by)),
            "covered": covered,
        })
    total = len(backlog_items)
    covered_count = sum(1 for i in backlog_items if i.get("covered"))
    strength = "n/a" if total == 0 else ("covered" if covered_count >= total else ("partial" if covered_count > 0 else "gap"))
    return {
        "backlog_items": backlog_items,
        "covered_count": covered_count,
        "total_recommendations": total,
        "coverage_strength": strength,
    }


def _compute_coverage_strength(test_count: int, expected_min: int) -> str:
    if expected_min == 0:
        return "n/a"
    if test_count >= expected_min:
        return "covered"
    if test_count > 0:
        return "partial"
    return "gap"


def detect_failure_class_gaps(coverage_by_failure_class: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Gaps: failure_class ohne catalog_bound Test."""
    gaps: list[dict[str, Any]] = []
    for i, (fc, entry) in enumerate(sorted(coverage_by_failure_class.items())):
        if entry.get("coverage_strength") != "gap":
            continue
        gaps.append({
            "gap_id": f"GAP-FC-{i + 1:03d}",
            "axis": "failure_class",
            "gap_type": "failure_class_uncovered",
            "value": fc,
            "severity": "medium",
            "expected": "≥1 catalog_bound test",
            "actual": 0,
            "evidence": [
                f"REGRESSION_CATALOG defines {fc}",
                "No test in QA_TEST_INVENTORY has failure_classes containing this with catalog_bound",
            ],
            "mitigation_hint": "Add test to failure_modes/ or appropriate domain; register in REGRESSION_CATALOG",
        })
    return gaps


def detect_guard_gaps(
    coverage_by_guard: dict[str, dict[str, Any]],
    guard_requirements: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Gaps: guard_type in Strategy erwartet, kein Test."""
    gaps: list[dict[str, Any]] = []
    for i, gr in enumerate(guard_requirements or []):
        gt = gr.get("guard_type")
        if not gt or coverage_by_guard.get(gt, {}).get("coverage_strength") != "gap":
            continue
        gaps.append({
            "gap_id": f"GAP-G-{i + 1:03d}",
            "axis": "guard",
            "gap_type": "guard_missing",
            "value": gt,
            "severity": gr.get("priority", "medium"),
            "expected": f"≥1 test for {gt}",
            "actual": 0,
            "evidence": [f"Guard requirement: {gr.get('subsystem')} / {gr.get('failure_class')}"],
            "mitigation_hint": "Add test with appropriate guard_type; register in REGRESSION_CATALOG",
        })
    return gaps


def detect_regression_requirement_gaps(regression_aggregate: dict[str, Any]) -> list[dict[str, Any]]:
    """Gaps: regression_required ohne regression_test."""
    gaps: list[dict[str, Any]] = []
    for i, inc in enumerate(regression_aggregate.get("incidents") or []):
        if inc.get("covered"):
            continue
        gaps.append({
            "gap_id": f"GAP-RR-{i + 1:03d}",
            "axis": "regression_requirement",
            "gap_type": "regression_requirement_unbound",
            "value": inc.get("incident_id"),
            "severity": "medium",
            "expected": "regression_test in bindings",
            "actual": None,
            "evidence": [f"Incident {inc.get('incident_id')} requires regression test"],
            "mitigation_hint": "Add regression_test to bindings.json; create test if missing",
        })
    return gaps


def detect_replay_binding_gaps(replay_aggregate: dict[str, Any]) -> list[dict[str, Any]]:
    """Gaps: Replay ohne regression_test in bindings."""
    gaps: list[dict[str, Any]] = []
    for i, b in enumerate(replay_aggregate.get("bindings") or []):
        if b.get("test_id"):
            continue
        gaps.append({
            "gap_id": f"GAP-RB-{i + 1:03d}",
            "axis": "replay_binding",
            "gap_type": "replay_unbound",
            "value": b.get("incident_id"),
            "severity": "medium",
            "expected": "regression_test in bindings",
            "actual": None,
            "evidence": [f"Binding for {b.get('incident_id')} has no regression_test or test not in inventory"],
            "mitigation_hint": "Set regression_catalog.regression_test in bindings.json",
        })
    return gaps


def _load_orphan_governance_config(qa_dir: Path | None = None) -> dict[str, Any]:
    """Lädt phase3_orphan_governance.json. Fallback auf Defaults."""
    if qa_dir is None:
        qa_dir = Path(__file__).resolve().parent.parent.parent / "docs" / "qa"
    path = qa_dir / "config" / "phase3_orphan_governance.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def detect_orphan_tests(
    inventory: dict[str, Any],
    config: dict[str, Any] | None = None,
    qa_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """
    Phase 3 Orphan-Governance: Review-Kandidaten statt Fehler.

    Orphan = test_domain in candidate_domains (root)
    AND nicht in whitelist (qa, helpers, meta)
    AND file_path nicht in exclusion_paths
    AND kein catalog_bound failure_class.
    """
    cfg = config if config is not None else _load_orphan_governance_config(qa_dir)
    whitelist = set(cfg.get("orphan_whitelist_domains", DEFAULT_ORPHAN_WHITELIST_DOMAINS))
    exclusion_paths = tuple(cfg.get("orphan_exclusion_paths", list(DEFAULT_ORPHAN_EXCLUSION_PATHS)))
    candidate_domains = set(cfg.get("orphan_candidate_domains", DEFAULT_ORPHAN_CANDIDATE_DOMAINS))

    orphans: list[dict[str, Any]] = []
    for t in inventory.get("tests") or []:
        domain = t.get("test_domain") or "root"
        path = t.get("file_path") or ""

        if domain in whitelist:
            continue
        if any(path.replace("\\", "/").startswith(p.replace("\\", "/")) for p in exclusion_paths):
            continue
        if domain not in candidate_domains:
            continue
        if _test_has_catalog_bound_failure_class(t):
            continue

        orphans.append({
            "test_id": t.get("test_id") or _pytest_nodeid_to_test_id(t.get("pytest_nodeid", "")),
            "reason": f"test_domain={domain}, no catalog_bound failure_class",
        })
    return orphans


def compute_orphan_breakdown(
    inventory: dict[str, Any],
    orphans: list[dict[str, Any]],
    config: dict[str, Any] | None = None,
    qa_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Phase 3: Aufschlüsselung review_candidates vs. whitelisted vs. excluded.
    """
    cfg = config if config is not None else _load_orphan_governance_config(qa_dir)
    whitelist = set(cfg.get("orphan_whitelist_domains", DEFAULT_ORPHAN_WHITELIST_DOMAINS))
    exclusion_paths = tuple(cfg.get("orphan_exclusion_paths", list(DEFAULT_ORPHAN_EXCLUSION_PATHS)))
    candidate_domains = set(cfg.get("orphan_candidate_domains", DEFAULT_ORPHAN_CANDIDATE_DOMAINS))

    whitelisted = 0
    excluded_by_path = 0
    for t in inventory.get("tests") or []:
        domain = t.get("test_domain") or "root"
        path = t.get("file_path") or ""
        if domain in whitelist:
            whitelisted += 1
            continue
        if any(path.replace("\\", "/").startswith(p.replace("\\", "/")) for p in exclusion_paths):
            excluded_by_path += 1

    return {
        "review_candidates": len(orphans),
        "whitelisted": whitelisted,
        "excluded_by_path": excluded_by_path,
        "treat_as": cfg.get("treat_as", "review_candidate"),
        "ci_blocking": cfg.get("ci_blocking", False),
    }


def detect_semantic_binding_gaps(
    inventory: dict[str, Any],
    knowledge_graph: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    validated_by: failure_class → test_domain.
    Gap wenn: failure_class X → domain Y, aber keine catalog_bound Tests für X in domain Y.
    """
    gaps: list[dict[str, Any]] = []
    edges = knowledge_graph.get("edges") or []
    validated_by = [(e.get("source_id"), e.get("target_id")) for e in edges if e.get("edge_type") == "validated_by"]
    for source_id, target_id in validated_by:
        if not source_id or not source_id.startswith("failure_class:") or not target_id or not target_id.startswith("test_domain:"):
            continue
        fc = source_id.split(":", 1)[1]
        domain = target_id.split(":", 1)[1]
        count = 0
        for t in inventory.get("tests") or []:
            if t.get("test_domain") != domain:
                continue
            if not _test_has_catalog_bound_failure_class(t):
                continue
            if fc in (t.get("failure_classes") or []):
                count += 1
        if count == 0:
            gaps.append({
                "failure_class": fc,
                "expected_test_domain": domain,
                "actual_test_count": 0,
                "evidence": f"Knowledge Graph validated_by: {fc} → {domain}; no catalog_bound test in {domain}",
            })
    return gaps


def compute_manual_review_required(inventory: dict[str, Any]) -> dict[str, Any]:
    """Governance: manual_review_required aus Inventar."""
    tests = inventory.get("tests") or []
    total = len(tests)
    mrr_ids = [t.get("test_id") or _pytest_nodeid_to_test_id(t.get("pytest_nodeid", "")) for t in tests if t.get("manual_review_required")]
    count = len(mrr_ids)
    share = count / total if total > 0 else 0.0
    return {
        "count": count,
        "test_ids": sorted(mrr_ids),
        "share_of_total": round(share, 4),
    }


def compute_coverage_quality(
    coverage_by_axis: dict[str, Any],
    manual_review_share: float,
) -> dict[str, str]:
    """
    Pro Axis: high (discovered/catalog_bound), medium (inferred), low (>30% manual_review).
    """
    axis_quality: dict[str, str] = {
        "failure_class": "high",
        "guard": "medium",
        "test_domain": "high",
        "regression_requirement": "high",
        "replay_binding": "high",
        "autopilot_recommendation": "medium",
    }
    if manual_review_share > 0.3:
        for k in axis_quality:
            if axis_quality[k] == "high":
                axis_quality[k] = "medium"
    return axis_quality


def build_gap_types(
    gaps: dict[str, list[dict[str, Any]]],
    autopilot_aggregate: dict[str, Any] | None = None,
) -> dict[str, int]:
    """Zählt gap_types aus gaps und autopilot_aggregate."""
    mapping = {
        "failure_class": "failure_class_uncovered",
        "guard": "guard_missing",
        "regression_requirement": "regression_requirement_unbound",
        "replay_binding": "replay_unbound",
    }
    result: dict[str, int] = {
        "failure_class_uncovered": 0,
        "guard_missing": 0,
        "regression_requirement_unbound": 0,
        "replay_unbound": 0,
        "autopilot_recommendation_uncovered": 0,
    }
    for axis, items in gaps.items():
        gt = mapping.get(axis)
        if gt:
            result[gt] = len(items)
    if autopilot_aggregate:
        backlog = autopilot_aggregate.get("backlog_items") or []
        result["autopilot_recommendation_uncovered"] = sum(1 for i in backlog if not i.get("covered"))
    return result
