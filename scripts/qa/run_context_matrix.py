#!/usr/bin/env python3
"""
Kontext-Matrix – iteriert durch definierte Kernfälle und Prompt-Datensatz.

Führt pro Prompt × pro Kernfall einen Run aus.
Keine Vollmatrix, kontrollierte Evaluationsbasis.

Input:
  - definierte Kernfälle aus der Matrix (CORE_CASES)
  - definierter Prompt-Datensatz (PROMPT_DATASET)

Output:
  - docs/qa/context_mode_experiments/context_matrix_002.json

Verwendung:
  python scripts/qa/run_context_matrix.py
"""

import asyncio
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "docs" / "qa" / "context_mode_experiments"
OUTPUT_FILE = OUTPUT_DIR / "context_matrix_002.json"

# Definiert in docs/qa/context_mode_experiments/CONTEXT_EVAL_DATASET.md
PROMPT_DATASET = [
    ("P01", "Erkläre mir die Architektur dieses Systems."),
    ("P02", "Wo sollte diese Logik architektonisch liegen?"),
    ("P03", "Welche Regressionen drohen bei dieser Änderung?"),
    ("P04", "Fasse den aktuellen Arbeitsstand dieses Chats zusammen."),
    ("P05", "Was ist hier der nächste sinnvolle Schritt?"),
    ("P06", "Worauf muss ich bei dieser Änderung besonders achten?"),
    ("P07", "Bleib beim API-Thema und nenne die wichtigsten Risiken."),
    ("P08", "Welche Tests fehlen für den Topic-Bereich?"),
    ("P09", "Was ist für dieses Teilproblem relevant, was nicht?"),
    ("P10", "Erkläre kurz, was Dependency Inversion ist."),
    ("P11", "Was ist ein Enum?"),
    ("P12", "Wann ist ein Smoke-Test sinnvoll?"),
]

CORE_CASES = [
    {"case_id": "CASE_1", "mode": "off", "detail": "standard", "fields": "all"},
    {"case_id": "CASE_2", "mode": "neutral", "detail": "standard", "fields": "all"},
    {"case_id": "CASE_3", "mode": "semantic", "detail": "full", "fields": "all"},
    {"case_id": "CASE_4", "mode": "semantic", "detail": "minimal", "fields": "project_only"},
    {"case_id": "CASE_5", "mode": "semantic", "detail": "standard", "fields": "project_chat"},
    {"case_id": "CASE_6", "mode": "neutral", "detail": "minimal", "fields": "project_only"},
]

FIELDS_MAP = {
    "all": (True, True, True),
    "project_only": (True, False, False),
    "project_chat": (True, True, False),
    "project_topic": (True, False, True),
}


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


async def run_matrix() -> dict:
    from app.core.config.settings_backend import InMemoryBackend
    from app.core.db.database_manager import DatabaseManager
    from app.services.infrastructure import init_infrastructure, set_infrastructure, get_infrastructure
    from app.services.chat_service import ChatService, get_chat_service, set_chat_service
    from app.services.project_service import ProjectService, get_project_service, set_project_service
    from app.services.topic_service import TopicService, get_topic_service, set_topic_service

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

        project_id = proj_svc.create_project("Matrix-Projekt", "", "active")
        topic_id = get_topic_service().create_topic(project_id, "Backend-Topic", "")
        chat_id = chat_svc.create_chat_in_project(
            project_id, "Matrix-Experiment", topic_id=topic_id
        )

        model = settings.model or "llama2"

        runs = []
        for prompt_id, prompt_text in PROMPT_DATASET:
            for case in CORE_CASES:
                inc_proj, inc_chat, inc_topic = FIELDS_MAP[case["fields"]]

                settings.chat_context_mode = case["mode"]
                settings.chat_context_detail_level = case["detail"]
                settings.chat_context_include_project = inc_proj
                settings.chat_context_include_chat = inc_chat
                settings.chat_context_include_topic = inc_topic
                settings.save()

                messages = [{"role": "user", "content": prompt_text}]
                final_messages = chat_svc._inject_chat_context(list(messages), chat_id)
                response = await _collect_response(chat_svc, model, list(messages), chat_id)

                runs.append({
                    "prompt_id": prompt_id,
                    "prompt_text": prompt_text,
                    "case_id": case["case_id"],
                    "mode": case["mode"],
                    "detail": case["detail"],
                    "fields": case["fields"],
                    "final_messages": final_messages,
                    "response": response,
                })

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
    result = asyncio.run(run_matrix())
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Matrix gespeichert: {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
