#!/usr/bin/env python3
"""
Kontextmodus-Experiment – systematischer Vergleich.

Führt denselben Prompt mit off, neutral, semantic aus.
Gleiche chat_id, gleiche messages, kein Streaming.

Verwendung:
  python scripts/qa/run_context_experiment.py

Output: docs/qa/context_mode_experiments/experiment_001.json
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PROMPT = "Erkläre mir die Architektur dieses Systems."
MODES = ["off", "neutral", "semantic"]
OUTPUT_DIR = PROJECT_ROOT / "docs" / "qa" / "context_mode_experiments"
OUTPUT_FILE = OUTPUT_DIR / "experiment_001.json"


async def _collect_response(chat_svc, model: str, messages: list, chat_id: int) -> str:
    """Ruft ChatService.chat auf (stream=False) und sammelt die Vollantwort."""
    content_parts = []
    async for chunk in chat_svc.chat(
        model=model,
        messages=messages,
        chat_id=chat_id,
        stream=False,
    ):
        if "error" in chunk:
            return f"Fehler: {chunk.get('error', 'Unbekannt')}"
        msg = chunk.get("message") or {}
        if msg.get("content"):
            content_parts.append(msg["content"])
    return "".join(content_parts)


async def run_experiment() -> dict:
    from app.core.config.settings_backend import InMemoryBackend
    from app.core.db.database_manager import DatabaseManager
    from app.services.infrastructure import init_infrastructure, set_infrastructure, get_infrastructure
    from app.services.chat_service import ChatService, get_chat_service, set_chat_service
    from app.services.project_service import ProjectService, get_project_service, set_project_service
    from app.services.topic_service import TopicService, set_topic_service

    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        db = DatabaseManager(db_path=db_path)
        backend = InMemoryBackend()
        init_infrastructure(settings_backend=backend)

        infra = get_infrastructure()
        infra._db = db

        set_project_service(ProjectService())
        set_chat_service(ChatService())
        set_topic_service(TopicService())

        chat_svc = get_chat_service()
        proj_svc = get_project_service()
        settings = get_infrastructure().settings

        project_id = proj_svc.create_project("Experiment-Projekt", "", "active")
        chat_id = chat_svc.create_chat_in_project(project_id, "Kontext-Experiment", topic_id=None)

        messages = [{"role": "user", "content": PROMPT}]
        model = settings.model or "llama2"

        runs = []
        for mode in MODES:
            settings.chat_context_mode = mode
            settings.save()

            final_messages = chat_svc._inject_chat_context(list(messages), chat_id)
            response = await _collect_response(chat_svc, model, list(messages), chat_id)

            runs.append({
                "mode": mode,
                "final_messages": final_messages,
                "response": response,
            })

        return {
            "prompt": PROMPT,
            "model": model,
            "chat_id": chat_id,
            "runs": runs,
        }
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass
        set_chat_service(None)
        set_project_service(None)
        set_topic_service(None)
        set_infrastructure(None)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = asyncio.run(run_experiment())
    OUTPUT_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Experiment gespeichert: {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
