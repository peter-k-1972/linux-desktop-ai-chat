"""
Command registry and fuzzy-style filtering (subsequence scoring).

Heavier fuzzy engines can replace ``_match_score`` without touching the dialog.
"""

from __future__ import annotations

from app.gui.workbench.command_palette.command_context import WorkbenchCommandContext
from app.gui.workbench.command_palette.command_item import CommandDefinition


def _match_score(query: str, candidate: str) -> int:
    """
    Return a positive score if every query character appears in order in ``candidate``.

    Longer queries and earlier matches score higher; 0 means no match.
    """
    if not query.strip():
        return 1
    q = query.casefold()
    t = candidate.casefold()
    qi = 0
    score = 0
    for i, ch in enumerate(t):
        if qi < len(q) and ch == q[qi]:
            score += 10 + max(0, 20 - i // 2)
            qi += 1
    if qi < len(q):
        return 0
    if t.startswith(q):
        score += 80
    return score


def _command_search_blob(cmd: CommandDefinition) -> str:
    parts = (cmd.label, cmd.id, cmd.category.value, " ".join(cmd.keywords))
    return " ".join(parts)


class WorkbenchCommandRegistry:
    """In-memory registry; swap for persisted or plugin-provided commands later."""

    def __init__(self) -> None:
        self._commands: list[CommandDefinition] = []

    def register(self, command: CommandDefinition) -> None:
        self._commands.append(command)

    def all_commands(self) -> tuple[CommandDefinition, ...]:
        return tuple(self._commands)

    def is_enabled(self, cmd: CommandDefinition, ctx: WorkbenchCommandContext) -> bool:
        if cmd.enabled_when is None:
            return True
        return bool(cmd.enabled_when(ctx))

    def filter_commands(self, query: str, ctx: WorkbenchCommandContext) -> list[CommandDefinition]:
        ranked: list[tuple[int, CommandDefinition]] = []
        for cmd in self._commands:
            if not self.is_enabled(cmd, ctx):
                continue
            blob = _command_search_blob(cmd)
            score = _match_score(query, blob)
            if score > 0:
                ranked.append((score, cmd))
        ranked.sort(key=lambda x: (-x[0], x[1].label.casefold()))
        return [c for _s, c in ranked]
