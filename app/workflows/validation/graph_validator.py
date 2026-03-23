"""Struktur- und Graphvalidierung für WorkflowDefinition."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.registry.node_registry import NodeRegistry


@dataclass
class ValidationResult:
    """Ergebnis der Validierung (UI-taugliche Meldungen)."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.is_valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


class GraphValidator:
    """Validiert Definitionen gegen Struktur, DAG und Registry."""

    def validate(self, definition: WorkflowDefinition, registry: NodeRegistry) -> ValidationResult:
        result = ValidationResult(is_valid=True)

        if not definition.nodes:
            result.add_error("Der Workflow enthält keine Knoten.")
            return result

        # Eindeutige IDs
        seen_nodes: Set[str] = set()
        for node in definition.nodes:
            if node.node_id in seen_nodes:
                result.add_error(f"Doppelte node_id: {node.node_id!r}.")
            else:
                seen_nodes.add(node.node_id)

        if result.errors:
            return result

        seen_edges: Set[str] = set()
        for edge in definition.edges:
            if edge.edge_id in seen_edges:
                result.add_error(f"Doppelte edge_id: {edge.edge_id!r}.")
            else:
                seen_edges.add(edge.edge_id)

        if result.errors:
            return result

        id_to_node: Dict[str, WorkflowNode] = {n.node_id: n for n in definition.nodes}

        # Kanten: referenzierte Knoten existieren
        for edge in definition.edges:
            if edge.source_node_id not in id_to_node:
                result.add_error(
                    f"Kante {edge.edge_id!r}: unbekannte source_node_id {edge.source_node_id!r}."
                )
            if edge.target_node_id not in id_to_node:
                result.add_error(
                    f"Kante {edge.edge_id!r}: unbekannte target_node_id {edge.target_node_id!r}."
                )

        if result.errors:
            return result

        enabled_ids = {n.node_id for n in definition.nodes if n.is_enabled}

        for edge in definition.edges:
            src_ok = edge.source_node_id in id_to_node and id_to_node[edge.source_node_id].is_enabled
            tgt_ok = edge.target_node_id in id_to_node and id_to_node[edge.target_node_id].is_enabled
            if not src_ok or not tgt_ok:
                result.add_warning(
                    f"Kante {edge.edge_id!r} wird ignoriert (deaktivierter oder ungültiger Endpunkt)."
                )
            if edge.condition:
                result.add_warning(
                    f"Kante {edge.edge_id!r}: 'condition' wird in dieser Engine-Phase noch nicht ausgewertet."
                )

        starts = [n for n in definition.nodes if n.is_enabled and n.node_type == "start"]
        ends = [n for n in definition.nodes if n.is_enabled and n.node_type == "end"]

        if len(starts) == 0:
            result.add_error("Es muss genau ein aktiver Start-Knoten (node_type 'start') existieren.")
        elif len(starts) > 1:
            result.add_error(
                "Es darf nur ein aktiver Start-Knoten existieren; gefunden: "
                + ", ".join(sorted(s.node_id for s in starts))
                + "."
            )

        if len(ends) == 0:
            result.add_error("Es muss mindestens ein aktiver End-Knoten (node_type 'end') existieren.")

        if result.errors:
            return result

        # Registry / Config je aktivem Knoten
        for node in definition.nodes:
            if not node.is_enabled:
                continue
            if not registry.is_supported(node.node_type):
                result.add_error(
                    f"Knoten {node.node_id!r}: unbekannter oder nicht registrierter Typ {node.node_type!r}."
                )
                continue
            cfg_err = registry.validate_node_config(node.node_type, node.config)
            if cfg_err:
                result.add_error(f"Knoten {node.node_id!r}: {cfg_err}")

        if result.errors:
            return result

        topo_edges, adj, radj = self._topology_subgraph(definition, enabled_ids)
        start_id = starts[0].node_id  # genau ein Start gesichert
        end_ids = {e.node_id for e in ends}

        if self._has_cycle(enabled_ids, topo_edges):
            result.add_error("Der Workflow enthält einen Zyklus (nur DAG erlaubt).")
            return result

        reachable_from_start = self._forward_reach(start_id, adj, enabled_ids)
        can_reach_end = self._backward_reach_to_set(end_ids, radj, enabled_ids)

        for nid in sorted(enabled_ids):
            if nid not in reachable_from_start:
                result.add_error(
                    f"Knoten {nid!r} ist vom Start nicht erreichbar (verwaister oder getrennter Teilgraph)."
                )
            if nid not in can_reach_end:
                result.add_error(
                    f"Knoten {nid!r} kann keinen End-Knoten erreichen (Sackgasse ohne Ausgang zum End)."
                )

        if not self._exists_path_start_to_some_end(start_id, end_ids, adj):
            result.add_error("Es existiert kein Pfad vom Start zu einem End-Knoten.")

        return result

    def _topology_subgraph(
        self,
        definition: WorkflowDefinition,
        enabled_ids: Set[str],
    ) -> Tuple[List[Tuple[str, str]], Dict[str, List[str]], Dict[str, List[str]]]:
        """Kantenliste und Adjazenz nur zwischen aktivierten Knoten."""
        edges_list: List[Tuple[str, str]] = []
        adj: Dict[str, List[str]] = defaultdict(list)
        radj: Dict[str, List[str]] = defaultdict(list)
        for e in definition.edges:
            if e.source_node_id in enabled_ids and e.target_node_id in enabled_ids:
                edges_list.append((e.source_node_id, e.target_node_id))
                adj[e.source_node_id].append(e.target_node_id)
                radj[e.target_node_id].append(e.source_node_id)
        for k in adj:
            adj[k].sort()
        for k in radj:
            radj[k].sort()
        return edges_list, dict(adj), dict(radj)

    def _has_cycle(self, nodes: Set[str], directed_edges: List[Tuple[str, str]]) -> bool:
        """DFS-Zykluserkennung."""
        adj: Dict[str, List[str]] = defaultdict(list)
        for u, v in directed_edges:
            adj[u].append(v)
        visited: Set[str] = set()
        stack: Set[str] = set()

        def visit(n: str) -> bool:
            if n in stack:
                return True
            if n in visited:
                return False
            visited.add(n)
            stack.add(n)
            for w in sorted(adj.get(n, ())):
                if visit(w):
                    return True
            stack.remove(n)
            return False

        for n in sorted(nodes):
            if n not in visited:
                if visit(n):
                    return True
        return False

    def _forward_reach(self, start: str, adj: Dict[str, List[str]], nodes: Set[str]) -> Set[str]:
        out: Set[str] = set()
        dq = deque([start])
        while dq:
            n = dq.popleft()
            if n in out:
                continue
            if n not in nodes:
                continue
            out.add(n)
            for w in adj.get(n, ()):
                if w in nodes and w not in out:
                    dq.append(w)
        return out

    def _backward_reach_to_set(
        self,
        targets: Set[str],
        radj: Dict[str, List[str]],
        nodes: Set[str],
    ) -> Set[str]:
        out: Set[str] = set()
        dq = deque([t for t in sorted(targets) if t in nodes])
        while dq:
            n = dq.popleft()
            if n in out:
                continue
            if n not in nodes:
                continue
            out.add(n)
            for w in radj.get(n, ()):
                if w in nodes and w not in out:
                    dq.append(w)
        return out

    def _exists_path_start_to_some_end(
        self,
        start_id: str,
        end_ids: Set[str],
        adj: Dict[str, List[str]],
    ) -> bool:
        seen: Set[str] = set()
        dq = deque([start_id])
        while dq:
            n = dq.popleft()
            if n in seen:
                continue
            seen.add(n)
            if n in end_ids:
                return True
            for w in adj.get(n, ()):
                if w not in seen:
                    dq.append(w)
        return False
