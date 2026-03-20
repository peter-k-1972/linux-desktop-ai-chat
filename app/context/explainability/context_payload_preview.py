"""
Context payload preview – safe preview of assembled context for developers.

Read-only, no hidden data reconstruction. Only previews text in final payload.

ORDERING CONTRACT (QA surface):
- sections: [header, project_context, chat_context, topic_context, instruction_block]
  Fixed order from _parse_fragment_to_sections; no dict/set iteration.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

CHARS_PER_TOKEN = 4

# Section order: header first, then project/chat/topic by marker order, then instruction_block
_PAYLOAD_SECTION_MARKERS: List[Tuple[str, str, str, str]] = [
    ("- Projekt:", "project_context", "project", "project_name"),
    ("- Chat:", "chat_context", "chat", "chat_title"),
    ("- Topic:", "topic_context", "topic", "topic_name"),
]
MAX_PREVIEW_LINES = 5
MAX_PREVIEW_CHARS = 300


@dataclass(frozen=True)
class ContextPayloadSection:
    """
    Section of the assembled context payload.

    Attributes:
        section_name: project_context | chat_context | topic_context | instruction_block | header
        included: whether this section is in the final payload
        line_count: number of lines in this section
        token_count: estimated tokens (chars/4)
        source_type: optional – project | chat | topic
        source_id: optional – identifier (e.g. project name, chat title)
        preview_text: optional – first N safe lines from assembled result
        truncated_preview: True if preview was truncated
    """

    section_name: str
    included: bool
    line_count: int
    token_count: int
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    preview_text: Optional[str] = None
    truncated_preview: bool = False


@dataclass(frozen=True)
class ContextPayloadPreview:
    """
    Safe preview of the assembled context payload.

    Attributes:
        sections: list of payload sections
        total_tokens: total tokens in payload
        total_lines: total lines in payload
        empty: True if payload is empty
    """

    sections: List[ContextPayloadSection] = field(default_factory=list)
    total_tokens: int = 0
    total_lines: int = 0
    empty: bool = True


def _safe_preview(text: str) -> tuple[str, bool]:
    """
    Extract safe preview: max 5 lines, max 300 chars.
    Returns (preview_text, truncated_preview).
    """
    if not text or not text.strip():
        return ("", False)
    lines = text.strip().splitlines()
    truncated = False
    result_lines: List[str] = []
    total_chars = 0
    for i, line in enumerate(lines):
        if i >= MAX_PREVIEW_LINES:
            truncated = True
            break
        remaining = MAX_PREVIEW_CHARS - total_chars
        if remaining <= 0:
            truncated = True
            break
        if len(line) > remaining:
            result_lines.append(line[:remaining] + ("..." if len(line) > remaining else ""))
            truncated = True
            total_chars += remaining
            break
        result_lines.append(line)
        total_chars += len(line)
    return ("\n".join(result_lines).strip() or "", truncated)


def _parse_fragment_to_sections(
    fragment: str,
    context: Optional[object] = None,
    render_options: Optional[object] = None,
) -> List[ContextPayloadSection]:
    """
    Parse assembled fragment into sections. Only uses text from fragment.
    Never reconstructs dropped content.
    """
    if not fragment or not fragment.strip():
        return []

    sections: List[ContextPayloadSection] = []
    lines = fragment.strip().splitlines()

    # Header (Arbeitskontext: or Kontext:)
    for ln in lines:
        if ln.strip() in ("Arbeitskontext:", "Kontext:"):
            sections.append(
                ContextPayloadSection(
                    section_name="header",
                    included=True,
                    line_count=1,
                    token_count=len(ln) // CHARS_PER_TOKEN,
                    source_type=None,
                    source_id=None,
                    preview_text=ln.strip(),
                    truncated_preview=False,
                )
            )
            break

    for marker, section_name, source_type, attr in _PAYLOAD_SECTION_MARKERS:
        section_lines: List[str] = []
        for ln in lines:
            if ln.strip().startswith(marker):
                section_lines.append(ln)
                break
        line_count = len(section_lines)
        text = "\n".join(section_lines) if section_lines else ""
        token_count = len(text) // CHARS_PER_TOKEN if text else 0
        preview, truncated = _safe_preview(text) if text else ("", False)
        source_id = None
        if context and hasattr(context, attr):
            val = getattr(context, attr, None)
            source_id = str(val) if val else None
        sections.append(
            ContextPayloadSection(
                section_name=section_name,
                included=line_count > 0,
                line_count=line_count,
                token_count=token_count,
                source_type=source_type,
                source_id=source_id,
                preview_text=preview if preview else None,
                truncated_preview=truncated,
            )
        )

    # Instruction block (e.g. "Berücksichtige diesen Kontext bei der Antwort.")
    instruction_lines = [
        ln for ln in lines
        if ln.strip()
        and not ln.strip().startswith("- ")
        and ln.strip() not in ("Arbeitskontext:", "Kontext:")
    ]
    if instruction_lines:
        text = "\n".join(instruction_lines)
        preview, truncated = _safe_preview(text)
        sections.append(
            ContextPayloadSection(
                section_name="instruction_block",
                included=True,
                line_count=len(instruction_lines),
                token_count=len(text) // CHARS_PER_TOKEN,
                source_type=None,
                source_id=None,
                preview_text=preview if preview else None,
                truncated_preview=truncated,
            )
        )

    return sections


def build_payload_preview(
    fragment: str,
    context: Optional[object] = None,
    render_options: Optional[object] = None,
) -> ContextPayloadPreview:
    """
    Build ContextPayloadPreview from assembled fragment.
    Only uses text in fragment – never reconstructs dropped content.
    """
    if not fragment or not fragment.strip():
        return ContextPayloadPreview(empty=True)

    sections = _parse_fragment_to_sections(fragment, context, render_options)
    total_chars = len(fragment.strip())
    total_tokens = total_chars // CHARS_PER_TOKEN
    total_lines = len(fragment.strip().splitlines())

    return ContextPayloadPreview(
        sections=sections,
        total_tokens=total_tokens,
        total_lines=total_lines,
        empty=False,
    )
