"""
Context replay CLI – load ReplayInput from JSON, run replay, print serialized result.

No UI. No logging side effects. Deterministic output only.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from app.context.replay.canonicalize import canonicalize
from app.context.replay.replay_models import ReplayInput, ReplayVersionMismatchError
from app.context.replay.replay_service import get_context_replay_service


def _load_replay_input(file_path: str | Path) -> ReplayInput:
    """Load ReplayInput from JSON file. Deterministic."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Replay input file not found: {path}")
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    return _dict_to_replay_input(data)


def _dict_to_replay_input(data: Dict[str, Any]) -> ReplayInput:
    """Build ReplayInput from dict. Canonicalized for deterministic parsing."""
    data = canonicalize(data)
    fields = data.get("fields")
    if isinstance(fields, list):
        fields = tuple(fields)
    elif fields is None:
        fields = ()
    return ReplayInput(
        chat_id=int(data["chat_id"]),
        project_id=data.get("project_id"),
        project_name=data.get("project_name"),
        chat_title=str(data.get("chat_title", "")),
        topic_id=data.get("topic_id"),
        topic_name=data.get("topic_name"),
        is_global_chat=bool(data.get("is_global_chat", False)),
        mode=str(data.get("mode", "semantic")),
        detail=str(data.get("detail", "standard")),
        include_project=bool(data.get("include_project", True)),
        include_chat=bool(data.get("include_chat", True)),
        include_topic=bool(data.get("include_topic", False)),
        max_project_chars=data.get("max_project_chars"),
        max_chat_chars=data.get("max_chat_chars"),
        max_topic_chars=data.get("max_topic_chars"),
        max_total_lines=data.get("max_total_lines"),
        limits_source=str(data.get("limits_source", "default")),
        source=str(data.get("source", "individual_settings")),
        profile=data.get("profile"),
        policy=data.get("policy"),
        hint=data.get("hint"),
        chat_policy=data.get("chat_policy"),
        project_policy=data.get("project_policy"),
        profile_enabled=bool(data.get("profile_enabled", False)),
        fields=fields,
        base_explanation=None,
        system_version=data.get("system_version"),
    )


def run_replay(file_path: str | Path) -> str:
    """
    Load ReplayInput from JSON file, run replay, return serialized result.

    No UI. No logging side effects. Deterministic output only.
    """
    logging.disable(logging.CRITICAL)
    try:
        replay_input = _load_replay_input(file_path)
        svc = get_context_replay_service()
        result = svc.replay(replay_input)
        out = result.to_dict()
        return json.dumps(out, sort_keys=True, ensure_ascii=False, indent=2)
    finally:
        logging.disable(logging.NOTSET)


def main() -> int:
    """CLI entry point. Usage: python -m app.cli.context_replay <file_path>"""
    import sys

    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python -m app.cli.context_replay <file_path>\n")
        return 1
    try:
        output = run_replay(sys.argv[1])
        print(output)
        return 0
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 1
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, ReplayVersionMismatchError) as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
