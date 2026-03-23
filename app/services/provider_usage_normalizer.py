"""
Normalisierung von Provider-Usage (Ollama lokal/cloud, einheitliche Extraktion).

Liefert optionale exakte Zähler; fehlende Werte werden in ``finalize`` mit Schätzung ergänzt.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ProviderUsageState:
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    raw_fragments: List[Dict[str, Any]] = field(default_factory=list)

    def to_raw_json(self) -> Optional[str]:
        if not self.raw_fragments:
            return None
        try:
            return json.dumps(self.raw_fragments[-12:], ensure_ascii=False, separators=(",", ":"))
        except (TypeError, ValueError):
            return None


def _pick_int(d: Dict[str, Any], *keys: str) -> Optional[int]:
    for k in keys:
        v = d.get(k)
        if v is None:
            continue
        try:
            iv = int(v)
            if iv >= 0:
                return iv
        except (TypeError, ValueError):
            continue
    return None


def extract_from_chunk(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """Extrahiert erkennbare Usage-Felder aus einem Stream- oder Final-Chunk."""
    out: Dict[str, Any] = {}
    prompt = _pick_int(
        chunk,
        "prompt_eval_count",
        "prompt_tokens",
        "input_tokens",
        "n_prompt_tokens",
    )
    comp = _pick_int(
        chunk,
        "eval_count",
        "completion_tokens",
        "output_tokens",
        "n_completion_tokens",
    )
    if prompt is not None:
        out["prompt_eval_count"] = prompt
    if comp is not None:
        out["eval_count"] = comp
    usage = chunk.get("usage")
    if isinstance(usage, dict):
        out["usage"] = usage
        if prompt is None:
            prompt = _pick_int(usage, "prompt", "input", "prompt_tokens")
        if comp is None:
            comp = _pick_int(usage, "completion", "output", "completion_tokens")
    return {"prompt": prompt, "completion": comp, "raw_keys": list(out.keys())}


def merge_provider_usage_state(state: ProviderUsageState, chunk: Dict[str, Any]) -> None:
    ext = extract_from_chunk(chunk)
    if ext["prompt"] is not None:
        state.prompt_tokens = ext["prompt"]
    if ext["completion"] is not None:
        state.completion_tokens = ext["completion"]
    frag = {k: chunk.get(k) for k in chunk if k not in ("message",)}
    if isinstance(chunk.get("message"), dict):
        frag["message"] = {
            k: chunk["message"].get(k)
            for k in ("content", "thinking")
            if k in chunk["message"]
        }
    state.raw_fragments.append(frag)


def finalize_token_counts(
    state: ProviderUsageState,
    messages: List[Dict[str, str]],
    assistant_text: str,
    max_tokens: int,
) -> Tuple[int, int, int, bool]:
    """
    Returns (prompt_tokens, completion_tokens, total_tokens, estimated_tokens_bool).

    estimated_tokens_bool=True wenn mindestens eine Komponente geschätzt wurde.
    """
    from app.services.token_usage_estimation import (
        estimate_completion_tokens,
        estimate_messages_prompt_tokens,
    )

    est_in = estimate_messages_prompt_tokens(messages)
    est_out = estimate_completion_tokens(assistant_text)

    p = state.prompt_tokens
    c = state.completion_tokens
    estimated = False

    if p is not None and c is not None:
        return p, c, p + c, False
    if p is not None:
        c2 = c if c is not None else est_out
        estimated = c is None
        return p, c2, p + c2, estimated
    if c is not None:
        p2 = est_in
        return p2, c, p2 + c, True
    p3, c3 = est_in, est_out
    if p3 + c3 <= 0:
        c3 = max(1, min(est_out, max(1, int(max_tokens))))
    return p3, c3, p3 + c3, True
