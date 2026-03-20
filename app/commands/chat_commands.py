"""
Re-Export für Rückwärtskompatibilität.
"""

from app.core.commands.chat_commands import (
    parse_slash_command,
    SlashCommandResult,
    SLASH_COMMANDS,
    ROLE_COMMANDS,
)

__all__ = [
    "parse_slash_command",
    "SlashCommandResult",
    "SLASH_COMMANDS",
    "ROLE_COMMANDS",
]


@dataclass
class SlashCommandResult:
    """Ergebnis der Slash-Command-Verarbeitung."""

    consumed: bool  # True = Command wurde erkannt, Text nicht als Chat senden
    role: Optional[ModelRole] = None
    auto_routing: Optional[bool] = None
    cloud_escalation: Optional[bool] = None
    overkill_mode: Optional[bool] = None
    message: Optional[str] = None  # Feedback an User
    remaining_text: str = ""  # Resttext nach dem Command (z.B. für /think Frage)
    use_delegation: bool = False  # True = Agenten-Orchestrierung (Task Planner → Delegation → Execution)


# Mapping: Command -> (role, message)
ROLE_COMMANDS: Dict[str, tuple] = {
    "/fast": (ModelRole.FAST, "Modus: Schnell"),
    "/smart": (ModelRole.DEFAULT, "Modus: Standard"),
    "/chat": (ModelRole.CHAT, "Modus: Chat"),
    "/think": (ModelRole.THINK, "Modus: Denken"),
    "/code": (ModelRole.CODE, "Modus: Code"),
    "/vision": (ModelRole.VISION, "Modus: Vision"),
    "/overkill": (ModelRole.OVERKILL, "Modus: Overkill"),
    "/research": (ModelRole.RESEARCH, "Modus: Research"),
}


def parse_slash_command(
    text: str,
    *,
    on_role_change: Optional[Callable[[ModelRole], None]] = None,
    on_auto_routing_change: Optional[Callable[[bool], None]] = None,
    on_cloud_change: Optional[Callable[[bool], None]] = None,
    on_overkill_change: Optional[Callable[[bool], None]] = None,
) -> SlashCommandResult:
    """
    Parst Slash-Commands aus dem Eingabetext.

    Returns:
        SlashCommandResult mit consumed=True wenn ein reines Toggle-Command
        (z.B. /auto on) ohne weiteren Text kam. Bei Rollen-Commands mit folgendem
        Text (z.B. /think Erkläre X) wird consumed=False zurückgegeben, damit
        die Nachricht gesendet wird, aber mit der gesetzten Rolle.
    """
    stripped = text.strip()
    if not stripped.startswith("/"):
        return SlashCommandResult(consumed=False, remaining_text=text)

    parts = stripped.split(maxsplit=1)
    cmd = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""

    # /auto on | off
    if cmd == "/auto":
        if rest in ("on", "1", "true", "ja"):
            if on_auto_routing_change:
                on_auto_routing_change(True)
            return SlashCommandResult(consumed=True, auto_routing=True, message="Auto-Routing: an")
        if rest in ("off", "0", "false", "nein"):
            if on_auto_routing_change:
                on_auto_routing_change(False)
            return SlashCommandResult(consumed=True, auto_routing=False, message="Auto-Routing: aus")
        return SlashCommandResult(consumed=True, message="Verwendung: /auto on | /auto off")

    # /cloud on | off
    if cmd == "/cloud":
        if rest in ("on", "1", "true", "ja"):
            if on_cloud_change:
                on_cloud_change(True)
            return SlashCommandResult(consumed=True, cloud_escalation=True, message="Cloud-Eskalation: an")
        if rest in ("off", "0", "false", "nein"):
            if on_cloud_change:
                on_cloud_change(False)
            return SlashCommandResult(consumed=True, cloud_escalation=False, message="Cloud-Eskalation: aus")
        return SlashCommandResult(consumed=True, message="Verwendung: /cloud on | /cloud off")

    # Rollen-Commands: /fast, /smart, /think, /code, /overkill, ...
    if cmd in ROLE_COMMANDS:
        role, msg = ROLE_COMMANDS[cmd]
        if on_role_change:
            on_role_change(role)
        if rest:
            # Es gibt weiteren Text -> Nachricht soll gesendet werden mit dieser Rolle
            return SlashCommandResult(
                consumed=False,
                role=role,
                message=msg,
                remaining_text=rest,
            )
        return SlashCommandResult(consumed=True, role=role, message=msg)

    # /delegate <prompt> – Agenten-Orchestrierung (Task Planner → Delegation → Execution)
    if cmd == "/delegate":
        if rest:
            return SlashCommandResult(
                consumed=False,
                use_delegation=True,
                message="Modus: Delegation (Agenten-Farm)",
                remaining_text=rest,
            )
        return SlashCommandResult(
            consumed=True,
            message="Verwendung: /delegate <Anfrage> – z.B. /delegate Erstelle ein Video über KI-Agenten",
        )

    # Unbekannt
    return SlashCommandResult(
        consumed=True,
        message="Unbekannter Befehl: " + cmd + ". Verfügbar: /fast, /smart, /chat, /think, /code, /vision, /overkill, /research, /delegate, /auto on|off, /cloud on|off",
    )


SLASH_COMMANDS = list(ROLE_COMMANDS.keys()) + ["/auto", "/cloud", "/delegate"]
