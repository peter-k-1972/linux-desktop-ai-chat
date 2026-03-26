"""
Tools – Dateisystem, Web-Suche und weitere Werkzeuge.

Phase A Refactoring:
- app/tools.py → app/tools/filesystem.py
- app/web_search.py → app/tools/web_search.py
"""

from app.tools.filesystem import FileSystemTools
from app.tools.web_search import (
    format_search_results_for_context,
    get_ollama_api_key,
    web_search,
)

__all__ = [
    "FileSystemTools",
    "web_search",
    "get_ollama_api_key",
    "format_search_results_for_context",
]
