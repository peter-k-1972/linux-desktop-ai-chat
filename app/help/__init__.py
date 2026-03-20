"""
In-App-Hilfesystem für Linux Desktop Chat.

- HelpWindow: Durchsuchbares Hilfefenster
- HelpIndex: Kategorien, Navigation, Volltextsuche
- tooltip_helper: get_tooltip, set_tooltip_if_defined
- GuidedTour: Schritt-für-Schritt-Anleitungen
"""

from app.help.help_index import HelpIndex, HelpTopic
from app.help.help_window import HelpWindow
from app.help.tooltip_helper import get_tooltip, set_tooltip_if_defined
from app.help.guided_tour import GuidedTour, TourStep

__all__ = [
    "HelpIndex",
    "HelpTopic",
    "HelpWindow",
    "get_tooltip",
    "set_tooltip_if_defined",
    "GuidedTour",
    "TourStep",
]
