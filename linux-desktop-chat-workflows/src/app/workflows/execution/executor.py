"""Sequentielle DAG-Ausführung mit topologischer Reihenfolge."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from app.workflows.execution.context import AbortToken, RunContext
from app.workflows.models.definition import WorkflowDefinition, WorkflowNode
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.registry.node_registry import NodeRegistry
from app.workflows.status import NodeRunStatus, WorkflowRunStatus


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


OnAfterNode = Optional[Callable[[WorkflowRun, NodeRun], None]]


class WorkflowExecutor:
    """Führt nur valide DAGs aus (Validierung erfolgt vorher durch GraphValidator)."""

    def __init__(self, node_run_id_factory: Optional[Callable[[], str]] = None) -> None:
        self._node_run_id_factory = node_run_id_factory or (lambda: f"nrun_{uuid.uuid4().hex[:16]}")

    def execute(
        self,
        definition: WorkflowDefinition,
        run: WorkflowRun,
        registry: NodeRegistry,
        abort: AbortToken,
        on_after_node: OnAfterNode = None,
    ) -> WorkflowRun:
        """
        Mutiert run (node_runs, status, final_output, timestamps).
        Disabled Knoten werden übersprungen (kein NodeRun).
        """
        run.status = WorkflowRunStatus.RUNNING
        run.started_at = _utc_now()
        run.error_message = None
        run.final_output = None
        run.node_runs = []

        id_to_node: Dict[str, WorkflowNode] = {n.node_id: n for n in definition.nodes}
        enabled_ids: Set[str] = {n.node_id for n in definition.nodes if n.is_enabled}

        adj, radj = self._build_adj(definition, enabled_ids)

        try:
            order = self._topological_sort(enabled_ids, definition, adj)
        except ValueError as e:
            run.status = WorkflowRunStatus.FAILED
            run.error_message = str(e)
            run.finished_at = _utc_now()
            return run

        ctx = RunContext(
            run_id=run.run_id,
            definition=definition,
            initial_input=dict(run.initial_input or {}),
            abort=abort,
        )

        for node_id in order:
            if abort.is_cancelled():
                run.status = WorkflowRunStatus.CANCELLED
                run.finished_at = _utc_now()
                return run

            node = id_to_node[node_id]
            if not node.is_enabled:
                continue

            execu = registry.create_executor(node.node_type)
            if execu is None:
                self._fail_run(run, f"Kein Executor für Knotentyp {node.node_type!r} (Knoten {node_id!r}).")
                return run

            input_payload = self._compose_input(node_id, node.node_type, radj, ctx, id_to_node, enabled_ids)

            nr = NodeRun(
                node_run_id=self._node_run_id_factory(),
                run_id=run.run_id,
                node_id=node_id,
                node_type=node.node_type,
                status=NodeRunStatus.RUNNING,
                started_at=_utc_now(),
                input_payload=self._snapshot_payload(input_payload),
            )
            run.node_runs.append(nr)
            if on_after_node:
                on_after_node(run, nr)

            try:
                out = execu.execute(node, input_payload, ctx)
                if not isinstance(out, dict):
                    raise TypeError(f"Executor muss dict zurückgeben, erhielt {type(out).__name__}")
            except Exception as e:
                nr.status = NodeRunStatus.FAILED
                nr.finished_at = _utc_now()
                nr.error_message = str(e)
                if on_after_node:
                    on_after_node(run, nr)
                self._fail_run(run, f"Knoten {node_id!r}: {e}")
                return run

            ctx.set_output(node_id, out)
            nr.status = NodeRunStatus.COMPLETED
            nr.finished_at = _utc_now()
            nr.output_payload = self._snapshot_payload(out)
            if on_after_node:
                on_after_node(run, nr)

        run.final_output = self._snapshot_payload(ctx.final_output) if ctx.final_output is not None else None
        run.status = WorkflowRunStatus.COMPLETED
        run.finished_at = _utc_now()
        return run

    def _fail_run(self, run: WorkflowRun, message: str) -> None:
        run.status = WorkflowRunStatus.FAILED
        run.error_message = message
        run.finished_at = _utc_now()

    def _build_adj(
        self,
        definition: WorkflowDefinition,
        enabled_ids: Set[str],
    ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        adj: Dict[str, List[str]] = {}
        radj: Dict[str, List[str]] = {}
        for n in enabled_ids:
            adj[n] = []
            radj[n] = []
        for e in definition.edges:
            u, v = e.source_node_id, e.target_node_id
            if u in enabled_ids and v in enabled_ids:
                adj[u].append(v)
                radj[v].append(u)
        for k in adj:
            adj[k].sort()
        for k in radj:
            radj[k].sort()
        return adj, radj

    def _topological_sort(
        self,
        enabled_ids: Set[str],
        definition: WorkflowDefinition,
        adj: Dict[str, List[str]],
    ) -> List[str]:
        indeg: Dict[str, int] = {n: 0 for n in enabled_ids}
        for u in enabled_ids:
            for v in adj.get(u, ()):
                indeg[v] = indeg.get(v, 0) + 1
        ready = sorted(n for n in enabled_ids if indeg[n] == 0)
        order: List[str] = []
        while ready:
            n = ready.pop(0)
            order.append(n)
            for w in adj.get(n, ()):
                indeg[w] -= 1
                if indeg[w] == 0:
                    ready.append(w)
                    ready.sort()
        if len(order) != len(enabled_ids):
            raise ValueError("Zyklus oder inkonsistenter Graph bei der topologischen Sortierung.")
        return order

    def _compose_input(
        self,
        node_id: str,
        node_type: str,
        radj: Dict[str, List[str]],
        ctx: RunContext,
        id_to_node: Dict[str, WorkflowNode],
        enabled_ids: Set[str],
    ) -> Optional[Dict[str, Any]]:
        preds = [p for p in radj.get(node_id, ()) if p in enabled_ids]
        preds.sort()
        if node_type == "start":
            return None
        if len(preds) == 0:
            return {}
        if len(preds) == 1:
            got = ctx.get_output(preds[0])
            return dict(got or {})
        merged: Dict[str, Any] = {}
        for p in preds:
            got = ctx.get_output(p)
            merged[p] = dict(got or {})
        return merged

    @staticmethod
    def _snapshot_payload(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if data is None:
            return None
        return dict(data)
