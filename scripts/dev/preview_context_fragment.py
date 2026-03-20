#!/usr/bin/env python3
"""
Kontext-Fragment – Vorschau ohne Provider-Call und ohne UI.

Erzeugt festen Beispielkontext, rendert Fragment, zeigt Strukturmetriken und Limits.

Verwendung:
  python scripts/dev/preview_context_fragment.py --mode semantic --detail standard --fields all
  python scripts/dev/preview_context_fragment.py --policy architecture --project-name "Lang"
  python scripts/dev/preview_context_fragment.py --policy debug --chat-title "X" * 100
  python scripts/dev/preview_context_fragment.py --mode off
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.chat.context import (
    ChatContextRenderOptions,
    ChatRequestContext,
    get_context_fragment_stats,
)
from app.chat.context_policies import ChatContextPolicy, resolve_limits_for_policy
from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode

# Fester Beispielkontext (kein DB-Zugriff)
EXAMPLE_CONTEXT = ChatRequestContext(
    project_id=1,
    project_name="Obsidian Core",
    chat_id=1,
    chat_title="Architekturprüfung",
    topic_id=1,
    topic_name="API",
    is_global_chat=False,
)

FIELDS_MAP = {
    "all": (True, True, True),
    "project_only": (True, False, False),
    "project_chat": (True, True, False),
    "project_topic": (True, False, True),
    "chat_only": (False, True, False),
    "topic_only": (False, False, True),
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vorschau des Chat-Kontext-Fragments ohne Provider-Call."
    )
    parser.add_argument(
        "--mode",
        choices=["off", "neutral", "semantic"],
        default="semantic",
        help="Kontextmodus",
    )
    parser.add_argument(
        "--detail",
        choices=["minimal", "standard", "full"],
        default="standard",
        help="Detailtiefe",
    )
    parser.add_argument(
        "--fields",
        choices=list(FIELDS_MAP),
        default="all",
        help="Feldprofil",
    )
    parser.add_argument(
        "--policy",
        choices=["architecture", "debug", "exploration", "default"],
        default="default",
        help="Policy-Budget (Limits)",
    )
    parser.add_argument(
        "--project-name",
        default=None,
        help="Projektname (Override)",
    )
    parser.add_argument(
        "--chat-title",
        default=None,
        help="Chat-Titel (Override)",
    )
    parser.add_argument(
        "--topic-name",
        default=None,
        help="Topic-Name (Override)",
    )
    return parser.parse_args()


def _fields_to_labels(fields: str) -> str:
    """Liefert lesbare Feldliste (z.B. 'project, chat, topic')."""
    inc_proj, inc_chat, inc_topic = FIELDS_MAP.get(fields, (True, True, True))
    parts = []
    if inc_proj:
        parts.append("project")
    if inc_chat:
        parts.append("chat")
    if inc_topic:
        parts.append("topic")
    return ", ".join(parts) if parts else "none"


def main() -> int:
    args = _parse_args()
    mode = ChatContextMode(args.mode)
    detail = ChatContextDetailLevel(args.detail)
    inc_proj, inc_chat, inc_topic = FIELDS_MAP[args.fields]
    opts = ChatContextRenderOptions(
        include_project=inc_proj,
        include_chat=inc_chat,
        include_topic=inc_topic,
    )

    policy = ChatContextPolicy(args.policy)
    limits = resolve_limits_for_policy(policy)
    limits_source = policy.value

    ctx = ChatRequestContext(
        project_id=EXAMPLE_CONTEXT.project_id,
        project_name=args.project_name if args.project_name is not None else EXAMPLE_CONTEXT.project_name,
        chat_id=EXAMPLE_CONTEXT.chat_id,
        chat_title=args.chat_title if args.chat_title is not None else EXAMPLE_CONTEXT.chat_title,
        topic_id=EXAMPLE_CONTEXT.topic_id,
        topic_name=args.topic_name if args.topic_name is not None else EXAMPLE_CONTEXT.topic_name,
        is_global_chat=EXAMPLE_CONTEXT.is_global_chat,
    )

    print(f"Mode: {mode.value}")
    print(f"Detail: {detail.value}")
    print(f"Fields: {_fields_to_labels(args.fields)}")
    print(f"Policy: {policy.value}")

    print("\nLimits:")
    print(f"  max_project_chars: {limits.max_project_chars}")
    print(f"  max_chat_chars: {limits.max_chat_chars}")
    print(f"  max_topic_chars: {limits.max_topic_chars}")
    print(f"  max_total_lines: {limits.max_total_lines}")
    print(f"  source: {limits_source}")

    if mode == ChatContextMode.OFF:
        print("\nno fragment")
        return 0

    fragment = ctx.to_system_prompt_fragment(mode, detail, opts, limits)
    if not fragment.strip():
        print("\nno fragment (keine aktiven Felder)")
        return 0

    full_fragment = f"[[CTX]]\n{fragment}"
    stats = get_context_fragment_stats(full_fragment)

    print("\nFragment:")
    print("--------------------------------")
    print(full_fragment.rstrip())
    print("--------------------------------")
    print("\nStats:")
    print(f"chars={stats['chars']}")
    print(f"lines={stats['lines']}")
    print(f"nonempty_lines={stats['nonempty_lines']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
