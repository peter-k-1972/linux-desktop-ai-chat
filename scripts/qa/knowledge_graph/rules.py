"""
QA Knowledge Graph – Regeln für Node- und Edge-Erzeugung.

Definiert welche Nodes und Edges aus den Inputs abgeleitet werden.
"""

from __future__ import annotations

from typing import Any

from .models import GraphEdge, GraphNode


def _node_id(node_type: str, identifier: str) -> str:
    """Erzeugt stabile Node-ID. Deterministisch."""
    return f"{node_type}:{identifier}"


def collect_incident_nodes(incident_index: dict[str, Any] | None) -> list[GraphNode]:
    """Erzeugt incident-Nodes aus incidents/index.json."""
    nodes: list[GraphNode] = []
    incidents = incident_index.get("incidents", []) if incident_index else []
    if not isinstance(incidents, list):
        return nodes

    for inc in incidents:
        inc_id = inc.get("incident_id") or inc.get("id") or ""
        if not inc_id:
            continue
        nid = _node_id("incident", inc_id)
        nodes.append(GraphNode(
            id=nid,
            node_type="incident",
            attributes={
                "incident_id": inc_id,
                "subsystem": inc.get("subsystem"),
                "failure_class": inc.get("failure_class"),
                "severity": inc.get("severity"),
                "status": inc.get("status"),
            },
        ))
    return nodes


def collect_failure_class_nodes(
    incident_index: dict[str, Any] | None,
    autopilot_v3: dict[str, Any] | None,
    test_strategy: dict[str, Any] | None,
    catalog_parsed: dict[str, Any],
) -> list[GraphNode]:
    """Erzeugt failure_class-Nodes. Sammelt aus allen Quellen."""
    seen: set[str] = set()
    nodes: list[GraphNode] = []

    # Aus Incidents
    incidents = incident_index.get("incidents", []) if incident_index else []
    if isinstance(incidents, list):
        for inc in incidents:
            fc = inc.get("failure_class") or ""
            if fc and fc not in seen:
                seen.add(fc)
                nodes.append(GraphNode(
                    id=_node_id("failure_class", fc),
                    node_type="failure_class",
                    attributes={"failure_class": fc},
                ))

    # Aus Autopilot v3
    for g in autopilot_v3.get("guard_gap_findings") or []:
        fc = g.get("failure_class") or ""
        if fc and fc not in seen:
            seen.add(fc)
            nodes.append(GraphNode(
                id=_node_id("failure_class", fc),
                node_type="failure_class",
                attributes={"failure_class": fc},
            ))
    for t in autopilot_v3.get("translation_gap_findings") or []:
        fc = t.get("failure_class") or ""
        if fc and fc not in seen:
            seen.add(fc)
            nodes.append(GraphNode(
                id=_node_id("failure_class", fc),
                node_type="failure_class",
                attributes={"failure_class": fc},
            ))

    # Aus Catalog
    for fc in catalog_parsed.get("failure_class_to_domains", {}).keys():
        if fc and fc not in seen:
            seen.add(fc)
            nodes.append(GraphNode(
                id=_node_id("failure_class", fc),
                node_type="failure_class",
                attributes={"failure_class": fc},
            ))

    return sorted(nodes, key=lambda n: n.id)


def collect_guard_nodes(
    autopilot_v3: dict[str, Any] | None,
    test_strategy: dict[str, Any] | None,
) -> list[GraphNode]:
    """Erzeugt guard-Nodes (guard_type als ID)."""
    seen: set[str] = set()
    nodes: list[GraphNode] = []

    for g in (autopilot_v3 or {}).get("guard_gap_findings") or []:
        gt = g.get("guard_type") or ""
        if gt and gt not in seen:
            seen.add(gt)
            nodes.append(GraphNode(
                id=_node_id("guard", gt),
                node_type="guard",
                attributes={"guard_type": gt},
            ))

    for g in (test_strategy or {}).get("guard_requirements") or []:
        gt = g.get("guard_type") or ""
        if gt and gt not in seen:
            seen.add(gt)
            nodes.append(GraphNode(
                id=_node_id("guard", gt),
                node_type="guard",
                attributes={"guard_type": gt},
            ))

    return sorted(nodes, key=lambda n: n.id)


def collect_test_domain_nodes(
    test_strategy: dict[str, Any] | None,
    catalog_parsed: dict[str, Any],
) -> list[GraphNode]:
    """Erzeugt test_domain-Nodes."""
    seen: set[str] = set()
    nodes: list[GraphNode] = []

    for td in (test_strategy or {}).get("test_domains") or []:
        d = td.get("domain") or ""
        if d and d not in seen:
            seen.add(d)
            nodes.append(GraphNode(
                id=_node_id("test_domain", d),
                node_type="test_domain",
                attributes={"domain": d, "priority": td.get("priority")},
            ))

    for d in catalog_parsed.get("test_domains") or []:
        if d and d not in seen:
            seen.add(d)
            nodes.append(GraphNode(
                id=_node_id("test_domain", d),
                node_type="test_domain",
                attributes={"domain": d},
            ))

    return sorted(nodes, key=lambda n: n.id)


