"""
Zentrale Datetime-Utilities für die Anwendung.

Einheitliches Parsen und Serialisieren von Datetime-Werten
über alle Module hinweg.
"""

from datetime import datetime
from typing import Optional, Union


def parse_datetime(value: Union[None, datetime, str]) -> Optional[datetime]:
    """
    Parst datetime aus String, datetime oder None.

    Unterstützt:
    - ISO-Format mit T (z.B. 2024-01-15T10:30:00+00:00)
    - ISO-Format mit Z (wird zu +00:00 konvertiert)
    - Raum-Format (z.B. 2024-01-15 10:30:00)

    Returns:
        datetime oder None bei ungültigem/leerem Input
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    s = str(value).replace("Z", "+00:00")
    try:
        if "T" in s or "+" in s:
            return datetime.fromisoformat(s)
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def to_iso_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Konvertiert datetime zu ISO-Format-String.

    Returns:
        ISO-String (z.B. 2024-01-15T10:30:00+00:00) oder None
    """
    if dt is None:
        return None
    return dt.isoformat()
