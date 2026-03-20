"""
ServiceResult – einheitliches Fehler- und Statusmodell für Services.

Services geben Erfolg/Ergebnis oder Fehler/Status strukturiert zurück.
Keine rohen Exceptions quer durch die GUI.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class OperationStatus(str, Enum):
    """Status einer Operation."""

    SUCCESS = "success"
    ERROR = "error"
    RUNNING = "running"
    IDLE = "idle"
    CANCELLED = "cancelled"


@dataclass
class ServiceResult(Generic[T]):
    """
    Einheitliches Rückgabeformat für Service-Operationen.

    - success: True wenn Operation erfolgreich
    - data: Ergebnisdaten (bei Erfolg)
    - error: Fehlermeldung (bei Fehler)
    - status: OperationStatus für Laufzeitstatus
    """

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    status: OperationStatus = OperationStatus.SUCCESS
    metadata: dict = field(default_factory=dict)

    @classmethod
    def ok(cls, data: T, **kwargs) -> "ServiceResult[T]":
        """Erfolgreiches Ergebnis."""
        return cls(success=True, data=data, status=OperationStatus.SUCCESS, **kwargs)

    @classmethod
    def fail(cls, error: str, **kwargs) -> "ServiceResult[T]":
        """Fehlgeschlagenes Ergebnis."""
        return cls(
            success=False,
            error=error,
            status=OperationStatus.ERROR,
            **kwargs,
        )

    @classmethod
    def running(cls, message: str = "", **kwargs) -> "ServiceResult[T]":
        """Operation läuft."""
        return cls(
            success=False,
            error=message or "Läuft…",
            status=OperationStatus.RUNNING,
            **kwargs,
        )
