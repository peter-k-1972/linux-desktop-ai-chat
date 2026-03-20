"""
Re-Export für Rückwärtskompatibilität.
Slash-Commands wurden nach app.core.commands verschoben.
"""

from app.core.commands import (
    parse_slash_command,
    SlashCommandResult,
    SLASH_COMMANDS,
)

__all__ = [
    "parse_slash_command",
    "SlashCommandResult",
    "SLASH_COMMANDS",
]