def collect_regression_requirement_nodes(
    test_strategy: dict[str, Any] | None,
) -> list[GraphNode]:
    """Erzeugt regression_requirement-Nodes."""
    nodes: list[GraphNode] = []
    for r in (test_strategy or {}).get("regression_requirements") or []:
        rid = r.get("id") or ""
        if not rid:
            continue
        nodes.append(GraphNode(
            id=_node_id("regression_requirement", rid),
            node_type="regression_requirement",
            attributes={
                "id": rid,
                "incident_id": r.get("incident_id"),
                "subsystem": r.get("subsystem"),
                "failure_class": r.get("failure_class"),
                "priority": r.get("priority"),
            },
        ))
    return sorted(nodes, key=lambda n: n.id)


def collect_incident_failure_edges(
    incident_index: dict[str, Any] | None,
) -> list[GraphEdge]:
    """Edges: incident -> failure_class (incident_failure)."""
    edges: list[GraphEdge] = []
    incidents = incident_index.get("incidents", []) if incident_index else []
    if not isinstance(incidents, list):
        return edges

    for inc in incidents:
        inc_id = inc.get("incident_id") or inc.get("id") or ""
        fc = inc.get("failure_class") or ""
        if inc_id and fc:
            edges.append(GraphEdge(
                source_id=_node_id("incident", inc_id),
                target_id=_node_id("failure_class", fc),
                edge_type="incident_failure",
                attributes={},
            ))
    return edges


def collect_requires_guard_edges(
    autopilot_v3: dict[str, Any] | None,
    test_strategy: dict[str, Any] | None,
) -> list[GraphEdge]:
    """Edges: failure_class -> guard (requires_guard)."""
    edges: list[GraphEdge] = []
    seen: set[tuple[str, str]] = set()

    for g in (autopilot_v3 or {}).get("guard_gap_findings") or []:
        fc = g.get("failure_class") or ""
        gt = g.get("guard_type") or ""
        if fc and gt:
            key = (fc, gt)
            if key not in seen:
                seen.add(key)
                edges.append(GraphEdge(
                    source_id=_node_id("failure_class", fc),
                    target_id=_node_id("guard", gt),
                    edge_type="requires_guard",
                    attributes={"subsystem": g.get("subsystem")},
                ))

    for g in (test_strategy or {}).get("guard_requirements") or []:
        fc = g.get("failure_class") or ""
        gt = g.get("guard_type") or ""
        if fc and gt:
            key = (fc, gt)
            if key not in seen:
                seen.add(key)
                edges.append(GraphEdge(
                    source_id=_node_id("failure_class", fc),
                    target_id=_node_id("guard", gt),
                    edge_type="requires_guard",
                    attributes={"subsystem": g.get("subsystem")},
                ))

    return sorted(edges, key=lambda e: (e.source_id, e.target_id))


def collect_validated_by_edges(catalog_parsed: dict[str, Any]) -> list[GraphEdge]:
    """Edges: failure_class -> test_domain (validated_by)."""
    edges: list[GraphEdge] = []
    fc_to_domains = catalog_parsed.get("failure_class_to_domains") or {}
    seen: set[tuple[str, str]] = set()

    for fc, domains in fc_to_domains.items():
        for d in domains:
            if fc and d:
                key = (fc, d)
                if key not in seen:
                    seen.add(key)
                    edges.append(GraphEdge(
                        source_id=_node_id("failure_class", fc),
                        target_id=_node_id("test_domain", d),
                        edge_type="validated_by",
                        attributes={},
                    ))
    return sorted(edges, key=lambda e: (e.source_id, e.target_id))


def collect_requires_regression_edges(
    test_strategy: dict[str, Any] | None,
) -> list[GraphEdge]:
    """Edges: incident -> regression_requirement (requires_regression)."""
    edges: list[GraphEdge] = []
    for r in (test_strategy or {}).get("regression_requirements") or []:
        inc_id = r.get("incident_id") or ""
        rid = r.get("id") or ""
        if inc_id and rid:
            edges.append(GraphEdge(
                source_id=_node_id("incident", inc_id),
                target_id=_node_id("regression_requirement", rid),
                edge_type="requires_regression",
                attributes={},
            ))
    return sorted(edges, key=lambda e: (e.source_id, e.target_id))


def collect_recommended_test_edges(
    autopilot_v3: dict[str, Any] | None,
    test_strategy: dict[str, Any] | None,
) -> list[GraphEdge]:
    """Edges: failure_class -> test_domain (recommended_test)."""
    edges: list[GraphEdge] = []
    seen: set[tuple[str, str]] = set()

    for b in (autopilot_v3 or {}).get("recommended_test_backlog") or []:
        fc = b.get("failure_class") or ""
        domain = b.get("test_domain") or ""
        if fc and domain:
            key = (fc, domain)
            if key not in seen:
                seen.add(key)
                edges.append(GraphEdge(
                    source_id=_node_id("failure_class", fc),
                    target_id=_node_id("test_domain", domain),
                    edge_type="recommended_test",
                    attributes={"subsystem": b.get("subsystem")},
                ))

    for f in (test_strategy or {}).get("recommended_focus_domains") or []:
        fc = f.get("failure_class") or ""
        domain = f.get("domain") or ""
        if fc and domain:
            key = (fc, domain)
            if key not in seen:
                seen.add(key)
                edges.append(GraphEdge(
                    source_id=_node_id("failure_class", fc),
                    target_id=_node_id("test_domain", domain),
                    edge_type="recommended_test",
                    attributes={"subsystem": f.get("subsystem")},
                ))

    return sorted(edges, key=lambda e: (e.source_id, e.target_id))
