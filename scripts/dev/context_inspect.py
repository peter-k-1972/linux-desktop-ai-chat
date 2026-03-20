#!/usr/bin/env python3
"""
Context inspection CLI – developer tooling for context resolution inspection.

Dev-only: requires CONTEXT_DEBUG_ENABLED=1 (or context_debug_enabled in settings).
Exits 0 with message when disabled; no inspection output in production.

Read-only. No UI, no persistence, no side effects. Uses ContextInspectionService
and inspection_result_to_dict only.

Usage:
  python scripts/dev/context_inspect.py --chat-id 1
  python scripts/dev/context_inspect.py --chat-id 1 --hint low_context_query --policy architecture
  python scripts/dev/context_inspect.py --fixture scripts/dev/fixtures/inspect_request.json
  python scripts/dev/context_inspect.py --chat-id 1 --format json
  python scripts/dev/context_inspect.py --chat-id 1 --format text --show-trace --show-budget --show-sources
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Context inspection: resolution, explainability, payload preview."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--chat-id",
        type=int,
        help="Chat ID",
    )
    input_group.add_argument(
        "--fixture",
        type=str,
        metavar="PATH",
        help="Path to JSON fixture with chat_id, request_context_hint, context_policy",
    )
    parser.add_argument(
        "--hint",
        help="Request context hint (e.g. low_context_query, architecture_work)",
    )
    parser.add_argument(
        "--policy",
        help="Context policy (e.g. architecture, debug, exploration)",
    )
    parser.add_argument(
        "--db",
        default="chat_history.db",
        help="Path to SQLite database (default: chat_history.db)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Alias for --format json",
    )
    parser.add_argument(
        "--show-trace",
        action="store_true",
        help="Show trace block (text mode)",
    )
    parser.add_argument(
        "--show-budget",
        action="store_true",
        help="Show budget block (text mode)",
    )
    parser.add_argument(
        "--show-sources",
        action="store_true",
        help="Show sources block (text mode)",
    )
    parser.add_argument(
        "--show-warnings",
        action="store_true",
        help="Show warnings block (text mode)",
    )
    parser.add_argument(
        "--show-payload-preview",
        action="store_true",
        help="Show payload preview block (text mode)",
    )
    return parser.parse_args()


def _load_request_from_args(args: argparse.Namespace) -> "ContextExplainRequest":
    from app.context.devtools.request_fixture_loader import (
        FixtureValidationError,
        load_request_fixture,
    )
    from app.services.context_explain_service import ContextExplainRequest

    if args.fixture:
        path = Path(args.fixture)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        path = path.resolve()
        data = load_request_fixture(path)
        return ContextExplainRequest(
            chat_id=data["chat_id"],
            request_context_hint=data.get("context_hint"),
            context_policy=data.get("context_policy"),
        )
    return ContextExplainRequest(
        chat_id=args.chat_id,
        request_context_hint=args.hint or None,
        context_policy=args.policy or None,
    )


def _bootstrap_infrastructure(db_path: str) -> None:
    """Initialize infrastructure for CLI (read-only, no DB mutation)."""
    from app.core.config.settings_backend import InMemoryBackend
    from app.core.db.database_manager import DatabaseManager
    from app.services.chat_service import ChatService, set_chat_service
    from app.services.infrastructure import get_infrastructure, init_infrastructure
    from app.services.project_service import ProjectService, set_project_service
    from app.services.topic_service import TopicService, set_topic_service

    init_infrastructure(settings_backend=InMemoryBackend())
    db = DatabaseManager(db_path=db_path)
    infra = get_infrastructure()
    infra._db = db

    set_project_service(ProjectService())
    set_chat_service(ChatService())
    set_topic_service(TopicService())


def _print_text(result: "ContextInspectionResult", args: argparse.Namespace) -> None:
    """Print text output: summary always, then selected blocks in deterministic order."""
    from app.context.debug.context_debug import (
        format_context_trace_block,
        format_payload_preview,
    )

    # Summary block always
    print(result.formatted_summary)
    if result.formatted_summary:
        print()

    # Optional blocks in deterministic order: trace, budget, sources, warnings, payload-preview
    if args.show_trace:
        print(format_context_trace_block(result.trace))
    if args.show_budget:
        print(result.formatted_budget)
        if result.formatted_budget:
            print()
    if args.show_sources:
        print(result.formatted_sources)
        if result.formatted_sources:
            print()
    if args.show_warnings and result.formatted_warnings:
        print(result.formatted_warnings)
        print()
    if args.show_payload_preview:
        print(format_payload_preview(result.payload_preview))


def main() -> int:
    args = _parse_args()

    try:
        from app.context.debug.context_debug_flag import is_context_debug_enabled
        if not is_context_debug_enabled():
            print(
                "Context inspection disabled. Set CONTEXT_DEBUG_ENABLED=1 or enable context_debug_enabled in settings.",
                file=sys.stderr,
            )
            return 0
    except Exception:
        print("Context inspection unavailable.", file=sys.stderr)
        return 0

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / args.db
    db_path = db_path.resolve()
    if not db_path.exists():
        print(f"Error: database not found: {db_path}", file=sys.stderr)
        return 1

    _bootstrap_infrastructure(str(db_path))

    try:
        from app.context.devtools import FixtureValidationError

        request = _load_request_from_args(args)
    except (
        FileNotFoundError,
        FixtureValidationError,
    ) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        from app.context.explainability.context_inspection_serializer import (
            inspection_result_to_dict,
        )
        from app.services.context_inspection_service import get_context_inspection_service

        svc = get_context_inspection_service()
        result = svc.inspect(request)

        out_format = "json" if args.json else args.format
        if out_format == "json":
            d = inspection_result_to_dict(result)
            print(json.dumps(d, indent=2, ensure_ascii=False))
        else:
            _print_text(result, args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
