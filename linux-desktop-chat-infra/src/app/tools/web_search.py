"""
Ollama Web Search API-Integration.

Nutzt die Cloud-API unter https://ollama.com/api/web_search.
API-Key aus .env (OLLAMA_API_KEY) oder Umgebungsvariable.

Phase A Refactoring: app/web_search.py → app/tools/web_search.py
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from app.utils.env_loader import load_env

OLLAMA_WEB_SEARCH_URL = "https://ollama.com/api/web_search"


def get_ollama_api_key() -> Optional[str]:
    """Liefert den Ollama-API-Key aus .env oder Umgebung."""
    load_env()
    return os.environ.get("OLLAMA_API_KEY") or None


async def web_search(
    query: str,
    max_results: int = 5,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Führt eine Websuche über die Ollama Cloud-API aus.

    Returns:
        {"results": [{"title", "url", "content"}, ...], "error": "..." (optional)}
    """
    key = api_key or get_ollama_api_key()
    if not key:
        return {
            "results": [],
            "error": "OLLAMA_API_KEY fehlt. Bitte in .env setzen (ollama.com/settings/keys).",
        }

    payload = {"query": query, "max_results": min(max_results, 10)}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                OLLAMA_WEB_SEARCH_URL, json=payload, headers=headers
            ) as r:
                if r.status != 200:
                    text = await r.text()
                    return {
                        "results": [],
                        "error": f"Websuche API Fehler {r.status}: {text[:200]}",
                    }
                data = await r.json()
                return {"results": data.get("results", [])}
    except aiohttp.ClientError as e:
        return {"results": [], "error": f"Netzwerkfehler: {e}"}
    except Exception as e:
        return {"results": [], "error": str(e)}


def format_search_results_for_context(results: List[Dict[str, Any]]) -> str:
    """Formatiert Suchergebnisse als Kontext für das Modell."""
    if not results:
        return ""
    parts = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "(ohne Titel)")
        url = r.get("url", "")
        content = r.get("content", "")[:800]  # Begrenzen
        parts.append(f"[{i}] {title}\nURL: {url}\n{content}")
    return "--- Aktuelle Websuchergebnisse ---\n" + "\n\n".join(parts) + "\n--- Ende Websuche ---"
