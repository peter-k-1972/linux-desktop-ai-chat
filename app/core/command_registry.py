"""
Command Registry – system-wide command registration and search.

Responsibilities:
- Register commands
- Search commands (fuzzy)
- Return ranked results

Categories: Workspace, Feature, Help, Setting, Command
"""

from dataclasses import dataclass
from typing import Callable

# Categories for the command palette
CATEGORY_WORKSPACE = "Workspace"
CATEGORY_FEATURE = "Feature"
CATEGORY_HELP = "Help"
CATEGORY_SETTING = "Setting"
CATEGORY_COMMAND = "Command"

# Category order for display
CATEGORY_ORDER = [CATEGORY_WORKSPACE, CATEGORY_FEATURE, CATEGORY_HELP, CATEGORY_SETTING, CATEGORY_COMMAND]


@dataclass
class PaletteCommand:
    """A command for the command palette."""

    id: str
    title: str
    description: str = ""
    icon: str = ""
    category: str = CATEGORY_WORKSPACE
    keywords: str = ""  # Extra search terms
    callback: Callable[[], None] | None = None

    def search_text(self) -> str:
        """Combined text for search (title + description + keywords)."""
        return f"{self.title} {self.description} {self.keywords}".lower()

    def execute(self) -> None:
        """Execute the command."""
        if self.callback:
            self.callback()


def _fuzzy_score(query: str, target: str) -> float:
    """
    Fuzzy match score. Higher is better.
    - Exact match: 100
    - Prefix match: 80
    - Substring: 60
    - Subsequence (chars in order): 20 + (len_matched / len_query) * 20
    """
    q = query.lower().strip()
    t = target.lower()
    if not q:
        return 0.0
    if q == t:
        return 100.0
    if t.startswith(q):
        return 80.0
    if q in t:
        return 60.0
    # Subsequence: chars of q appear in order in t
    ti = 0
    matched = 0
    for c in q:
        while ti < len(t):
            if t[ti] == c:
                matched += 1
                ti += 1
                break
            ti += 1
        else:
            return 0.0
    return 20.0 + (matched / len(q)) * 20.0


class CommandRegistry:
    """Central registry for palette commands."""

    _commands: dict[str, PaletteCommand] = {}
    _order: list[str] = []

    @classmethod
    def register(cls, command: PaletteCommand) -> None:
        """Register a command."""
        if command.id not in cls._commands:
            cls._commands[command.id] = command
            cls._order.append(command.id)

    @classmethod
    def unregister(cls, command_id: str) -> bool:
        """Remove a command."""
        if command_id in cls._commands:
            del cls._commands[command_id]
            if command_id in cls._order:
                cls._order.remove(command_id)
            return True
        return False

    @classmethod
    def get(cls, command_id: str) -> PaletteCommand | None:
        """Get command by ID."""
        return cls._commands.get(command_id)

    @classmethod
    def search(cls, query: str) -> list[tuple[PaletteCommand, float]]:
        """
        Search commands with fuzzy matching. Returns list of (command, score) sorted by score desc.
        """
        q = query.strip().lower()
        if not q:
            return [(cls._commands[cid], 50.0) for cid in cls._order if cid in cls._commands]

        scored: list[tuple[PaletteCommand, float]] = []
        for cid in cls._order:
            cmd = cls._commands.get(cid)
            if not cmd:
                continue
            search_text = cmd.search_text()
            score = _fuzzy_score(q, search_text)
            if score > 0:
                # Boost title matches
                title_score = _fuzzy_score(q, cmd.title)
                if title_score > score:
                    score = title_score
                scored.append((cmd, score))

        scored.sort(key=lambda x: -x[1])
        return scored

    @classmethod
    def search_commands(cls, query: str) -> list[PaletteCommand]:
        """Search and return commands only (no scores)."""
        return [cmd for cmd, _ in cls.search(query)]

    @classmethod
    def all_commands(cls) -> list[PaletteCommand]:
        """All commands in registration order."""
        return [cls._commands[cid] for cid in cls._order if cid in cls._commands]

    @classmethod
    def execute(cls, command_id: str) -> bool:
        """Execute a command by ID."""
        cmd = cls.get(command_id)
        if cmd:
            cmd.execute()
            return True
        return False
