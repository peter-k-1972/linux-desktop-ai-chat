"""
Markdown-Demo: Metadaten und Laden der Beispieldateien.

Quelltext liegt unter app/resources/demo_markdown/*.md (kein eingebetteter Parser).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# app/gui/devtools → parents[2] == app-Paketwurzel (Ordner app/)
_APP_ROOT = Path(__file__).resolve().parents[2]
DEMO_MARKDOWN_DIR = _APP_ROOT / "resources" / "demo_markdown"


@dataclass(frozen=True)
class MarkdownDemoSample:
    """Ein Demo-Beispiel."""

    sample_id: str
    title: str
    filename: str


# Reihenfolge = Navigationsreihenfolge in der Demo-UI
MARKDOWN_DEMO_SAMPLES: tuple[MarkdownDemoSample, ...] = (
    MarkdownDemoSample("basic", "1 · Basic (Überschriften, Listen, Zitat)", "basic.md"),
    MarkdownDemoSample("code", "2 · Code (Fence + Inline)", "code_blocks.md"),
    MarkdownDemoSample("ascii_tree", "3 · ASCII-Baum", "ascii_tree.md"),
    MarkdownDemoSample("ascii_boxes", "4 · ASCII-Boxdiagramm", "ascii_boxes.md"),
    MarkdownDemoSample("cli_output", "5 · CLI-/Testausgabe", "cli_output.md"),
    MarkdownDemoSample("mixed", "6 · Gemischtes Dokument", "mixed.md"),
    MarkdownDemoSample("broken", "7 · Kaputtes Markdown", "broken_markdown.md"),
    MarkdownDemoSample("help_like", "8 · Hilfe-ähnlich", "help_like.md"),
    MarkdownDemoSample("chat_like", "9 · Chat-ähnlich (Assistant)", "chat_like.md"),
)


def demo_markdown_dir() -> Path:
    return DEMO_MARKDOWN_DIR


def load_sample_text(sample_id: str) -> str:
    """Lädt Text für sample_id aus der Markdown-Datei; Fehler → leerer String."""
    for s in MARKDOWN_DEMO_SAMPLES:
        if s.sample_id == sample_id:
            path = DEMO_MARKDOWN_DIR / s.filename
            if path.is_file():
                try:
                    return path.read_text(encoding="utf-8")
                except OSError:
                    return ""
            return ""
    return ""
