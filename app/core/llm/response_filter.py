"""
Post-Processing-Filter für LLM-Antworten.
"""
import re
from dataclasses import dataclass


@dataclass
class FilterResult:
    """Ergebnis des Post-Processing-Filters."""
    text: str
    should_retry: bool


# Thinking-Block-Muster (<think>...</think>)
_THINK_PATTERN = re.compile(
    r"<think>.*?</think>",
    re.DOTALL,
)
