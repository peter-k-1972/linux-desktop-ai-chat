"""prompt_build: sicheres String-Template aus Vorgänger-Daten + Konfiguration."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

from app.workflows.execution.context import RunContext
from app.workflows.execution.node_executors.base import BaseNodeExecutor
from app.workflows.models.definition import WorkflowNode


def normalize_prompt_variables(input_payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Vereinheitlicht Executor-Input für Platzhalter:
    - ein Vorgänger: flaches dict
    - mehrere Vorgänger: dict[predecessor_id, subdict] -> flach mit Präfix ``pred__key``
    """
    if not input_payload:
        return {}
    vals = list(input_payload.values())
    if vals and all(isinstance(v, dict) for v in vals) and len(input_payload) > 1:
        merged: Dict[str, Any] = {}
        for pred_id, d in input_payload.items():
            if not isinstance(d, dict):
                continue
            p = str(pred_id)
            for k, v in d.items():
                merged[f"{p}__{k}"] = v
        return merged
    if len(input_payload) == 1:
        sole = next(iter(input_payload.values()))
        if isinstance(sole, dict):
            return dict(sole)
    return dict(input_payload)


def stringify_template_variables(variables: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in variables.items():
        key = str(k)
        if isinstance(v, str):
            out[key] = v
        elif v is None:
            out[key] = ""
        else:
            try:
                out[key] = json.dumps(v, ensure_ascii=False)
            except (TypeError, ValueError):
                out[key] = str(v)
    return out


def apply_variable_map(flat: Dict[str, Any], mapping: Any) -> Dict[str, Any]:
    """Mappt Eingabefeldnamen auf Template-Variablennamen: {template_key: input_key}."""
    if not mapping:
        return flat
    if not isinstance(mapping, dict):
        raise ValueError("config.variable_map muss ein Objekt sein.")
    out = dict(flat)
    for tpl_key, src_key in mapping.items():
        sk = str(src_key)
        tk = str(tpl_key)
        if sk in flat:
            out[tk] = flat[sk]
    return out


def resolve_prompt_template_string(config: dict) -> str:
    pid = config.get("prompt_id")
    if pid is not None:
        try:
            pid_int = int(pid)
        except (TypeError, ValueError) as e:
            raise ValueError("prompt_id muss eine ganze Zahl sein.") from e
        from app.prompts.prompt_service import get_prompt_service

        prompt = get_prompt_service().get(pid_int)
        if prompt is None or not str(prompt.content or "").strip():
            raise ValueError(f"Prompt prompt_id={pid_int} nicht gefunden oder leer.")
        return str(prompt.content).strip()

    template = str(config.get("template") or "").strip()
    prompt_text = str(config.get("prompt_text") or "").strip()
    if template:
        return template
    if prompt_text:
        return prompt_text
    raise ValueError("prompt_build: template, prompt_text oder prompt_id erforderlich.")


def render_prompt_template(template: str, string_vars: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    try:
        rendered = template.format(**string_vars)
    except KeyError as e:
        raise ValueError(f"Fehlende Template-Variable: {e}") from e
    return rendered, string_vars


class PromptBuildNodeExecutor(BaseNodeExecutor):
    """Erzeugt prompt_text per format() ohne eval; optional PromptService (prompt_id)."""

    def execute(
        self,
        node: WorkflowNode,
        input_payload: Optional[Dict[str, Any]],
        context: RunContext,
    ) -> Dict[str, Any]:
        cfg = dict(node.config or {})
        raw = normalize_prompt_variables(input_payload)
        raw = apply_variable_map(raw, cfg.get("variable_map"))
        string_vars = stringify_template_variables(raw)
        template = resolve_prompt_template_string(cfg)
        prompt_text, used = render_prompt_template(template, string_vars)
        return {
            "prompt_text": prompt_text,
            "rendered_variables": used,
        }
