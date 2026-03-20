"""
QA Test Inventory – Regeln und Heuristik-Sicherheit.

- Ableitungslogik korrekt
- unsichere Ableitungen werden markiert (inference_sources, manual_review_required)
- keine stillschweigende Überklassifikation
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

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


@pytest.mark.unit
def test_derive_test_domain_from_path() -> None:
    """test_domain aus Pfad korrekt."""
    assert derive_test_domain("tests/failure_modes/test_foo.py") == "failure_modes"
    assert derive_test_domain("tests/async_behavior/test_bar.py") == "async_behavior"
    assert derive_test_domain("tests/qa/autopilot_v3/test_baz.py") == "qa"
    assert derive_test_domain("tests/test_root.py") == "root"
    assert derive_test_domain("tests/helpers/test_diag.py") == "helpers"


@pytest.mark.unit
def test_derive_test_type_marker_priority() -> None:
    """Marker hat Priorität vor test_domain."""
    t, src = derive_test_type(["failure_mode", "asyncio"], "integration")
    assert t == "failure_mode"
    assert src == "discovered"


@pytest.mark.unit
def test_derive_test_type_fallback_domain() -> None:
    """Ohne Marker: test_domain als test_type."""
    t, src = derive_test_type([], "failure_modes")
    assert t == "failure_modes"
    assert src == "inferred"


@pytest.mark.unit
def test_derive_test_type_root_unknown() -> None:
    """root/helpers => unknown."""
    t, _ = derive_test_type([], "root")
    assert t == "unknown"
    t, _ = derive_test_type([], "helpers")
    assert t == "unknown"


@pytest.mark.unit
def test_derive_subsystem_heuristic() -> None:
    """Subsystem aus Dateiname/Testname."""
    sub, src = derive_subsystem("tests/failure_modes/test_chroma_unreachable.py", "test_rag_service_handles")
    assert sub == "RAG"
    assert src == "inferred"

    sub, src = derive_subsystem("tests/contracts/test_debug_event_contract.py", "test_event_metadata")
    assert sub == "Debug/EventBus"
    assert src == "inferred"


@pytest.mark.unit
def test_derive_subsystem_unknown_when_no_match() -> None:
    """Unbekanntes Muster => unknown."""
    sub, src = derive_subsystem("tests/unit/test_foo.py", "test_bar")
    assert sub is None
    assert src == "unknown"


@pytest.mark.unit
def test_derive_guard_types_only_where_rule() -> None:
    """guard_type nur wo Regel existiert."""
    assert derive_guard_types("failure_mode") == ["failure_replay_guard"]
    assert derive_guard_types("contract") == ["event_contract_guard"]
    assert derive_guard_types("async_behavior") == []
    assert derive_guard_types("regression") == []


@pytest.mark.unit
def test_requires_manual_review_root_and_helpers() -> None:
    """root und helpers => manual_review_required."""
    assert requires_manual_review("root", "unknown", None, "tests/test_foo.py", "test_bar") is True
    assert requires_manual_review("helpers", "unknown", None, "tests/helpers/test_diag.py", "test_foo") is True


@pytest.mark.unit
def test_requires_manual_review_unit_generic_name() -> None:
    """unit + generischer Name => manual_review."""
    assert requires_manual_review("unit", "unit", None, "tests/unit/test_foo.py", "test_parse") is True
    assert requires_manual_review("unit", "unit", None, "tests/unit/test_foo.py", "test_validate") is True


@pytest.mark.unit
def test_requires_manual_review_unit_specific_name() -> None:
    """unit + spezifischer Name => kein manual_review."""
    assert requires_manual_review("unit", "unit", "RAG", "tests/unit/test_rag.py", "test_embedding_query") is False


@pytest.mark.unit
def test_parse_regression_catalog_extracts_mapping() -> None:
    """Catalog-Parser extrahiert (domain, datei) -> test -> failure_classes."""
    content = """
### failure_modes/

| Datei | Test | Fehlerklasse |
|-------|------|--------------|
| test_chroma_unreachable | test_rag_service_handles_chroma | rag_silent_failure |

## Historische Bugs
"""
    catalog = parse_regression_catalog(content)
    key = ("failure_modes", "test_chroma_unreachable")
    assert key in catalog
    assert "test_rag_service_handles_chroma" in catalog[key]
    assert catalog[key]["test_rag_service_handles_chroma"] == ["rag_silent_failure"]


@pytest.mark.unit
def test_lookup_failure_classes_catalog_bound() -> None:
    """Lookup aus Catalog => catalog_bound."""
    catalog = {
        ("failure_modes", "test_chroma_unreachable"): {
            "test_rag_service_handles_chroma": ["rag_silent_failure"],
        },
    }
    classes, src = lookup_failure_classes(
        catalog, "failure_modes", "test_chroma_unreachable", "test_rag_service_handles_chroma"
    )
    assert classes == ["rag_silent_failure"]
    assert src == "catalog_bound"


@pytest.mark.unit
def test_lookup_failure_classes_unknown_when_not_in_catalog() -> None:
    """Nicht im Catalog => unknown."""
    catalog = {}
    classes, src = lookup_failure_classes(
        catalog, "failure_modes", "test_foo", "test_bar"
    )
    assert classes == []
    assert src == "unknown"


@pytest.mark.unit
def test_inference_sources_present_in_output(minimal_catalog_path: Path) -> None:
    """Jeder Test hat inference_sources für test_type, subsystem, failure_class."""
    import json
    from .conftest import run_build_test_inventory

    ec, out, err = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path), "--timestamp", "2026-01-01T00:00:00Z"],
    )
    assert ec == 0, err
    data = json.loads(out)
    for t in data.get("tests", [])[:10]:
        assert "inference_sources" in t
        src = t["inference_sources"]
        assert "test_type" in src
        assert "subsystem" in src
        assert "failure_class" in src


@pytest.mark.unit
def test_no_failure_class_without_catalog_entry() -> None:
    """failure_class nur catalog_bound, nie geraten."""
    catalog = {("failure_modes", "test_other"): {"test_other_foo": ["rag_silent_failure"]}}
    classes, src = lookup_failure_classes(
        catalog, "failure_modes", "test_unknown_file", "test_unknown_test"
    )
    assert classes == []
    assert src == "unknown"
