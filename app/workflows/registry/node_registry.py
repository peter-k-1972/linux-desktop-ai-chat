"""Registrierung von Knotentypen → Executor + Config-Validierung."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Type

from app.workflows.execution.node_executors.base import BaseNodeExecutor


ConfigValidator = Callable[[dict], Optional[str]]


def _validate_empty_config(config: dict) -> Optional[str]:
    if config:
        return "Dieser Knotentyp erlaubt keine Einträge in 'config'."
    return None


def _validate_prompt_build_config(config: dict) -> Optional[str]:
    c = dict(config or {})
    allowed = {"template", "prompt_text", "prompt_id", "variable_map", "preserve_input_keys"}
    unknown = set(c.keys()) - allowed
    if unknown:
        return f"Unbekannte config-Schlüssel: {sorted(unknown)}"
    pid = c.get("prompt_id")
    has_t = bool(str(c.get("template") or "").strip())
    has_p = bool(str(c.get("prompt_text") or "").strip())
    if pid is not None:
        try:
            int(pid)
        except (TypeError, ValueError):
            return "prompt_id muss eine ganze Zahl sein."
        if has_t or has_p:
            return "prompt_id darf nicht zusammen mit template oder prompt_text verwendet werden."
        return None
    if not has_t and not has_p:
        return "prompt_build: 'template' oder 'prompt_text' setzen (oder nur 'prompt_id')."
    vm = c.get("variable_map")
    if vm is not None and not isinstance(vm, dict):
        return "variable_map muss ein Objekt sein."
    pik = c.get("preserve_input_keys")
    if pik is not None and not isinstance(pik, bool):
        return "preserve_input_keys muss ein Boolean sein."
    return None


def _validate_agent_config(config: dict) -> Optional[str]:
    c = dict(config or {})
    allowed = {"agent_id", "agent_slug", "model_override"}
    unknown = set(c.keys()) - allowed
    if unknown:
        return f"Unbekannte config-Schlüssel: {sorted(unknown)}"
    has_id = bool(str(c.get("agent_id") or "").strip())
    has_slug = bool(str(c.get("agent_slug") or "").strip())
    if not has_id and not has_slug:
        return "agent: 'agent_id' oder 'agent_slug' erforderlich."
    if has_id and has_slug:
        return "agent: nur eines von agent_id / agent_slug setzen."
    mo = c.get("model_override")
    if mo is not None and not isinstance(mo, (str, int, float)):
        return "model_override muss ein String sein."
    return None


def _validate_tool_call_config(config: dict) -> Optional[str]:
    c = dict(config or {})
    allowed = {
        "executor_type",
        "executor_config",
        "step_id",
        "merge_step_output_into_payload",
        "replace_payload_with_tool_output",
    }
    unknown = set(c.keys()) - allowed
    if unknown:
        return f"Unbekannte config-Schlüssel: {sorted(unknown)}"
    if not str(c.get("executor_type") or "").strip():
        return "tool_call: 'executor_type' erforderlich."
    mso = c.get("merge_step_output_into_payload")
    if mso is not None and not isinstance(mso, bool):
        return "tool_call: merge_step_output_into_payload muss ein Boolean sein."
    rpo = c.get("replace_payload_with_tool_output")
    if rpo is not None and not isinstance(rpo, bool):
        return "tool_call: replace_payload_with_tool_output muss ein Boolean sein."
    ec = c.get("executor_config")
    if ec is not None and not isinstance(ec, dict):
        return "executor_config muss ein Objekt sein."
    et = str(c.get("executor_type") or "").strip()
    if et == "cursor_light":
        from app.pipelines.executors import KNOWN_TOOL_IDS

        ec_dict = dict(ec or {})
        tid = str(ec_dict.get("tool_id") or "").strip()
        if not tid:
            return "cursor_light: executor_config.tool_id erforderlich."
        if tid not in KNOWN_TOOL_IDS:
            return f"cursor_light: unbekannte tool_id {tid!r}."
        raw_in = ec_dict.get("input")
        if raw_in is None:
            raw_in = ec_dict.get("tool_input")
        if raw_in is not None and not isinstance(raw_in, dict):
            return "cursor_light: input / tool_input muss ein Objekt sein."
    return None


def _validate_context_load_config(config: dict) -> Optional[str]:
    from app.chat.context_policies import ChatContextPolicy
    from app.chat.request_context_hints import RequestContextHint

    c = dict(config or {})
    allowed = {
        "chat_id",
        "request_context_hint",
        "context_policy",
        "include_payload_preview",
        "include_trace",
    }
    unknown = set(c.keys()) - allowed
    if unknown:
        return f"Unbekannte config-Schlüssel: {sorted(unknown)}"
    cid = c.get("chat_id")
    if cid is not None:
        try:
            n = int(cid)
        except (TypeError, ValueError):
            return "context_load: chat_id muss eine ganze Zahl sein."
        if n < 1:
            return "context_load: chat_id muss >= 1 sein."
    h = c.get("request_context_hint")
    if h is not None and str(h).strip():
        try:
            RequestContextHint(str(h).strip())
        except ValueError:
            return (
                "context_load: request_context_hint ungültig (erlaubt: "
                + ", ".join(sorted(x.value for x in RequestContextHint))
                + ")."
            )
    pol = c.get("context_policy")
    if pol is not None and str(pol).strip():
        try:
            ChatContextPolicy(str(pol).strip())
        except ValueError:
            return (
                "context_load: context_policy ungültig (erlaubt: "
                + ", ".join(sorted(x.value for x in ChatContextPolicy))
                + ")."
            )
    for key in ("include_payload_preview", "include_trace"):
        v = c.get(key)
        if v is not None and not isinstance(v, bool):
            return f"context_load: {key} muss ein Boolean sein."
    return None


def _validate_chain_delegate_config(config: dict) -> Optional[str]:
    c = dict(config or {})
    allowed = {"mode", "model_override", "planner_model"}
    unknown = set(c.keys()) - allowed
    if unknown:
        return f"Unbekannte config-Schlüssel: {sorted(unknown)}"
    mode = str(c.get("mode") or "execute").strip().lower()
    if mode not in ("plan_only", "execute"):
        return "chain_delegate: mode muss 'plan_only' oder 'execute' sein."
    mo = c.get("model_override")
    if mo is not None and not isinstance(mo, (str, int, float)):
        return "chain_delegate: model_override muss ein String sein."
    pm = c.get("planner_model")
    if pm is not None and not isinstance(pm, (str, int, float)):
        return "chain_delegate: planner_model muss ein String sein."
    return None


def _validate_noop_config(config: dict) -> Optional[str]:
    if not config:
        return None
    allowed_noop = {
        "merge",
        "snapshot_response_as",
        "copy_tool_result_as",
        "snapshot_tool_success_as",
    }
    unknown = set(config.keys()) - allowed_noop
    if unknown:
        return f"Unbekannte config-Schlüssel: {sorted(unknown)}"
    merge = config.get("merge")
    if merge is not None and not isinstance(merge, dict):
        return "config.merge muss ein Objekt sein, falls gesetzt."
    for key in ("snapshot_response_as", "copy_tool_result_as", "snapshot_tool_success_as"):
        v = config.get(key)
        if v is not None and not isinstance(v, str):
            return f"noop: {key} muss ein String sein, falls gesetzt."
    return None


@dataclass(frozen=True)
class NodeTypeSpec:
    """Metadaten und Factory für einen Knotentyp."""

    type_id: str
    executor_class: Type[BaseNodeExecutor]
    validate_config: ConfigValidator
    description: str = ""


class NodeRegistry:
    """Erweiterbare Registry für unterstützte node_type-Werte."""

    def __init__(self) -> None:
        self._specs: Dict[str, NodeTypeSpec] = {}

    def register(self, spec: NodeTypeSpec) -> None:
        self._specs[spec.type_id] = spec

    def register_type(
        self,
        type_id: str,
        executor_class: Type[BaseNodeExecutor],
        validate_config: Optional[ConfigValidator] = None,
        description: str = "",
    ) -> None:
        vc = validate_config if validate_config is not None else _validate_empty_config
        self.register(NodeTypeSpec(type_id=type_id, executor_class=executor_class, validate_config=vc, description=description))

    def get_spec(self, type_id: str) -> Optional[NodeTypeSpec]:
        return self._specs.get(type_id)

    def is_supported(self, type_id: str) -> bool:
        return type_id in self._specs

    def create_executor(self, type_id: str) -> Optional[BaseNodeExecutor]:
        spec = self._specs.get(type_id)
        if spec is None:
            return None
        return spec.executor_class()

    def validate_node_config(self, type_id: str, config: dict) -> Optional[str]:
        """Liefert Fehlertext oder None wenn gültig."""
        spec = self._specs.get(type_id)
        if spec is None:
            return f"Unbekannter Knotentyp: {type_id!r}"
        return spec.validate_config(dict(config or {}))


def build_default_node_registry() -> NodeRegistry:
    """Registry mit start, end, noop und Phase-6-Knoten."""
    from app.workflows.execution.node_executors.agent import AgentNodeExecutor
    from app.workflows.execution.node_executors.chain_delegate import ChainDelegateNodeExecutor
    from app.workflows.execution.node_executors.context_load import ContextLoadNodeExecutor
    from app.workflows.execution.node_executors.end import EndNodeExecutor
    from app.workflows.execution.node_executors.noop import NoopNodeExecutor
    from app.workflows.execution.node_executors.prompt_build import PromptBuildNodeExecutor
    from app.workflows.execution.node_executors.start import StartNodeExecutor
    from app.workflows.execution.node_executors.tool_call import ToolCallNodeExecutor

    reg = NodeRegistry()
    reg.register_type("start", StartNodeExecutor, _validate_empty_config, "Einstiegspunkt")
    reg.register_type("end", EndNodeExecutor, _validate_empty_config, "Ausgabe / Abschluss")
    reg.register_type("noop", NoopNodeExecutor, _validate_noop_config, "Identität / optionales merge")
    reg.register_type(
        "prompt_build",
        PromptBuildNodeExecutor,
        _validate_prompt_build_config,
        "Prompt aus Template / Prompt-DB",
    )
    reg.register_type("agent", AgentNodeExecutor, _validate_agent_config, "Agent → Modell (Backend)")
    reg.register_type(
        "tool_call",
        ToolCallNodeExecutor,
        _validate_tool_call_config,
        "Pipeline-Executor (tool_call)",
    )
    reg.register_type(
        "context_load",
        ContextLoadNodeExecutor,
        _validate_context_load_config,
        "Kontext laden (ContextExplainService)",
    )
    reg.register_type(
        "chain_delegate",
        ChainDelegateNodeExecutor,
        _validate_chain_delegate_config,
        "TaskPlanner / ExecutionEngine (ohne ChatWidget)",
    )
    return reg
