"""
Segment 7: Finaler persistierbarer Assistant-Text aus Akkumulator-Zustand.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.chat.final_message_cleaning import strip_embedded_think_blocks

if TYPE_CHECKING:
    from app.chat.stream_accumulator import ChatStreamAccumulator


def final_assistant_message_for_persistence(acc: ChatStreamAccumulator) -> str:
    return strip_embedded_think_blocks(acc.visible_assistant_text)
