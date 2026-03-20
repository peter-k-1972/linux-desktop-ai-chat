"""
Command-System – Command Palette, Registry, Commands.
"""

from app.gui.commands.model import Command
from app.gui.commands.registry import CommandRegistry, get_command_registry
from app.gui.commands.palette import CommandPaletteDialog

__all__ = ["Command", "CommandRegistry", "get_command_registry", "CommandPaletteDialog"]
