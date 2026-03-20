"""
CommandRegistry – zentrale Registrierung und Suche von Commands.
"""

from app.gui.commands.model import Command


class CommandRegistry:
    """
    Zentrale Registry für Commands.
    - Registrierung
    - Suche (Filter nach Text)
    - Ausführung
    """

    _commands: dict[str, Command] = {}
    _order: list[str] = []

    @classmethod
    def register(cls, command: Command) -> None:
        """Registriert einen Command."""
        if command.id not in cls._commands:
            cls._commands[command.id] = command
            cls._order.append(command.id)

    @classmethod
    def unregister(cls, command_id: str) -> bool:
        """Entfernt einen Command. Gibt True bei Erfolg zurück."""
        if command_id in cls._commands:
            del cls._commands[command_id]
            if command_id in cls._order:
                cls._order.remove(command_id)
            return True
        return False

    @classmethod
    def get(cls, command_id: str) -> Command | None:
        """Liefert einen Command nach ID."""
        return cls._commands.get(command_id)

    @classmethod
    def search(cls, query: str) -> list[Command]:
        """
        Sucht Commands nach Titel und Beschreibung.
        Leere Query liefert alle Commands in Registrierungsreihenfolge.
        """
        q = query.strip().lower()
        if not q:
            return [cls._commands[cid] for cid in cls._order if cid in cls._commands]

        results: list[Command] = []
        for cid in cls._order:
            cmd = cls._commands.get(cid)
            if not cmd:
                continue
            if q in cmd.title.lower() or (cmd.description and q in cmd.description.lower()):
                results.append(cmd)
        return results

    @classmethod
    def all_commands(cls) -> list[Command]:
        """Liefert alle Commands in Registrierungsreihenfolge."""
        return [cls._commands[cid] for cid in cls._order if cid in cls._commands]

    @classmethod
    def execute(cls, command_id: str) -> bool:
        """Führt einen Command aus. Gibt True bei Erfolg zurück."""
        cmd = cls.get(command_id)
        if cmd:
            cmd.execute()
            return True
        return False


_registry: CommandRegistry | None = None


def get_command_registry() -> CommandRegistry:
    """Singleton-Zugriff auf die CommandRegistry."""
    return CommandRegistry
