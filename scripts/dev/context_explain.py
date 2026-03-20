#!/usr/bin/env python3
"""
Kontext-Explainability – Developer-Tooling.

Dev-only: requires CONTEXT_DEBUG_ENABLED=1 (or context_debug_enabled in settings).
Exits 0 with message when disabled; no inspection output in production.

Zeigt die Kontext-Erklärung für einen Chat. Keine UI, keine Side Effects.

Verwendung:
  python scripts/dev/context_explain.py --chat-id 1
  python scripts/dev/context_explain.py --db chat_history.db --chat-id 1 --hint low_context_query
  python scripts/dev/context_explain.py --db chat_history.db --chat-id 1 --policy architecture --format json
  python scripts/dev/context_explain.py --chat-id 1 --format text --show-trace --show-budget --show-dropped
"""

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Kontext-Explainability: zeigt Erklärung für einen Chat."
    )
    parser.add_argument(
        "--db",
        default="chat_history.db",
        help="Pfad zur SQLite-Datenbank (default: chat_history.db)",
    )
    parser.add_argument(
        "--chat-id",
        type=int,
        required=True,
        help="Chat-ID",
    )
    parser.add_argument(
        "--hint",
        help="Request-Context-Hint (z.B. low_context_query, architecture_work)",
    )
    parser.add_argument(
        "--policy",
        help="Context-Policy (z.B. architecture, debug, exploration)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output-Format (default: text)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Alias für --format json",
    )
    parser.add_argument(
        "--show-trace",
        action="store_true",
        help="Policy chain, limits, fields anzeigen",
    )
    parser.add_argument(
        "--show-budget",
        action="store_true",
        default=True,
        help="Budget-Accounting anzeigen (default: an)",
    )
    parser.add_argument(
        "--show-dropped",
        action="store_true",
        default=True,
        help="Dropped context anzeigen (default: an)",
    )
    parser.add_argument(
        "--no-budget",
        action="store_true",
        help="Budget-Accounting ausblenden",
    )
    parser.add_argument(
        "--no-dropped",
        action="store_true",
        help="Dropped context ausblenden",
    )
    parser.add_argument(
        "--show-payload-preview",
        action="store_true",
        help="Assembliertes Kontext-Payload mit Sections, Tokens, Preview-Text anzeigen",
    )
    return parser.parse_args()


def _bootstrap_infrastructure(db_path: str) -> None:
    """Initialisiert Infrastruktur für CLI (keine DB-Änderung)."""
    from app.core.config.settings_backend import InMemoryBackend
    from app.core.db.database_manager import DatabaseManager
    from app.services.infrastructure import init_infrastructure, set_infrastructure, get_infrastructure
    from app.services.chat_service import ChatService, get_chat_service, set_chat_service
    from app.services.project_service import ProjectService, get_project_service, set_project_service
    from app.services.topic_service import TopicService, get_topic_service, set_topic_service

    init_infrastructure(settings_backend=InMemoryBackend())
    db = DatabaseManager(db_path=db_path)
    infra = get_infrastructure()
    infra._db = db

    set_project_service(ProjectService())
    set_chat_service(ChatService())
    set_topic_service(TopicService())


def main() -> int:
    args = _parse_args()

    try:
        from app.context.debug.context_debug_flag import is_context_debug_enabled
        if not is_context_debug_enabled():
            print(
                "Kontext-Explainability deaktiviert. CONTEXT_DEBUG_ENABLED=1 oder context_debug_enabled in Einstellungen aktivieren.",
                file=sys.stderr,
            )
            return 0
    except Exception:
        print("Kontext-Explainability nicht verfügbar.", file=sys.stderr)
        return 0

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / args.db
    db_path = db_path.resolve()
    if not db_path.exists():
        print(f"Fehler: Datenbank nicht gefunden: {db_path}", file=sys.stderr)
        return 1

    _bootstrap_infrastructure(str(db_path))

    from app.context.debug.context_debug import format_context_explanation, format_payload_preview
    from app.services.context_explain_service import (
        ContextExplainRequest,
        get_context_explain_service,
    )

    request = ContextExplainRequest(
        chat_id=args.chat_id,
        request_context_hint=args.hint or None,
        context_policy=args.policy or None,
    )

    try:
        svc = get_context_explain_service()
        out_format = "json" if args.json else args.format
        if out_format == "json":
            d = svc.preview_as_dict(
                request,
                include_trace=args.show_trace,
                include_budget=args.show_budget and not args.no_budget,
                include_dropped=args.show_dropped and not args.no_dropped,
                include_payload_preview=args.show_payload_preview,
            )
            print(json.dumps(d, indent=2, ensure_ascii=False))
        else:
            trace = svc.preview_with_trace(request) if args.show_trace else None
            expl = svc.preview(request)
            include_budget = args.show_budget and not args.no_budget
            include_dropped = args.show_dropped and not args.no_dropped
            print(format_context_explanation(
                expl=expl,
                trace=trace,
                include_budget=include_budget,
                include_dropped=include_dropped,
            ))
            if args.show_payload_preview:
                payload = svc.preview_payload(request)
                print(format_payload_preview(payload))
    except Exception as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
