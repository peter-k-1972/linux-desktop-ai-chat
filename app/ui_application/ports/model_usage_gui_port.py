"""
ModelUsageGuiReadPort — synchroner Lesezugriff für UI-Hinweise (Qt-frei).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ModelUsageGuiReadPort(Protocol):
    """Delegiert an Model-Usage-GUI-Service (Hinweise, keine Persistenz)."""

    def quick_sidebar_hint(self) -> str:
        """Kurzer Status-/Hinweistext für die Modell-Sidebar."""
        ...
