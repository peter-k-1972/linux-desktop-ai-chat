"""Definition: workflow.dev_assist.analyze_modify_test_review (Dev Assist, Cursor-light)."""

from __future__ import annotations

from typing import List

from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode

WORKFLOW_ID = "workflow.dev_assist.analyze_modify_test_review"

_PY = "python_callable"
_CL = "cursor_light"


def _tc_py(callable_path: str, *, merge: bool = True) -> dict:
    return {
        "executor_type": _PY,
        "merge_step_output_into_payload": merge,
        "executor_config": {"callable": callable_path},
    }


def _edges_linear(node_ids: List[str]) -> List[WorkflowEdge]:
    return [
        WorkflowEdge(f"e_{a}__{b}", a, b) for a, b in zip(node_ids, node_ids[1:])
    ]


def build_dev_assist_workflow_definition() -> WorkflowDefinition:
    """
    Linearer Ablauf: Kontext (read) → Analyse → Plan → Developer-Patch → Tests → Review → Doku → Report.
    Agenten per Slug: critic_agent (Qualität), planner_agent, code_agent, documentation_agent.
    """
    nodes: List[WorkflowNode] = [
        WorkflowNode("s", "start", title="Start"),
        WorkflowNode(
            "norm",
            "tool_call",
            title="Inputs normalisieren",
            config=_tc_py("app.workflows.dev_assist_tools.dev_assist_normalize_inputs"),
        ),
        WorkflowNode(
            "fread",
            "tool_call",
            title="Datei lesen (cl.file.read)",
            config={
                "executor_type": _CL,
                "executor_config": {"tool_id": "cl.file.read", "input": {}},
            },
        ),
        WorkflowNode(
            "lift",
            "tool_call",
            title="Dateiinhalt für Prompts",
            config=_tc_py("app.workflows.dev_assist_tools.dev_assist_lift_file_read"),
        ),
        WorkflowNode(
            "pb_an",
            "prompt_build",
            title="Prompt Analyse",
            config={
                "preserve_input_keys": True,
                "template": (
                    "[DEV_ASSIST_PHASE=analysis]\n"
                    "Du bist Quality-Analyst (critic). Analysiere die Zieldatei.\n\n"
                    "workspace_root: {workspace_root}\n"
                    "target_file: {target_file}\n"
                    "Problemstellung: {problem_description}\n"
                    "test_scope (optional): {test_scope}\n\n"
                    "Datei gelesen: file_read_success={file_read_success}\n\n"
                    "Inhalt (ggf. gekürzt):\n---\n{source_file_content}\n---\n\n"
                    "Liefere: Risiken, Verständnis des Problems, kurze technische Einschätzung."
                ),
            },
        ),
        WorkflowNode(
            "ag_an",
            "agent",
            title="Agent Analyse",
            config={"agent_slug": "critic_agent"},
        ),
        WorkflowNode(
            "snap_an",
            "noop",
            title="Snapshot Analyse",
            config={"snapshot_response_as": "analysis"},
        ),
        WorkflowNode(
            "pb_pl",
            "prompt_build",
            title="Prompt Planung",
            config={
                "preserve_input_keys": True,
                "template": (
                    "[DEV_ASSIST_PHASE=plan]\n"
                    "Du bist Planner. Nutze die Analyse und formuliere einen konkreten Änderungsplan.\n\n"
                    "Analyse:\n{analysis}\n\n"
                    "Zieldatei: {target_file}\n"
                    "Problem: {problem_description}\n\n"
                    "Patch-Strategie: bevorzugt replace_block (ein eindeutiges old_text); "
                    "alternativ unified_diff, falls sinnvoll."
                ),
            },
        ),
        WorkflowNode(
            "ag_pl",
            "agent",
            title="Agent Planung",
            config={"agent_slug": "planner_agent"},
        ),
        WorkflowNode(
            "snap_pl",
            "noop",
            title="Snapshot Plan",
            config={"snapshot_response_as": "plan"},
        ),
        WorkflowNode(
            "pb_dev",
            "prompt_build",
            title="Prompt Umsetzung",
            config={
                "preserve_input_keys": True,
                "template": (
                    "[DEV_ASSIST_PHASE=develop]\n"
                    "Du bist Developer. Setze den Plan in eine maschinenlesbare Patch-Anweisung um.\n\n"
                    "Plan:\n{plan}\n\n"
                    "Zieldatei: {target_file}\n\n"
                    "Antwort **ausschließlich** mit einem JSON-Objekt in einem Markdown-Codeblock "
                    "```json ... ```:\n"
                    '- mode: \"replace_block\" mit path (relativ zu workspace_root), old_text, new_text '
                    "(old_text genau einmal in der Datei)\n"
                    '- oder mode: \"unified_diff\" mit patch (String), optional strip\n\n'
                    "Kein Freitext außerhalb des Codeblocks."
                ),
            },
        ),
        WorkflowNode(
            "ag_dev",
            "agent",
            title="Agent Umsetzung",
            config={"agent_slug": "code_agent"},
        ),
        WorkflowNode(
            "parse_pt",
            "tool_call",
            title="Patch aus Antwort parsen",
            config=_tc_py("app.workflows.dev_assist_tools.dev_assist_parse_developer_patch"),
        ),
        WorkflowNode(
            "t_patch",
            "tool_call",
            title="Patch anwenden (cl.file.patch)",
            config={
                "executor_type": _CL,
                "executor_config": {"tool_id": "cl.file.patch", "input": {}},
            },
        ),
        WorkflowNode(
            "snap_patch",
            "noop",
            title="Snapshot patch_applied",
            config={"snapshot_tool_success_as": "patch_applied"},
        ),
        WorkflowNode(
            "t_test",
            "tool_call",
            title="Tests (cl.test.run)",
            config={
                "executor_type": _CL,
                "executor_config": {"tool_id": "cl.test.run", "input": {}},
            },
        ),
        WorkflowNode(
            "snap_test",
            "noop",
            title="Snapshot test_results",
            config={"copy_tool_result_as": "test_results"},
        ),
        WorkflowNode(
            "pb_rev",
            "prompt_build",
            title="Prompt Review",
            config={
                "preserve_input_keys": True,
                "template": (
                    "[DEV_ASSIST_PHASE=review]\n"
                    "Du bist Quality-Analyst (critic). Bewerte Umsetzung und Tests.\n\n"
                    "Analyse:\n{analysis}\n\n"
                    "Plan:\n{plan}\n\n"
                    "patch_applied: {patch_applied}\n\n"
                    "Test-Tool-Ergebnis (JSON):\n{test_results}\n\n"
                    "Ist die Änderung sinnvoll? Wie sind die Testresultate zu interpretieren?"
                ),
            },
        ),
        WorkflowNode(
            "ag_rev",
            "agent",
            title="Agent Review",
            config={"agent_slug": "critic_agent"},
        ),
        WorkflowNode(
            "snap_rev",
            "noop",
            title="Snapshot Review",
            config={"snapshot_response_as": "review"},
        ),
        WorkflowNode(
            "pb_auth",
            "prompt_build",
            title="Prompt Dokumentation",
            config={
                "preserve_input_keys": True,
                "template": (
                    "[DEV_ASSIST_PHASE=document]\n"
                    "Du bist Technical Author. Fasse die Änderung für Stakeholder zusammen.\n\n"
                    "Review:\n{review}\n\n"
                    "Zieldatei: {target_file}\n"
                    "Problem (Ausgang): {problem_description}\n\n"
                    "Kurze Änderungserklärung (Release-Notes-Stil). "
                    "Optional: einen Satz README/Changelog-Hinweis."
                ),
            },
        ),
        WorkflowNode(
            "ag_auth",
            "agent",
            title="Agent Dokumentation",
            config={"agent_slug": "documentation_agent"},
        ),
        WorkflowNode(
            "snap_auth",
            "noop",
            title="Snapshot Doku",
            config={"snapshot_response_as": "documentation"},
        ),
        WorkflowNode(
            "fin",
            "tool_call",
            title="Ergebnis strukturieren",
            config={
                **_tc_py("app.workflows.dev_assist_tools.dev_assist_finalize_report", merge=False),
                "replace_payload_with_tool_output": True,
            },
        ),
        WorkflowNode("e", "end", title="Ende"),
    ]

    order = [n.node_id for n in nodes]
    edges = _edges_linear(order)

    return WorkflowDefinition(
        workflow_id=WORKFLOW_ID,
        name="Dev Assist: Analyse → Patch → Test → Review",
        description=(
            "Cursor-light Entwicklungs-Workflow: Datei lesen, Agenten (Analyse/Plan/Code/Review/Doc), "
            "cl.file.patch, cl.test.run, strukturiertes Ergebnis."
        ),
        nodes=nodes,
        edges=edges,
    )
